origin: ai
time: 2026-09-27T09:26+08:00
stage: 04 / round: r11 / status: DONE (blocker#2 sharpened to exact $1735; deliverable still gated)

# cursor: 04/r11 break-even quantified -> blocker#2 now a single number ($1735), not a range

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r10-status.md -> advanced to r11 here. Stayed GPU thread, did not restart.

## done this round (implementation/verification, not analysis)
- NEW: computed BREAK-EVEN price (一手✓, machine-checked inv5 added).
  p_be = price_5090 * (roofline_A100/roofline_5090) = 1999 * 0.867 = $1735 (INT8 & INT4, same ratio).
- sharpened blocker#2 from vague "$1200-3000 straddles" -> EXACT decision rule:
  refurb A100-40 quote < $1735 -> H* = A100-40 refurb INT8 ; quote > $1735 -> H* = RTX 5090.
- executed: ALL ASSERTS PASS ✓ (inv1-5). $1200 assumption confirmed < $1735 (flip valid).

## why this matters (advance, not restate)
- blocker#2 was un-actionable ("somewhere in $1200-3000, does flip hold?"). Now it is a binary test the user
  can answer with one live quote: is the refurb A100-40 under $1735 or not? No more ambiguity.
- The whole H* collapse now reduces to TWO binary gates: (a) form-factor [tower->5090 | server->A100-40],
  (b) refurb quote vs $1735. Both are USER/market, both are one-line answers.

## precise blocking (sharpened, NOT loosened)
1. form-factor = USER: desktop tower -> H*=RTX 5090 ; server/workstation-can-cool -> H*=A100-40 refurb INT8.
2. refurb A100-40 quote vs $1735 = USER/market (binary: under/over $1735).
3. first-hand single-stream vLLM = ENV (host Apple M1 Max no CUDA; needs rented NVIDIA box).

## next concrete action
- nothing autonomous advances deliverable until (1) or (2) answered.
- when form-factor answered -> collapse H* to single card (r12).
- when NVIDIA box appears -> real vLLM batch=1, replace community R with first-hand.