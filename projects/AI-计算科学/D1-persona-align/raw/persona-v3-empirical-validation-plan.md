# persona-v3 实证验证计划

**日期**: 2026-05-31
**目标**: 设计让成璐本人评估 persona-v3 输出对齐度的实验协议

## 背景

外部研究 (Whose Personae? 综述 63 篇合成 persona 研究) 指出：
> "only 35% discussing the representativeness of their personae"

persona-v3 最大的鸿沟不是理论，而是 empirical validation —— 让真人评估输出是否真实反映目标 persona。

## 实验设计

### 核心问题

persona-v3 prompt 生成的输出是否与成璐的真实输出在 persona 维度上一致？

### 方法：A/B 盲测

1. **准备真实样本**: 收集 10-20 组成璐的真实回复（从对话日志、社交媒体、学术写作）
2. **生成对应样本**: 用 persona-v3 prompt 和 method_only 策略生成同样主题的回答
3. **盲测设计**: 将真实回答和生成回答混合，随机编号
4. **评估维度**: 让成璐对每组回答评分（1-5）：
   - 语言风格是否像成璐？
   - 思维方式是否像成璐？
   - 你会自己这样回复吗？
   - 整体 persona 匹配度

### 评估指标

| 指标 | 描述 | 评分方式 |
|------|------|----------|
| Language Match | 语言风格匹配度 | 1-5 分 |
| Thinking Match | 思维方式匹配度 | 1-5 分 |
| "Would I say this?" | 成璐本人会说这种回答 | 是/否/不确定 |
| Overall Persona Match | 整体 persona 匹配度 | 1-5 分 |

### 实验步骤

```
Phase 1: 样本收集 (当前阶段)
- 从对话日志中收集真实回复（至少 20 条）
- 确保主题多样（学术、社科、数学、个人）

Phase 2: 生成对照样本
- 用 persona-v3 prompt 生成回答
- 用 method_only 80字符提示词生成回答
- 用 baseline（无特殊提示词）生成回答

Phase 3: 盲测
- 混合所有回答，随机编号
- 发送给成璐评估
- 收集评分数据

Phase 4: 数据分析
- 比较三种策略在各维度上的平均得分
- 验证假设：persona-v3 > method_only > baseline
- 分析错误模式：哪些维度最容易偏离
```

## 当前阻塞

- **真实对话样本**: 需要从对话日志中整理。对话日志可能在 `persona-evolve/` 目录或 Claude Code 的 session 历史中。
- **成璐的参与**: 实验需要成璐本人参与评估。如果成璐无法参与，可以用自动评估（alignment checker）代替人工评估。

## 自动评估替代方案

如果无法获得人工评估，可以使用以下自动化方法：

1. **alignment_checker 一致性**: 比较真实回答和生成回答的 6 维度得分分布
2. **聚类分析**: 用 embedding 对真实回答和生成回答进行聚类，观察是否在同一簇中
3. **cross-entropy 比较**: 计算真实回答与生成回答之间的 KL divergence

## 下一步行动

1. [ ] 整理真实对话样本（从 persona-evolve/ 或对话日志）
2. [ ] 生成对照样本（persona-v3 + method_only + baseline）
3. [ ] 设计评估问卷
4. [ ] 执行盲测或自动评估
5. [ ] 分析结果并更新 persona-v3
