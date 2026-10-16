origin: ai
time: 2026-09-28T05:00+08:00
stage: 04 / round: r31 / status: DONE (IMPLEMENTATION: attack the BATCH axis -- the roofline has ALWAYS been evaluated at batch=1 (the batch dimension was SILENTLY set to 1; "memory-bound" holds ONLY for small batch). At batch=B the WEIGHTS amortize /B but the attention KV re-read does NOT -> bytes/token = weights/B + kv FALLS with B -> AI=flops/bytes RISES -> crosses ridge at critical batch B*~38 (INT8) -> decode flips COMPUTE-bound -> bw/bytes (the deliverable's throughput P) OVERestimates tok/s for B>=B* -> P is BATCH-DEPENDENT -> the deliverable NEVER specified batch = a NEW required input (Q4). Encoded into roofline_verify.py (inv22) + registered batch as required input Q4 in the deliverable resolve_hstar.py.)

# cursor: 04/r31 = the roofline invisibly assumed batch=1 -- proved the memory-bound ceiling is valid only below critical batch B*~38, surfaced batch size as a NEW required input Q4

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r30-status.md -> advanced to r31 here. Stayed GPU thread, did not restart.
- guardrail satisfied: r30 attacked the GATE structure; r31 attacks a NEW axis (BATCH domain, never a knob).

## the genuine NEW axis this round (the batch dimension was silently =1)
- inv10/11/15/18/19/20/21 all evaluated the roofline at batch=1 without ever naming batch. "memory-bound" is a
  batch=1-specific regime. At batch=B: weights read ONCE for the whole batch (amortized /B), but each token still
  re-reads its OWN sequence's KV (attention does NOT amortize) -> bytes/token = weights/B + kv_read FALLS with B
  -> AI = flops/token (=2*PARAMS, compute NOT shared) / bytes/token RISES with B -> crosses ridge at critical
  batch B* -> decode flips MEMORY-bound -> COMPUTE-bound -> bw/bytes OVERestimates achievable tok/s beyond B*.
- DISTINCT from inv20 (that was PHASE: prefill batch=prompt_len, a compute-bound ENDPOINT; this is the
  batched-DECODE continuum between single-stream decode and prefill -- a THIRD regime the roofline never modeled).

## done this round (implementation + verification)
### roofline_verify.py -- inv22 (the roofline-side proof)
- bytes_per_token_batched(B,prec) = PARAMS*bp/1e9/B + kv_read_bytes_fp16(CTX)/1e9 (weights /B + per-token KV).
- ai_batched(B,prec) = 2*PARAMS / (bytes_per_token_batched(B,prec)*1e9) (flops/token constant, bytes/token drops).
- inv22(1): bytes/token INT8 batch=1=28.21GB -> batch=64=1.63GB (17.3x drop) -> floors at KV re-read 1.21GB
  (attention does NOT amortize).
- inv22(2): AI(INT8) batch=1=1.91 << ridge 27.9 (memory-bound, matches inv10/15) -> rises with B -> crosses ridge
  at CRITICAL batch B*=38 -> decode flips COMPUTE-bound for B>=38 -> roofline bw/bytes VALID ONLY for B<38.
- inv22 teeth: pretend weights NOT amortized across batch (bytes_bad, no /B) -> AI stays 1.91 < ridge for ALL B
  -> NO critical batch exists -> the B*-existence check BITES (the flip is CAUSED by weight amortization /B, the
  roofline's invisible batch=1 assumption).
### resolve_hstar.py -- deliverable: register batch as required input Q4
- REQUIRED_INPUTS registry {Q1 form-factor, Q2 A100-40 quote, Q3 4090 quote, Q4 batch size}; guard fails if
  "Q4 batch size" not declared -> the tree must never present a be as batch-invariant.

## teeth-proven (all, EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0; [B] canary sed drop `/B` in bytes_per_token_batched -> b64<b1 fails AND
  B_star search raises StopIteration -> EXIT=1 ✓; [C] run_all.py EXIT=0.
- resolve_hstar.py: [A] normal EXIT=0. [B] deliverable guard teeth: FIRST attempt sed `/Q4 batch size/d` deleted
  BOTH the entry AND the guard (both contain "Q4 batch size") -> guard removed -> FALSE PASS EXIT=0. FIXED: sed
  delete ONLY the entry (`/"Q4 batch size (roofline/d`, entry-unique) -> guard present (line 118) -> fires RED for
  the RIGHT reason: `RESULT: FAIL -> inv22: batch NOT declared a required input -> the tree silently assumes
  batch=1` -> EXIT=1 ✓. Restored -> [A] EXIT=0, [C] run_all.py EXIT=0.

## why this matters (advance, not restate)
- This surfaces a NEW REQUIRED INPUT the deliverable never asked for: BATCH SIZE. The whole roofline (and the
  $1735/$1995 break-even) is a batch=1 figure. If the deployment batches beyond B*~38 (INT8), the roofline's
  bw/bytes OVERestimates P -> the ranking/be drift toward the compute ratio (needs per-card peak flops =
  ENV-BLOCKED). So the deliverable's criterion R=P/C is incomplete without a batch spec -- batch joins Q1/Q2/Q3 as
  a required user/market input. Honest: at batch=1 single-stream (the stated anchor) the roofline is VALID.

## honest boundary (NOT loosened)
- B*=38 is a roofline-model figure at the ~10x-pessimistic PEAK_COMPUTE_TFLOPS=50 (real tensor-core 100-300+ ->
  real ridge LOWER -> real B* SMALLER -> the flip happens SOONER -> B*=38 is a CONSERVATIVE upper bound on when
  the roofline stays valid). 一手✓ arithmetic on the model.
- cross-card compute-bound be (for B>=B*) needs PER-CARD peak flops (only global 50 stored) -> ENV-BLOCKED; the
  batched-decode be is a NEW open quantity, not computed here.
- batch is a NEW required input (USER/market); the tree declares it (Q4) but does not branch on it (cannot
  recompute the compute-bound be without per-card flops).

## precise blocking (deliverable advances ONLY on these; this round added Q4 batch to the required-input set)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. NEW: batch size = USER/market (Q4) -- the roofline be is batch=1;
   a batched deployment (B>=~38) invalidates bw/bytes and needs per-card flops. 5. first-hand single-stream vLLM =
   ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready
   (inv21), A100-40 bw (inv8 -- r31 WebSearch multi-source CORROBORATED 1555 GB/s NVIDIA-datasheet+TechPowerUp+
   spec-tables, value CONFIRMED-consistent, still 社区R not 一手✓ first-hand measured).

## next concrete action
- premise chain complete through the PHASE boundary, the GATE structure, AND now the BATCH domain, all encoded:
  regime (inv10) + traffic (inv11/15) + cache (inv16) + sparsity (inv17) + quant-meta (inv18) + KV-precision
  (inv19) + PHASE-domain (inv20) + GATE-structure/COMPAT (inv21) + BATCH-domain (inv22) + eta (inv13) + constants
  (inv8/14) + cross-file (inv12) + tree (r17/inv9). Every remaining unknown is ENV/USER-gated. Offline advance
  genuinely exhausted -- HOLD awaiting user Q1-Q4 / market quotes / hardware.

## r31 housekeeping DONE
- persisted r31 cursor; advanced INDEX.md cursor pointer r30->r31 + added the inv22 entry; updated durable memory
  with inv22 (BATCH-domain) + upgraded the first-hand vLLM list to SEXTUPLE (adds batch-domain confirmation);
  refreshed MEMORY.md index line with inv22 + Q4.
- r31.5 substantive advance (post-persistence): last ENV-BLOCKED constant A100-40 bw UPGRADED to MULTI-SOURCE
  CORROBORATED -- WebSearch returned peak mem bandwidth 1,555 GB/s (HBM2e, 5120-bit bus @1215MHz) citing NVIDIA
  Official Datasheet + TechPowerUp + NVIDIA Developer Docs = EXACTLY matches CARDS["A100-40"]["bw"]=1555. Honest:
  kept 社区R (model-summarized search, NOT 一手✓ first-hand measurement), upgraded from single-source 社区R to
  3-source corroborated. Annotation updated in roofline_verify.py (line-31 comment + inv8 honest-gap print) +
  durable memory + this cursor. run_all EXIT=0 (gate green; annotation/print-text only, no logic change).