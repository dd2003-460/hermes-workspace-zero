# P1-2: 三角探测器网络的手征重叠归一化函数 Gamma^V

> **版本**: v1.0
> **日期**: 2026-07-11
> **基于文献**:
> - Hu PRD 111.084065 (arXiv:2406.05636) — 通用单程链路 ORF 框架
> - JCAP 05 (2025) 050 "Circularly polarized gravitational wave background search with a network of space-borne triangular detectors"
> - 楼明智硕士论文 — OLC 构型 ORF 分析

---

## 1. 手征 ORF 的物理背景

### 1.1 Stokes 参数与手征参量

引力波有两个线性极化模式 $+$ 和 $\times$。定义圆极化（手征）基：

**原文引用** (JCAP §2, Eq. 2.3):
$$e^R_{ab} = \frac{e^+_{ab} + i e^\times_{ab}}{\sqrt{2}}, \quad e^L_{ab} = \frac{e^+_{ab} - i e^\times_{ab}}{\sqrt{2}}$$

对应的光应变：

**原文引用** (JCAP §2, Eq. 2.4):
$$h_R = \frac{h_+ - i h_\times}{\sqrt{2}}, \quad h_L = \frac{h_+ + i h_\times}{\sqrt{2}}$$

SGWB 的统计特性由 Stokes 参数描述（JCAP §2, Eq. 2.6）：
$$I(f) = \frac{1}{2}[S_R(f) + S_L(f)], \quad V(f) = \frac{1}{2}[S_R(f) - S_L(f)]$$

归一化手征参数：
$$\chi(f) = \frac{V(f)}{I(f)} = \frac{S_R(f) - S_L(f)}{S_R(f) + S_L(f)}$$

**物理直觉**：$I(f)$ 是总强度（R 与 L 之和的一半），$V(f)$ 是圆极化不对称度。如果 $\chi=0$（$I$ 个方向 R、L 等量），背景是非手征的；如果 $|\chi|=1$，背景是纯圆极化的。

### 1.2 交叉相关中的手征 ORF 分解

对于两个探测器 $i$ 和 $j$，信号交叉相关期望值为（JCAP §2, Eq. 2.9）：

$$\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle = \frac{1}{2}\delta(f - f')\left[\Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f)\right]$$

$\Gamma^I$ 是宇称偶 ORF（对总强度 $I$ 的响应），$\Gamma^V$ 是宇称奇 ORF（对手征不对称度 $V$ 的响应）。探测手征性即测量非零的 $\Gamma^V$。

---

## 2. Gamma^V 的数学定义

### 2.1 宇称奇收缩

$\Gamma^V$ 的定义来自极化张量的宇称奇收缩（JCAP §2, Eq. 2.10）：

$$\Gamma^V_{ij}(f) = \int \frac{d^2\hat{k}}{4\pi} \, F_i^{A}(\hat{k}) F_j^{B}(\hat{k}) \, \epsilon_{AB} \, e^{i2\pi f \hat{k}\cdot\vec{\Delta r}_{ij}/c}$$

其中 $\epsilon_{AB}$ 是反对称张量，$\epsilon_{+\times} = 1$，$\epsilon_{\times +} = -1$，$A,B \in \{+,\times\}$。

**物理直觉**：$\Gamma^I$ 对偏振求和 $\sum_A R_A R_A^*$ 是偶宇称（正号和交叉号各自平方再相加），$\Gamma^V$ 是反对称组合 $\epsilon_{AB} R_A R_B$，在空间反换下变号。这就是"宇称奇"名称的由来。

### 2.2 极化张量收缩的几何结构

展开 $\Gamma^V$ 的被积函数（与 P-chiral-orf-analytical.md 附录 B 相同推导）：

$$\mathcal{P}^V(\hat{n}) = -i\left[F_+(\hat{u}_1,\hat{n})F_\times(\hat{u}_2,\hat{n}) - F_\times(\hat{u}_1,\hat{n})F_+(\hat{u}_2,\hat{n})\right]$$

在 GW 传播方向 $\hat{n}$ 的正交基 $\{\hat{x}, \hat{y}, \hat{n}\}$ 中显式计算天线方向图（$e^+_{ab} = \hat{x}_a\hat{x}_b - \hat{y}_a\hat{y}_b$，$e^\times_{ab} = \hat{x}_a\hat{y}_b + \hat{y}_a\hat{x}_b$）：

**推导 Step 1 — 天线方向图的显式表达式**：

设 $\hat{u}_1$ 和 $\hat{u}_2$ 分别为两个探测器的平均臂方向。对臂方向的线性组合做积分得到 Michelson-like 变量。令 $F_A = \frac{1}{2}e^A_{ab}u^a u^b$ 为单臂天线方向图，对于 Michelson-like 变量：

$$F_A^{\rm Michelson} = F_A^{(1)} + F_A^{(2)}$$

其中 $A = +,\times$ 为偏振指标，上标 $(1),(2)$ 为臂指标。

**推导 Step 2 — 手征因子的几何分解**：

手征因子为：
$$G = F_{+1}F_{\times 2} - F_{\times 1}F_{+2}$$

其中 $F_{A m} = F_A^{(1)} - F_A^{(2)}$ 是 Michelson 组合（以标准 Michelson 定义为准）。直接计算可得：

$$\mathcal{P}^V(\hat{n}) = \frac{1}{2}(\hat{u}_1 \times \hat{u}_2) \cdot \hat{n} \cdot \left[(\hat{n}\cdot\hat{u}_1)^2 - (\hat{n}\cdot\hat{u}_2)^2\right]$$

**物理直觉**：这个表达式包含两个关键几何因子：
- $(\hat{u}_1 \times \hat{u}_2) \cdot \hat{n}$：探测器的"非共面度"，即 $\hat{n}$ 方向与探测器平面法向的投影。如果 $\hat{n}$ 在探测器平面内，此项为零。
- $(\hat{n}\cdot\hat{u}_1)^2 - (\hat{n}\cdot\hat{u}_2)^2$：两臂对 $\hat{n}$ 方向投影的差异，如果两臂正交且 $\hat{n}$ 在平分面内，此项也为零。

### 2.3 Hu PRD 框架下的 ORF 计算

Hu PRD 给出了通用单程链路 ORF 的解析框架（Hu §IV, Eq. 8）：

$$\Gamma^{IJ}(f) = \frac{1}{8\pi} \int d^2\Omega_{\hat{n}} \sum_A R_I^A(f,\hat{n}) R_J^{A*}(f,\hat{n})$$

对于两条单程链路，Hu 将 ORF 分解为四项（Hu Eq. 10-11）：

$$\Gamma_{\rm one} = \frac{1}{32\pi}[I_1 - e^{-i\beta_u}I_1(\alpha_2,s_2) - e^{i\beta_v}I_1(\alpha_3,s_3) + e^{i(\beta_v-\beta_u)}I_1(\alpha_4,s_4)]$$

其中五个留数极点为（Hu Eq. 16）：
$$z_0 = 0, \quad z_1 = -\hat{n}\cdot\hat{u} + i0^+, \quad z_2 = \hat{n}\cdot\hat{u} + i0^+, \quad z_3 = -\hat{n}\cdot\hat{v} + i0^+, \quad z_4 = \hat{n}\cdot\hat{v} + i0^+$$

完整的 $I_1$ 结果（Hu Eq. 18）包含 $\frac{\sin\alpha}{\alpha}$ 项、指数积分 $\text{Ei}$ 和角度依赖项。

**扩展至手征**：Hu 框架可以自然地扩展到 $\Gamma^V$——只需将偏振求和 $\sum_A$ 替换为 $\epsilon_{AB}\sum_{A,B}$。sinc 传递函数（OLC 专用）展开为指数形式后，I1-I4 分解框架同样适用，只是留数计算因 sinc 函数在复平面上的极点-零点结构而更加复杂。

**物理直觉**：I1-I4 分解的本质是将 sky-average 积分转化为复平面上的留数求和。每个指数项 $e^{-i\beta(1+\hat{n}\cdot\hat{u})}$ 对应一个传播方向上的相位延迟，四项对应两个链路的所有可能相位组合。留数定理将这些天空积分转化为离散的代数表达式。

### 2.4 JCAP 的辅助张量与几何因子分解

JCAP 给出了适用于三角探测器网络的 $\Gamma^V$ 分解（JCAP §2, Eq. 2.15-2.16）：

$$\gamma^V_{abcd} = b_0^V w_{ac}\delta_{bd} + b_1^V w_{ac}s_b s_d$$

其中 $s^i$ 为卫星间分离方向，$w^{ij}$ 为反投影张量（JCAP Eq. 2.14-2.15），球贝塞尔系数为：

$$b_0^V(\rho) = 4j_1 - j_3, \quad b_1^V(\rho) = 5j_3$$

JCAP 进一步给出宇称奇几何因子 $X_m^{V}$ 的显式表达式（JCAP Eq. 2.23）：

$$X_{11}^V = -\cos\psi_{12}(n_1 \times n_2) \cdot \hat{z}, \quad X_{22}^V = \sin\psi_{12}(n_1 \times n_2) \cdot \hat{z}$$

$$X_1^V = -[\cos\psi_{12}\sin\phi_{12}(n_1 \times n_2)\cdot\hat{z} + (n_1 \times \hat{d})\cdot\hat{z}\sin\psi_{12}]$$

$$X_2^V = -[-\sin\psi_{12}\sin\phi_{12}(n_1 \times n_2)\cdot\hat{z} + (n_1 \times \hat{d})\cdot\hat{z}\cos\psi_{12}]$$

其中 $n_i$ 为探测器轨道面法向量，$\psi_{12}$ 为两臂夹角，$\hat{d}$ 为两探测器间的分离方向。

**物理直觉**：JCAP 的分解将 $\Gamma^V$ 分离为两个独立因子：(1) 几何因子 $X^V$ 仅依赖于探测器的空间构型（轨道面法向、臂方向），(2) 球贝塞尔系数 $b_m^V$ 仅依赖于频率和臂长。这种分解使得优化探测器网络构型时可以独立处理几何设计。

---

## 3. 严格证明：平面三角网络 Gamma^V = 0

### 3.1 反射对称性论证

**定理**：任意由三个卫星组成的三角星座，其所有两变量交叉相关的手征 ORF $\Gamma^V$ 恒等于零。

**证明**：

**Step 1**：任意三个点在三维空间中必然定义唯一平面。设该平面为 $P$。

**Step 2**：所有链路方向单位向量 $\hat{n}_{ij} = (\vec{r}_j - \vec{r}_i)/|\vec{r}_j - \vec{r}_i|$ 均在平面 $P$ 内。这是因为 $\vec{v}_{ij} = \vec{r}_j - \vec{r}_i$ 是平面内的位移向量，其方向单位化后仍在平面内。

**Step 3**：考虑对平面 $P$ 的反射操作 $\mathcal{R}$。反射性质：
- 在平面内的向量不变：$\hat{n}_{ij} \to \hat{n}_{ij}$（所有链路方向）
- 天线方向图 $F_+$ 是偶宇称：$F_+ \to +F_+$
- 天线方向图 $F_\times$ 是奇宇称：$F_\times \to -F_\times$

**Step 4**：手征被积函数 $G = F_{+1}F_{\times 2} - F_{\times 1}F_{+2}$ 在反射下：
$$G \to (+F_{+1})(-F_{\times 2}) - (-F_{\times 1})(+F_{+2}) = -F_{+1}F_{\times 2} + F_{\times 1}F_{+2} = -G$$

因此 $G$ 是反射下的奇函数。

**Step 5**：天区积分 $\int d^2\Omega_{\hat{n}} G(\hat{n})$：反射操作 $\mathcal{R}$ 将天区映射到自身（$\hat{n} \to \mathcal{R}\hat{n}$），而 $G$ 变号，故 $\int G = -\int G$，唯一可能是 $\int G = 0$。

$\square$

### 3.2 反射对称的直观理解

想象一个三角形探测器"躺"在桌面上。从桌子下方往上反射观察，探测器看起来还是同样的三角形（因为三点决定一个平面）。但是，交叉偏振模式 $F_\times$ 在反射下反号——这与镜子中的左右互换效应类似：

**物理直觉**：想象你站在镜子前举起右手。你的像举的是"左手"。类似的，$+$ 模式像照镜子一样不改变（拉伸还是拉伸），但 $\times$ 模式像被左右翻转了（拉伸方向从东北-西南变成了西北-东南）。手征性恰恰需要 $+$ 和 $\times$ 之间的相位差，而反射使这个相位差反号。对于一个自身在反射下不变的系统（如共面三角），反射前后的 $\Gamma^V$ 应该相等，但反射又使 $\Gamma^V$ 反号——唯一的自洽解是 $\Gamma^V = 0$。

### 3.3 JCAP 中的相同结论

JCAP §1 明确陈述（原文）：

> "For an isotropic SGWB, circular polarization is undetectable with planar detector(s) [33, 34]."

JCAP 中的"planar detector"指的就是所有臂方向共面的探测器。这与上述反射论证完全一致。

---

## 4. 非共面条件与多星座网络

### 4.1 $\Gamma^V \neq 0$ 的几何条件

从 $\mathcal{P}^V(\hat{n}) = \frac{1}{2}(\hat{u}_1 \times \hat{u}_2) \cdot \hat{n} \cdot [( \hat{n}\cdot\hat{u}_1)^2 - (\hat{n}\cdot\hat{u}_2)^2]$ 可以看出：

$\Gamma^V \neq 0$ 的必要条件是 $(\hat{u}_1 \times \hat{u}_2) \cdot \hat{n}$ 在全天空平均后非零。对于单个共面三角星座，对所有 $\hat{n}$ 的积分使奇对称部分相消。对于多星座网络（如 LISA-Taiji），两星座的空间分离方向 $\hat{d}$ 不同，使得整体几何不再具有反射对称性。

### 4.2 LISA-Taiji 网络的手征灵敏度

JCAP 详细计算了 LISA-Taiji 网络的手征响应。由于 LISA 和 Taiji 轨道面在三维空间中分离，两星座之间的链路方向不共面，打破了反射对称性。

JCAP 的结果显示：
- LISA-Taiji（不同轨道面夹角）：$|\Gamma^V|$ 可达 1.00
- LISA-Taiji-c（共面近似）：$\Gamma^V \approx 0$
- 最优轨道面夹角约为 $\pi/2$

这验证了"非共面是手征性探测的必要条件"这一结论。

---

## 5. 与现有项目代码的对比分析

### 5.1 代码实现：`scripts/10-olc-chiral-orf-triangular.py`

**手征因子计算**（line 230）：
```python
chiral_factor = M1p * M2x - M1x * M2p
```
这与 JCAP 定义的 $F_{+1}F_{\times 2} - F_{\times 1}F_{+2}$ 完全一致。

**Michelson-like 变量**（line 154-167）：
```python
def michelson_effective_response(link_responses):
    return link_responses[0] + link_responses[1]
```
将两个单向链路响应相加构造等效 Michelson 变量，与楼明智论文和 LISA 文献中的定义一致。

**三角形卫星位置**（line 115-138）：
```python
triangle_sat_positions(side_length=5e9)  # z=0, all coplanar
```
所有卫星在 xy 平面内（z=0），天然共面。

### 5.2 迭代结果对比

| 迭代 | 配置 | 代码状态 | Gamma^V 结果 | 可靠性 |
|------|------|----------|-------------|--------|
| Iter6 | 共面三角 | 有天线方向图 bug (ny=sin(theta_g)) | 非零（错误） | 低 |
| Iter7 | LISA x Taiji | 代码正确 | ~1.00 | 高 |
| Iter8 | 共面三角 | 代码修正后 | ~1.3e-18 (零) | 高 |

**关键结论**：Iter6 显示的非零 Gamma^V 结果来自天线方向图 bug（$ny = \sin\theta_g$ 应为 $ny = \sin\theta_g\sin\phi_g$），必须排除。Iter8 使用修正后的代码，得到 $\Gamma^V \sim 10^{-18}$（机器精度级别），与严格证明一致。

### 5.3 理论-代码一致性检查

1. **手征因子公式**：代码 `M1p * M2x - M1x * M2p` 与 JCAP Eq. 2.10 完全一致。
2. **共面约束**：代码中 `triangle_sat_positions()` 将所有卫星放在 z=0 平面，满足反射对称条件。
3. **零结果**：Iter8 的 $\Gamma^V \approx 0$ 验证了定理，残差 ~1.3e-18 为数值噪声。
4. **多星座验证**：Iter7 的 LISA x Taiji 结果 $\Gamma^V \approx 1.00$ 与 JCAP 的理论预测一致，同时验证了非共面条件下 $\Gamma^V \neq 0$。

---

## 6. 自我问答

### Q1：如果单个三角星座的 Gamma^V 恒为零，为什么还要构造 Michelson-like 变量？

**A**：Michelson-like 变量（$M = \text{link}(a) - \text{link}(b)$）的主要目的是抑制激光频率噪声，并非为了获得手征灵敏度。对于共面三角，每个 Michelson 通道的 $\Gamma^V = 0$，但这不影响它们在 $\Gamma^I$（标准 ORF）中的灵敏度。探测总强度 SGWB 只需要 $\Gamma^I$。手征性探测需要至少两个非共面三角星座的交叉相关。

### Q2：JCAP 中提到 $\hat{\gamma}_{\rm eff}^V = \sqrt{\sum (\gamma^V_\alpha)^2 - [\sum \gamma^I_\alpha \gamma^V_\alpha]^2/\sum(\gamma^I_\alpha)^2}$，对于单三角星座这一表达式是否等于零？

**A**：是的。对于单三角星座，所有 Michelson 通道 $\alpha$（E、T 等）都有 $\gamma^V_\alpha = 0$（由反射对称性证明）。因此 $\sum (\gamma^V_\alpha)^2 = 0$ 且 $\sum \gamma^I_\alpha \gamma^V_\alpha = 0$，整个表达式为 $\sqrt{0 - 0} = 0$。这与定理完全一致。JCAP 给出的有效 ORF 公式是多探测器网络的一般表达式，对单三角星座的退化情况自动给出零结果。

### Q3：Sinc 传递函数是否会影响 Gamma^V = 0 的结论？

**A**：不会。反射对称性论证只依赖于天线方向图的宇称性质（$F_+$ 偶、$F_\times$ 奇），与频率依赖的传递函数形式无关。无论传递函数是 Hu 的指数形式、OLC 的 sinc 形式，还是其他任何频率函数，只要它对两个偏振模式是相同的（这是 GW-物质耦合的普适性保证的），反射对称性就使 $\Gamma^V$ 为零。频率依赖性只影响 $\Gamma^I$ 的幅度和振荡结构。

---

## 7. 结论与启示

1. **严格结论**：任意三卫星三角星座，无论其构型如何（等边、不等边、倾斜、旋转），所有两变量交叉相关的 $\Gamma^V$ 恒为零。这是由三点必然共面的几何约束和反射对称性导致的。

2. **手征性探测条件**：非共面链路方向网络是探测圆极化 SGWB 的必要条件。实际可行的方案包括：多星座网络（如 LISA-Taiji，利用三维空间分离打破对称性）、四面体四卫星构型、或更多卫星的复杂网络。

3. **对 OLC 网络设计的启示**：如果 OLC 网络要具备手征灵敏度，必须采用非共面构型（如多个不同轨道面的三角星座组合）。单三角 OLC 网络只能测量 $\Gamma^I$（总强度），无法探测手征不对称度 $V$。

---

*产出：手征重叠归一化函数 P1-2 笔记*
*完成日期：2026-07-11*
*置信度：0.95 — 反射对称性证明为严格数学论证，代码验证（Iter8）与理论一致，多星座结果（LISA-Taiji）与 JCAP 原文一致*
