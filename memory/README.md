# memory
# origin: ai

## 本文件夹主要功能

全局记忆库（跨项目、项目级 memory/ 之外的仓库层记忆）：`INDEX.md`（记忆总索引）、`arena-audit-report-2026-10-20.md`（arena 审计报告）、`arxiv_submission_status.md`（arXiv 投稿状态）、`dashboards/`（状态面板）、`notes/`（全局笔记）。

## 接口

- 输入：各项目的状态快照、审计结论
- 输出：索引 + 状态文件 + 面板
- 对外函数签名：无（纯文档层）

## 调用说明

- 新增记忆文件必须同步登记到 `INDEX.md`（记忆入库前向量化并分类：decision/approach/result/reflection）
- 子目录功能见各自内容
