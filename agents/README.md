# agents — 全局 Agent 规格与 SOP
# origin: ai

## 本文件夹主要功能

全局 Agent 规格与标准操作流程（SOP）集合：`SOP-INDEX.md`（所有 SOP 的总索引，先查这里）、`goal-template.md` / `goal-template-addon-acp-rule.md`（goal 模板）、`arena-loop-pipeline.md` / `arena-outsource.md`（arena 外包 SOP）、`ego-browser-index.md`（ego-browser 用法）、`loop-executor.md`（loop 执行器规格）、`task-manager.md`（任务管理器）、`sub-brain.md`（副脑规格）、`qwen-thinking-loop-fix.md`（qwen 思考循环修复记录）、`acp-rules.json`（ACP 规则）、`archived-20261016/`（归档）。

## 接口

- 输入：各 loop/外包通道的规格需求
- 输出：SOP 文档（供 AGENTS.md 指针引用与 agent 读取）
- 对外函数签名：无（纯文档层）

## 调用说明

- 查找 SOP 从 `SOP-INDEX.md` 进；AGENTS.md「压缩与驱逐索引」中多个 SOP 指针指向本目录或 `.claude/skills/`
