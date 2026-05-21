# D26 共振距离导出

> **创建**: iteration 59
> **来源**: D26 微扰放大理论与控制系统的 $\mathbf{DistCat}$ 规范表述
> **类型**: 应用案例 — 控制系统的范畴论表述

## 0. D26 核心理论回顾

D26 的核心是**共振放大理论**：
- **共振频率**：$\omega_{res} = \arg\max_\omega \|G(j\omega)\|_2$
- **临界行为**：$G_{AMP} \sim \epsilon^{-\gamma}$，$\epsilon = \min_i |\text{Re}(\lambda_i)|$
- **H∞ 鲁棒性**：$\mathcal{R} = 1/\|T_{zw}\|_\infty$

这些概念在 $\mathbf{DistCat}$ 框架下有自然的距离导出表述。

## 1. D26 作为 $\mathbf{DistCat}$ 特例

**命题 1.1（D26 ∈ $\mathbf{DistCat}$）**：

设 $\mathcal{B}_{\text{D26}} = (\mathbf{C}_{\text{D26}}, \mathcal{F}_{\text{D26}}, \mathcal{O}_{\text{D26}})$，其中：

### 1.1 源范畴 $\mathbf{C}_{\text{D26}}$（控制系统范畴）

**定义 1.1（控制系统范畴）**：
$\mathbf{C}_{\text{D26}}$ 是一个 1-范畴（非 2-范畴），其：
- **0-对象**：线性时不变（LTI）系统 $S = (A, B, C, D)$，即 $\dot{x} = Ax + Bu, \quad y = Cx + Du$
- **1-态射**：系统间同态 $(\Psi, \Phi)$，其中 $\Psi$ 为状态空间同构，$\Phi$ 为输入输出同构
- **约束**：$(A, B, C, D)$ 与 $(A', B', C', D')$ 间存在同态当且仅当 $\exists P$ 可逆使 $A' = PAP^{-1}, B' = PBD^{-1}, C' = DC P^{-1}, D' = D$

**同态条件**：
$$\begin{pmatrix} A' & B' \\ C' & D' \end{pmatrix} = \begin{pmatrix} P & 0 \\ 0 & Q \end{pmatrix} \begin{pmatrix} A & B \\ C & D \end{pmatrix} \begin{pmatrix} P^{-1} & 0 \\ 0 & Q^{-1} \end{pmatrix}$$

### 1.2 结构函子 $\mathcal{F}_{\text{D26}}$（共振放大函子）

**定义 1.2（共振放大函子）**：
$$\mathcal{F}_{\text{D26}}: \mathbf{C}_{\text{D26}} \to \mathbf{Spectrum}$$
$$\mathcal{F}_{\text{D26}}(A, B, C, D) = G(s) = C(sI - A)^{-1}B + D$$

其中 $\mathbf{Spectrum}$ 是有理传递函数范畴。

**性质**：$\mathcal{F}_{\text{D26}}$ 保持系统串联（串联系统的传递函数 = 传递函数乘积）。

### 1.3 观测函子 $\mathcal{O}_{\text{D26}}$（共振观测）

**定义 1.3（共振观测函子）**：
$$\mathcal{O}_{\text{D26}}(A, B, C, D) = (\omega_{res}, G_{AMP}(\omega_{res}))$$

即观测值为共振频率和共振增益对。

### 1.4 距离导出

**原距离 $\Gamma$**（极点扰动距离）：
$$\Gamma((A_1, B_1, C_1, D_1), (A_2, B_2, C_2, D_2)) = \max_i |\lambda_i(A_1) - \lambda_i(A_2)|$$

即系统矩阵特征值的最大扰动距离。

**导出距离 $\delta$**（共振放大距离）：
$$\delta((\omega_{r1}, G_1), (\omega_{r2}, G_2)) = |\omega_{r1} - \omega_{r2}| + \left|\frac{1}{G_1} - \frac{1}{G_2}\right|$$

其中 $1/G$ 为鲁棒性度量（与 D26-5 H∞ 鲁棒性一致）。

**自然变换 $\eta$**：
$$\eta: \delta(\mathcal{O}(S_1), \mathcal{O}(S_2)) \Rightarrow \Gamma(S_1, S_2)$$

即：**共振观测距离的上界由极点扰动距离控制**。

## 2. D26 定理在 $\mathbf{DistCat}$ 中的表述

### 2.1 共振频率与极点距离

**定理 2.1（共振频率灵敏度）**：
设 $S_\epsilon = (A + \epsilon \delta A, B, C, D)$ 为受扰系统，$\omega_{res}(S_\epsilon)$ 为共振频率。则：
$$\lim_{\epsilon \to 0} \frac{|\omega_{res}(S_\epsilon) - \omega_{res}(S)|}{\epsilon} \leq \max_i \frac{|\lambda_i(A + \epsilon \delta A) - \lambda_i(A)|}{\epsilon} = \kappa_\lambda(\delta A)$$

其中 $\kappa_\lambda$ 为特征值灵敏度（与 D26-1 微扰灵敏度定理一致）。

**在 $\mathbf{DistCat}$ 中**：$\kappa_\lambda$ 是 $\eta$ 的局部 Lipschitz 常数——控制共振观测距离相对于原距离的放大率。

### 2.2 临界放大与 $\mathbf{DistCat}$ 不变量

**定理 2.2（临界放大上界）**：
设系统 $S = (A, B, C, D)$ 接近临界点，$\epsilon = \min_i |\text{Re}(\lambda_i(A))|$ 为到临界点的距离。则：
$$G_{AMP}(S) \leq \frac{\|C\| \cdot \|B\|}{\epsilon}$$

**在 $\mathbf{DistCat}$ 中**：$G_{AMP}$ 是 $\mathcal{O}_{\text{D26}}(S)$ 的不变量，$\epsilon$ 是 $\Gamma$ 的不变量。定理表明 $G_{AMP} \leq f(\epsilon)$ 对某个函数 $f$ 成立——这正是 $\eta$ 作为上界的性质。

### 2.3 鲁棒性与距离导出

**定理 2.3（鲁棒性作为距离导出）**：
由 D26-5，$\mathcal{R}(S) = 1/\|T_{zw}(s)\|_\infty$。在 $\mathbf{DistCat}$ 框架下：
$$\mathcal{R}(S) = \frac{1}{\delta(\mathcal{O}(S), \mathcal{O}_{\text{critical}})}$$

其中 $\mathcal{O}_{\text{critical}} = (\omega_{crit}, \infty)$ 为临界观测（共振增益发散）。

**物理含义**：鲁棒性 = 到临界观测的距离的倒数。这与 D26 的 H∞ 鲁棒性边界完全等价，但以距离导出的形式表述。

## 3. D26 共振距离导出原理

**定义 3.1（共振距离导出原理）**：
在 D26 中，距离导出原理的表述为：
> **共振放大距离 = 极点扰动距离的函数**

即 $\delta(\omega_{res}, G_{AMP}) = f(\Gamma(\lambda_1, \dots, \lambda_n))$，其中 $f$ 由 D26-2 共振峰位置定理和 D26-3 临界幂律确定。

### 3.1 共振距离导出 vs 信息几何距离导出

| 属性 | D26 共振距离导出 | D16+D24 信息几何距离导出 |
|---|---|---|
| 基础结构 | LTI 控制系统 | Fisher 信息流形 |
| 原距离 | 极点扰动距离 $\Gamma$ | Fisher-Rao 距离 $\Gamma$ |
| 导出距离 | 共振放大距离 $\delta$ | 语义测地线 $\delta$ |
| 关键函数 | 传递函数 $G(s)$ | 统计模型 $p(x|\sigma)$ |
| 临界行为 | 极点趋近虚轴 | 曲率趋近零 |

### 3.2 统一的距离导出原理

**定理 3.2（统一距离导出原理）**：
设 $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$ 为任意基础结构。存在通用的距离导出函子 $D: \mathbf{DistCat} \to \mathbf{Met}$，使得：
- $D(\mathcal{B}) = (\mathcal{O}(\text{Obj}(\mathbf{C})), \delta)$
- $\delta(\mathcal{O}(X), \mathcal{O}(Y)) = \Phi(\Gamma(X, Y))$ 对某个函数 $\Phi$

**D26 特例**：$\Phi = f_{\text{resonance}}$（共振放大函数，由传递函数极点位置决定）
**D16+D24 特例**：$\Phi = \frac{1}{2} \cdot (\cdot)^2$（Amari 二次近似）
**D1-grav-waves 特例**：$\Phi = f_{\text{AQFT}}$（函子赋值函数）

## 4. 跨框架统一：所有特例的距离导出统一

**命题 4.1（距离导出统一性）**：
D1-grav-waves、D16+D24、bayesian-frame、D26 共享同一个距离导出原理，区别仅在于 $\Phi$ 的具体形式：

$$\begin{array}{c|c|c}
\text{框架} & \Gamma & \Phi \\
\hline
\text{D1-grav-waves} & d_{TV} & \text{HD 相关性函数} \\
\text{D16+D24} & d_{FR} & \frac{1}{2}x^2 \text{（Amari 近似）} \\
\text{bayesian-frame} & d_{FR} & D_{KL} \text{（边际化）} \\
\text{D26} & \Gamma_{\text{pole}} & f_{\text{resonance}} \text{（传递函数）}
\end{array}$$

**核心洞察**：距离导出原理的统一不取决于基础结构的形式（物理理论、统计模型、控制系统），而取决于**距离导出函子 $D$ 的范畴论结构**——所有框架共享同一个 2-范畴 $\mathbf{DistCat}$，距离导出是该范畴的内在性质。

## 5. 待完成

- [ ] 严格证明定理 2.1（共振频率灵敏度）
- [ ] 严格证明定理 2.3（鲁棒性作为距离导出）
- [ ] 计算 D26 与其他 $\mathbf{DistCat}$ 特例的距离等价性
- [ ] 将 bayesian-frame 鲁棒性理论 (D26-5) 与 bayesian-frame 先验优化结合
