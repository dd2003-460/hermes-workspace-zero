# CLAUDE.md — RALPH 字段增量项目

本项目使用字段中心 RALPH runtime。当前阶段以 `loop-state.json.stage` 为准。

## 必须遵守

- 可多轮增量填写，不要求一次完成任务分解。
- 若当前阶段草稿不存在，运行 `ralph field-init .`。
- 只修改 `loop-artifacts/stages/<stage>/<revision>/fields.json`，再运行 `ralph field-apply . <文件>`。
- 不得直接 Write/Edit `loop-state.json`；由 runtime 负责字段校验、合并和原子保存。
- 语法错误或缺字段时，只修复 Hook/命令列出的项目，已通过字段保留。
- 字段和 required outputs 完成后写同目录 `advance.json`，运行 `ralph apply . <advance.json>`。
- 对 `research_required` 字段，Agent 是必需的窄任务协作者；一个字段派发一个 Agent，prompt 第一行必须带 `RALPH_FIELD_TASK=<task.json>`，给出字段范围、证据要求和 JSON 输出格式。只有 `confirmed` / `inferred` / `assumed_default` 字段可由 Commander 自己增量填写。
- 不要因为普通缺失字段停止；只有无法推断、研究或采用默认值的硬可行性问题才记录 `open-questions.md`。
- 不要读取完整 `loop-events.md`；诊断用 `ralph events . --tail 20`。

## 阶段重点

- `01`：背景、决策对象、目标、比较集合、约束、交付物和未知因素。
- `02`：对 `research_required` 字段补证据；研究引出的未知继续作为 pending 字段增殖。
- `02.5`：对关键事实做独立来源交叉验证。
- `03`：拆解和执行最小正交 DAG；并行节点写入范围不得冲突。
- `04` / `04.5`：验证产物、claim、来源、日期和适用条件。
- `05` / `06`：形成决策、交接、任务板选择和 exploration candidate。

## 权威文件

- `loop-state.json`：唯一状态。
- `loop-events.md`：有限可观察事件摘要。
- `loop-artifacts/stages/<stage>/<revision>/fields.json`：增量字段。
- `loop-artifacts/stages/<stage>/<revision>/fields.md`：runtime 自动生成的可读快照。
- `loop-artifacts/stages/<stage>/<revision>/advance.json`：阶段动作。

项目由 `ralph run` / `ralph loop` 初始化或恢复；默认 Hook 模式是 `hybrid`。受保护状态文件、危险副作用和越界路径仍会硬拒绝，普通字段缺失只返回提示。
