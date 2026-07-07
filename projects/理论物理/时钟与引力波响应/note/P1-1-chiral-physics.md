# P1-1: 手征引力波的物理基础

> 基于 JCAP05(2025)050 "Circularly polarized gravitational wave background search with a network of space-borne triangular detectors"
> 基于 Seto PRL 97, 151101 (2006) "Prospects for direct detection of circular polarization of gravitational-wave background"

---

## 1. 什么是引力波的手征性 (Chirality)

### 1.1 两种极化模式

在广义相对论中，引力波有两个张量极化模式：+" 和 "x"。这两种模式是线性极化的基础。

**原文引用** (JCAP §2, eq. 2.1):
$$h_{ab}(t, \hat{\vec{r}}) = \sum_{P=+, \times} \int df \int \frac{d^2\hat{k}}{4\pi} \tilde{h}_P(f, \hat{k}) e^P_{ab}(\hat{k}) e^{i2\pi f (t - \hat{k}\cdot\hat{\vec{r}}/c)}$$

### 1.2 圆极化基（手征基）

定义右旋 (Right-handed, R) 和左旋 (Left-handed, L) 圆极化基张量：

**原文引用** (JCAP §2, eq. 2.3):
$$e^R_{ab} = \frac{e^+_{ab} + i e^\times_{ab}}{\sqrt{2}}, \quad e^L_{ab} = \frac{e^+_{ab} - i e^\times_{ab}}{\sqrt{2}}$$

对应的光应变：

**原文引用** (JCAP §2, eq. 2.4):
$$h_R = \frac{h_+ - i h_\times}{\sqrt{2}}, \quad h_L = \frac{h_+ + i h_\times}{\sqrt{2}}$$

**物理直觉**：想象一个引力波沿 z 轴传播。+" 模式在 x-y 平面上拉伸/压缩，x" 模式是 +" 旋转 45 度。R 和 L 是这两个模式的复数叠加，分别对应顺时针和逆时针旋转的极化。一个纯 R 模式的引力波，其 +" 和 x" 分量之间有 90 度的相位差，导致测试粒子在波通过时做圆周运动。

### 1.3 手征性 = 宇称

手征性本质上与宇称 (parity) 有关。在宇称变换下（空间反演 $\vec{x} \to -\vec{x}$），右旋和左旋手征态互换。因此：
- 如果宇宙学过程中 R 和 L 的产生率相等 → 非手征背景
- 如果 R 和 L 的产生率不等 → 手征背景（宇称破坏）

---

## 2. Stokes 参数 S^I 和 S^V

### 2.1  ensemble average 的形式

SGWB 的统计特性由 Fourier 振幅的系综平均描述。

**原文引用** (JCAP §2, eq. 2.2):
$$\langle \tilde{h}_+(f, \hat{k}) \tilde{h}_+^*(f', \hat{k}') \rangle \quad \langle \tilde{h}_+(f, \hat{k}) \tilde{h}_\times^*(f', \hat{k}') \rangle$$
$$\langle \tilde{h}_+^*(f, \hat{k}) \tilde{h}_\times(f', \hat{k}') \rangle \quad \langle \tilde{h}_\times(f, \hat{k}) \tilde{h}_\times^*(f', \hat{k}') \rangle$$
$$= \frac{1}{2} \delta(f - f') \delta^2(\hat{k} - \hat{k}') \frac{1}{4\pi} \begin{pmatrix} I(f) - iV(f) \\ iV(f) \quad I(f) \end{pmatrix}$$

### 2.2 I 和 V 的物理意义

**原文引用** (JCAP §2, 紧接 eq. 2.2):
> "where I, V are the Stokes parameters, with I related to the overall intensity of the background and V characterizes the asymmetry of the intensity of right and left-hand circular polarization, i.e. the parity-violating components."

在圆极化基下，系综平均更简洁：

**原文引用** (JCAP §2, eq. 2.5):
$$\langle \tilde{h}_\Lambda(f, \hat{k}) \tilde{h}_{\Lambda'}^*(f', \hat{k}') \rangle = \frac{1}{2} \delta(f - f') \delta^2(\hat{k} - \hat{k}') \frac{1}{4\pi} \delta_{\Lambda\Lambda'} S_\Lambda(f)$$

其中 $\Lambda = R, L$，且：

**原文引用** (JCAP §2, eq. 2.6):
$$I(f) = \frac{1}{2}[S_R(f) + S_L(f)], \quad V(f) = \frac{1}{2}[S_R(f) - S_L(f)]$$

### 2.3 核心物理

| 参数 | 物理含义 | 数学定义 |
|------|----------|----------|
| I(f) | 总强度 | $(S_R + S_L)/2$ — 两种手征态的平均功率 |
| V(f) | 圆极化不对称性 | $(S_R - S_L)/2$ — 右旋与左旋的功率差 |

- **V = 0**: 无手征性，R 和 L 强度相等，宇称守恒
- **V > 0**: 右旋占优
- **V < 0**: 左旋占优
- **|V| = I**: 完全手征（纯 R 或纯 L）

### 2.4 为什么 Q 和 U 被忽略？

**原文引用** (JCAP §2, 紧接 eq. 2.2):
> "The other two Stokes parameters, Q and U, which describe linear polarization, are spin-4 quantities and do not contribute to the monopole modes, i.e., the isotropic components of the stochastic background."

**物理直觉**：Q 和 U 描述线性极化，对应自旋为 4 的谐波。在球面谐波展开中，各向同性背景只有 monopole ($\ell=0$) 项。自旋为 4 的量在 $\ell=0$ 时为零。因此对于**各向同性** SGWB，Q = U = 0。

---

## 3. 手征参数 chi

### 3.1 定义

手征参数定义为 V 分量与 I 分量的比值：

$$\chi(f) = \frac{\Omega^{V}(f)}{\Omega^{I}(f)} = \frac{V(f)}{I(f)} = \frac{S_R(f) - S_L(f)}{S_R(f) + S_L(f)}$$

其中 $\Omega^{I,V}$ 是分数能量密度谱：

**原文引用** (JCAP §3.1, eq. 3.3):
$$\Omega_I(f) = \frac{4\pi^2}{3H_0^2} f^3 I(f), \quad \Omega_V(f) = \frac{4\pi^2}{3H_0^2} f^3 V(f)$$

### 3.2 取值范围

- $\chi = 0$: 无手征（$S_R = S_L$）
- $\chi = +1$: 完全右旋（$S_L = 0$）
- $\chi = -1$: 完全左旋（$S_R = 0$）
- $|\chi| \leq 1$: 一般情况

### 3.3 物理意义

chi 直接量化了 SGWB 的宇称破坏程度。在标准宇宙学中，引力波的产生过程（如暴胀的量子涨落）宇称守恒，预期 $\chi \approx 0$。但在以下宇称破坏的模型中，$\chi$ 可以显著非零：

**原文引用** (JCAP §1):
> "parity violation in gravity could alter both the generation and propagation of gravitational waves, resulting in a circularly polarized SGWB."

---

## 4. 宇称破坏宇宙学模型如何产生手征 GW

### 4.1 主要机制

JCAP 列举了三种主要机制：

**a) 暴胀中的自发宇称破坏** (§1):
- **Leptogenesis 模型**: Alexander, Peskin, Sheikh-Jabbari (2006) — 在暴胀期间通过轴子-规范场耦合产生手征 GW
- **Chern-Simons 耦合**: Satoh, Kanno, Soda (2008); Adshead, Wyman (2012) — 修改引力作用量，加入 $R\tilde{R}$ 项

**b) 一阶相变中的螺旋原初磁场** (§1):
-  Cornwall (1997); Vachaspati (2001) — 螺旋磁场在手性湍流中产生手征 GW
- Kahniashvili et al. (2005); Roper Pol et al. (2020) — 数值模拟确认

**c) 传播过程中的双折射** (§1):
- Callister et al. (2025); Li et al. (2024) — 宇称破坏导致 R 和 L 的传播速度不同（双折射），即使初始非手征，传播后也会产生净圆极化

### 4.2 关键概念

所有这三种机制的共同点：**R 和 L 的模式被不对称地增强或抑制**。在量子场论的语言中，这意味着 R 和 L 的有效质量或耦合常数不同，导致它们的增长率不同。

---

## 5. 可探测性条件：为什么需要非共面探测器

### 5.1 核心结论

**原文引用** (JCAP §1):
> "For an isotropic SGWB, circular polarization is undetectable with planar detector(s). The detection of such signals requires correlating gravitational wave detectors that are not co-planar, which means a network of detectors is necessary."

### 5.2 交叉相关公式

**原文引用** (JCAP §2.1, eq. 2.9):
$$\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle = \frac{1}{2} \delta(f - f') \left[ \Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f) \right]$$

其中 $\Gamma^I$ 是宇称偶 (parity-even) ORF，$\Gamma^V$ 是宇称奇 (parity-odd) ORF。

### 5.3 Gamma^V 的宇称奇性

**原文引用** (JCAP §2.1, eq. 2.10):
$$\Gamma^V_{ij}(f) \propto -i \int \frac{d^2\hat{k}}{4\pi} \left( e^+_{ab}(\hat{k}) e^\times_{cd}(\hat{k}) - e^\times_{ab}(\hat{k}) e^+_{cd}(\hat{k}) \right) e^{-i2\pi f \hat{k}\cdot\vec{\Delta r}/c}$$

括号内的组合 $e^+ e^\times - e^\times e^+$ 是**宇称奇**的——它在空间反换下变号。而 $\Gamma^I$ 是宇称偶的。

**物理直觉**：对于一个平面探测器网络，存在一个镜面反射将该网络映射到自身。在这个反射下，宇称奇的 $\Gamma^V$ 必须变号。但既然网络不变，$\Gamma^V$ 也必须保持不变。唯一可能的值就是 $\Gamma^V = 0$。

因此，**只有当探测器网络没有镜面对称性时（即非共面），才能探测到手征性。**

---

## 6. SGWB 能量密度与 Stokes 参数的关系

**原文引用** (JCAP §2, 紧接 eq. 2.6):
$$\Omega_{GW} = \frac{4\pi^2 f^3}{3H_0^2} I(f)$$

注意：这是标准定义，总能量密度只依赖于 I(f)（总强度），与 V(f) 无关。

原文特别说明了其 I(f) 定义的归一化（与 Maggiore 教科书不同）：

**原文引用** (JCAP §2, 紧接 eq. 2.6):
> "Notice that comparing with eq. (8.38) in [39], there is an additional factor 1/2 due to different definitions of I(f)."

Maggiore 的 I(f) = S_R + S_L（两种极化的总和），而 JCAP 的 I(f) = (S_R + S_L)/2（两种极化的平均）。JCAP 采用的定义与 Seto 2006 和 Maggiore 的公式 (8.38) 一致。

---

## 7. 与项目的关系

- **项目代码 `scripts/01-olc-orf-solver.py`** 中的 R^I 部分对应于 JCAP 的 $\Gamma^I$，需要确认是否已正确处理归一化因子
- **记忆 15** (chi_orb 物理推理正确) 和 **记忆 16** (镜面对称性与 R^V = 0) 确认了我们之前关于手征性的直觉是正确的
- JCAP 的 Stokes 参数定义与 PTA 文献（如 Seto 2006）一致
- 对于 OLC（光学晶格钟）探测器，同样的手征理论框架适用——关键区别在于探测器张量的定义

---

## 8. 不确定之处

1. **圆极化基与线性极化基的变换细节**: 方程 (2.3) 和 (2.4) 中的 $\sqrt{2}$ 归一化是否确保 $|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_\times|^2$？需要验证。

2. **传播双折射的具体机制**: 宇称破坏引力理论（如 Chern-Simons 引力）如何导致 R 和 L 的传播速度不同？这需要更深入的场论推导，不在当前任务范围内。

3. **手征参数的频率依赖性**: chi(f) 是否随频率变化？在不同宇称破坏模型中，chi(f) 的频谱形状是否有可区分特征？

---

## 9. 自我提问与回答

**Q1: 如果 SGWB 是完全手征的 (chi = 1)，意味着什么？**

A: 这意味着只有一种手征模式（纯 R 或纯 L），另一种为零。这在标准宇宙学中几乎不可能——需要极端的手征产生机制。但如果观测到 chi 显著非零（如 chi ~ 0.1），已经能强烈暗示宇称破坏的新物理。

**Q2: 为什么 Q 和 U 对各向同性背景没有贡献？**

A: 因为 Q 和 U 是自旋为 4 的量（对应 + 和 x 极化的交叉项），在各向同性平均下，自旋 s > 0 的谐波在 $\ell = 0$ (monopole) 时为零。简单地说，线性极化方向在天空所有方向上均匀平均后相互抵消，只有总强度 I 和圆极化不对称 V（它们是标量，自旋为零）能存活。

**Q3: 为什么平面三角探测器（如单个 LISA）对 Gamma^V = 0？**

A: 单个三角探测器虽然是由三个臂组成的三角形，但其所有航天器都在同一个平面内。当计算与该探测器自身相关的 Gamma^V 时，镜面反射穿过该平面将网络映射到自身，导致 Gamma^V = 0。只有当两个探测器不在同一平面时（如 LISA-Taiji 网络），才可能有 Gamma^V ≠ 0。
