# decomp · Jin 线路调研（agent 脚手架 / MCTS+harness / agent 层 RSI）
# origin: ai · 2026-11-22 · D 指令："先往 jin 这个方向找，我们的 bench/judge 机制/改善点，jin 可以算一个，继续滚雪球调研"

## 最终目标
把 Jin 线（agent 脚手架 + MCTS + 持久记忆）作为对标，摸清业界 agent 可靠性评测的 bench + judge 机制，
找出我们 bench（gold-facts + D1-D5 + 三版 A/B）的改善点，落盘可执行清单。

## 分解树（正交子项）

### S1 我们的 bench/judge 现状盘点（本地，已完成）
- gold-facts.md：单题锚点（H100 PCIe vs SXM，含 14x 隐藏矛盾）
- scoring-r1.md：D1-D5 五维判据（矛盾发现/缺口识别/幻觉率/工具使用/自校准）
- v3/v4/v5 三版 A/B：工具边界 + prompt 边界证据链
- 缺口：n=1 单题单模型；judge=我（Lead）人工判，无自动化；无跨题泛化

### S2 Jin 线的评测机制（外查）
- MoLRSI 怎么评：hit rate 定义？谁判 hit（专家/模型/自动）？
- SAGA 怎么评：Analyzer 终止判据 + 人工评审？
- 缺口：[待核验] MoLRSI 的 hit rate 15.9% vs 8.7% 的判定流程

### S3 业界 agent 可靠性 bench 谱系（外查，滚雪球）
- 候选：AI-Scientist / AI-Scientist-v2 / AgentBench / GAIA / BrowseComp / DeepResearch 类
- 每家的 judge 机制：LLM-as-judge？人工？自动验证？
- 缺口：[待核验] 各家 judge 的可靠性验证（judge 本身怎么被评）

### S4 judge 机制设计模式（外查）
- LLM-as-judge 的已知偏差（position/verbosity/self-preference）
- 小模型 judge 的可行性（我们的约束：本地 27b，无 frontier API）
- 缺口：[待核验] 27b 当 judge 的校准数据（我们 scoring-calib 事故是 1 例）

### S5 改善点清单（综合 S1-S4 产出）
- 我们 bench 缺什么、加什么、成本多少
- 落盘：tasks/bench-improvement-20261122.md

## 执行顺序
S1（已完成）→ S2（Jin 线全文已在 scratch，直接提取）→ S3（arXiv API + ego-browser）→ S4（S3 延伸）→ S5（综合）
