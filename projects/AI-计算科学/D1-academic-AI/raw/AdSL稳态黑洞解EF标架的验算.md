基本设定：
$$
\begin{align}
\epsilon_{\bar{0}\bar{1}\bar{2}} = \epsilon_{\bar{1}\bar{2}\bar{0}} = \epsilon_{\bar{2}\bar{0}\bar{1}} &= 1,&\epsilon_{\bar{0}\bar{2}\bar{1}} = \epsilon_{\bar{1}\bar{0}\bar{2}} = \epsilon_{\bar{2}\bar{1}\bar{0}} &= -1,\\
\epsilon^{\bar{0}\bar{1}\bar{2}} = \epsilon^{\bar{1}\bar{2}\bar{0}} = \epsilon^{\bar{2}\bar{0}\bar{1}} &= -1, &\epsilon^{\bar{0}\bar{2}\bar{1}} = \epsilon^{\bar{1}\bar{0}\bar{2}} = \epsilon^{\bar{2}\bar{1}\bar{0}} &= 1.
\end{align}
$$

$$
\begin{align}
R^{\bar{a}} &&&= \mathrm{d}\omega^{\bar{a}} - \frac{1}{2}\epsilon^{\bar{a}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\omega_{\bar{c}},\\
T^{\bar{a}} &= \mathrm{D}_\omega e^{\bar{a}} &&= \mathrm{d}e^{\bar{a}} - \epsilon^{\bar{a}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}},\\
F^{\bar{a}} &= \mathrm{D}_{\omega}\sigma^{\bar{a}} + \frac{1}{2}\epsilon^{\bar{a}\bar{b}\bar{c}}\sigma_{\bar{b}}\wedge\sigma_{\bar{c}} &&= \mathrm{d}\kappa^{\bar{a}} - \epsilon^{\bar{a}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\kappa_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{a}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge\kappa_{\bar{c}}.
\end{align}
$$

## Outgoing

$$
\begin{align}
\hat{e}^{\bar{0}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}, &\hat{e}^{\bar{1}} &= \mathrm{d}u, &\hat{e}^{\bar{2}} &= r\mathrm{d}\hat{\phi},\\
\hat{\omega}^{\bar{0}} &= {+}\frac{b}{2}\mathrm{d}\hat{\phi}, &\hat{\omega}^{\bar{1}} &= {-}\mathrm{d}\hat{\phi}, &\omega^{\bar{2}} &= 0,\\
\hat{\kappa}^{\bar{0}} &= -\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}, &\hat{\kappa}^{\bar{1}} &= 0, &\hat{\kappa}^{\bar{2}} &= \frac{r}{\ell^{2}}\mathrm{d}u.
\end{align}
$$

$$
\begin{align}
\hat{e}_{\bar{0}} & = \mathrm{d}u, &\hat{e}_{\bar{1}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}, &\hat{e}_{\bar{2}} &= r\mathrm{d}\hat{\phi},\\
\hat{\omega}_{\bar{0}} &= {-}\mathrm{d}\hat{\phi}, &\hat{\omega}_{\bar{1}} &= {+}\frac{b}{2}\mathrm{d}\hat{\phi}, &\hat{\omega}_{\bar{2}} &= 0,\\
\hat{\kappa}_{\bar{0}} &= 0, &\hat{\kappa}_{\bar{1}} &= -\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}, &\hat{\kappa}_{\bar{2}} &= \frac{r}{\ell^{2}}\mathrm{d}u.
\end{align}
$$

$$
\begin{align}
\mathrm{d}\hat{e}^{\bar{0}} &= \frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r, &\mathrm{d}\hat{e}^{\bar{1}} &= 0, &\mathrm{d}\hat{e}^{\bar{2}} &= \mathrm{d}r\wedge\mathrm{d}\hat{\phi},\\
\mathrm{d}\hat{\omega}^{\bar{0}} &= 0, &\mathrm{d}\hat{\omega}^{\bar{1}} &= 0, &\mathrm{d}\omega^{\bar{2}} &= 0,\\
\mathrm{d}\hat{\kappa}^{\bar{0}} &= -\frac{r}{\ell^{2}}\mathrm{d}r\wedge\mathrm{d}\hat{\phi}, &\mathrm{d}\hat{\kappa}^{\bar{1}} &= 0, &\mathrm{d}\hat{\kappa}^{\bar{2}} &= -\frac{1}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r.
\end{align}
$$

### $(e, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{e}_{\bar{1}}\wedge \hat{e}_{\bar{2}} + \hat{e}_{\bar{2}}\wedge \hat{e}_{\bar{1}} = -2\hat{e}_{\bar{1}}\wedge \hat{e}_{\bar{2}} &= -2\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(r\mathrm{d}\hat{\phi}\right)\\
&= -r\left(\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - 2\mathrm{d}r\right)\wedge\mathrm{d}\hat{\phi},\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{e}_{\bar{2}}\wedge \hat{e}_{\bar{0}} + \hat{e}_{\bar{0}}\wedge \hat{e}_{\bar{2}} = -2\hat{e}_{\bar{2}}\wedge \hat{e}_{\bar{0}} &= -2\left(r\mathrm{d}\hat{\phi}\right)\wedge\left(\mathrm{d}u\right)\\
&= 2r \mathrm{d}u\wedge \mathrm{d}\hat{\phi},\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{e}_{\bar{0}}\wedge \hat{e}_{\bar{1}} + \hat{e}_{\bar{1}}\wedge \hat{e}_{\bar{0}} = -2\hat{e}_{\bar{0}}\wedge \hat{e}_{\bar{1}} &= -2\left(\mathrm{d}u\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right)\\
&= \mathrm{d}u\wedge\left( 2\mathrm{d}r + J\mathrm{d}\hat{\phi}\right).
\end{align}
$$

### $(\omega, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\omega}_{\bar{1}}\wedge \hat{e}_{\bar{2}} + \hat{\omega}_{\bar{2}}\wedge \hat{e}_{\bar{1}} &= -\left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(r\mathrm{d}\hat{\phi}\right) + \left(0\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right)\\
&= 0,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\omega}_{\bar{2}}\wedge \hat{e}_{\bar{0}} + \hat{\omega}_{\bar{0}}\wedge \hat{e}_{\bar{2}} &= -\left(0\right)\wedge\left(\mathrm{d}u\right) + \left({-}\mathrm{d}\hat{\phi}\right)\wedge\left(r\mathrm{d}\hat{\phi}\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\omega}_{\bar{0}}\wedge \hat{e}_{\bar{1}} + \hat{\omega}_{\bar{1}}\wedge \hat{e}_{\bar{0}} &= -\left({-}\mathrm{d}\hat{\phi}\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right) + \left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(\mathrm{d}u\right)\\
&= {-}\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}u - \mathrm{d}r\right) \wedge \mathrm{d}\hat{\phi}.
\end{align}
$$

### $(\omega, \omega)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\omega}_{\bar{c}} = - \hat{\omega}_{\bar{1}}\wedge \hat{\omega}_{\bar{2}} + \hat{\omega}_{\bar{2}}\wedge \hat{\omega}_{\bar{1}} = -2\hat{\omega}_{\bar{1}}\wedge \hat{\omega}_{\bar{2}} &= -2\left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(0\right)\\
&= 0,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\omega}_{\bar{c}} = - \hat{\omega}_{\bar{2}}\wedge \hat{\omega}_{\bar{0}} + \hat{\omega}_{\bar{0}}\wedge \hat{\omega}_{\bar{2}} = -2\hat{\omega}_{\bar{2}}\wedge \hat{\omega}_{\bar{0}} &= -2\left(0\right)\wedge\left({-}\mathrm{d}\hat{\phi}\right)\\
&=0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\omega}_{\bar{c}} = - \hat{\omega}_{\bar{0}}\wedge \hat{\omega}_{\bar{1}} + \hat{\omega}_{\bar{1}}\wedge \hat{\omega}_{\bar{0}} = -2\hat{\omega}_{\bar{0}}\wedge \hat{\omega}_{\bar{1}} &= -2\left({-}\mathrm{d}\hat{\phi}\right)\wedge\left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\\
&=0.
\end{align}
$$

### $(\omega, \kappa)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\omega}_{\bar{1}}\wedge \hat{\kappa}_{\bar{2}} + \hat{\omega}_{\bar{2}}\wedge \hat{\kappa}_{\bar{1}} &= -\left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(\frac{r}{\ell^{2}}\mathrm{d}u\right) + \left(0\right)\wedge\left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right)\\
&=\frac{br}{2\ell^{2}} \mathrm{d}u\wedge \mathrm{d}\hat{\phi},\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\omega}_{\bar{2}}\wedge \hat{\kappa}_{\bar{0}} + \hat{\omega}_{\bar{0}}\wedge \hat{\kappa}_{\bar{2}} &= -\left(0\right)\wedge\left(0\right) + \left({-}\mathrm{d}\hat{\phi}\right)\wedge\left(\frac{r}{\ell^{2}}\mathrm{d}u\right)\\
&= \frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}\hat{\phi},\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\omega}_{\bar{0}}\wedge \hat{\kappa}_{\bar{1}} + \hat{\omega}_{\bar{1}}\wedge \hat{\kappa}_{\bar{0}} &= -\left({-}\mathrm{d}\hat{\phi}\right)\wedge\left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right) + \left({+}\frac{b}{2}\mathrm{d}\hat{\phi}\right)\wedge\left(0\right)\\
&= \frac{J}{2\ell^{2}} \mathrm{d}u\wedge \mathrm{d}\hat{\phi}.
\end{align}
$$

### $(\kappa, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\kappa}_{\bar{1}}\wedge \hat{e}_{\bar{2}} + \hat{\kappa}_{\bar{2}}\wedge \hat{e}_{\bar{1}} &= -\left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right)\wedge\left(r\mathrm{d}\hat{\phi}\right) + \left(\frac{r}{\ell^{2}}\mathrm{d}u\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right)\\
&= -\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\kappa}_{\bar{2}}\wedge \hat{e}_{\bar{0}} + \hat{\kappa}_{\bar{0}}\wedge \hat{e}_{\bar{2}} &= -\left(\frac{r}{\ell^{2}}\mathrm{d}u\right)\wedge\left(\mathrm{d}u\right) + \left(0\right)\wedge\left(r\mathrm{d}\hat{\phi}\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} = - \hat{\kappa}_{\bar{0}}\wedge \hat{e}_{\bar{1}} + \hat{\kappa}_{\bar{1}}\wedge \hat{e}_{\bar{0}} &= -\left(0\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}\right) + \left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right)\wedge\left(\mathrm{d}u\right)\\
&= \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}u\wedge\mathrm{d}\hat{\phi}.
\end{align}
$$

### $(\kappa, \kappa)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\kappa}_{\bar{1}}\wedge \hat{\kappa}_{\bar{2}} + \hat{\kappa}_{\bar{2}}\wedge \hat{\kappa}_{\bar{1}} = -2\hat{\kappa}_{\bar{1}}\wedge \hat{\kappa}_{\bar{2}} &= -2\left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right)\wedge\left(\frac{r}{\ell^{2}}\mathrm{d}u\right)\\
&= -\frac{r}{\ell^{2}}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}u\wedge\mathrm{d}\hat{\phi},\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\kappa}_{\bar{2}}\wedge \hat{\kappa}_{\bar{0}} + \hat{\kappa}_{\bar{0}}\wedge \hat{\kappa}_{\bar{2}} = -2\hat{\kappa}_{\bar{2}}\wedge \hat{\kappa}_{\bar{0}} &= -2\left(\frac{r}{\ell^{2}}\mathrm{d}u\right)\wedge\left(0\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge \hat{\kappa}_{\bar{c}} = - \hat{\kappa}_{\bar{0}}\wedge \hat{\kappa}_{\bar{1}} + \hat{\kappa}_{\bar{1}}\wedge \hat{\kappa}_{\bar{0}} = -2\hat{\kappa}_{\bar{0}}\wedge \hat{\kappa}_{\bar{1}} &= -2\left(0\right)\wedge\left(-\frac{J}{2\ell^{2}}\mathrm{d}u - \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\hat{\phi}\right)\\
&= 0.
\end{align}
$$

### $R$
$$
\begin{align}
\hat{R}^{\bar{0}} = \mathrm{d}\hat{\omega}^{\bar{0}} - \frac{1}{2}\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\omega}_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right)\\
&=0,\\
\hat{R}^{\bar{1}} = \mathrm{d}\hat{\omega}^{\bar{1}} - \frac{1}{2}\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\omega}_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right)\\
&=0,\\
\hat{R}^{\bar{2}} = \mathrm{d}\hat{\omega}^{\bar{2}} - \frac{1}{2}\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\omega}_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right)\\
&=0.
\end{align}
$$

### $T$
$$
\begin{align}
\hat{T}^{\bar{0}} = \mathrm{d}\hat{e}^{\bar{0}} - \epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r\right) - \left(0\right)\\
&=\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r,\\
\hat{T}^{\bar{1}} = \mathrm{d}\hat{e}^{\bar{1}} - \epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left(0\right) - \left(0\right)\\
&=0,\\
\hat{T}^{\bar{2}} = \mathrm{d}\hat{e}^{\bar{2}} - \epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left(\mathrm{d}r\wedge\mathrm{d}\hat{\phi}\right) - \left({-}\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}u - \mathrm{d}r\right) \wedge \mathrm{d}\hat{\phi}\right)\\
&= \left({+}\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}u + {0}\mathrm{d}r\right) \wedge \mathrm{d}\hat{\phi}\\
&{=\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}u \wedge\mathrm{d}\hat{\phi}}.
\end{align}
$$

### $F$
$$
\begin{align}
\hat{F}^{\bar{0}} = \mathrm{d}\hat{\kappa}^{\bar{0}} - \epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} &= \left(-\frac{r}{\ell^{2}}\mathrm{d}r\wedge\mathrm{d}\hat{\phi}\right) - \left(\frac{br}{2\ell^{2}} \mathrm{d}u\wedge \mathrm{d}\hat{\phi}\right) +\frac{1}{2}\left(-\frac{r}{\ell^{2}}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}u\wedge\mathrm{d}\hat{\phi}\right)\\
&{= \frac{r}{\ell^{2}}\left(\frac{1}{2}\left(- \frac{r^2}{\ell^2} + M\right)\mathrm{d}u -\mathrm{d}r\right)\wedge \mathrm{d}\hat{\phi}},\\
\hat{F}^{\bar{1}} = \mathrm{d}\hat{\kappa}^{\bar{1}} - \epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} &= \left(0\right) - \left(\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}\hat{\phi}\right) +\frac{1}{2}\left(0\right)\\
&= {-}\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}\hat{\phi},\\
\hat{F}^{\bar{2}} = \mathrm{d}\hat{\kappa}^{\bar{2}} - \epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\omega}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{\kappa}_{\bar{b}}\wedge\hat{\kappa}_{\bar{c}} &= \left(-\frac{1}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r\right) - \left(\frac{J}{2\ell^{2}}\mathrm{d}u\wedge\mathrm{d}\hat{\phi}\right) +\frac{1}{2}\left(0\right)\\
&{=-\frac{1}{\ell^{2}}\mathrm{d}u\wedge\left(\mathrm{d}r + \frac{J}{2}\mathrm{d}\hat{\phi}\right)}.
\end{align}
$$

### EoM for $R$
$$
\begin{align}
\hat{R}^{\bar{0}} = 0,\\
\hat{R}^{\bar{1}} = 0,\\
\hat{R}^{\bar{2}} = 0.
\end{align}
$$

### EoM for $T$
$$
\begin{align}
\hat{T}^{\bar{0}} + \epsilon^{\bar{0}\bar{b}\bar{c}} \hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r\right) + \left(-\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}r\right)\\
&=0,\\
\hat{T}^{\bar{1}} + \epsilon^{\bar{1}\bar{b}\bar{c}} \hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left(0\right) + \left(0\right)\\
&=0,\\
\hat{T}^{\bar{2}} + \epsilon^{\bar{2}\bar{b}\bar{c}} \hat{\kappa}_{\bar{b}}\wedge \hat{e}_{\bar{c}} &= \left({\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}u \wedge\mathrm{d}\hat{\phi}}\right) + \left(\frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}u\wedge\mathrm{d}\hat{\phi}\right)\\
&= {0}.
\end{align}
$$

### EoM for $F$
$$
\begin{align}
\hat{F}^{\bar{0}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{0}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge\hat{e}_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\left(\frac{1}{2}\left(- \frac{r^2}{\ell^2} + M\right)\mathrm{d}u -\mathrm{d}r\right)\wedge \mathrm{d}\hat{\phi}\right) + \frac{1}{2\ell^{2}}\left(-r\left(\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}u - 2\mathrm{d}r\right)\wedge\mathrm{d}\hat{\phi}\right)\\
&= 0,\\
\hat{F}^{\bar{1}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{1}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge\hat{e}_{\bar{c}} &= \left(-\frac{r}{\ell^{2}}\mathrm{d}u\wedge\mathrm{d}\hat{\phi}\right) + \frac{1}{2\ell^{2}}\left(2r \mathrm{d}u\wedge \mathrm{d}\hat{\phi}\right)\\
&= 0,\\
\hat{F}^{\bar{2}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{2}\bar{b}\bar{c}}\hat{e}_{\bar{b}}\wedge\hat{e}_{\bar{c}} &= \left(-\frac{1}{\ell^{2}}\mathrm{d}u\wedge\left(\mathrm{d}r + \frac{J}{2}\mathrm{d}\hat{\phi}\right)\right) + \frac{1}{2\ell^{2}}\left(\mathrm{d}u\wedge\left( 2\mathrm{d}r + J\mathrm{d}\hat{\phi}\right)\right)\\
&= 0.
\end{align}
$$

## Ingoing

$$
\begin{align}
e^{\bar{0}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi , &e^{\bar{1}} &= \mathrm{d}v , &e^{\bar{2}} &= r\mathrm{d}\phi, \\
\omega^{\bar{0}} &= -\frac{b}{2}\mathrm{d}\phi , &\omega^{\bar{1}} &= \mathrm{d}\phi , &\omega^{\bar{2}} &= 0, \\
\kappa^{\bar{0}} &= \frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi , &\kappa^{\bar{1}} &= 0 , &\kappa^{\bar{2}} &= -\frac{r}{\ell^{2}}\mathrm{d}v.
\end{align}
$$

$$
\begin{align}
e_{\bar{0}} &= \mathrm{d}v, &e_{\bar{1}} &= \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi, &e_{\bar{2}} &= r\mathrm{d}\phi,\\
\omega_{\bar{0}} &= \mathrm{d}\phi, &\omega_{\bar{1}} &= -\frac{b}{2}\mathrm{d}\phi, &\omega_{\bar{2}} &= 0,\\
\kappa_{\bar{0}} &= 0, &\kappa_{\bar{1}} &= \frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi, &\kappa_{\bar{2}} &= -\frac{r}{\ell^{2}}\mathrm{d}v.
\end{align}
$$

$$
\begin{align}
\mathrm{d}e^{\bar{0}} &= \frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r, &\mathrm{d}e^{\bar{1}} &= 0, &\mathrm{d}e^{\bar{2}} &= \mathrm{d}r\wedge\mathrm{d}\phi,\\
\mathrm{d}\omega^{\bar{0}} &= 0, &\mathrm{d}\omega^{\bar{1}} &= 0, &\mathrm{d}\omega^{\bar{2}} &= 0,\\
\mathrm{d}\kappa^{\bar{0}} &= \frac{r}{\ell^{2}}\mathrm{d}r\wedge\mathrm{d}\phi, &\mathrm{d}\kappa^{\bar{1}} &= 0, &\mathrm{d}\kappa^{\bar{2}} &= \frac{1}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r.
\end{align}
$$

### $(e, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} = -2e_{\bar{1}}\wedge e_{\bar{2}} &= -2\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right)\wedge\left(r\mathrm{d}\phi\right)\\
&= -r\left(\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + 2\mathrm{d}r\right)\wedge\mathrm{d}\phi, \\
\epsilon^{\bar{1}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} = -2e_{\bar{2}}\wedge e_{\bar{0}} &= -2\left(r\mathrm{d}\phi\right)\wedge\left(\mathrm{d}v\right)\\
&= 2r \mathrm{d}v\wedge\mathrm{d}\phi, \\
\epsilon^{\bar{2}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} = -2e_{\bar{0}}\wedge e_{\bar{1}} &= -2\left(\mathrm{d}v\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right)\\
&= - \mathrm{d}v\wedge\left( 2\mathrm{d}r - J\mathrm{d}\phi\right).
\end{align}
$$

### $(\omega, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} = -\omega_{\bar{1}}\wedge e_{\bar{2}} + \omega_{\bar{2}}\wedge e_{\bar{1}} &= -\left(-\frac{b}{2}\mathrm{d}\phi\right)\wedge\left(r\mathrm{d}\phi\right) + \left(0\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right) \\
&= 0,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} = -\omega_{\bar{2}}\wedge e_{\bar{0}} + \omega_{\bar{0}}\wedge e_{\bar{2}} &= -\left(0\right)\wedge\left(\mathrm{d}v\right) + \left(\mathrm{d}\phi\right)\wedge\left(r\mathrm{d}\phi\right) \\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} = -\omega_{\bar{0}}\wedge e_{\bar{1}} + \omega_{\bar{1}}\wedge e_{\bar{0}} &= -\left(\mathrm{d}\phi\right)\wedge\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right) + \left(-\frac{b}{2}\mathrm{d}\phi\right)\wedge\left(\mathrm{d}v\right) \\
&= \left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}v + \mathrm{d}r\right)\wedge\mathrm{d}\phi.
\end{align}
$$

### $(\omega, \omega)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \omega_{\bar{c}} = -2\omega_{\bar{1}}\wedge \omega_{\bar{2}} &= -2\left(-\frac{b}{2}\mathrm{d}\phi\right)\wedge \left(0\right)\\
&= 0,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \omega_{\bar{c}} = -2\omega_{\bar{2}}\wedge \omega_{\bar{0}} &= -2\left(0\right)\wedge \left(\mathrm{d}\phi\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \omega_{\bar{c}} = -2\omega_{\bar{0}}\wedge \omega_{\bar{1}} &= -2\left(\mathrm{d}\phi\right)\wedge \left(-\frac{b}{2}\mathrm{d}\phi\right)\\
&= 0.
\end{align}
$$

### $(\omega, \kappa)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \kappa_{\bar{c}} = -\omega_{\bar{1}}\wedge \kappa_{\bar{2}} + \omega_{\bar{2}}\wedge \kappa_{\bar{1}} &= -\left(-\frac{b}{2}\mathrm{d}\phi\right)\wedge \left(-\frac{r}{\ell^{2}}\mathrm{d}v\right) + \left(0\right)\wedge \left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right)\\
&= \frac{br}{2\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \kappa_{\bar{c}} = -\omega_{\bar{2}}\wedge \kappa_{\bar{0}} + \omega_{\bar{0}}\wedge \kappa_{\bar{2}} &= -\left(0\right)\wedge \left(0\right) + \left(\mathrm{d}\phi\right)\wedge \left(-\frac{r}{\ell^{2}}\mathrm{d}v\right)\\
&= \frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge \kappa_{\bar{c}} = -\omega_{\bar{0}}\wedge \kappa_{\bar{1}} + \omega_{\bar{1}}\wedge \kappa_{\bar{0}} &= -\left(\mathrm{d}\phi\right)\wedge \left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right) + \left(-\frac{b}{2}\mathrm{d}\phi\right)\wedge \left(0\right)\\
&= \frac{J}{2\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi. 
\end{align}
$$

### $(\kappa, e)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge e_{\bar{c}} = -\kappa_{\bar{1}}\wedge e_{\bar{2}} + \kappa_{\bar{2}}\wedge e_{\bar{1}} &= -\left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right)\wedge \left(r\mathrm{d}\phi\right) + \left(-\frac{r}{\ell^{2}}\mathrm{d}v\right)\wedge \left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right)\\
&= - \frac{r}{\ell^{2}}\mathrm{d}v\wedge \mathrm{d}r,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge e_{\bar{c}} = -\kappa_{\bar{2}}\wedge e_{\bar{0}} + \kappa_{\bar{0}}\wedge e_{\bar{2}} &= -\left(-\frac{r}{\ell^{2}}\mathrm{d}v\right)\wedge \left(\mathrm{d}v\right) + \left(0\right)\wedge \left(r\mathrm{d}\phi\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge e_{\bar{c}} = -\kappa_{\bar{0}}\wedge e_{\bar{1}} + \kappa_{\bar{1}}\wedge e_{\bar{0}} &= -\left(0\right)\wedge \left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right) + \left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right)\wedge \left(\mathrm{d}v\right)\\
&= -\frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}v\wedge \mathrm{d}\phi.
\end{align}
$$

### $(\kappa, \kappa)$
$$
\begin{align}
\epsilon^{\bar{0}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge \kappa_{\bar{c}} = -2\kappa_{\bar{1}}\wedge \kappa_{\bar{2}} &= -2\left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right)\wedge \left(-\frac{r}{\ell^{2}}\mathrm{d}v\right)\\
&= -\frac{r}{\ell^{2}}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}v\wedge \mathrm{d}\phi,\\
\epsilon^{\bar{1}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge \kappa_{\bar{c}} = -2\kappa_{\bar{2}}\wedge \kappa_{\bar{0}} = &= -2\left(-\frac{r}{\ell^{2}}\mathrm{d}v\right)\wedge \left(0\right)\\
&= 0,\\
\epsilon^{\bar{2}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge \kappa_{\bar{c}} = -2\kappa_{\bar{0}}\wedge \kappa_{\bar{1}} = &= -2\left(0\right)\wedge \left(\frac{J}{2\ell^{2}}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi\right)\\
&= 0.
\end{align}
$$

### $R$
$$
\begin{align}
R^{\bar{0}} = \mathrm{d}\omega^{\bar{0}} - \frac{1}{2}\epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\omega_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right) \\
&= 0,\\
R^{\bar{1}} = \mathrm{d}\omega^{\bar{1}} - \frac{1}{2}\epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\omega_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right) \\
&= 0,\\
R^{\bar{2}} = \mathrm{d}\omega^{\bar{2}} - \frac{1}{2}\epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\omega_{\bar{c}} &= \left(0\right) - \frac{1}{2}\left(0\right) \\
&= 0. 
\end{align}
$$

### $T$
$$
\begin{align}
T^{\bar{0}} = \mathrm{d}e^{\bar{0}} - \epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r\right) - \left(0\right) \\
&= \frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r,\\
T^{\bar{1}} = \mathrm{d}e^{\bar{1}} - \epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} &= \left(0\right) - \left(0\right) \\
&= 0,\\
T^{\bar{2}} = \mathrm{d}e^{\bar{2}} - \epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge e_{\bar{c}} &= \left(\mathrm{d}r\wedge\mathrm{d}\phi\right) - \left(\left(\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}v + \mathrm{d}r\right)\wedge\mathrm{d}\phi\right) \\
&= -\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}v\wedge\mathrm{d}\phi.
\end{align}
$$

### $F$
$$
\begin{align}
F^{\bar{0}} = \mathrm{d}\kappa^{\bar{0}} - \epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\kappa_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{0}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge\kappa_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\mathrm{d}r\wedge\mathrm{d}\phi\right) - \left(\frac{br}{2\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi\right) + \frac{1}{2}\left(-\frac{r}{\ell^{2}}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}v\wedge \mathrm{d}\phi\right) \\
&= \frac{r}{\ell^{2}}\left(\mathrm{d}r + \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v\right)\wedge\mathrm{d}\phi,\\
F^{\bar{1}} = \mathrm{d}\kappa^{\bar{1}} - \epsilon^{\bar{1}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\kappa_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{1}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge\kappa_{\bar{c}} &= \left(0\right) - \left(\frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi\right) + \frac{1}{2}\left(0\right) \\
&= -\frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi,\\
F^{\bar{2}} = \mathrm{d}\kappa^{\bar{2}} - \epsilon^{\bar{2}\bar{b}\bar{c}}\omega_{\bar{b}}\wedge\kappa_{\bar{c}} + \frac{1}{2}\epsilon^{\bar{2}\bar{b}\bar{c}}\kappa_{\bar{b}}\wedge\kappa_{\bar{c}} &= \left(\frac{1}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r\right) - \left(\frac{J}{2\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi\right) + \frac{1}{2}\left(0\right) \\
&= \frac{1}{\ell^{2}}\mathrm{d}v\wedge\left(\mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right).
\end{align}
$$

### EoM for $R$
$$
\begin{align}
R^{\bar{0}} &= 0,\\
R^{\bar{1}} &= 0,\\
R^{\bar{2}} &= 0.
\end{align}
$$

### EoM for $T$
$$
\begin{align}
T^{\bar{0}} + \epsilon^{\bar{0}\bar{b}\bar{c}} \kappa_{\bar{b}}\wedge e_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}r\right) + \left(- \frac{r}{\ell^{2}}\mathrm{d}v\wedge \mathrm{d}r\right) = 0, \\
T^{\bar{1}} + \epsilon^{\bar{1}\bar{b}\bar{c}} \kappa_{\bar{b}}\wedge e_{\bar{c}} &= \left(0\right) + \left(0\right) = 0, \\
T^{\bar{2}} + \epsilon^{\bar{2}\bar{b}\bar{c}} \kappa_{\bar{b}}\wedge e_{\bar{c}} &= \left(-\frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}} + b\right)\mathrm{d}v\wedge\mathrm{d}\phi\right) + \left(-\frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}v\wedge \mathrm{d}\phi\right) = 0.
\end{align}
$$

### EoM for $F$
$$
\begin{align}
F^{\bar{0}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{0}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} &= \left(\frac{r}{\ell^{2}}\left(\mathrm{d}r + \frac{1}{2}\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v\right)\wedge\mathrm{d}\phi\right) + \frac{1}{2\ell^{2}}\left(-r\left(\left(M - \frac{r^{2}}{\ell^{2}}\right)\mathrm{d}v + 2\mathrm{d}r\right)\wedge\mathrm{d}\phi\right) = 0, \\
F^{\bar{1}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{1}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} &= \left(-\frac{r}{\ell^{2}}\mathrm{d}v\wedge\mathrm{d}\phi\right) + \frac{1}{2\ell^{2}}\left(2r \mathrm{d}v\wedge\mathrm{d}\phi\right) = 0, \\
F^{\bar{2}} + \frac{1}{2\ell^{2}}\epsilon^{\bar{2}\bar{b}\bar{c}}e_{\bar{b}}\wedge e_{\bar{c}} &= \left(\frac{1}{\ell^{2}}\mathrm{d}v\wedge\left(\mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right)\right) + \frac{1}{2\ell^{2}}\left(- \mathrm{d}v\wedge\left( 2\mathrm{d}r - J\mathrm{d}\phi\right)\right) = 0.
\end{align}
$$
