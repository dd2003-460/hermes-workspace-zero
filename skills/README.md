# skills
# origin: ai

## 本文件夹主要功能

工作区级 skill 存放目录，当前含 `grill-ralph/`。注意：会话实际加载的 skill 挂载点是 `.claude/skills/`（如 `arena-outsource`、`ego-verify`、`project-tidy` 等），本目录为工作区侧副本/草稿位，两者关系用途待补充。

## 接口

- 输入：skill 定义（SKILL.md + 配套脚本）
- 输出：可被 skill 机制加载的指令包
- 对外函数签名：无

## 调用说明

- skill 格式参照 `.claude/skills/` 下既有 SKILL.md
- 正式启用的 skill 以 `.claude/skills/` 为准
