# Web LLM Receipt: Perplexity

- **Service**: Perplexity AI (online, requires login)
- **Final URL**: `https://www.perplexity.ai/s/...` (search result page, exact ID in session)
- **Observation Time**: 2026-08-15 ~04:00 UTC+8
- **Tool**: ego-browser (Playwright chromium)
- **Query**: "你了解 prompt-first 或 declarative 方式的 agent 框架吗？与 code-based agent 相比，纯 prompt 定义的框架在状态管理、错误处理、DAG 依赖方面有什么局限？请给出具体例子和来源。"

## Response Summary

Perplexity provided a detailed comparison between prompt-first/declarative agent frameworks and code-based agent frameworks across three dimensions:

### 1. State Management
- **Prompt-first**: Uses implicit state in conversation history. State is "remembered" by the model's context window. No versioning, no checkpoints, no rollback.
- **Code-based**: Explicit state objects, databases, checkpoints, versioned schemas. Can save/restore, compare versions, rollback.
- **Concrete example**: In a multi-step review pipeline, prompt-first must re-send all prior messages to maintain context; code-based loads a state object from disk.

### 2. Error Handling
- **Prompt-first**: Relies on model judgment for failure/retry/recovery. No exception types, no retry strategies, no timeouts.
- **Code-based**: Exception types, retry strategies, timeouts, fallbacks, compensation logic.
- **Concrete example**: If an API call times out, code-based can distinguish timeout vs auth error and retry with backoff; prompt-first just sees "no result" and may misinterpret.

### 3. DAG Dependencies
- **Prompt-first**: Dependencies are written in text for the model to decide. No guaranteed topological order.
- **Code-based**: Nodes, edges, joins, conditions, topological order guaranteed by the program.
- **Concrete example**: A parallel review pipeline with `gather()` ensures all branches complete before merge; prompt-first may skip a branch or merge early.

### 4. Concrete Counterexample: Reimbursement Approval
Perplexity provided a detailed scenario where a prompt-only agent might:
- Misinterpret a timeout as "no violation"
- Parse "10,000" as 10000 or 10
- Use an old version of the invoice for budget check
- Enter ERP before compliance branch returns
- Duplicate write due to retry without idempotency

### 5. Assessment
Perplexity concluded that prompt-first frameworks have **fundamental limitations** in state management, error handling, and DAG orchestration that cannot be solved by better prompting alone. These are structural issues requiring runtime semantics.

## How This Was Used
This response directly informed the RALPH Loop stage 02 research on prompt-first vs code-based agent implementations. The findings corroborate the source code analysis that:
1. DAG validation (cycle_check, write_conflict, parallel_group) is code-only in `dag.py`
2. Field schemas and atomic field-apply require programmatic guarantees
3. Prompt-first cannot replicate structural guarantees

## Evidence
- Full snapshot text captured via `snapshotText()`
- Response URL: perplexity.ai search result (exact URL in browser session)
- Screenshot attempt failed (CDP timeout), but snapshot is sufficient audit evidence

## Verdict
**PASS** - Perplexity provided a substantive, well-structured response with concrete examples and code snippets. The response is consistent with the source code analysis findings.
