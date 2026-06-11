---
name: iteration-150-index-update
description: 更新 INDEX.md 反映 persona-v3 框架 + 评估系统 + 外部研究
metadata:
  type: project
  iteration: 150
---

# Iteration 150: INDEX.md 更新

## 问题
INDEX.md 严重过时 — 缺失 persona-v3 框架、三层评估系统、26 篇外部研究等信息。文件结构描述也不完整 (scripts/ 目录不在索引中)。

## 更新内容
1. 状态行: 更新为 "persona-v3 框架完整 + 三层评估系统 + 26 篇外部研究"
2. 最终产物: 新增 persona-manifest-v3.txt (8 原则, 80 字符) + persona-v3 框架描述 (6 维度+3 行为约束)
3. 三层评估系统: 新增工具表格 (alignment_checker + realtime_monitor + gap_filler) + 统一权重 + 区分验证结果
4. 文件结构: 更新为完整目录树, 包含 scripts/, persona-evolve/, eval_results/
5. 新增文件列表 (iteration 131-150)
6. 外部研究列表 (26 篇, 分高/中相关)

## 改进
- INDEX.md 现在反映当前项目状态
- 文件结构完整且与磁盘一致
- 外部研究有明确的索引

## 后续
INDEX.md 当前包含大量非索引内容 (详细 eval 结果、进度表等)。可考虑精简为纯索引, 详细内容由子目录 INDEX.md 或独立报告承载。这符合 AGENTS.md 红线 #0 规范。
