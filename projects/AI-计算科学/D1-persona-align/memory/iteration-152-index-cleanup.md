---
name: iteration-152-index-cleanup
description: INDEX.md 精简为纯索引格式 (AGENTS.md 红线 #0)
metadata:
  type: project
  iteration: 152
---

# Iteration 152: INDEX.md 精简为纯索引

## 问题
INDEX.md 包含大量非索引内容：详细 eval 结果、进度表、最终产物描述、项目目标等。违反 AGENTS.md 红线 #0 "每层的 INDEX.md 只描述下一层有哪些项目（纯索引）"。

## 操作
重写 INDEX.md 为纯索引格式：
- 保留基本信息 (状态、创建日期、更新日期)
- 子目录索引 (tasks/, memory/, raw/, researches/, persona-evolve/, eval_results/, scripts/)
- 顶层文件索引 (persona-manifest-v3.txt, persona-v3-prompt.txt, 评估报告)
- 递归索引指向子目录 INDEX.md

### 移除的内容
- 项目目标描述 (详细分析 → 各研究报告承载)
- 最终产物详细描述 (细节 → persona-manifest-v3.txt 和评估报告)
- 进度表 (tasks/ 子目录承载)
- eval 结果 (eval_results/ 子目录承载)
- 外部研究列表 (raw/ 子目录承载)
- 文件结构树 (子目录索引已替代)

## 验证
INDEX.md 现在 30 行 (原 201 行)，纯索引格式。
