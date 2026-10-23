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

## R3 追加：bench 校准（2026-10-24 · goal-0bc2d9c2）

> 背景：r1/r2 的 92.7 是 n=1 内部过程综合分（conf 0.8），双源交叉验证指认 3 缺陷（权重未校准/M1×M5 相关/缺终态效度）。R3 目标 = 校准过的度量。

### 分解树

```
R3 bench 校准
├── R3.1 run1 本地链路（带 M7 gate 锚点 + token 账本）      [无依赖]
├── R3.2 run2 arena 通道链路（ego-browser + pfb 中转）       [无依赖，与 R3.1 并行]
├── R3.3 run3 独立复跑（任务书变体，防复读）                 [无依赖，与 R3.1/R3.2 并行]
├── R3.4 M1-M6 两两相关矩阵 + 权重校准（|r(M1,M5)|>0.7 调整） [依赖 R3.1-3 的 bench 分]
├── R3.5 token 绝对口径（bili 账本 + 外部 ≥1 数据点对比）     [依赖 R3.1-3 的 token 记录]
└── R3.6 bench.md 更新（mean±std + M7 gate + 校准权重）+ push pfb + 第 4 轮 goal 落盘 [依赖 R3.4/3.5]
```

### 空缺清单

- [x] run 数：n=1 → 补 3（R3.1-3）
- [x] 权重推导：无 → 相关矩阵实测（R3.4）
- [x] 终态效度：无 → M7 gate（R3.1-3 每步挂锚点）
- [x] token 绝对值：无 → bili 账本（R3.5）
- [ ] 外部可比分：维度缺位（r2 实锤）→ 本轮只补"绝对口径外部数据点对比"，不虚构基准分

### 任务表（派发只执行表内条目）

| ID | 任务 | 执行者 | 依赖 | 验收锚点（M7 gate） |
|----|------|--------|------|---------------------|
| R3.1 | run1 本地完整链路：loop-state.json（run1）+ 每步锚点（测试退出码/fs diff）+ acp_cache 账本快照 + bench 分行 | Lead 本地 | 无 | 文件存在 + git hash |
| R3.2 | run2 arena 通道：ego-browser arena.ai/agent 发任务书 → pfb 中转（pull→push→ls-remote）→ arena 回执 → bench 分行 | Lead（ego-browser） | 无 | ls-remote HEAD + arena 会话 URL |
| R3.3 | run3 任务书变体复跑：任务书换 1 个新指标题（防复读），本地链路 | subagent（fresh） | 无 | 文件存在 + 与 run1 工件 diff 非空 |
| R3.4 | 相关矩阵 + 权重校准：3 run 数据 → 两两 Pearson r → 权重推导落盘 | Lead | R3.1-3 | bench.md 权重表带推导 |
| R3.5 | token 绝对口径：acp_cache 账本（3 run 输入/输出/缓存）+ 外部 ≥1 数据点（arXiv/GitHub 开源 agent 实测） | Lead | R3.1-3 | bench.md 绝对值表 + 来源 URL |
| R3.6 | 汇总：bench.md r3（mean±std）+ push pfb + ls-remote + 第 4 轮 goal 落盘 | Lead | R3.4/3.5 | ls-remote 回执 + 落盘文件 |
