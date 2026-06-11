---
name: iteration-195-behavioral-negative-fix
description: gap_filler --apply 行为约束负面词修复
metadata:
  type: project
  iteration: 195
---

# Iteration 195: behavioral suggestion negative word fix

## 操作
修复 gap_filler --apply 行为约束建议中的负面词问题。

## 问题
原有行为修正建议使用"避免'总的来说'"等否定句式, 触发 alignment_checker 的 negative_patterns 检测, 导致 behavioral 分数下降。

## 结果
重写为纯正向行动指令:
- "避免'总的来说'" → "以核心结论开头, 直接展示关键数据和推理步骤"
- behavioral 分数从 0.14 提升到 0.29
- --validate 模式可以检测到 behavioral 降级
