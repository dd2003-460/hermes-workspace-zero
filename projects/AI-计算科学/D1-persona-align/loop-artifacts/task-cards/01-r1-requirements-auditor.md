# RALPH 子代理任务卡

- **Card ID**: `01-r1-requirements-auditor`
- **阶段**: `01-r1`
- **角色**: `requirements-auditor`
- **标题**: 需求、遗漏和假设审计
- **任务目标**: 独立检查 Commander 对用户意图的语义分解，找出会改变决策的遗漏属性与隐含假设。
- **原始任务**: RALPH 流程试运行：在现有用户人格提取项目中，从当前阶段开始，先读取 loop-state.json、raw/raw.md、项目 INDEX 与当前阶段契约。目标是以原始人类材料为锚点，重新审计并完善用户人格/偏好/思维模式提取与可验证评估；明确区分 human 原始意图、证据和 AI 推断，不能捏造传记事实或把 AI 假设写成人类偏好。先主动发现缺失维度、冲突、适用边界和隐私风险，再做可验证分解。后续允许阶段使用网页检索和可用网页 LLM 做独立评审，但不得上传原始私人对话、敏感人格材料或完整未公开文档；只传经脱敏的最小摘要。把外部反馈写成证据或不确定项，按反馈修改项目产物并回归测试。严格只做当前阶段、派发批准任务卡、不要跳步。

## 必读文件

- `loop-artifacts/contracts/01-r1-stage-input-package.json`
- `loop-artifacts/contracts/01-r1-stage-contract.md`
- `loop-artifacts/contracts/01-r1-submission-template.json`

## 上下文隔离

你是独立门禁审计代理：不得依赖 Commander 主对话、隐藏推理或未列出的历史资料。
只以本卡列出的阶段输入包、阶段契约和提交模板作判断；输入不足时应给出 rollback 或 blocked_human，而不是猜测。

## 执行边界

1. 你是独立阶段门禁，不继承 Commander 主对话；只读取任务卡中的阶段输入包、契约和提交模板。
2. 只分析已给输入与项目内已有资料；不得开始外部调研或给出最终推荐。
3. 按背景、决策对象、目标、比较集合、约束、交付物、不确定性逐项审计。
4. 每个叶节点必须标记为：已确认、必须追问、可假设或待研究，并说明为什么。
5. 返回一次性问题包：仅包含会改变后续任务图或推荐结论的问题，并为每题给推荐选项。
6. 返回 requirements_audit：覆盖缺口、冲突、默认假设风险和建议场景分支。

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
  "stage": "01",
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
    "loop-artifacts/contracts/01-r1-stage-input-package.json"
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
  "reviewer_card_id": "01-r1-requirements-auditor",
  "summary": "填写独立审计的结论与边界。",
  "verdict": "pass"
}
```

## 返回给 Commander 的格式

- 已确认事实 / 来源 / 适用条件
- 不确定或冲突项
- 对应任务卡的结构化结论
- 不要修改 `loop-state.json`，不要替 Commander 决定后续阶段。
