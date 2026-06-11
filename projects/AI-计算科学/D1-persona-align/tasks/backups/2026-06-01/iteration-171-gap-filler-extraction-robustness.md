---
name: iteration-171-gap-filler-extraction-robustness
description: gap_filler 上下文提取鲁棒性改进 — 跳过元数据/引用/代码块, 精准定位 topic 相关段落
metadata:
  type: project
  iteration: 171
---

# Iteration 171: gap_filler 上下文提取鲁棒性改进

## 问题
Iteration 168 的 `extract_context` 使用简单的正则关键词匹配提取上下文内容。
问题：
1. 元数据行（`**来源**`, `**日期**`）被错误合并为段落
2. 引用行（`>`）被当作普通内容
3. 代码块（```）中的数学公式被当作文本段落
4. key_point 匹配包含通用关键词的行（"核心/关键/主要"）而非 topic 相关段落
5. perspective_1/perspective_2 fallback 总是返回通用占位符

## 修复
重写 `extract_context` 函数：
- **代码块跳过**: 识别 ``` 标记, 跳过中间所有行
- **元数据跳过**: 跳过 `**` 开头和 `>` 开头的行
- **标题跳过**: 跳过 `#` 和 `---`
- **段落合并**: 正确合并 markdown 段落
- **key_point**: 查找包含 topic 的"非问题陈述"段落（排除以 ? 结尾的问题句）
- **secondary_point**: 查找包含"例如/形式化/公式"等关键词的证据段落
- **perspective_1**: 查找包含"机制/本质/内部"的段落
- **perspective_2**: 查找包含"观测/规律"的段落或用结论性段落

## 验证
10/10 sample 文件通过提取质量检查:
- idea-01: "成璐问了一个关于数据表示的结构..." 
- idea-15: "笨是否等价于信息效率？"
- idea-18: "不同的选择压如何塑造基因编码？"
- idea-20: "KV cache 自适应...自适应精度的代理"

所有 key_point 均为 topic 特异性的实质性内容, 不再产出通用占位符。

## 教训
上下文提取的关键不是"关键词匹配", 而是"跳过噪声 + 精准定位"。
跳过元数据/引用/代码块是前提, 精准定位 topic 相关段落是核心。
