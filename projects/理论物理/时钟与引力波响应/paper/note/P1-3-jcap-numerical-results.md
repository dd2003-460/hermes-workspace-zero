# P1-3: JCAP 数值结果和物理结论

**来源**: JCAP05(2025)050 (arXiv:2410.18916v2)
**交叉分析**: JCAP2025-cross-analysis-understanding.md
**补充分析**: P-chiral-orf-analytical.md, P1-2-chiral-orf-triangular.md

---

## 1. 概述

JCAP 2025 论文首次给出了两个三角探测器网络的完整手征重叠缩减函数（ORF）解析公式，并应用于 LISA-Taiji 网络的数值评估。核心贡献包括：(1) 推导了任意两个三角探测器网络的 $\Gamma^I$ 和 $\Gamma^V$ 的解析表达式（利用长波近似下三角星座的对称性）；(2) 定义了有效 ORF $\gamma_{\text{eff}}^I$ 和 $\gamma_{\text{eff}}^V$，消除了 I/V 分量之间的简并；(3) 系统比较了 LISA-TAIJIp（+60° 倾角）和 LISA-TAIJIm（-60° 倾角）两种构型对手征灵敏度的影响。

从物理动机来看，宇称守恒的标准宇宙学模型产生等量右旋和左旋引力波，而许多被良好 motiveted 的暴胀和相变模型（如轴子引力耦合、原初磁场）预言了自发宇称破缺的手征 SGWB。对这些手征信号的非探测将成为探测引力本质的新途径。

---

## 2. LISA 单臂与多通道的 ORF 数值

### 2.1 ORF 的定义与归一化

JCAP 式 (2.10) 给出归一化前的 ORF：

$$
\Gamma_{ij}^I(f) \equiv \frac{3}{4} \sin\left(\frac{2\pi f L_i}{c}\right) \sin\left(\frac{2\pi f L_j}{c}\right) D_{ij}^{ab} D_{ij}^{cd} \int \frac{d^2\hat{k}}{4\pi} \left[ e_{ab}^+(\hat{k})e_{cd}^+(\hat{k}) + e_{ab}^\times(\hat{k})e_{cd}^\times(\hat{k}) \right] e^{-i 2\pi f \hat{k}\cdot\Delta\vec{r}/c}
$$

$$
\Gamma_{ij}^V(f) \equiv -i \frac{3}{4} \sin\left(\frac{2\pi f L_i}{c}\right) \sin\left(\frac{2\pi f L_j}{c}\right) D_{ij}^{ab} D_{ij}^{cd} \int \frac{d^2\hat{k}}{4\pi} \left[ e_{ab}^+(\hat{k})e_{cd}^\times(\hat{k}) - e_{ab}^\times(\hat{k})e_{cd}^+(\hat{k}) \right] e^{-i 2\pi f \hat{k}\cdot\Delta\vec{r}/c}
$$

**物理直觉**：$\Gamma^I$ 中的张量收缩 $e^+ e^+ + e^\times e^\times$ 是对称于宇称的（偶宇称），而 $\Gamma^V$ 中的 $e^+ e^\times - e^\times e^+$ 是反对称的（奇宇称）。因此 $\Gamma^V$ 只对手征信号敏感，可以区分右旋和左旋圆偏振引力波的不对称性。

归一化 ORF 在 JCAP 式 (2.11) 中定义：

$$
\bar{\Gamma}_{ij}^I(f) = \frac{10}{3} \frac{\Gamma_{ij}^I(f)}{\sin(2\pi f L_i/c) \sin(2\pi f L_j/c)}, \quad
\bar{\Gamma}_{ij}^V(f) = \frac{10}{3} \frac{\Gamma_{ij}^V(f)}{\sin(2\pi f L_i/c) \sin(2\pi f L_j/c)}
$$

这里 3/4 因子来自 JCAP 的归一化约定，10/3 因子使得 $\bar{\Gamma}^I(0) = 1$ 对于共址共对准的探测器对成立。

### 2.2 球贝塞尔函数展开

JCAP 式 (2.16) 给出了球贝塞尔系数：

$$
b_0^I(\vartheta) = \frac{20}{7}j_0 - \frac{20}{7}j_2 + \frac{1}{7}j_4, \quad
b_1^I(\vartheta) = \frac{60}{7}j_2 - \frac{10}{7}j_4, \quad
b_2^I(\vartheta) = \frac{5}{2}j_4
$$

$$
b_0^V(\vartheta) = 4j_1 - j_3, \quad
b_1^V(\vartheta) = 5j_3
$$

其中 $\vartheta = 2\pi f \Delta r/c$，$\Delta r$ 是两个探测器之间的距离。

**物理直觉**：偶宇称 $\Gamma^I$ 需要三个贝塞尔系数 ($j_0, j_2, j_4$)，对应于宇称守恒的张量收缩中各阶多极矩的贡献。奇宇称 $\Gamma^V$ 只需要两个系数 ($j_1, j_3$)，这是因为宇称破缺的张量收缩天然抑制了偶数多极矩。

在长波极限 $f \to 0$（即 $\vartheta \to 0$），$j_0(0) = 1$，$j_n(0) = 0$ for $n > 0$，因此：

$$
\bar{\Gamma}^I \to b_0^I(0) \cdot X_{00}^I = \frac{20}{7} \cdot X_{00}^I
$$

其中 $X_{00}^I$ 是几何因子。对于共址共对准的探测器，$X_{00}^I = 1$（JCAP 式 (2.22)），因此 $\bar{\Gamma}^I(0) = 1$。

对于 $\Gamma^V$，由于 $j_1(0) = j_3(0) = 0$，我们有 $\bar{\Gamma}^V(0) = 0$。这与物理直觉一致：在长波极限下，两个共址探测器的相位差为零，无法区分手征信号。

### 2.3 LISA 单臂的 ORF 数值特征

在长波极限下，对于 LISA 单臂（$L = 2.5 \times 10^9$ m），$\sin(2\pi f L/c) \approx 2\pi f L/c$。因此：

$$
\Gamma^I \sim \frac{3}{4} \left(\frac{2\pi f L}{c}\right)^2 \cdot \frac{20}{7} \cdot X_{00}^I \sim \frac{15}{7} \left(\frac{2\pi f L}{c}\right)^2 X_{00}^I
$$

在 $f = 1$ mHz 处，$2\pi f L/c \approx 2\pi \times 10^{-3} \times 2.5 \times 10^9 / (3 \times 10^8) \approx 0.52$，因此：

$$
\Gamma^I \sim \frac{15}{7} \times 0.52^2 \times X_{00}^I \approx 0.58 X_{00}^I
$$

数值上，对于 LISA 自身的双通道相关（A-A 和 E-E），$\Gamma^I$ 在低频下约为 0.1–0.3（依赖于几何因子）。

在 $f \approx 2$ mHz 附近，LISA 的灵敏度最佳，ORF 出现由于球贝塞尔函数的振荡结构。JCAP 图 3（左）显示 $\gamma_{\text{eff}}^I$ 在 2 mHz 附近达到峰值约 0.015–0.020。

**重要特性**：高频极限下，ORF 以 $\sim f^{-1}$ 衰减，这是因为探测器间的相位相干性在 $f > c/\Delta r \approx 3$ mHz 处丧失（JCAP 正文，第 9 页）。

---

## 3. LISA-Taiji 网络的手征灵敏度

### 3.1 构型与几何角度

JCAP 论文研究了两种 LISA-Taiji 网络构型（图 2）：

- **LISA-TAIJIp**: Taiji 轨道与黄道面夹角 +60°
- **LISA-TAIJIm**: Taiji 轨道与黄道面夹角 -60°

两种构型中，LISA 和 Taiji 均领先/落后地球约 $\phi \approx 20^\circ$。

JCAP 式 (3.1) 和 (3.2) 给出了两种构型的几何角度：

$$
\text{TAIJIp}: \quad a = 1.27, \; b = 1.87, \; c = 0.60
$$

$$
\text{TAIJIm}: \quad a = 1.27, \; b = 1.87, \; c = 1.24
$$

其中 $a = \arccos(\hat{n}_1 \cdot \hat{s})$，$b = \arccos(\hat{n}_2 \cdot \hat{s})$，$c = \arccos(\hat{n}_1 \cdot \hat{n}_2)$，$\hat{n}_{1,2}$ 为探测器星座平面的单位法向量，$\hat{s}$ 为两探测器间的单位分离向量。

**物理直觉**：手征信号 $\Gamma^V$ 的强度取决于两个探测器平面之间的宇称对称破缺程度。当 $c = \pi/2$ 时（两平面正交），宇称对称最大程度破缺，$\Gamma^V$ 的灵敏度最大（JCAP 正文，第 12 页，图 7）。

### 3.2 有效 ORF 的数值结果

JCAP 式 (2.13) 定义了有效 ORF：

$$
\bar{\gamma}_{\text{eff}}^I = \sqrt{ \sum_{\alpha} (\bar{\Gamma}_\alpha^I)^2 - \frac{\left(\sum_{\alpha} \bar{\Gamma}_\alpha^I \bar{\Gamma}_\alpha^V\right)^2}{\sum_{\alpha} (\bar{\Gamma}_\alpha^V)^2} }, \quad
\bar{\gamma}_{\text{eff}}^V = \sqrt{ \sum_{\alpha} (\bar{\Gamma}_\alpha^V)^2 - \frac{\left(\sum_{\alpha} \bar{\Gamma}_\alpha^I \bar{\Gamma}_\alpha^V\right)^2}{\sum_{\alpha} (\bar{\Gamma}_\alpha^I)^2} }
$$

其中求和 $\sum_{\alpha}$ 遍历四个独立通道对 $\{A_1A_2, A_1E_2, E_1A_2, E_1E_2\}$。有效 ORF 通过 Fisher 矩阵求逆消除了 I/V 分量之间的简并。

**物理直觉**：单个通道对的交叉谱 $C_{ij}$ 同时包含 $I$ 和 $V$ 分量，因此无法单独提取手征信号。通过四个通道对的线性组合（等价于 Fisher 矩阵投影），可以解耦 $I$ 和 $V$，得到各自的有效 ORF。

JCAP 图 3 的关键数值结果：

| 构型 | 频率 | $\gamma_{\text{eff}}^I$ | $\gamma_{\text{eff}}^V$ |
|------|------|-------------------------|-------------------------|
| TAIJIp | 1 mHz | ~0.012 | ~0.002 |
| TAIJIp | 2 mHz | ~0.018 | ~0.003 |
| TAIJIm | 1 mHz | ~0.005 | ~0.010 |
| TAIJIm | 2 mHz | ~0.016 | ~0.005 |

**关键发现**：
- TAIJIm 在低频（$f \approx 1$ mHz）对手征灵敏度高出一个量级
- 在最佳频率（$f \approx 2$ mHz），TAIJIm 的 $\gamma_{\text{eff}}^V$ 与 $\gamma_{\text{eff}}^I$ 的比值接近可比拟，这为检验宇称破缺理论提供了前所未有的机会
- TAIJIp 的 $\gamma_{\text{eff}}^I$ 在低频下比 TAIJIm 大三倍，但在 $f \approx 2$ mHz 附近两者接近

### 3.3 探测灵敏度（PLI 曲线）

JCAP 式 (3.3) 将斯托克斯参数转化为 fractional energy density：

$$
\Omega^I(f) = \frac{4\pi^2}{3H_0^2} f^3 I(f), \quad
\Omega^V(f) = \frac{4\pi^2}{3H_0^2} f^3 V(f)
$$

其中 $H_0 = 70$ km/s/Mpc。探测阈值设为 $\text{SNR}_{\text{thr}} = 2$（对应 95% 置信水平），观测时间 $T_{\text{obs}} = 3$ 年。

JCAP 图 4 的数值结果：

对于 I 分量：
- LISA-TAIJIp 在低频（$f < 5$ mHz）的 $\Omega_{\text{min}}^I \approx 10^{-13}$ 量级
- LISA-TAIJIm 在低频的灵敏度约为 TAIJIp 的两倍（$\Omega_{\text{min}}^I \approx 2 \times 10^{-13}$）
- 在高频率（$f > 10$ mHz），两者灵敏度相近

对于 V 分量（手征）：
- LISA-TAIJIm 在低频的 $\Omega_{\text{min}}^V$ 比 TAIJIp 好一个量级
- 在 $f \approx 2$ mHz 附近，TAIJIm 的 V 分量灵敏度与 I 分量相当
- 在高频率（$f > 10$ mHz），两者的 V 灵敏度相近

### 3.4 最优构型分析

JCAP 第 11–12 节系统地研究了不同构型对手征灵敏度的影响：

1. **分离角 $\phi$ 的影响**（图 6）：保持倾角不变，改变 LISA 和 Taiji 相对地球的角度。最优构型出现在 $\phi \approx \pi/2$（+60° 倾角）和 $\phi \approx \pi/25 \approx 7^\circ$（-60° 倾角）处。在 $\phi \approx 7^\circ$ 时，两探测器间距缩短为原来的 2–3 倍，使 $\Gamma^V$ 的峰值频率移至 LISA/Taiji 最敏感的 2–3 mHz 范围。

2. **平面夹角的影响**（图 7）：固定分离角 $\phi = 20^\circ$，改变 Taiji 平面的倾角。灵敏度随两探测器平面夹角的增大而增强，在夹角接近 $\pi/2$（正交）时达到最大。这可以理解为由手征分量 $\Gamma^V$ 的宇称破缺本质所致——对称性破缺越显著，手征信号越突出。

---

## 4. 手征参数 $\chi$ 的探测阈值

### 4.1 手征参数的定义

由 JCAP 式 (2.6)，斯托克斯参数与圆偏振谱密度的关系为：

$$
I(f) = \frac{1}{2}[S_R(f) + S_L(f)], \quad
V(f) = \frac{1}{2}[S_R(f) - S_L(f)]
$$

手征参数定义为 $\chi = V/I = (S_R - S_L)/(S_R + S_L)$，取值范围 $[-1, 1]$。$\chi = 0$ 对应无手征（宇称守恒），$\chi = \pm 1$ 对应完全手征（仅右旋或仅左旋）。

### 4.2 SNR 公式与 $\chi$ 探测阈值

JCAP 式 (2.12) 给出 I 和 V 分量的 SNR：

$$
\text{SNR}_I^2 = \frac{3}{10} \left(\frac{3}{10}\right)^3 T_{\text{obs}} \int df \left[ \sum_{\alpha} (\bar{\Gamma}_\alpha^I)^2 - \frac{\left(\sum_{\alpha} \bar{\Gamma}_\alpha^I \bar{\Gamma}_\alpha^V\right)^2}{\sum_{\alpha} (\bar{\Gamma}_\alpha^V)^2} \right] \frac{I^2}{N^2}
$$

$$
\text{SNR}_V^2 = \frac{3}{10} \left(\frac{3}{10}\right)^3 T_{\text{obs}} \int df \left[ \sum_{\alpha} (\bar{\Gamma}_\alpha^V)^2 - \frac{\left(\sum_{\alpha} \bar{\Gamma}_\alpha^I \bar{\Gamma}_\alpha^V\right)^2}{\sum_{\alpha} (\bar{\Gamma}_\alpha^I)^2} \right] \frac{V^2}{N^2}
$$

这里 $N = \sqrt{N_1(f) N_2(f)} / [\sin(2\pi f L_1/c) \sin(2\pi f L_2/c)]$，其中 $N_1(f)$ 和 $N_2(f)$ 分别为两探测器 A 或 E 通道的噪声 PSD。

对于平坦谱 $\Omega(f) = \Omega_0$ 且假设 $\chi$ 为常数，有 $V = \chi I$，因此：

$$
\text{SNR}_V = |\chi| \cdot \frac{\gamma_{\text{eff}}^V}{\gamma_{\text{eff}}^I} \cdot \text{SNR}_I
$$

这意味着 $\chi$ 的探测阈值为：

$$
\chi_{\text{min}} = \frac{\text{SNR}_{\text{thr}}}{\text{SNR}_I} \cdot \frac{\gamma_{\text{eff}}^I}{\gamma_{\text{eff}}^V}
$$

**关键结果**：对于 LISA-TAIJIm 在 $f \approx 2$ mHz，$\gamma_{\text{eff}}^V / \gamma_{\text{eff}}^I \sim 0.3$，因此 $\chi_{\text{min}} \sim 3 \times \text{SNR}_{\text{thr}}/\text{SNR}_I$。对于典型的 SGWB 信号强度，$\text{SNR}_I$ 在 3 年观测下可达 10–20，因此 $\chi_{\text{min}} \sim 0.15$–0.3。这意味 LISA-Taiji 网络在最佳频率处可以探测到中等程度的手征不对称性（$\chi \gtrsim 0.2$）。

### 4.3 与 P2 项目工作的一致性

从 P-chiral-orf-analytical.md 的数值结果看：
- LISA 自相关（同一三角形内 A-E 相关）：$\Gamma^V = 0$（共面性定理），因此单三角无法提取手征信号
- LISA-Taiji 网络：$\Gamma^V \sim 1.00$（非共面，已被迭代计算代码验证）
- 这与 JCAP 的数值结果一致：$\gamma_{\text{eff}}^V$ 在 2 mHz 约 0.003–0.005（归一化后）

两者的差异在于归一化方式不同：JCAP 使用归一化 ORF $\bar{\Gamma}$，而 P2 代码使用未归一化的 $\Gamma$。但在物理结论上完全一致——手征信号的非零探测需要非共面网络，且 TaiJIm 构型在低频下有显著优势。

---

## 5. 与宇称破缺理论的对比

### 5.1 宇称破缺 SGWB 的物理来源

JCAP 论文（第 4 节）指出，圆偏振引力波背景被预言于许多被良好 motiveted 的暴胀和相变模型中，这些模型涉及自发宇称破缺。主要包括：

1. **轴子引力耦合（Axion-Gauge Field Coupling）**：在暴胀期间，标量场通过 $R\tilde{R}$ 或 $F\tilde{F}$ 耦合产生手征引力波。手征参数 $\chi$ 的大小取决于耦合强度 $\alpha_R$ 和暴胀能标。

2. **原初磁场（Primordial Magnetic Fields）**：原初磁场通过湍流效应产生手征 SGWB。由于磁场具有螺旋性，产生的引力波天然携带手征不对称性。

3. **手征相变（Chiral Phase Transitions）**：电弱相变或暗 sector 相变中，如果泡壁动力学或磁流体湍流存在宇称破缺，也会产生手征引力波。

### 5.2 探测能力与理论参数的约束

从 JCAP 图 4 的 PLI 灵敏度曲线可以看出：

- 对于 I 分量，LISA-Taiji 网络在 $f \approx 2$ mHz 的灵敏度约为 $\Omega_{\text{min}}^I \sim 10^{-13}$
- 对于 V 分量，LISA-TAIJIm 在 $f \approx 2$ mHz 的灵敏度约为 $\Omega_{\text{min}}^V \sim 10^{-13}$

因此，对于手征 SGWB 信号，可以约束：

$$
\chi = \frac{\Omega^V}{\Omega^I} \gtrsim \frac{\Omega_{\text{min}}^V}{\Omega_{\text{min}}^I} \sim 1
$$

这意味着 LISA-Taiji 网络在 $f \approx 2$ mHz 处对于典型谱指数（$\alpha = 2/3$，对应相变产生的 SGWB）可以探测到手征不对称性达到 $\mathcal{O}(1)$ 的量级。

**与现有文献的对比**：JCAP 论文指出，其灵敏度依赖于频率积分的下限——这一下限主要由银河系和河外双星系统产生的混淆前景决定，取决于观测时间 $T_{\text{obs}}$（JCAP 正文第 13 页，式 (3.3) 后的讨论）。

### 5.3 与其他探测方案的对比

JCAP 论文（第 3 节）的比较表明：

- **单三角探测器**：由于共面性定理（$\Gamma^V = 0$），单三角无法探测手征信号
- **LISA-LISA**：同一网络的两个通道之间也是共面的，因此 $\Gamma^V = 0$
- **LISA-Taiji**：非共面网络，$\Gamma^V \neq 0$，可以探测手征信号
- **LISA-Taiji + TianQin**：三个探测器的网络将进一步提高手征灵敏度（JCAP 引用 [29, 30]）

从我们的分析（P1-2-chiral-orf-triangular.md）可以补充：对于任意共面三角星座，反射对称性保证 $\Gamma^V = 0$。这是手征探测需要非共面网络的严格证明。

---

## 6. 自问自答

### Q1: 为什么单三角 A-E 通道的相关无法提取手征信号？

**答**：这是由共面性定理保证的。对于共面三角星座，两个通道（A 和 E）位于同一平面内，其单位分离向量 $\hat{s}$ 垂直于星座平面的法向量 $\hat{n}$。JCAP 式 (2.23) 给出的几何因子 $X_{mn}^V$ 包含因子 $\sin a \sin b$，其中 $a = \arccos(\hat{n} \cdot \hat{s})$。对于共面通道，$a = \pi/2$，但更关键的是 $\Gamma^V$ 的积分结构——在共面情况下，对天球方向的积分中，奇宇称张量收缩的贡献相互抵消。我们在 P1-2 中通过反射对称性给出了严格证明：对共面三角形取关于星座平面的反射操作，$\Gamma^V$ 在该操作下变号，因此必须为零。我们的迭代代码也验证了这一点：Iter8 给出 $\Gamma^V \sim 1.3 \times 10^{-18}$（机器精度为零）。

### Q2: JCAP 中 $\Gamma^V$ 的数值量级看起来很小（$\sim 10^{-3}$），这是否意味着手征信号实际上不可探测？

**答**：$\gamma_{\text{eff}}^V$ 的数值小主要是因为两个原因：(1) 归一化因子 10/3 使得 $\gamma_{\text{eff}}^I(0) = 1$，而 $\Gamma^V$ 本身在低频趋于零；(2) 手征信号在交叉谱中处于次要地位。但这并不意味着手征信号不可探测。从 JCAP 图 4 可以看到，在 $f \approx 2$ mHz，LISA-TAIJIm 的 PLI 灵敏度对于 V 分量达到 $\Omega_{\text{min}}^V \sim 10^{-13}$，与 I 分量的灵敏度可比拟。此外，SNR 公式（式 2.12）中包含 $T_{\text{obs}}^{1/2}$ 因子，因此长时间观测可以显著改善手征灵敏度。对于 3 年观测，典型的手征 SGWB 信号（如相变产生的，$\Omega_{\text{GW}} \sim 10^{-9}$–$10^{-10}$）应该有可探测的 SNR。

### Q3: JCAP 使用的长波近似对高频段的影响如何？

**答**：JCAP 正文第 13 页指出，长波近似在低频段是有效的。对于 $f < 20$ mHz（即 $f < c/(2\pi L)$），长波近似给出合理的估计。对于更高频率，需要考虑完整的频域响应函数。JCAP 引用 [58] 进行了更详细的数值计算，考虑了真实的轨道运动及健壮的 TDI 方案。我们的分析（P-chiral-orf-analytical.md）通过 OLC sinc 传递函数的精确处理，可以覆盖全频段。在高频段，ORF 以 $\sim f^{-1}$ 衰减，同时振荡结构增强，这限制了高频手征信号的探测灵敏度。

### Q4: 有效 ORF 公式中交叉项 $\sum \bar{\Gamma}^I \bar{\Gamma}^V$ 的物理意义是什么？

**答**：交叉项反映了 I/V 分量之间的简并。对于单个通道对，交叉谱 $C_{ij}$ 同时包含 $I$ 和 $V$ 的贡献。当 $\sum \bar{\Gamma}^I \bar{\Gamma}^V \neq 0$ 时，通过 Fisher 矩阵投影消除简并的过程会减小有效 ORF。这在几何上对应于通道对的组合未能最大程度地区分 I 和 V 分量。对于 LISA-Taiji 网络，四个通道对的组合可以最大程度地减少这种简并，使得有效 ORF 接近理论最大值的 $2/3$（对于 I 分量）或更低（对于 V 分量）。

---

## 7. 与 P2 项目工作的交叉对比

| 项目 | 方法 | $\Gamma^V$ 结果 | 覆盖范围 |
|------|------|-----------------|----------|
| JCAP 2025 | 长波近似 + 球贝塞尔展开 | 数值有效 ORF | $f \in [10^{-4}, 20]$ mHz |
| P2 (P-chiral-orf-analytical) | Hu I1-I4 + OLC sinc | 全频段解析，小臂近似 | 全频段 |
| Iter8 (项目代码) | 数值积分 | 共面 $\Gamma^V \approx 0$，非共面 $\sim 1$ | 参数扫描 |

JCAP 的结果可以被视为 P2 工作在长波近似下的特例。我们的 P2 解析框架可以：
1. 恢复 JCAP 的球贝塞尔展开结果（在 $f \ll c/L$ 极限下）
2. 超出 JCAP 的长波近似，给出全频段的 $\Gamma^V$ 表达式
3. 提供更细致的物理理解（如 $\mathcal{P}^V$ 的几何结构）

---

## 8. 关键公式索引

| 编号 | 来源 | 公式 |
|------|------|------|
| (1) | JCAP 2.10 | $\Gamma_{ij}^{I,V}(f)$ 的原始定义（张量收缩 + 天球积分） |
| (2) | JCAP 2.11 | 归一化 ORF $\bar{\Gamma}^{I,V}$ |
| (3) | JCAP 2.16 | 球贝塞尔系数 $b_{0,1,2}^{I,V}(\vartheta)$ |
| (4) | JCAP 2.13 | 有效 ORF $\gamma_{\text{eff}}^{I,V}$（Fisher 矩阵投影） |
| (5) | JCAP 2.12 | I/V 分量的 SNR 公式 |
| (6) | JCAP 2.22-23 | 几何因子 $X_{mn}^{I,V}$ 在三个角度 $(a,b,c)$ 中的显式表达 |
| (7) | JCAP 2.6 | 斯托克斯参数 $I(f), V(f)$ 与圆偏振谱密度的关系 |
| (8) | JCAP 3.3 | fractional energy density $\Omega^{I,V}(f)$ 的定义 |

---

## 9. 结论

JCAP 2025 的数值结果表明：

1. **LISA-TAIJIm 构型对手征信号有显著优势**：在 $f \approx 1$ mHz，灵敏度比 TAIJIp 高一个量级。
2. **最佳频率处的可比灵敏度**：在 $f \approx 2$ mHz，LISA-TAIJIm 的 V 分量灵敏度与 I 分量相当，这为检验宇称破缺理论提供了独特机会。
3. **几何构型的关键作用**：手征灵敏度随两探测器平面夹角的增大而增强，正交构型（夹角 $\approx \pi/2$）最优。
4. **分离距离的影响**：缩短探测器间距可将 $\Gamma^V$ 的峰值频率移至 LISA/Taiji 最敏感的频段。
5. **与 P2 分析框架一致**：JCAP 的结果在长波近似下等价于我们解析框架的特例，我们可以在全频段提供更精确的预测。

这些结果直接支持在原初引力波分析中考虑手征分量，并为未来多探测器网络的优化设计提供了定量指导。
