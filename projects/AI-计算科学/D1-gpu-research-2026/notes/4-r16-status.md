origin: ai
time: 2026-09-27T20:10+08:00
stage: 04 / round: r16 / status: DONE (roofline 其余两卡 bw/vram 一手✓ 升级 4090+L40S + inv8 扩展 pinned 三卡; A100-40 bw 诚实 BLOCKED; 统一门全绿; deliverable still gated on user/market)

# cursor: 04/r16 = 一手✓ 升级余两卡 roofline 输入 (4090/L40S bw+vram WebFetch-confirmed); inv8 现 pinned 三卡

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r15-status.md -> advanced to r16 here. Stayed GPU thread, did not restart.

## done this round (一手✓ 验证, not analysis)
上一多为分析 -> 本轮一手✓ 核实其余 roofline 输入。r15 仅 5090 一手✓；本轮升级另两卡：
- 一手✓ (WebFetch, Wikipedia GeForce RTX 40 series): RTX 4090 = **1008 GB/s** GDDR6X, 24 GB -> 匹配硬编码 `bw=1008,vram=24`.
- 一手✓ (WebFetch, NVIDIA L40S data-center page): L40S = **864 GB/s** GDDR6 ECC, 48 GB -> 匹配硬编码 `bw=864,vram=48`.
- inv8 重构: 单常量 AUTH_5090 -> 三卡 dict AUTH={5090,4090,L40S} -> 脚本硬编码值 now pinned against 一手✓ 权威
  三卡 bw+vram. 整 roofline 链除 A100-40 bw 一手✓ grounded.
- 统一门 run_all.py 全绿 (exit 0) after edits ✓ (re-ran this round).

## honest boundary (NOT loosened — A100-40 bw stays 社区R, NOT fabricated)
- A100-40 bw=1555 一手✓ BLOCKED (precise, four sources tried): ① NVIDIA 官方 A100 page 只 lists 80GB variants
  (1935/2039 GB/s HBM2e), 40GB bw NOT stated; ② TechPowerUp a100-sxm4-40gb -> 403 Forbidden; ③ Wikipedia
  A100_(GPU) -> domain-safety block; ④ datasheet PDF -> API 400 (80k tokens > fetch-model 80k ctx). -> 诚实留 社区R.
- price 全部 = 二手市场假设 (USER/market), 不可一手✓ offline.
- first-hand single-stream vLLM 仍 BLOCKED (host Apple Silicon, no CUDA) -> 唯一 remaining honesty gap.

## why this matters (advance, not restate)
- 之前 (r15): 仅 1/4 卡 bw 一手✓ -> 其余三卡 roofline (4090 74.7 / L40S 64 / A100-40 58 tok/s INT8) unverified.
- 现在: 3/4 卡 bw+vram 一手✓ + inv8 pinned -> 两 H* 候选分支的 roofline grounded: 5090 (132.7 INT4) + 4090
  (74.7 INT4, the cheap-refurb 3rd candidate) both on 一手✓ bw. break-even $1735/$1124 rests on 一手✓ ratios.
- 实质: 决定 H* 的 dominant branch (5090) AND the refurb-4090 challenger 的 roofline now 一手✓ grounded, not eyeballed.

## precise blocking (unchanged count; deliverable still gated — this round verified inputs, not the answer)
1. form-factor = USER (desktop tower vs server/workstation).
2. refurb A100-40 quote vs $1735 = USER/market.
3. refurb RTX 4090 quote vs $1124 = USER/market (conditional on tower form-factor).
4. first-hand single-stream vLLM = ENV (Apple Silicon no CUDA; rented NVIDIA box).

## next concrete action
- autonomous 一手✓ exhausted for roofline inputs (3/4 cards pinned; A100-40 blocked, honestly labeled). No further
  offline 一手✓ advance possible without user/market/ENV.
- deliverable advances only on (1)/(2)/(3) — user/market. When an NVIDIA box appears -> replace 社区R throughput
  with first-hand ✓ (the one remaining honesty gap).
- resting state: harness green + teeth-proven; roofline inputs 3/4 一手✓; H* fully determined by user's answers.