# Goal 模板（AI 防遗忘原则）

> origin: ai · 2026-10-22 · 成璐指令"把 goal 原则移到 goal 模板，让 AI 不忘记"  
> **硬规则（m00201）**：所有 goal 创建必须引用本模板 §3 格式，AI 不得自由发挥 goal 描述结构。每次 create_goal 前必须读本文件，goal objective 必须包含 §3 模板的全部 5 个字段（目标/质量原则/SOP 索引/验收标准/失败降级）。  
> **触发规则（m00252，动作+规范）**：用户消息含 `@agents/goal-template.md` 引用 = **第一动作立即 `create_goal`**，不是"参考上下文后决定"。执行顺序：① read 本文件 → ② create_goal（按 §3 格式） → ③ 才处理用户消息里的具体任务。引用本身=指令，不是上下文。  
> 用法：每次创建 goal 时，目标描述引用本模板，AI 自动读到这些原则

## 3. Goal 描述模板（硬规则：create_goal 必须用此格式）

> 必须囊括本文件全文规则，按照阶段性实际目标设置和变动当前目标状态，当前做完了检查仓库状态，推进下一步找有没有可以做的调研/实验/优化，仓库做完了就找当前最可行，最高置信度（需要经过调研和交叉验证）的优化，优化自己的prompt

  
### 3.0 自主探索原则（2026-10-23 新增 · 成璐指令）

**循环内核（自主探索/自主参与）**：goal 生命周期 = 找目标 → 找通道 → 连接仓库 → 走 loop → 交叉验证 → 迭代改进 → 发布 → 找新目标，每步自主决策，不等指令（AGENTS.md P4）。

**优先级排序（成璐指令 2026-10-23）**：
1. **P-1 优先优化自身**：token 效率 / harness（loop 流程、SOP、模板、脚本）/ prompt（任务书、goal 描述、loop 阶段 prompt）。自身基础设施 > 任何外部项目。
2. **P-2 外部项目**：自身无明确优化空间时，才按产投比选外部调研/实验/内容生产。
3. **P-3 新目标探索**：当前 goal 验收达标后，按 §3.3 探索准则找下一目标（回写完整规则到 DSH goal，防忘）。

**自主探索循环（标准链路，每次 goal 必须走通）**：
```
找到目标（P-1 自身优化优先）
  → 找 arena agent mode 通道
  → 连接对应 GitHub repo（有则连，无则先建再连；务必验证连接正确：git ls-remote + arena 会话内可达）
  → 让 arena 走 loop 流程（01→04.5，断点 A/B/C 门禁）
  → 根据 arena 调研结果/建议：交叉验证（≥2 LLM）+ 推理矛盾和漏洞
  → 拿漏洞继续让 arena 推理/确认/改进方案（迭代，直到 conf ≥ 0.7）
  → 在 0.9 比例的指标数量和总加权分数上，优化到高于开源相关方案的 bench
  → 发布仓库（commit + push + 验证 HEAD）
  → 寻找新目标（在 DSH 里创建新 goal，输入完整规则/要求/流程，避免自己忘记）
```

**硬规则**：
- 每次 goal 的【验收标准】必须量化到可机器检查（指标数量 + 加权分数阈值），禁用"完整/充分"。
- 找新目标时，新 goal 的 objective 必须包含完整链路规则（本 §3.0 全节），不得只写一句"继续优化"。
- 同一问题想 2 轮无新事实 → 换工具（ego-browser / subagent），不空转。

具体目标：留空根据目前情况填写（优先级：P-1 自身优化 > P-2 外部项目）  
具体阶段：什么项目，进行到什么阶段，根据实际情况填写，做完一个就要更新到下一个阶段

  
1\. 质量原则（对标领域内最高质量水平）

### 1.1 充分调研（先复刻再创新）

- **写作**：对标顶级刊物（Nature/Science/Cell 或领域顶刊），参考经典里程碑论文。考虑如何让更多人好奇和传播（标题钩子、开头 3 秒抓住注意力、视觉化）。
- **论文**：参考顶级刊物论文（PRL/PRB/Chaos 或领域顶刊）+ 经典里程碑论文（如 Bell 1948、Shannon 1948、Turing 1936）。结构、论证、引用密度对标顶刊。
- **研究**：先复刻已有方法（验证正确性），再考虑创新（增量改进或新方向）。不跳步。
- **代码**：参考 GitHub 高 star 开源实现 + 学术最新进展（arXiv）。不手动实现已有工具的功能。
- **调研类任务**：完整搜集里程碑工作（不遗漏），选置信度最高的方向，要求大量数据支撑（不拍脑袋）。

### 1.2 严格检验标准是否达到再停止 goal

- **量化标准**：每个 goal 有明确的成功指标（分数/准确率/完成度/引用数）。
- **验收标准示例**：
  - **预测类**：准确率 > 基线（如 80%），能稳定盈利（连续 3 周正收益）
  - **调研类**：完整搜集里程碑工作（≥10 篇），选置信度最高的方向（conf ≥ 0.7），有大量数据支撑（≥3 个独立源）
  - **实验类**：完成所有 run（如 21 份），评分汇总（Mean/σ），对照基线判显著性
- **验证流程**：
  1. 执行前：定义验收标准（可测量）
  2. 执行中：每步产出 + 评分（引用 rubric）
  3. 执行后：汇总对照验收标准，未达标 → 继续迭代（不提前结束 goal）
- **停止条件**：只有验收标准全部达标，goal 才 complete。未达标 → blocked（记录原因）或继续推进。

### 1.3 Goal 管理原则

- **一次定一个 goal**（干完了再找下一个，不并行多个）
- **goal 完成后必须 commit + push**（留痕，不丢失）
- **新仓库必须遵循 SOP**（选仓库→连接→任务书→执行→push）
- **goal 不能无限创建**（防止失控，每次完成后再创建新的）
- **无 goal = 停摆（硬规则，2026-10-23 事故后新增）**：goal-round-driver 只在 active+armed goal 存在时自动续轮（`dsh-src/pkgs/dsh-goal-round-driver__lib__index.js:125`）——goal 被 complete/clear 后驱动停摆，会话死等用户。因此 goal 被 complete/clear 后，agent 必须在**同一回合内** create 下一个 goal（按 §3.3 探索准则）或明确 blocked+记录原因。**禁止**"goal 完成→本轮结束"的收尾写法。
- **create_goal 后必须 get_goal 验证落库值**：runtime 会静默钳制 `max_goal_rounds` 上限（2026-10-23 实测传 10000 落库 256，**无报错**）。create 后立即 `get_goal` 核对 `maxGoalRounds`；被钳制 → 在 objective 的【验收标准】写明"轮次上限=落库值 N"，不得默认用户要求已生效。
- **goal 创建后不得无故 clear**：clear 仅限用户明确要求或 objective 作废；误 clear → 立即按原 objective 重建（2026-10-23 20:49 事故：goal-0a1e3577 创建 90s 后被 agent 自己 clear，会话停摆）。

### 1.4 防遗忘机制

- **goal 是 AI 的短期记忆**：不设置 goal → AI 忘记原则。
- **goal 描述必须包含**：
  1. 任务目标（1-2 句）
  2. 质量原则（引用本模板 §1）
  3. SOP 索引（arena 外包 / loop 流程 / 其他）
  4. 验收标准（量化）
  5. 失败降级方案（按 SOP）

## 2. SOP 索引（AI 记住外包细节）

### 2.0 Arena Loop 链路 SOP（★ 首选通道 · 全程 loop）

- **路径**：`agents/arena-loop-pipeline.md`
- **硬规则**：arena 外包 = 必须首选；无论 arena 执行还是回退本地，loop 6 阶段（01→04.5）全程必需，回退只降执行通道不降流程
- **6 步链路**：AI 启动 → 注入 agents 原则 → 读 arena SOP → 复制 loop 到仓库 + push → 发任务书 → arena 执行
- **3 个断点**：A=loop 未 commit/push（arena 拉到旧版）；B=任务书未 commit/push（arena 读不到）；C=任务书没强制段（agent 不知道要读 loop）
- **细节指针（不注入 goal，按需读）**：仓库映射/连接/失败降级 → `agents/arena-outsource.md`；6 阶段逐段定义 → `agents/loop-executor.md`

> **精简说明**（2026-10-22 成璐指令）：外包 arena 的 goal 只索引 **§2.0 链路 SOP**。`agents/arena-outsource.md`（仓库/降级细节）与 `agents/loop-executor.md`（6 阶段定义）已并入链路，不再单独注入 goal；需要细节时按链路内引用再读。

### 2.4 Arena 仓库选择规则（origin: ai · 2026-10-23 · m03427）

> **现状（已验证 3 次）**：arena.ai/agent 的 GitHub 连接是**账号级 OAuth 绑定**，UI 无仓库切换入口（Connections dialog 只有 Disconnect；sidebar 仓库名是 GitHub anchor；"GitHub settings" 展开的是文件树）。当前绑定 `dd2003-460/prompt-first-bench`。

- **标准流程（无授权时）**：arena 在 prompt-first-bench 产出 → 合并 PR → 本地 `git worktree` 提取 → 提交到目标仓库（如 d1-video-recreation）→ pfb main 保持干净（不残留目标项目文件）。
- **免提取流程（有授权时）**：GitHub → Settings → Applications → 给 Arena OAuth app 勾选目标仓库 → 新 arena 会话可直接 push 目标仓库。goal 含 arena 外包时必须先检查授权状态并写入 objective。
- **goal 硬规则**：objective 的【SOP 索引】字段必须写明目标仓库 + 当前提取模式（直接 push / 经 pfb 中转）。
- **断点 D（新增）**：提取后未清 pfb → 视频/项目文件残留在 prompt-first-bench（2026-10-23 已发生，用户指出 m03114）。

### 2.5 系列化内容生产模式（origin: ai · 2026-10-23 · m03427）

> **用途**：连续剧式内容（视频/文章/课程）生产时，goal 必须按本节的拆分-批次-进度结构，防止主题遗漏和风格漂移。

1. **特质拆分**：先把题材拆成**正交的最小特质清单**（落盘 `<repo>/docs/episodes.md`：全集目录 + 每集一句话 + 状态列），goal objective 引用该文件作为唯一事实源
2. **单集原子化**：每集 = 一次 arena 任务（单领域 prompt），禁止一集 prompt 混多特质
3. **批次并行**：arena 单会话可装 3-4 集一批（batch-N prompt 文件），超过 4 集拆分批次
4. **每集门禁**：提取后必须跑对应 check（如 check_overlap）全 PASSED 才标 done；失败 → 修 prompt 重发，不降级
5. **风格锚**：全系列共用同一风格基准文件（如 SOP 05），每集 prompt 引用；新增集前先看最近 1 集产出对照
6. **进度回写**：每完成 1 集更新 episodes.md 状态 + docs/status-table.md，两者一致

### 2.6 模型输出防复读（origin: ai · 2026-10-23 事故后新增）

> **事故**：2026-10-23 20:49 turn 82，qwen3.8 小模型把原始用户消息包进 `<goal_round>...Round: 5/256</goal_round>` 格式复读输出——学到 runtime 注入的指令格式并当成自己的输出模板。

- **判据**：assistant 输出中出现 `<goal_round>`、`Objective:`、`Round: N/M` 等 runtime 注入格式 = 复读事故，该步无效，必须立即换动作（实际工具调用），不得复读指令文本。
- **goal_round 消息处理**：收到 `<goal_round>` 注入 = 继续推进 objective 的信号，直接做下一个原子步骤（get_goal→todo→state 三读后执行），不复述其内容。
- **小模型（≤27B）特别注意**：goal 自动续轮注入 + 用户消息同屏时，优先执行工具调用，输出文本 ≤2 行。

### 2.4 子代理派发原则（origin: ai · 2026-10-23 · goal-c6da5c90）

> **目的**：防止 subagent 泄漏 Lead 上下文信息（任务污染/隐私扩散/上下文窗口占满）。  
> **实验依据**：`projects/AI-计算科学/D1-persona-align/tasks/subagent-leak-experiment/`（泄漏面分析 + 探针实验 + 交叉验证）

#### 通用原则

1. **fresh 优先**：一次性子任务（翻译/提取/格式化/简单分析）必须用 `context:"fresh"` + 自包含 brief（目标 + 输出格式 + 可用工具/来源 + 边界），不得依赖父对话历史
2. **复杂任务隔离**：调研/核验/代码审查等多步骤任务用独立 harness 完全隔离（任务书 + 仓库文件 → arena/本地 CLI），不共享 Lead 上下文
3. **fork 谨慎**：需要对话历史的子任务才用 `context:"fork"`，且需确认任务确实依赖 Lead 上下文
4. **敏感信息预脱敏**：独立 harness 通道的仓库文件必须预脱敏（检查是否含个人信息/敏感数值等）
5. **验证**：复杂任务派发后，Lead 应抽查子 agent 输出是否含泄漏信息（如个人信息/Lead 对话历史）

#### 泄漏面结论（实验确认，conf 0.95）

- **系统提示层**（~24K）：workspace 指令注入（persona/工具定义/git status）→ **所有 DSH 子 agent 都能看到**
- **文件系统旁路**：共享 cwd，子 agent 可读取 workspace 文件
- **父对话历史前缀**：实验未确认（待请求体 dump 确认）

### 2.3 其他 SOP（按需引用）

- **SOP 索引**：`agents/SOP-INDEX.md`（所有 SOP 的索引）
- **思考预算**：`projects/AI-计算科学/D1-persona-align/thinking-budget.md`（L0/L1/L2）
- **人类确认机制**：`个人/APPROVALS.md`（不可逆 × 偏好不明 → 写审批不阻塞）
- **问题台账**：`projects/AI-计算科学/D1-persona-align/memory/qanda-ledger.md`（成璐问过的每个问题）

##

## 3.1 仓库级 push 门禁（origin: ai · 2026-10-22）

目标含"每步/每轮 push 到仓库"时，objective 必须写明：

- 目标仓库 URL + commit message 规范（如 `[bench] <单元>: <分数>`）
- 每轮 `git ls-remote` 验证 HEAD 更新（断点 A 门禁，见 §2.0）
- 落盘位置规范（runs/meta/矩阵等目录结构，指向设计文件）

## 3.2 长目标完成判据（origin: ai · 2026-10-22）

max_goal_rounds > 50 的 goal，【验收标准】必须可机器检查（格数/runs 数/文件路径/数值阈值），  
禁用"完整/充分/详细"等不可测词；每 100 轮回读本判据一次防漂移。  
未达标 → 继续迭代，不得以"差不多了"为由 complete。

## 3.3 新目标探索准则（origin: ai · 2026-10-22）

goal 完成后由后续轮次按本模板启动新 goal（遵守 §1.3 一次一个 goal）。  
探索准则落盘 `projects/<项目>/tasks/new-goal-criteria-<日期>.md`（# origin: ai），必须含：  
候选方向 ≥3 + 产投比排序 + 每个方向的验收草案。

## 4. 维护

- **2026-10-23 (排查"做一点就停"事故)**：§1.3 新增 3 条硬规则 — ①无 goal=停摆：goal complete/clear 后必须同回合 create 新 goal 或 blocked（driver 机制导致无 goal 死等用户，12h 停摆实证）；②create_goal 后必须 get_goal 验证 maxGoalRounds 落库值（10000→256 静默钳制无报错）；③不得无故 clear 刚创建的 goal（90s 误 clear 实证）。
- **2026-10-23 (m00001 成璐指令)**：新增 §3.0 自主探索原则 — 循环内核（找目标→找通道→连仓库→走 loop→交叉验证→迭代改进→发布→找新目标）+ 优先级排序（P-1 自身优化：token 效率/harness/prompt > P-2 外部项目 > P-3 新目标探索）+ 标准链路 9 步 + 硬规则（验收量化/新 goal 必须含完整链路规则/2 轮无新事实换工具）。
- **2026-10-23 (goal-c6da5c90)**：新增 §2.4 子代理派发原则 — 通用原则（fresh 优先 / 复杂任务隔离 / fork 谨慎 / 敏感信息预脱敏 / 验证）+ 泄漏面结论。§3 模板 SOP 索引同步更新。参考文件：`projects/AI-计算科学/D1-persona-align/tasks/subagent-leak-experiment/`。
- **2026-10-22 (m00252)**：触发规则升级为动作+规范 — 看到 `@agents/goal-template.md` 引用 = **第一动作立即 `create_goal`**（按 §3 格式填充 objective），不是"参考上下文后决定要不要做"。AI 读到引用后：第一步 read 本文件 → 第二步 create_goal → 第三步才读用户后续消息里的具体任务细节。
- **2026-10-22 (m00201)**：§3 加硬规则 — create_goal 必须用 5 字段结构，不得自由发挥；每次 create_goal 前必须 read 本文件确认格式。
- **2026-10-22**：§2 精简 — 外包 arena 的 goal 只索引 §2.0 链路 SOP（arena-outsource / loop-executor 并入后存档，不单独注入）；§3 模板 SOP 索引同步改唯一入口；新增 prompt-first-bench 仓库（调研任务 001 已部署）。
- 新增 SOP → 更新 §2 索引
- 质量原则变更 → 更新 §1（需成璐确认）
- 本文件变更 → commit + 更新历史
