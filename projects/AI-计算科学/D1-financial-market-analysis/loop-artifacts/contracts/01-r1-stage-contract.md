# RALPH 阶段契约

阶段：01-r1

## 固定提交接口

通过本阶段时必须复制并填写 `loop-artifacts/contracts/01-r1-submission-template.json`；不得自创字段或只用自然语言声明通过。
其中的 `payload.stage_review` 必须来自已完成的独立阶段门禁，并且所有检查均为 pass、无 blocking_findings。

## 通用语义分解规则

先按决策语义而非字面词语拆解：background、decision_object、objective、comparison_set、constraints、deliverable、uncertainty。

对每个语义角色展开会改变决策的隐藏属性；当属性已能被确认、向人类追问、明确假设或变成可验证研究任务时，停止继续拆分。禁止无穷拆词或静默假设。

## 01：主动澄清与遗漏分析

必须形成 `task_spec`：semantic_map、attribute_matrix、约束、假设、一次性问题包、场景分支和成功标准。
先读取项目内上下文；对会改变任务图或结论的未知项必须主动追问，不能把它们伪装成事实。
完成前必须派发 requirements-auditor；本阶段禁止 deep-research、Skill、WebSearch、WebFetch 和最终推荐。

## 已批准的子代理任务卡

- `01-r1-requirements-auditor`：需求、遗漏和假设审计（pending）— `loop-artifacts/task-cards/01-r1-requirements-auditor.md`
