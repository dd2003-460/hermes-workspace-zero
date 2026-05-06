---
active: true
iteration: 0
session_id: ""
max_iterations: 100
completion_promise: ""
started_at: "2026-04-30"
last_action: ""
last_outcome: "start"
last_insight: ""
---

# Ralph Loop — Thinking Framework (Not Task List)

## Navigation (What to Read)

```
├── .claude/bootstrap.md          ← Work compass (read first for context)
├── AGENTS.md                     ← Global principles (red lines)
├── .claude/memory.md             ← Session memory (compact)
├── .claude/ralph-loop.config.md  ← THIS file (read for lessons)
├── raw/INDEX.md                  ← Raw idea indices
│   ├── raw/math.md
│   ├── raw/ai/ai_information_theory_optimization.md
│   └── raw/social/math_social_cross.md
├── loop/loop.md                  ← Work principles and progress
├── loop/theory/                  ← Theory documents (when they exist)
├── loop/experiment/              ← Experiment designs
└── D1-memory/exploration/        ← Generated exploration records
```

**Rule**: Always read `memory.md` → then `bootstrap.md` → decide.

## Decision Principles (How to Think)

### 1. When to Deepen vs Redirect

| Signal | Action |
|--------|--------|
| Last action succeeded with no blocker | Deepen same thread by 1 level |
| Last action had partial success | Switch to address blocker |
| Last action could not start (no data) | Find working subset |
| Working for 3+ rounds without breakthrough | Must redirect to different thread |
| Output quality degradation | Change approach, don't continue |

### 2. What Counts as "Repetition"

NOT repetition (allowed):
- Same file, different level of detail
- Same topic, different angle/question
- Verification/confirmation of previous work

IS repetition (must avoid):
- Updating the same progress marker
- Formatting/sanitizing without content change
- Reading the same files without new reading intent
- Iterating on unfinished work past obvious failure point

### 3. When to Stop (Completion Criteria)

<stop-priority>
1. `has_blocker_and_no_solution` — True blocker with no path forward after 2 attempts
2. `completion_promise_met` — Original task + all follow-ups done
3. `diminishing_returns` — Last 3 iterations changed nothing substantive
</stop-priority>

## Lessons Compression (How to Remember)

Format: `Date | Iter: X-Y | [type] observation → action_rule`

Types:
- `[blocker]` — Tool/API/resource limitation
- `[pattern]` — Something that worked consistently
- `[mistake]` — What to avoid next time
- `[insight]` — Non-obvious finding

**Compression**: Only keep lessons. Delete "completed" lesson references. Keep maximum 5 lessons.

## Work Threads (Pick One)

> Do not multi-thread. Pick one, go deep, note handoff position.

```
Thread A: Raw idea → exploration record conversion
Thread B: Theory development (e.g., D2-1 planning capacity)
Thread C: Experiment design + verification
Thread D: New hypothesis generation
Thread E: Research gap identification
```

## Stop Criteria Override

Default `completion_promise`: `""` (disabled — loop continues until manual stop or 100 iterations)

Set `completion_promise` when you have a specific verifiable statement.
