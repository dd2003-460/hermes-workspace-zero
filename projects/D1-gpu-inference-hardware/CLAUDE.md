# CLAUDE.md — RALPH 字段增量项目

本项目使用字段中心 RALPH runtime。当前阶段以 `loop-state.json.stage` 为准。

## 工作规则

- 多轮增量填写：`ralph field-init .` → 修改当前阶段 `fields.json` → `ralph field-apply . <文件>`。
- 禁止直接 Write/Edit `loop-state.json`；JSON 语法、必填字段、证据、置信度和原子保存由 runtime 完成。
- 缺失字段只按命令输出逐项修复，保留已经通过字段；不要因缺失而伪造 advance。
- 字段与 required outputs 完整后写 `advance.json`，运行 `ralph apply . <advance.json>`。
- Agent 可按字段范围派发；不需要预先创建或等待任务卡。
- 人类阻塞只影响当前任务；其余 ready 任务继续，候选任务必须标记 candidate。
- 不读完整 `loop-events.md`，只用 `ralph events . --tail 20`。

## 阶段重点

`01` 语义分解；`02` 证据调研；`02.5` 交叉验证；`03` 正交最小 DAG 与执行；`04` 验证；`04.5` 产出交叉验证；`05` 决策；`06` 交接和 exploration。

并行节点必须正交、独立可验证且写入路径不冲突；Join 必须列出全部依赖。未知因素继续作为 pending/research_required 字段增殖，直到有证据或明确默认。

## 文件边界

- `loop-state.json`：runtime 管理的唯一状态。
- `loop-events.md`：有限事件日志。
- `loop-artifacts/stages/<stage>/<revision>/fields.json`：Agent 唯一字段草稿。
- 同目录 `fields.md`：自动生成的阅读快照。
- 同目录 `advance.json`：经校验的阶段动作。

默认 Hook 是 `hybrid`：普通策略问题给提示并允许继续；受保护状态、危险副作用、越界路径和活动人类阻塞硬拒绝。
