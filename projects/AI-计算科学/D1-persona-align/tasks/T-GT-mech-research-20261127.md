# origin: ai

# T-GT-mech：LLM general 思考机制调研（成熟方案撞车）

[任务] 回答一个问题：**让 LLM 产生 general 推理（把抽象机制迁移到未见域解题，而非背域内套路）的成熟方法，有哪些？各自证据多强？哪些能直接搬进我们的 prompt？** 分三个子领域分别作答：
- A. prompt 级机制：meta-prompting / CoT 变体（self-consistency、least-to-most、plan-and-solve）/ 自我反思（reflexion）/ 原理抽象（先归纳规则再应用）/ reasoning shaping。每种给：做法一句话、代表文献（arXiv 号或 URL）、迁移到未见域的效果证据（有数字最好）、适用条件与失效条件
- B. 评测方法：怎么测"推理是否 general"而非"是否答对"——transfer 探针设计、域偏移检测、held-out 域电池。给可复用的判据（可量化、机械可算优先）
- C. 开源实现：GitHub 上可直接复用的 prompt 模板库 / 评测电池 / agent 脚手架（star 数 + 许可证 + 能否零改造接入）

[背景]（最小事实，其余自己搜）
- 我们的执行体：本地 Qwen3.8-27B，**只改 prompt/hook，不改权重**
- 已实测：模型能复刻"爬一层"的形式（机械指标 5.67/6），但内容 100% 域偏移——形式注入有效，机制未注入
- 我们自己的候选机制：5 模板（代价模型/统一覆盖/量化落地/类比审计/判据瓶颈），定义在 `projects/AI-计算科学/D1-persona-align/memory/general-thinking-template-20261124.md`（可参考但不必依赖）
- 调研顺序要求：GitHub（开源）→ arXiv/见刊（学术）→ 交叉验证；不确定的标"未验证"

[约束] 中文回答；每条结论标 conf(0-1)；给来源 URL；不确定的标"未验证"；不编造 arXiv 号（搜不到就写"未找到"）

[交付] markdown，两段：
1. 汇总表：`| 机制/方法 | 类别(A/B/C) | 做法一句话 | 证据(数字+URL) | conf | 可搬性(零改造/需适配/不适用) |`，≤15 行
2. 核心发现 ≤20 行：top-3 最值得搬的机制 + 各自最便宜的验证方式（在我们 27b 上怎么测，≤1 句话）
过程论证不要写进交付物。

[长度] ≤50 行

[落盘] 写入 `projects/AI-计算科学/D1-persona-align/memory/research-general-thinking-mech-20261127.md`，文件头标 `# origin: ai` + 调研时间戳。**文件不存在 = 任务未完成，Lead 不验收。**

[回执] 完成后回执必须含：repo URL + branch + commit_sha + 交付文件路径 + 实际执行的搜索次数。
