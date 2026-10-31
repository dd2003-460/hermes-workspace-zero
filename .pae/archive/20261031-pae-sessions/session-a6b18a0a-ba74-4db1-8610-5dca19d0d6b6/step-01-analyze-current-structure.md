# Step 01: 分析当前结构问题并给出诊断

## 目标
基于已读取的文件，产出对 goal-template.md 当前结构问题的完整诊断。

## 涉及文件
- `agents/goal-template.md`（255 行）
- `agents/goal-template-addon-acp-rule.md`（29 行待合并补丁）
- `agents/SOP-INDEX.md`
- `agents/arena-loop-pipeline.md`
- `loop/prompt-first/*.md`
- `agents/acp-rules.json`

## 做法
1. 统计 goal-template.md 各节内容占比
2. 识别哪些内容是"建 goal 时必须读"vs"执行时才需要"vs"完全不该在 goal 模板里"
3. 对照用户三个改进方向给出推荐

## 验收标准
- 产出清晰的问题分类表
- 给出推荐方案（含理由）