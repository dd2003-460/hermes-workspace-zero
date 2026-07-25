# RALPH 子代理任务卡

- **Card ID**: `02-r1-builder-plan`
- **阶段**: `02-r1`
- **角色**: `plan-decomposer`
- **标题**: 任务 DAG 构造
- **任务目标**: 把已澄清需求分解为正交、可验证、可并行/合并的任务图切片。
- **原始任务**: 我需要跑本地 AI，帮我调研性价比最高的 GPU（2026 年最新）。要求：1) 深度——分析必须深入到硬件底层约束（显存带宽与容量、互联拓扑、统一内存、功耗墙、量化与推理框架兼容性、本地 35B 级模型真实吞吐与延迟），而非罗列型号参数；2) 时效性——所有价格、型号、规格、基准必须用网页搜索获取当前 2026 数据，严禁依赖陈旧记忆；3) 验证——关键事实必须带来源 URL、发布日期、适用条件与核验状态，并由网页 LLM 交叉验证，无法核验的明确标 uncertain。最终按性价比排序交付可验证推荐及适用边界。

## 必读文件

- `loop-artifacts/contracts/02-r1-stage-contract.md`
- `loop-artifacts/contracts/02-r1-submission-template.json`
- `loop-artifacts/stages/02/r1/plan.json`

## 执行边界

1. 每个节点必须有 title、objective、evidence_plan、acceptance_criteria、输入输出、依赖与写入路径。
2. 并行节点显式标注 execution_mode 与 parallel_group_id；Join 节点声明 join_policy。
3. 每个 MUST 类约束必须被至少一个节点覆盖；DAG 无环。
4. 用 **Write** 工具把完整填充后的切片写入 `loop-artifacts/stages/02/r1/plan.json`（该文件顶层对象即 `payload.plan` 完整内容；运行时已预生成骨架，直接整体覆盖为填充版）。
5. 禁止再派发任何子代理（不得调用 Agent）；你必须自己用 Write 完成切片写入，嵌套子代理只会额外增加断流风险。
6. 不要写入 loop-state.json 或其他受控文件；不要替 Commander 做独立门禁审计（那是 gate 子代理的职责）。
7. 完成后只把结构化结论简短返回给 Commander，并确认切片文件已写好。
8. 参考阶段方法论（源自 loop/1-loop，补充要求，不覆盖上方门禁/边界规则）：
9. 本阶段 = 调研分解结果：对 01 的每个 research_required 字段派窄调研 subagent，带回 evidence_refs。
10. 调研完成字段处置变为 confirmed / assumed_default；引出新未知项作为 pending 字段增殖，直到无 pending。
11. 同时为每个分解项整理「后续执行需要什么」雏形，供 03 细化。
12. 每个任务必须有输入 AND 输出、继续条件 AND 回退条件；任务 ID 唯一；DAG 无环。
13. 每个 MUST 类约束必须被至少一个任务覆盖。
14. 单个任务文档 + 执行上下文 ≤ 8K token（作为 subagent prompt 时）；过长需进一步拆分。
15. 并行节点必须显式标注 execution_mode 与 parallel_group_id，同一并行组具有不同正交维度键，且写入路径无冲突。
16. 跨层依赖必须声明 input_refs、output_schema 与依赖条件；Join 节点必须声明 join_policy。
17. 本阶段只做调研与分解确认，不做交叉验证（交叉验证在 02.5）。

**切片填写方式（关键）**：`loop-artifacts/stages/02/r1/plan.json` 已由运行时预生成为骨架（结构完整、含占位/示例值）。
你**必须用 Write 工具把整个填充后的切片写入 `loop-artifacts/stages/02/r1/plan.json`**（直接整体覆盖骨架），不要只返回 JSON 文本。
**严禁把 JSON 作为纯文本返回**：只有写入了 `{slice_ref}` 文件才算完成；只回自然语言会被判定为未提交并退回重做。
**增量填写**：`semantic_map` 中仍为空数组的语义角色才需要补充；已填角色不要重写，只针对空角色补真实条目，并补上对应 `attribute_matrix` 叶节点（concept/role/attribute/disposition/rationale，disposition∈{confirmed,inferred,assume,research}）。七类角色（background/decision_object/objective/comparison_set/constraints/deliverable/uncertainty）都非空后才算完成。
若 Commander 派发时附带门禁回执（`<RALPH_GATE_REVIEW>`），只修正回执中 `status:"fail"` 的 check 对应的字段，其余保持不变。

## 允许工具

`Read`, `Glob`, `Grep`, `Write`

## 输出接口

```json
{
  "coverage_proof": [],
  "decomposition_rationale": [],
  "joins": [],
  "nodes": [],
  "parallel_groups": [],
  "revision": "r1",
  "risk_notes": []
}
```

## 返回给 Commander 的格式

- 已确认事实 / 来源 / 适用条件
- 不确定或冲突项
- 对应任务卡的结构化结论
- 不要修改 `loop-state.json`，不要替 Commander 决定后续阶段。
