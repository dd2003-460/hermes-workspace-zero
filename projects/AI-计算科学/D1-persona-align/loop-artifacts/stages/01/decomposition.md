# 阶段 01：目标分解、已知与空缺条件

- 任务书：`projects/AI-计算科学/D1-persona-align/tasks/understanding-d/T6-revival-frontier-research.md`（指纹复算 sha256(去 `[指纹]` 行) = d0fdaf81b4cf24d4...，与任务书一致）
- 基线 commit：c9afd64a（分支 arena/423a71ef-hermes-workspace-zero）
- 执行通道：本会话直接执行（Arena Agent Mode 内本地执行）。未派发到独立 arena 子会话。

## 1. 交付目标

产出 `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/revival-frontier-research.md`，按任务书 [交付] 格式给出三方向 SOTA：
- Q1 记忆 / 人格持久化：长期 persona 如何不衰减、不漂移
- Q2 思维操作的可执行编码：质疑-猜想-验证环、正交分解、置信度标注 → 可执行检查 / 注入 / judge
- Q3 外部锚点网络：多模型共识、回归测试集、可执行真值作为外部校验源的长期维护

每方向：方法 + 链接 + 一句话原理 + 对我们适配度（高/中/低+理由）+ conf(0-1)。
横向：≤10 行的最小系统形态。

## 2. 目标的主要影响因素（正交分解）

| 因素 | 含义 | 覆盖 |
|------|------|------|
| F1 Q1 记忆/人格持久化机制 | 外部记忆存储、时间知识图谱、consolidation、persona 漂移度量 | Q1 |
| F2 Q2 思维操作可执行化 | 把"思考习惯"转成检查、注入、judge 的方法族（CoVe / self-consistency / PRM / Constitutional AI / reflection） | Q2 |
| F3 Q3 外部锚点与校验源 | 多模型辩论、LLM-as-judge 校准、eval 回归集维护 | Q3 |
| F4 我方约束 | 本地 27b vLLM、不改权重、Hermes agent hooks（prompt 注入层）、git 版本化记忆 | 适配度判断的输入 |
| F5 交付与证据标准 | 中文、conf 0-1、URL、≥3 独立来源/方向、矛盾显式记录、2024-2026 活跃度 | 质量门 |

正交性检查：F1–F3 按"记忆 / 思维编码 / 外部校验"三个不同机制切分，互不包含；F4 是约束而非方向；F5 是交付规则。

## 3. 三类条件

### 3.1 人类已提供的条件（已确定）
- C1 三方向 Q1/Q2/Q3 已定义，候选线索已给出（见任务书）。
- C2 基础设施：本地 27b vLLM（不改权重）、Hermes agent hooks、git 版本化记忆。
- C3 交付格式、路径、回执要求（repo URL + branch + commit_sha、指纹、三方向结论条数与来源数）。
- C4 只调研 2024–2026 活跃方案；活跃度以 star 数 / 近期 commit 为证据。
- C5 每方向 ≥3 个独立来源交叉；矛盾显式记录；不确定标"未验证"。

### 3.2 可从项目推导的条件（已确定）
- D1 因为本地 27b 不改权重，方法必须是"推理期"可落地（prompt 注入、检查器、judge、检索），不能依赖微调 / RLHF 训练。
- D2 Hermes hooks 是注入层，因此 Q2 的"注入"与 Q1 的"加载 persona map"可直接对接；Q3 的 judge 需要与生成模型异族才有独立性（来自 SOP judge 选择条款的通用原则，作为设计假设，待在 02 阶段核验）。
- D3 "像 D 一样思考"的评价需要外部可执行锚点，否则只能自评（推导，非事实）。

### 3.3 空缺清单（仍需研究，未验证）
- G1 [待研究] Q1：mem0、Letta(MemGPT)、Zep/Graphiti、LangMem 的架构、persona/记忆 consolidation 机制、开源活跃度与论文出处。
- G2 [待研究] Q1：长期 persona 漂移的实证（是否有 drift 度量与缓解结果）。
- G3 [待研究] Q2：Chain-of-Verification、self-consistency、PRM（如 Math-Shepherd / PRM800K 系）、Constitutional AI、Reflexion 的可执行性证据与适用边界。
- G4 [待研究] Q2："思维习惯"类规则（置信度标注、正交分解）能否被可执行化的已有工作。
- G5 [待研究] Q3：multi-model debate 的独立性与收益证据；LLM-as-judge 偏差与校准方法；eval 回归集维护实践（如 promptfoo / OpenAI evals / lm-eval-harness 等）。
- G6 [待研究] 本地 27b 规模下上述方法的可行性（计算成本、是否需要更大模型做 judge）。
- G7 [缺口-文件] 任务书引用的 `thinking-patterns-v1.md`（11 条思考习惯）与 `idea-inventory-v1.md`（61 条 idea）在同目录 `tasks/understanding-d/` **不存在**（仓库内仅有任务书本身）。Q2 的"把 11 条习惯编码"无法基于原始清单执行；本轮只以任务书中点名的三类习惯（质疑-猜想-验证环、正交分解、置信度标注）作为代表性输入，缺口原样保留，不编造清单内容。
- G8 [待确认] 网页 LLM 交叉询问（ego-browser + ego-verify skill）在本会话不可用（无 ego-browser 工具）。阶段 02 按 02 文件规定记录失败原因后，改用公开网页搜索 + 原文抓取完成核验。

## 4. 阶段 02 研究入口（第一批行动）

| 方向 | 研究路径 | 来源优先级 | 备用来源 |
|------|---------|-----------|---------|
| Q1 | 搜 mem0 / Letta / Zep Graphiti / LangMem 论文与官方文档；核对 GitHub star 与最近 commit | arXiv 论文、官方 docs、GitHub | 技术博客（仅作线索，标 conf 低） |
| Q2 | 搜 CoVe、self-consistency、PRM、Constitutional AI、Reflexion 原论文；核对可执行性证据 | arXiv / ACL / ICLR 原文 | 官方 blog |
| Q3 | 搜 multi-model debate 原文、LLM-as-judge 偏差论文、promptfoo / lm-eval 文档 | arXiv、GitHub、官方 docs | 厂商 eval 文档 |

失败备用路径：WebSearch 0 结果 → 换一次关键词；WebFetch 单 URL 失败 → 记录，最多 4 个具体 URL 各一次（02 规则）。

## 5. 阶段边界声明

- 本阶段只做分解，不包含任何事实核验结果；上述方法名称、机制描述均为待验证研究目标，不作为已知事实。
- 候选集冻结：本阶段列出的候选方法为冻结集合。阶段 02 新增候选须在 02 工件中显式记录"新增 + 理由"，排除须写"排除 — 理由"。

## 6. 本阶段必须回答

- 交付什么：三方向 SOTA 表 + 横向最小系统形态。✔
- 影响因素：F1–F5。✔
- 已确定条件：C1–C5、D1–D3。✔
- 缺失条件：G1–G8。✔
- 阻塞哪个判断：G1–G5 阻塞三方向结论；G7 阻塞"基于 11 条习惯的编码"的原始输入，只能降级为代表性输入；G8 阻塞"网页 LLM 线索"这一类证据。
- 阶段 02 优先研究：G1、G3、G5（三方向的主证据）。
