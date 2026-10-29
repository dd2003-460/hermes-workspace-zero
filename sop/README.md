# sop — 全局 SOP 与 Agent 规格（原 agents/，2026-10-29 改名）
# origin: ai

## 本文件夹主要功能

全局 SOP 集合（2026-10-29 清理：旧 agent 规格已删，归档在 `archive/`、`archived-20261016/`）：`SOP-INDEX.md`（总索引，先查这里）、`goal-template.md`（goal 模板，五字段+阶段指针）、`arena-loop-pipeline.md`（arena 外包链路，唯一入口）、`research-task-template.md`（调研任务模板）、`structured-dispatch.md`（结构化输出派发）、`ego-browser-index.md`（ego-browser 用法）、`acp-rules.json`（ACP 硬规则下发入口）。

## 接口

- 输入：各 loop/外包通道的规格需求
- 输出：SOP 文档（供 AGENTS.md 指针引用与 agent 读取）
- 对外函数签名：无（纯文档层）

## 调用说明

- 查找 SOP 从 `SOP-INDEX.md` 进；AGENTS.md「压缩与驱逐索引」中多个 SOP 指针指向本目录或 `.claude/skills/`
