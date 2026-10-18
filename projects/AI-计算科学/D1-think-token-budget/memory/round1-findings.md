# origin: ai
# R1 pilot findings — D1-think-token-budget

## Goal
Reduce surfaced thinking (decode-time proxy) WITHOUT hurting accuracy,
ideally via ADAPTIVE thinking (budget by difficulty + reversibility).

## Method
- Subagent surfaced text ≈ output/decode-token proxy (chars ≈ tokens/4).
- 5 prompt treatments (see prompts/conditions.md): P0 baseline, P1 minimal,
  P2 oracle, P3 adaptive, P4 wordcap.
- 12 AIME-style tasks (easy3/med4/hard5) with python-computed ground truth.
- R1 = 2-task pilot (T01 easy arith, T09 hard combinatorics) × P0/P1/P2/P3.
  R1 is a SIGNAL, not a conclusion — R2 = full 12-task sweep.

## R1 frontier table (2 tasks: T01 easy + T09 hard)
| cond | acc | fmt% | mean_chars | mean_toks | notes |
|------|-----|------|-----------|-----------|-------|
| P0 baseline   | 100% | 100% | 468.0 | 117 | full step-by-step |
| P1 minimal    | 100% | 100% | 91.0  | 23  | **shortest + compliant** |
| P2 oracle     | 100% | 100% | 161.5 | 40  | still ran a cross-check on hard |
| P3 adaptive   | 100% | **0%** | 640.5 | 160 | adapted length (short easy / long hard) BUT dropped FINAL: on both, meta-narration on hard |

## Key findings (R1)
1. **Answer-verbosity is the big cuttable source.** P0→P1 cuts mean chars ~5.1×
   (468→91) at identical 100% accuracy and 100% format compliance, on both an
   easy and a hard task.
2. **P1 (minimal) is the current winner** on this pair: 91 chars, 100% acc,
   100% fmt. Even the hard task T09 came in at ~74 chars.
3. **P3 (adaptive) adapted correctly but REGRESSED on format.** It produced
   short output on easy (74ch) and full reasoning on hard (1207ch) — the
   adaptive-by-difficulty behavior we want — BUT:
   - dropped the `FINAL:` line on BOTH runs (0% fmt) → a pipeline parsing
     `FINAL:` would lose the answers;
   - on the hard task it was LONGER than even the P0 baseline (1207 vs 754),
     because the "LEVEL:" framing induced meta-narration ("This is a math task
     delegated to me", "The parent's ID is already given").
4. **Hard tasks pull reasoning back** even under answer-only prompts (P2 oracle
   still cross-checked T09). So "answer only" holds accuracy here but the
   model re-invests effort on hard items.

## Open questions / R2 plan
- Does P3's adaptive advantage show up ACROSS the difficulty spectrum (i.e. does
  saving a lot on many easy/med tasks outweigh going long on hard ones)? R1's
  1-easy+1-hard sample is too small / biased to say.
- **P3 prompt must be tightened before R2:** force the `FINAL:` line (it is the
  pipeline's answer carrier) + explicitly forbid role/meta narration.
- R2 = full 12-task sweep of P0/P1/P3 (and P2/P4 if signal justifies),
  waves of 3 (active-child limit).

## Bug log
- `re.findall(r"-?\d+(\.\d+)?", s)` returns the CAPTURING GROUP matches, not
  the full match → for integers (no decimal) it returns `['','','']`, so
  `nums[-1]` = `''` and the no-FINAL fallback silently returned empty.
  Fix: group-free pattern `r"-?\d+\.?\d*"` in taskset.py `_clean` (line ~94).
