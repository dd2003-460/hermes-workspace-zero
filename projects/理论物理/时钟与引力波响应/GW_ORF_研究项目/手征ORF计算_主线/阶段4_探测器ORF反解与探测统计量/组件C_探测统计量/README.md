# 组件C：探测统计量

## 目标

从估计量 $\hat{I}(f), \hat{V}(f)$ 及其协方差出发，构造：
1. **似然比检验** (LRT)：H₀: I=V=0 vs H₁: I,V≠0
2. **Fisher 信息矩阵**：参数空间中的信息含量
3. **灵敏度曲线**：最小可探测信号强度 vs 频率（95% 置信）

## 核心公式

### Fisher 信息（单频率 bin）

对参数 θ = (I, V)，高斯互相关数据下的 Fisher 信息：

$$\mathcal{I}_{\alpha\beta}(f) = \sum_{i<j} \frac{1}{S_n^{(i)} S_n^{(j)}} \cdot \frac{\partial x_{ij}}{\partial \theta_\alpha} \cdot \frac{\partial x_{ij}}{\partial \theta_\beta}$$

其中 ∂x_ij/∂I = 0.5·Γ^I_ij, ∂x_ij/∂V = 0.5·Im(Γ^V_ij)。

由于分离原理，$\mathcal{I}$ 是对角阵：
$$\mathcal{I}_{II} = \sum_{i<j} \frac{[\Gamma^I_{ij}]^2}{4 S_n^{(i)} S_n^{(j)}}, \quad \mathcal{I}_{VV} = \sum_{i<j} \frac{[\text{Im}(\Gamma^V_{ij})]^2}{4 S_n^{(i)} S_n^{(j)}}$$

### 最小可探测信号 (95%)

$$I_{min}(f) = 1.645 \cdot \frac{1}{\sqrt{\mathcal{I}_{II}(f)}}$$

（单侧 95% → z=1.645；双侧 95% → z=1.96）

### 似然比检验

$$\Lambda(f) = \frac{L(I=\hat{I}, V=\hat{V})}{L(I=0, V=0)}$$

Wilks 定理：$-2\ln\Lambda \xrightarrow{d} \chi^2_2$（大样本）

## 输入

- 阶段3 的 Γ^I, Γ^V
- 噪声模型 S_n^(i)(f)
- （可选）组件B 的估计值用于 LRT

## 输出

- Fisher 信息矩阵 $\mathcal{I}(f)$
- 灵敏度曲线 $I_{min}(f), V_{min}(f)$
- LRT 统计量分布（Monte Carlo 验证 Wilks 近似）

## 验证计划

- 数值验证/01：Fisher 信息 vs 实际估计量方差（应互为倒数）
- 数值验证/02：LRT Monte Carlo — 注入不同 SNR 信号，看 p-value 校准
