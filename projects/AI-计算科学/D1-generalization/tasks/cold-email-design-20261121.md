# 套磁邮件设计（2026-11-21）
# origin: ai
# 对象：generalization-survey-snowball-20261121.md §3 名单（泛化线）+ pfb process-depth-eval-survey §5（评测线）
# 背景：D = 理论物理背景，做 LLM 泛化实证（本地 27b + 跨域探针 + CodeARC + 压缩-泛化框架）

## 定位策略（D 的理论物理背景怎么用）
- **压缩-泛化线（Delétang/Veness）+ 动力系统线（Reddy）**：物理背景=加分项。AIT/MDL 是物理传统（Hutter 的 AIXI 就是信息论+物理），dynamical systems 直接对口。邮件里**主动亮出物理背景**，作为"能读懂你们方法核心"的证据。
- **类比推理线（Pavlick/Stevenson）**：物理背景弱相关，但**实验设计能力**（防记忆污染对照、小样本统计、能力/触发分离）是通用资产。邮件里亮"我做了 X 实验"而不是"我是物理的"。
- 核心原则：**每封邮件的"为什么是你"必须具体到论文里的某个机制/数字**，证明真读过。模板化群发 = 0 回复。

## 邮件结构（学术 cold email 通用最优，5 段 ≤150 词）
1. **Subject**：具体 + 引对方论文 + 8 词内。格式 `Question about [论文短名]: [你的具体问题]`
2. **P1 你是谁**（1 行）：身份 + 背景 + 一句话在做什么
3. **P2 为什么是你**（2 行）：论文里**具体哪个点**（机制/数字/claim），为什么它和我的工作撞上了
4. **P3 我做了什么**（2 行）：具体数字（n、命中率、p 值），让对方 10 秒判断我的水平
5. **P4 请求**（1 行）：具体 + 低成本（"15 min chat" 或 "one specific question"），不要 "if you have time to supervise me" 这种高承诺请求
6. 签名带主页/GitHub/一篇可点的东西

## 模板 A：压缩-泛化线（Delétang / Veness）— 物理背景主打

Subject: Question on LM-as-compressor: does compression predict rule induction?

Dear Prof. Delétang,

I'm [Name], a [PhD student / researcher] in theoretical physics at UCAS, now running empirical studies on LLM generalization with a local 27B model.

Your "Language Modeling Is Compression" (2309.10668) reframed prediction as compression, and I've been building on exactly that lens: I measure how much a model can *induce a hidden rule* from oracle queries (inductive program synthesis, CodeARC-style) and find a clean dissociation — the model spontaneously knows the optimal *strategy* (systematic boundary probing) yet still fails to induce the rule from the same evidence (edge-case prompt flips only 1/5 stable failures).

This looks like a behavioral instance of the compression–generalization disconnect reported in 2410.15280, but for *rule induction* rather than data compression. My question: do you expect lossless compression ratio to predict rule-induction capacity at all, or is the disconnect structural?

Happy to share the full traces (n=20, two rounds, 44% reliable solve rate) if useful. A 15-minute chat or even a one-line reaction would be great.

[Name]
[link: one-page note / GitHub]

## 模板 B：动力系统线（Reddy, UT Austin）— 物理×LLM

Subject: LLM-ACES × spontaneous ODE modeling — one question

Dear Prof. Reddy,

I'm [Name], a theoretical physics researcher at UCAS working on whether LLMs spontaneously map real-world problems onto dynamical systems.

Your LLM-ACES (2606.25039) closes the loop the other direction — LLM *discovers* the ODE. I'm probing the prior: given a scenario (rumor spread with forgetting, inventory with proportional outflow), does the model spontaneously reach for SIS / first-order linear ODE without any hint? On 27B, n=6, it hits 6/6 including scenarios with no named model.

My open question, given your closed-loop setup: when the LLM's prior model is wrong, does the adaptive search recover faster than when the prior is absent — i.e., is a wrong spontaneous prior a net asset or liability in the loop?

I'd value 15 minutes of your time, or a pointer to who on the team works on the prior-modeling side.

[Name]

## 模板 C：类比推理线（Pavlick / Musker, Cambridge）— 实验设计主打

Subject: Cross-domain probe design — counterfactual vs. novel-scenario controls

Dear Prof. Pavlick,

I'm [Name], a researcher at UCAS (theoretical physics background) running a small empirical probe on whether LLMs spontaneously apply mathematical frameworks across domains — 27B, n=6, 6/6 spontaneous hits including novel scenarios (SIS model for rumor-with-forgetting, logistic ODE for saturating growth).

Your "LLMs as Models for Analogical Reasoning" (2406.13803) frames the key question I'm trying to operationalize: superficial re-use of training-distribution patterns vs. flexible structural mapping. My current anti-memorization control is textbook-vs-novel-scenario contrast; Webb et al. (2404.13070) use counterfactual permutations. I haven't seen the two controls compared head-to-head.

Would you recommend one over the other for *math-framework* transfer (vs. letter-string analogies), or is there a third control I'm missing? Happy to share the probe set and raw outputs.

[Name]

## 模板 D：social 邮件（LinkedIn / Twitter DM 版，≤80 词）
> Hi [First name] — read your [paper short name] this week and ran a small experiment that touches exactly your [specific mechanism]: 27B spontaneously maps novel scenarios onto ODE/SIS frameworks 6/6, but fails to induce rules from the same evidence under constrained oracle feedback (1/5 flip). Curious whether you'd expect compression-style metrics to predict that gap. Would love 15 min or even a one-line take. — [Name], UCAS, theoretical physics → LLM generalization

## 发送纪律（成功率杠杆，按重要性）
1. **个性化 > 一切**：P2 必须具体到机制/数字，每封 10 分钟改，别群发
2. **发送时间**：对方时区周二~周四 9-11 点（美东/伦敦），避开周一（清邮箱）和周五下午
3. **follow-up 一次**：10-14 天后没回，发一次简短 follow-up（"bumping — I've since added X result"，带新信息，不是 "just checking in"）；两次不回复就停
4. **一次只发一个请求**：chat 或 feedback 二选一，别同时要
5. **别附大文件**：给链接（one-page note / GitHub / 匿名 HuggingFace space）
6. **发前测试**：给自己发一封，查到达的 header（SPF/DKIM 是否 pass）；.ac.cn 机构邮箱一般有 SPF，deliverability 远高于 Gmail
7. **UCAS 邮箱被屏蔽的概率**：机构域名被当 spam 的概率很低（conf 0.8，凭经验未实测）；真正风险是①对方学校的外部过滤（首次发陌生机构可能被进 spam 文件夹——follow-up 时换一句 subject 提高进 inbox 概率）②短时间发太多封触发限流（每天 ≤5 封）。**实测方法**：发 3 封后让一个朋友用 Gmail 收测试邮件看是否进 spam
8. **回复率预期**（凭经验估计，conf 0.5，无公开统计）：个性化学术 cold email 5-15%；带具体结果+具体问题的比纯"求指导"高一档；follow-up 后再加 3-5 个点。5 个对象 × 2 触达 ≈ 期望 1-2 个回复，属正常

## 待办
- [ ] 发前核实 5 个对象的**当前机构+邮箱**（组主页，来源③未验证）
- [ ] 准备 one-page note（1 页 PDF：问题+3 个实验+数字+图 1 张）
- [ ] 模板里 [Name]/[身份] 填实
- [ ] pfb 评测线 4 个对象（ResearchRubrics 等）用同结构另写 P2/P3
