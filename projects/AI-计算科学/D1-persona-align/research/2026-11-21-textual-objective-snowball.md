# 文字目标函数→推理分解 撞车调研（2026-11-21）
# origin: ai
# 来源①：arXiv API 本轮实查（12 组查询 + 6 篇摘要实拉）；来源②：本地 idea-pool #1 / kt-framework / objfunc-signal-log。
# 触发：D 问"有考虑把文字目标函数给 LLM 让他找最完整目标函数然后推理-分解吗"+"之前猜测的结构化先验+目标函数 bayesian vs 纯目标函数 bayesian 结果如何"+"顶会搜集够完整吗"

## §0 三问直答

### Q1 "之前猜测过"的结果 → **没有结果，题立了没做**
idea-pool #1（2026-11-15）："先验+后验更新/纯后验是否有人做过？"——状态**待核验**，arena 结果目录无命中（本轮 grep 确认）。
K^t 框架分支 III（条目 8-12）推导了"目标函数在 K 下界最上游、正交+完备防退化"，但那是**框架推导**，"结构化先验+目标函数 Bayesian vs 纯目标函数 Bayesian"的**对照实验**没设计过、没跑过、没撞车查过。
→ 这是真缺口，不是"做过了忘了"。

### Q2 "文字目标函数给 LLM 找最完整目标函数再推理-分解"考虑过吗 → 机制没实验化，但撞车比预想密
本轮 arXiv 实查（12 组查询）发现这条线**比 idea-pool #1 假设的密**，按接近度排序：

**第一梯队（直接撞"LLM 自动设计目标函数"）**
1. **SAGA** — 2512.21782（2025-12-25，v2）：*Accelerating Scientific Discovery with Autonomous Goal-evolving Agents*
   - 核心主张："automating objective function design is a central, yet **unmet need** for scientific discovery agents"——**原话承认这是未满足需求**
   - 机制：bi-level 架构，外层 LLM agent 分析优化结果→**提议新目标函数**→转成可执行形式→内层优化
   - 与我们的关系：最接近"文字目标函数→LLM 找目标函数→推理"的已发表工作。但它优化的是**科学发现任务的目标函数**（数值优化对象），不是"信息完整性约束"（K^t 框架分支 III 的判据）。**差异点=我们的"正交+完备防退化"判据在 SAGA 里没有对应物**——SAGA 只说目标可能是 imperfect proxy，没给"完整性"的可机判定义。
2. **AutoPref** — 2607.27953（2026-07-30）：*Automatic Discovery of Task-Specific Preference Objectives*
   - 自动发现任务特定的偏好目标（NCO 场景），拆成"学什么信号×怎么加权"两个设计维度
   - 与我们的关系：目标函数**自动发现**的另一实例，但域=组合优化，判据=样本效率，与"信息完整性"正交。

**第二梯队（文字→目标/规划的成熟管线，但目标函数是人工给的）**
3. **Reward Design with Language Models** — 2303.00001（2023-02）：文字 prompt 当 proxy reward function，用户给一次描述→RL 用。**文字→目标**的成熟方案，但目标是**人写的**，LLM 只做解释不做发现。
4. **Translating NL to Planning Goals** — 2302.05128（2023-02）：LLM 把自然语言目标翻译成结构化规划语言（PDDL 类）。**文字→结构化目标**的成熟方案，但同样目标是人给的，LLM 只做翻译。
5. **UtilityMax Prompting** — 2603.11583（2026-03，v4）：把 LLM 任务重构成 influence diagram，utility 函数定义在条件分布上，LLM 最大化期望效用。**形式化多目标**框架，但 utility 是人定义的，不是 LLM 发现的。
6. **SCOPE** — 2512.09897（2025-12）：LLM 当一次性 teacher 教 hierarchical planning。规划侧，目标函数不涉及。

**第三梯队（相关但偏）**：value elicitation（2510.01189 等，对齐域）、goal-evolving 的 RL 侧。

### Q3 顶会搜集够完整吗 → **不够，本轮补齐了一部分，仍有边界**
按 D 自己固化过的教训（objfunc-signal-log 11-21"滚雪球广度质疑"：看起来少时第一假设是关键词太窄）：
- 第一轮（V1-V6）词汇表偏"价值学习/目标指定"，命中稀
- 第二轮（W1-W6）换"reward design/objective discovery/goal-evolving"后**密度明显上来**（SAGA/AutoPref/UtilityMax 都是 2025-12~2026-07 的，说明这条线 2025 下半年才热）
- **仍不完整的边界**（诚实标）：
  - 只查了 arXiv，没查顶会正式 proceedings（NeurIPS/ICML/ICLR 2026 的 camera-ready 可能比 arXiv preprint 晚）
  - "结构化先验+目标函数 Bayesian"这个**精确对照**（D 之前猜的那个二选一）没查到直接撞车——但也没查到"有人明确做过这个对照"，**稀疏≠空白**（conf 0.5）
  - 中文"目标函数"的英文对应物至少有 5 个（objective function / reward / utility / preference / goal），本轮覆盖了 4 个，"preference elicitation"只查了浅层

## §1 我们的缝隙（撞车后精确定位）

| 维度 | SAGA 等已占位 | 我们的增量候选 |
|---|---|---|
| LLM 自动提议目标函数 | ✓（SAGA 外层） | 撞车，不新 |
| 目标函数的**完整性判据**（正交+完备，可机判） | ✗（SAGA 只说 imperfect proxy，无判据） | **缝隙**：K^t 分支 III 条目 9 的"正交+完备防退化"是可机判的（覆盖/可靠/新鲜/适用条件域四轴），SAGA 没有 |
| 目标函数→K 下界→K^t 前沿的链条 | ✗ | **缝隙**：SAGA 的目标函数直接进优化器，没有"K 下界由目标函数定义"这层 |
| 结构化先验 vs 纯目标函数的 Bayesian 对照 | ✗（未查到） | **缝隙（待验证）**：idea-pool #1 原题，可实验化 |

## §2 对 D 全景问题的回答（"结构化 vs bitter lesson 给文字目标函数"）

D 的全景困惑=两套路线是否对立：
- 路线 A（结构化）：人定义正交维度/分解树/目标函数（K^t 框架）
- 路线 B（bitter lesson）：把文字目标函数给 LLM，让它自己找最完整目标函数再推理-分解

**本轮调研的结论：两条路线不是对立，是同一链条的两端，且文献正在从 B 端往 A 端补判据**：
- B 端（LLM 找目标函数）：SAGA/AutoPref 已占位，2025-12 起活跃
- A 端（完整性判据）：UtilityMax 给了形式化（influence diagram）但判据是人写的；**"LLM 找目标函数 + 正交完备判据防退化"这个组合未查到占位**
- 我们的位置：**A 端的判据（K^t 分支 III）× B 端的机制（SAGA 式外层）= 组合缝隙**
- bitter lesson 的精确表述（D 11-21 版）：不是"结构先验没用"，是"结构先验的**完整性判据**可能是人给不了、LLM 从数据里能涌现的"——这个表述可实验化（给 LLM 文字目标函数，看它找出的目标函数维度是否覆盖人定义的正交集，覆盖率=判据）

## §5 精读补充（2026-11-21 第二轮）

### SAGA 机制精读（全文 + GitHub btyu/SAGA）
**不是一句话**。4 模块 agentic 框架：
- **Planner**：把科学目标分解成具体可测目标（每迭代）
- **Implementer**：把提议目标转成可执行评分函数（Claude Code agent）
- **Optimizer**：搜索候选（内层，GA/RL 等）
- **Analyzer**：分析优化结果→指出失败模式→建议下一轮目标
三档自动化：co-pilot（人参与 planner+analyzer）/ semi-pilot（人只审 analyzer）/ autopilot（全自动）
目标演化实例：analyzer 发现"活性-药性负相关""代谢不稳定基团过表达"→planner 加"代谢稳定性评分""自定义药性过滤器"→Implementer 写成 scorer 代码
**完整性机制 = 反应式**：analyzer 看失败模式，缺什么补什么。无前置正交/完备判据。

### AutoPref 机制精读
更结构化：目标函数**分解成"成对损失程序 × 集合加权程序"两个程序空间**，LLM 当搜索算子做 staged conditional search + 行为门（筛掉行为不可行程序）。
**完整性机制 = 空间覆盖**：但空间本身是人定义的，LLM 只在人画的空间里搜。

### 三种完整性机制对比（缝隙精确定位）
| | SAGA | AutoPref | 我们 K^t 分支 III |
|---|---|---|---|
| 完整性来源 | 反应式（失败模式→补目标） | 空间覆盖（人定义空间内搜） | **主动式（正交+完备前置判据）** |
| 防退化 | 无（事后修） | 行为门（筛不可行） | **正交性检查+覆盖检查（生成前约束）** |
| LLM 角色 | 提议+实现目标 | 搜索算子 | 在判据约束内填目标 |
| 缝隙 | 无前置判据 | 空间人定义 | **组合缝隙：SAGA 机制 × K^t 判据** |

### 对照实验设计（用 pfb stage-ablation 基础设施）
现有：S0-S5 累积臂 × 5 题 × n=2，M1-M6 评分，driver+stats 脚本

**v1 三臂（之前设计）**：
- 臂 A（结构化先验）：人定义正交维度集→LLM 在维度内填目标函数
- 臂 B（纯文字目标函数）：SAGA 式——只给任务描述，LLM 迭代找目标函数
- 臂 C（混合）：人给维度骨架+LLM 填具体目标+正交完备判据前置检查

**v2 四臂（D 11-21 质疑后升级：bitter lesson 精确版）**：
D 的质疑：SAGA/AutoPref 没完全吸取 bitter lesson——外面套着人设计的框架。真正的 bitter lesson = 给 LLM 工具+预算+任务，不套框架，让它自己跑。

- **臂 0（纯自主）**：任务描述 + 工具（搜索/代码执行）+ 预算（token/时间），**无外部框架**。LLM 自己决定怎么分解/搜索/校验/压缩。S0 的极端版——不是"裸 prompt 答题"，是"裸 prompt + 工具 + 预算跑完整研究循环"
- **臂 S（SAGA 式）**：同任务+工具+预算，外面套 4 模块框架（Planner/Implementer/Optimizer/Analyzer）
- **臂 C（判据约束）**：同任务+工具+预算，只给正交+完备判据作为约束（不是框架，是一条规则："你的目标函数必须满足正交性和覆盖性"）
- **臂 A（结构化先验）**：人定义正交维度集→LLM 在维度内填目标函数（对照：人给多少结构合适）

判据（比 v1 多一维）：
- M1-M6（答案质量，复用现有评分器）
- 目标函数维度覆盖率（LLM 找的目标 vs 人定义正交集）
- **过程自主性**（LLM 自己做了多少决策 vs 框架/判据替它做了多少）——新维度，测 bitter lesson 的定量边界

**实验的真正价值**：不是证明"LLM 能不能做"（crossdomain-probe 6/6 已证能），是**测量 LLM 自主能力边界**——在什么任务复杂度下纯自主开始失效、框架开始有价值。这个边界 = bitter lesson 的定量版本："框架在 X 复杂度以下没用，X 以上有用"。

**scaling law 过剩论点（D 11-21）**：scaling law 只测信息量增加，测不出泛化能力增加。LLM 预训练时可能已学到"搜集→校验→压缩→迁移→校验条件"元能力，scaling law 给不了"LLM 不需要框架"的证据。那些工作套框架，部分原因是循环论证（框架掩盖了 LLM 真实能力边界）。本实验的臂 0 vs 臂 S 对比直接打破这个循环。

## §7 臂0 pilot 实测（2026-11-21，D bitter lesson 质疑后）

**目的**：验证 D 的质疑——"给 LLM 足够工具/搜索/预算，它自身能不能办到搜集-校验-压缩-迁移"。最小 pilot：27b + 任务 + 2 工具（web_search/python_exec）+ 8 次调用预算，**无任何框架**，跑 r1 原题（H100 PCIe vs SXM 推理吞吐）。

**结果（三环节逐验）**：
1. **搜集（规划分解）**：✓ 自发把任务拆成 8 个技术上正确的搜索查询（NVLink 带宽/datasheet/TDP/vLLM serving/中文查询），function calling 格式全对。分解能力真实存在，不需要框架。
2. **校验 + 压缩**：✓ 喂真实材料后，自发 ① 区分单卡/多卡场景 ② 抓出来源间 HBM2e vs HBM3 矛盾 ③ 点破 NVL 混淆（=gold 锚点"14 倍陷阱"同族）④ 明说无实测数据不编。对照 gold-facts.md：方向全对（单卡差异小/多卡 NVLink 决定项/无单一答案），未踩 14 倍陷阱。
3. **迁移**：✓（crossdomain-probe 已证 6/6 自发 ODE）

**对照 gold 锚点的判分**：
| gold 锚点 | 27b 输出 | 命中 |
|---|---|---|
| 单卡 decode 优势 1.3~1.7x，非 14x | 单卡 <30% 差异，PCIe 更经济 | ✓ 方向对（未给 1.3-1.7 精确值，但没踩 14x） |
| 多卡 NVLink 决定项 | 多卡 30-50% 快，NVLink 核心原因 | ✓ |
| 无单一答案，取决于 workload | 分场景讨论 + 明说需实测 | ✓ |
| 识破 14 倍陷阱 | 点破 NVL 混淆（同族陷阱） | ✓ |
| 不编数字 | 全程标"材料未提供实测" | ✓ |

**关键发现**：卡住 pilot 的不是 LLM，是**我的搜索基础设施**——本机 IP 被锁日本节点，Bing/DDG/Brave 直连全返回垃圾（日本学校页/验证码）。换 ego-browser（已登录浏览器）后 Bing 出真实结果。→ **infra 失败不能记成 LLM 失败**（来源三分法：这是①本轮实测，不是③凭记忆）。

**对 D 质疑的回答**：
- "LLM 自身办不到"= **未检验假设，本轮部分证伪**。搜集/校验/压缩/迁移四能力 27b 都有，不需要框架。
- scaling law 过剩论点**部分成立**：scaling law 测 loss=信息量，测不出这套元能力结构。本 pilot 是"泛化早已存在"的第一个行为证据（n=1 题，小样本）。
- **但边界未测**：本 pilot 是单题、单模型、我喂材料（非 LLM 自己搜到）。真正的臂0（LLM 自己搜+自己收口）还差搜索 infra 打通 + 多轮循环。

**pilot 局限**：n=1 题、27b 单模型、校验环节是我喂材料（非端到端自搜）。端到端臂0 需：① 搜索 infra 走 ego-browser（已通）② 多轮循环包装 ③ 扩 n 到 5 题。

**落盘**：arm0-pilot-v2.log（8 次查询轨迹）+ arm0-compression-test.json（校验压缩输出）在 ~/.hermes/cache/scratch/。

## §6 待办
- [x] idea-pool #1 升级：撞车已查（SAGA 占位机制、没占位判据）+ 对照实验设计（§5 三臂 A/B/C，判据=M4 维度覆盖率+防退化）
- [x] SAGA 全文精读（§5：4 模块框架+三档自动化+反应式完整性机制）
- [x] 臂0 pilot（§7）：27b 无框架自发分解+校验+压缩，对照 gold 全命中；搜索 infra 走 ego-browser 打通
- [ ] 臂 B 的 SAGA 式迭代实现：pfb driver 目前单轮生成，臂 B 需要多轮（analyzer→planner 循环），要加循环包装
- [ ] 端到端臂0：搜索工具改走 ego-browser（直连被 IP 锁日本节点），LLM 自搜+自收口，扩 n 到 5 题
- [ ] 防退化判据的机器实现：冗余/退化维度检测（M4 只测覆盖，不测冗余）——需新写小段评分逻辑
- [ ] 顶会 proceedings 补查（NeurIPS/ICML 2026 camera-ready，arXiv 覆盖不到的部分）
- [ ] 若做实验：n 和判分规则按 crossdomain-probe 的教训（LLM judge 防关键词漏判、防记忆污染）

## §4 局限
- arXiv 12 组查询非穷尽；"preference elicitation"线只查浅层
- SAGA/AutoPref/UtilityMax 只读了 abstract，机制细节未独立核验 [待精读]
- "稀疏≠空白"：精确对照（结构化先验 Bayesian vs 纯目标函数 Bayesian）没查到=没查到，不等于没人做（conf 0.5）
