# 01 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/01/r1/kb9-fields-r290.json` 生成，请勿手改。

> 生成时间：2026-11-04 04:31

## 概览

- 字段总数：**4**
- 待办（pending / research_required）：**1**
- 分组：background×1、goal×1、known×1、unknown×1

## 字段明细

### background

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 用户原始任务 | 任务描述 | confirmed | 1.00 | material | 否 |

### goal

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal | KB.1 教材第9篇『伪 thinking vs 真推理』note 收口：产出 notes/pseudo-thinking-vs-real-reasoning.md（A段概念块×6：CoT/scratchpad、伪thinking判定、推理时计算(test-time compute)、自校验verify机制、loss与目标函数在推理时的角色、习惯刻入权重vs prompt；每块是什么/为什么/边界+conf；B段成璐视角判断+可证伪idea；C段≥2条可证伪预测带判死条件）+ INDEX.md 加行 + drift-check v1≥75→v2=100/100。覆盖已知因素(前8篇已建框架/成璐S3质疑点/T17本地27b实验锚点)与未知因素(CoT是否真改变推理路径的实证边界/test-time scaling 在本地小模型上的拐点/伪thinking的可检测判据)。 | confirmed | 0.95 | material | 是 |

### known

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| known | ① KB.1 格式规范(A名词表+B成璐视角+drift-check硬门槛: 句级第一人称率/均句长/禁词0)见 README.md，前8篇全过100分；② 成璐 S3 场景亲自质疑过『伪thinking』『习惯在权重还是prompt』(interest-directions C区#8 记录)；③ 本地有 qwen3.8-27b @ :8787 可做推理行为实验(T17 full01 刚跑完 610 题，answerer/judge 链路健康)；④ 前8篇已覆盖训练机制(loss/RLHF/fine-tuning)/记忆/goal-loop控制层，本篇不重复只接边。 | confirmed | 0.90 | material | 是 |

### unknown

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| unknown | ① CoT/scratchpad 对 LLM 推理路径改变的实证边界(哪些任务真受益/哪些是表演性步骤)——需调研 arXiv 实证研究；② 伪thinking的可检测判据(logprob探针? 步骤冗余度? 删步骤后答案不变率?)——成璐研究方向相关但无现成结论；③ test-time compute scaling 在 7B-27B 本地模型的拐点位置(大模型曲线能否外推)；④ verify/自校验在小模型上是否正收益(错误放大风险)。 | research_required | 0.30 | material | 是 |

## 证据与备注

### 用户原始任务

用户初始任务输入，作为本阶段已知背景字段。

证据：
- user:initial_task

### goal

exploration r1 选定任务，范围限定单文件 note + INDEX 行，纯本地执行。

证据：
- projects/知识/D1-knowledge-base/memory/interest-directions.md (C区#8)
- projects/知识/D1-knowledge-base/notes/INDEX.md (前8篇清单)

### known

均为工作区既有台账/产物事实。

证据：
- projects/知识/D1-knowledge-base/README.md
- projects/知识/D1-knowledge-base/notes/INDEX.md
- tools/memory-benchmarks/results/locomo/locomo-full01-final-report.md (:8787 链路健康证据)

### unknown

四项均需外部调研(arXiv/web-llm)或本地实验回填，当前无证据。
