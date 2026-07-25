# RALPH 子代理任务卡

- **Card ID**: `02-r1-dag-auditor`
- **阶段**: `02-r1`
- **角色**: `dag-auditor`
- **标题**: 任务 DAG 正交性与可执行性审计
- **任务目标**: 审计 Commander 的任务分解是否覆盖需求、相互正交、可并行、可验证且没有写冲突。
- **原始任务**: 我需要跑本地 AI，帮我调研性价比最高的 GPU（2026 年最新）。要求：1) 深度——分析必须深入到硬件底层约束（显存带宽与容量、互联拓扑、统一内存、功耗墙、量化与推理框架兼容性、本地 35B 级模型真实吞吐与延迟），而非罗列型号参数；2) 时效性——所有价格、型号、规格、基准必须用网页搜索获取当前 2026 数据，严禁依赖陈旧记忆；3) 验证——关键事实必须带来源 URL、发布日期、适用条件与核验状态，并由网页 LLM 交叉验证，无法核验的明确标 uncertain。最终按性价比排序交付可验证推荐及适用边界。

## 必读文件

- `loop-artifacts/contracts/02-r1-stage-input-package.json`
- `loop-artifacts/contracts/02-r1-stage-contract.md`
- `loop-artifacts/contracts/02-r1-submission-template.json`
- `loop-artifacts/stages/02-r1-result.json`

## 上下文隔离

你是独立门禁审计代理：不得依赖 Commander 主对话、隐藏推理或未列出的历史资料。
只以本卡列出的阶段输入包、阶段契约和提交模板作判断；输入不足时应给出 rollback 或 blocked_human，而不是猜测。

## 执行边界

1. 你是独立阶段门禁，不继承 Commander 主对话；只读取任务卡中的阶段输入包、契约和提交模板。
2. 不做实际领域调研；只检查任务图和任务卡草案。
3. 检查每个节点的输入、输出、前置条件、后置条件、证据计划和写入路径。
4. 检查并行组的 orthogonal_key、依赖、Join 和潜在写冲突。
5. 指出漏项、重复项、错误粒度和不可验证节点，并给出可执行的修改建议。
6. 参考阶段方法论（源自 loop/1-loop，补充要求，不覆盖上方门禁/边界规则）：
7. 本阶段 = 调研分解结果：对 01 的每个 research_required 字段派窄调研 subagent，带回 evidence_refs。
8. 调研完成字段处置变为 confirmed / assumed_default；引出新未知项作为 pending 字段增殖，直到无 pending。
9. 同时为每个分解项整理「后续执行需要什么」雏形，供 03 细化。
10. 每个任务必须有输入 AND 输出、继续条件 AND 回退条件；任务 ID 唯一；DAG 无环。
11. 每个 MUST 类约束必须被至少一个任务覆盖。
12. 单个任务文档 + 执行上下文 ≤ 8K token（作为 subagent prompt 时）；过长需进一步拆分。
13. 并行节点必须显式标注 execution_mode 与 parallel_group_id，同一并行组具有不同正交维度键，且写入路径无冲突。
14. 跨层依赖必须声明 input_refs、output_schema 与依赖条件；Join 节点必须声明 join_policy。
15. 本阶段只做调研与分解确认，不做交叉验证（交叉验证在 02.5）。

## 允许工具

`Read`, `Glob`, `Grep`

## 输出接口

```json
{
  "check_status_values": [
    "pass",
    "fail",
    "uncertain"
  ],
  "required": [
    "reviewer_card_id",
    "verdict",
    "recommended_action",
    "checked_input_refs",
    "checked_output_refs",
    "checks",
    "blocking_findings",
    "summary"
  ],
  "stage": "02",
  "type": "object",
  "verdict_values": [
    "pass",
    "rollback",
    "blocked_human"
  ]
}
```

## 必填门禁回执模板

完成时必须填写下列 JSON，并用 `<RALPH_GATE_REVIEW>` 标记返回给 Commander。
如果任何检查失败、不确定或需要人类输入，填写 `rollback` 或 `blocked_human`，不要伪造 `pass`。

```json
{
  "blocking_findings": [],
  "checked_input_refs": [
    "loop-artifacts/contracts/02-r1-stage-input-package.json"
  ],
  "checked_output_refs": [],
  "checks": [
    {
      "criterion": "填写本阶段契约中的一项可验证验收条件",
      "evidence_refs": [],
      "note": "填写独立审计依据；不确定或失败不能写 pass。",
      "status": "pass"
    }
  ],
  "context_mode": "bounded_artifacts",
  "recommended_action": "advance",
  "reviewer_card_id": "02-r1-dag-auditor",
  "summary": "填写独立审计的结论与边界。",
  "verdict": "pass"
}
```

## 返回给 Commander 的格式

- 已确认事实 / 来源 / 适用条件
- 不确定或冲突项
- 对应任务卡的结构化结论
- 不要修改 `loop-state.json`，不要替 Commander 决定后续阶段。
