---
name: Optimal distance export — Fisher-Rao universality theorem (iter 73)
description: DistCat 最优距离导出 — 证明 Fisher-Rao 是唯一最优预距离，所有 5 个特例统一
type: reference
---

## iteration 73 结果

### 核心定理

**定理 3.1 (Fisher-Rao universality theorem)**:
对于 DistCat 基础结构 $\mathcal{B}$，如果观察函子 $\mathcal{O}$ 将 $\mathbf{C}$ 映射到指数族（或其数学类比：线性扰动结构的光滑参数化族），则 Fisher-Rao 距离 $d_{\text{FR}}$ 是唯一最优预距离。

**证明关键**：
1. 定理 1.4：Fisher-Rao 是唯一使数据处理的 KL 不等式取等号的度量 (Amari 唯一性)
2. 引理 1.2：Fisher-Neyman 因子分解定理 → 最优预距离 $\Gamma^*$ 满足 $\delta = f(\Gamma^*)$
3. 定理 3.1：唯一性证明 — 任何其他最优 $\Gamma'$ 等价于 $d_{\text{FR}}$ 至多一个缩放因子

### 5 个特例的统一解释

| 特例 | 参数空间 | Fisher-Rao 度量 | 导出距离 δ |
|------|---------|----------------|------------|
| D16+D24 | 统计模型参数 $\sigma$ | 费雪度量 $g_F$ | KL 散度 $D_{\text{KL}}$ |
| Bayesian | 先验参数 $\theta$ | 费雪-拉奥距离 | 后验 KL 散度 |
| D26 | LTI 系统矩阵 A | 特征值空间欧氏距离 | 共振放大 $G_{\text{amp}}$ |
| EMRI | 暗晕参数 $(\rho_s, r_s)$ | $L^2$ 度规扰动 | Lyapunov 指数 $\lambda_T$ |
| D1-grav-waves | AQFT 代数态 | 高斯态 Bures 距离 | HD 相关 $\zeta(\theta)$ |

### 相关文献

- Amari 1985: 信息几何基础
- Cencov 1982 / Chentsov 1972: Fisher-Rao 唯一性定理
- Petz 1996: 量子单调度量唯一性
- Menicucci 2014: 高斯态 Bures = Fisher-Rao

### 文件
- papers/DISTCAT-optimal-distance-export.md: 155 行理论论文
- 统一框架 Sec.9.4 标记 #4 完成
- TASKS.md / INDEX.md 同步更新
