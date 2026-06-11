---
name: iteration-168-gap-filler-context-aware-templates
description: gap_filler 上下文感知模板 — 从通用占位符改为从源文件提取真实内容
metadata:
  type: project
  iteration: 168
---

# Iteration 168: gap_filler 上下文感知模板

## 问题
旧的 `fill_template(template, topic)` 只接受 topic 字符串，所有占位符都用硬编码通用文本：
- `{key_point}` → "该论点的信息论结构决定了系统的核心约束"
- `{secondary_point}` → "该论点的形式化表达细节"
- `{perspective_1}` → "系统的内禀动力学过程"
- `{perspective_2}` → "系统输出的统计规律"

补全建议虽然结构正确，但内容通用，与源文件无关。

## 修复
新增 `extract_context(file_path, topic)` 函数:
- **key_point**: 搜索包含"核心/关键/主要"的语句，或取第一段
- **secondary_point**: 搜索包含"形式化/数学/公式"的语句，或取第四段
- **perspective_1**: 搜索"内部/内禀/主观/第一人称"相关语句
- **perspective_2**: 搜索"外部/统计/观测/输出"相关语句
- **perspective_1 fallback**: "{topic} 作为内在的认知动力学过程"
- **perspective_2 fallback**: "{topic} 作为可观测的统计规律"

`fill_template(template, context)` 改为接受完整上下文字典。

## 验证
测试 `memory/idea-01-ai训练数据是否是层级化的...md`:
- 自适应精度建议中: key_point 提取为 "**核心问题**：", secondary_point 提取为实际内容
- 自适应先验建议中: perspective_1 提取为关于训练数据层级化的原文，perspective_2 提取为关于 RAG 的原文
- 补全建议现在包含源文件的具体内容，而非通用占位符

## 更新
- TASKS.md: T23 (gap_filler 上下文感知模板改进)
- 项目最终状态: 修正研究论文数 50→33 (实际文件计数), 新增 Hermes 部署项
- 总分任务: T1-T23 全部完成

## 教训
模板系统的实用性取决于内容的相关性。即使是最简单的模板，如果填充的是源文件真实内容，也远比通用占位符更有用。
