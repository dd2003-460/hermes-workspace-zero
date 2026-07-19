# RALPH 子代理任务卡

- **Card ID**: `01-r1-requirements-auditor`
- **阶段**: `01-r1`
- **角色**: `requirements-auditor`
- **标题**: 需求、遗漏和假设审计
- **任务目标**: 独立检查 Commander 对用户意图的语义分解，找出会改变决策的遗漏属性与隐含假设。
- **原始任务**: 我需要为本地 AI 工作站选择 GPU 或整机方案。

使用场景：macOS、本地运行 Claude Code/RALPH 和本地大语言模型，主要模型是 Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit，同时比较 9B 和 27B 模型。需要支持约 60000 token 上下文、工具调用、单用户长时间运行，未来希望支持 1 至 2 个并行任务。不训练模型，只做推理、研究、代码和文档工作。

决策目标：在价格、显存/统一内存、长上下文速度、首 token 延迟、持续解码速度、稳定性、功耗、噪音、可维护性和迁移成本之间，选择性价比最高的方案。

候选范围：Mac、PC GPU 工作站、二手显卡和云服务，分别比较。预算按 5000 元以内、5000 至 15000 元、15000 元以上三个区间分析。必须区分新机、二手市场和云服务，不允许把不同类型直接混成一个排名。

必须调查：模型实际内存需求、显存/统一内存余量、MLX/CUDA/Metal 兼容性、长上下文性能、持续运行温度和功耗、并行任务能力、升级空间、价格和可获得性。价格必须注明日期、地区、来源和新旧状态。

证据要求：优先使用厂商、官方文档、可靠硬件评测和实际销售页面；关键事实至少交叉核验一次；所有事实记录来源链接、日期、适用条件和核验状态；不能使用未来数据、不能把推测写成事实、不能承诺盈利或绝对性能。

交付物：需求属性矩阵、可验证任务 DAG、兼容旧 Ralph Loop 的 tasks/TASKS.md、候选方案表、不同预算场景推荐、性能测试协议、风险和不确定性清单。

流程要求：先完成当前 RALPH 阶段的需求审计和任务分解，必须派 requirements-auditor；完成 01 和 02、生成 DAG、任务卡和 tasks/TASKS.md 后暂停，不开始网页调研，等待我的下一条提示。

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
