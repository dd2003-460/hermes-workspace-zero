---
name: iteration-187-gap-filler-behavioral-fix
description: gap_filler behavioral suggestion 去负面词 — 不再触发 alignment_checker negative_patterns
metadata:
  type: project
  iteration: 187
---

# Iteration 187: gap_filler behavioral suggestion negative word fix

## Bug
BEHAVIORAL_FILL_TEMPLATES 中的 suggestion 文本包含对齐检测器 negative_patterns:
- "避免'总的来说'" → 触发 简洁直接 negative pattern
- "避免'这意味着'" → 触发 不解释 negative pattern

## 修复
重写 behavioral suggestion 为纯正面行动语言:
- "简洁直接": "以核心结论开头，直接展示关键数据和推理步骤" (无负面词)
- "不解释": "假设读者已具备背景知识，从分析主体开始" (无负面词)
- "推进而非停滞": "用'下一步做X'和'接下来是Y'结尾" (无负面词)

## 结果
- idea-42: 31.72 → 66.74 (+35.0)
- 行为约束: 0.14 → 0.29 (从下降变为上升)
- 维度覆盖率: 6/6 (100%)

## 教训
生成补全建议时，建议文本本身不能触发检测器的负面模式。必须做 self-consistency check: 对建议文本也运行 alignment_checker。
