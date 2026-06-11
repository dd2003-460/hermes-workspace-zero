---
name: iteration-181-english-checker-drift-detection
description: 英文版 alignment_checker 添加 drift 检测 (--baseline), 与中文版对齐
metadata:
  type: project
  iteration: 181
---

# Iteration 181: English checker drift detection

## 操作
将中文版 alignment_checker 的 drift 检测功能同步到英文版 persona_v3_alignment_checker_en.py。

新增:
- detect_drift(baseline_scores, current_scores): 维度评分变化检测
- --baseline 参数: 基线文件路径
- 中文版的 detect_drift 函数和 drift 分析输出

## 验证
测试: idea-01 vs persona-v3-prompt.txt
- Baseline: 1.26 (英文版量化方式不同, 维度评分 0.11-0.43 而非 0/1)
- Current: 3.42
- Drift: +0.0433 (1 个维度变化, 无 HIGH severity)
- 英文版分数绝对值更低但 drift 检测逻辑正确

## 教训
双检测器策略: 中文版用于快速检测 (binary matching), 英文版用于详细评估 (nuanced scoring)。两者都应支持 drift 检测。
