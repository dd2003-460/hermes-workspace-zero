# T-OS-1 用户信号 ICL+RAG agent 进化框架 · 碰撞调研任务书

> 仓库绑定：dd2003-460/hermes-workspace-zero @ main
> 派发：2026-11-20
> 交付物：`projects/AI-计算科学/D1-persona-align/research/2026-11-20-user-signal-iclagents-collision.md`
> 回执：search-log-os1.json（检索通道/查询/命中/排除）

## 背景（给 agent 的上下文）

D 的肯定/否定/建议/纠正是**带置信度的行为信号**（RL 类比：reward + demonstration）。
本 idea 主张：把这些信号固化成 ICL 示例库 + RAG 召回，构成一个**不改权重**的 agent 进化框架——
比 skill（流程级）更细（信号级）、更有可分析标准（漏斗指标可量化）。

冷启动数据：1171 条用户直聊消息 + 20 条已归因信号（评价信号：反问/建议/纠正；行为信号：cli 命令=注意力分配）。

## 核心问题（collision check）

**Q1（最关键）**：有没有先例做「用户反馈信号（带置信度、分评价/行为两类）→ ICL 示例 + RAG 召回 → agent 行为进化」这个**具体组合**？
- 单组件都有先例（反思/记忆/skill/自进化），但"用户反馈信号→ICL+RAG 固化"这个组合有没有人做过？
- 判据：找到一篇论文/系统，其核心机制 = 从用户反馈提取信号 → 转成 few-shot 示例 → 检索召回注入 prompt → 行为改变。全命中=撞车；缺任一环节=部分重叠。

**Q2**：最近邻系统的**精确机制**（逐条读原文，不凭摘要）：
- ExpeL (2308.10144)：它抽的 insight 从哪来（任务成功/失败 vs 用户反馈）？怎么存？怎么检索？
- Reflexion (2303.11366)：反思是 agent 自产还是外部监督？
- Voyager (2305.16291)：skill 是代码级还是行为级？
- SEAL (2506.10943)：改权重还是改 prompt？
- Eureka (2310.12931)：反思改写的是什么（reward 定义 vs 行为示例）？
- Darwin Gödel Machine (2025)：进化代码还是 prompt 层？
- Self-Evolving Agents survey (2507.21046)：有没有覆盖"用户反馈→ICL"这个组合？它的分类法里这个 idea 落在哪个格子？

**Q3**：新颖性主张收窄后是什么？
- 如果 Q1 找到全命中先例 → 新颖性主张放弃，记录撞车对象。
- 如果只有部分重叠 → 收窄主张到具体差异点（如"带置信度的信号"、"评价/行为两类分治"、"漏斗可分析标准"），给出 conf。

**Q4（2026-11-20 追加 · harness 触发回路方向，D 点名感兴趣）**：
核心问题：有没有系统把「用户反馈信号」固化成 **harness 层的稳定触发器**（"遇到情境 X 就执行 Y"的固定回路），且回路本身随新信号自进化？
- 三环节拆解（每个先例逐环节命中/缺失）：
  ① 结晶判据：哪条信号该从"记忆条目"升级为"固定触发器"（判据是什么：频次？置信度？失败次数？）
  ② 触发稳定性：同一情境是否每次触发（靠确定性 hook/规则 vs 靠 LLM 当轮自决——后者=不稳定）
  ③ 回路自进化：触发→执行→产生新信号→更新触发器，闭环有没有人做
- 最近邻（逐条读原文）：
  - ACE / Agentic Context Engineering (2510.04995，凭记忆未核验)：playbook + delta 更新循环。它的 playbook 条目是"触发器"还是"示例"？更新信号源是任务执行结果还是用户反馈？触发是确定性还是 LLM 自决？
  - COVE (2608.01234，凭记忆未核验)：harness 记忆 vs 参数内化的任务感知路由。路由规则怎么产生、怎么更新？
  - Darwin Gödel Machine：它进化的"代码"里有没有"触发器"这一层？
  - Voyager skill library：skill 触发靠 LLM 自决——有没有后续工作把它改成确定性触发？
  - 搜索词建议：harness evolution / trigger-based agent behavior / procedural memory consolidation / habit formation LLM agent / rule induction from feedback / "context engineering" self-updating playbook
- 判决：找到全命中（用户反馈信号源 + 稳定触发 + 自进化三环节全有）= 撞车；缺任一环节 = 收窄主张到缺失环节，给 conf。

## 检索通道（强制，禁纯记忆）

- arXiv API（full-query + sortBy=relevance）
- 直访 arXiv 原文（读 abstract + related work 节）
- GitHub（搜 self-evolving agent / skill library / user feedback ICL）
- 搜索引擎（ego-browser 可达的）
- 每条来源标：URL + 读到的深度（abstract/全文/related-work）+ 与 Q1 判据的逐环节命中/缺失

## 验收标准

- AC1：≥15 个来源，其中 ≥8 读原文（不止 abstract）
- AC2：Q1 有明确判决（撞车/部分重叠/无先例），带逐环节命中表
- AC3：Q2 每个最近邻系统有机制拆解（信号来源/存储/检索/注入 四环节）
- AC4：Q3 新颖性主张收窄或放弃，带 conf
- AC5：search-log-os1.json 含检索通道/查询/命中/排除
- AC6：反方复核 ≥3 质询（"这个组合真的没人做吗？""置信度信号是不是过度包装？""漏斗标准是不是不可操作？"）
- AC7（Q4）：harness 触发回路三环节（结晶判据/触发稳定性/自进化）逐先例命中表 + 全命中/缺环节判决 + conf

## 方法学红线

- 禁止纯记忆引用——每条来源必须有 URL + 读取深度
- 禁止把"没搜到"当"不存在"——穷尽检索通道后才可下"无先例"
- 碰撞 ≠ 抄袭：机制部分重叠但差异点实在 = 可收窄主张，不算撞死
