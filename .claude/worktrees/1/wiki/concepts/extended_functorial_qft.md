# Extended Functorial QFT (EFQFT)

## 概述

Extended Functorial Quantum Field Theory 是将传统函子型 QFT 扩展到流形所有维度子结构的推广框架。

## 核心数学结构

### 基础框架（Atiyah-Segal）
- **标准 functorial QFT**：从 n-维 cobordism 范畴 Cob_n 到向量空间范畴 Vect 的对称单值函子
- Cob_n 的对象：(n-1)-维闭流形；态射：n-维 cobordism（带边流形）
- 公理：函子性（cobordism 组合 → 算符复合）、对称性（流形直和 → 张量积）

### Extended 推广（Baez-Dolan, Lurie）
- **Extended QFT**：不仅对全维流形定义，还对任意维度子流形（包括点、曲线、曲面）定义数据
- 数学表述：从 extended cobordism ∞-范畴到 ∞-范畴的 n-函子
- 关键：在 k-维子流形上定义 k-向量空间（而非仅在 (n-1)-维闭流形上定义向量空间）

### Schreiber 的统一（arXiv:0806.1079）
- AQFT（代数 QFT）与 n-functorial QFT 的统一框架
- 核心：从时空范畴（Lorentzian 流形 + 因果嵌入）到代数范畴的函子
- **关键创新**：将局部协变性（local covariance）表述为自然变换

## 与引力波检测的关联

### PTA 建模
- N 颗脉冲星 → N 条世界线（1-维子流形）
- 每颗脉冲星的计时残差 → 在该世界线上的标量场数据
- Hellings-Downs 相关性 → 不同世界线之间的关联函数
- Extended Functorial QFT 框架：F(Σ_i) = 脉冲星 i 的希尔伯特空间，F(W_ij) = 从脉冲星 i 到 j 的传播子

### 干涉仪建模
- LIGO/Virgo/KAGRA 的臂 → 光线的零测地线（1-维子流形）
- 引力波扰动 → 度规变化 δg_μν，影响光程差
- Extended Functorial QFT 框架：F(arm) = 干涉仪的量子态空间，F(cobordism) = 引力波传播算符

### 关键洞察
- Extended Functorial QFT 提供了一个统一的框架，可以同时描述 PTA（长基线、低频）和干涉仪（短基线、高频）的引力波检测
- 不同尺度的探测器对应于不同维度的子流形上的数据
- **创新潜力**：用 Extended Functorial QFT 的函子性，可以严格推导不同探测器之间的关联关系

## 三条可行路径对比

| 路径 | 数学成熟度 | 与观测的联系 | 创新潜力 | 工作量 |
|------|-----------|------------|---------|--------|
| A: 引力子作为态 | 中（Euclidean 成熟，Lorentzian 发展中） | 高（直接计算传播振幅） | 高 | 大 |
| B: 局部协变扩展 | 高（已有 AQFT 框架） | 中高（可推导 GW 传播方程） | 中 | 中 |
| C: Extended + 自旋泡沫 | 低（高度理论化） | 低（远离观测） | 极高 | 极大 |

## 核心挑战
- Extended Functorial QFT 目前主要在 Euclidean 背景下发展
- Lorentzian 时空的 extended functorial QFT 表述仍在发展中（Schreiber 2008 部分处理）
- **具体挑战**：Lorentzian cobordism 的范畴结构比 Euclidean 更复杂（因果结构、时间定向）

## 状态
- [x] 理解基本定义和数学框架
- [ ] 深入阅读 Schreiber (0806.1079) AQFT 统一框架
- [ ] 研究 Brunetti-Fredenhagen-Verch (1105.6202) 局部协变扩展
- [ ] 探索 Lorentzian cobordism 的最新进展

## 相关概念
- [[AQFT]]
- [[Cobordism]]
- [[Lorentzian Cobordism]]
- [[局部协变性]]

## 关键参考文献
1. **Atiyah (1988)** — "Topological quantum field theories"
2. **Baez & Dolan (1995)** — "From finite sets to Feynman diagrams"
3. **Lurie (2009)** — "On the classification of topological field theories"
4. **Schreiber (0806.1079)** — "AQFT from n-functorial QFT"
5. **Brunetti, Fredenhagen & Verch (1105.6202)** — 局部协变性的范畴论表述
