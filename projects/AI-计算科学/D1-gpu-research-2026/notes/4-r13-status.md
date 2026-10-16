origin: ai
time: 2026-09-27T19:10+08:00
stage: 04 / round: r13 / status: DONE (two integrity defects fixed + proven; deliverable still gated on 2 user/market answers)

# cursor: 04/r13 = make the self-test actually able to FAIL, and evaluate dominance at FEASIBLE quants

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r12-status.md -> advanced to r13 here. Stayed GPU thread, did not restart.

## done this round (implementation/verification, not analysis)
Two REAL defects found by reading my own r12 dominance check carefully, both fixed + machine-proven:

1. EXIT-CODE INTEGRITY BUG (roofline_verify.py): computed `fails` and printed a verdict but had NO
   `sys.exit(1 if fails else 0)`. A self-test that cannot fail is decorative, not a test.
   FIX: added exit, GUARDED by `if __name__=="__main__"` so `import roofline_verify` (used by
   test_hstar_rule.py) does not kill the importing host.
   PROOF (test-the-test, exit codes captured):
     [1] clean direct run            -> exit 0 ✓
     [2] fault injected (A100 price 1200->1900, above $1735 be) -> exit 1 ✓  (inv4+inv5 caught it)
     [3] import path via test_hstar_rule.py -> exit 0 ✓  (host survived the __main__ guard)

2. INFEASIBLE-CONFIG DEFECT (dominance check): r12 compared RTX_4090 at INT8 (29.6 GB), but the script's
   OWN VRAM gate (inv3) excludes the 24 GB 4090 from INT8. So the displayed "4090 INT8 @37.3" was a config
   that will not load. FIX: evaluate each card at best_feasible_quant(c) = INT8 if fits else INT4.
   Now: RTX_4090 [INT4, 24GB] @ 74.7 vs 5090 @ 132.7 -> be $1124 ; L40S [INT8, 48GB] @ 32.0 -> be $963.
   Added inv7: break-even is QUANTIZATION-INVARIANT (bytes/param cancels in roof_c/roof_5090) -> be(INT4)==be(INT8).
   This is why the $1124 conclusion survived the fix unchanged (it was numerically right, just shown on an
   infeasible config).

## why this matters (advance, not restate)
- Integrity: the regression net now has teeth. Before r13, ANY future edit that broke H* would still print
  "ALL ASSERTS PASS" and exit 0 -> silent rot. Now it exits 1. Verified, not asserted.
- Substantive: the dominance finding is now config-honest. 4090 beats 5090 at roofline only via INT4 (its only
  feasible quant), and L40S never flips at realistic ($7500 new) price.

## sharpened decision structure (this EXTENDS r11's two-gate model with a 3rd live candidate)
H* among NVIDIA cards is NOT just {A100-40 refurb} vs {RTX 5090}. A cheap refurb RTX 4090 (<$1124, INT4-only)
is a THIRD live candidate that beats 5090 at roofline cost-perf. So the user/market gates are now:
  (a) form-factor: desktop tower -> 5090/4090 class ; server/workstation-can-cool -> A100-40/L40S class.
  (b) refurb A100-40 quote vs $1735.
  (c) refurb RTX 4090 quote vs $1124 (only relevant if tower form-factor AND sub-$1124 available).
L40S is effectively dead as a candidate (be $963 << $7500 new; no realistic refurb path below $963).

## precise blocking (unchanged count of USER/market gates; deliverable still gated)
1. form-factor = USER (tower vs server).
2. refurb A100-40 quote vs $1735 = USER/market.
3. refurb RTX 4090 quote vs $1124 = USER/market (new, conditional on tower form-factor).
4. first-hand single-stream vLLM = ENV (host Apple M1 Max no CUDA; needs rented NVIDIA box).

## next concrete action
- nothing autonomous advances the DELIVERABLE until (1) answered; (2)/(3) are market quotes the user supplies.
- when NVIDIA box appears -> real vLLM batch=1, replace community R numbers with first-hand ✓.
- autonomous hardening continues: next candidate = fold roofline_verify.py + test_hstar_rule.py into one
  pytest-style runner so a single `pytest tasks/` gates the whole thread (r14).