# Stage 04 验证报告 (r1) — D1-gpu-inference-hardware

日期: 2026-09-09 | 执行: 主会话直接执行 (subagent 本地 MLX 超时不可用)

## 1. 验证范围
7 个字段任务: verification_scope, hardware_matrix, cost_performance, decision_framework,
recommendations, uncertainties, report。方法: L1 独立重算 (Python) + L2 交叉一致性
($/tok=price/tok_s) + L3 加权框架复算 + L4 外部来源复核 (NVIDIA 官方页 x2, Wikipedia x1)。

## 2. 结果汇总
| 层 | 结果 | 状态 |
|----|------|------|
| L1 $/tok 重算 | 22/22 通过, 0 偏差 | PASS |
| L2 排名一致性 | rankings_7b 6 处顺序违规; score_percentile 不自洽 | FAIL (需修复) |
| L3 加权框架 | 权重和=0.90 (应=1.0); 9/11 total 不可复现; 重算 H200(65.75)>5090(62.5) best_overall 翻转 | FAIL (需修复) |
| L4 外部复核 | 3/15 设备完成: RTX 5090 ✓, H200 ✓, MI300X (内存) ✓; 均与矩阵一致, 0 矛盾 | PARTIAL |
| 来源可追溯性 | 全项目 0 条 HTTPS 链接 (stage 03 "source attribution" 不可追溯) | FAIL (系统性) |

## 3. 外部复核证据 (2026-09-09)
- RTX 5090: MSRP "Starting at $1999" + 32GB GDDR7 — NVIDIA 产品页
- H200: "first GPU to offer 141 GB HBM3e at 4.8 TB/s", Llama2 70B 1.9X H100 — NVIDIA 数据页
- MI300X: 192GB HBM3 单卡, 304 CU, 153B transistors — Wikipedia AMD_Instinct
- 未解决: MI300X 定价 $15k (无来源), 5090 零售溢价 $4700-7000, 7B tok/s 基准单源 (5841)

## 4. Overall Confidence
- 本地计算层: 0.95 (重算可复现)
- 外部证据层: 0.55 (3/15 设备; 12 设备无 URL 来源)
- 推荐可靠性: 分工作负载推荐 3/3 成立 (0.75); best_overall=5090 不稳健 (0.5, 因 L3 bug)
- **Overall: 0.72**

## 5. Stage 05 Go/No-Go
**CONDITIONAL GO**。进入 stage 05 前必须完成:
1. 修复 decision_framework 权重 (归一到和=1.0) 并复算 11 个 total — 修复后 best_overall 可能变为 H200, 报告结论需随之更新
2. 修复 rankings_7b 6 处顺序违规 + score_percentile
3. 为剩余 12 设备补 HTTPS 来源, 或将无来源单元格显式降为 low_confidence (不得静默保留)
4. MI300X 定价: 找到来源或标记 research_required 并剔除出价格类结论

## 6. 字段状态
scope ✓ confirmed | hardware_matrix ✓ confirmed | cost_performance ✓ confirmed |
decision_framework ✓ confirmed (bug 已记录) | recommendations ✓ confirmed (0.75) |
uncertainties ✓ confirmed (0.80, 5 项开放) | report = 本文
