# RALPH 阶段契约

阶段：01-r1

## 固定提交接口

通过本阶段时必须复制并填写 `loop-artifacts/contracts/01-r1-submission-template.json`；不得自创字段或只用自然语言声明通过。
其中的 `payload.stage_review` 必须来自已完成的独立阶段门禁，并且所有检查均为 pass、无 blocking_findings。
任务卡、阶段契约、输入包和提交模板由运行时物化；Commander 不得用 Agent、Write 或 Edit 创建/修复它们。
任务卡为 `dispatched` 时表示内部子代理正在运行，不是 `blocked_human`；不得重派或循环读取 `loop-events.md`，等待 `SubagentStop`。

## 通用语义分解规则

先按决策语义而非字面词语拆解：background、decision_object、objective、comparison_set、constraints、deliverable、uncertainty。

对每个语义角色展开会改变决策的隐藏属性；当属性已能被确认、合理推断、向人类追问、明确假设或变成可验证研究任务时，停止继续拆分。禁止无穷拆词、把未单独命名的字段自动变成问题，或无证据静默假设。

需求分流闸门：用户明确输入/历史补充 > 项目状态与文档 > 本地环境与配置 > 工具研究 > 高置信推断 > 默认假设/场景。只有当信息无法确认、推断或研究，会改变硬可行性/硬预算/验收标准/价值授权，且不能用场景覆盖时，才使用 ask_human。模型档位未知时先检查本地配置，仍未知就建立 30-35B 与更大模型场景并研究内存；用户已明确购买本地硬件或候选集合已包含云服务时，不得重复追问这些事实。

## 01：主动澄清与遗漏分析

必须形成 `task_spec`：semantic_map、attribute_matrix、约束、假设、一次性问题包、场景分支和成功标准。
先读取项目内上下文；对会改变任务图或结论的未知项执行需求分流闸门，只有无法确认、推断、研究且不能场景化的事项才主动追问。
完成前必须派发 requirements-auditor；本阶段禁止 deep-research、Skill、WebSearch、WebFetch 和最终推荐。

## 已批准的子代理任务卡

- `01-r1-requirements-auditor`：需求、遗漏和假设审计（completed）— `loop-artifacts/task-cards/01-r1-requirements-auditor.md`
