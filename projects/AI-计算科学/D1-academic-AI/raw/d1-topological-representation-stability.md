# D1-2: 拓扑等价类-泛化稳定性猜想

## 来源
转化自：
- raw/math.md (2): 同调群的几何直观

## 核心猜想

**拓扑等价类-泛化稳定性定理（猜想）**：设 $f_\theta$ 为深度学习模型，其中间层表征为点云 $\mathcal{P}_\theta \subset \mathbb{R}^d$。计算其持久同调的Betti数字 $\beta_k(\mathcal{P}_\theta)$。

**猜想**：$\beta_1$（1-循环数）与OOD泛化间隙 $\Delta_G$ **单调相关**——高 $\beta_1$ 对应高 $\Delta_G$（拓扑复杂性高的表征更脆弱）。

## 物理直觉

- $\beta_0$ = 连通分量数（数据集中在几个簇中）
- $\beta_1$ = 环/循环数（**这是关键**：环形结构意味着"近邻不近"）
- $\beta_2$ = 空腔数

**为什么 $\beta_1$ 预测OOD泛化？**
环形结构在拓扑上意味着：在表征空间中距离相近的点，在语义上可能属于不同类别。这正是OOD崩溃的本质——最近邻检索失效。

## 可验证性

1. **训练规模扫掠**：训练不同规模的Transformer，跟踪中间层 $\beta_1$ 与OOD误差
2. **数据增强对照**：对比有/无数据增强的 $\beta_1$ 演化
3. **理论连接**：将 $\beta_1$ 与D9-I中的 $\Delta_G$ 建立不等式关系

## 与已有研究的差异

TDA在AI中的应用（Mileyko et al., 2019; Sun et al., 2021）主要用于**特征提取**——用Betti数字作为输入。**这是首次提出用拓扑复杂性作为表征质量的度量**，而非特征。

## 关键方法论问题

1. 持久同调的"条带长度"（persistence length）是否比简单的 $\beta_1$ 更有判别力？
2. 不同层级的 $\beta_k$ 演化是否有不同的语义意义？
3. 能否用拓扑统计量设计新的正则化项？

---
*Created: 2026-04-29 | Status: Conjecture — Requires TDA analysis of neural network representations*
