origin: ai
time: 2026-09-27T09:20+08:00
stage: 04 / round: r10 / status: DONE (self-test hardened; deliverable still gated on user+env)

# cursor: 04/r10 verification-hardening DONE -> deliverable sharply gated (form-factor=user, NVIDIA=env)

## ground-truth reconciliation (honest-first)
- stop-hook "持久状态" said stage 02 / Ego Lite / partition-cover / well-founded μ -> that is a GLOBAL formal-methods cursor, NOT this project.
- grep "partition/atomicity/well-founded" in this repo = incidental word matches only (no real stage-02 proof artifact).
- THIS project's real cursor = notes/4-r9-status.md (RESTING) / tasks/04-KV-reconcile-r9.md. -> stayed on GPU thread, did not restart.

## done this round (implementation/verification, not analysis)
- hardened tasks/roofline_verify.py with SELF-TEST block -> 4 machine-checked invariants:
  inv1 hybrid-KV VRAM == prior artifact (INT4/8/16 = 15.80/29.60/57.21, tol 0.05) [closes r9 defect]
  inv2 first-hand Gemma-3 pattern full=10 / sliding=52
  inv3 fit verdicts: INT8->{A100-40,L40S,RTX_5090} (4090 excluded), BF16->none
  inv4 H* flip A100-40 R@low > 5090 R@low @ $1200
- executed: ALL ASSERTS PASS ✓ -> closed defects now regression-proof (silent regress -> loud FAIL).

## honest boundary (unchanged, sharply gated)
- form-factor (desktop tower -> H*=5090 vs server/workstation-can-cool -> H*=A100-40): USER decision.
- A100-40 live refurb quote (flip holds only near $1200): USER/market.
- first-hand single-stream vLLM on candidate cards: ENV (host=Apple M1 Max no CUDA; needs rented NVIDIA box).

## next concrete action
- nothing autonomous advances the deliverable until form-factor or NVIDIA-box unblocks.
- if user answers form-factor -> collapse H* to single card (r11).
- if GPU appears -> run real vLLM batch=1, replace community R with first-hand, settle roofline-vs-community.