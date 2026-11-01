# 组件B：反解估计量

## 目标

从模拟（或真实）探测器数据 $\tilde{s}_i(f)$ 中，用互相关最优估计量
反解出信号功率谱 $I(f), V(f)$。

## 核心公式（仿 Allen & Romano 1999）

对于 N 个探测器的网络，给定 ORF 张量 $\Gamma^I_{ij}(f), \Gamma^V_{ij}(f)$
和噪声谱 $S_n^{(i)}(f)$，最优估计量为：

$$\hat{I}(f) = \sum_{i,j,k,l} w^{(I)}_{ij,kl}(f) \, \tilde{s}_i(f) \tilde{s}_j^*(f) \, \delta_{ik}\delta_{jl}$$

其中权重矩阵 $w^{(I)}$ 由 $(\Gamma^I)^{-1}$ 和噪声协方差确定。
对两参数（I + V）情形，需要联合求解 2×2 线性系统。

简化版（单参数、白噪声）：
$$\hat{I}(f) = \frac{\sum_{i<j} \Gamma^I_{ij}(f) \, \tilde{s}_i(f)\tilde{s}_j^*(f)}{\sum_{i<j} [\Gamma^I_{ij}(f)]^2 \, S_n^{(i)}(f) S_n^{(j)}(f)}$$

## 输入

- 组件A 生成的 $\tilde{s}_i(f)$（或真实数据）
- 阶段3 的 $\Gamma^I_{ij}(f), \Gamma^V_{ij}(f)$
- 噪声模型 $S_n^{(i)}(f)$

## 输出

- $\hat{I}(f), \hat{V}(f)$ 估计值
- 估计量的方差 $\text{Var}[\hat{I}(f)], \text{Var}[\hat{V}(f)], \text{Cov}[\hat{I},\hat{V}]$

## 验证计划

- 数值验证/01：注入-恢复测试（用组件A生成数据→组件B反解→比对真值）
- 数值验证/02：无信号时估计量应为零（均值检验）
