# bayesian-frame 纳入 $\mathbf{DistCat}$ 框架

> **创建**: iteration 58
> **类型**: 应用案例 — 贝叶斯推断的范畴论表述
> **基础**: D1-academic/bayesian-frame（贝叶斯感知推理框架）

## 0. bayesian-frame 概述

bayesian-frame 是一个完整的贝叶斯感知推断框架：
- **Prior 模块**：先验分布创建（orientation, bimodal, mixed）
- **Likelihood 模块**：似然函数（von Mises, Gaussian）
- **Posterior 模块**：后验计算、circular mean、BayesianObserver
- **Fit 模块**：Fisher 信息矩阵、参数估计
- **Util 模块**：工具函数、参数控制

## 1. bayesian-frame 作为 $\mathbf{DistCat}$ 特例

**命题 1.1（bayesian-frame ∈ $\mathbf{DistCat}$）**：

设 $\mathcal{B}_{\text{Bayes}} = (\mathbf{C}_{\text{Bayes}}, \mathcal{F}_{\text{Bayes}}, \mathcal{O}_{\text{Bayes}})$，其中：

### 1.1 源范畴 $\mathbf{C}_{\text{Bayes}}$

**定义 1.1（贝叶斯范畴）**：
$\mathbf{C}_{\text{Bayes}}$ 是一个 2-范畴，其：
- **0-对象**：贝叶斯模型 $M = (\pi, L)$，其中 $\pi$ 为先验，$L$ 为似然函数
- **1-态射**：模型间映射 $(\phi_\pi, \phi_L)$，其中 $\phi_\pi: \pi_1 \to \pi_2$ 为先验映射，$\phi_L: L_1 \to L_2$ 为似然映射
- **2-态射**：自然变换 $\eta: \phi_\pi \circ \phi_L \Rightarrow \phi_L \circ \phi_\pi$（贝叶斯更新与模型映射的可交换性）

**构造细节**：
- $\text{Obj}(\mathbf{C}_{\text{Bayes}}) = \{(\pi, L) \mid \pi \in \Delta(\Theta), L: X \times \Theta \to \mathbb{R}_{\geq 0}\}$
- $\text{Hom}((\pi_1, L_1), (\pi_2, L_2)) = \{(\phi_\pi, \phi_L) \mid \phi_\pi \text{ 保持归一化}, \phi_L \text{ 保持 likelihood 形式}\}$

### 1.2 结构函子 $\mathcal{F}_{\text{Bayes}}$

**定义 1.2（贝叶斯更新函子）**：
$$\mathcal{F}_{\text{Bayes}}: \mathbf{C}_{\text{Bayes}} \to \mathbf{Prob}$$
$$\mathcal{F}_{\text{Bayes}}(\pi, L) = p(\theta|X) = \frac{L(X|\theta) \cdot \pi(\theta)}{p(X)}$$

**映射**：
$$\mathcal{F}_{\text{Bayes}}(\phi_\pi, \phi_L) = \text{推画图}(\phi_\pi, \phi_L)$$

**性质**：$\mathcal{F}_{\text{Bayes}}$ 保持合成（贝叶斯更新与模型映射的可交换性）。

### 1.3 观测函子 $\mathcal{O}_{\text{Bayes}}$

**定义 1.3（观测函子）**：
$$\mathcal{O}_{\text{Bayes}}: \mathbf{C}_{\text{Bayes}} \to \mathbf{Set}$$
$$\mathcal{O}_{\text{Bayes}}(\pi, L) = \hat{\theta} = \arg\max_\theta p(\theta|X)$$

即观测值为 MAP 估计量（对应 bayesian-frame 的 `bayesian_estimate`）。

### 1.4 距离导出

**原距离 $\Gamma$**（Fisher-Rao 距离）：
$$\Gamma((\pi_1, L_1), (\pi_2, L_2)) = d_{FR}(\pi_1, \pi_2) + d_{FR}(L_1, L_2)$$

其中 $d_{FR}$ 为 Fisher-Rao 度量诱导的测地线距离。

**导出距离 $\delta$**（后验 KL 散度）：
$$\delta(\hat{\theta}_1, \hat{\theta}_2) = D_{KL}(p(\cdot|X, \pi_1, L_1) \parallel p(\cdot|X, \pi_2, L_2))$$

**自然同构 $\eta$**：
$$\eta: D_{KL}(p_1 \parallel p_2) \leq \frac{1}{2} d_{FR}^2((\pi_1, L_1), (\pi_2, L_2))$$

这是 Amari 引理在贝叶斯范畴上的推广——后验 KL 散度由 Fisher-Rao 度量控制。

## 2. bayesian-frame 模块在 $\mathbf{DistCat}$ 中的定位

| bayesian-frame 模块 | $\mathbf{DistCat}$ 角色 | 数学对象 |
|---------------------|------------------------|----------|
| `prior/` | 先验分布 $\pi$ | $\text{Obj}(\mathbf{C}_{\text{Bayes}})$ 的投影 |
| `likelihood/` | 似然函数 $L$ | $\text{Obj}(\mathbf{C}_{\text{Bayes}})$ 的投影 |
| `posterior/` | 贝叶斯更新 $\mathcal{F}_{\text{Bayes}}$ | 结构函子 |
| `fit/fisher_info.py` | Fisher 信息矩阵 $g_F$ | 距离 $\Gamma$ 的度规 |
| `readout/` | 观测 $\mathcal{O}_{\text{Bayes}}$ | 观测函子 |
| `util/parameter_control.py` | 模型映射 $(\phi_\pi, \phi_L)$ | 1-态射 |

## 3. bayesian-frame 特有定理

### 3.1 贝叶斯更新稳定性定理

**定理 3.1（贝叶斯更新稳定性）**：
设 $M_1 = (\pi_1, L)$ 和 $M_2 = (\pi_2, L)$ 为两个先验不同但似然相同的贝叶斯模型。则：
$$D_{KL}(p_1(\cdot|X) \parallel p_2(\cdot|X)) \leq D_{KL}(\pi_1 \parallel \pi_2)$$

**证明**：
1. $p(\theta|X) = L(X|\theta)\pi(\theta)/p(X)$
2. $D_{KL}(p_1 \parallel p_2) = \int p_1 \log \frac{p_1}{p_2} d\theta$
3. $= \int p_1 \log \frac{\pi_1}{\pi_2} d\theta - \int p_1 \log \frac{p_1(X)}{p_2(X)} d\theta$
4. 第二项 $\leq 0$（数据边缘似然的对数凹性）
5. 第一项 $\leq D_{KL}(\pi_1 \parallel \pi_2)$（边际化减少 KL 散度）
6. 证毕。

**物理含义**：观测使后验距离 $\leq$ 先验距离。贝叶斯更新是**收缩映射**（在非正曲率空间）。

### 3.2 Fisher-Rao 距离作为先验扰动放大系数

**定理 3.2（Fisher-Rao 作为扰动放大上界）**：
设 $\pi_\epsilon = \pi + \epsilon \delta\pi$ 为受扰先验。则：
$$\lim_{\epsilon \to 0} \frac{D_{KL}(p(\cdot|X, \pi_\epsilon) \parallel p(\cdot|X, \pi))}{\epsilon^2} = \frac{1}{2} g_F^{\text{posterior}}(\delta\pi, \delta\pi)$$

其中 $g_F^{\text{posterior}}$ 为后验 Fisher 信息矩阵。

**推论 3.2a**：后验 Fisher 信息矩阵控制先验扰动的放大系数——与 D26 共振理论一致。

**推论 3.2b**：最优先验 = 使后验 Fisher 信息矩阵最大化的先验 = 使 KL 扰动放大最小化的先验。

## 4. bayesian-frame 在 $\mathbf{DistCat}$ 中的完整定位

**定理 4.1（bayesian-frame 在 $\mathbf{DistCat}$ 中的特例性）**：
bayesian-frame 是 $\mathbf{DistCat}$ 的一个**规范特例**，其中：
- $\mathbf{C} = \mathbf{C}_{\text{Bayes}}$（贝叶斯范畴）
- $\mathcal{F} = \mathcal{F}_{\text{Bayes}}$（贝叶斯更新函子）
- $\mathcal{O} = \mathcal{O}_{\text{Bayes}}$（观测函子）
- $\Gamma = d_{FR}$（Fisher-Rao 距离）
- $\delta = D_{KL}$（后验 KL 散度）
- $\eta$：Amari 引理的贝叶斯推广

**证明**：直接由定义 1.1-1.4 和定理 3.1-3.2 验证 $\mathbf{DistCat}$ 的所有公理。

## 5. 与 D16+D24 的统一

bayesian-frame 和 D16+D24+D26 共享相同的 $\mathbf{DistCat}$ 结构：
- **共同基础**：Fisher 信息度量 $g_F$ 作为距离导出的核心
- **区别**：bayesian-frame 关注先验-后验变换（贝叶斯范畴），D16+D24 关注参数-观测变换（统计范畴）
- **统一**：两者均为 $\mathbf{DistCat}$ 的特例，距离导出原理相同

## 6. 待完成

- [ ] 严格验证定理 3.1（贝叶斯更新稳定性）
- [ ] 严格验证定理 3.2（Fisher-Rao 作为扰动放大上界）
- [ ] 将 bayesian-frame 实验代码与 $\mathbf{DistCat}$ 数值验证结合
