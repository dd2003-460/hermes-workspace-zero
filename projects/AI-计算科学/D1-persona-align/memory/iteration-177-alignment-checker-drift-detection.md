---
name: iteration-177-alignment-checker-drift-detection
description: alignment_checker 添加 drift 检测 (--baseline) — 对比基线检测 persona drift, severity 分级
metadata:
  type: project
  iteration: 177
---

# Iteration 177: alignment_checker drift 检测

## 操作
添加 `--baseline` 选项到 alignment_checker，支持对比两个文本的维度评分变化。

新增功能:
- `detect_drift(baseline_scores, current_scores, threshold=0.1)`: 检测维度评分变化
- severity 分级: HIGH (≥0.3), MEDIUM (≥0.15), LOW (<0.15)
- 综合漂移: 平均维度评分变化
- JSON 输出包含 baseline 和 current 的完整对比

## 验证
测试: `--baseline persona-v3-prompt.txt memory/idea-01-...md`
- Base alignment: 63.08 (persona-v3 prompt)
- Current alignment: 39.0 (idea-01)
- Total drift: -0.50 (平均维度下降 0.5)
- 3 HIGH severity drifts: 探索/感知/自我 1.00→0.00

## 更新
- TASKS.md: T28 (drift 检测)
- 项目最终状态: 三层评估工具更新, 中文检测器新增 drift 检测

## 教训
drift 检测是生产环境中 persona 监控的核心功能。ContextEcho/SPASM 证明 persona drift 是真实问题, persona-v3 的 alignment_checker 可以作为轻量级替代方案。
