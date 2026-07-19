# RALPH 子代理任务卡

- **Card ID**: `01-r1-builder-task_spec`
- **阶段**: `01-r1`
- **角色**: `task-spec-writer`
- **标题**: 任务规格构造
- **任务目标**: 把需求审计的结论与项目上下文综合成完整、可机器校验的 task_spec 切片。
- **原始任务**: 

## 必读文件

- `loop-state.json`
- `loop-artifacts/contracts/task-spec.json`
- `loop-artifacts/contracts/01-r1-stage-contract.md`
- `loop-artifacts/contracts/01-r1-submission-template.json`
- `loop-artifacts/stages/01/r1/task_spec.json`

## 执行边界

1. 综合 requirements-auditor 的 requirements_audit、task_spec 草稿与项目内已有资料，产出最终 task_spec。
2. 七类语义角色逐条给出；每个 attribute_matrix 叶节点必须含 concept/role/attribute/disposition/rationale，disposition ∈ {confirmed,inferred,assume,research}。
3. 预算/可行性/验收等不确定项用 assumption + scenario 覆盖，写入 assumptions/scenarios，不要留空字符串。
4. requirements_audit 填本轮 auditor 的 card_id、audit_artifact_ref 与一句话 summary。
5. 只写一份切片文件到 `loop-artifacts/stages/01/r1/task_spec.json`；该文件的顶层对象就是 `payload.task_spec` 的完整内容。
6. 不要写入 loop-state.json 或其他受控文件；不要替 Commander 做独立门禁审计（那是 gate 子代理的职责）。
7. 完成后只把结构化结论简短返回给 Commander，并确认切片文件已写好。
8. 参考阶段方法论（源自 loop/1-loop，补充要求，不覆盖上方门禁/边界规则）：
9. 搜索优先、不问可搜：派发前先搜索所有可搜索信息（项目结构、依赖、代码、文档、数据、工具、外部论文/GitHub），搜索齐全后才允许问用户。
10. 问题必须一次性完整、必须是选择题且带推荐项；禁止逐个追问、禁止“你觉得呢”式开放提问。
11. 约束按分类标记：已确认 / 可推断(记录证据+置信度+可逆性) / 假设(默认策略+置信度) / 待研究 / 必须追问。
12. 提问闸门（先推断后提问）：仅当同时满足“用户/项目/环境均无答案、不能推断或研究、会改变硬可行性/硬预算/验收标准/价值授权、不能用场景覆盖”四项，才生成用户问题。
13. 置信度门槛：所有 MUST 类约束已确认、整体置信度 ≥ 0.7 才继续；< 0.5 回退重新澄清。
14. 模型档位未知时先查本地配置，仍未知则并列 30–35B 与更大模型档位并研究内存需求；用户已明确买本地硬件或候选含云服务时不再追问。

## 允许工具

`Read`, `Glob`, `Grep`, `Write`, `Edit`

## 输出接口

```json
{
  "assumptions": [],
  "attribute_matrix": [
    {
      "alternative_scenario": "",
      "attribute": "",
      "concept": "",
      "confidence": 0.0,
      "disposition": "confirmed",
      "evidence_refs": [],
      "impact": "material",
      "rationale": "",
      "reversible": true,
      "role": ""
    }
  ],
  "constraints": [],
  "open_questions": [],
  "requirements_audit": {
    "artifact_ref": "",
    "card_id": "01-r1-requirements-auditor",
    "summary": ""
  },
  "scenarios": [
    {
      "id": "S1",
      "name": ""
    }
  ],
  "semantic_map": {
    "background": [],
    "comparison_set": [],
    "constraints": [],
    "decision_object": [],
    "deliverable": [],
    "objective": [],
    "uncertainty": []
  },
  "success_criteria": []
}
```

## 返回给 Commander 的格式

- 已确认事实 / 来源 / 适用条件
- 不确定或冲突项
- 对应任务卡的结构化结论
- 不要修改 `loop-state.json`，不要替 Commander 决定后续阶段。
