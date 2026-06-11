---
name: iteration-190-dashboard-top-filter
description: dashboard --top 参数支持 JSON 过滤 (最弱 N + 最强 N)
metadata:
  type: project
  iteration: 190
---

# Iteration 190: dashboard --top parameter for JSON

## 操作
修复 `persona_v3_dashboard.py` 中 `--top` 参数只对文本输出生效的问题。

## 结果
- `--top N` JSON 输出: 返回最弱 N + 最强 N 个文件 (无重复)
- `--top 0`: 返回全部 (原始行为)
- `--top >= 总数`: 返回全部 (上限保护)

## 测试
- `--top 0`: 53 条 (全部)
- `--top 3`: 6 条 (最弱3 + 最强3)
- `--top 100`: 53 条 (全部, 截断)

## 教训
CLI 参数需要一致性: 文本输出和 JSON 输出都应受相同参数控制。
