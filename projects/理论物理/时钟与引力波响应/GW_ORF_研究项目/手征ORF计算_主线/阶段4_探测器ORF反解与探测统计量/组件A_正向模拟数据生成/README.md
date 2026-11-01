# 组件A：正向模拟数据生成

## 目标

假设一个 $S_h(f)$/$I(f),V(f)$ 模型，结合阶段3的 $\Gamma_{ij}(f)$ 和噪声模型，
生成模拟的探测器数据流。

## 输入

- 阶段3组件B（GbLI）或C2（SbLI TDI）算出的 $\Gamma^I_{ij}(f), \Gamma^V_{ij}(f)$
- 假设的信号模型：$I(f), V(f)$（功率谱密度）
- 噪声模型：各探测器的噪声功率谱 $S_n^{(i)}(f)$

## 输出

- 模拟的探测器时间序列 $\tilde{s}_i(f)$（频率域）
- 对应的互相关矩阵 $\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle$

## 方法

$$\langle \tilde{s}_i(f)\tilde{s}_j^*(f')\rangle = \frac{1}{2}\delta(f-f')\left[\Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f)\right] + \delta_{ij} S_n^{(i)}(f) \delta(f-f')$$

用 Cholesky 分解或 eigendecomposition 从协方差矩阵采样高斯随机变量，
得到 $\tilde{s}_i(f)$ 的独立实现。

## 验证计划

- 数值验证/01：检查生成的互相关矩阵是否匹配理论预测（大样本平均）
- 数值验证/02：检查噪声项是否独立于信号项（交叉项应趋近零）
