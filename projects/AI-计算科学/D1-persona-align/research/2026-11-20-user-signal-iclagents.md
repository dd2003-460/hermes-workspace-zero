# Idea: 用户信号驱动的 ICL+RAG agent 进化框架（无权重更新）

> origin: human (D 2026-11-20 提出) + ai (整理/分解)
> 状态：❌ 信号源层撞车（Q1 判决，arena T-OS-1 11-20，撞车对象 ICAL 2024，agent conf 0.97 待核验）→ 转向 Q4 harness 触发回路方向（派发中，11-20 17:00）
> 素材：tools/objfunc/d-messages.json (1171 条 D 直聊消息) + memory/objfunc-signal-log.md (S1-S20)
> 进度快照：research/2026-11-20-tos1-progress.md

## 一句话

D 的肯定/否定/建议/纠正是**带置信度的行为信号**（RL 类比：reward + demonstration），
把它们固化成 ICL 示例库 + RAG 召回，构成一个**不改权重**的 agent 进化框架——
比 skill（hermes 卖点）更细（信号级 vs 流程级）、更有可分析标准（漏斗指标可量化）。

## 为什么值得做（D 的判断 + 我的补充）

1. **信号粒度**：skill 是流程级（"怎么做 X 类任务"），信号是行为级（"这次你偏了，偏在哪"）。
   1171 条消息里已分出评价信号（反问/建议/纠正）+ 行为信号（cli 命令=注意力分配），两类都可用。
2. **可分析标准**：漏斗指标（捕捉→归因→落地）+ 反问率（按周）= 进化有没有发生可测量。
   现有 skill 体系没有这个闭环——skill 写了但有没有用、有没有偏，没人测。
3. **无权重更新**：ICL+RAG 路线 = 纯 prompt/记忆层，本地 27b 可跑，符合 D 的
   "prompt+hook 不改权重" 约束（USER.md）。
4. **数据已就位**：提取脚本 + 1171 条素材 + 20 条已归因信号 = 冷启动数据。

## 分解树（正交子项 + 缺口）

| # | 子项 | 状态 | 缺口 |
|---|------|------|------|
| 1 | **碰撞调研**：这个 idea 撞了谁（ExpeL/Reflexion/Voyager/SEAL/Eureka/DGM/自进化 survey） | 🔍本轮启动 | 四象限搜索 + 概念级核验（collision-research skill） |
| 2 | **信号形式化**：信号 schema（类型/置信度/层/归因/落地状态）→ 可检索单元 | 🔸部分（objfunc-signal-log 已有雏形） | 置信度怎么从语气/上下文估；行为信号（cli）怎么归因 |
| 3 | **ICL 固化**：信号 → few-shot 示例（"遇到 X 情境，D 的期望行为是 Y"） | ❓ | 示例格式；多少条示例有效（ICL 剂量-效应） |
| 4 | **RAG 召回**：任务时检索相关信号（按层/情境/时间衰减） | ❓ | 检索键设计；与现有 hook 注入的关系（替代/互补） |
| 5 | **进化验证**：漏斗指标 + 反问率作为"进化发生"的测量 | 🔸部分（指标已定义） | 基线数据（分类 subagent 在跑，1171 条） |
| 6 | **与 skill 的关系**：信号库 vs skill 库的正交性/层级 | ❓ | 信号累积到何时该结晶成 skill（结晶判据） |

## 碰撞候选（待核验，凭本地 lit-survey 记忆，conf 0.5）

| 候选 | 重叠点 | 差异假设 |
|------|--------|---------|
| ExpeL (2308.10144) | 从轨迹抽 insight → 记忆库 → ICL 检索 | 它抽的是任务成功/失败，我的是用户反馈信号（带置信度） |
| Reflexion (2303.11366) | 语言化反思 → 情景记忆 | 它的反思是 agent 自产的，我的是用户给的（外部监督） |
| Voyager (2305.16291) | skill library 累积 | skill 是代码级，信号是行为级 |
| SEAL (2506.10943) | 反思触发自我更新 | SEAL 改权重/代码，我不改 |
| Eureka (2310.12931) | 反思改写目标函数文本 | 它改 reward 定义，我改行为示例 |
| Darwin Gödel Machine (2025) | 自进化 agent | 它进化代码，我进化 prompt 层 |
| Self-Evolving Agents survey (2507.21046) | 领域全景 | 查它有没有覆盖"用户反馈信号→ICL"这个具体组合 |
| ACE / Agentic Context Engineering (2510.04995，凭记忆未核验) | playbook + delta 更新循环（"上下文梯度"） | 信号来源是任务执行结果 vs 我的用户反馈信号；机制最像，需读原文确认 |
| TextGrad (2406.07496) / OPRO (2309.03409) / DSPy | training 类比→prompt 层优化（文本梯度/迭代改写/编译优化） | 它们优化的是任务性能，信号源不是用户反馈——确认"类比迁移多、用户反馈信号源少"这个粗判 |

**核心新颖性假设（待证伪）**：用户反馈信号（带置信度、分评价/行为两类）→ ICL+RAG 固化，
这个**具体组合**没有先例；单组件（反思/记忆/skill/自进化）都有先例。
conf 0.4——没查过，纯从本地 lit-survey 推的。

## 调研计划（大批交叉，D 已认可）

1. 四象限搜索（collision-research skill）：权威/小众/近 3 月/历史
2. 概念级核验：ExpeL 和 self-evolving survey 的 related work 追引用链
3. 交叉验证：≥2 个独立 LLM（ego-browser）核验"组合是否已有先例"
4. 外包优先：arena agent mode（若通道可用）；不可用则 ego-browser 自做
5. 落盘：本文件 §碰撞结论 + 新颖性主张收窄/放弃

## 关联

- 上游：objfunc-signal-log.md（信号台账 = 本框架的数据层）
- 下游：若调研通过 → 独立 goal（goal-template 五字段），可能进 pfb 做消融
- 正交：idea-pool #3（D 式追问模式提取=进攻侧）；本 idea=防守侧的进化机制
