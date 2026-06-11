---
name: iteration-167-gap-filler-scan-performance-fix
description: gap_filler scan 性能修复 — 消除 100+ 子进程 fork 开销
metadata:
  type: project
  iteration: 167
---

# Iteration 167: gap_filler scan 性能修复

## 问题
gap_filler 的 `scan_all` 对 52 个 idea 文件逐一调用 monitor 子进程 (monitor 又 fork checker)。
总共约 52 × 2 = 104 个子进程 fork，执行需数分钟。

## 修复
替换 `get_missing_dimensions` 实现:
- **旧**: subprocess.run([monitor, "--file", f, "--json"]) → 2 层 fork
- **新**: 直接读取文件文本 + 正则匹配关键词 (内存分析)

## 新增
- DIMENSION_KEYWORDS: 6 维关键词词典 (与 alignment_checker 相同)
- BEHAVIORAL_CONSTRAINTS: 3 行为约束正负模式
- get_missing_dimensions 直接内存分析, 无 subprocess 开销

## 验证
- scan 52 文件: 几乎瞬间完成 (之前数分钟)
- 结果正确: 自适应精度 51/52 缺失, 感知 50/52 缺失, 自我 50/52 缺失
- 行为约束: 推进而非停滞 52/52 缺失 (预期, 静态文档非行动输出)

## 教训
不要在循环中 fork 子进程做本可用内存分析完成的工作。
后续如果有类似的 scan 场景 (批量处理多个文件), 优先考虑内存分析。
