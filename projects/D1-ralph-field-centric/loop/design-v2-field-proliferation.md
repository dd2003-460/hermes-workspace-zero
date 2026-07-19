# 设计 v2：逗号拆字段 + disposition 驱动增殖（字段中心最终形态）

> 取代 `DECOMPOSITION-REDESIGN.md` / v1 中"主 agent 递归建 matrix"的弱处。
> 核心改进：**字段增殖从"主 agent 递归"改为"程序机械拆 + disposition 驱动队列"**，主 agent 只做语义标注。

## 1. 目标维度分解（主 agent 负责）

- 主 agent 把"目标"按维度用**逗号分隔**写进 `attribute_matrix` 里 `concept=目标` 的那一条 `attribute` 字段。
- 例：`attribute = "性价比, 显存容量, 功耗, 价格, 本地推理适配性"`。
- 这一步是主 agent 唯一要做的"语义分解"，弱模型也稳（自然语言列维度）。

## 2. 程序自动逗号拆字段（运行时负责，确定性）

- 状态机在每次主 agent 提交/写入后，扫 `attribute_matrix` 中 `attribute` 含逗号的字段，
  拆成多条**同 concept、独立 attribute** 的子字段：`性价比` / `显存容量` / `功耗` / …。
- 纯字符串处理，可单测，不依赖模型。
- 落点：新增 `state._explode_comma_fields(matrix)`，在 `_apply_agent_result` 后调用。

## 3. 主 agent 标注 disposition（背景类型）

每个拆出的维度，主 agent 标三种之一：
- `confirmed`：明确已知背景。
- `assumed_default`：不确定偏好 → 默认全范围（无人类输入）。
- `research_required`：未知信息（最新显卡、价格行情…）需调研。

## 4. 程序把 research_required 维度自动作为"待调研字段队列"

- 当前阶段内，`research_required` 字段即"待派发调研 subagent 的队列"。
- 不需要跨节点传播：阶段内闭环即可。
- 落点：`protocol._collect_field_gate_issues` 已能列出 `research_required` 且缺 evidence 的字段 → 改为"调研队列"输出。

## 5. 主 agent 逐个派发调研 subagent（一次 2-3 个）

- 字段模式已去掉重卡片，主 agent 可自由派 Agent。
- 模板写明：一次派 2-3 个 `research_required` 字段的窄调研 subagent，每个只回该字段 JSON（`{concept,role,attribute,disposition,ratione,evidence_refs,confidence,...}`）。
- 回填后该字段 disposition 变 `confirmed`（带 evidence）。

## 6. 调研完成后 → 执行分解（同一字段机制贯通）

- 按是否有执行需求分叉：
  - **有代码/写作执行需求** → 把执行动作也建模为字段（`action` 字段），继续拆到可执行的章节/函数级。
  - **纯背景类（如写作）无未知字段** → 直接按风格约束、逻辑线路分解到章节/小节，不派调研。
- 粗→细、分支条件、执行分解全部落在同一套"逗号拆 + disposition 队列"机制上。

## 可行性结论

- 第 1/3/5/6 步：主 agent 语义能力，弱模型可完成（已用 live 弱模型验证"去限制后主动推进"）。
- 第 2/4 步：程序机械动作，确定性、可单测，**当前代码缺失，需新增**（约 30-50 行）。
- 整体：可作为最终设计落地；v1 仅缺第 2/4 步的"增殖"，v2 补齐。

## 7. 分解完全性判据 + 显式进阶命令（闭环最后一步）

- 门禁在每次主 agent 提交后检查两件事：
  1. **是否还有可继续拆的维度**：扫描 `attribute_matrix`，若某字段的 `attribute` 仍含逗号（未拆完）、或某 `research_required` 字段带回的 evidence 又引出新未知项（差集），则视为"还可分解"。
  2. **是否还有 pending / 未调研字段**：所有字段 disposition ∈ {confirmed, assumed_default} 且无逗号残留，才算"分解到最小单元"。
- 门禁只回传提醒（不致命）：
  - 仍可拆 → "维度 X 还可继续分解，你可继续填入子字段"。
  - 有 researching 缺口 → 列出待调研队列。
  - 全满 → 提示主 agent 运行 `ralph advance`（或输出 `<RALPH_STAGE_RESULT> advance`）进入下一阶段。
- 主 agent 不自行判断"够不够"，只负责"继续填/标注"；**是否 advance 由门禁的完全性判据 + 显式命令触发**，避免弱模型过早或过晚推进。
- 这把"分解完全性"从模糊的模型自觉变成**机械可验证的字段状态判据**。
