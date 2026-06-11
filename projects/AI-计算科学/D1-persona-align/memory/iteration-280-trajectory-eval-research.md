# Iteration 280: Persona Evaluation Research — Trajectory-Level + Black-Box Drift Detection

## Action
- gap_filler_v2 评分升级后的 persona-v3-prompt.txt: 平均 0.9292 (加权匹配), 全部 6 维度 PASS
- 但关键词分数 ≠ 实际 persona 质量 — gap_filler 只能检测"缺少什么"，不能检测"质量如何"
- 外部研究: 搜索 2025-2026 最先进 persona 评估方法

## Key Findings

1. **EMPA (arXiv:2603.00552)** — 轨迹级评估 vs 孤立回复评分。方向对齐 + 累积影响 + 稳定性 三指标可映射到 persona-v3 的6维度
2. **Nautilus Compass (2026)** — 黑盒 drift 检测，适用于闭源 API。与 gap_filler 白盒方法互补
3. **The Chameleon's Limit (2026)** — "Persona Collapse" 风险: 6 维度可能 collapse 到同一行为模式。需要测量维度间互信息

## Critical Insight

当前 persona-v3 评估范式存在根本性局限:
- gap_filler = 孤立文件评分，检测"缺少关键词"
- dashboard = 静态匹配度，不做轨迹分析
- drift detection = 仅 baseline 对比

新范式应该:
- **轨迹评分** (EMPA): 在对话轨迹中评估 persona 一致性
- **黑盒检测** (Nautilus): 从输入输出行为检测 drift
- **多样性测量** (Chameleon): 检测 6 维度 collapse

## Status
- 新增 3 篇 review (EMPA/Nautilus/Chameleon)
- 外部研究总数: 19 + 3 = 22 篇
- gap_filler 评分验证: prompt 自身质量优秀 (0.9292)
- 下一步: 推进到 trajectory-level evaluation 或 black-box drift detection 实现
