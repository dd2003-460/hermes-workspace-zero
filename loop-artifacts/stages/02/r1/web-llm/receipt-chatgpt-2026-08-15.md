# ChatGPT Receipt: Prompt-first vs Code-based Agent Frameworks

- **Service**: ChatGPT (GPT-4, online, requires login)
- **Final URL**: `https://chatgpt.com/c/6a800022-ef90-83ee-b792-4f7ff7646cb6#main`
- **Observation Time**: 2026-08-15 ~05:00 UTC+8
- **Tool**: ego-browser (Playwright chromium)
- **Query**: "你了解 prompt-first 或 declarative 方式的 agent 框架吗？与 code-based agent 相比，纯 prompt 定义的框架在状态管理、错误处理、DAG 依赖方面有什么局限？请给出具体例子和来源。"

## Response Summary

ChatGPT provided an extensive analysis (Level 1-3 architecture) covering four key dimensions:

### 1. State Management
- **Prompt-first**: Uses semantic state ("I believe we have completed steps 1-6") — not durable, not authoritative
- **Code-based**: Uses durable state (`video_generated = true`, checkpoints, resume capability)
- **Concrete example**: Video rendering pipeline — if Step 2 (upload) fails, code-based resumes from checkpoint; prompt-first regenerates everything
- **Key insight**: "LLM can propose state transitions, but runtime decides whether to accept them"

### 2. Error Handling
- **Prompt-first**: Compresses complex exception taxonomy into a single natural language rule ("try again")
- **Code-based**: Hard constraints on retry count, timeout, fallback, error handlers
- **Concrete example**: `TimeoutError` vs `AuthenticationError` vs `InvalidInput` — each requires different handling (retry after 30s, ask human, do not retry)
- **Reference**: LangGraph fault-tolerance docs treat retries/timeouts/fallbacks as core capabilities

### 3. DAG Dependencies
- **Prompt-first**: Dependencies are scheduler constraints the model "decides" to follow — may execute out of order, repeat nodes, or skip
- **Code-based**: Runtime knows which nodes are done/blocked — won't execute Synthesis until both Research A and B complete
- **Concrete example**: Parallel execution — code-based runs A/B/C concurrently; prompt-first is naturally sequential reasoning loop
- **Reference**: LangGraph nodes + edges with deterministic execution guarantees

### 4. Verifiability
- **Prompt-first**: "All sources verified" is just a model statement — no deterministic check
- **Code-based**: Deterministic validation → state transition → LLM confirmation
- **Key insight**: Production systems form a chain: deterministic check → state transition → LLM says it's okay

### 5. Architecture Assessment
ChatGPT proposed a 3-level hierarchy:
- **Level 1**: Prompt-first (weak state/error/DAG/verifiability)
- **Level 2**: Declarative + Runtime (prompt describes semantics, runtime guarantees execution)
- **Level 3**: Dynamic Agent + Explicit State Machine (LLM planner + state machine + checkpoint)

**Key recommendation**: "If order/state/failure behavior affects money, data, time, or external consequences, don't leave it to prompt alone."

### 6. Concrete Reference Examples
- OpenAI Agents SDK: Runner handles turns, tool execution, guardrails, handoffs, sessions
- Microsoft Magentic-One: Orchestrator with Task Ledger + Progress Ledger + stall detection
- LangGraph: durable execution, fault tolerance, parallel node execution

## How This Was Used
This response corroborates and extends the Perplexity findings with:
1. More detailed error taxonomy (5 distinct error types with different handling strategies)
2. Explicit 3-level architecture hierarchy (prompt-first → declarative+runtime → dynamic+state machine)
3. Concrete production examples (OpenAI Agents SDK, Magentic-One, LangGraph)
4. The "policy vs control flow" framing: Prompt = policy/intent, Code = control flow, State store = truth, Runtime = execution

## Evidence
- Full snapshot text: `chatgpt-snapshot.txt` (72,664 bytes)
- Conversation URL: `https://chatgpt.com/c/6a800022-ef90-83ee-b792-4f7ff7646cb6#main`
- Send mechanism: JS click on `button[data-testid="send-button"]`
- Note: ChatGPT may also make errors. Verify important information.

## Verdict
**PASS** — ChatGPT provided a highly substantive, well-structured response with concrete examples, framework references, and a clear architecture hierarchy. The response is consistent with and extends the Perplexity findings.
