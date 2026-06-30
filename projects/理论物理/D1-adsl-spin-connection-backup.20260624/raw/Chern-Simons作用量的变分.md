## Lie 代数值微分形式的基本知识
考虑 Lie 代数 $\mathfrak{g}$-值 $m$-form $\mu = \mu^{i}I_{i}$ 和 $n$-form $\nu = \nu^{i}I_{i}$，其中 $I_{i}$ 为 $\mathfrak{g}$ 的生成元，$[I_{i}, I_{j}] = C^{k}{}_{ij}I_{k}$，$C^{k}{}_{ij}$ 是 $\mathfrak{g}$ 的结构常数。定义
$$
\mathrm{d}\mu = (\mathrm{d}\mu^{i})I_{i}.
$$
定义
$$
\mu\wedge\nu = (\mu^{i}\wedge \nu^{j})I_{i}I_{j},
$$
以及
$$
[\mu, \mu] = \mu^{i}\wedge\mu^{j}[I_{i}, I_{j}].
$$

特别地，如果 $m$ 为奇数，那么 $\mu^{i}\wedge \mu^{j} = (-1)^{m^{2}}\mu^{j}\wedge\mu^{i} = -\mu^{j}\wedge\mu^{i}$，那么此时
$$
\mu\wedge\mu = (\mu^{i}\wedge\mu^{j}) I_{i}I_{j} = (\mu^{j}\wedge\mu^{i}) I_{j}I_{i} = -(\mu^{i}\wedge\mu^{j})I_{j}I_{i}.
$$
把第二个表达形式和第四个表达形式加和除以2，得到
$$
\mu\wedge\mu = \frac{1}{2}\mu^{i}\wedge\mu^{j}[I_{i}, I_{j}] = \frac{1}{2}[\mu, \mu].
$$

如果 $m, n$ 都是奇数，那么 $\mu^{i}\wedge \nu^{j} = (-1)^{mn}\nu^{j}\wedge\mu^{i} = -\nu^{j}\wedge\mu^{i}$，那么此时
$$
[\mu, \nu] = \mu^{i}\wedge\nu^{j}[I_{i}, I_{j}] = (-\nu^{j}\wedge\mu^{i})(-[I_{j}, I_{i}]) = \nu^{j}\wedge\mu^{i}[I_{j}, I_{i}] = [\nu, \mu].
$$

进一步，令 $m = 1, n = 2$，定义
$$
\langle \mu\wedge\nu\rangle = \mu^{i}\wedge\nu^{j}\langle I_{i}, I_{j}\rangle，
$$
后一个尖括号 $\langle\cdot, \cdot\rangle$ 为 $\text{ad}$-不变、非退化的对称双线性型。所谓 $\text{ad}$-不变，指的是
$$
\langle I_{i}, [I_{j}, I_{k}]\rangle = \langle[I_{i}, I_{j}], I_{k}\rangle.
$$
注意，$\langle I_{i}, I_{j}\rangle$ 是常数。

## Chern-Simons 作用量

考虑以下 Chern-Simons 作用量
$$
S[A] = \int\left(\langle A\wedge \mathrm{d}A\rangle + \frac{1}{3} \langle A\wedge [A, A]\rangle\right),
$$
其中
$$
\begin{align}
A &= A^{i}I_{i}, &&A^{i}\text{是 1-form}, &&I_{i}\text{是 Lie 代数生成元},
\end{align}
$$
注意 $A$ 为奇数阶形式，所以 $[A, A] = 2 A\wedge A$，因此也常见
$$
S[A] = \int\left(\langle A\wedge \mathrm{d}A\rangle + \frac{2}{3} \langle A\wedge (A\wedge A)\rangle\right)
$$
甚至 $\frac{2}{3}$ 项中的圆括号可省略。

记
$$
S_{1}[A] = \int\langle A\wedge\mathrm{d}A\rangle,\quad S_{2}[A] = \int\langle A\wedge[A, A]\rangle.
$$

## 变分

### $\delta S_{1}$
$$
\delta S_{1} = \int \left(\langle (\delta A)\wedge \mathrm{d}A\rangle + \langle A\wedge \mathrm{d}(\delta A)\rangle\right),
$$
其中
$$
\int\langle A\wedge \mathrm{d}(\delta A)\rangle = \int A^{i}\wedge \mathrm{d}(\delta A^{j})\langle I_{i}, I_{j}\rangle.
$$
注意由于外微分算子的分次 Leibniz 性质，
$$
\mathrm{d}(A^{i}\wedge (\delta A^{j})) = (\mathrm{d}A^{i})\wedge (\delta A^{j}) + (-1)^{1} A^{i}\wedge \mathrm{d}(\delta A^{j}),
$$
从而
$$
A^{i}\wedge \mathrm{d}(\delta A^{j}) = (\mathrm{d}A^{i})\wedge (\delta A^{j}) - \mathrm{d}(A^{i}\wedge (\delta A^{j})).
$$
后者进入积分成为边界项，变分时不考虑，因此
$$
\begin{align}
\delta S_{1} &= \int \left(\langle (\delta A)\wedge \mathrm{d}A\rangle + (\mathrm{d}A^{i})\wedge (\delta A^{j})\langle I_{i}, I_{j}\rangle\right)\\
&= \int \left(\langle (\delta A)\wedge \mathrm{d}A\rangle + (-1)^{2\times 1}(\delta A^{j})\wedge(\mathrm{d}A^{i}) \langle I_{j}, I_{i}\rangle\right)\\
&=2\int \langle (\delta A)\wedge \mathrm{d}A\rangle\\
&= \int\langle (\delta A)\wedge (2\mathrm{d}A)\rangle.
\end{align}
$$

### $\delta S_{2}$

$$
\delta S_{2} = \int \left(\langle (\delta A)\wedge [A, A]\rangle + \langle A\wedge [\delta A, A]\rangle + \langle A\wedge [A, \delta A]\rangle\right).
$$
注意 $\delta A$ 和 $A$ 都是（Lie 代数值）1-form，从而
$$
[\delta A, A] = [A, \delta A],
$$
故
$$
\langle A\wedge [\delta A, A]\rangle = \langle A\wedge [A, \delta A]\rangle.
$$

计算
$$
\begin{align}
\langle A\wedge [A, \delta A]\rangle &= A^{i}\wedge(A^{j}\wedge\delta A^{k})\langle I_{i}, [I_{j}, I_{k}]\rangle\\
&= (A^{i}\wedge A^{j})\wedge\delta A^{k}\langle [I_{i}, I_{j}], I_{k}\rangle &\text{wedge 的结合律， ad-不变性}\\
&= (-1)^{2\times1}(\delta A^{k})\wedge(A^{i}\wedge A^{j})\langle I_{k}, [I_{i}, I_{j}]\rangle &\text{wedge 的 sign，双线性型的对称性}\\
&= \langle (\delta A)\wedge[A, A]\rangle,
\end{align}
$$
可见
$$
\delta S_{2} = 3\int \langle (\delta A)\wedge[A, A]\rangle.
$$

### $\delta S$
$$
\begin{align}
\delta S &= \delta S_{1} + \frac{1}{3}\delta S_{2}\\
&= \int\left(\langle (\delta A)\wedge (2\mathrm{d}A)\rangle + \langle (\delta A)\wedge[A, A]\rangle\right)\\
&= \int\left\langle(\delta A)\wedge\left(2\left(\mathrm{d}A + \frac{1}{2}[A, A]\right)\right)\right\rangle\\
&= 2\int\langle(\delta A)\wedge \Theta\rangle,
\end{align}
$$
其中曲率（=场强） $\Theta$ 定义为
$$
\Theta = \mathrm{d}A + \frac{1}{2}[A, A].
$$

可见，如果 Chern-Simons 作用量就是总作用量，那么运动方程自然为
$$
\Theta = 0
$$
这一平坦联络条件。