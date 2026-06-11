---
name: iteration-196-batch-enhance
description: persona_v3_batch_enhance.py 批量增强工具 — --top/--all/--file
metadata:
  type: project
  iteration: 196
---

# Iteration 196: persona_v3_batch_enhance.py batch tool

## 操作
创建批量增强脚本, 一次性处理多个 idea 分析文件。

## 功能
- `--all`: 增强所有 idea 分析文件
- `--top N`: 增强最弱 N 个文件 (结合 dashboard 和 baseline)
- `--file`: 增强指定文件
- `--json`: JSON 输出 (stdout, 无污染)
- 进度输出到 stderr
- 自动清理增强文件

## 测试
`--top 3 --baseline persona-v3-prompt.txt --json`:
- 6 文件 (worst 3 + best 3)
- iteration-111: 26.75 → 64.57 (+37.8)
- idea-42: 31.72 → 66.74 (+35.0)
- idea-24: 42.6 → 69.28 (+26.7)
- idea-102: 64.31 → 69.82 (+5.5)
- idea-46: 59.28 → 72.49 (+13.2)
- idea-97: 54.37 → 69.82 (+15.4)

## 教训
stderr/stdout 分离很重要。批量工具的进度消息必须走 stderr, JSON 走 stdout。
