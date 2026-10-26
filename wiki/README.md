# wiki
# origin: ai

## 本文件夹主要功能

个人知识库 wiki（卡片盒结构）：`SCHEMA.md`（结构规范）、`index.md`（总索引）、`log.md`（变更日志）、`wiki_export.json`（导出物），内容分三类子域：`concepts/`（概念卡）、`entities/`（实体卡）、`infrastructure/`（基础设施卡），原始素材层 `raw/`，维护脚本 `scripts/`。

## 接口

- 输入：`raw/` 原始素材、日常笔记
- 输出：结构化知识卡片（md）与 `wiki_export.json` 导出
- 对外函数签名：无统一 API；`scripts/` 内含维护脚本（见 `SCHEMA.md`）

## 调用说明

- 新增卡片遵循 `SCHEMA.md` 的卡片格式与链接规范
- 子目录功能见各自内容（本 README 不展开子域细节）
