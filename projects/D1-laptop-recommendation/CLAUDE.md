# CLAUDE.md — RALPH 字段增量项目

本项目使用字段中心 RALPH runtime，不使用任务卡主流程。

- 当前阶段以 `loop-state.json.stage` 为准。
- 运行 `ralph field-init .` 创建草稿；增量编辑 `loop-artifacts/stages/<stage>/<revision>/fields.json`。
- 每轮运行 `ralph field-apply . <文件>`，只修复命令列出的错误，保留已通过字段。
- 不得直接编辑 `loop-state.json`；字段由 runtime 校验、按 concept 合并并原子保存。
- 字段和 required outputs 完成后写同目录 `advance.json`，运行 `ralph apply . <advance.json>`。
- Agent 是可选窄协作者；给出字段范围、输出 schema 和证据要求即可派发。
- 普通缺失字段不阻塞；不可推断/研究/采用默认的硬问题才记入 open-questions。
- 并行任务必须正交、独立可验证且写入不冲突；候选任务必须标记 candidate。
- 事件只用 `ralph events . --tail 20` 查看；模型中断用 `ralph resume .`。

阶段顺序：`01` 语义分解 → `02` 调研 → `02.5` 交叉验证 → `03` DAG/执行 → `04` 验证 → `04.5` 产出交叉验证 → `05` 决策 → `06` 交接与探索。

默认 Hook 为 `hybrid`。普通工具策略以提示为主；直接写状态文件、危险副作用、越界路径和活动人类阻塞硬拒绝。
