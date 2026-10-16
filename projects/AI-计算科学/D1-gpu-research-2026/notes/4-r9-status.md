origin: ai
time: 2026-09-27T09:30+08:00
stage: 04 / round: r9 / status: RESTING (KV defect CLOSED; user deferred form-factor + declined method-check)

# cursor: 04/r9 RESTING -> deliverable gated on form-factor (user) OR NVIDIA box (env); nothing autonomous left

## done this round (verification, closes r8 open item)
- obtained 一手✓ hybrid-attention pattern from public transformers configuration_gemma3.py
  (bypassed HF 401 via GitHub raw): every-6th-full, sliding_window=4096 -> 10 full / 52 sliding.
- fixed roofline_verify.py KV term (full-KV overestimate -> hybrid).
- re-executed: INT4/INT8/BF16 = 15.80/29.60/57.21 GB == prior artifact 15.81/29.61/57.22 (fp match).
- => script-vs-artifact VRAM CONTENT DEFECT CLOSED. no open numeric discrepancy.

## verdict-stable (reconcile did not move conclusions)
- fit: INT4 all 4 cards; INT8 A100-40/L40S/5090 (4090 excluded, 29.60>24); BF16 none.
- roofline tok/s unchanged (KV not in single-stream decode ceiling).
- H* flip unchanged: A100-40 refurb INT8 R@low 0.0480 > 5090 0.0332 (price-driven, 5090 faster 66>58).

## remaining open (narrowed to env + user only)
- ENV (corrected, 一手✓ probed): host = Apple M1 Max, 69GB unified, Metal/MPS. NO NVIDIA/CUDA.
  -> first-hand on CANDIDATE cards (5090/4090/A100/L40S, all NVIDIA-CUDA) = STRUCTURALLY BLOCKED
  (hardware-class mismatch, NOT "no GPU"). Unblocked only by a rented/cloud NVIDIA instance.
- M1 Max can validate the roofline METHOD (69GB fits INT8 27B) but needs runtime install + ~30GB
  download -> yields a METHOD datapoint on Apple Silicon, NOT a candidate-card number. Heavy, optional detour.
- USER: form-factor (desktop tower -> H*=5090 | server/workstation you can cool -> H*=A100-40 refurb INT8).
- USER/market: A100-40 live refurb quote (flip holds only near $1200).

## next concrete action
- deliverable (H* among NVIDIA cards) needs an NVIDIA box -> user/cloud decision, not this host.
- await user form-factor answer to collapse to single H*.
- optional: M1 Max roofline-method validation (install llama.cpp/MLX + 30GB GGUF) if user wants method-check.