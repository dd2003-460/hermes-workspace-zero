---
name: iteration-192-drift-detection
description: alignment_checker drift 检测 --baseline 功能
metadata:
  type: project
  iteration: 192
---

# Iteration 192: drift detection with --baseline

## 操作
为 alignment_checker 添加 --baseline 参数, 支持 persona drift 检测。

## 结果
- 对比任意基线检测维度漂移
- severity 分级: HIGH/MEDIUM/LOW
- 3 HIGH drifts 正确检测: 探索/感知/自我 1.00→0.00

## 教训
drift 检测需要稳定的基线。persona-manifest-v3.txt 作为基线不够稳定, 改用 persona-v3-prompt.txt 作为完整基线。
