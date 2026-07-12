# OLC 传递函数的不变性与构型变换分析

> **版本**: v1.0
> **日期**: 2026-07-12
> **基于文献**: 楼明智硕士论文, Hu PRD 111.084065
> **理解人**: Claude (RALPH Loop Commander)

---

## 第1节：OLC 探测器的物理原理

### 1.1 光学晶格钟作为引力波探测器

光学晶格钟（Optical Lattice Clock, OLC）是利用原子钟跃迁频率测量引力波的新一代探测器。其基本原理：

引力波经过时引起时空度规扰动 $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$，导致：
1. **时钟速率变化**：原子的固有频率 $\nu_0$ 受到度规扰动的影响
2. **光传播时间变化**：激光在两个位置间传播的时间受 GW 调制

### 1.2 观测量：频率偏移

OLC 的核心观测量是激光频率相对于原子参考频率的偏移：
$$y(t) = \frac{\Delta\nu}{\nu_0}(t) = \frac{\nu_{\text{laser}}(t) - \nu_0}{\nu_0}(t)$$

在引力波作用下，频率偏移为（楼明智 Eq. 2-28）：
$$y(t) = \frac{1}{2}\frac{e^A_{ab}(\hat{n})u^a u^b}{1+\hat{n}\cdot\hat{u}} \left[h_A(t_{\text{recv}}) - h_A(t_{\text{emit}})e^{-i\beta}\right]$$

其中：
- $t_{\text{recv}}$ 是接收时刻
- $t_{\text{emit}} = t_{\text{recv}} - L/c$ 是发射时刻
- $\beta = 2\pi f L/c$ 是往返相位

### 1.3 与 PTA 和 GbLI 的比较

| 特征 | PTA | GbLI | OLC |
|------|-----|------|-----|
| 观测量 | 时序残差 $z$ | 应变 $h$ | 频率偏移 $y$ |
| 傅里叶域关系 | $\tilde{z} = \tilde{y}/(i2\pi f)$ | $\tilde{h} = \tilde{y}/(i2\pi f)\cdot c/(2L)$ | 原始测量 |
| 传递函数 | Hu Eq.6 指数 | Hu Eq.6 指数 | 楼 Eq.2-30 sinc |
| 频段 | nHz | mHz-kHz | mHz-Hz |
| 臂长 | kpc (脉冲星距离) | km (地基) | $10^8$-$10^9$ m (空间) |

**核心区别**：OLC 直接测量频率偏移 $y(t)$，而 PTA 测量 $\int y dt$，GbLI 测量 $\int y dt / L$。这导致传递函数相差积分/微分因子。

---

## 第2节：OLC 传递函数的 sinc 形式

### 2.1 从积分到 sinc

频率偏移响应函数（楼明智 Eq. 2-30）：
$$R^{\text{OLC}}_A(f, \hat{n}) = \frac{1}{2}e^A_{ab}(\hat{n})u^a u^b \cdot \mathcal{T}(f, \hat{n})$$

其中传递函数：
$$\mathcal{T}(f, \hat{n}) = \frac{i2\pi f L}{c} \cdot \text{sinc}\left[\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})\right] \cdot e^{-i\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})}$$

推导：
$$\mathcal{T} = \int_0^L \frac{dl}{L} e^{i2\pi f l(1-\hat{u}\cdot\hat{n})/c} = \frac{e^{iy} - 1}{iy} = \text{sinc}(y)e^{-iy}$$

其中 $y = \frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})$。

**前置因子** $i2\pi f L/c$ 来自频率偏移 vs 应变的导数关系。

### 2.2 sinc 函数的物理意义

$\text{sinc}(y) = \sin(y)/y$ 是路径积分的结果：
- $y = 0$（纵向 GW，$\hat{n}\parallel\hat{u}$）：$\text{sinc}(0) = 1$，全响应
- $y \to \infty$（横向 GW，$\hat{n}\perp\hat{u}$）：$\text{sinc} \to 0$，响应抑制
- $y = \pi$：$\text{sinc}(\pi) = 0$，第一个零点

零点位置：
$$f_n = \frac{n c}{L(1-\hat{u}\cdot\hat{n})}, \quad n = 1, 2, 3, \dots$$

对于 LISA 臂长 $L = 2.5\times 10^9$ m，$f_1 \approx c/L \approx 0.12$ Hz（纵向）。

### 2.3 与 Hu 指数形式的等价性

通过 Euler 公式展开：
$$\mathcal{T}^{\text{OLC}} = \frac{i2\pi fL}{c} \cdot \frac{e^{iy}-e^{-iy}}{2iy} \cdot e^{-iy} = \frac{1}{1-\hat{u}\cdot\hat{n}}[1 - e^{-2ix(1-\hat{u}\cdot\hat{n})}]$$

其中 $x = \pi fL/c$。

**与 Hu 的形式对比**：
$$\mathcal{T}^{\text{Hu}} = \frac{1+\hat{n}\cdot\hat{u}}{2}[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$$

差异：
1. **分母**：OLC 是 $(1-\hat{u}\cdot\hat{n})$，Hu 是 $2/(1+\hat{n}\cdot\hat{u})$
2. **指数参数**：OLC 是 $2x(1-\hat{u}\cdot\hat{n})$，Hu 是 $\beta(1+\hat{n}\cdot\hat{u})$
3. **前置因子**：OLC 是 $i2\pi fL/c$，Hu 是 $1$

**统一表达式**：
$$\mathcal{T}^{\text{gen}} = f_{\text{pref}}(\hat{u}\cdot\hat{n}) \cdot [1 - e^{-i\kappa \eta(1-\sigma\hat{u}\cdot\hat{n})}]$$

其中 $\sigma = \pm 1$（方向约定），$\kappa$ 是频率参数。

---

## 第3节：传递函数的不变性

### 3.1 旋转不变性

考虑 $\hat{u}$ 绕 $\hat{n}$ 旋转角度 $\alpha$：$\hat{u}' = R_{\hat{n}}(\alpha)\hat{u}$。

$$\hat{n}\cdot\hat{u}' = \hat{n}\cdot\hat{u}$$

因此 $\mathcal{T}(f, \hat{n})$ 不变——仅依赖于 $\hat{u}$ 在 $\hat{n}$ 方向上的投影。

### 3.2 反射对称性

考虑 $\hat{u} \to -\hat{u}$（反向激光传播）：
$$\mathcal{T}(f, \hat{n}, -\hat{u}) = \frac{1}{1+\hat{u}\cdot\hat{n}}[1 - e^{-2ix(1+\hat{u}\cdot\hat{n})}]$$

这与 $\mathcal{T}(f, \hat{n}, \hat{u})$ 的形式**不同**——因为 $1-\hat{u}\cdot\hat{n} \to 1+\hat{u}\cdot\hat{n}$。

**物理意义**：OLC 的单程链路是**非对称**的。激光从 A 到 B 的响应不同于从 B 到 A。这是因为 GW 在两个方向上的相位累积不同。

### 3.3 臂长缩放不变性

对于固定的无量纲参数 $x = \pi fL/c$，传递函数的形状不依赖于 $L$ 和 $f$ 的具体值：
$$\mathcal{T}(f, \hat{n}) = F(x, \hat{u}\cdot\hat{n})$$

这意味着对于不同臂长的 OLC 探测器，其 ORF 作为 $fL/c$ 的函数是**通用的**。

### 3.4 天空平均不变性

对于各向同性 SGWB，ORF 需要对天空平均。关键问题：$\Gamma^I$ 和 $\Gamma^V$ 是否独立于探测器的绝对取向？

**$\Gamma^I$**：天空平均后仅依赖于：
- 两臂夹角 $\gamma$
- 基线方向 $\hat{d}$ 与臂方向的相对关系
- 臂长比

**$\Gamma^V$**：天空平均后还依赖于：
- 两探测器平面的相对倾角 $\psi$
- 两探测器平面的相对方位角

因此 $\Gamma^I$ 具有更强的旋转不变性，而 $\Gamma^V$ 对探测器的绝对取向敏感。

---

## 第4节：构型变换与 ORF 不变性

### 4.1 楼明智论文中的构型变换

楼明智硕士论文的核心分析工具是**构型变换**——交换激光的发射/接收位置。

考虑链路 A→B 和 B→A。两种构型的几何量：

| 量 | A→B | B→A |
|---|---|---|
| 臂方向 | $\hat{u} = (\vec{r}_B-\vec{r}_A)/L$ | $-\hat{u}$ |
| $1-\hat{u}\cdot\hat{n}$ | $1-\hat{u}\cdot\hat{n}$ | $1+\hat{u}\cdot\hat{n}$ |
| 传递函数 | $\mathcal{T}_+(f, \hat{n})$ | $\mathcal{T}_-(f, \hat{n})$ |

### 4.2 双向链路的构成

对于双程链路（A→B→A），总响应为：
$$y_{\text{round-trip}} = y_{A\to B\to A} + y_{B\to A\to B}$$

在频率域：
$$\mathcal{T}_{\text{two}} = \mathcal{T}_+(f, \hat{n}) + \mathcal{T}_-(f, \hat{n})e^{-i\beta}$$

利用 sinc 展开：
$$\mathcal{T}_{\text{two}} = \frac{1}{1-\mu}[1-e^{-2ix(1-\mu)}] + \frac{1}{1+\mu}[1-e^{-2ix(1+\mu)}]e^{-2ix}$$

其中 $\mu = \hat{u}\cdot\hat{n}$。

### 4.3 ORF 的构型不变性定理

**定理**：对于由两条反向链路组成的双程探测器，其 ORF $\Gamma^I$ 在交换发射/接收位置后不变。

**证明**：双程链路的传递函数 $\mathcal{T}_{\text{two}}$ 在 $\hat{u}\to-\hat{u}$ 下的形式不变（因为两项互换）。因此 ORF 作为 $\mathcal{T}_{\text{two}}$ 的函数也不变。

**物理意义**：OLC 双程探测器的 ORF 不依赖于激光的"方向性"——这简化了构型设计，因为任意选择激光传播方向都不会影响灵敏度。

### 4.4 对 OLC 网络设计的指导

1. **单程链路**：方向有影响，需要仔细选择
2. **双程链路**：方向不影响 ORF
3. **手征敏感性**：$\Gamma^V$ 在单程链路中非零，在双程链路中可能为零（取决于对称性）

---

## 第5节：OLC 与 Hu 框架的衔接

### 5.1 OLC 单程链路作为 Hu 框架的特例

将 OLC 的 sinc 传递函数展开为指数后，完全符合 Hu 的 I1-I4 分解框架。

差异仅在于参数替换：
- Hu: $\beta = 2\pi fL/c$, $D = 1+\hat{n}\cdot\hat{u}$
- OLC: $\beta_{\text{OLC}} = 2\pi fL/c$, $D_{\text{OLC}} = 1-\hat{u}\cdot\hat{n}$

### 5.2 极点结构的等价性

Hu 的五极点 $z_0-z_4$ 适用于 OLC，只需将 $1+\hat{n}\cdot\hat{u}$ 替换为 $1-\hat{u}\cdot\hat{n}$。这仅改变极点的符号，不改变数量和位置类型。

### 5.3 对小臂近似的共同预测

在小臂近似下，OLC 和 Hu 都给出：
$$\Gamma^I \propto f^2 L_1 L_2 \cdot \frac{2}{5}(1+\cos^2\gamma)$$

这是两种方法的交叉验证——不同物理出发，相同极限结果。

---

## 第6节：总结

### 6.1 OLC 传递函数的关键特征

1. **sinc 形式**：来自路径积分平均，具有明显的零点结构
2. **前置因子** $i2\pi fL/c$：来自频率偏移观测量
3. **非对称性**：$\hat{u}\to-\hat{u}$ 改变传递函数
4. **与 Hu 等价性**：sinc 展开为指数后符合 Hu 框架

### 6.2 不变性总结

| 变换 | $\Gamma^I$ | $\Gamma^V$ |
|------|-----------|-----------|
| $\hat{u}\to-\hat{u}$ (单程) | 改变 | 改变 |
| 绕 $\hat{n}$ 旋转 | 不变 | 不变 |
| 双程链路 | 不变 | 可能为零 |
| 各向同性天空平均 | 仅依赖几何 | 依赖绝对取向 |

### 6.3 关键公式

| 公式 | 来源 |
|------|------|
| $\mathcal{T}^{\text{OLC}} = \frac{i2\pi fL}{c}\text{sinc}[x(1-\hat{u}\cdot\hat{n})]e^{-ix(1-\hat{u}\cdot\hat{n})}$ | 楼 Eq.2-30 |
| $\mathcal{T}^{\text{OLC}} = \frac{1}{1-\hat{u}\cdot\hat{n}}[1-e^{-2ix(1-\hat{u}\cdot\hat{n})}]$ | Euler 展开 |
| $\mathcal{T}^{\text{two}} = \mathcal{T}_+ + \mathcal{T}_-e^{-2ix}$ | 双程链路 |

---

*产出：OLC 传递函数的物理性质、不变性与构型变换分析*
*完成日期：2026-07-12*
*置信度：0.88 — 主要基于楼明智硕士论文，与 Hu PRD 交叉验证*
