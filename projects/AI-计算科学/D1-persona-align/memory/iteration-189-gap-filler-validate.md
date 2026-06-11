---
name: iteration-189-gap-filler-validate
description: gap_filler --validate 自一致性检查 + --scan 零 subprocess fork
metadata:
  type: project
  iteration: 189
---

# Iteration 189: gap_filler --validate self-consistency check

## 操作
1. 添加 `process_file(file_path, capture_behavioral=False)` 参数，仅当需要时调用 alignment_checker
2. `--scan` 模式: capture_behavioral=False (零 subprocess fork)
3. `--file --validate`: capture_behavioral=True (调用 alignment_checker 比较 before/after behavioral score)
4. `--validate` 输出: "OK: behavioral score improved by 0.1508" 或 "WARNING: degraded"

## 结果
- `--scan`: 52 文件扫描，0 subprocess fork
- `--file --validate`: original 0.1402 → enhanced 0.2910, OK
- `--json` 输出包含 `original_behavioral_overall: 0.1402`

## 教训
工具链中的 subprocess fork 需要精确控制调用点。`process_file` 被多个调用点使用，参数化是关键。
