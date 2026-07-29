---
name: ralph-prompt-first
description: Run a RALPH task through short Markdown stages in one continuous Claude session. Use for research, writing, planning, and implementation work that needs durable progress without field schemas or per-tool gatekeeping.
---

# RALPH Prompt-First

`ralph-loop.md` names the sole current Markdown artifact and stage. Read it,
but never edit it: the Stop Hook alone maintains its mechanical cursor. Then
write the complete current stage document.

- Never create `loop-state.json`, field tasks, DAG JSON, or stage-result JSON.
- First substantive entry: `Write` the whole current Markdown file with a
  title and useful content. Use `Edit` only for later changes; on any Edit
  failure, immediately return to `Write` rather than reporting the error.
- Use the current prompt's stage requirements. For external claims, record
  source/date/observation/uncertainty. A browser/Playwright web-LLM response is
  a lead, not invented evidence. In stage 02, run exactly `ralph prompt-first
  web-llm .` once before generic web search; record its Markdown receipt or a
  truthful tool/login/page failure. If all providers fail, record that and move
  directly to the next section; do not start WebSearch/Fetch. A zero-result
  search is not evidence.
- When the current Markdown is genuinely ready, append exactly
  `<!-- ralph: done -->` on its own line. The Stop Hook then supplies the next
  stage in the same Claude session. It does not grade semantics. The marker is
  the final write of this turn: stop immediately after it; never start a later
  stage or browse for it before the hook advances the cursor. Record uncertainty
  in Markdown; never delete a marker after writing it for self-review.

Ordinary project reads and writes are allowed. Do not fabricate sources,
browser actions, or results.
