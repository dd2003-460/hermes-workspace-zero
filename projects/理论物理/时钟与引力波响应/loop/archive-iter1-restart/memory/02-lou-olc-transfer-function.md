# Lou 硕士论文 OLC 传递函数提取

> 来源: 楼明智 硕士论文 (2026), 华东师范大学
> 提取日期: 2026-06-28

## 1. OLC 探测原理

OLC 使用一对原子钟通过激光脉冲同步。引力波调制光传播距离和原子钟跃迁频率，测量**单向光频率偏移**。

## 2. 单向链路传递函数

### 公式 (2-30): 频率偏移测量下的传递函数

$$\mathcal{T}(\hat{u} \cdot \hat{n}, f) = \frac{i 2\pi f L}{c} \, \text{sinc}\left[\frac{\pi f L}{c}(1 - \hat{u} \cdot \hat{n})\right] e^{-i \frac{\pi f L}{c}(1 - \hat{u} \cdot \hat{n})}$$

其中:
- $L$ 是臂长
- $\hat{u}$ 是臂方向单位向量
- $\hat{n}$ 是引力波传播方向
- $\text{sinc}(x) = \sin(x)/x$

**与 Hu PRD 的差异**：Hu PRD 的 $T_{\text{one}} = \frac{1+\hat{n}\cdot\hat{u}}{2}[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$ 对应 PTA 的纳秒脉冲到达时间测量。OLC 的 $\mathcal{T}$ 多了前置因子 $i2\pi f L/c$ 和 sinc 函数形式——这是因为 OLC 测量的是频率偏移而非到达时间。

原文位置: `/tmp/lou_thesis.txt` p679-682

### 公式 (2-29): 傅里叶变换关系

$$\tilde{s}_1(f) = \frac{i 2\pi f L}{c} \tilde{s}_2(f)$$

时间导数对应乘上 $i2\pi f$。

原文位置: `/tmp/lou_thesis.txt` p675-677

## 3. 随机引力波背景

### 公式 (2-31): 度规扰动

$$h_{ij}(t, \vec{x}) = \sum_A \int_{-\infty}^{\infty} df \int d^2\hat{n} \, \tilde{h}_A(f, \hat{n}) e_{ij}^A(\hat{n}) e^{i2\pi f(t - \hat{n}\cdot\vec{x}/c)}$$

原文位置: `/tmp/lou_thesis.txt` p700-705

## 4. OLC 探测器的响应函数

### 公式 (2-30) 附近: OLC 响应的完整形式

OLC 的响应函数为：
$$R^A(f, \hat{n}) = e_A(\hat{n}) \, \mathcal{T}_{\text{one}}(f, \hat{u}\cdot\hat{n})$$

其中 $\mathcal{T}_{\text{one}}$ 是公式 (2-30) 给出的传递函数。

原文位置: `/tmp/lou_thesis.txt` p779-786

## 5. OLC 的关键特征

1. **sinc 函数形式**: 与 Hu PRD 的 PTA 传递函数不同，OLC 使用 sinc 函数，对应频率偏移测量
2. **臂长非常短**: $L \sim 1$-10 m vs PTA 的 kpc vs LISA 的 $10^9$ m
3. **频率范围极高**: OLC 采样率极高（光钟频率稳定度 $\sim 10^{-18}$），可达 $10^3$ Hz

这意味着 OLC 的 $fL/c$ 值覆盖了比 PTA（$10^{-15}$）和 LISA（$10^{-3}$）大得多的范围。
