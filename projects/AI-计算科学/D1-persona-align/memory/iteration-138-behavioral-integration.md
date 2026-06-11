---
name: iteration-138-behavioral-integration
description: 行为约束层集成到 realtime_alignment_monitor 和 gap_filler
metadata:
  type: project
  iteration: 138
---

# Iteration 138: 行为约束层集成到完整工具链

## 背景

Iteration 136 完成了 alignment_checker 的行为约束层集成。Iteration 138 将行为约束扩展到另外两个工具: realtime_alignment_monitor 和 gap_filler。

## 变更

### realtime_alignment_monitor.py
- 新增 `BEHAVIORAL_ANCHORS` 字典: 简洁直接 / 不解释 / 推进而非停滞
- 每个约束有 positive_patterns 和 negative_patterns
- `score_text()` 新增 `compute_behavioral_score()` 逻辑
- 权重从 60/15/25 改为 50/10/20/20
- `print_report()` 新增行为约束可视化

### persona_v3_gap_filler.py
- 新增 4 个维度模板: 自适应精度 / 自适应探索 / 自适应先验 / 自适应投影
- 新增 `BEHAVIORAL_FILL_TEMPLATES`: 3 个行为约束修正建议
- `get_missing_dimensions()` 扩展: 检测 behavioral: 前缀的缺失
- `generate_fill_suggestions()` 扩展: 区分 dimension 和 behavioral 类型
- `scan_all()` 统计区分维度和行为约束

## 测试结果

### gap_filler --scan (52 文件)
```
缺失维度统计:
  自适应自我: 39/52
  自适应感知: 9/52
  自适应先验: 5/52

缺失行为约束统计:
  推进而非停滞: 52/52
  简洁直接: 35/52
  不解释: 30/52
```

### gap_filler --file idea-11
正确输出: 1 个维度缺失(自适应自我) + 3 个行为约束缺失

## 发现

52 个 idea 分析文件全部缺少"推进而非停滞"约束。这是合理的——这些是静态分析文档，不是实时对话输出。行为约束应该主要应用于 AI 的实际对话回复中。

## 工具链覆盖

现在 3 个工具都支持双层评估:
1. alignment_checker — 静态文本分析
2. realtime_monitor — 会话中实时监控
3. gap_filler — 缺失补全建议生成

统一权重: 50% 维度 + 10% 信息论 + 20% 验证 + 20% 行为约束
