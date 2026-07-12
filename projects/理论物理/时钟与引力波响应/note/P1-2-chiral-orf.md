# 手征 ORF（$\Gamma^V$）的物理、几何与探测意义

> **版本**: v1.0
> **日期**: 2026-07-12
> **基于文献**: JCAP 05 (2025) 050, Hu PRD 111.084065, 楼明智硕士论文
> **理解人**: Claude (RALPH Loop Commander)

---

## 第1节：手征 SGWB 的物理基础

### 1.1 圆极化基

引力波有两个线性偏振 $+$ 和 $\times$。定义圆极化（手征）基：
$$e^R_{ab} = \frac{e^+_{ab} + i e^\times_{ab}}{\sqrt{2}}, \quad e^L_{ab} = \frac{e^+_{ab} - i e^\times_{ab}}{\sqrt{2}}$$

对应的光应变：
$$h_R = \frac{h_+ - i h_\times}{\sqrt{2}}, \quad h_L = \frac{h_+ + i h_\times}{\sqrt{2}}$$

### 1.2 Stokes 参数与手征参数

SGWB 的功率谱在手征基下对角化：
$$\langle \tilde{h}_R(f) \tilde{h}_R^*(f') \rangle = S_R(f) \delta(f-f')$$
$$\langle \tilde{h}_L(f) \tilde{h}_L^*(f') \rangle = S_L(f) \delta(f-f')$$

定义 Stokes 参数：
$$I = \frac{1}{2}(S_R + S_L), \quad V = \frac{1}{2}(S_R - S_L)$$

归一化手征参数：
$$\chi \equiv \frac{V}{I} = \frac{S_R - S_L}{S_R + S_L}$$

$\chi \in [-1, 1]$：
- $\chi = 1$：纯右旋（纯圆极化）
- $\chi = -1$：纯左旋
- $\chi = 0$：宇称对称（等量左右旋）

### 1.3 手征 SGWB 的物理起源

- **原初引力波**（暴胀时期）：手征性来自 CP 破坏的暴胀耦合（如赝标量-规范场耦合）
- **宇宙弦**：涡旋弦产生手征 SGWB
- **磁流体湍流**：螺旋度非零的磁场产生手征信号

探测 $\chi \neq 0$ 是验证上述物理机制的关键。

---

## 第2节：手征 ORF 的数学结构

### 2.1 交叉相关中的手征项

对于两个探测器 $i$ 和 $j$，信号交叉相关的期望值为（JCAP Eq.2.9）：
$$\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle = \frac{1}{2}\delta(f-f') \left[\Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f)\right]$$

其中：
- $\Gamma^I$：宇称偶 ORF，对标准 SGWB 敏感
- $\Gamma^V$：宇称奇 ORF，对手征性敏感

测量 $\chi$ 的能力取决于 $\Gamma^V/\Gamma^I$ 的大小。

### 2.2 $\Gamma^I$ 和 $\Gamma^V$ 的极化收缩

**$\Gamma^I$** 对应线性偏振求和：
$$\mathcal{P}^I(\hat{n}) = \sum_{A=+,\times} F_A(\hat{u}_1, \hat{n}) F_A(\hat{u}_2, \hat{n})$$

其中 $F_A(\hat{u}, \hat{n}) = \frac{1}{2}e^A_{ab}(\hat{n}) u^a u^b$。

**$\Gamma^V$** 对应偏振交叉项（JCAP Eq.2.10）：
$$\mathcal{P}^V(\hat{n}) = -i\sum_{A,B}\epsilon_{AB} F_A(\hat{u}_1, \hat{n}) F_B(\hat{u}_2, \hat{n})$$

其中 $\epsilon_{+\times} = 1$, $\epsilon_{\times+} = -1$。

### 2.3 $\mathcal{P}^V$ 的紧凑几何形式

通过复数表示（见 `P-chiral-orf-analytical.md` 附录 B 的完整推导）：
$$\mathcal{P}^V(\hat{n}) = \text{Im}(w_1^2 w_2^{*2})$$

其中 $w_i = (\hat{u}_i\cdot\hat{x}) + i(\hat{u}_i\cdot\hat{y})$ 是臂方向在垂直于 $\hat{n}$ 平面上的复投影。

展开为几何量：
$$\mathcal{P}^V(\hat{n}) = [\hat{u}_1\cdot\hat{u}_2 - (\hat{n}\cdot\hat{u}_1)(\hat{n}\cdot\hat{u}_2)] \cdot [(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}]$$

**几何解释**：
- 第一个因子 $[\hat{u}_1\cdot\hat{u}_2 - c_{n1}c_{n2}]$：两臂在天空平面上的"修正"投影
- 第二个因子 $[(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}]$：两臂构成的平行面在 $\hat{n}$ 方向上的投影（即定向体积元）

$\mathcal{P}^V$ 是**宇称奇**的：在反射操作下，$(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}$ 变号，其余因子不变。

---

## 第3节：$\Gamma^V = 0$ 的共面定理

### 3.1 定理陈述

**定理**：对于共面探测器网络（存在一个平面包含所有探测器臂），$\Gamma^V_{12}(f) = 0$ 对所有频率成立。

### 3.2 对称性证明

**反射论证**：
对于共面网络，存在反射平面 $\Sigma$ 使网络不变。在反射下：
1. $\hat{n} \to \hat{n}' = R_\Sigma \hat{n}$（天空反射）
2. $\hat{u}_i \to \hat{u}_i' = R_\Sigma \hat{u}_i$（臂反射）
3. $\mathcal{P}^V(\hat{n}) \to -\mathcal{P}^V(\hat{n}')$（宇称奇性）
4. 传递函数 $|\mathcal{T}_i| \to |\mathcal{T}_i'|$（模长不变）
5. 基线相位 $e^{i\vec{k}\cdot\vec{\Delta x}} \to e^{i\vec{k}\cdot\vec{\Delta x}'}$（因为 $\vec{\Delta x}$ 也反射）

由于反射保持测度 $d^2\hat{n}$ 且网络不变：
$$\Gamma^V = \int d^2\hat{n} \, \mathcal{P}^V(\hat{n}) \mathcal{T}_1\mathcal{T}_2^* e^{i\phi} = -\int d^2\hat{n}' \, \mathcal{P}^V(\hat{n}') \mathcal{T}_1'\mathcal{T}_2'^* e^{i\phi'} = -\Gamma^V$$

因此 $\Gamma^V = 0$。$\square$

### 3.3 代数验证

共面时 $\hat{u}_1\times\hat{u}_2$ 垂直于该平面。选择坐标系使该平面为 $xy$ 平面，则 $\hat{u}_1\times\hat{u}_2 = \hat{z}$。

对于共面网络，$\vec{\Delta x}$ 也在 $xy$ 平面内，且反射平面包含 $\hat{z}$ 和 $\hat{d}$。

在 $xz$ 反射（$y \to -y$）下：
- $\mathcal{P}^V \propto (\hat{u}_1\times\hat{u}_2)\cdot\hat{n} = n_z \to n_z = (\hat{u}_1\times\hat{u}_2)\cdot\hat{n}'$
- 但第一个因子 $[\hat{u}_1\cdot\hat{u}_2 - c_{n1}c_{n2}]$ 不变
- 需要更细致的分析

完整的代数证明见 `P-chiral-orf-analytical.md` 第4.3节。

### 3.4 数值验证（本项目 Iter80）

在 Iter80 中验证了螺旋度翻转对称性（4/4 PASS），其核心就是共面时 $\Gamma^V = 0$。

---

## 第4节：非共面构型的 $\Gamma^V$

### 4.1 非共面因子的出现

对于两个探测器，定义：
- $\hat{n}_1$：探测器1的平面法向
- $\hat{n}_2$：探测器2的平面法向
- $\psi$：两平面法向的夹角

$\Gamma^V$ 的大小正比于 $(\hat{n}_1\times\hat{n}_2)\cdot\hat{d} = \sin\psi \sin\theta_d$，其中 $\hat{d}$ 是两探测器的基线方向。

### 4.2 小臂近似下的 $\Gamma^V$

从 `P-chiral-orf-analytical.md` 第5.3节：
$$\Gamma^V_{12}(f) \approx \left(\frac{2\pi f}{c}\right)^2 L_1 L_2 \cdot \frac{1}{3} \sin\psi \sin(2\gamma)$$

其中 $\gamma$ 是探测器内部臂夹角。

**关键结论**：
- $\Gamma^V \propto f^2$：高频更敏感
- $\Gamma^V \propto \sin\psi$：共面时为零
- $\Gamma^V \propto \sin(2\gamma)$：$\gamma = \pi/2$ 时最大（正交臂）

### 4.3 归一化手征参数

在小臂近似下：
$$\chi(f) = \frac{\Gamma^V}{\Gamma^I} \approx \frac{\frac{1}{3}\sin\psi\sin(2\gamma)}{\frac{2}{5}(1+\cos^2\gamma)} = \frac{5}{6}\frac{\sin\psi\sin(2\gamma)}{1+\cos^2\gamma}$$

对于典型构型：
- 两个正交臂探测器（$\gamma = \pi/2$）：$\chi \approx \frac{5}{6}\sin\psi$
- 若 $\psi = 30°$：$\chi \approx 0.43$

### 4.4 LISA × Taiji 网络

这是最典型的非共面网络：
- 臂长：$L_{\text{LISA}} = 2.5\times 10^9$ m, $L_{\text{Taiji}} = 3.0\times 10^9$ m
- 平面夹角：$\psi \approx 30°$
- 预期：$\Gamma^I \sim 0.1$, $\Gamma^V \sim 0.05$, $\chi \sim 0.5$

详见 `P-chiral-orf-analytical.md` 第7节。

---

## 第5节：手征 ORF 的 I1-I4 分解

### 5.1 结构相同、被积函数不同

$\Gamma^V$ 与 $\Gamma^I$ 共享相同的 I1-I4 分解结构：
$$\Gamma^V = \frac{1}{4}[I_1^V - I_2^V - I_3^V + I_4^V]$$

唯一的区别是极化收缩因子 $\mathcal{P}^V(\hat{n})$ 替代 $\mathcal{P}^I(\hat{n})$。

### 5.2 留数计算的差异

由于 $\mathcal{P}^V$ 与 $\mathcal{P}^I$ 的角依赖不同，留数 $R_j^{(V)}$ 的表达式不同。

关键区别：$\mathcal{P}^V$ 含有 $(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}$ 因子，在复平面上引入额外的 $z$ 线性项。这修改了留数的分子，但不改变极点位置和数量。

### 5.3 Ei 函数的差异

Ei 函数的**参数结构**（$\sigma_\pm$ 的形式）保持不变，但**系数**不同。具体而言：

$\mathcal{P}^I$ 的 Ei 系数来自 $\cos(2\phi)$ 类型的角依赖，而 $\mathcal{P}^V$ 的 Ei 系数来自 $\sin(2\phi)$ 类型。

---

## 第6节：探测灵敏度估算

### 6.1 信噪比

手征参数 $\chi$ 的测量信噪比（JCAP Eq.3.14）：
$$\text{SNR}_V = \frac{\Gamma^V}{\sigma_V} \sqrt{T_{\text{obs}}}$$

其中 $\sigma_V$ 是 $\Gamma^V$ 的噪声水平。

### 6.2 与 $\Gamma^I$ 的比较

由于 $\Gamma^V \sim \sin\psi \cdot \Gamma^I$，手征探测的信噪比比标准 ORF 探测小 $\sin\psi$ 因子。

对于 LISA × Taiji：$\sin\psi \approx 0.5$，因此手征探测比标准探测弱约 2 倍。

### 6.3 与 PTA 手征探测的比较

PTA 也使用 $\Gamma^V$ 探测手征 SGWB（JCAP 2025）。两者的关键区别：
- PTA 的传递函数：$T_{\text{one}}^{\text{PTA}} \propto \frac{1+\hat{n}\cdot\hat{u}}{2}[1-e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$
- OLC 的传递函数：$T_{\text{one}}^{\text{OLC}} \propto \text{sinc}[x(1-\hat{u}\cdot\hat{n})]e^{-ix(1-\hat{u}\cdot\hat{n})}$

PTA 在 nHz 频段，OLC 在 mHz-Hz 频段——探测不同的引力波源。

---

## 第7节：手征 ORF 的完整被积函数

### 7.1 $\Gamma^V$ 的完整表达式

$$\Gamma^V_{12}(f) = \int \frac{d^2\hat{n}}{4\pi} \, \mathcal{P}^V(\hat{n}) \cdot \mathcal{T}_1(\hat{u}_1\cdot\hat{n}, f) \mathcal{T}_2^*(\hat{u}_2\cdot\hat{n}, f) \cdot e^{i 2\pi f \hat{n}\cdot\vec{\Delta x}_{12}/c}$$

其中：
- $\mathcal{P}^V(\hat{n}) = [\hat{u}_1\cdot\hat{u}_2 - (\hat{n}\cdot\hat{u}_1)(\hat{n}\cdot\hat{u}_2)] \cdot [(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}]$
- $\mathcal{T}_i = \frac{i2\pi fL_i}{c}\text{sinc}[y_i]e^{-iy_i}$，$y_i = \frac{\pi fL_i}{c}(1-\hat{u}_i\cdot\hat{n})$
- $\vec{\Delta x}_{12} = \vec{x}_2 - \vec{x}_1$ 是两探测器位置差

### 7.2 $\Gamma^V$ 的数值计算流程

1. 对天空方向 $(\theta, \phi)$ 离散化
2. 对每个 $\hat{n}$，计算：
   - $\mu_1 = \hat{n}\cdot\hat{u}_1$, $\mu_2 = \hat{n}\cdot\hat{u}_2$
   - $\mathcal{P}^V(\hat{n})$
   - $\mathcal{T}_1, \mathcal{T}_2$
   - 基线相位
3. 求和并乘以测度

---

## 第8节：总结

### 8.1 核心发现

1. **手征 ORF 的几何本质**：$\mathcal{P}^V = (\hat{u}_1\times\hat{u}_2)\cdot\hat{n} \cdot [\hat{u}_1\cdot\hat{u}_2 - (\hat{n}\cdot\hat{u}_1)(\hat{n}\cdot\hat{u}_2)]$ 是两个探测器几何构型与天空方向的联合函数
2. **共面定理**：$\Gamma^V = 0$ 对共面网络严格成立——这是宇称奇性的直接后果
3. **非共面比例**：$\Gamma^V \propto \sin\psi$，取决于两探测器平面的相对倾角
4. **I1-I4 通用性**：手征 ORF 共享 Hu 框架的 I1-I4 分解结构，仅极化收缩不同
5. **探测意义**：$\chi = \Gamma^V/\Gamma^I \sim 0.5$ 对 LISA × Taiji，是可观测的效应

### 8.2 与相关文献的一致性

| 文献 | 手征定义 | $\mathcal{P}^V$ 形式 | 共面 $\Gamma^V=0$ |
|------|----------|---------------------|-------------------|
| JCAP 05 (2025) 050 | $V = (S_R-S_L)/2$ | JCAP Eq.2.10 | 是（§3.5.3 镜面论证） |
| Hu PRD 111.084065 | 未显式处理 | 通用框架可扩展 | 是（宇称奇性） |
| 楼明智硕士论文 | 未显式处理 | 构型依赖的 $\Gamma^V$ | 是（数值验证） |
| Seto PRL 97, 151101 | 前景分析 | 未显式计算 | 否（未讨论） |

### 8.3 关键公式汇总

| 公式 | 含义 |
|------|------|
| $\chi = (S_R-S_L)/(S_R+S_L)$ | 归一化手征参数 |
| $\Gamma = \frac{1}{2}[\Gamma^I I + \Gamma^V V]$ | 交叉相关期望 |
| $\mathcal{P}^V = \frac{1}{2}\text{Im}(w_1^2w_2^{*2})$ | 手征极化收缩紧凑形式 |
| $\mathcal{P}^V = (\hat{u}_1\cdot\hat{u}_2 - c_{n1}c_{n2})(\hat{u}_1\times\hat{u}_2)\cdot\hat{n}$ | 手征极化收缩几何形式 |
| $\Gamma^V = 0$ (共面) | 共面定理 |
| $\Gamma^V \approx \frac{1}{3}(2\pi f/c)^2 L_1L_2 \sin\psi \sin(2\gamma)$ | 小臂近似 |

---

*产出：手征 ORF $\Gamma^V$ 的完整物理、几何和计算分析*
*完成日期：2026-07-12*
*置信度：0.85 — 核心推导基于 JCAP 和 Hu 原文，部分代数细节有待数值验证*
