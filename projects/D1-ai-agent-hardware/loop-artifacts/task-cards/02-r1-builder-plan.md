# RALPH 子代理任务卡

- **Card ID**: `02-r1-builder-plan`
- **阶段**: `02-r1`
- **角色**: `plan-decomposer`
- **标题**: 任务 DAG 构造
- **任务目标**: 把已澄清需求分解为正交、可验证、可并行/合并的任务图切片。
- **原始任务**: 我需要跑本地 AI，帮我调研性价比最高的 GPU

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
9. 每个任务必须有输入 AND 输出、继续条件 AND 回退条件；任务 ID 唯一；DAG 无环。
10. 每个 MUST 类约束必须被至少一个任务覆盖。
11. 单个任务文档 + 执行上下文 ≤ 8K token（作为 subagent prompt 时）；过长需进一步拆分。
12. 并行节点必须显式标注 execution_mode 与 parallel_group_id，同一并行组具有不同正交维度键，且写入路径无冲突。
13. 跨层依赖必须声明 input_refs、output_schema 与依赖条件；Join 节点必须声明 join_policy。
14. 不得依赖隐藏 Chain of Thought 的字段。
15. 对每个节点执行“执行者模拟”：仅凭定义能否执行；gold case 不检查数量不检查质量、不漏环。
16. 计划 revision 不设次数上限，旧版本必须保留。

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
