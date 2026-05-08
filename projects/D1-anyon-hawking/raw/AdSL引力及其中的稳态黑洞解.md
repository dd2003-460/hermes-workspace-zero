参考文献：JHEP09(2023)185

## AdSL 代数

AdSL 代数是由九个生成元构成的 Lie 代数：关联时空旋转的 $J_{a}$，关联时空平移的 $P_{a}$，新引入的生成元 $Z_{a}$。他们的对易关系是
$$
\begin{equation}
\begin{aligned}
&[J_{a}, J_{b}] = \epsilon_{abc}J^{c}, &[J_{a}, P_{b}] = \epsilon_{abc}P^{c}, &&[J_{a}, Z_{b}] = \epsilon_{abc}Z^{c},\\
&[Z_{a}, Z_{b}] = \epsilon_{abc}Z^{c}, &[P_{a}, P_{b}] = \epsilon_{abc}Z^{c}, &&[Z_{a}, P_{b}] = \epsilon_{abc}P^{c},
\end{aligned}
\end{equation}
$$
其中 $\epsilon_{abc}$ 是 Levi-Civita 符号，$\epsilon_{012} = 1, \epsilon^{012} = -1$。Lorentz 指标 $a\in{\{0, 1, 2\}}$，用 Minkowski 度规 $(\eta_{ab}) = \text{diag}(-++)$ 来升降指标。

不变对称双线性型我们采用如下定义：
$$
\begin{equation}
\begin{aligned}
&\langle J_{a}, J_{b}\rangle = \alpha_{0}\eta_{ab}, &\langle J_{a}, P_{b}\rangle = \alpha_{1}\eta_{ab}, &&\langle J_{a}, Z_{b}\rangle = \alpha_{2}\eta_{ab},\\
&\langle Z_{a}, Z_{b}\rangle = \alpha_{2}\eta_{ab}, &\langle P_{a}, P_{b}\rangle = \alpha_{2}\eta_{ab}, &&\langle Z_{a}, P_{b}\rangle = \alpha_{1}\eta_{ab}.
\end{aligned}
\end{equation}
$$
上面双线性型应当要求非退化性，即
$$
\det\begin{pmatrix}
\alpha_{0}(\eta_{ab}) &\alpha_{1}(\eta_{ab}) &\alpha_{2}(\eta_{ab})\\
\alpha_{1}(\eta_{ab}) &\alpha_{2}(\eta_{ab}) &\alpha_{1}(\eta_{ab})\\
\alpha_{2}(\eta_{ab}) &\alpha_{1}(\eta_{ab}) &\alpha_{2}(\eta_{ab})
\end{pmatrix} = (-1)(\alpha_{0} - \alpha_{2})(\alpha_{2}^{2} - \alpha_{1}^{2}) \neq 0.
$$

## AdSL 引力的作用量

作用量取为 Chern-Simons 形式：
$$
\begin{equation}
I[A] = \frac{k}{4\pi}\int_{\mathcal{M}}\left\langle A\wedge{\mathrm{d}A} + \frac{2}{3}A\wedge A\wedge A\right\rangle.
\end{equation}
$$
对于 AdSL 引力，联络取为
$$
\begin{equation}
A = \omega^{a}J_{a} + \frac{e^{a}}{\ell}P_{a} + \sigma^{a}Z_{a},
\end{equation}
$$
其中 $\omega^{a}$ 是对偶联络 1-形式（和通常的联络1-形式 $\omega^{a}{}_{b}$ 之间的关系是 $\omega^{a} = \frac{1}{2}\epsilon^{abc} \eta_{bd}\omega^{d}{}_{c}$），$e^{a}$ 是余标架，$\sigma^{a}$ 是所谓和生成元 $Z_{a}$ 关联的补偿规范场的 1-形式，$\ell$ 是 AdS 半径，$k = \frac{\ell}{4G_{\text{N}}}$。基于这个联络，我们可以定义一些 2-形式：
$$
\begin{align}
&\text{对偶几何曲率 2-形式：}&R^{a} &= \mathrm{d}\omega^{a} - \frac{1}{2}\epsilon^{abc}\omega_{b}\wedge\omega_{c},\\
&\text{对偶挠率 2-形式：}&T^{a} &= \mathrm{D}_\omega e^{a},\\
&\text{对偶 $\sigma^{a}$ 曲率 2-形式：}&F^{a} &= \mathrm{D}_{\omega}\sigma^{a} + \frac{1}{2}\epsilon^{abc}\sigma_{b}\wedge\sigma_{c},
\end{align}
$$
其中 $\mathrm{D}_{\omega}$ 是对全自旋联络而言的协变导数，作用到余标架上 $\mathrm{D}_{\omega}e^{a} = \mathrm{d}e^{a} - \epsilon^{abc}\omega_{b}\wedge e_{c}$。

利用这些 2-形式，我们可以把作用量分解成三个部分：
$$
\begin{align}
I_{\text{AdSL}}[e, \omega, \sigma] &= \frac{k}{4\pi}\int_{\mathcal{M}}(L_{\text{EC}} + L_{\text{exotic}} + L_{\sigma}),\\
L_{\text{EC}} &= \frac{\alpha_{1}}{\ell}\left(2R_{a}\wedge e^{a} + \frac{1}{3\ell^2}\epsilon^{abc}e_{a}\wedge e_{b}\wedge e_{c} \right),\\
L_{\text{exotic}} &= \alpha_{0}\left(\omega^{a}\wedge \mathrm{d}\omega_{a} + \frac{1}{3}\epsilon^{abc}\omega_{a}\wedge \omega_{b}\wedge \omega_{c} \right) + \frac{\alpha_{2}}{\ell^2}T^{a}\wedge e_{a},\\
L_{\sigma} &= \alpha_{2}\left(2R^{a}\wedge \sigma_{a} + \frac{1}{3}\epsilon^{abc}\sigma_{a}\wedge \sigma_{b}\wedge \sigma_{c} + (\mathrm{D}_{\omega}\sigma^{a})\wedge\sigma_{a} + \frac{1}{\ell}\epsilon^{abc}e_{a}\wedge \sigma_{b}\wedge e_{c}\right) + \frac{2\alpha_{1}}{\ell}F^{a}\wedge e_{a}.
\end{align}
$$

## AdSL 引力的运动方程

把 $I_{\text{AdSL}}$ 分别对不同场量变分：
$$
\begin{equation}
\begin{aligned}
&\delta \omega^{a}: && 0 = \alpha_{0}R_{a} + \alpha_{1}\frac{1}{\ell}\left(T_{a} + \epsilon_{abc} \sigma^{b}\wedge e^{c}\right) + \alpha_{2}\left(F_{a}+ \frac{1}{2\ell^2}\epsilon_{abc}e^{b}\wedge e^{c}\right),\\
&\delta e^{a}: && 0 = \alpha_{1}\frac{1}{\ell}\left(R_{a} + F_{a} + \frac{1}{2\ell^{2}}\epsilon_{abc} e^{b}\wedge e^{c}\right) + \alpha_{2}\frac{1}{\ell^2}\left(T_{a} + \epsilon_{abc} \sigma^{b}\wedge e^{c}\right),\\
&\delta \sigma^{a}: && 0 = \alpha_{1}\frac{1}{\ell}\left(T_{a} + \epsilon_{abc} \sigma^{b}\wedge e^{c}\right) + \alpha_{2}\left(R_{a} + F_{a} + \frac{1}{2\ell^{2}}\epsilon_{abc} e^{b}\wedge e^{c}\right).
\end{aligned}
\end{equation}
$$
这可以整理成
$$
\begin{align}
\begin{pmatrix}
\alpha_{0} &\alpha_{1}/\ell &\alpha_{2}\\
\alpha_{1}/\ell &\alpha_{2}/\ell^{2} &\alpha_{1}/\ell\\
\alpha_{2} &\alpha_{1}/\ell &\alpha_{2}
\end{pmatrix}\begin{pmatrix}
R_{a}\\ T_{a} + \epsilon_{abc}\sigma^{b}\wedge e^{c}\\ F_{a} + \frac{1}{2\ell^{2}}\epsilon_{abc}e^{b}\wedge e^{c}
\end{pmatrix} = \begin{pmatrix}
0\\ 0\\ 0
\end{pmatrix}.
\end{align}
$$
当系数矩阵非退化，即要求 $(\alpha_{0}-\alpha_{2})(\alpha_{2}^{2} - \alpha_{1}^{2}) \neq 0$ 时（这与前面 AdSL 代数的对称不变双线性型非退化的要求相符），上面的运动方程相当于下面的运动方程：
$$
\begin{align}
R_{a} &= 0,\\
T_{a} + \epsilon_{abc} \sigma^{b}\wedge e^{c} &= 0,\\
F_{a} + \frac{1}{2\ell^{2}}\epsilon_{abc} e^{b}\wedge e^{c} &= 0.
\end{align}
$$
从上面第二个方程可以看出，实际上 $\sigma^{a} = \kappa^{a}$，其中 $\kappa^{a}$ 是自旋联络中的 contortion 部分 $\omega^{a} = \mathring{\omega}^{a} + \kappa^{a}$。

## AdSL 引力中的静态黑洞解

### 标架和联络

#### BTZ标架

在 BTZ 标架下的度规为
$$
\begin{equation}
\mathrm{d}s^{2} = -N(r)^2 \mathrm{d}t^2 + \frac{\mathrm{d}r^{2}}{N(r)^2} + r^2\left(\mathrm{d}\varphi + N_{\varphi}(r)\mathrm{d}t\right)^{2},
\end{equation}
$$
其中 Lapse 函数
$$
\begin{equation}
N(r)^{2} = -M + \frac{J^{2}}{4r^{2}} + \frac{r^{2}}{\ell^{2}} =: f(r), \quad N_{\varphi}(r) = -\frac{J}{2r^{2}},
\end{equation}
$$
$M$ 和 $J$ 都是积分常数。外视界 $r_{+}$ 和内视界 $r_{-}$ 分别满足
$$
\begin{align}
r_{+}^2 &= \frac{M\ell^2 + \ell\sqrt{M^2\ell^2 - J^2}}{2},\\
r_-^2 &= \frac{M\ell^2 - \ell\sqrt{M^2\ell^2 - J^2}}{2}.
\end{align}
$$
为方便后续使用，我们可以计算
$$
\begin{align}
r_+^2 + r_-^2 &= M\ell^2,\\
r_+^2 - r_-^2 &= \ell\sqrt{M^2\ell^2 - J^2},\\
r_+ r_- &= \frac{J\ell}{2}.
\end{align}
$$
#### 入射 EF 坐标系

因 BTZ 坐标在视界处存在坐标奇点，不甚方便。我们可以考虑坐标变换
$$
\begin{equation}
\left\{ \begin{aligned} v & = t + h(r) = u + 2h(r),\\ r &= r,\\ \phi & = \varphi - g(r) = \hat{\phi} - 2g(r), \end{aligned} \right.
\end{equation}
$$
切换到入射 Eddington-Finkelstein (EF) 坐标系，其中依赖于 $r$ 的函数 $h, g$ 满足
$$
\begin{equation}
\frac{\mathrm{d}h}{\mathrm{d}r} = \frac{1}{f(r)}, \quad \frac{\mathrm{d}g}{\mathrm{d}r} = \frac{N_{\varphi}(r)}{f(r)}.
\end{equation}
$$
在此坐标下，度规消除了交叉项发散，可写为
$$
\begin{equation}
\mathrm{d}s^2 = \left(r^{2}N_{\varphi}(r)^{2}-f(r)\right)\mathrm{d}v^2 + 2\mathrm{d}v\mathrm{d}r + 2r^{2}N_{\varphi}(r)\mathrm{d}v\mathrm{d}\phi + r^2\mathrm{d}\phi^2.
\end{equation}
$$
度规行列式平方根保持为 $\sqrt{-g} = r$。逆度规的非零分量为
$$
\begin{equation}
g^{vr} = 1, \quad g^{rr} = f(r) = \frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2}, \quad g^{r\phi} = -N_{\varphi}(r) = \frac{J}{2r^2}, \quad g^{\phi\phi} = \frac{1}{r^2}.
\end{equation}
$$

我们可以选取的余标架场为
$$
\begin{equation}
{e}^{\bar{0}} = \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi, \quad {e}^{\bar{1}} = \mathrm{d}v, \quad {e}^{\bar{2}} = r\mathrm{d}\phi.
\end{equation}
$$
于是度规为
$$
\begin{equation}
g = {e}^{\bar{0}}\otimes {e}^{\bar{1}} + {e}^{\bar{1}}\otimes {e}^{\bar{0}} + {e}^{\bar{2}}\otimes {e}^{\bar{2}}.
\end{equation}
$$
注意到 $e^{\bar{0}}$ 中 $\mathrm{d}r$ 前的系数为 $+1$，这个坐标系在未来视界处正则，对应于 ingoing null vector。

满足运动方程的自旋联络为
$$
\begin{equation}
{\omega}^{\bar{0}} = -\frac{b}{2}\mathrm{d}\phi, \quad {\omega}^{\bar{1}} = \mathrm{d}\phi, \quad {\omega}^{\bar{2}} = 0.
\end{equation}
$$
于是，contortion form 为
$$
\begin{equation}
{\kappa}^{\bar{0}} = \frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi, \quad {\kappa}^{\bar{1}} = 0, \quad {\kappa}^{\bar{2}} = -\frac{r}{\ell^{2}}\mathrm{d}v.
\end{equation}
$$
注意，自旋联络有一个冗余自由度（积分常数 $b$）。规范群随 AdSL 代数的引入而扩大，这使得黑洞的解空间（相空间）被扩展了。积分常数 $b$ 就是这个扩展相空间里的新坐标。

使用非对角 Minkowski 度规
$$(\eta_{\bar{a}\bar{b}}) = \begin{pmatrix} 0 &1 &0\\ 1 &0 &0\\ 0 &0 &1 \end{pmatrix}$$
进行指标下降，我们得到入射系下的所有降指标形式：
$$
\begin{align}
&{e}_{\bar{0}} = \eta_{\bar{0}\bar{1}}{e}^{\bar{1}} = \mathrm{d}v, &&{e}_{\bar{1}} = \eta_{\bar{1}\bar{0}}{e}^{\bar{0}} = \frac{1}{2\ell^{2}}\left(\ell^{2}M - r^{2}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi, &&{e}_{\bar{2}} = \eta_{\bar{2}\bar{2}}{e}^{\bar{2}} = r\mathrm{d}\phi,\\
&{\omega}_{\bar{0}} = \eta_{\bar{0}\bar{1}}{\omega}^{\bar{1}} = \mathrm{d}\phi, &&{\omega}_{\bar{1}} = \eta_{\bar{1}\bar{0}}{\omega}^{\bar{0}} = -\frac{b}{2}\mathrm{d}\phi, &&{\omega}_{\bar{2}} = \eta_{\bar{2}\bar{2}}{\omega}^{\bar{2}} = 0,\\
&{\kappa}_{\bar{0}} = \eta_{\bar{0}\bar{1}}{\kappa}^{\bar{1}} = 0, &&{\kappa}_{\bar{1}} = \eta_{\bar{1}\bar{0}}{\kappa}^{\bar{0}} = \frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi, &&{\kappa}_{\bar{2}} = \eta_{\bar{2}\bar{2}}{\kappa}^{\bar{2}} = -\frac{r}{\ell^{2}}\mathrm{d}v.
\end{align}
$$

#### 出射 EF 坐标系

类似地，我们考虑坐标变换
$$
\begin{equation}
\left\{
\begin{aligned}
u &= t - h(r),\\
r &= r,\\
\hat{\phi} &= \varphi + g(r),
\end{aligned}
\right.
\end{equation}
$$
使用出射 EF 坐标系（亦称 BMS 标架），其中依赖于 $r$ 的函数 $h, g$ 满足同样的关系。

在此坐标下，度规可写为
$$
\begin{equation}
\mathrm{d}s^2 = \frac{1}{\ell^2}(\ell^2 M - r^2)\mathrm{d}u^2 - 2\mathrm{d}u\mathrm{d}r - J\mathrm{d}u\mathrm{d}\hat{\phi} + r^2\mathrm{d}\hat{\phi}^2.
\end{equation}
$$
注意，相比于入射 EF 系，出射系的径向微分的符号发生反转。度规行列式平方根 $\sqrt{-g} = r$。逆度规的非零分量为
$$
\begin{equation}
g^{ur} = -1, \quad g^{rr} = \frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2} = f(r), \quad g^{r\hat{\phi}} = -\frac{J}{2r^2} = N_{\varphi}(r), \quad g^{\hat{\phi}\hat{\phi}} = \frac{1}{r^2}.
\end{equation}
$$

我们可以选取的余标架场为
$$
\begin{equation}
\hat{e}^{\bar{0}} = \frac{1}{2\ell^{2}}\left(\ell^{2}M - r^{2}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}, \quad \hat{e}^{\bar{1}} = \mathrm{d}u, \quad \hat{e}^{\bar{2}} = r\mathrm{d}\hat{\phi},
\end{equation}
$$
于是度规可以用标架形式写为
$$
\begin{equation}
g = \hat{e}^{\bar{0}}\otimes \hat{e}^{\bar{1}} + \hat{e}^{\bar{1}}\otimes \hat{e}^{\bar{0}} + \hat{e}^{\bar{2}}\otimes \hat{e}^{\bar{2}},
\end{equation}
$$
此时满足运动方程的自旋联络为
$$
\begin{equation}
\hat{\omega}^{\bar{0}} = \frac{b}{2}\mathrm{d}\hat{\phi}, \quad \hat{\omega}^{\bar{1}} = -\mathrm{d}\hat{\phi}, \quad \omega^{\bar{2}} = 0.
\end{equation}
$$
于是 contortion form 为
$$
\begin{equation}
\hat{\kappa}^{\bar{0}} = -\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}, \quad \hat{\kappa}^{\bar{1}} = 0, \quad \hat{\kappa}^{\bar{2}} = \frac{r}{\ell^{2}}\mathrm{d}u.
\end{equation}
$$
同样地，几何中的形式的 Lorentz 指标升降都由上述非对角 Minkowski 度规 $\eta_{\bar{a}\bar{b}}$ 给出，从而
$$
\begin{align}
\hat{e}_{\bar{0}} & = \mathrm{d}u, &\hat{e}_{\bar{1}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}, &\hat{e}_{\bar{2}} &= r\mathrm{d}\hat{\phi},\\
\hat{\omega}_{\bar{0}} &= {-}\mathrm{d}\hat{\phi}, &\hat{\omega}_{\bar{1}} &= {+}\frac{b}{2}\mathrm{d}\hat{\phi}, &\hat{\omega}_{\bar{2}} &= 0,\\
\hat{\kappa}_{\bar{0}} &= 0, &\hat{\kappa}_{\bar{1}} &= -\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}, &\hat{\kappa}_{\bar{2}} &= \frac{r}{\ell^{2}}\mathrm{d}u.
\end{align}
$$

具体验算见 [[AdSL稳态黑洞解EF标架的验算]]。

### 热力学性质

这个黑洞具有规范荷
$$
\begin{align}
m &= \alpha_{1}M - \frac{\alpha_{2}}{\ell}J,\\
j &= (\alpha_{0} - \alpha_{2})\ell b + \alpha_{1}J - \alpha_{2}\ell M,\\
w &= (\alpha_{0} - \alpha_{2})\ell b.
\end{align}
$$
黑洞熵为
$$
\begin{equation}
S = 2\pi\sqrt{\ell}\left(\sqrt{(\ell m + j - w)(\alpha_{1} - \alpha_{2})} + \sqrt{(\ell m - j + w)(\alpha_{1} + \alpha_{2})} + 4\sqrt{w(\alpha_{2} - \alpha_{0})}\right).
\end{equation}
$$
