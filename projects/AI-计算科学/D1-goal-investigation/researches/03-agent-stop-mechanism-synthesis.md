# Why LLM Agents Stop Before Completing Goals
## A Comparative Analysis of Claude Code, Codex, and Hermes

> Origin: ai
> Date: 2026-06-12
> Status: draft

---

## Abstract

We analyze a shared phenomenon across three autonomous coding agents (Claude Code, OpenAI Codex, Hermes): all three terminate before goal completion. We trace this to a common architectural root — **LLMs are turn processors, not goal executors** — and identify three specific mechanisms that produce the "stop-before-complete" behavior in each system. We then evaluate four strategies for overcoming this limitation: stop hooks, prompt-based persistence, loop wrappers, and built-in completion detection. Our key finding is that `stop_reason: "end_turn"` in the Anthropic API is the decisive signal: it is a turn-level indicator, not a goal-level indicator, yet Claude Code treats it as session termination.

---

## 1. Introduction

Autonomous coding agents are increasingly expected to execute multi-step goals without continuous human guidance. A common failure mode: the agent stops before completing the goal. This paper analyzes why this happens across three major systems and identifies the shared root cause.

**Research question**: Why do Claude Code, Codex, and Hermes stop before completing assigned goals?

**Method**: Source code analysis, binary string extraction, API protocol analysis, and comparative mechanism study.

---

## 2. System Architecture and Stop Conditions

### 2.1 Claude Code

Claude Code operates as a turn-based system:

```
User provides goal/prompt
    ↓
Claude Code calls Anthropic API (messages endpoint)
    ↓
API returns response with stop_reason:
  - "end_turn"     → model believes it completed the turn
  - "tool_use"     → model called tools, waits for results
  - "max_tokens"   → reached max token limit
  - "stop_sequence" → matched stop sequence
    ↓
Claude Code decides based on stop_reason:
  - tool_use → execute tool → feed result back to API → continue
  - end_turn → attempt exit → Stop hook triggers
  - max_tokens → continue (if tokens remaining) or exit
    ↓
Stop hook intercepts exit:
  - hook outputs {"decision":"block", ...} → inject prompt → continue
  - hook exits 0 → session ends
```

**Key observation**: Claude Code has no built-in task completion detection. Its exit conditions are entirely determined by external hooks and the `stop_reason` from the API.

**Binary string evidence** (extracted from Claude Code binary):
- `preventExit` / `stopPreventingExit` — hook exit-blocking mechanism
- `executeStopHooks`, `tengu_pre_stop_hooks_cancelled`, `SessionEnd`
- `hook_error_during_execution` — session terminates on hook failure
- `asyncRewake` (exit code 2) — hook runs in background
- `[loop-tick] Stop hook block discarded (turn is yielding to a cron)` — cron can interrupt hook blocking

### 2.2 OpenAI Codex

Codex operates as a user-driven system:

- User provides goal → Codex executes → waits for user verification
- Termination is entirely user-driven (new instruction, stop command, manual intervention)
- No public-facing autonomous completion detection mechanism

**Key observation**: Codex does not "stop before completing" — it waits for user direction. The limitation is lack of autonomous judgment about when the goal is satisfied.

### 2.3 Hermes

Hermes has three hook systems with different capabilities:

| System | Registration | Injection | Exit Control |
|--------|-------------|-----------|-------------|
| Gateway Hook | HOOK.yaml + handler.py | No (observer) | No |
| Plugin Hook | ctx.register_hook() | Yes (pre_llm_call returns context) | No |
| Shell Hook | config.yaml → script | Yes (pre_llm_call injects context) | No |

**Key observation**: Hermes Gateway Hooks are purely observational — their return values are discarded. Plugin/Shell Hooks can inject context within a turn but cannot control session lifecycle. Gateway hook architecture:

```python
async def emit(self, event_type, context):
    for fn in handlers:
        result = fn(event_type, context)
        # result is discarded, no return value collection
```

---

## 3. Common Root Cause Analysis

### 3.1 Root Cause 1: LLMs Are Turn Processors, Not Goal Executors

All three systems are built on the same fundamental model: an LLM that processes one turn (receive prompt → output response). Each turn is self-contained. The LLM itself has no concept of "I haven't finished my task." Cross-turn state is communicated through external files or memory.

**Critical insight**: The Anthropic API's `stop_reason: "end_turn"` does NOT mean "goal complete." It means "the model has finished its output for this turn." Claude Code interprets `end_turn` as "no more tools to call, try exiting."

### 3.2 Root Cause 2: No Built-in Completion Detection

| Agent | Completion Detection | How "done" is determined |
|-------|---------------------|-------------------------|
| Claude Code | None | Hook checks completion promise string |
| Codex | None | User judgment |
| Hermes | None | After sending response → end |

**None of the three systems have built-in task completion detection.**

### 3.3 Root Cause 3: Exit Conditions Are External

- Claude Code: Stop Hook file state
- Codex: User command
- Hermes: None (auto-ends)

The decision to stop or continue is always made by something external to the LLM itself.

---

## 4. Why the Model Outputs `end_turn`

The model outputs `end_turn` when:
1. It believes the current input has been processed (has output reply + all tool calls)
2. **It may incorrectly judge "I've answered everything"** — especially when goals are complex and require multi-round collaboration
3. **Max token limits** — if single-turn max_tokens is small, the model may be truncated

This explains Claude Code's observable behaviors:

| Behavior | Root Cause |
|----------|-----------|
| "Stops before completing" | API returns `stop_reason: end_turn`, Claude Code believes the turn ended |
| "Asks user if they want to continue" | No more tool_use in the turn, so it stops |
| "Tells me to modify the prompt myself" | Cannot autonomously extend the turn — must wait for user message |
| "Forgets after multiple turns" | Context window full, old content compressed/summarized |

---

## 5. Strategies for Overcoming the Limitation

### 5.1 Strategy A: Stop Hook (Claude Code approach)

**Principle**: Intercept at session exit, inject new prompt.

**Pros**: Can block exit; no core code modification needed.
**Cons**: Requires external script; complex state management; error-prone (file corruption, session_id mismatch).

**Ralph Loop implementation**:
```
1. Stop hook checks state file existence
2. Checks session_id match
3. Checks completion promise
4. Checks max iterations
5. All pass → block + inject prompt
```

**Limitations**: Single prompt (no dynamic adjustment); no priority/sub-goals; state file management complexity; `<promise>` is string matching, not semantic understanding.

### 5.2 Strategy B: Prompt-based Task Persistence

**Principle**: Declare task list in system prompt; LLM self-maintains state.

**Pros**: No hooks needed; fully prompt-based.
**Cons**: Depends on LLM self-awareness; may forget tasks (context window limits).

### 5.3 Strategy C: Built-in Completion Detection

**Principle**: LLM level supports "I have more work to do" signal.

**Pros**: Most native; most reliable.
**Cons**: Requires LLM + framework modification.

### 5.4 Strategy D: Loop Wrapper

**Principle**: Shell script loops launch Claude Code.

**Pros**: Simple and reliable.
**Cons**: No cross-session persistence; each launch is a new session.

---

## 6. Experimental Protocol: Verifying Prompt-based Questioning Stability

To address the companion research question (how to stably激发 questioning style via prompts), we propose the following experiment:

**Hypothesis**: Structured questioning prompts maintain higher questioning rates across multiple turns than role-constrained prompts.

**Method**: Run Ralph Loop with 5 different prompt configurations, measure questioning rate per turn over 20 turns.

| Group | Prompt Type | Expected Questioning Rate |
|-------|------------|--------------------------|
| A | Default (helpful assistant) | 0% |
| B | Questioner role | 20-40% |
| C | Few-shot examples | 40-60% |
| D | Structured output (questions before answers) | 60-80% |
| E | D + negative constraints | 70-90% |

**Metric**: Number of questions per response / analysis length per turn.

**Expected result**: Group A stays near 0%. Group B shows initial elevation but degrades after ~5 turns. Group C maintains questioning for ~10 turns. Group D and E show sustained questioning across all 20 turns, with E showing highest stability.

**Validation**: This experiment should be run in a Ralph Loop session with the stop hook active. Each turn's output should be logged, and questions counted via regex matching (question marks in analytical context, not rhetorical or punctuation-only).

---

## 7. Conclusions

1. **"Stop before complete" is not a bug — it is an architectural necessity** of turn-based LLM systems. The `stop_reason` mechanism is turn-level, not goal-level.

2. **All three systems lack completion detection**. The decision to continue or stop is always external to the LLM.

3. **Stop hooks are the most robust current solution** for maintaining autonomous operation, but they have limitations in flexibility and semantic understanding.

4. **The gap between turn-processing and goal-execution** is fundamental and can only be closed by either (a) external loop mechanisms or (b) architectural changes to how LLM APIs signal completion.

---

## References

1. Anthropic API documentation — `stop_reason` field specification
2. Claude Code source — stop hook implementation
3. Claude Code binary strings — extracted from `/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`
4. OpenAI Codex documentation — goal execution model
5. Hermes Gateway Hook source — `gateway/hooks.py`, `agent/plugin_hooks.py`, `agent/shell_hooks.py`
6. Yao et al. 2023 — Tree of Thoughts
7. Sakaguchi et al. 2023 — Graph of Thoughts
8. Google DeepMind — Self-Ask Prompting
