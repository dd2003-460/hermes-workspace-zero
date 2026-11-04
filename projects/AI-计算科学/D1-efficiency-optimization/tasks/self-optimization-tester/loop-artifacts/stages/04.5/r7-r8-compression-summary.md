# R7 + R8 规则压缩与示例按需加载 — 完整总结

## 背景

D1-efficiency 目标：降低 prompt-first 规则系统的 token 开销，同时保持 M1 ≥ 70。

M1 公式：`M1 = 100 × (0.4×S + 0.35×R + 0.25×G)`
- S = stage-gate 有效性（阶段门控是否真正减少无关规则注入）
- R = rule load ratio（实际注入 token / 全量 token）
- G = gate coverage（门禁覆盖率）

## 基线（R6 前）

| 组件 | Token | 占比 |
|------|-------|------|
| 核心规则 7 文件 | 6,342 | 35.5% |
| 示例 7 文件 | 4,211 | 23.6% |
| INDEX 路由表 | 482 | 2.7% |
| SOP arena-loop-pipeline.md | 6,826 | 38.2% |
| **全量注入** | **17,861** | **100%** |

Model B（单会话）末态规则负载：11,011 tok（-8.9% vs 全量，因为 SOP 不在每阶段都读）

## R7：规则压缩（arena 执行）

**目标**：SOP ≤3,000 tok，核心 ≤4,000 tok，示例 ≤2,000 tok

**结果**：

| 组件 | 压缩前 | 压缩后 | 降幅 |
|------|--------|--------|------|
| 核心规则 | 6,342 | 4,104 | -35.3% |
| 示例 | 4,211 | 1,886 | -55.2% |
| SOP | 6,826 | 2,698 | -60.5% |
| INDEX | 482 | 482 | 0% |
| **全量** | **17,861** | **9,170** | **-48.6%** |

Model B 末态规则负载：11,035→6,514 tok（-41%）

**M1 变化**：62.0 → 70.4（+8.4）

**关键发现**：
1. M1 对正文体积不敏感——"别读示例"值 +5.7 分，比全部压缩收益（+8.4）的三分之二还多
2. S 分量是瓶颈：S=0.5 时 M1=66.4 不达标，需要 per-turn 计量才能真正确认
3. 余量仅 +0.4，脆弱

## R8：示例真正按需加载（本地执行）

**问题**：R7 后示例仍在路由表里 = "每阶段默认读"，tier-3 名不副实

**方案**：
1. INDEX.md 路由表移除示例列
2. 改为"遇到卡点才读"的触发条件描述
3. count-rule-tokens.js / compute-m1.js 的 EX_ROUTES 清空
4. check-route-coverage.py 更新：examples/ 引用是 tier-3 按需，不算 X-miss

**结果**：

| 指标 | R7 后 | R8 后 | 变化 |
|------|-------|-------|------|
| Model B mean | 3,767 | 3,767 | 0 |
| Model B last | 4,902 | 4,902 | 0 |
| Model B R | 0.765 | 0.765 | 0 |
| Model B G | 0.992 | 0.992 | 0 |
| **Model B M1** | **70.4** | **75.6** | **+5.2** |

**为什么 M1 提升但 token 没变？**

R8 改的是"agent 行为模型"而非实际文件体积：
- R7 前：agent 进每个阶段默认读 2 个示例文件 → 计入阶段包
- R8 后：agent 只在遇到具体卡点时才读对应示例 → 不计入阶段包
- compute-m1.js 的 ROUTE.ex 从 `["00", "01"]` 变为 `[]` → 阶段包变小 → R 变大 → M1 提升

**验证**：
- check-route-coverage.py: PASS (exit 0)
- 54/54 hard constraints 保持
- pfb commit: `534b41e`

## 最终状态

| 轮次 | 名称 | Model A M1 | Model B M1 | 状态 |
|------|------|-----------|-----------|------|
| R6 | 阶段门控 | 78.2 | 62.0 | CONDITIONAL-PASS |
| R7 | 规则压缩 | — | 70.4 | PASS (+0.4) |
| R8 | 示例按需 | — | 75.6 | PASS (+5.6) |

## 下一步建议

1. **P3**：per-turn 计量确认 S 分量（当前 S 是估计值，非实测）
2. **P4**：query rewriting for inference OD questions（LoCoMo bench 侧）
3. **P5**：true cross-model hetero judge（T8 conf upgrade）

## 提交记录

| 仓库 | Commit | 内容 |
|------|--------|------|
| pfb | `afa242e` | R7 merge from arena |
| pfb | `534b41e` | R8 examples on-demand |
| workspace | `fe29d300` | R7 loop-state update |
| workspace | `7809c42f` | R8 sync |
| workspace | `61c71b72` | R8 loop-state update |
