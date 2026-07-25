# CLAUDE.md — RALPH 字段增量项目

当前执行协议只有字段增量协议，不使用任务卡或预先批准的 auditor 卡。

1. 读取 `loop-state.json` 当前阶段。
2. 不存在草稿时运行 `ralph field-init .`。
3. 只编辑 `loop-artifacts/stages/<stage>/<revision>/fields.json`，允许多轮补写。
4. 每轮运行 `ralph field-apply . <fields.json>`；只修复返回的语法/字段问题。
5. 字段和 required outputs 完成后写同目录 `advance.json`，运行 `ralph apply . <advance.json>`。

不得直接编辑 `loop-state.json`，不得因普通字段缺失停止，已通过字段不能被增量提交删除。`research_required` 必须逐步补 `evidence_refs`；并行任务必须正交且写入不冲突；人类阻塞任务可跳过，候选任务必须保留 candidate 标记。

Agent 是可选的窄协作者，不需要预先创建任务卡；派发时明确一个字段或一个 DAG 节点的输入、输出和证据要求。

使用 `ralph events . --tail 20` 查看有限日志，使用 `ralph resume .` 从中断创建短上下文。默认 Hook 为 hybrid：普通问题软提示，状态文件、危险副作用和越界路径硬拒绝。
