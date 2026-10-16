# Stage 04 r1 独立计算验证记录
# origin: ai
# 日期: 2026-09-09
# 方法: Python 独立重算 (price_usd / llm_tok_s; breakdown × weights)，与 stage 03 artifacts 逐项比对

## L1 $/tok 算术验证 (22 个值)
全部通过。RTX 4090=1.33, 4090D=1.6, 5090=0.34, 6000Ada 7b=9.38/70b=93.75, A100SXM4 7b=33.33/70b=117.65,
A100PCIe 7b=48/70b=160, H100SXM5 7b=37.5/70b=142.86, H100PCIe 7b=50/70b=166.67, H200 7b=14/70b=110.4,
MI300X 7b=25/70b=107.14, M4=16.25, M4Max 7b=22.5/70b=81.82, SN3000 7b=36.67/70b=137.5。0 mismatches。

## L2 排名一致性 — 发现 6 处顺序违规
recorded rankings_7b (cost-performance-analysis.json):
#1 5090(#1) #2 4090(#2) #3 4090D(#3) #4 M4(#4) #5 M4Max(#5) #6 MI300X(#6) #7 SN3000(#7) #8 H100SXM5(#8)
#10 H100PCIe #11 A100PCIe #12 H200 #13 RTX6000Ada
按 $/tok 升序重算应为:
#1 5090 $0.34 #2 4090 $1.33 #3 4090D $1.60 #4 6000Ada $9.38 #5 H200 $14.00 #6 M4 $16.25 #7 M4Max $22.50
#8 MI300X $25.00 #9 A100SXM4 $33.33 #10 SN3000 $36.67 #11 H100SXM5 $37.50 #12 A100PCIe $48.00 #13 H100PCIe $50.00
违规: RTX6000Ada(记录#13, 应#4), H200(记录#12, 应#5), Apple M4(记录#4, 应#6), M4Max(#5→#7),
MI300X(#6→#8), SN3000(#7→#10)。recorded 序列与 $/tok 值不一致，score_percentile 同样不自洽
(4090=26 但 M4=2, 与 $/tok 差距不成比例)。可能原因: 排名用了不同口径(如只排消费级?)或数据陈旧，需修复或注明口径。

## L3 决策框架内部一致性 — 2 处失败
1) 8 项权重之和 = 0.2+0.15+0.1×5+0.05 = 0.90 ≠ 1.0 (缺失 0.10)。
2) 11 个 GPU 中 9 个 recorded total 无法由 breakdown×weights 复现:
   RTX5090: 记录82 vs 重算62.5 | RTX4090: 65 vs 51.0 | H200: 78 vs 65.75 | MI300X: 72 vs 60.5
   A100SXM4: 58 vs 51.5 | H100SXM5: 68 vs 56.5 | 6000Ada: 52 vs 55.0 | Groq: 40 vs 32.75 | SN3000: 30 vs 36.0
   仅 M4Max(45) 和 Cerebras(35.5≈35) 通过。归一化权重(÷0.9)后 5090=69.4 仍 < H200=73.1。

## 关键影响
重算下 H200(65.75) > RTX 5090(62.5): 'best overall = RTX 5090' 推荐在框架自身算术下不成立 (翻转)。
'RTX 5090 最佳 7B' 结论在 L1/L2 下仍成立 (0.34 是 $/tok_7b 最低值, 重算排名 #1)。
修复项: (a) 权重归一化到 1.0 (b) 重算全部 total (c) rankings_7b 按 $/tok 重排或注明口径 (d) 重新导出 best_overall 推荐。

## L4 交叉验证 (独立来源)
hardware_matrix / recommendations / uncertainties 三个字段待联网核实 (subagent 因本地模型过慢超时，改为主会话执行)。

## L4 外部来源复核 (2026-09-09, 网页 2 次, 官方产品页)
1. RTX 5090 — https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
   官方确认: "Starting at $1999" (MSRP ✓), "32 GB of super-fast GDDR7 memory" (✓), Blackwell 架构 ✓
   未覆盖: 5841 tok/s@7B (第三方基准, 方法论相关), 零售溢价 $4700-7000 (待补)
2. H200 — https://www.nvidia.com/en-us/data-center/h200/
   官方确认: "first GPU to offer 141 GB of HBM3e memory at 4.8 TB/s" (141GB HBM3e ✓, 4800 GB/s ✓),
   Llama2 70B 推理比 H100 快 1.9X (与矩阵 H100 210 tok/s → H200 316 tok/s 量级一致)
   未覆盖: $35000 单价 (官方页无标价, 维持估计值标注)

## 系统性发现
全项目 grep (json+md, 01~04.5 所有 stage): **0 条 HTTPS 来源链接**。stage 03 coverage-proof 声称
"source attribution", 但 artifact 中不存在可追溯的 URL。stage 04 复核只完成了 2/15 设备 (5090, H200),
其余 13 个 (MI300X, A100/H100 变体, 6000Ada, 4090/4090D, M4, M4Max, SN3000, Groq, Cerebras)
的规格/价格/吞吐来源不可追溯 → 需 stage 04.5/05 补来源 (research_required)。
