# D1-efficiency-optimization 任务分解

> origin: ai · 2026-10-22 · 01-goal-decomposition

## 目标

识别成璐工作流中的效率瓶颈，通过 prompt 优化（性能/速度）+ 流程优化（减少轮次/等待）提升整体效率。

## 现有数据源

| 数据源 | 位置 | 内容 |
|--------|------|------|
| ablation-L1 实验 | `projects/decomp/bench/runs/ablation-L1/` | 11 变体 × 3run，C0=15.2/C1-small=10.0/C2-expos=16.0/C9-plain=15.3 |
| SKILL.md 88 行 | `projects/AI-计算科学/D1-persona-align/memory/human-vs-ai/research/skill-human-voice-writing/SKILL.md` | 任务卡模板 3 原则（背景最小化/长度约束/交付模板） |
| thinking-token-budget | `projects/AI-计算科学/D1-think-token-budget/` | R3 前沿映射（P1=prompt 级前沿，414.5ch/104tok 2.63x 短于 P0） |
| arena-robustness-r1 | `projects/AI-计算科学/D1-persona-align/memory/human-vs-ai/research/arena-robustness-r1.md` | 4 失败模式（落页校验/格式校验/登录态/串行提交） |
| bottleneck-report-r1 | `projects/AI-计算科学/D1-persona-align/memory/human-vs-ai/memory/bottleneck-report-r1.md` | 8 瓶颈 × SOP 覆盖矩阵（修订后 8/8 覆盖） |

## 瓶颈识别（从现有数据提取）

### B1: prompt 长度 vs 效果
- C0（21 零件）= 15.2 分 vs C1-small（9 零件）= 10.0 分 vs C2-expos（+草稿）= 16.0 分
- **发现**: 9 零件是下限（<9 丢分），12 零件是上限（>12 不涨分）
- **优化方向**: 找到每个任务的最优零件数（不是越多越好）

### B2: 草稿节驱动 C2 不驱动 C4
- C2-expos（+草稿）= 16.0 vs C0（无草稿）= 15.2，Δ=0.8 无显著
- **发现**: 草稿让模型"先想再写"，驱动计算（C2 满分），但不驱动讨论（C4 仍 1 分）
- **优化方向**: 针对 C4（保值属性）设计显式约束，不靠草稿

### B3: 契约价值 = 方差降低非分数提升
- C0 σ=0.45 vs C9-plain σ=1.53，小 3.4x
- **发现**: 契约的价值是稳定性，不是分数
- **优化方向**: 用方差（不是均分）作为 prompt 优化指标

### B4: arena 通道不稳定
- 4 失败模式：落页校验（5min 超时）/格式校验/登录态/串行提交
- **优化方向**: 已写入 SKILL.md SOP #6-#9

### B5: subagent 并发限制
- 硬上限 3 active children
- **优化方向**: 串行提交 + 任务拆分（SKILL.md SOP #8）

## 任务表

| ID | 任务 | 依赖 | 状态 |
|----|------|------|------|
| E1 | 瓶颈量化：从 acp_cache 提取历史 token 消耗（input/cached/output），计算每任务效率 | 无 | pending |
| E2 | prompt 优化实验：针对 B1（最优零件数）+ B2（C4 显式约束）设计 A/B 实验 | E1 | pending |
| E3 | 流程优化：识别 subagent 派发等待时间，设计并行调度策略 | E1 | pending |
| E4 | 效率指标体系：定义 token 效率（分/token）+ 时间效率（分/分钟）+ 稳定性（σ） | E1 | pending |
| E5 | 汇总：效率优化报告（瓶颈 × 优化方案 × 预期收益） | E2,E3,E4 | pending |

## 正交性核对

- E1（量化）→ E2/E3/E4（优化）→ E5（汇总）：单向依赖，无循环 ✓
- E2（prompt）vs E3（流程）：正交（不同优化维度）✓
- E4（指标）独立于 E2/E3（度量 vs 优化）✓
