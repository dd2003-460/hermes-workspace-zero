origin: ai
time: 2026-09-27T09:12+08:00
stage: 04 / round: r8 / status: DONE (first script落盘 verified; VRAM-num reconcile open)

# cursor: 04/r8 script落盘验证 DONE -> 显存数值 reconcile open + first-hand still blocked

## done this round (实现/验证, not analysis)
- FIRST real .py落盘 (tasks/roofline_verify.py) -> converts "script-verified" CLAIM into executable truth (诚实第一红线).
- executed OK. Confirmed: roofline rank + H* flip (A100-40@1200 R@low 0.0480 > 5090@1999 0.0332, single-stream).
- fixed var bug (pr->p).

## NEW honest discrepancy (script vs prior artifact)
- script VRAM: INT4=16.02 / INT8=30.04 / BF16=58.08 GB.
- prior artifact (02.5/04): INT4=15.81 / INT8=29.61 / BF16=57.22 GB.
- delta ~0.2-0.86 GB. ROOT CAUSE (hypothesis): KV term. script uses full CTX=8192 * 2(K+V);
  prior likely used SLIDING-WINDOW partial KV (Gemma-3 hybrid: some layers local 512, some global).
  -> not yet reconciled. Does NOT change fit verdict (INT8 fits 5090/A100-40/L40S; BF16 none).
- OPEN: reconcile KV (sliding-window layer count) so artifact == script. Content defect, fixable.

## confirmed (script, 一手✓)
- roofline tok/s: 5090 INT4=132.7/INT8=66.4; 4090 INT4=74.7; L40S INT4=64/INT8=32; A100-40 INT4=115.2/INT8=57.6.
- community ABOVE-roofline: 5090 INT4/INT8 (batched). FAR-BELOW: 4090/L40S-INT4/A100-40-INT4 (non-opt). WITHIN: L40S-INT8/A100-40-INT8.
- single-stream cost-perf H* = A100-40 refurb INT8 ($1200). flip on PRICE, 5090 faster 66>58.

## precise blocking (unchanged)
- first-hand single-stream vLLM: BLOCKED no GPU (env).
- form-factor tower-vs-server + A100-40 live refurb quote: USER.
- KV reconcile一手: BLOCKED this session — HF config.json 401 (gated repo, needs auth) + WebSearch
  returned no-execution ("no tools active"). 一手 KV split unavailable -> artifact-vs-script delta stays open.
  Does NOT change fit verdict (INT8 fits 5090/A100-40/L40S; BF16 none) nor H* flip (price-driven).

## next concrete action
- 04-r9: reconcile KV via authenticated fetch (gh/HF token) OR local Gemma-3 config if present -> close content defect.