# SimPersona: Behavioral Trajectory Clustering for Persona Learning

**来源**: arXiv 2025
**相关度**: 极高相关

## 摘要

从原始行为数据 (clickstream) 学习离散买家 persona。通过 K-means 聚类行为轨迹 → 生成 persona cluster → 训练专用代理。无需人工定义 persona。

## 核心方法

1. 收集用户行为数据 (点击序列)
2. K-means 聚类行为轨迹
3. 生成 persona cluster profile
4. 训练专用代理匹配每个 persona

## 对 persona-v3 的启示

- **learned vs defined persona**: SimPersona 代表"learned persona"路径 — 从数据自动学习 persona。persona-v3 定位为 **"唯一不依赖训练的 prompt-based adaptive persona 框架"**
- **prompt 层 vs 行为层**: persona-v3 在 prompt 层实现自适应, 而 SimPersona 在行为层学习 persona

## 与 persona-v3 的关系

persona-v3 的 6 维度可以被理解为 SimPersona 的 prompt 层等价物:
- K-means 聚类 = persona-v3 的维度分布
- Persona cluster = persona-v3 的维度组合

## 参考

论文: SimPersona — 从行为轨迹学习离散 persona (见 iteration-170)
