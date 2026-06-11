# Iteration 208: 修复 persona_v3_dashboard.py Python 3.14 glob 兼容性

## 问题

`persona_v3_dashboard.py --json /tmp/dashboard-test.json` 崩溃:
```
NotImplementedError: Non-relative patterns are unsupported
```

## 根因

Python 3.14 的 `pathlib.Path.glob()` 不再支持非相对路径 (absolute paths 或含 `..` 的路径).

Dashboard 在 line 262 使用 `memory_dir.glob(pattern)`, 当 `pattern` 是绝对路径 (如 `--file /tmp/xxx`) 时直接崩溃.

## 修复

```python
if pattern:
    p = Path(pattern)
    if p.is_absolute() or '..' in pattern:
        # Python 3.14+ pathlib.glob doesn't support non-relative patterns
        files = [f for f in [p] if f.exists() and f.is_file() and memory_dir in f.resolve().parents]
    else:
        files = list(memory_dir.glob(pattern))
```

## 验证

- Dashboard 扫描 53 文件, 分数范围 1.9-33.9, 平均分 28.1
- 所有 6 维度覆盖率正确计算
- 前 3 最对齐文件正确列出

## 教训

- Python 3.14 的 pathlib 有更激进的变更, 不能假设 glob 行为向后兼容
- 在 CI 或环境升级前, 应该验证关键脚本的兼容性
- 如果需要一个文件路径, 应该用 `Path(path).exists()` 而不是 `Path.glob()`
