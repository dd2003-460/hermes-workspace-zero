origin: ai
time: 2026-09-27T09:22+08:00
input: 一手✓ transformers configuration_gemma3.py (layer_types pattern) + roofline_verify.py (r8) + prior artifact (02.5/04)

# 04-r9 KV reconcile — close script-vs-artifact VRAM content defect

## root cause (一手✓, was hypothesis in r8)
Gemma-3 = HYBRID attention. Authoritative source = public transformers
`configuration_gemma3.py` (HF config.json 401 bypassed via GitHub raw):
- `sliding_window: int | None = 4096`
- `self._sliding_window_pattern = kwargs.get("sliding_window_pattern", 6)`
- `layer_types[i] = "full_attention" if (i+1) % 6 == 0 else "sliding_attention"`

For num_hidden_layers=62 -> FULL (global) layers = indices where (i+1)%6==0
= {5,11,17,23,29,35,41,47,53,59} = **10 layers**; SLIDING (local) = **52 layers**.

## the defect
r8 script modeled KV as 62 layers x full CTX=8192 -> OVERESTIMATE.
Prior artifact (02.5/04) modeled hybrid (local layers window-capped) -> ACCURATE.
Delta was entirely the 52 local layers' KV being counted at 8192 instead of min(CTX,4096).

## fix (landed in roofline_verify.py)
kv_tokens = FULL_LAYERS*CTX + SLIDING_LAYERS*min(CTX, SLIDING_WINDOW)
            = 10*8192 + 52*4096 = 81920 + 212992 = 294912 token-slots
            (vs full-KV 62*8192 = 507904 -> 41.7% fewer KV token-slots)

## reconciliation result (script executed, 一手✓)
- INT4: script 15.80 GB vs artifact 15.81 GB -> MATCH (±0.01 fp)
- INT8: script 29.60 GB vs artifact 29.61 GB -> MATCH
- BF16: script 57.21 GB vs artifact 57.22 GB -> MATCH
=> content defect CLOSED. artifact == script. No more open numeric discrepancy.

## what did NOT change (verdict-stable)
- fit verdict unchanged: INT4 fits all 4; INT8 fits A100-40/L40S/5090 (4090 24GB now EXCLUDED —
  29.60>24, consistent w/ artifact); BF16 fits none.
- roofline tok/s unchanged (KV does not enter single-stream decode roofline; weights bytes only).
- H* flip unchanged: A100-40 refurb INT8 R@low 0.0480 > 5090 0.0332 (price-driven).

## honest boundary (unchanged, still the real open item)
- all throughput = community R vs roofline ceiling; first-hand single-stream vLLM BLOCKED (no GPU).
- A100-40 live refurb quote + form-factor (tower vs server) still USER.

`review: 04-r9 | KV-reconcile | pass | root cause 一手✓ confirmed (hybrid every-6th-full, window 4096) -> script fixed -> INT4/8/16 = 15.80/29.60/57.21 GB == artifact 15.81/29.61/57.22 (fp match) -> content defect CLOSED; verdicts (fit/roofline/H*) stable; first-hand benchmark + refurb quote + form-factor remain open (env/user) | next: await GPU for first-hand vLLM; await user form-factor + refurb quote`