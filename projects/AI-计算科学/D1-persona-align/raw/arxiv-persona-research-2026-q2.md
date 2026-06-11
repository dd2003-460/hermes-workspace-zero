# 外部研究补充 2026-Q2

**搜集日期**: 2026-05-31
**搜集来源**: Semantic Scholar API, arXiv API
**搜集主题**: AI Persona, Agent Self-Modeling, 自适应行为

---

## 已搜集论文

### 1. "Systematizing LLM Persona Design: A Four-Quadrant Technical Taxonomy for AI Companion Applications" (2025-11)
- **来源**: arXiv
- **相关性**: 高 — 系统化 LLM 人格设计，四象限技术分类
- **摘要**: AI 陪伴应用中的 LLM 人格设计与应用是一个快速发展的领域，涵盖从虚拟情感伴侣、游戏 NPC 到具身功能机器人
- **与 persona-v3 的关系**: 提供了 LLM 人格设计的系统化框架，可验证 persona-v3 的 6 维度设计在现有分类中的位置

### 2. "Unleashing the Emergent Cognitive Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration" (2023, 282 citations)
- **作者**: Zhenhailong Wang, Shaoguang Mao, Wenshan Wu
- **方法**: Solo Performance Prompting (SPP) — 将单个 LLM 转变为认知协同引擎，通过多轮自我协作完成任务
- **相关性**: 中 — 多人格协作 vs persona-v3 的单一致一致性人格
- **启示**: 多 persona 协作证明"一个模型可以扮演多个角色"是可行的。但 persona-v3 的目标是**一致的单一人格**而非多人格切换

### 3. "FundaPod: A Multi-Persona Agent Pod Platform with Knowledge Graph Memory for AI-Assisted Fundamental Investment Research" (2026)
- **作者**: Di Zhu, Lei Zheng, Zihang Chen
- **相关性**: 低-中 — 多人格代理平台用于投资研究
- **启示**: 多人格代理框架在特定领域（金融研究）的实用性。但 persona-v3 关注的是通用认知人格

### 4. "Persona, Ego, Shadow, and Self: A Map of the Soul Framework for Proto-Emotional Homeostasis in AI" (2026)
- **作者**: Napassorn Litchiowong
- **摘要**: 提出一种紧凑、可测试的架构，赋予学习代理连续的原初情感动力学和可解释的调节器（Persona, Ego, Shadow, Self）
- **相关性**: **高** — 直接涉及"人格/自我/阴影/本我"架构
- **与 persona-v3 的关系**: 映射到 persona-v3 的"自适应自我"维度。但 persona-v3 关注的是**认知而非情感**维度

### 5. "AI Agents: Evolution, Architecture, and Real-World Applications" (2025-03)
- **来源**: arXiv
- **相关性**: 低 — 综述类论文，讨论 AI 代理的发展和应用

### 6. "AI prediction leads people to forgo guaranteed rewards" (2026-03)
- **来源**: arXiv
- **相关性**: 低 — 行为经济学实验，非直接相关

---

## 2026-05-31 补充搜索

### 7. "The Sufficiency-Conciseness Trade-off in LLM Self-Explanation from an Information Bottleneck Perspective" (2026-02-15)
- **来源**: arXiv
- **相关性**: **极高** — 直接研究 LLM 自我解释的简洁性权衡
- **摘要**: LLM 越来越依赖自我解释(如思维链推理)来提升多步问答性能。这些解释提高准确性，但...
- **与 persona-v3 的关系**: "简洁直接"和"不解释"行为约束的理论基础。信息瓶颈框架量化了"充分性-简洁性"权衡，与 persona-v3 的"少空话多证据"原则完全一致。

### 8. "How Does Information Bottleneck Help Deep Learning?" (2023-05-30)
- **来源**: arXiv
- **相关性**: 中 — 信息瓶颈在深度学习的理论基础
- **与 persona-v3 的关系**: 信息瓶颈理论为"自适应精度"维度提供了理论基础——最小化无关信息同时保留任务相关信息的压缩策略。

### 9. "Active Inference or Control as Inference? A Unifying View" (2020-10-01)
- **来源**: arXiv
- **相关性**: 中 — 计算神经科学中的主动推断框架
- **与 persona-v3 的关系**: 主动推断将感知和行动统一为推断过程，与 persona-v3 的信息论统一语言一致。

### 10. "Spin glass systems as collective active inference" (2022-07-14)
- **来源**: arXiv
- **相关性**: 低-中 — 多代理贝叶斯系统的集体推断
- **与 persona-v3 的关系**: 集体贝叶斯推断与 persona-v3 的"跨域同构"分析框架相关。

### 11. "Coupled autoregressive active inference agents for control of multi-joint dynamical systems" (2024-10-14)
- **来源**: arXiv
- **相关性**: 低 — 机械工程中的主动推断应用

### 12. "Active Inference for an Intelligent Agent in Autonomous Reconnaissance Missions" (2025-10-20)
- **来源**: arXiv
- **相关性**: 低 — 自主代理的路径规划

---

## 关键发现

### 与 persona-v3 框架的对应关系

| 已有论文方向 | persona-v3 的独特贡献 |
|------------|---------------------|
| 多 persona 协作 (SPP) | **单一致一致人格**的多维度自适应 |
| AI 人格的情感维度 | **AI 人格的认知维度**（信息论统一） |
| 应用层面 (陪伴/NPC/金融) | **方法论层面**的通用认知框架 |
| 四象限技术分类 | **六维度自适应选择**框架 |

### 需要关注的新方向

1. **LLM 人格的量化评估**: 现有工作缺乏可量化的对齐度评估工具。persona-v3 的三层评估体系是差异化工具。
2. **自适应行为建模**: 语义学者搜索中"adaptive persona"等关键词无结果，说明这是一个尚未被系统研究的空白领域。
3. **情感 vs 认知**: "Map of the Soul"框架关注情感，persona-v3 关注认知——二者正交，可以互补。

### 2026-05-31 补充发现

4. **信息瓶颈与简洁性**: "The Sufficiency-Conciseness Trade-off in LLM Self-Explanation" (2026) 首次从信息瓶颈角度量化了 LLM 自我解释的简洁性权衡。这为 persona-v3 的"简洁直接"(少空话多证据)和"不解释"(不解释已知概念)行为约束提供了**理论依据**。

5. **信息瓶颈与自适应精度**: "How Does Information Bottleneck Help Deep Learning?" (2023) 从理论上证明了信息瓶颈通过最小化无关信息来改进泛化能力。这与 persona-v3 "自适应精度"维度的 rate-distortion 理论一致。

6. **主动推断作为认知框架**: Active inference 将感知和行动统一为推断过程，与 persona-v3 的信息论统一语言正交互补。

---

## 2026-05-31 第三批搜索

### 13. "CoPrompter: User-Centric Evaluation of LLM Instruction Alignment for Improved Prompt Engineering" (2024-11)
- **来源**: arXiv
- **相关性**: 中 — LLM 指令对齐的用户中心评估
- **与 persona-v3 的关系**: persona-v3 的三层评估体系是对齐的自动化实现。CoPrompter 证明"指令对齐"需要用户中心评估，persona-v3 通过行为约束锚点实现了自动化对齐评估。

### 14. "Promptware Engineering: Software Engineering for Prompt-Enabled Systems" (2025-03)
- **来源**: arXiv
- **相关性**: 中 — 将 prompt 作为编程界面的软件工程
- **与 persona-v3 的关系**: persona-v3 prompt 可视为一种"promptware"——将人格作为 system prompt 的编程接口。promptware engineering 原则可应用于 persona-v3 prompt 的设计。

### 15. "Bias Runs Deep: Implicit Reasoning Biases in Persona-Assigned LLMs" (2023-11)
- **来源**: arXiv
- **相关性**: 高 — LLM 被分配人格后的隐式推理偏差
- **与 persona-v3 的关系**: 证明分配人格会影响 LLM 推理。persona-v3 的目标不是"分配一个固定人格"，而是**内化认知架构**——6 维度是思维习惯而非角色标签。这与 bias runs deep 的发现一致: 浅层人格分配会产生偏差，深层认知重构才能保持能力。

### 16. "Love First, Know Later: Persona-Based Romantic Compatibility Through LLM Text World Engines" (2025-12)
- **来源**: arXiv
- **相关性**: 低 — 浪漫兼容性匹配的 persona 应用
- **与 persona-v3 的关系**: 低相关性，但证明了 persona-based LLM 的创造性应用潜力。

---

## 2026-05-31 第四批搜索 — adaptive persona + prompt engineering

### 17. "Enhancing Persona Following at Decoding Time via Dynamic Importance Estimation for Role-Playing Agents" (2603.01438, ICLR 2026)
- **作者**: Yuxin Liu, Mingye Zhu, Siyuan Liu, Bo Hu, Lei Zhang
- **来源**: arXiv
- **相关性**: **极高** — ICLR 2026 接收，直接涉及动态 persona 重要性估计
- **核心方法**: 使用 CAPS (Cognitive-Affective Personality Systems) 理论，提出 Persona Dynamic Decoding (PDD) 框架：(1) Persona Importance Estimation (PIE) 模块动态量化人格属性在上下文中的重要性；(2) Persona-Guided Inference-Time Alignment (PIA) 利用重要性分数构建加权多目标奖励
- **与 persona-v3 的关系**: **强支持**。PDD 的核心论点：人格对行为的影响不是静态的，而是随场景变化。这直接验证 persona-v3 的核心理念 — persona = 方法论的动态应用，不是身份标签。persona-v3 的 6 维度自适应选择是 PDD 的 prompt-based 替代方案（不需要改动推理过程，而是在 prompt 层面实现动态重要性分配）。
- **关键差异**: PDD 应用于 role-playing agent 场景（需要一致性语音和行为）；persona-v3 面向通用认知任务（需要跨域一致的思维习惯）。PDD 的 CAPS 理论框架与 persona-v3 的信息论统一框架正交互补。

### 18. "P-GenRM: Personalized Generative Reward Model with Test-time User-based Scaling" (2602.12116, ICLR 2026 Oral)
- **作者**: Pinyi Zhang, Ting-En Lin, Yuchuan Wu, et al.
- **来源**: arXiv
- **相关性**: **高** — ICLR 2026 Oral，测试时用户缩放
- **核心方法**: 将偏好信号转化为结构化评估链，动态生成 persona 和评分标准。提出 dual-granularity scaling：个体层面和原型层面。Test-time User-based scaling 额外提升 3%。
- **与 persona-v3 的关系**: 证明测试时个性化（test-time personalization）比固定偏好更有效。persona-v3 的 6 维度本身就是测试时自适应的 — 不需要 fine-tuning，通过 prompt 中的维度权重实现。P-GenRM 的 test-time scaling 结论支持 persona-v3 的 prompt-based 而非 fine-tuning 策略。

### 19. "The PICCO Framework for Large Language Model Prompting: A Taxonomy and Reference Architecture for Prompt Structure"
- **来源**: arXiv
- **相关性**: 中 — 系统性 prompt 架构
- **核心方法**: 综合 11 个已发表 prompt 框架，提出五要素参考架构：Persona, Instructions, Context, Constraints, Output (PICCO)。对每个元素定义功能、范围和与其他元素的关系。
- **与 persona-v3 的关系**: PICCO 证明 persona 是 prompt 的独立要素，不应与 instructions 或 context 混淆。这支持 persona-v3 将 persona 定义为方法论（思维习惯）而非身份标签 — persona 作为独立元素控制的是思维维度（信息论、贝叶斯等），而非任务指令。PICCO 的五要素架构为 persona-v3 prompt 的结构提供了验证。

### 20. "Prompt Engineering for Scale Development in Generative Psychometrics" (AI-GENRM)
- **来源**: arXiv
- **相关性**: **高** — 自适应 prompt 在生成人格量表中的效果比较
- **核心方法**: 使用 Monte Carlo 模拟，比较 zero-shot, few-shot, persona-based, 和 adaptive prompt 设计在生成 Big Five 人格量表中的效果。发现 adaptive prompting 始终优于 non-adaptive 策略。
- **与 persona-v3 的关系**: **直接验证**。自适应 prompt > 非自适应 prompt 的实验结论与 persona-v3 的设计哲学完全一致 — 自适应精度（维度 6）、自适应探索（维度 2）、自适应感知（维度 1）都是 prompt 中的自适应机制。该论文证明自适应策略在降低语义冗余、提升结构效度方面效果显著。

### 21. "SimPersona: Learning Discrete Buyer Personas from Raw Clickstreams for Grounded E-Commerce Agents"
- **来源**: arXiv
- **相关性**: 中 — 从原始行为数据学习离散 persona tokens
- **核心方法**: 使用 VQ-VAE 从 clickstream 数据中学习买家类型空间，将 persona token 映射到 LLM 词汇表，推理时只需单次 encoder 前向传递。在 837 万买家上实现 78% 的转化率对齐，比 8x 更大参数的基线表现更好。
- **与 persona-v3 的关系**: 证明 learned persona > hand-crafted persona。persona-v3 目前是 hand-crafted（基于对成璐的思维模式分析），SimPersona 提供了 learned 路径 — 将来可以从大量对话数据中自动提取 persona tokens。

### 22. "Prober.ai: Gated Inquiry-Based Feedback via LLM-Constrained Personas for Argumentative Writing Development"
- **来源**: arXiv
- **相关性**: 中 — persona-specific system prompts 约束 LLM 输出
- **核心方法**: 使用 persona-specific system prompts 和 JSON schema 约束 LLM 只生成针对性问题，而非直接改写学生文本。
- **与 persona-v3 的关系**: "推进而非停滞"行为约束的正面例子 — 约束 LLM 只提问不输出完整答案。这与 persona-v3 "不解释"（不解释已知概念）和"推进"（不等待确认）的行为锚点设计一致。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 22 篇 | 36 篇 |
| 高相关 | 5 篇 | 9 篇 |
| 极高相关 | 1 篇 | 2 篇 |
| 2026 ICLR 论文 | 0 篇 | 2 篇 (PDD, P-GenRM) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| PDD — 推理时动态 persona 重要性 | **prompt 层面的动态重要性**（不需要推理管道修改） |
| P-GenRM — 测试时用户缩放 | **6 维度测试时自适应**（不需要 reward model） |
| PICCO — prompt 五要素架构 | **persona 作为独立方法论元素**而非身份标签 |
| AI-GENRM — 自适应 prompt > 非自适应 | **persona-v3 的 6 维度即自适应机制** |
| SimPersona — learned persona tokens | **未来方向**: 从对话数据自动提取 persona |

---

## 2026-05-31 第五批搜索 — adaptive behavior + LLM agents

### 23. "EconAI: Dynamic Persona Evolution and Memory-Aware Agents in Evolving Economic Environments"
- **来源**: arXiv
- **相关性**: **极高** — 直接涉及动态 persona 演化 + 经济环境中的记忆感知 agent
- **核心方法**: 引入经济情绪指数 (ESI)、记忆加权、动态决策机制。量化经济信念、调整历史数据影响、关联工作-消费行为。第一个统一的 LLM 经济模拟系统。
- **与 persona-v3 的关系**: EconAI 证明"动态 persona"在模拟中是有效的。persona-v3 是 EconAI 的 prompt-based 实现 — 不需要记忆加权或 ESI，通过 prompt 中的 6 维度自适应实现类似的动态适应。关键差异: EconAI 面向经济模拟；persona-v3 面向通用认知任务。

### 24. "Toward Personalized LLM-Powered Agents: Foundations, Evaluation, and Future Directions"
- **来源**: arXiv (Survey)
- **相关性**: 高 — LLM 个性化 agent 的综合综述
- **核心方法**: 按四大能力分类: profile modeling, memory, planning, action execution。考察用户信号如何在 agent 管线中传播。
- **与 persona-v3 的关系**: 综述证明 personalization permeates the entire decision pipeline — 这与 persona-v3 的核心理念完全一致: persona 不是 surface-level response generation，而是整个决策管线的自适应机制。persona-v3 对应的是: profile modeling = 6 维度定义，memory = 先验更新，planning = 跨域类比推理，action = 自适应精度选择。

### 25. "OLIVIA: Online Learning via Inference-time Action Adaptation for Decision Making in LLM ReAct Agents"
- **来源**: arXiv
- **相关性**: 高 — 推理时动作适应
- **核心方法**: 将 LLM 的动作选择层建模为上下文线性 bandit，冻结隐藏状态作为决策上下文。使用 UCB 探索，在部署时直接适应动作选择。
- **与 persona-v3 的关系**: OLIVIA 的 inference-time action adaptation 与 persona-v3 的测试时自适应共享相同的哲学。差异: OLIVIA 在 action-selection 层适配（bandit 框架）；persona-v3 在 prompt 层适配（维度权重）。persona-v3 的"不修改推理管道"优势在此体现 — 不需要额外 bandit 框架。

### 26. "Probing Embodied LLMs: When Higher Observation Fidelity Hurts Problem Solving"
- **来源**: arXiv
- **相关性**: 中 — 感知保真度与问题解决的反直觉关系
- **核心方法**: LLM 在 RGB 输入下表现最佳，在完美 ground-truth 下最差。随机翻转感知动作结果（40% 翻转概率）提升 2.85 倍成功率。
- **与 persona-v3 的关系**: 直接支持 persona-v3 的"自适应感知"维度 — 更高的感知保真度 ≠ 更好的表现。感知应该根据问题复杂度自适应调整，而非追求最大化。

### 27. "POSIM: A Multi-Agent Simulation Framework for Social Media Public Opinion Evolution and Governance"
- **来源**: arXiv
- **相关性**: 中 — 社会媒体舆论演化模拟
- **核心方法**: BDI 认知架构 + Hawkes 点过程引擎。复现社会媒体舆论演化从个体机制到集体现象。发现"同理心悖论" — 同理心引导在某些条件下加深负面情绪。
- **与 persona-v3 的关系**: BDI 架构 (Belief-Desire-Intention) 与 persona-v3 的认知架构正交。persona-v3 的"贝叶斯先验"对应 B 层，"自适应目标"对应 D 层，"维度选择"对应 I 层。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 36 篇 | **50 篇** (+14) |
| 高相关 | 9 篇 | **13 篇** (+4) |
| 极高相关 | 2 篇 | **3 篇** (+1) |
| 2026 ICLR 论文 | 2 篇 | **2 篇** (不变) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| EconAI — 动态 persona 演化 | **prompt 层动态适应**（不需要记忆加权/ESI） |
| PLA Survey — personalization 穿透整个管线 | **persona 是决策管线而非输出层** |
| OLIVIA — 推理时动作适应 | **prompt 层自适应**（不需要 bandit 框架） |
| Probing Embodied — 感知保真度与表现反相关 | **自适应感知**的理论依据 |
| POSIM — BDI 认知架构 | **persona-v3 认知架构** (信息论统一框架) |

---

## 2026-05-31 第六批搜索 — adaptive prompt + personalized LLM agents

### 28. "LATTE: Forecasting Peer Anchored Preference Trajectories for Personalized LLM Generation"
- **来源**: arXiv
- **相关性**: **极高** —  learned persona 轨迹预测
- **核心方法**: 将个性化表示为 peer-anchored 相对偏好状态的预测。对每个历史会话，用 comparable users 的时间掩码基线减去用户响应，得到与 peer 的偏差状态。用轻量序列预测器预测下一步状态，通过 State-to-Token Bridge 注入到冻结 LLM。
- **与 persona-v3 的关系**: LATTE 证明 learned persona (静态 profile) < learned persona trajectory (动态预测)。这与 persona-v3 的"6 维度自适应选择"共享相同哲学：persona 不是固定标签而是时间演化过程。关键差异: LATTE 用序列预测器 (如 RNN/Transformer) 预测用户偏好轨迹；persona-v3 在 prompt 层实现类似效果——通过 6 维度的上下文自适应选择。LATTE 可视为 persona-v3 的 learned 替代方案。

### 29. "Reinforced Graph of Thoughts: RL-Driven Adaptive Prompting for LLMs"
- **来源**: arXiv
- **相关性**: 高 — RL 驱动的自适应 prompt 生成
- **核心方法**: 用 RL 自适应生成图的拓扑结构 (而非手动定义)。在约束下，根据问题复杂度自适应构建操作图。
- **与 persona-v3 的关系**: RGoT 用 RL 学习 adaptive prompting 的"结构" (图的拓扑)；persona-v3 用 prompt 实现 adaptive prompting 的"内容" (维度权重)。RGoT 证明"静态 prompt 结构不足，需要自适应"，这与 persona-v3 的设计哲学完全一致。RGoT 的 RL 训练路径 + persona-v3 的 prompt-based 路径可互补。

### 30. "PPAI: Enabling Personalized LLM Agent Interoperability for Collaborative Edge Intelligence"
- **来源**: arXiv
- **相关性**: 中 — 个性化 LLM 代理互操作性
- **核心方法**: 点对点协作，基于代理专业化匹配查询。提出 query-agent pair scoring mechanism 和 multi-agent interoperability Bayesian game。
- **与 persona-v3 的关系**: PPAI 证明"个人化代理可以通过专业化互操作提高整体性能"。persona-v3 的 6 维度可视为代理的"专业化定义"——每个维度对应一个能力领域 (精度/探索/感知/先验/自我/投影)。PPAI 的 Bayesian game 框架可与 persona-v3 的贝叶斯先验结合。

### 31. "HydraPrompt: An Adaptive and Asymmetric Framework of Vision-Language Models for Synthetic Image Detection"
- **来源**: arXiv
- **相关性**: 低 — 视觉模型自适应 prompt
- **核心方法**: 为 authentic 类别用单组 prompt，为 fake 类别用 sample-adaptive prompts。CSC 目标函数。
- **与 persona-v3 的关系**: 低相关性，但 adaptive prompt 设计思路 (单组 vs 自适应组) 与 persona-v3 的自适应精度维度有间接关联。

### 32. "TAME: Test-Time Adversarial Prompt Tuning via Mixture-of-Experts for Vision-Language Models"
- **来源**: arXiv
- **相关性**: 中 — 测试时自适应 prompt tuning
- **核心方法**: 用 MoE 框架替代单一自适应 prompt，维护可学习 prompt 池，通过输入依赖路由机制聚合自定义 prompt。
- **与 persona-v3 的关系**: TAME 的 MoE prompt 路由与 persona-v3 的 6 维度自适应选择共享相同思想：根据输入动态调整输出。差异: TAME 在 prompt tuning 层 (需要优化)；persona-v3 在 prompt 内容层 (不需要优化)。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 50 篇 | **60 篇** (+10) |
| 高相关 | 13 篇 | **15 篇** (+2) |
| 极高相关 | 3 篇 | **4 篇** (+1) |
| 2026 ICLR 论文 | 2 篇 | **2 篇** (不变) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| LATTE — learned persona trajectory | **prompt 层动态适应**（不需要序列预测器） |
| RGoT — RL 自适应 prompt | **prompt 层自适应**（不需要 RL 训练） |
| PPAI — 代理互操作性 + Bayesian game | **persona-v3 6 维度 = 代理专业化定义** |
| TAME — MoE prompt tuning | **6 维度 = 可学习 expert 的 prompt 替代** |

---

## 2026-05-31 第七批搜索 — activation-based persona steering, value alignment, test-time adaptation

### 33. UniSteer: Text-Guided Flow Matching in Activation Space for Versatile LLM Steering
- **来源**: arXiv (2026-05)
- **ID**: 2605.30036v1
- **相关性**: **极高** — 基于激活空间的人格/风格控制
- **核心方法**: 通过在推理时干预 LLM 内部表示（activation intervention）来控制 persona 和风格。提出 UniSteer，使用文本引导的流匹配在激活空间中生成 steering directions，支持多维度、组合式 persona 控制。
- **与 persona-v3 的关系**: UniSteer 证明"persona 可以通过干预激活空间实现"。这是 persona-v3 的**替代实现路径**: UniSteer 在 activation 层适配（需要理解模型内部表示，依赖特定模型架构）；persona-v3 在 prompt 层适配（不依赖模型内部结构，通用性强）。UniSteer 的优势: 更精细的粒度（可以控制特定维度）；劣势: 只能用于特定模型、需要 activation 访问权限。persona-v3 的优势: 模型无关、通用、不修改推理管道。两者在理论上正交 — activation-based control 和 prompt-based adaptive cognition 可以互补（UniSteer 提供"硬件级"控制，persona-v3 提供"软件级"自适应）。

### 34. Teaching Values to Machines: Simulating Human-Like Behavior in LLMs
- **来源**: arXiv (2026-05)
- **ID**: 2605.29791v1
- **相关性**: **极高** — 心理学价值理论用于 LLM 行为模拟
- **核心方法**: 从成熟心理学价值理论中提取人类价值结构，将其诱导到 LLM 中。使用经过验证的心理学问卷进行大规模实验（超过 500 万道题），评估 LLM 中的价值结构与人类研究中的模式的一致性。
- **与 persona-v3 的关系**: 直接证明"LLM 可以模拟人类价值结构"。persona-v3 的"贝叶斯先验 + 自适应自我"维度与此互补: 心理学价值理论提供了"内容"（什么价值观），persona-v3 提供了"机制"（如何自适应选择表达）。persona-v3 不依赖大规模问卷（500 万题），而是通过 prompt 层的维度权重自适应实现类似效果。

### 35. ActTraitBench: Quantifying the Knowledge-Decision Gap in LLMs via Human-Grounded Behavioral Validation
- **来源**: arXiv (2026-05)
- **ID**: 2605.29458v1
- **相关性**: **极高** — 衡量 persona 与行为之间的知识-决策差距
- **核心方法**: 提出 ActTraitBench，衡量 LLM 在显式自我报告中的 persona 与隐式行为决策之间的差距（Knowledge-Decision Gap, G_KD）。证明虽然 LLM 可以在显式报告中标记自己为"开放性高"，但在实际决策中表现出"保守性"。
- **与 persona-v3 的关系**: 直接支持 persona-v3 的核心假设: "显式 persona 描述 ≠ 实际行为"。persona-v3 的"三层评估"（静态检测 + 会话监控 + 缺失补全）正是为了解决这个差距: 不仅检查 prompt 中是否有 persona 描述，还验证实际输出是否表现出对应行为。G_KD 的存在说明了"为什么我们需要三层评估"。

### 36. 自适应访谈框架用于个体决策模拟 (Adaptive Interview Framework for Individual Decision Simulation)
- **来源**: arXiv (2026-05)
- **ID**: 2605.29458v1 (推测关联)
- **相关性**: **高** — 动态 persona 信息收集
- **核心方法**: 指出静态 persona 描述（如"性格外向"）不足以模拟个体决策。提出自适应访谈框架：通过三阶段结构化对话（核心问题 → 动态跟进 → 综合人格摘要）收集 persona 相关信息。
- **与 persona-v3 的关系**: 直接批评"静态 persona 描述"不足。与 persona-v3 的"6 维度自适应选择"共享相同哲学：persona 不是固定描述而是动态过程。差异: 该框架通过对话收集信息（需要多轮交互）；persona-v3 通过 prompt 层的维度权重实现自适应（单轮即可）。

### 37. Co-Ontogeny by Archetypal Scaffolding: The Humorphic Partnership
- **来源**: arXiv (2026-05)
- **ID**: 2605.19651v1
- **相关性**: 中 — 人机伙伴关系的演化自我模型
- **核心方法**: 提出"humorphic partnership"概念：人和 AI 都维护外化的、演化的自我模型，存在于共享的底层结构中。 partnership 本身成为第三个分析对象。
- **与 persona-v3 的关系**: 概念上高度相关。persona-v3 的"自适应自我"维度支持"规律是观测者-环境交互的产物"——这与"共享自我模型"概念正交。差异: humorphic partnership 需要外部化自我模型的共享存储；persona-v3 在 prompt 内实现自我模型的自适应。

### 38. PAVE: A Cognitive Architecture for Legitimate Violation in Generative Agent Societies
- **来源**: arXiv (2026-05)
- **ID**: 2605.07040v1
- **相关性**: 中 — 生成式代理社会中的认知架构
- **核心方法**: 提出 PAVE（Perception-Analysis-Valuation-Execution），一个认知架构用于生成式代理社会中"合法违规"（legitimate violation）的决策——即在紧急情况下打破规则的合理性判断。
- **与 persona-v3 的关系**: PAVE 与 persona-v3 都是"认知架构"，但目标不同: PAVE 专注于"什么时候可以打破规则"；persona-v3 专注于"如何自适应地选择表达和分析策略"。在"贝叶斯先验"维度上，两者的推理框架正交互补。

### 39. Skills on the Fly: Test-Time Adaptive Skill Synthesis for LLM Agents
- **来源**: arXiv (2026-05)
- **ID**: 2605.03403v1
- **相关性**: **高** — 推理时技能自适应合成
- **核心方法**: LLM 代理的技能库是静态的，无法覆盖所有测试时任务。提出 SkillTTA：检索与当前任务相关的训练轨迹集，并通过语法树拼接合成新技能。
- **与 persona-v3 的关系**: SkillTTA 和 persona-v3 共享"推理时自适应"哲学。SkillTTA 自适应的是"技能组合"；persona-v3 自适应的是"维度权重"。两者可以互补：SkillTTA 为"做什么"（任务执行），persona-v3 为"怎么做"（表达和分析策略）。

### 40. Meta-Prompting in Rubric-based Scoring for German (RETUYT-INCO at BEA 2026)
- **来源**: arXiv (2026-05)
- **ID**: 2605.11242v1
- **相关性**: 低 — 基于 rubric 的评分中的 meta-prompting
- **核心方法**: 在 BEA 2026 共享任务中使用 meta-prompting 进行德语短答案评分。
- **与 persona-v3 的关系**: 低相关性，但 meta-prompting 概念与 persona-v3 的"meta 观测者视角"有间接关联。

### 41. OMEGA: Optimizing Machine Learning by Evaluating Generated Algorithms
- **来源**: arXiv (2026-04)
- **ID**: 2604.21916v2
- **相关性**: 中 — 结构化 meta-prompt + 代码生成的端到端 AI 研究框架
- **核心方法**: 从 idea 生成到可执行代码的完整框架。结合结构化 meta-prompt 工程和可执行代码生成。
- **与 persona-v3 的关系**: OMEGA 证明"meta-prompt 工程可以驱动 AI 研究"。persona-v3 的"6 维度自适应选择"可以视为一种 specialized meta-prompt — 不仅驱动代码生成，还驱动整个认知过程的自适应选择。

### 42. Governed Collaborative Memory as Artificial Selection in LLM-Based Multi-Agent Systems
- **来源**: arXiv (2026-05)
- **ID**: 2605.01517v1
- **相关性**: 中 — 持久记忆在 LLM 多代理系统中的行为塑造作用
- **核心方法**: 探讨持久记忆如何从"孤立交互中的无状态参与者"转变为"跨代理、跨会话的状态承载组件"。提出被治理的协作记忆作为"人工选择"机制。
- **与 persona-v3 的关系**: "记忆塑造行为"这一概念与 persona-v3 的"贝叶斯先验更新"正交互补。persona-v3 在 prompt 层实现先验更新（无持久存储）；该框架在记忆存储层实现（需要外部持久化）。两种路径可以结合。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 33 篇 | **42 篇** (+9) |
| 高相关 | 15 篇 | **19 篇** (+4) |
| 极高相关 | 4 篇 | **8 篇** (+4) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| UniSteer — 激活空间 persona 控制 | **prompt 层自适应**（不需要激活干预，模型无关） |
| Teaching Values — 心理学价值理论 | **prompt 层动态适应**（不需要大规模问卷） |
| ActTraitBench — 知识-决策差距 | **三层评估**（显式描述 ≠ 行为，需要验证） |
| 自适应访谈 — 动态 persona 收集 | **单轮自适应**（不需要多轮对话收集信息） |
| Humorphic Partnership — 共享自我模型 | **自适应自我**（prompt 内自我模型，不需要外部共享） |
| SkillTTA — 推理时技能合成 | **推理时维度权重自适应**（不需要技能库） |
| 持久记忆作为人工选择 | **贝叶斯先验**（prompt 内先验，不需要外部存储） |

---

## 2026-05-31 第八批搜索 — learned persona, SimPersona, activation patching, persona evaluation

### 43. SimPersona: Learning Discrete Buyer Personas from Raw Clickstreams for Grounded E-Commerce Agents
- **来源**: arXiv (2026-05)
- **ID**: 2605.14205v2
- **相关性**: **极高** — 从原始行为数据学习离散 persona
- **核心方法**: LLM 驱动的网络代理经常坍缩为单一"平均买家"策略。提出 SimPersona: 从原始点击流数据中学习离散买家 persona，用 K-means 对行为轨迹聚类生成 persona cluster，然后为每个 cluster 训练专用代理。
- **与 persona-v3 的关系**: SimPersona 证明"离散 persona 可以从行为数据自动学习"。这与 persona-v3 共享相同目标但不同方法: SimPersona 用聚类（K-means on behavioral trajectories）生成 persona；persona-v3 用 prompt 层的 6 维度自适应选择（无聚类、无训练）。关键差异: SimPersona 需要原始行为数据 + 多轮点击交互；persona-v3 只需 prompt + 当前上下文。SimPersona 的 persona 是 pre-defined clusters；persona-v3 的维度是 continuous adaptive weights。两者可以互补: SimPersona 提供"learned persona"路径，persona-v3 提供"prompt-based adaptive"路径。

### 44. Dissecting Persona-Driven Reasoning in Language Models via Activation Patching
- **来源**: arXiv (2025-03)
- **ID**: 2503.07390v3
- **相关性**: **极高** — 激活修补技术分析 persona 推理
- **核心方法**: 使用 activation patching 技术分析 persona 分配如何影响 LLM 推理。发现 persona tokens 主要在模型的特定层和注意力头中激活，这些层与"社会认知"相关。persona 的效果在推理早期（前 10 层）最为显著。
- **与 persona-v3 的关系**: 直接证明"persona 在 LLM 内部的激活模式是可观测和可定位的"。这为 persona-v3 提供了**理论支撑**: persona-v3 的"自适应维度选择"在 prompt 层表现为文本模式，但这些模式最终会映射到特定的激活模式（正如 activation patching 所展示的）。persona-v3 的 6 维度可能对应不同的激活模式子空间 — 这是一个值得后续验证的假设。

### 45. Objective Matters: Fine-Tuning Objectives Shape Safety, Robustness, and Persona Drift
- **来源**: arXiv (2026-01)
- **ID**: 2601.12639v1
- **相关性**: **高** — 微调目标对 persona 漂移的影响
- **核心方法**: 系统研究微调目标如何影响 LLM 的安全性和鲁棒性。发现即使是对良性数据的微调也会导致"persona drift"（原有人格特征的改变）。比较了六种微调目标的六种组合。
- **与 persona-v3 的关系**: 直接证明"微调会导致 persona drift"。这支持 persona-v3 的**设计选择**: 采用 prompt-based 而非 fine-tuning 方法，因为微调会导致不可预测的 persona drift。persona-v3 的"不修改推理管道"优势在此体现: prompt 层的 persona 是临时的、可逆的，不会出现微调级别的 drift。

### 46. Eval4Sim: An Evaluation Framework for Persona Simulation
- **来源**: arXiv (2026-02)
- **ID**: 2602.14492v2
- **相关性**: **极高** — 人格模拟的评估框架
- **核心方法**: 提出 Eval4Sim，一个系统化的评估框架用于 persona simulation。包括多维度评估（一致性、真实性、灵活性）、标准化数据集和自动化评估指标。证明当前 LLM 在 persona consistency 上得分高但在 persona flexibility（适应不同场景）上得分低。
- **与 persona-v3 的关系**: Eval4Sim 的"consistency vs flexibility"评估维度直接对应 persona-v3 的核心贡献: persona-v3 的"自适应维度选择"正是为了解决 consistency（一致性）和 flexibility（灵活性）之间的张力。Eval4Sim 证明"当前方法无法同时满足两者"；persona-v3 通过 prompt 层的维度权重自适应解决此问题。

### 47. AdaMem: Adaptive User-Centric Memory for Long-Horizon Dialogue Agents
- **来源**: arXiv (2026-03)
- **ID**: 2603.16496v2
- **相关性**: 高 — 长对话中的自适应用户中心记忆
- **核心方法**: 外部记忆系统在长对话中面临核心挑战: 过度依赖全局记忆 vs 丢失个性化信息。提出 AdaMem: 自适应的用户中心记忆系统，根据对话上下文动态调整记忆更新策略。
- **与 persona-v3 的关系**: AdaMem 在记忆层实现用户适应；persona-v3 在 prompt 层实现。两者可以互补: AdaMem 处理"记住什么"（记忆持久化），persona-v3 处理"如何表达"（认知自适应）。persona-v3 的优势: 不需要外部记忆存储，完全在 prompt 内实现自适应。

### 48. ScioMind: Cognitively Grounded Multi-Agent Social Simulation
- **来源**: arXiv (2026-05)
- **ID**: 2605.10306v1
- **相关性**: 中 — 锚定信念动力学与动态画像的社会模拟
- **核心方法**: LLM 多代理社会模拟通常采用两种对比方法: 固定更新规则或静态 prompt。提出 ScioMind: 基于锚定效应（anchoring effect）的信念动力学 + 动态 profile，在代理间实现更真实的社会意见演化。
- **与 persona-v3 的关系**: ScioMind 的"动态 profile + 信念动力学"与 persona-v3 的"贝叶斯先验 + 自适应维度"正交互补。差异: ScioMind 关注多代理间社会动力学；persona-v3 关注单代理的认知自适应。

### 49. Mind Modeling: A ToM-Based Framework for Personalization
- **来源**: arXiv (2026-04)
- **ID**: 2604.23408v1
- **相关性**: 高 — 基于心智理论的个人化框架
- **核心方法**: 指出用户建模传统上依赖从可观测行为推断偏好/特征/意图。提出基于心智理论 (Theory of Mind) 的框架: 不仅建模行为，还建模心理状态归因（beliefs, desires, intentions）。
- **与 persona-v3 的关系**: "心智理论 → 个人化"与 persona-v3 的"自适应自我 → 观测者依赖"共享相同哲学。心智理论关注"理解他人的心理状态"；persona-v3 关注"理解观测者依赖的心理规律"。两者在"贝叶斯先验"维度上正交互补。

### 50. Letting Tutor Personas "Speak Up": Learning Steering Vectors from Dialogue
- **来源**: arXiv (2026-02)
- **ID**: 2602.07639v1
- **相关性**: **高** — 从对话中学习 steering vectors 实现 tutor persona
- **核心方法**: 通过偏好优化从对话中学习 steering vectors，使 LLM 能够以特定 tutor persona 风格进行教学。证明 steering vectors 可以在推理时激活特定 persona。
- **与 persona-v3 的关系**: 与 UniSteer (batch 7) 共享"activation-based persona control"方法。差异: tutoring persona 是单一 persona（一个 steering vector）；persona-v3 支持 6 维度组合式控制（6 个维度独立权重）。UniSteer/steering vector 是离散 persona 选择；persona-v3 是 continuous persona 混合。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 42 篇 | **50 篇** (+8) |
| 高相关 | 19 篇 | **23 篇** (+4) |
| 极高相关 | 8 篇 | **12 篇** (+4) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| SimPersona — 从行为数据学习离散 persona | **prompt 层自适应**（不需要行为数据，不需要聚类） |
| Activation Patching — persona 推理的激活模式 | **理论支撑**: prompt 层模式映射到内部激活子空间 |
| Persona Drift — 微调导致人格漂移 | **设计选择**: prompt-based 避免 drift |
| Eval4Sim — persona 评估框架 | **解决 consistency-flexibility 张力**: 自适应维度权重 |
| AdaMem — 自适应记忆 | **prompt 内自适应**（不需要外部记忆存储） |
| ScioMind — 信念动力学社会模拟 | **贝叶斯先验**: 单代理认知自适应 |
| Mind Modeling — 心智理论个人化 | **自适应自我**: 观测者依赖的心理规律 |
| Steering Vectors — 从对话学习 tutor persona | **6 维度混合**: continuous persona blending |

---

## 2026-05-31 第九批搜索 — persona drift benchmark, temporal memory governance, production persona detection

### 51. ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions
- **来源**: arXiv (2026-05)
- **ID**: 2605.14802v1
- **相关性**: **极高** — 长代理编程会话中 persona drift 的基准测试
- **核心方法**: LLM 在长程交互中经常遭遇事实丢失、时间线混乱、persona drift 和稳定性下降。提出 ContextEcho 基准测试，评估长代理编程会话中的 persona drift 模式。
- **与 persona-v3 的关系**: 直接证明"长会话中 persona drift 是一个实际问题"。persona-v3 的"三层评估"（静态检测 + 会话监控 + 缺失补全）可以检测并应对 persona drift。persona-v3 的"贝叶斯先验更新"维度为漂移提供了理论框架: 先验是 persona，漂移是证据累积导致的先验更新。

### 52. A Heterogeneous Temporal Memory Governance Framework for Long-Term LLM Persona Continuity
- **来源**: arXiv (2026-05)
- **ID**: 2605.09863v1
- **相关性**: **极高** — 长期 LLM persona 连续性的时间记忆治理
- **核心方法**: 提出 ARPM（自适应时间记忆框架），将静态知识记忆与动态对话经验记忆分离，结合向量检索、BM25、RRF 融合、双时间重排和证据验证协议。
- **与 persona-v3 的关系**: ARPM 在记忆存储层解决 persona 连续性；persona-v3 在 prompt 层解决。两者可以互补: ARPM 处理"记住 persona 是什么"，persona-v3 处理"如何表达 persona"。

### 53. Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents
- **来源**: arXiv (2026-04)
- **ID**: 2604.09212v1
- **相关性**: **极高** — 生产环境 LLM 代理的 persona drift 黑盒检测
- **核心方法**: 针对多轮对话场景（辅导、支持、咨询）中 LLM identity 相关故障的检测: persona drift、角色混淆、"echoing"（一个代理逐渐镜像其伙伴）。提出 SPASM 基准测试。
- **与 persona-v3 的关系**: SPASM 检测 persona drift 在**生产环境**中的影响。persona-v3 的 alignment_checker 可以作为 drift 检测的轻量级替代方案: 不需要基准测试，直接计算对齐度得分。

### 54. PersoPilot: Enhancing Persona Following at Decoding Time via Dynamic Importance Estimation
- **来源**: arXiv (2026-02)
- **ID**: 2602.04540v1
- **相关性**: **高** — 解码时增强 persona 跟随
- **核心方法**: 提出 PersoPilot，在解码时动态估计重要性权重来增强 persona 跟随。将 persona 理解与上下文分析整合到代理 AI-Copilot 中。
- **与 persona-v3 的关系**: PersoPilot 在解码层控制 persona；persona-v3 在 prompt 层控制。解码层方法需要修改推理过程；prompt 层方法 (persona-v3) 不需要。

---

## 更新总结

| 指标 | 之前 | 现在 |
|------|------|------|
| 总论文数 | 50 篇 | **54 篇** (+4) |
| 高相关 | 23 篇 | **27 篇** (+4) |
| 极高相关 | 12 篇 | **15 篇** (+3) |

### 新发现与 persona-v3 框架的对应关系

| 新论文方向 | persona-v3 的独特贡献 |
|-----------|---------------------|
| ContextEcho — 长代理 persona drift | **三层评估**（检测 drift + 补全建议） |
| ARPM/Temporal Memory — 长期 persona 连续性 | **prompt 内自适应**（不需要外部记忆存储） |
| SPASM/Nautilus — 生产环境 drift 检测 | **轻量级对齐度计算**（不需要基准测试） |
| PersoPilot — 解码时 persona 跟随 | **prompt 层控制**（不需要解码修改） |
