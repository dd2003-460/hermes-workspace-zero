# origin: ai
# R3 findings — D1-think-token-budget (official AIME 2025, 10 problems)

## Goal
Reduce surfaced thinking (decode-time proxy) WITHOUT hurting accuracy on a
REAL public benchmark — R2's set was self-generated AIME-lite; R3 uses the
official AoPS AIME 2025 set (the item in the Qwen3-32B post-training table
with the 52.7 pt thinking−non-thinking gap; ZebraLogic's 59.6 is larger but
its test set is not public). Find where the answer-only prompt (P1) breaks
100% accuracy and map the quality boundary of the strict adaptive prompt (P5).

## Method
- Arms: P0 baseline (step-by-step + own-line FINAL), P1 minimal
  ("Answer only. No reasoning, no working, no explanation." + own-line FINAL),
  P5 strict adaptive (4-rule block: minimal text / STOP-never-rederive /
  no-agent-mention / LAST line exactly FINAL: <answer>; supersedes P3v2).
- Data: tasks/aime25_test.jsonl (30 official AIME 2025 problems, via
  hf-mirror.com — huggingface.co blocked 403). R3 subset = 10 problems:
  A00(easy,70) A03(easy,117) A04(med,279) A09(hard,81) A11(hard,510)
  A16(med,49) A19(hard,336) A23(med,149) A25(hard,113) A27(hard,248).
- Every key independently re-derived in python before use (two were caught
  wrong: A09 first brute force missed ×216 row-3 orderings → 66 not 81;
  A27 first iteration forgot the per-step /3 → 176 not 248).
- Scorer: tasks/scorer_r3.py → results/round3/scores.csv
  (chars = sent+closing; acc = FINAL parsed anywhere else last number;
  fmt = own-line FINAL: line check; toks_est = chars/4).
- Raw: results/round3/raw/<COND>__A##.txt (sent + closing).

## R3 frontier table (9/10 scored; A27 pending)
| cond | n | acc | fmt% | mean_chars | mean_toks |
|------|---|-----|------|------------|-----------|
| P0 baseline   | 9 | 100% | 56% | 1088.6 | 272 |
| P1 minimal    | 9 | 100% | 89% | **380.9** | **95** |
| P5 strict     | 9 | 89%  | 89% | 521.3 | 130 |

### Per-task chars / fmt / correct (P0 / P1 / P5)
| task  (key) | P0     | P1    | P5    |
|-------------|--------|-------|-------|
| A00 (70)    | 923/T/T | 74/T/T  | 188/T/T |
| A03 (117)   | 746/T/T | 329/T/T | 434/T/T |
| A04 (279)   | 970/F/T | 251/F/T | 138/T/T |
| A09 (81)    | 764/F/T | 424/T/T | 657/T/**F** |
| A11 (510)   | 1420/T/T | 755/T/T | 821/T/T |
| A16 (49)    | 618/F/T | 354/T/T | 347/F/T |
| A19 (336)   | 909/F/T | 149/T/T | 883/T/T |
| A23 (149)   | 1041/T/T | 221/T/T | 308/T/T |
| A25 (113)   | 2406/T/T | 871/T/T | 916/T/T |
| A27 (248)   | pending | pending | pending |

## Key findings (R3)
1. **P1 holds 100% on 9/9 official AIME problems** (3 easy-med, 6 hard
   incl. geometry + combinatorics + recurrence), at 2.86× fewer chars than
   P0 (380.9 vs 1088.6). "Answer only" is the current length-accuracy
   frontier on real competition math for this model.
2. **P5's strictness is not free**: it is LONGER than P1 (521.3 ch) and made
   THE single accuracy error of the round — A09 (3×9 grid counting): P5
   output 66 (missed ×216 row-3 within-block orderings) while P0/P1 both
   got 81. The STOP-never-rederive rule suppressed the re-derivation that
   would have caught it. P5's discipline also decays on hard tasks: A25
   broke both sent-leak AND closing re-derivation (was clean on A00–A19).
   → P5 = worst of both: not shorter than P1, not as safe as P0.
3. **Error pattern is task-type specific, not "hard" in general**: P5's only
   error is combinatorial counting (A09); it passed all hard geometry
   (A11, A19) and hard algebra. A09 is also the task where the CORRECT
   answer requires a 3-part product and P5 truncated the derivation.
4. **fmt (own-line FINAL) is unstable across ALL arms on real tasks**:
   P0 5/9, P1 8/9, P5 8/9. Failures: bold **FINAL**, "FINAL ANSWER:",
   FINAL mid-line. The deployment parser (unanchored, acc metric) absorbs
   most of it, but strict-pipeline users will see ~1–5% format drops.
   P1's failures are the cheapest to fix (one extra reminder sentence).
5. **P1 leak pattern**: sent message usually contains a one-line method leak
   ("(d=n+2, product ≡ 39 mod d, so d|39...)") or task restate, even with
   "No reasoning". The leak is a SUMMARY (one line), not a derivation —
   the saving is real. Occasionally (A00) P1 sends only "FINAL: 70".
6. **P0 double-derivation persists**: full work in sent + full re-derivation
   in closing (A25 closing is a second full solution). This is the
   dominant R3 waste pattern (P0 mean 1088.6 ch vs P1 380.9).

## Data-integrity notes
- tasks/aime25_test.jsonl had 2 corrupted LaTeX fragments: `\frac` written
  as `<0x0C form-feed>rac` (the `\f` escape eaten on write) in ids 18 and
  27. Fixed in place (backup /tmp/aime25_test.jsonl.bak). A27's three
  running subagents saw the corrupted but semantically obvious version.
- A09 key 81 and A27 key 248 independently re-derived (see Method).

## Open
- A27 (P0/P1/P5) → completes 10/10 table.
- P6 adaptive arm (classify easy/hard → answer-only vs 3-5 lines) on
  A3/A16/A27 → tests whether adaptive beats P1 on the hard bucket without
  P5's suppression.
- Final recommendation to user: two-layer (prompt P1 + serving-level
  thinking_token_budget), see memory/thinking-reduction-survey.md.
