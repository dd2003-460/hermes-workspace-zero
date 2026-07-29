---
name: ralph-stage-executor
description: Execute, recover, and verify any field-centric RALPH loop stage. Use when a project has loop-state.json or a user asks to run ralph, complete a research/validation/DAG stage, recover stalled field agents, gather browser-LLM cross-checks, or produce a phase-complete final result.
---

# RALPH Stage Executor

Use the runtime as the source of truth. This skill supplies the working
discipline; `ralph` validation remains the authority.

## Start every turn from durable state

1. Run `ralph field-status .`; do not reconstruct the phase from chat memory.
2. Identify the current `stage.id`, `revision`, ready field task, and required
   output roles.
3. If a `research_required` task is ready, dispatch exactly one Agent whose
   first prompt line is `RALPH_FIELD_TASK=<task path>`. Do not read its task
   file or merge it with other research questions in the Commander context.
4. If no research task is ready, run `ralph field-init .`, edit only the
   current stage's `fields.json`, then run `ralph field-apply . <fields.json>`.

Never modify `loop-state.json` directly. Never call a stage complete because
the prose sounds plausible: submit the artifact and let `ralph` validate it.

## Flow-only experiments

When the runtime says `flow-only`, `test_flow`, or that no actual web research
is required, treat the stated fictional/local inputs as closed-world test data:

- Do not call web tools and do not create `research_required` fields solely
  because a fictional system lacks real-world sources.
- Use `disposition=inferred`, an explicit “仅用于验证流程” rationale, and
  `evidence_refs=[]` for the synthetic details required to exercise a stage.
- Still create the required structured artifacts, apply them through `ralph`,
  and let the normal phase validators reject malformed fields/DAGs.

## Process one field completely

For a current fact, obtain a claim-level HTTPS source and record the exact URL,
observation time, claim, and uncertainty. A homepage, search snippet, model
memory, or unverified marketplace claim is not evidence.

After at most two failed WebSearch/WebFetch attempts:

1. Save the field as `research_required` with empty `evidence_refs` and a
   concise failure rationale.
2. Run `ralph field-apply . <task-file>` so the work becomes durable.
3. If the task remains `dispatched` after a successful apply, run
   `ralph field-reconcile .`; this preserves the draft and reopens it instead
   of deleting context or faking completion.
4. When browser LLM is globally authorized, use `ralph web-llm-check` only to
   obtain source leads and a receipt. Read the exact primary/authority pages
   before using any lead as evidence.

## Phase contracts

| Phase | Required proof before advance |
|---|---|
| 01 | Distinct goal, known, and unknown fields; unknowns are split into research leaves. |
| 02 | Every external claim has exact dated evidence; unresolved claims remain explicit research fields. |
| 02.5 | Each important claim has a validation record with two independent, specific sources and a supported/contradicted/uncertain verdict. |
| 03 | A structured DAG with dependencies and output paths; every node produces its declared artifact and is completed by `ralph graph-apply`. |
| 04 | Verify each executable result against its acceptance criterion and retain artifact references. |
| 04.5 | Independently cross-check conclusions, enumerate contradictions, and state residual uncertainty. |

Advance only by writing the current stage's `advance.json` and running
`ralph apply . <advance.json>`. If validation rejects it, repair only the
listed field or artifact; preserve all accepted work.

## Finish a user-facing task

Before saying a task is complete, run `ralph field-status .` and confirm that
the current phase has no required ready/pending/research fields or incomplete
DAG nodes. Deliver a concise result with:

- recommendation or decision;
- evidence URLs and observation dates for current facts;
- artifacts and reproducible commands;
- unresolved items and their impact.

If a required source remains unavailable, report the task as incomplete. Do
not replace missing evidence with confident language.
