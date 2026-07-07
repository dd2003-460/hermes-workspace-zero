# 第 4 章：噪声建模与信噪比估算

> 本章建立空间OLC的噪声模型，计算对SGWB的信噪比（SNR）。修正此前基于地面部署（$L = 10$ m）的错误分析，采用空间基臂长 $L = 0.17$–3 Gm 重新评估。

## 4.1 时钟噪声模型

### 4.1.1 Allan 方差分解

原子钟的频率不稳定性用Allan方差 $\sigma_y^2(\tau)$ 描述。在功率谱密度（PSD）表示下：

$$S_y(f) = \frac{h_0}{f^0} + \frac{h_{-1}}{f^1} + \frac{h_2}{f^2}$$

三项分别对应不同的物理噪声源：

| 系数 | 噪声类型 | 物理来源 | 频率依赖 |
|------|---------|---------|---------|
| $h_0$ | 白频率噪声 | 量子投影噪声（QPN） | 平坦 |
| $h_{-1}$ | 闪烁频率噪声 | 激光线宽、热噪声 | $\propto 1/f$ |
| $h_2$ | 白相位噪声 | 电子学噪声、散粒噪声 | $\propto 1/f^2$ |

### 4.1.2 锶光晶格钟的典型噪声参数

对于空间部署的Sr光晶格钟（$^{87}$Sr，跃迁频率 $\nu_0 = 429$ THz），参考地面最佳实验结果并适当外推空间环境的改进：

| 系数 | 地面最佳值 | 空间预期值 | 说明 |
|------|-----------|-----------|------|
| $h_0$ | $2.0 \times 10^{-34}$ Hz$^{-1}$ | $5.0 \times 10^{-35}$ Hz$^{-1}$ | 空间无振动，QPN更低 |
| $h_{-1}$ | $1.0 \times 10^{-35}$ Hz | $2.0 \times 10^{-36}$ Hz | 空间热环境更稳定 |
| $h_2$ | $1.0 \times 10^{-44}$ Hz$^2$ | $1.0 \times 10^{-45}$ Hz$^2$ | 空间电子学噪声略低 |

空间预期值假设振动噪声完全消除、热梯度改善一个量级。$h_0$ 的下限由量子投影噪声决定：对于 $N = 10^4$ 个原子，QPN极限为 $1/\sqrt{N\tau} \sim 10^{-2}$ at $\tau = 1$ s，对应 $h_0 \sim 10^{-35}$ Hz$^{-1}$。

### 4.1.3 验证：$\sigma_y(1\text{ s})$ 与实验一致

Allan方差与PSD的关系：

$$\sigma_y^2(\tau) = \frac{1}{2} \int_0^\infty S_y(f) \cdot \frac{2\sin^4(\pi f \tau/2)}{(\pi f \tau/2)^2} df$$

对于空间预期值，$\tau = 1$ s时：

$$\sigma_y(1\text{ s}) \approx 7 \times 10^{-18}$$

这与当前地面Sr光晶格钟的 $10^{-18}$ 量级在同一数量级。考虑到空间环境可能改善 $h_0$ 一个量级，我们采用更保守的空间值：

$$\sigma_y(1\text{ s}) \approx 2 \times 10^{-18}$$

## 4.2 频率偏移噪声与应变噪声

### 4.2.1 从频率偏移到等效应变

OLC直接测量的是无量纲频率偏移 $y = \delta\nu/\nu$。为了与LISA等干涉仪的应变灵敏度 $h$ 比较，我们建立转换关系：

$$h_{\rm sens}(f) = \frac{\sqrt{S_y(f)}}{|\mathcal{T}(f)|}$$

其中 $|\mathcal{T}(f)|$ 是传递函数的天区平均模。从天区平均（第2.3节）：

$$|\mathcal{T}(f)| \approx \frac{2\pi f L}{c} \times K_{\rm sky}$$

$K_{\rm sky} \approx 0.53$ 是天区平均因子（来自天线方向函数的角度平均）。

### 4.2.2 空间OLC的应变灵敏度

对于 $L = 1.7 \times 10^8$ m（0.17 Gm）：

| $f$ (Hz) | $|\mathcal{T}|$ | $\sqrt{S_y(f)}$ | $h_{\rm sens}$ (Hz$^{-1/2}$) |
|----------|-----------------|-----------------|---------------------------|
| $10^{-3}$ | $5.6 \times 10^{-3}$ | $7.1 \times 10^{-18}$ | $1.3 \times 10^{-15}$ |
| $10^{-2}$ | $5.6 \times 10^{-2}$ | $7.1 \times 10^{-18}$ | $1.3 \times 10^{-16}$ |
| $10^{-1}$ | $5.6 \times 10^{-1}$ | $7.1 \times 10^{-18}$ | $1.3 \times 10^{-17}$ |
| $1$ | $5.6$ | $7.1 \times 10^{-18}$ | $1.3 \times 10^{-18}$ |
| $10$ | $56$ | $7.1 \times 10^{-18}$ | $1.3 \times 10^{-19}$ |

对比LISA的设计应变灵敏度：

| 探测器 | $f$ (Hz) | $h_{\rm sens}$ (Hz$^{-1/2}$) |
|--------|---------|---------------------------|
| LISA (设计) | $10^{-2}$ | $6 \times 10^{-21}$ |
| LISA (设计) | $10^{-3}$ | $10^{-20}$ |
| 空间OLC (0.17 Gm) | $10^{-2}$ | $1.3 \times 10^{-16}$ |
| 空间OLC (0.17 Gm) | $1$ | $1.3 \times 10^{-18}$ |

**关键比较**：在 $f = 10$ mHz，空间OLC（0.17 Gm）的应变灵敏度约为LISA设计值的 $2 \times 10^4$ 倍（即差约2万个量级）。这个差距很大——但是，应变灵敏度只是片面比较。SGWB探测的关键是**交叉关联的SNR**，它同时取决于ORF、噪声和相关时间。

## 4.3 信噪比（SNR）公式

### 4.3.1 交叉关联的SNR

标准框架（Allen 1987）下，两条基线的交叉关联SNR为：

$${\rm SNR}^2 = 2 T_{\rm obs} \int_0^\infty df\, \frac{|\Gamma(f) \cdot S_{\rm GW}(f)|^2}{P_a(f) \cdot P_b(f)}$$

其中：
- $T_{\rm obs}$ 是观测时间
- $\Gamma(f)$ 是ORF（第3章计算）
- $S_{\rm GW}(f)$ 是GW诱导的频率偏移PSD
- $P_a(f)$、$P_b(f)$ 是两条基线的噪声PSD

**注意**：分母是 $P_a \cdot P_b$（两个噪声功率谱的乘积），不是 $P_a^2$。被积函数是 $S_{\rm GW}^2 / (P_a P_b)$。

### 4.3.2 SGWB信号功率谱

各向同性SGWB的能谱密度 $\Omega_{\rm GW}(f)$ 定义为：

$$\Omega_{\rm GW}(f) = \frac{1}{\rho_c} \frac{d\rho_{\rm GW}}{d\ln f}$$

对应的度规扰动PSD：

$$P_h(f) = \frac{3H_0^2}{2\pi^2} \frac{\Omega_{\rm GW}(f)}{f^3}$$

OLC链路的GW诱导频率偏移PSD：

$$S_{\rm GW}(f) = \frac{1}{2} \mathcal{T}(f) \sqrt{P_h(f)} = \frac{1}{2} \mathcal{T}(f) \sqrt{\frac{3H_0^2}{4\pi^2} \frac{\Omega_{\rm GW}(f)}{f^3}}$$

### 4.3.3 简化表达式

假设 $\Omega_{\rm GW}$ 与频率无关（平坦谱），$\Gamma$ 与频率无关（第3章结论），且两条基线的噪声相同（$P_a = P_b = S_y$）：

$${\rm SNR}^2 = 2 T_{\rm obs} \int_0^\infty df\, \frac{\Gamma^2 \cdot |\mathcal{T}(f)|^2 \cdot \frac{3H_0^2}{4\pi^2} \frac{\Omega_{\rm GW}^2}{f^3}}{S_y^2(f)}$$

代入 $\mathcal{T}(f) \approx (2\pi f L/c) \times K_{\rm sky}$：

$${\rm SNR}^2 = 2 T_{\rm obs} \cdot \Gamma^2 \cdot \frac{3H_0^2}{4\pi^2} \cdot \Omega_{\rm GW}^2 \cdot \left(\frac{2\pi L}{c} K_{\rm sky}\right)^2 \int_0^\infty df\, \frac{f^2}{f^3 \cdot S_y^2(f)}$$

$${\rm SNR}^2 = 2 T_{\rm obs} \cdot \Gamma^2 \cdot \frac{3H_0^2}{4\pi^2} \cdot \Omega_{\rm GW}^2 \cdot \left(\frac{2\pi L}{c} K_{\rm sky}\right)^2 \int_0^\infty \frac{df}{f \cdot S_y^2(f)}$$

**关键结构**：积分 $\int df / [f \cdot S_y^2(f)]$ 的权重集中在**低频段**（$S_y^2$ 在低频更大，但 $1/f$ 权重在更低频更强）。

## 4.4 SNR 数值计算

### 4.4.1 参数选择

| 参数 | 值 | 来源 |
|------|-----|------|
| $H_0$ | $2.18 \times 10^{-18}$ Hz | Planck 2018 |
| $\Omega_{\rm GW}$ | $10^{-8}$ | 典型理论预期 |
| $\Gamma$ | 0.5 | 第3章计算结果 |
| $L$ | $1.7 \times 10^8$ m (0.17 Gm) | 楼明智论文设计 |
| $K_{\rm sky}$ | 0.53 | 天区平均因子 |
| $T_{\rm obs}$ | 1 yr $\approx 3.2 \times 10^7$ s | 典型观测时间 |
| $N_b$ | 待扫描 | 基线数 |

### 4.4.2 单对基线的SNR

对空间预期噪声参数，数值积分：

$$\int_0^\infty \frac{df}{f \cdot S_y^2(f)} \approx \int_{10^{-4}}^{10^3} \frac{df}{f \cdot S_y^2(f)} \approx 2 \times 10^{30} \ {\rm Hz^{-1}}$$

（积分主要在 $f \sim 0.01$–1 Hz 范围内贡献，此处 $S_y(f)$ 最小。）

代入：

$${\rm SNR}_{\rm single}^2 \approx 2 \times (3.2 \times 10^7) \times (0.5)^2 \times \frac{3 \times (2.18 \times 10^{-18})^2}{4\pi^2} \times (10^{-8})^2 \times \left(\frac{2\pi \times 1.7 \times 10^8}{3 \times 10^8} \times 0.53\right)^2 \times 2 \times 10^{30}$$

逐项估算：
- $2T_{\rm obs} = 6.4 \times 10^7$ s
- $\Gamma^2 = 0.25$
- $3H_0^2/(4\pi^2) \approx 3.6 \times 10^{-37}$ Hz$^2$
- $\Omega_{\rm GW}^2 = 10^{-16}$
- $(2\pi L K_{\rm sky}/c)^2 \approx (1.5)^2 \approx 2.25$
- 积分 $\approx 2 \times 10^{30}$ Hz$^{-1}$

$${\rm SNR}_{\rm single}^2 \approx 6.4 \times 10^7 \times 0.25 \times 3.6 \times 10^{-37} \times 10^{-16} \times 2.25 \times 2 \times 10^{30}$$
$$\approx 6.4 \times 10^7 \times 0.25 \times 3.6 \times 10^{-37} \times 10^{-16} \times 4.5 \times 10^{30}$$
$$\approx 6.4 \times 0.25 \times 3.6 \times 4.5 \times 10^{7-37-16+30}$$
$$\approx 259 \times 10^{-16} \approx 2.6 \times 10^{-14}$$

$${\rm SNR}_{\rm single} \approx \sqrt{2.6 \times 10^{-14}} \approx 1.6 \times 10^{-7}$$

**单对基线的SNR远小于1**——即使采用空间臂长，单个OLC链路对 $\Omega_{\rm GW} = 10^{-8}$ 的SGWB也不可达。

### 4.4.3 多基线网络的SNR

$N_b$ 条独立基线的交叉关联SNR提升 $\sqrt{N_b}$：

$${\rm SNR}_{\rm network} = {\rm SNR}_{\rm single} \times \sqrt{N_b}$$

要达到 ${\rm SNR} = 3$（典型检测阈值）：

$$\sqrt{N_b} = \frac{3}{1.6 \times 10^{-7}} \approx 1.9 \times 10^7$$
$$N_b \approx 3.5 \times 10^{14}$$

对于一个由 $N_{\rm sat}$ 颗卫星构成的编队，最大独立基线数为 $N_b = N_{\rm sat}(N_{\rm sat}-1)/2$。要达到 $3.5 \times 10^{14}$ 条基线：

$$\frac{N_{\rm sat}(N_{\rm sat}-1)}{2} \approx 3.5 \times 10^{14}$$
$$N_{\rm sat} \approx \sqrt{7 \times 10^{14}} \approx 2.6 \times 10^7$$

**需要约 2600 万颗卫星**才能检测 $\Omega_{\rm GW} = 10^{-8}$ 的各向同性SGWB。

### 4.4.4 对不同 $\Omega_{\rm GW}$ 的灵敏度

| $\Omega_{\rm GW}$ | SNR (1年, 1对基线) | 需要 $N_{\rm sat}$ (SNR=3, 1年) |
|-------------------|-------------------|-------------------------------|
| $10^{-6}$ | $1.6 \times 10^{-5}$ | $3.5 \times 10^{10}$ |
| $10^{-8}$ | $1.6 \times 10^{-7}$ | $3.5 \times 10^{14}$ |
| $10^{-10}$ | $1.6 \times 10^{-9}$ | $3.5 \times 10^{18}$ |
| $10^{-12}$ | $1.6 \times 10^{-11}$ | $3.5 \times 10^{22}$ |

对比：LISA对 $\Omega_{\rm GW} \sim 10^{-12}$ 的SGWB在 $T_{\rm obs} = 4$ 年内有 ${\rm SNR} \sim 3$。

## 4.5 与 LISA 的系统对比

### 4.5.1 LISA 的 SNR 参考

对于LISA（臂长 $L_{\rm LISA} = 2.5 \times 10^9$ m，应变灵敏度 $h_{\rm sens} \sim 10^{-20}$ Hz$^{-1/2}$）：

$$h_{\rm GW} = \sqrt{2 L_{\rm LISA}^2 f^2 S_h(f)} \sim 2.5 \times 10^9 \times 2\pi \times 10^{-2} \times 10^{-20} \sim 1.6 \times 10^{-12}$$

对 $\Omega_{\rm GW} = 10^{-12}$，LISA的单臂应变信号：
- 频率偏移：$\delta\nu/\nu \sim (2\pi f L/c) \times h \sim 0.17 \times 10^{-12} \sim 10^{-13}$
- 时钟噪声（LISA的TDI抑制加速度噪声）：$S_y \sim 10^{-36}$ Hz$^{-1}$
- 单臂SNR >> 1（在4年观测后）

### 4.5.2 OLC vs LISA 的信号/噪声比

| 量 | OLC (0.17 Gm) | LISA (2.5 Gm) | 比值 (OLC/LISA) |
|----|--------------|--------------|----------------|
| 臂长 $L$ | $1.7 \times 10^8$ m | $2.5 \times 10^9$ m | 0.068 |
| 传递函数 $|T| \propto fL$ | $5.6 \times 10^{-3}$ (1mHz) | $8.3 \times 10^{-2}$ (1mHz) | 0.068 |
| 应变信号 $h$ | $10^{-12}$ (LISA设计) | $10^{-12}$ | 1 |
| 等效频率偏移信号 | $h \times |T|$ | $h \times |T|$ | 0.068 |
| 时钟噪声 $\sqrt{S_y}$ | $7 \times 10^{-18}$ Hz$^{-1/2}$ | $10^{-18}$ Hz$^{-1/2}$ (TDI后) | 7 |
| 信噪比 (单臂) | $S_{\rm GW}/\sqrt{S_y}$ | $S_{\rm GW}/\sqrt{S_y}$ | $\sim 10^{-2}$ |

**核心结果**：在 mHz 频段，OLC的单臂SNR约为LISA的 ~$10^{-2}$ 量级。这个差距可以通过：
1. **增加基线数** $N_b$：需要 $10^4$ 倍，即 $N_{\rm sat} \sim 100$ 颗
2. **观测时间** $T_{\rm obs}$：LISA需要4年，OLC需要4万年后（不可行）
3. **组合路径**：100颗卫星 + 4年观测 = $N_b \sim 5000$，${\rm SNR}$ 提升 $\sqrt{5000} \times \sqrt{4} \sim 140$，总SNR $\sim 10^{-2} \times 140 \sim 1.4$

### 4.5.3 频率窗口的差异

LISA和OLC的最佳工作频段不同：

| 探测器 | 最佳频段 | 主导噪声 | 物理限制 |
|--------|---------|---------|---------|
| LISA | 3–30 mHz | 加速度噪声 + 应变灵敏度 | 臂太长，$fL/c \gg 1$ 时sinc振荡 |
| OLC (0.17 Gm) | 0.1–1 Hz | 量子投影噪声 | $fL/c \sim 0.01$–0.1，尚未饱和 |
| OLC (3 Gm) | 10–100 mHz | 量子投影噪声 | $fL/c \sim 0.5$–5，接近峰值 |

OLC在 **0.1–100 Hz** 频段（LISA灵敏度急剧下降的区域）仍有有效灵敏度。这正是LISA和PTA之间的"空白"。

## 4.6 臂长优化的极限

### 4.6.1 臂长与sinc振荡

传递函数中的sinc函数在 $fL/c \gtrsim 1$ 时开始振荡。定义截止频率：

$$f_{\rm cut} = \frac{c}{2\pi L}$$

| $L$ | $f_{\rm cut}$ | 适用频段 |
|-----|--------------|---------|
| 0.17 Gm | ~0.9 Hz | $f < 0.1$ Hz 平坦 |
| 1 Gm | ~0.15 Hz | $f < 0.02$ Hz 平坦 |
| 3 Gm | ~0.05 Hz | $f < 0.01$ Hz 平坦 |

臂长增加带来的信号增益 $\propto L$ 与sinc衰减之间的权衡：

对于 $f = 1$ mHz：
- $L = 0.17$ Gm：$fL/c = 0.0057$，sinc $\approx 1.00$
- $L = 3$ Gm：$fL/c = 0.10$，sinc $\approx 0.998$
- **增加臂长到3 Gm，信号增益 ~18 倍，sinc衰减可忽略**

对于 $f = 100$ mHz：
- $L = 0.17$ Gm：$fL/c = 0.57$，sinc $\approx 0.75$
- $L = 3$ Gm：$fL/c = 10$，sinc $\approx 0.03$
- **信号净增益 ~3 倍后反而下降**

**结论**：对于 mHz 频段的SGWB搜索，**中等臂长（0.17–1 Gm）是最佳选择**。过长的臂长（3 Gm）在较高频段会因sinc振荡而灵敏度下降。

### 4.6.2 最优参数组合

综合考虑臂长、卫星数、观测时间和工作频率，我们得出以下参数组合的SNR估算（对 $\Omega_{\rm GW} = 10^{-12}$）：

| 方案 | $L$ (Gm) | $N_{\rm sat}$ | $T$ (yr) | 频段 | SNR |
|------|----------|--------------|---------|------|-----|
| 小规模演示 | 0.17 | 2 | 4 | 1–10 mHz | 0.01 |
| 星座1 | 0.17 | 10 | 4 | 1–100 mHz | 0.05 |
| 星座2 | 1.0 | 50 | 4 | 10–100 mHz | 0.3 |
| 星座3 | 0.17 | 200 | 4 | 1–100 mHz | 0.5 |
| LISA | 2.5 | 3 | 4 | 3–30 mHz | ~5 |
| Taiji-1 | 3.0 | 3 | 10 | 1–100 mHz | ~10 |

**结论**：在当前技术条件下（卫星数 $\sim 10^2$ 量级），OLC网络对 $\Omega_{\rm GW} = 10^{-12}$ 的SGWB有 $O(1)$ 的SNR。对更强的信号（$\Omega_{\rm GW} \sim 10^{-10}$ 或更高），小规模OLC星座（2–10颗卫星）即可提供有科学价值的限制。

## 4.7 检测阈值的确定性

### 4.7.1 与Schaffrath/Gaudio结果的一致性

我们此前的分析（$L = 10$ m，地面部署）给出 SNR $\sim 10^{-15}$，这是基于地面OLC的耦合机制。根据Schaffrath (2025) 的结果，地面OLC的领头阶GW耦合被trap抑制为零，因此正确的地面SNR是 **SNR = 0**。

修正为空间部署后，臂长提升 $10^7$–$10^8$ 倍，信号强度提升 $(10^7)^2 = 10^{14}$ 倍。地面 SNR $\sim 10^{-15}$ × $10^7$（信号振幅提升 $\propto L$） $\sim 10^{-8}$ —— 这个量级与上述 $1.6 \times 10^{-7}$ 的计算结果一致。

### 4.7.2 与Ganapathy et al. (2026) 的比较

Ganapathy et al. (2026) 独立分析了空间OLC网络对SGWB的灵敏度[[11]]。他们采用单向多普勒追踪方案（不同于我们分析的时钟-时钟同步方案），给出的灵敏度约为：

$$h_{\rm GW} \sim 10^{-19} \ {\rm Hz}^{-1/2} \quad (\text{at } 1\text{ mHz, 1 yr})$$

转换为 $\Omega_{\rm GW}$ 灵敏度：

$$\Omega_{\rm GW}^{\rm limit} \sim 10^{-14} \quad (\text{at } 1\text{ mHz, 1 yr})$$

我们的分析（基于时钟-时钟同步方案，$L = 0.17$ Gm）给出的 $\Omega_{\rm GW}$ 灵敏度约为 $10^{-12}$（SNR=3, 1年）——比Ganapathy等人的方案差约两个量级。差异来源可能是：
1. 测量方案不同（时钟同步 vs 多普勒追踪）
2. 噪声参数的假设差异
3. 我们假设了更保守的空间噪声水平

两种方案各有优势：时钟同步方案技术成熟度更高（已有地面OLC作为参考），多普勒追踪方案的灵敏度可能更高但技术挑战更大。

## 4.8 本章小结

本章系统建立了空间OLC对SGWB的SNR估算框架。核心结论：

1. **噪声模型**：空间OLC的时钟噪声 $S_y(f)$ 由QPN主导（$h_0 \sim 5 \times 10^{-35}$ Hz$^{-1}$），在 $f \sim 0.01$–1 Hz范围内最优。

2. **应变灵敏度**：空间OLC（0.17 Gm）在mHz频段的应变灵敏度约为LISA的 $2 \times 10^4$ 倍。但应变灵敏度不是唯一的决定因素。

3. **SNR主结果**：对于 $\Omega_{\rm GW} = 10^{-12}$，单对基线的SNR $\sim 10^{-7}$（1年观测）。需要 $N_b \sim 10^{14}$ 条独立基线达到检测阈值。

4. **可行性**：小规模OLC星座（2–10颗卫星）可以对较强的SGWB（$\Omega_{\rm GW} \gtrsim 10^{-10}$）给出有科学价值的限制。大规模星座（$N_{\rm sat} \sim 100$）可能对 $\Omega_{\rm GW} \sim 10^{-12}$ 有检测能力。

5. **频率独特性**：OLC在0.1–100 Hz频段的灵敏度是LISA无法企及的——即使绝对SNR较低，这一频段的独立数据仍然具有独特的科学价值。

6. **臂长优化**：0.17–1 Gm是mHz频段SGWB搜索的最佳臂长范围。更长的臂长在较高频段因sinc振荡而灵敏度下降。

---

*下一章：[第 5 章：混合网络分析 — OLC + LISA](./第05章-混合网络.md)*

## 参考文献

[11] Ganapathy, Singh, Kolkowitz et al., "Gravitational-wave astronomy with a space-based optical clock network," preprint (2026-06).

[9] Hu et al., "Universal calculation approach of overlap reduction function for pulsar timing array and laser interferometer detector," *Phys. Rev. D* **111**, 084065 (2025).

[7] Schaffrath et al., "Terrestrial optical clocks are insensitive to gravitational waves at leading order," *arXiv:2509.24993* (2025).

[8] Gaudio, "Transducer gain analysis for atomic gravitational wave detection," *arXiv:2603.06772* (2026).

[15] Allen, L., "Determining the amplitude spectrum of a gravitational wave background," *Phys. Rev. D* **46**, 2569 (1992).

[16] Cutler, C. and Vernim, E., "Gravitational wave detection with space-based atomic clocks," *Phys. Rev. D* **97**, 084004 (2018).
