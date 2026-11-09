# New Goal Criteria — 2026-11-06

## 候选 (≥3, ROI-sorted)

| # | Goal | ROI | Blocked? | 依据 |
|---|------|-----|----------|------|
| 1 | pfb-n-expansion (n=30/arm) | MEDIUM-HIGH | NO | GPU available, ~2h compute, directly tightens CIs |
| 2 | pfb-hetero-judge (R-06 closure) | HIGH | YES (arena+API) | Removes L1 limitation but cannot execute now |
| 3 | pfb-multi-model (2nd family) | HIGH | PARTIAL (70B RAM?) | Addresses L4, strongest paper upgrade if feasible |
| 4 | pfb-question-expansion (Q6-Q10) | MEDIUM | PARTIAL (gold needs arena) | Addresses L5, but gold construction is the bottleneck |

## 选择

**pfb-n-expansion** — 唯一完全可执行的 P1 项。

产投比：2h GPU time → n doubles → CI width ÷√2 → 从 "suggestive" 升级到 "robust"。
对比 hetero-judge (blocked) 和 multi-model (partially blocked)，这是当前唯一能立即产生新数据的方向。

## 验收标准预判
- 每臂 ≥30 runs (S0/S1/S5 × Q1-Q5 × r1-r6)
- Bootstrap CI 宽度 < 0.05 (vs 当前 0.05-0.13)
- S5-S0 在 n=30 下仍 p<0.01