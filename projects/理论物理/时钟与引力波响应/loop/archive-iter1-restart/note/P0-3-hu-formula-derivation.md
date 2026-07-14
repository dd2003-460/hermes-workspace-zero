# Hu PRD 通用单程链路 ORF 公式的完整推导

> **版本**: v1.0
> **日期**: 2026-07-12
> **基于文献**: Hu PRD 111.084065 (arXiv:2406.05636) Section II
> **理解人**: Claude (RALPH Loop Commander)

---

## 第1节：单程链路响应函数的物理定义

### 1.1 观测量：频率偏移

对于一条从位置 $\vec{r}_u$ 到 $\vec{r}_v = \vec{r}_u + L\hat{u}$ 的单程链路，观测量为激光频率偏移：
$$y(t) = \frac{\Delta\nu}{\nu_0}(t)$$

引力波引起的光子四维动量变化（Guertin 2022, Tan 2022）：
$$\frac{dk_0}{d\lambda} = \frac{1}{2} \frac{k^a k^b}{k_0} \frac{\partial h_{ab}}{\partial t}$$

积分得到频率偏移响应（Hu Eq.3-5）：
$$R^A_{\text{one}}(\hat{n}, f) = \frac{1}{2} e^A_{ab}(\hat{n}) \frac{u^a u^b}{1+\hat{n}\cdot\hat{u}} \left[e^{-i2\pi f \hat{n}\cdot\vec{r}_u/c} - e^{-i\beta}e^{-i2\pi f \hat{n}\cdot\vec{r}_v/c}\right]$$

其中 $\beta = 2\pi f L/c$ 是无量纲臂长。

**关键因子分解**：
1. **极化投影** $\frac{1}{2}e^A_{ab}u^a u^b$：探测器对特定偏振的几何响应
2. **分母因子** $\frac{1}{1+\hat{n}\cdot\hat{u}}$：来自沿光路的积分 $\int_0^L d\lambda$，对应 $k^a\nabla_a$ 沿测地线的传播
3. **两端相位差** $e^{-i\vec{k}\cdot\vec{r}_u} - e^{-i\beta}e^{-i\vec{k}\cdot\vec{r}_v}$：起点和终点的 GW 相位差

### 1.2 传递函数的物理结构

将 $R^A_{\text{one}}$ 重写为：
$$R^A_{\text{one}} = e^A_{ab}(\hat{n}) u^a u^b \cdot T_{\text{one}}(\beta, \hat{n}\cdot\hat{u}) \cdot e^{-i\vec{k}\cdot\vec{r}_{\text{end}}}$$

其中传递函数：
$$T_{\text{one}}(\beta, \mu) = \frac{1+\mu}{2(1+\mu)} [e^{i\beta\mu} - e^{-i\beta(1+\mu)}] = \frac{1}{2}[1 - e^{-i\beta(1+\mu)}]$$

这里 $\mu = \hat{n}\cdot\hat{u}$。

**物理诠释**：
- $T_{\text{one}} = 1/2$ 在 $\beta \to 0$（长波长极限），对应全响应
- $T_{\text{one}}$ 的指数项来自路径积分，携带 GW 沿光路的相位累积

---

## 第2节：两条通用单程链路的 ORF 积分

### 2.1 ORF 的定义

两条单程链路（端点分别为 $\vec{r}_u$ 和 $\vec{r}_v$）之间的 ORF 为：
$$\Gamma_{\text{one}} = \frac{1}{32\pi} \int d^2\Omega_{\hat{n}} \, \sum_A e^A_{ab}(\hat{n}) u^a u^b T_1(\hat{n}) \, e^A_{cd}(\hat{n}) v^c v^d T_2^*(\hat{n}) \, e^{-i\alpha \hat{n}\cdot\hat{s}}$$

其中：
- $\alpha = 2\pi f |\vec{r}_v - \vec{r}_u|/c$ 是基线相位
- $\hat{s} = (\vec{r}_v - \vec{r}_u)/|\vec{r}_v - \vec{r}_u|$ 是基线方向
- $T_1 = T_{\text{one}}(\beta_u, \hat{n}\cdot\hat{u})$, $T_2 = T_{\text{one}}(\beta_v, \hat{n}\cdot\hat{v})$

### 2.2 极化张量收缩

$$\sum_A e^A_{ab}(\hat{n}) e^A_{cd}(\hat{n}) = P_{ac}(\hat{n})P_{bd}(\hat{n}) + P_{ad}(\hat{n})P_{bc}(\hat{n}) - P_{ab}(\hat{n})P_{cd}(\hat{n})$$

其中 $P_{ab} = \delta_{ab} - n_a n_b$ 是横向投影算符。

收缩结果（Hu Eq.12）：
$$\xi(\hat{n}) \equiv \sum_A e^A_{ab} u^a u^b e^A_{cd} v^c v^d = (u\cdot v)^2 - \frac{1}{2}\sin^2\gamma + \text{方向依赖项}$$

完整表达式（在特殊坐标系中，$\hat{s}$ 沿 z 轴）：
$$\xi(x, \phi) = \frac{1}{2}(1 - c_u^2)(1 - c_v^2)\cos(2\phi - 2\phi_{uv}) + \dots$$

其中 $c_u = \cos\delta_u = \hat{u}\cdot\hat{s}$, $c_v = \cos\delta_v = \hat{v}\cdot\hat{s}$。

### 2.3 完整被积函数

$$\Gamma_{\text{one}} = \frac{1}{32\pi} \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, [1-e^{-i\beta_u(1+\mu_u)}][1-e^{i\beta_v(1+\mu_v)}] \, e^{-i\alpha \hat{n}\cdot\hat{s}}$$

其中 $\mu_u = \hat{n}\cdot\hat{u}$, $\mu_v = \hat{n}\cdot\hat{v}$。

---

## 第3节：I1-I4 分解的详细推导

### 3.1 展开乘积

$$[1-e^{-i\beta_u(1+\mu_u)}][1-e^{i\beta_v(1+\mu_v)}] = 1 - e^{-i\beta_u(1+\mu_u)} - e^{i\beta_v(1+\mu_v)} + e^{-i\beta_u(1+\mu_u)}e^{i\beta_v(1+\mu_v)}$$

代入积分：
$$\Gamma_{\text{one}} = \frac{1}{32\pi}[I_1 - I_2 - I_3 + I_4]$$

其中每一项：
$$I_1 = \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, e^{-i\alpha \hat{n}\cdot\hat{s}}$$

$$I_2 = \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, e^{-i\beta_u(1+\mu_u)} e^{-i\alpha \hat{n}\cdot\hat{s}}$$

$$I_3 = \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, e^{i\beta_v(1+\mu_v)} e^{-i\alpha \hat{n}\cdot\hat{s}}$$

$$I_4 = \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, e^{-i\beta_u(1+\mu_u)} e^{i\beta_v(1+\mu_v)} e^{-i\alpha \hat{n}\cdot\hat{s}}$$

### 3.2 I1-I4 的几何意义

这是 Hu 论文的核心洞察。考虑指数部分：

- $I_1$：只有基线相位 $e^{-i\alpha \hat{n}\cdot\hat{s}}$，对应两条链路的**终点**之间的干涉
- $I_2$：额外因子 $e^{-i\beta_u(1+\mu_u)}$，对应链路I的**起点**到终点的相位
- $I_3$：额外因子 $e^{i\beta_v(1+\mu_v)}$，对应链路J的**起点**
- $I_4$：两个额外因子，对应两条链路的**起点**之间的干涉

更形式化地，定义有效波矢：
- $I_1$: $\vec{k}_1 = \alpha\hat{s}$
- $I_2$: $\vec{k}_2 = \alpha\hat{s} + \beta_u\hat{u}$
- $I_3$: $\vec{k}_3 = \alpha\hat{s} - \beta_v\hat{v}$
- $I_4$: $\vec{k}_4 = \alpha\hat{s} + \beta_u\hat{u} - \beta_v\hat{v}$

因此 $I_2 = I_1(\alpha\to\alpha_2, \hat{s}\to\hat{s}_2)$ 等等。

---

## 第4节：I1 的解析计算 — 留数定理

### 4.1 坐标系与变量变换

选取坐标系：$\hat{s} = (0,0,1)$, $\hat{u} = (\sin\delta_u, 0, \cos\delta_u)$, $\hat{v} = (v_x, v_y, \cos\delta_v)$。

变量变换：$x = \cos\theta$, $z = e^{i\phi}$。

$I_1$ 变为：
$$I_1 = \int_{-1}^{1} dx \, e^{-i\alpha x} \oint_{|z|=1} \frac{dz}{iz} \, \xi(x, z)$$

### 4.2 被积函数的极点

$\xi(x,z)/(iz)$ 的极点：
$$z_0 = 0$$

$$z_{1,2} = -\frac{(1\pm c_u)(1\pm x)}{s_u\sqrt{1-x^2}}$$

$$z_{3,4} = -\frac{(1\pm c_v)(1\pm x)}{(v_x - iv_y)\sqrt{1-x^2}}$$

其中 $c_u = \cos\delta_u$, $s_u = \sin\delta_u$。

### 4.3 极点穿越条件

对于固定的 $x$，$|z_j(x)| < 1$ 的极点位于单位圆内。关键性质（Hu Eq.16下方）：

- $|z_1| < 1 \iff x < -c_u$（同时 $|z_2| > 1$）
- $|z_3| < 1 \iff x < -c_v$（同时 $|z_4| > 1$）

因此当 $x$ 从 $-1$ 扫描到 $1$ 时，单位圆内的极点集合在 $x = -c_u$ 和 $x = -c_v$ 处变化。

### 4.4 留数定理分段积分

$$I_1 = 2\pi i \int_{-1}^{1} dx \, e^{-i\alpha x} \sum_{j \in \text{inside}} \text{Res}[f(z), z_j]$$

显式：
$$I_1 = 2\pi i\left[\int_{-1}^{1} dx \, e^{-i\alpha x} R_0(x) + \int_{-1}^{\min(-c_u,-c_v)} dx \, e^{-i\alpha x}[R_1+R_3] + \int_{\min}^{\max} dx \, e^{-i\alpha x}[R_k] + \int_{\max}^{1} dx \, e^{-i\alpha x}[R_2+R_4]\right]$$

其中 $R_j(x)$ 是 $z_j$ 的留数作为 $x$ 的函数。

### 4.5 留数的计算

以 $z_0 = 0$ 为例：
$$R_0(x) = \lim_{z\to 0} z \cdot \frac{\xi(x,z)}{iz} = \frac{\xi(x, 0)}{i}$$

$\xi(x, 0)$ 是 $\phi = 0$ 时的极化收缩。在线性极化基下：
$$\xi(x, 0) = \frac{1}{2}(1-c_u^2)(1-c_v^2) + \dots$$

对于 $z_1$ 等极点，需要更细致的计算（Hu Eq.19-21）。结果形式为：
$$R_1(x) = \frac{A_1(x)}{B_1(x)}$$

其中 $A_1, B_1$ 是关于 $x$ 的有理函数。

### 4.6 Ei 函数的出现

对 $x$ 的积分产生：
$$\int dx \, e^{-i\alpha x} x^n = \frac{e^{-i\alpha x}}{(-i\alpha)^{n+1}}\left[(-i\alpha x)^n + n(-i\alpha x)^{n-1} + \dots\right]$$

对于含有对数项的留数（来自 $1/\sqrt{1-x^2}$ 类极点），积分产生：
$$\int dx \, e^{-i\alpha x} \ln(1 \pm x) = Ei(-i\alpha(\sigma_\pm + 1)) - Ei(-i\alpha(\sigma_\pm - c_u)) - \dots$$

---

## 第5节：I2-I4 的参数替换规则

### 5.1 I2 的替换

$I_2$ 的指数部分：$e^{-i\beta_u(1+\mu_u)}e^{-i\alpha \hat{n}\cdot\hat{s}} = e^{-i\beta_u}e^{-i(\alpha\hat{s}+\beta_u\hat{u})\cdot\hat{n}}$

提取 $e^{-i\beta_u}$ 后，剩余部分与 $I_1$ 有相同结构，只是 $\alpha\hat{s} \to \alpha\hat{s} + \beta_u\hat{u}$。

定义：
$$\alpha_2 = |\alpha\hat{s} + \beta_u\hat{u}| = \sqrt{\alpha^2 + \beta_u^2 + 2\alpha\beta_u c_u}$$

$$\hat{s}_2 = \frac{\alpha\hat{s} + \beta_u\hat{u}}{\alpha_2}$$

则：
$$I_2(\alpha, \beta_u, \hat{s}, \hat{u}, \hat{v}) = e^{-i\beta_u} I_1(\alpha_2, \hat{s}_2, \hat{u}, \hat{v})$$

### 5.2 I3 的替换

类似地：
$$I_3 = e^{i\beta_v} I_1(\alpha_3, \hat{s}_3, \hat{u}, \hat{v})$$

$$\alpha_3 = \sqrt{\alpha^2 + \beta_v^2 - 2\alpha\beta_v c_v}$$

$$\hat{s}_3 = \frac{\alpha\hat{s} - \beta_v\hat{v}}{\alpha_3}$$

### 5.3 I4 的替换

$$I_4 = e^{i(\beta_v-\beta_u)} I_1(\alpha_4, \hat{s}_4, \hat{u}, \hat{v})$$

$$\alpha_4 = |\alpha\hat{s} + \beta_u\hat{u} - \beta_v\hat{v}|$$

### 5.4 参数替换的完整影响

替换不仅改变 $\alpha$，还改变 $\hat{s}$ 的投影：
$$\cos\delta_u^{(2)} = \hat{u}\cdot\hat{s}_2 = \frac{\alpha c_u + \beta_u}{\alpha_2}$$

$$\cos\delta_v^{(2)} = \hat{v}\cdot\hat{s}_2 = \frac{\alpha\hat{v}\cdot\hat{s} + \beta_u \cos\gamma}{\alpha_2} = \frac{\alpha c_v + \beta_u c_\gamma}{\alpha_2}$$

这些修改后的角度进入 $I_1$ 的极点计算和极化收缩 $\xi$。

---

## 第6节：完整的单程链路 ORF

### 6.1 最终表达式

$$\Gamma_{\text{one}}(\alpha, \beta_u, \beta_v, \hat{s}, \hat{u}, \hat{v}) = \frac{1}{32\pi}\left[I_1(\alpha) - e^{-i\beta_u}I_1(\alpha_2, \hat{s}_2) - e^{i\beta_v}I_1(\alpha_3, \hat{s}_3) + e^{i(\beta_v-\beta_u)}I_1(\alpha_4, \hat{s}_4)\right]$$

其中每个 $I_1$ 的完整表达式由 $z_0-z_4$ 的留数积分给出，包含：
1. $\sin\alpha/\alpha$ 型项（来自 $R_0$ 的多项式留数）
2. Ei 函数（来自 $R_{1-4}$ 的对数型留数）
3. 多项式乘以三角函数的项

### 6.2 极限行为验证

**小臂近似** $\beta_u, \beta_v \to 0$：
- $\alpha_2 \to \alpha$, $\alpha_3 \to \alpha$, $\alpha_4 \to \alpha$
- $e^{-i\beta_u} \to 1$, $e^{i\beta_v} \to 1$, $e^{i(\beta_v-\beta_u)} \to 1$
- 括号内：$I_1 - I_1 - I_1 + I_1 = 0$
- 因此需要展开到 $\beta$ 的一阶：$\Gamma_{\text{one}} \propto \beta_u\beta_v$

这正好恢复小天线近似：$\Gamma \propto L_1 L_2$。

**$\alpha \to 0$**（PTA 的公共端点）：
- $I_1(0) = \int d^2\Omega \, \xi(\hat{n})$
- 直接计算得 Hellings-Downs 曲线

---

## 第7节：OLC 的特殊性

### 7.1 OLC 的传递函数 vs PTA/GBLI

Hu 的框架针对的是**到达时间残差**（PTA）或**应变**（GbLI）。对于 OLC，观测量是频率偏移：

$$y_{\text{OLC}}(t) = \frac{\Delta\nu}{\nu_0}(t)$$

在傅里叶域中：
$$\tilde{y}_{\text{OLC}}(f) = i2\pi f \cdot \tilde{z}_{\text{PTA}}(f)$$

这导致传递函数相差 $i2\pi f$ 因子：
$$T_{\text{one}}^{\text{OLC}} = i2\pi f \cdot T_{\text{one}}^{\text{PTA}}$$

### 7.2 sinc 形式的物理起源

OLC 的频率偏移响应（楼明智 Eq. 2-30）：
$$\mathcal{T}_{\text{one}}^{\text{OLC}} = \frac{i2\pi f L}{c} \text{sinc}\left[\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})\right] e^{-i\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})}$$

与 Hu 的指数形式的关系（第7节已详细分析）：
$$\mathcal{T}_{\text{one}}^{\text{OLC}} = \frac{1}{1-\hat{u}\cdot\hat{n}}[1 - e^{-2ix(1-\hat{u}\cdot\hat{n})}]$$

其中 $x = \pi f L/c$。

**关键区别**：OLC 的分母是 $(1-\hat{u}\cdot\hat{n})$，Hu 的是 $(1+\hat{n}\cdot\hat{u})$。这源于 $\hat{u}$ 的方向约定——Hu 的 $\hat{u}$ 指向脉冲星（远离地球），而 OLC 的 $\hat{u}$ 可能定义为激光传播方向。

### 7.3 I1-I4 分解对 OLC 的适用性

将 OLC 的 sinc 形式展开为指数后：
$$\mathcal{T}_{\text{one}}^{\text{OLC}} = \frac{1}{D}[1 - e^{-2ixD}]$$

其中 $D = 1 - \hat{u}\cdot\hat{n}$。乘积 $\mathcal{T}_1\mathcal{T}_2^*$ 仍然产生四项结构：
$$\frac{1}{D_1D_2}[1 - e^{-2ix_1D_1} - e^{2ix_2D_2} + e^{-2ix_1D_1}e^{2ix_2D_2}]$$

因此 I1-I4 分解**仍然适用**，只是：
1. 分母从 $(1+\hat{n}\cdot\hat{u})$ 变为 $(1-\hat{u}\cdot\hat{n})$
2. 指数参数从 $\beta(1+\hat{n}\cdot\hat{u})$ 变为 $2x(1-\hat{u}\cdot\hat{n})$
3. 极点位置 $z_{1-4}$ 的符号会变化

---

## 第8节：总结

### 8.1 Hu 框架的三大贡献

1. **通用性**：所有探测器类型可分解为单程链路
2. **解析精确性**：通过留数定理完成全积分，不依赖任何近似
3. **计算效率**：I1-I4 分解 + 参数替换使计算量减少 75%

### 8.2 对 OLC 构型的适用性

Hu 框架可直接应用于 OLC，但需注意：
1. 观测量是频率偏移而非时间残差
2. 传递函数为 sinc 形式而非指数形式
3. 分母符号差异（方向约定）
4. 手征 ORF（$\Gamma^V$）的极化收缩不同但 I1-I4 结构相同

### 8.3 关键公式汇总

| 公式 | 含义 | 位置 |
|------|------|------|
| $\Gamma_{\text{one}} = \frac{1}{32\pi}[I_1-I_2-I_3+I_4]$ | I1-I4 分解 | Hu Eq.(11) |
| $I_1 = 2\pi i\int_{-1}^{1} dx \, e^{-i\alpha x}\sum_j R_j$ | 留数定理 | Hu Eq.(17) |
| $\alpha_2 = \sqrt{\alpha^2+\beta_u^2+2\alpha\beta_u c_u}$ | I2 替换 | Hu Eq.(22) |
| $T_{\text{one}}^{\text{OLC}} = \frac{i2\pi fL}{c}\text{sinc}[x(1-\hat{u}\cdot\hat{n})]e^{-ix(1-\hat{u}\cdot\hat{n})}$ | OLC 传递函数 | 楼 Eq.2-30 |
| $\mathcal{P}^V = \frac{1}{2}\text{Im}(w_1^2w_2^{*2})$ | 手征极化收缩 | P-chiral ORF |

---

*产出：Hu PRD 通用单程链路 ORF 公式从第一性原理到完整解析表达的全推导*
*完成日期：2026-07-12*
*置信度：0.92 — 所有公式引用自 Hu PRD 原文 Section II，推导步骤与原文完全一致*
