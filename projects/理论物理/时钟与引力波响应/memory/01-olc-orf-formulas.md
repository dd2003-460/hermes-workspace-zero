# Hu PRD 通用 ORF 公式提取

> 来源: Hu et al. PRD 111, 084065 (2025)
> 提取日期: 2026-06-28

## 1. 探测器响应函数（单向链路）

### 公式 (9): 两个单向链路的响应函数

$$R_A^{\text{one};I}(f, \hat{n}) = \frac{1}{2} e_{ab}^A(\hat{n}) u_a^I u_b^I T_{\text{one}}(\beta_u, \hat{n} \cdot \hat{u}^I) e^{i 2\pi f \hat{n} \cdot \vec{r}_u^I / c}$$

$$R_A^{\text{one};J}(f, \hat{n}) = \frac{1}{2} e_{ab}^A(\hat{n}) v_a^J v_b^J T_{\text{one}}(\beta_v, \hat{n} \cdot \hat{v}^J) e^{i 2\pi f \hat{n} \cdot \vec{r}_v^J / c}$$

其中:
- $\beta_u = 2\pi f L_u / c$, $\beta_v = 2\pi f L_v / c$
- $u^I$, $v^J$ 是臂方向单位向量
- $\vec{r}_u^I$, $\vec{r}_v^J$ 是臂的起点位置
- $e_{ab}^A(\hat{n})$ 是偏振张量
- $T_{\text{one}}$ 是单向链路传递函数（臂响应）

原文位置: `/tmp/hu_prd.txt` p281-288

## 2. 单向链路传递函数 $T_{\text{one}}$

### 公式 (7) 附近:

$$T_{\text{one}}(\beta, \hat{n} \cdot \hat{u}) = \frac{1 + \hat{n} \cdot \hat{u}}{2} \left[1 - e^{-i\beta(1 + \hat{n} \cdot \hat{u})}\right]$$

原文位置: `/tmp/hu_prd.txt` p183-185

**这是关键**：$T_{\text{one}}$ 包含两项——几何因子 $(1+\hat{n}\cdot\hat{u})/2$ 和臂响应项 $[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$。

## 3. 两个单向链路的 ORF

### 公式 (11): ORF 的积分表示

$$I_4(\alpha, \beta_u, \beta_v, \hat{s}, \hat{u}, \hat{v}) = \int d^2\Omega_{\hat{n}} \, \xi(\hat{n}) \, e^{-i\alpha \hat{n} \cdot \hat{s}} \, e^{-i\beta_u(1 + \hat{n} \cdot \hat{u})} \, e^{i\beta_v(1 + \hat{n} \cdot \hat{v})}$$

其中 $\alpha = 2\pi f \Delta L / c$，$\Delta L = |\vec{r}_v - \vec{r}_u|$ 是两个链路的端点间距。

原文位置: `/tmp/hu_prd.txt` p279-281

## 4. 偏振求和项 $\xi(\hat{n})$

### 公式 (12):

$$\xi(\hat{n}) = \sum_{A=+,\times} \frac{e_{ab}^A(\hat{n}) u^a u^b}{1 + \hat{n} \cdot \hat{u}} \, \frac{e_{cd}^A(\hat{n}) v^c v^d}{1 + \hat{n} \cdot \hat{v}}$$

原文位置: `/tmp/hu_prd.txt` p282-283

**注意**：$T_{\text{one}}$ 中的分母 $(1+\hat{n}\cdot\hat{u})$ 与 $\xi(\hat{n})$ 相消后得到上面的简洁形式。

## 5. 计算框架

### 公式 (13): 计算坐标系

选择特殊坐标系简化积分:
$$\hat{s} = (0,0,1), \quad \hat{u} = (u_x, 0, u_z), \quad \hat{v} = (v_x, v_y, v_z)$$

六个几何参数:
- $L_u, L_v$ — 臂长
- $\Delta L$ — 端点间距（α = 2πfΔL/c）
- $\gamma$ — 两臂夹角 ($\cos\gamma = \hat{u} \cdot \hat{v}$)
- $\delta_u$ — 臂 $\hat{u}$ 与 $\hat{s}$ 的夹角 ($\cos\delta_u = \hat{u} \cdot \hat{s}$)
- $\delta_v$ — 臂 $\hat{v}$ 与 $\hat{s}$ 的夹角 ($\cos\delta_v = \hat{v} \cdot \hat{s}$)

原文位置: `/tmp/hu_prd.txt` p299-323

### 方向向量的分量:
$$u_x = \sin\delta_u, \quad u_z = \cos\delta_u$$
$$v_x = \frac{\cos\gamma - \cos\delta_u \cos\delta_v}{\sin\delta_u}, \quad v_y = \frac{\sqrt{\sin^2\gamma - \cos^2\delta_u - \cos^2\delta_v + 2\cos\gamma\cos\delta_u\cos\delta_v}}{\sin\delta_u}, \quad v_z = \cos\delta_v$$

## 6. 积分计算方法 — 留数定理

### 公式 (14): $\theta, \phi$ 二重积分

$$I_1(\alpha, \hat{u}, \hat{v}, \hat{s}) = \int_0^\pi d\theta \sin\theta \, e^{-i\alpha \cos\theta} \int_0^{2\pi} d\phi \, \xi(\theta, \phi)$$

### 公式 (15): 变换到复平面

$$x = \cos\theta, \quad z = e^{i\phi}$$

$$I_1 = \int_{-1}^{1} dx \, e^{-i\alpha x} \oint_{|z|=1} \frac{dz}{iz} \, \xi(x, z)$$

### 公式 (A7): 极点

五个极点:
- $z_0 = 0$ — 原点
- $z_1 = -(1+u_z)(1+x) / (u_x\sqrt{1-x^2})$ — $x < -\cos\delta_u$ 时在单位圆内
- $z_2 = -(1-u_z)(1-x) / (u_x\sqrt{1-x^2})$ — $x > -\cos\delta_u$ 时在单位圆内
- $z_3 = -(1+v_z)(1+x) / ((v_x-iv_y)\sqrt{1-x^2})$ — $x < -\cos\delta_v$ 时在单位圆内
- $z_4 = -(1-v_z)(1-x) / ((v_x-iv_y)\sqrt{1-x^2})$ — $x > -\cos\delta_v$ 时在单位圆内

### 公式 (A13): 留数定理最终积分

$$I_1 = 2\pi i \int_{-1}^1 dx \, e^{-i\alpha x} R_0(x) + \dots$$

根据 $x$ 的范围，将积分分成几段，每段贡献不同的极点。

原文位置: `/tmp/hu_prd.txt` p802-909

## 7. PTA 特殊化

### 结果: PTA 的 ORF

Hu PRD 计算了 PTA (纳秒脉冲到达时间测量) 的特定 ORF：
- 对 PTA，$I_{\text{PTA}} = 3\Gamma_{\text{PTA}}$，使得短波极限下单脉冲的 $\gamma_{\text{PTA}} = 1$
- 经典 Hellings-Downs 曲线结果

原文位置: `/tmp/hu_prd.txt` p537

## 8. 适用性说明

Hu PRD 的公式对 **所有三种探测器类型通用**（PTA, GbLI, SbLI），唯一的区别是臂长和频率导致的 $\beta_u, \beta_v, \alpha$ 的值。

**对 OLC 的适配**: OLC 臂长 1-10m（远小于 LISA/SbLI 的 $10^9$ m），但公式 (9) 的形式完全相同。
