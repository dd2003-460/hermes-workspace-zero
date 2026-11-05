# Efficiency Bottlenecks Log

## 2026-11-06: Arena GitHub App Token 403

**Symptom**: `git push` to arena-hosted branches (e.g. `arena/78602cd5-prompt-first-bench`) returns 403 Forbidden. Local commits succeed; remote sync fails.

**Root cause (hypothesis, conf ~0.7)**: The GitHub App token used by arena's agent mode has expired or lost write scope on the target repo. Arena creates feature branches and commits locally within its sandbox, but the final push-back step requires a valid installation token with `contents:write` permission on the specific repository.

**Impact**: T33/T36 full JSONL artifacts and patches remain in arena local commits only. Data integrity was verified via conversation text extraction (scores, verdicts, per-assertion details), but raw artifact files are inaccessible without token fix.

**Workaround applied**: Extract key data from arena conversation transcripts → commit locally → push to our own fork (`dd2003-460/prompt-first-bench`). Lossy but sufficient for paper-draft purposes.

**Fix path**: 成璐 needs to re-authorize the GitHub App installation for the `prompt-first-bench` repo in arena settings, OR provide a PAT with `repo` scope that arena can use for push.

**Status**: Open. Blocks full artifact retrieval from arena sessions.
