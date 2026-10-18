# origin: ai
# R2 findings — D1-think-token-budget (full 12-task sweep)

## Goal
Reduce surfaced thinking (decode-time proxy) WITHOUT hurting accuracy,
ideally via ADAPTIVE thinking (budget by difficulty + reversibility).

## Method
- Subagent surfaced text = sent-to-parent message + closing message (BOTH are
  model-generated decode output). Chars ≈ tokens/4. Raw capture convention:
  `results/round2/raw/<COND>__<TASK>.txt` = sent + blank line + closing.
- 3 treatments (P2/P4 deferred): P0 baseline (step-by-step), P1 minimal
  (answer only), P3v2 adaptive-v2 (strict LEVEL + level-sized reasoning +
  own-line FINAL; fixes R1's P3 format drop + meta-narration).
- 12 AIME-style tasks: T01-T03 easy, T04-T07 medium, T08-T12 hard
  (ground truth python-computed in tasks/taskset.py; ALL SELF-TESTS PASS).
- Scorer: tasks/scorer.py → results/round2/scores.csv
  (acc = FINAL parsed anywhere/unanchored = realistic deployment parse;
  fmt = strict OWN-LINE FINAL flag, separate from acc).
- Prompt files materialized: prompts/generated/<COND>__<TASK>.prompt.txt (36)
  via tasks/gen_prompts.py.

## R2 frontier table (12 tasks)
| cond     | n  | acc  | fmt% | mean_chars | mean_toks |
|----------|----|------|------|------------|-----------|
| P0 baseline   | 12 | 100% | 75% | 503.1 | 126 |
| P1 minimal    | 12 | 100% | 75% | **167.2** | **42** |
| P3v2 adaptive | 12 | 100% | **92%** | 338.9 | 85 |

### Per-difficulty mean chars (P0 / P1 / P3v2, and P0:P1 ratio)
| diff   | P0     | P1     | P3v2    | P0:P1 |
|--------|--------|--------|---------|-------|
| easy   (T01-03) | 362.0 | 115.3 | 205.7 | 3.14× |
| medium (T04-07) | 643.5 | 214.8 | 465.2 | 3.00× |
| hard   (T08-12) | 495.4 | 160.4 | 324.2 | 3.09× |

## Key findings (R2)
1. **Decisive test PASSED: P1 (answer-only) holds 100% accuracy on ALL 12
   tasks including all 5 hard tasks** (T08=819, T09=96, T10=9, T11=66,
   T12=39). Skipping reasoning did NOT cost accuracy on this AIME-lite set.
   P1 = 3.01× shorter than P0 (167.2 vs 503.1 chars) at identical accuracy.
2. **The baseline verbosity gap is ~3× UNIFORM across difficulty** (3.00–3.14×
   easy/med/hard). The cost of "show your work" is NOT concentrated on hard
   problems — so difficulty-adaptive budgets gain little over flat-minimal on
   this task distribution.
3. **P3v2 (adaptive-v2) did NOT beat P1.** Best format (92%) but 2.03× longer
   than P1 at equal 100% acc. The adaptive benefit was unrealized:
   - on easy, P1 is already minimal (P3v2 adds LEVEL+FINAL overhead);
   - on medium/hard, P3v2 still full-reasons (sometimes DOUBLE-derives:
     T04=556ch sent+re-derive, T06=856ch with ~300ch of closing
     META-narration about whether it followed the format);
   - strict format rules INDUCE new ineffective thinking: the model spends
     tokens worrying about format compliance, not the task (T06 closing:
     "actually, I should check — the previous message included 'LEVEL: easy /
     FINAL: 199'... the instructions said the last line must be exactly...").
   - strict rules also mis-fire: T05 fmt=N (dropped both LEVEL and FINAL).
4. **Format compliance is a prompt-independent weakness, not an answer-only
   weakness.** P1 dropped OWN-LINE FINAL on 3/12 (T07, T08, T10) — same rate
   as P0 (T03, T09, T11). Answers were still correct in every case (acc
   parses FINAL anywhere or last number). If the deployment parser is lenient
   (searches for FINAL anywhere / last number), P1's fmt% is a non-issue; if
   it requires own-line FINAL, both P0 and P1 need a P5 reinforcement
   variant ("last line of your reply MUST be exactly 'FINAL: <answer>'").
5. **Hard tasks pull reasoning back even under answer-only** (reconfirmed R1):
   P1 leaked short derivations in parens on T08/T09/T10 — but cheaply
   (hard mean 160.4ch) with zero accuracy loss.
6. **Closing-stream re-derivation is the waste pattern** the existing
   thinking-budget.md termination rule targets (回头重论证 / 每个推理步只写一次):
   P0 re-derives in BOTH streams (T04 sent 119 + closing 261; T05 double);
   P1 re-derives on medium (T04 closing 317ch = "Let me verify: 333, 66,
   333-66=267") but not on easy/hard; P3v2 double-derives on T04/T06.
   Single-stream deployment this shows as "derive… wait, let me check…
   derive again". A prompt-level lever: append the termination rules
   (conclude→act; no "wait/actually/let me verify"; each step written once)
   as a P5/P6 test.

## Bug log (scorer/taskset fixes this round)
- `re.findall(r"-?\d+(\.\d+)?")` capturing group → findall returned group
  matches `['','','']`; fixed to group-free `r"-?\d+\.?\d*"`.
- `_frac` no-FINAL fallback took LAST NUMBER → "28" for "3/28"; fixed: if
  FINAL line exists search it, else search whole text for LAST fraction
  `r"(\d+)/(\d+)"`, only then fall back to _num.
- Line-anchored `FINAL` in _clean/_frac made P0 T11 (FINAL mid-line, math
  correct) score acc=N via fallback grabbing "12" from C(12,2); fixed: acc
  parsing now searches FINAL ANYWHERE (unanchored, last occurrence) =
  realistic deployment regex; has_final stays line-anchored for the strict
  fmt flag.
- Self-test escape typo: ok-line used real `\n`, print line used literal
  `\\n` (one line → false "FAIL" label); fixed with shared own/mid vars.
- After all fixes: `python3 tasks/taskset.py` → ALL SELF-TESTS PASS
  (12 main + 3 fallback + has_final own/mid).

## State / next (R3)
- R2 = conclusive on THIS set: P1 minimal = recommended prompt for
  decode-minimal subagent dispatch (100% acc, 3.0× shorter, 42 tok mean).
  Caveat: task set is AIME-lite (answer verifiable by exact match); R3 must
  stress-test with genuinely hard, error-prone items from the HF official
  benchmark for qwen3.8-27b to find where P1's 100% breaks (that boundary
  is where adaptive budgeting may actually pay off).
- Candidate follow-up treatments: P4 wordcap (≤15 words); P5 = P1 +
  last-line-FINAL reinforcement + termination rules (kill closing
  re-derivation); P6 = P5 + explicit "do not re-derive; one pass".
- Safety: R3 = read-only benchmark fetching + subagent prompt tests + local
  python only. No server/deploy actions, no AGENTS.md edit.
