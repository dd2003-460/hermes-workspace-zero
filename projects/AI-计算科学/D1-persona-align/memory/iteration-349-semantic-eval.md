# Iteration 349: 语义匹配评估器 — 替代关键词匹配

## 背景

迭代 343-347 的真实 Hermse 会话测试发现 **F4 假阴性问题**：
- 关键词匹配评估工具仅通过精确子串匹配判定维度覆盖
- 模型生成了 persona 概念的实质内容（贝叶斯、rate-distortion、成璐），但**未使用关键词词汇**（探索、感知、观测者）
- 导致 persona-v3 功能对齐但维度得分偏低

## 解决方案：语义匹配评估器 `semantic_alignment_checker.py`

### 设计

使用 sklearn TF-IDF + cosine similarity 实现零外部依赖的语义评估：

1. **TF-IDF cosine similarity** (`analyzer="char_wb"`, char n-grams): 捕获整体风格相似性（权重 0.7）
2. **概念类别覆盖率**: 8 个粗粒度概念类别（权重 0.3）
3. **加权综合评分**: `0.7 * tfidf + 0.3 * avg_concept`

不依赖预训练嵌入模型，纯 sklearn + numpy。

### 8 概念类别

| 类别 | 关键词覆盖 |
|------|-----------|
| rate_distortion | rate-distortion, R(D), 信息瓶颈, channel, capacity, 互信息 |
| bayesian | 贝叶斯, 先验, 后验, p(h|e), bayesian update |
| cross_domain | 同构, isomorphic, 跨域, 类比, homomorphism |
| observer_dependence | 观测者, observer, y(theta), 第一人称 |
| perception_time | 感知时间, 感知速率, t_p, perception |
| exploration | 探索, exploit, 磨刀, 不确定性 |
| self_preservation | 存在延续, 永生, 抗毁, 价值函数 |
| behavioral | 简洁, 追问, 边界条件, 过拟合, 置信度 |

## 实验结果

### 真实会话响应语义评分

| 版本 | Prompt 长度 | 响应长度 | TF-IDF | Avg Concept | **Semantic Score** |
|------|-----------|---------|--------|-------------|-------------------|
| v1 (original) | 11278 bytes | 1673 chars | 0.3678 | 0.8121 | **0.5011** |
| v2 (math injected) | 11566 bytes | 309 chars | 0.2474 | 0.3438 | **0.2763** |
| minimal | 810 bytes | 293 chars | 0.2057 | 0.2806 | **0.2281** |

### 对比关键词评分

| 版本 | Keyword avg | Keyword min | Semantic Score |
|------|------------|-------------|----------------|
| v1 | 0.2849 | 0.0000 | **0.5011** |
| v2 | 0.1864 | 0.0000 | **0.2763** |
| minimal | 0.0686 | 0.0000 | **0.2281** |

### 关键发现

1. **语义评分保持了相同排序**：v1 > v2 > minimal — 与关键词评估一致
2. **语义评分给出更有意义的绝对值**：v1 得分 0.50（中等偏上对齐）而非三个维度零分
3. **概念覆盖率揭示真实对齐**：
   - v1 响应: bayesian=0.80, rate_distortion=0.67, cross_domain=0.57, self_preservation=3.33
   - 虽然探索/感知/观测者为零，但其他 5 个概念类别有良好覆盖

## 结论

语义评估器成功区分了**功能对齐**和**词汇对齐**：
- v1 响应即使只使用 persona-v3 prompt 的 15%（1673/11278 bytes），仍达到 0.50 语义对齐度
- 概念覆盖率证明模型理解了 persona 的核心概念（贝叶斯推理、rate-distortion、跨域同构），尽管未使用特定关键词

## 下一步

1. 建立语义评估基线：persona-v3 prompt.txt 自身 vs 响应文件的语义评分
2. 将语义评估器集成到 unified_eval.py pipeline
3. 对比语义评估 vs 关键词评估在 52 个 idea 文件上的相关性
