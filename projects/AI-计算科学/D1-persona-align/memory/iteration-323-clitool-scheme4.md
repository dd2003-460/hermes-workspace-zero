# Iteration 323: Scheme 4 - Tool-Based State Management (ralph-loop CLI)

## Action
- Created `/Users/a1-6/Desktop/workspace/loop/scripts/ralph-loop.sh` — a CLI tool for managing ralph-loop state machine
- 5 commands: `check`, `advance`, `status`, `validate`, `save-state`

## Implementation Details
- **check**: validates that iteration, last_output_hash, and loop_phase are all set
- **advance**: increments iteration by 1, resets hash (prevents re-execution)
- **status**: displays current loop state (all fields)
- **validate**: checks stage file completeness for current loop_phase (1-loop/2-loop)
- **save-state**: creates backup snapshot to ~/.claude/ralph-loop.state.d/

## Test Results
- `ralph-loop.sh status` — OK (shows iteration 323, phase idle)
- `ralph-loop.sh validate` — OK (idle phase, no stage files required)
- `ralph-loop.sh check` — OK (hash verified, iteration valid)

## Status
Scheme 4 (tool-based state management) deployed and verified. All 4 dynamic workflow schemes are now implemented.
