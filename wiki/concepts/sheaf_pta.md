# 层论在 PTA 数据分析中的应用

## 概述

细胞层/余层（Cellular Sheaves/Cosheaves）在脉冲星计时阵列数据分析中的潜在应用。

## 核心思想
- **细胞层**：在胞腔复形上定义的层，每个胞腔关联一个向量空间，包含映射描述数据在胞腔间的传递
- **层上同调**：量化了数据的全局一致性约束
- Hellings-Downs 相关性可表述为层的相容性条件

## PTA 建模
- N 颗脉冲星 → N 个胞腔（顶点）
- 每颗脉冲星的计时残差 → 该胞腔上的层数据
- Hellings-Downs 相关性 → 不同脉冲星之间的映射（边的结构）
- **创新点**：层上同调可检测 HD 相关性的全局一致性

## 关键论文
- Ghrist (2013) — arXiv:1303.3255 "Sheaves, Cosheaves and Applications"
- 2025 (arXiv:2502.15476) — "Sheaf theory: from deep geometry to deep learning"
- 2025 (arXiv:2504.08095) — "Sheaf Topos Theory: A powerful setting for Lagrangian Field Theory"

## 研究空白
- **最大空白**：层上同调检测 HD 相关性——这是一个全新的研究方向
- 成熟度：★★☆☆☆（概念新颖）

## 状态
- [x] 理解层论基本概念
- [ ] 设计 PTA 数据的层结构建模方案
- [ ] 探索层上同调检测 HD 相关性的具体算法

## 相关概念
- [[拓扑斯理论]]
- [[Extended Functorial QFT]]
