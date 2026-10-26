# D1-hintfree-decomposition — 无提示目标分解
# origin: ai

## 本文件夹主要功能

hint-free goal decomposition 实验：验证不依赖提示词（hint-free）的目标分解能否工作。`prompt/01-decomposition.md` 为交付的核心分解 prompt（红线：禁止任务泄漏——prompt 里不得出现具体任务内容）。子目录：`prompt/`（交付 prompt）、`runs/`（实验运行）、`memory/`、`raw/`、`tasks/`。

## 接口

- 输入：`prompt/01-decomposition.md`（给任意模型）
- 输出：`runs/` 下的分解结果与对照评分
- 对外函数签名：无（prompt 交付）

## 调用说明

- 红线：修改 `prompt/` 任何文件前先确认不泄漏任务内容；实验记录在 `runs/`
