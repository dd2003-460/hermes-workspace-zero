# plan.md — RALPH 字段中心化重构（field-centric redesign）

> 项目：D1-ralph-field-centric
> 来源：用户 2026-07-18 请求 + 既有 `loop/ralph_runtime/DECOMPOSITION-REDESIGN.md`（v1）
> 当前目标设计：**v2 逗号拆字段 + disposition 驱动增殖**（见 `loop/design-v2-field-proliferation.md`）

## 0. 已用 live 证据验证的结论（2026-07-18）

在 `D1-ralph-smoke-matrix`（弱模型 Qwen3.6-35B）上对照实验：

- **enforce + 卡片强制**：卡死。全程 `advance`=0，stage 02 出现=0；主 agent 提交"builder 运行中"被 `stage_result_rejected` 后不能自愈，静默空转 Read/Bash。根因=刚性全有全无结果 + 强制卡片 + 一次格式错致命。
- **shadow + 字段中心模板 + field-gate（去卡片）**：弱模型从死循环变为**主动推进**（自己读契约、派 Agent、等 subagent 回执、事件稳定增长）。证明"去掉限制→不再卡死"成立。
- **字段中心模板对陌生 agent 可操作**：已用模板全文核对确认（任务定义清晰、决策有默认值、提交是填空）。
- **仍待验证**：弱模型在字段模式下走重 builder 卡片（v1 未禁卡片）慢且没收敛 → 已改为 v2 禁卡片 + 逗号增殖。

## 1. 已落地的代码改动（可逆、env 守护、默认不变）

- `prompt_renderer.py`：`RALPH_PROMPT_TEMPLATE` 选择器（默认旧模板）；字段中心恢复提示 `_field_recovery_prompt`；render 补 `stage_input_package_ref`。
- `protocol.py`：`RALPH_FIELD_GATE` 字段门禁（只校验 required 字段 disposition + 只回传空缺字段，不要求 stage_review/task_spec 全段）；`import os`。
- `contracts.py`：field-gate 下 `ensure_stage_cards` 不生成卡片、`materialize_contract_documents` 不写卡片文件。
- `state.py`：field-gate 下 `_initial_task_spec` 给 `attribute_matrix` 种入一条 `confirmed` 背景字段（"已知背景=已有条件"起点）。
- 测试：108 passed / 3 failed，与改动前基线一致（3 个失败是 enforce/Commander-edit 相关既有失败，非本次引入）。

## 2. v2 待实现（核心缺口：字段增殖）

- [ ] `state._explode_comma_fields(matrix)`：每次 apply 后把 `attribute` 含逗号的字段拆成独立子字段（确定性、可单测）。
- [ ] 调研队列抽取：`research_required` 字段即"待派发调研 subagent 队列"，门禁输出该队列而非整段错误。
- [ ] 模板第5步写明"一次派 2-3 个 research_required 窄调研 subagent，每个只回该字段 JSON"。
- [ ] 执行分解：把执行动作建模为 `action` 字段，写作类无未知字段直接按约束拆章节。

## 3. 执行阶段（建议顺序）

- Phase 1（已做）：去 enforce + 去卡片强制 + shadow 验证不死循环。
- Phase 2（做中）：v2 逗号增殖 + 调研队列 + 模板细化。
- Phase 3：在弱模型上重跑，验证能否 `advance` 过 01 并真正完成标准分解。
- Phase 4：泛化到执行分解（代码/写作），确认粗→细/分支条件同一机制贯通。
- Phase 5：用 `decomposition_benchmark.py` 对比质量/卡死率 vs 旧刚性编排。

## 4. 停止规则（防字段膨胀/无限拆）

- 字段一旦"可确认/可推断/可研究"即停止继续拆分（禁无穷拆词）。
- `assumed_default` 须在交付摘要显式标注"默认假设，非用户指定"。
- 主 agent 填字段需字段级去重，避免反复改写同一字段。

## 2.1 v2 代码落点（已验证，env 守护可逆，2026-07-18）

- `state._explode_comma_fields` + `state.field_completeness`：确定性增殖 + 完全性判据（已单测验证）。
- `state.apply_action`：stage01 advance 时自动 explode 逗号维度。
- `protocol._collect_field_gate_issues`：用 `field_completeness` 输出缺口（splittable/researching/pending）+ 进阶提示，不要求 stage_review。
- `protocol.collect_validation_issues`：field-gate 早退，优先读 payload 的 task_spec。
- 测试：108 passed / 3 failed（与改动前基线一致，3 个为 enforce/Commander-edit 既有失败）。
- 待 live 验证：弱模型在 v2 下能否真正 `advance` 过 01。
