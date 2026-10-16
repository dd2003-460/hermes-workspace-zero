origin: ai
time: 2026-09-27T20:50+08:00
stage: 04 / round: r18 / status: DONE (roofline's DEEPEST unverified assumption machine-checked: decode IS memory-bound not compute-bound -> bw/bytes ceiling VALID; found+fixed a units bug that made the first inv10 decorative; teeth-proven)

# cursor: 04/r18 = prove the roofline MODEL applies (memory-bound regime), the assumption every H* number silently rests on

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r17-status.md -> advanced to r18 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析 -> 本轮验证")
The entire roofline conclusion (break-even $1735/$1124, H* tree) silently rests on ONE never-checked assumption:
"single-stream decode is MEMORY-bandwidth-bound". If it were COMPUTE-bound, bw/bytes is the WRONG ceiling and
every H* number would be off. Roofline regime test = arithmetic-intensity vs ridge-point. inv10 (NEW):
- decode batch=1: FLOPs/token ~= 2*params (each weight one MAC); bytes/token = params*bytes_per_param.
  -> AI = 2*params/(params*bytes_per_param) = 2/bytes_per_param (params CANCELS -> quant-only, card-independent).
  INT8 -> AI=2 flops/byte ; INT4 -> AI=4 flops/byte. Decode re-reads ALL weights every token -> AI is TINY.
- ridge_point = peak_flops/(bw_bytes/s). Used PEAK_COMPUTE=50 TF (DELIBERATELY ~10x PESSIMISTIC; real INT8
  tensor-core is 100-300+ TF). Low compute -> low ridge -> if AI still beats THAT, memory-bound holds regardless.
- ridge_min (worst card, 5090 highest bw -> lowest ridge) = 27.9 flops/byte. AI(INT4)=4 << 27.9 -> ~7x margin.
  -> memory-bound CONFIRMED -> bw/bytes ceiling VALID -> all H* numbers stand on solid ground.

## BUG caught this round (test-the-test discipline, not decorative)
- First inv10 wrote ridge = peak_flops/bw_GBps (MISSING *1e9 to convert GB/s->bytes/s) -> ridge inflated 1e9
  -> assertion AI<ridge trivially true -> canary (PEAK=1.0) did NOT go RED -> inv10 had NO teeth. Caught by
  deliberately forcing compute-bound; fixed to peak_flops/(bw*1e9); re-proved: normal green (ridge 27.9), canary
  PEAK=1.0 -> ridge 0.56 < AI=4 -> FAIL exit1 ✓ (teeth). Same exit-code discipline as r13/r14.

## why this matters (advance, not restate)
- Before r18: roofline was ASSUMED applicable. A compute-bound workload would silently invalidate every number here.
- Now: the regime is machine-checked with a ~7x margin under a 10x-pessimistic compute bound -> robust to wide
  uncertainty in the (community-R) peak-FLOPS specs. The foundation of the whole deliverable is now verified,
  not assumed. This is the deepest load-bearing check in the project.

## honest boundary (unchanged, NOT loosened)
- peak compute = vendor/community R (no 一手✓ offline), but the REGIME CLASSIFICATION is robust to ~10x error
  (margin 7x at 10x-pessimistic compute) -> the conclusion does not hinge on the exact FLOPS number.
- throughput still roofline ceiling / community R; first-hand vLLM ENV-BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round verified the roofline's VALIDITY, not the answer)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA).

## next concrete action
- autonomous 一手✓ + logic/regime verification exhausted: roofline inputs pinned (3/4), tree runs+tested (r17),
  roofline validity proven (r18). No further offline advance without user Q1/Q2/Q3 or an NVIDIA box.
- resting state: deliverable = self-resolving tree whose FOUNDATION (memory-bound regime) is now machine-proven.