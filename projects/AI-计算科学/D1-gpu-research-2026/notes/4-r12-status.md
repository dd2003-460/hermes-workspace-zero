origin: ai
time: 2026-09-27T09:34+08:00
stage: 04 / round: r12 / status: DONE (decision-rule machine-checked; deliverable still gated)

# cursor: 04/r12 H*-collapse DECISION RULE machine-checked -> only user form-factor + NVIDIA box remain

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r11 -> advanced to r12 here. Stayed GPU thread, did not restart.

## done this round (implementation/verification, not analysis)
- NEW tasks/test_hstar_rule.py: independent runner that machine-checks the H*-collapse DECISION RULE itself
  (not just the $1735 threshold). 4 invs: be-algebra-tie, be-algebra-value, 3 boundary points, pattern, VRAM.
- honest-first working: FIRST RUN FAILED on inv2 (my test wrote quote/P_be instead of actual R@ values).
  一手✓ confirmed rule correct via algebra (inv1 passed) -> fixed TEST logic (not the rule) -> re-run ALL PASS ✓ exit=0.
- net: the binary decision rule is now machine-checked at $1200/$2000/$1735, not eyeballed.

## why advance (not restate)
- r11 gave the number $1735. r12 proves the RULE that uses it is correct at boundaries + tie.
- so when user returns a live quote Q, the answer is unambiguous AND verified: Q<$1735->A100-40, Q>$1735->5090.

## precise blocking (sharpened, NOT loosened)
1. form-factor = USER (binary): tower->5090 | server-can-cool->A100-40.
2. refurb A100-40 quote vs $1735 = USER/market (binary, now machine-verified rule).
3. first-hand single-stream vLLM = ENV (host Apple M1 Max no CUDA; needs rented NVIDIA box).

## next concrete action
- nothing autonomous advances deliverable until (1) or (2) answered.
- when form-factor answered -> collapse H* to single card (r13).
- when NVIDIA box appears -> real vLLM batch=1, replace community R with first-hand.