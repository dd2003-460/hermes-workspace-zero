# Iteration 322: Scheme 3 - CLAUDE.md Constraints for Dynamic Workflow

## Action
- Added "动态工作流强制执行 (Scheme 3: CLAUDE.md 约束)" section to workspace CLAUDE.md
- Section enforces state-driven workflow with `ralph-loop.global.md` fields
- Requires verification of `last_output_hash` change, `iteration` update, `loop_phase` stage adherence

## Implementation Details
- Location: `/Users/a1-6/Desktop/workspace/CLAUDE.md` (lines appended before "会话最小阅读链路")
- Contains: state validation rules, non-skippable flow rules, per-round constraints
- Complement: works alongside existing 1-loop (line 29) and 2-loop (line 31) constraints

## Status
Scheme 3 (CLAUDE.md constraints) deployed. This is stronger than scheme 2 (hooks) because CLAUDE.md is read at session start and cannot be bypassed by the model.
