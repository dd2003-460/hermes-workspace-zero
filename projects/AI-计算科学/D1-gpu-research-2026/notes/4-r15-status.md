origin: ai
time: 2026-09-27T19:30+08:00
stage: 04 / round: r15 / status: DONE (roofline load-bearing input 一手✓ upgraded: 5090 bw/vram WebFetch-confirmed + inv8 pinned; deliverable still gated on user/market answers)

# cursor: 04/r15 = 一手✓ 核实 roofline 唯一未一手✓ load-bearing 输入 (RTX 5090 显存带宽/容量)

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r14-status.md -> advanced to r15 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis)
上一回答多为分析 -> 本轮切换到一手✓ 验证。roofline 结论 (break-even $1735/$1124, H* 三候选) 全部 rests on
显存带宽数，此前这些数无 provenance 标签 (= 社区 R)。本轮一手✓ 升级 5090 的：
- 一手✓ (WebFetch, Wikipedia GeForce RTX 50 series): RTX 5090 = **1792 GB/s**, 512-bit bus, 32 GB GDDR7.
- 与脚本硬编码 `bw=1792, vram=32` 一致 -> 升级 provenance 标签 社区 R -> 一手✓.
- 新增 inv8: 脚本硬编码值 against 一手✓ 权威常量 AUTH_5090={bw:1792,vram:32} -> catches future typo/regression
  on the single most load-bearing number in the whole roofline chain.
- 统一门 run_all.py 全绿 (exit 0) after edits ✓.

## honest boundary (NOT loosened)
- 仅 5090 bw/vram 一手✓。4090/L40S/A100-40 bw/vram 仍厂商公开规格 (社区 R, 待一手✓)。
- price 全部 = 二手市场假设 (USER/market), 不可一手✓ offline。
- first-hand single-stream vLLM 仍 BLOCKED (host Apple Silicon, no CUDA) -> 社区 R 吞吐 vs roofline 仍唯一 honesty gap.

## why this matters (advance, not restate)
- 之前: 整 roofline 结论 rests on unverified bw numbers -> if bw wrong, $1735/$1124 all wrong, silently.
- 现在: 决定 H* 两分支之一 (5090) 的 bw 一手✓ + pinned by inv8 -> 该分支的 roofline 132.7 tok/s INT4 is grounded.
- 这是把"理论天花板"从 unverified 到 partially-一手✓: 实质诚实进步, 不是 restatement.

## precise blocking (unchanged count; deliverable still gated — this round verified an input, not the answer)
1. form-factor = USER (desktop tower vs server/workstation).
2. refurb A100-40 quote vs $1735 = USER/market.
3. refurb RTX 4090 quote vs $1124 = USER/market (conditional on tower form-factor).
4. first-hand single-stream vLLM = ENV (Apple Silicon no CUDA; rented NVIDIA box).

## next concrete action
- autonomous: 一手✓ 余三卡 bw via WebFetch (A100-40 1555 GB/s HBM2e 40GB; 4090 1008 GB/s; L40S 864 GB/s) ->
  升级其余 roofline inputs 一手✓ (r16). 这是继续一手✓ 推进 without user input.
- deliverable advances only on (1)/(2)/(3) — user/market.