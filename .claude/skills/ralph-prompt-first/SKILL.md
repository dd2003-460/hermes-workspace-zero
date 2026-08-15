---
name: ralph-prompt-first
description: Run a RALPH task through short Markdown stages in one continuous Claude session. Use for research, writing, planning, and implementation work that needs durable progress without field schemas or per-tool gatekeeping.
---

# RALPH Prompt-First

`ralph-loop.md` is the durable stage cursor; never edit it. Runtime injects the
current task, target, and external stage rules. Because Claude Code's `Write`
requires a prior `Read`, read the current artifact once, then use the
PostToolUse reminder to write the complete Markdown artifact. Do not narrate a
plan or create JSON field/DAG state.

Follow the injected stage rules and record real sources, dates, observations,
and uncertainty. A browser/Playwright web-LLM response is a lead, not evidence.
After substantive writing, stop. The Stop Hook launches the independent
read-only Reviewer. Do not run it manually, append the done marker before a
matching Reviewer pass, or start the next stage yourself. On `revise`, use the
latest review to repair its declared stage in the same session. Prefer one
complete `Write` of the current Markdown over patch-style `Edit` calls, then
stop for a new automatic review.

Never write a `ralph-review` routing block or a self-authored `verdict` into
the stage Markdown. The runtime owns review receipts; the stage artifact is
only for the work, sources, evidence, uncertainty, and repair record.
