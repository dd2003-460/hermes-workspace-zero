---
name: iteration-197-batch-persist-enhance
description: 批量持久化增强全部 52 个 idea 文件 (gap_filler --apply --persist)
metadata:
  type: project
  iteration: 197
---

# Iteration 197: Batch persistent enhancement of all 52 idea files

## 操作
修复 gap_filler 的 `--apply` 行为以支持 `--persist`（覆盖原文件），然后批量增强所有 52 个 idea 分析文件。

## 变更

### persona_v3_gap_filler.py
- 添加 `--persist` 参数
- `--apply --persist` 覆盖原文件，`--apply`（默认）生成 `-enhanced.md`
- 修复增强路径命名：使用 `Path.stem` 代替 `.replace(".md", "-enhanced.md")`

### persona_v3_batch_enhance.py
- `enhance_file(file_path, persist=False)` 接受持久化标志
- `run_gap_filler(file_path, persist=False)` 传递 `--persist` 给 gap_filler
- `--persist` 时直接读取原文件验证增强效果，不复用独立路径

## 结果
- 52/52 文件增强成功
- gap_filler --scan 显示 0 缺失维度
- alignment_checker 分数范围: 66-73 (avg ~69)
- 文件增长: +8~150 行/文件不等

## 教训
`Path.stem` 比 `.replace(".md", "-enhanced.md")` 更可靠地处理文件名中的连字符和特殊字符。
