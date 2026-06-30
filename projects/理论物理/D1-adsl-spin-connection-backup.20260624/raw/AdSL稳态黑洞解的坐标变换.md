考虑 Ingoing 解
$$
\begin{align}
e^{\bar{0}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi , &e^{\bar{1}} &= \mathrm{d}v , &e^{\bar{2}} &= r\mathrm{d}\phi, \\
\omega^{\bar{0}} &= -\frac{b}{2}\mathrm{d}\phi , &\omega^{\bar{1}} &= \mathrm{d}\phi , &\omega^{\bar{2}} &= 0.
\end{align}
$$
标架场 $E_{\bar{a}}$ 和余标架场 $e^{\bar{a}}$ 互为对偶基，即
$$
e^{\bar{a}}(E_{\bar{b}}) = \delta^{\bar{a}}_{\bar{b}},
$$
并注意到坐标基的对偶性
$$
\mathrm{d}x^{\mu}(\partial_{\nu}) = \delta^{\mu}_{\nu},
$$
于是标架场的坐标分量 $(E_{\bar{a}})^{\mu}$ 形成的矩阵是余标架场的坐标分量 $(e^{\bar{a}})_{\mu}$ 形成的矩阵的转置矩阵的逆矩阵。于是，上述解对应的标架场为
$$
E_{\bar{0}} = \partial_{r}, \quad E_{\bar{1}} = \partial_{v} - \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\partial_{r},\quad E_{\bar{2}} = \frac{J}{2r} \partial_{r} + \frac{1}{r}\partial_{\phi}.
$$

考虑坐标变换 $(v, r, \phi)\mapsto (T, z, X)$：
$$
\begin{align}
\left\{
\begin{aligned}
z &= \frac{r^{2} - r_{+}^{2}}{r^{2} - r_{-}^{2}},\\
T+X &= (r_{+}-r_{-})(v+\phi-h(r)+g(r)),\\
T-X &= (r_{+}+r_{-})(v-\phi-h(r)-g(r)),
\end{aligned}
\right.
\end{align}
$$
其中
$$
\frac{\mathrm{d}h}{\mathrm{d}r} = \frac{1}{f(r)} = \frac{1}{\frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2}}, \quad \frac{\mathrm{d}g}{\mathrm{d}r} = \frac{N_{\varphi}(r)}{f(r)} = -\frac{\frac{J}{2r^2}}{\frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2}}.
$$
逆变换为
$$
\begin{align}
\left\{
\begin{aligned}
r^2 &= \frac{r_{+}^2}{1-z} - \frac{r_{-}^2 z}{1-z} =: R(z)^2, &\text{where }R(z)>0,\\
v + \phi &= \frac{T+X}{r_{+} - r_{-}} + h(r) - g(r),\\
v - \phi &= \frac{T-X}{r_{+} + r_{-}} + h(r) + g(r),
\end{aligned}
\right.
\end{align}
$$
从而
$$
\begin{align}
f(r) &= \frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2} = \frac{R(z)^2}{\ell^2} - M + \frac{J^2}{4R(z)^2} &=: F(z),\\
N_{\varphi}(r) &= - \frac{J}{2r^2} = - \frac{J}{2R(z)^2} &=: \mathcal{N}(z).
\end{align}
$$
特别地，记
$$
\mathcal{M}(z):= M - \frac{R(z)^2}{\ell^2},
$$
从而
$$
F(z) = - \mathcal{M}(z) + \frac{J^2}{4R(z)^2} = - \mathcal{M}(z) - \frac{J}{2}\mathcal{N}(z).
$$
也就是说
$$
J\mathcal{N}(z) = -2(F(z) + \mathcal{M}(z)).
$$

根据逆变换余切向量场的坐标基满足
$$
\begin{align}
\left\{
\begin{aligned}
2r\mathrm{d}r &= \frac{r_{+}^2 - r_{-}^{2}}{(1 - z)^2}\mathrm{d}z,\\
\mathrm{d}v + \mathrm{d}\phi &= \frac{1}{r_{+} - r_{-}}(\mathrm{d}T + \mathrm{d}X) + \frac{\mathrm{d}r}{f(r)} - \frac{N_{\varphi}(r)}{f(r)}\mathrm{d}r = \frac{1}{r_{+} - r_{-}}(\mathrm{d}T + \mathrm{d}X) + \frac{1-\mathcal{N}(z)}{F(z)}\mathrm{d}r,\\
\mathrm{d}v - \mathrm{d}\phi &= \frac{1}{r_{+} + r_{-}}(\mathrm{d}T - \mathrm{d}X) + \frac{1+\mathcal{N}(z)}{F(z)}\mathrm{d}r,
\end{aligned}
\right.
\end{align}
$$
记
$$
\Delta_{r} := r_{+}^2 - r_{-}^{2},
$$
从而
$$
\begin{align}
\left\{
\begin{aligned}
\mathrm{d}r &= \frac{\Delta_{r}}{2}\frac{\mathrm{d}z}{R(z)(1 - z)^2},\\
\mathrm{d}v &= \frac{r_{+}}{\Delta_{r}}\mathrm{d}T + \frac{r_{-}}{\Delta_{r}}\mathrm{d}X + \frac{\Delta_{r}}{2}\frac{1}{F(z)}\frac{\mathrm{d}z}{R(z)(1 - z)^2},\\
\mathrm{d}\phi &= \frac{r_{-}}{\Delta_{r}}\mathrm{d}T + \frac{r_{+}}{\Delta_{r}}\mathrm{d}X - \frac{\Delta_{r}}{2}\frac{\mathcal{N}(z)}{F(z)}\frac{\mathrm{d}z}{R(z)(1 - z)^2}.
\end{aligned}
\right.
\end{align}
$$
特别地，
$$
\begin{align}
J\mathrm{d}\phi &= \frac{Jr_{-}}{\Delta_{r}}\mathrm{d}T + \frac{Jr_{+}}{\Delta_{r}}\mathrm{d}X + \Delta_{r}\left(1+\frac{\mathcal{M}(z)}{F(z)}\right)\frac{\mathrm{d}z}{R(z)(1 - z)^2},\\
\mathcal{M}(z)\mathrm{d}v - J\mathrm{d}\phi &= \frac{\mathcal{M}(z)r_{+} - Jr_{-}}{\Delta_{r}}\mathrm{d}T + \frac{- Jr_{+} + \mathcal{M}(z)r_{-}}{\Delta_{r}}\mathrm{d}X - \Delta_{r}\left(\frac{1}{2}\frac{\mathcal{M}(z)}{F(z)} + 1\right)\frac{\mathrm{d}z}{R(z)(1 - z)^2},
\end{align}
$$
于是余标架场为
$$
\begin{align}
e^{\bar{0}} &= \frac{1}{2}\left(\mathcal{M}(z)\mathrm{d}v - J\mathrm{d}\phi\right) + \mathrm{d}r = \frac{\mathcal{M}(z)r_{+} - Jr_{-}}{2\Delta_{r}}\mathrm{d}T + \frac{- Jr_{+} + \mathcal{M}(z)r_{-}}{2\Delta_{r}}\mathrm{d}X - \frac{\Delta_{r}}{2}\left(\frac{1}{2}\frac{\mathcal{M}(z)}{F(z)}\right)\frac{\mathrm{d}z}{R(z)(1 - z)^2}, \\
e^{\bar{1}} &= \mathrm{d}v = \frac{r_{+}}{\Delta_{r}}\mathrm{d}T + \frac{r_{-}}{\Delta_{r}}\mathrm{d}X + \frac{\Delta_{r}}{2}\frac{1}{F(z)}\frac{\mathrm{d}z}{R(z)(1 - z)^2}, \\
e^{\bar{2}} &= R(z)\mathrm{d}\phi = \frac{R(z)r_{-}}{\Delta_{r}}\mathrm{d}T + \frac{R(z)r_{+}}{\Delta_{r}}\mathrm{d}X - \frac{\Delta_{r}}{2}\frac{\mathcal{N}(z)}{F(z)}\frac{\mathrm{d}z}{(1 - z)^2},
\end{align}
$$
联络为
$$
\begin{align}
\omega^{\bar{0}} &= -\frac{b}{2}\mathrm{d}\phi = -\frac{b}{2}\left(\frac{r_{-}}{\Delta_{r}}\mathrm{d}T + \frac{r_{+}}{\Delta_{r}}\mathrm{d}X - \frac{\Delta_{r}}{2}\frac{\mathcal{N}(z)}{F(z)R(z)(1-z)^2}\mathrm{d}z\right), \\
\omega^{\bar{1}} &= \mathrm{d}\phi = \frac{r_{-}}{\Delta_{r}}\mathrm{d}T + \frac{r_{+}}{\Delta_{r}}\mathrm{d}X - \frac{\Delta_{r}}{2}\frac{\mathcal{N}(z)}{F(z)R(z)(1-z)^2}\mathrm{d}z, \\
\omega^{\bar{2}} &= 0.
\end{align}
$$

由坐标变换可知，
$$
\begin{align}
\mathrm{d}z &= 2(r_{+}^2 - r_{-}^2)\frac{r}{(r^2-r_{-}^{2})^2}\mathrm{d}r = 2\Delta_{r}\frac{r}{(r^2-r_{-}^{2})^2}\mathrm{d}r,\\
\mathrm{d}T + \mathrm{d}X &= (r_{+}-r_{-})\left(\mathrm{d}v+\mathrm{d}\phi+\left(-\frac{1}{f(r)} + \frac{N_{\varphi}(r)}{f(r)}\right)\mathrm{d}r\right),\\
\mathrm{d}T - \mathrm{d}X &= (r_{+}+r_{-})\left(\mathrm{d}v-\mathrm{d}\phi - \left(\frac{1}{f(r)} + \frac{N_{\varphi}(r)}{f(r)}\right)\mathrm{d}r\right),
\end{align}
$$
后二者等价于
$$
\begin{align}
\mathrm{d}T &= r_{+}\mathrm{d}v - r_{-}\mathrm{d}\phi - \frac{r_{-} + r_{+}N_{\varphi}(r)}{f(r)} \mathrm{d}r = r_{+}\mathrm{d}v - r_{-}\mathrm{d}\phi - \frac{r_{-} + r_{+}\mathcal{N}(z)}{F(z)} \mathrm{d}r,\\
\mathrm{d}X &= -r_{-}\mathrm{d}v + r_{+}\mathrm{d}\phi - \frac{r_{-}N_{\varphi}(r) + r_{+}}{f(r)}\mathrm{d}r = -r_{-}\mathrm{d}v + r_{+}\mathrm{d}\phi - \frac{r_{-}\mathcal{N}(z) + r_{+}}{F(z)}\mathrm{d}r.
\end{align}
$$
于是
$$
\begin{align}
\partial_{v} &= \frac{\partial T}{\partial v}\partial_{T} + \frac{\partial X}{\partial v}\partial_{X} = r_{+}\partial_{T} - r_{-}\partial_{X},\\
\partial_{r} &= \frac{\partial T}{\partial r}\partial_{T} + \frac{\partial X}{\partial r}\partial_{X} + \frac{\partial z}{\partial r}\partial_{z} = - \frac{r_{-} + r_{+}\mathcal{N}(z)}{F(z)}\partial_{T} - \frac{r_{-}\mathcal{N}(z) + r_{+}}{F(z)}\partial_{X} + 2\Delta_{r}\frac{R(z)}{(R(z)^2-r_{-}^{2})^2}\partial_{z},\\
\partial_{\phi} &= \frac{\partial T}{\partial \phi}\partial_{T} + \frac{\partial X}{\partial \phi}\partial_{X} = - r_{-}\partial_{T} + r_+{}\partial_{X}.
\end{align}
$$
特别地，
$$
J\partial_{r} = \frac{- Jr_{-} + 2 \left(\mathcal{M}(z) + F(z)\right)r_{+}}{F(z)}\partial_{T} + \frac{2 \left(\mathcal{M}(z) + F(z)\right)r_{-} - Jr_{+}}{F(z)}\partial_{X} + 2J\Delta_{r}\frac{R(z)}{(R(z)^2-r_{-}^{2})^2}\partial_{z}
$$
因此标架场为
$$
\begin{align}
E_{\bar{0}} &= \partial_{r},\\
E_{\bar{1}} &= \partial_{v} - \frac{1}{2}\mathcal{M}(z)\partial_{r},\\
E_{\bar{2}}& = \frac{J}{2R(z)} \partial_{r} + \frac{1}{R(z)}\partial_{\phi}
\end{align}
$$