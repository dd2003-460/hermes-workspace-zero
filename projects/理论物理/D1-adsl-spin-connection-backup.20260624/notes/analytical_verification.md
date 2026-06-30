# AdSL 引力 BTZ 黑洞 Spin Connection 解析验证

> Reference: JHEP09(2023)185  
> Created: 2026-03-31T22:24+08:00  
> Status: planning

## 1. 背景与目标

验证 AdSL 引力理论中 BTZ 黑洞解的 spin connection 在入射/出射 Eddington-Finkelstein 坐标系下的正确性。

### 运动方程（需验证）

从 Chern-Simons 作用量对 $\omega^a, e^a, \sigma^a$ 变分，要求系数矩阵退化，得到：

$$
\begin{align}
R_a &= 0 \quad \text{(几何曲率为零)} \\
T_a + \epsilon_{abc}\sigma^b \wedge e^c &= 0 \quad \text{(修正挠率)} \\
F_a + \frac{1}{2\ell^2}\epsilon_{abc}e^b \wedge e^c &= 0 \quad \text{(σ曲率)}
\end{align}
$$

其中 $\sigma^a = -\kappa^a$（contortion 的负值）。

## 2. 代数与约定

### AdSL 代数生成元对易关系

$$
[J_a, J_b] = \epsilon_{abc}J^c, \quad [J_a, P_b] = \epsilon_{abc}P^c, \quad [J_a, Z_b] = \epsilon_{abc}Z^c
$$
$$
[Z_a, Z_b] = \epsilon_{abc}Z^c, \quad [P_a, P_b] = \epsilon_{abc}Z^c, \quad [Z_a, P_b] = \epsilon_{abc}P^c
$$

### Minkowski 度规

非对角形式（入射/出射 EF 坐标系）：
$$
(\eta_{\bar{a}\bar{b}}) = \begin{pmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{pmatrix}
$$

指标升降规则：
- $e_{\bar{0}} = \eta_{\bar{0}\bar{1}}e^{\bar{1}} = e^{\bar{1}}$
- $e_{\bar{1}} = \eta_{\bar{1}\bar{0}}e^{\bar{0}} = e^{\bar{0}}$
- $e_{\bar{2}} = \eta_{\bar{2}\bar{2}}e^{\bar{2}} = e^{\bar{2}}$

### BTZ 参数

$$
f(r) = \frac{r^2}{\ell^2} - M + \frac{J^2}{4r^2}, \quad N_\varphi(r) = -\frac{J}{2r^2}
$$

视界：
$$
r_\pm^2 = \frac{M\ell^2 \pm \ell\sqrt{M^2\ell^2 - J^2}}{2}
$$

## 3. 入射 EF 坐标系验证

### 3.1 标架场

坐标：$(v, r, \phi)$

$$
e^{\bar{0}} = \frac{1}{2\ell^2}(\ell^2 M - r^2)\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi
$$
$$
e^{\bar{1}} = \mathrm{d}v, \quad e^{\bar{2}} = r\,\mathrm{d}\phi
$$

**验证 3.1a: 线元重构**

$$
\mathrm{d}s^2 = 2e^{\bar{0}} \otimes e^{\bar{1}} + e^{\bar{2}} \otimes e^{\bar{2}}
$$

展开：
$$
= 2\left[\frac{(\ell^2 M - r^2)}{2\ell^2}\mathrm{d}v + \mathrm{d}r - \frac{J}{2}\mathrm{d}\phi\right]\mathrm{d}v + r^2\mathrm{d}\phi^2
$$
$$
= \frac{(\ell^2 M - r^2)}{\ell^2}\mathrm{d}v^2 + 2\mathrm{d}v\,\mathrm{d}r - J\,\mathrm{d}v\,\mathrm{d}\phi + r^2\mathrm{d}\phi^2
$$

这应等于入射 EF 度规：
$$
\mathrm{d}s^2 = (r^2 N_\varphi^2 - f)\mathrm{d}v^2 + 2\mathrm{d}v\,\mathrm{d}r + 2r^2 N_\varphi\,\mathrm{d}v\,\mathrm{d}\phi + r^2\mathrm{d}\phi^2
$$

检查系数：
- $\mathrm{d}v^2$: $\frac{\ell^2 M - r^2}{\ell^2} = M - \frac{r^2}{\ell^2}$
  而 $r^2 N_\varphi^2 - f = r^2 \cdot \frac{J^2}{4r^4} - f = \frac{J^2}{4r^2} - \frac{r^2}{\ell^2} + M - \frac{J^2}{4r^2} = M - \frac{r^2}{\ell^2}$ ✓
- $\mathrm{d}v\,\mathrm{d}r$: $2$ ✓
- $\mathrm{d}v\,\mathrm{d}\phi$: $-J$ vs $2r^2 N_\varphi = 2r^2 \cdot \left(-\frac{J}{2r^2}\right) = -J$ ✓
- $\mathrm{d}\phi^2$: $r^2$ ✓

**结论**: 标架重构度规正确。

### 3.2 自旋联络

$$
\omega^{\bar{0}} = -\frac{b}{2}\mathrm{d}\phi, \quad \omega^{\bar{1}} = \mathrm{d}\phi, \quad \omega^{\bar{2}} = 0
$$

### 3.3 Contortion

$$
\kappa^{\bar{0}} = \frac{J}{2\ell^2}\mathrm{d}v + \frac{1}{2}\left(\frac{r^2}{\ell^2} - M - b\right)\mathrm{d}\phi
$$
$$
\kappa^{\bar{1}} = 0, \quad \kappa^{\bar{2}} = -\frac{r}{\ell^2}\mathrm{d}v
$$

### 3.4 几何曲率 $R_a = 0$

对偶曲率 2-形式：
$$
R^a = \mathrm{d}\omega^a - \frac{1}{2}\epsilon^{abc}\omega_b \wedge \omega_c
$$

逐分量计算：

**$R^{\bar{0}}$:**
$$
R^{\bar{0}} = \mathrm{d}\omega^{\bar{0}} - \frac{1}{2}\epsilon^{\bar{0}\bar{b}\bar{c}}\omega_{\bar{b}} \wedge \omega_{\bar{c}}
$$

$\omega^{\bar{0}} = -\frac{b}{2}\mathrm{d}\phi$，所以 $\mathrm{d}\omega^{\bar{0}} = 0$（$b$ 是常数，$\mathrm{d}(\mathrm{d}\phi) = 0$）。

需要降指标：$\omega_{\bar{0}} = \omega^{\bar{1}} = \mathrm{d}\phi$，$\omega_{\bar{1}} = \omega^{\bar{0}} = -\frac{b}{2}\mathrm{d}\phi$，$\omega_{\bar{2}} = \omega^{\bar{2}} = 0$。

$\epsilon^{\bar{0}\bar{b}\bar{c}}$ 非零项：
- $\epsilon^{\bar{0}\bar{1}\bar{2}} = \epsilon^{012} = -1$（因为 $\epsilon_{012} = 1$，但 $\epsilon^{012} = -\det(\eta)^{-1} = -1$... 需要仔细处理非对角度规的升降）

⚠️ **注意**: 使用非对角 Minkowski 度规时，Levi-Civita 符号的升降需要谨慎。需用 $\epsilon^{\bar{a}\bar{b}\bar{c}} = -\epsilon_{\bar{a}\bar{b}\bar{c}}$（因为 $\det(\eta) = -1$ 对于此非对角形式）。

待 SymPy 验证。

### 3.5 修正挠率 $T_a + \epsilon_{abc}\sigma^b \wedge e^c = 0$

对偶挠率：
$$
T^a = \mathrm{D}_\omega e^a = \mathrm{d}e^a - \epsilon^{abc}\omega_b \wedge e_c
$$

且 $\sigma^a = -\kappa^a$，所以需验证：
$$
T^a - \epsilon^{abc}\kappa_b \wedge e_c = 0
$$

展开待计算。

### 3.6 σ曲率 $F_a + \frac{1}{2\ell^2}\epsilon_{abc}e^b \wedge e^c = 0$

$$
F^a = \mathrm{D}_\omega \sigma^a + \frac{1}{2}\epsilon^{abc}\sigma_b \wedge \sigma_c
$$

代入 $\sigma^a = -\kappa^a$，需验证：
$$
\mathrm{D}_\omega(-\kappa^a) + \frac{1}{2}\epsilon^{abc}(-\kappa_b) \wedge (-\kappa_c) + \frac{1}{2\ell^2}\epsilon^{abc}e_b \wedge e_c = 0
$$

展开待计算。

## 4. 出射 EF 坐标系验证

结构与入射 EF 完全平行，只需替换：
- $v \to u$（outgoing time）
- $\phi \to \hat{\phi}$
- $\mathrm{d}r$ 的符号在 $e^{\bar{0}}$ 中取反

标架：
$$
\hat{e}^{\bar{0}} = \frac{1}{2\ell^2}(\ell^2 M - r^2)\mathrm{d}u - \mathrm{d}r - \frac{J}{2}\mathrm{d}\hat{\phi}
$$
$$
\hat{e}^{\bar{1}} = \mathrm{d}u, \quad \hat{e}^{\bar{2}} = r\,\mathrm{d}\hat{\phi}
$$

自旋联络同形：
$$
\hat{\omega}^{\bar{0}} = -\frac{b}{2}\mathrm{d}\hat{\phi}, \quad \hat{\omega}^{\bar{1}} = \mathrm{d}\hat{\phi}, \quad \hat{\omega}^{\bar{2}} = 0
$$

验证步骤同 §3，仅替换坐标和符号。

## 5. SymPy 验证脚本设计

由于本机无 Mathematica，使用 SymPy 实现：

```python
# 符号定义
r, ell, M, J, b = symbols('r ell M J b', real=True)
v, u, phi, phi_hat = symbols('v u phi phi_hat')

# 1-形式基
dv, dr, dphi = Function('dv'), Function('dr'), Function('dphi')
# 外微分 & wedge product 需要自定义实现
```

**挑战**: SymPy 没有原生微分形式 wedge product 支持。需要：
1. 用 SymPy 的 `diffgeom` 模块，或
2. 手动实现 2D/3D 微分形式代数（形式为 $f(r)\mathrm{d}x^i \wedge \mathrm{d}x^j$）

推荐方案 2，因为 2+1 维度下微分形式只有有限基底。

## 6. 验证检查清单

| # | 检查项 | 方法 | 状态 |
|---|--------|------|------|
| 1 | 入射标架重构度规 | 手动 | ✅ 已验证 |
| 2 | 入射 $R_a = 0$ | SymPy | ⬜ |
| 3 | 入射 $T_a + \epsilon\sigma e = 0$ | SymPy | ⬜ |
| 4 | 入射 $F_a + \frac{1}{2\ell^2}\epsilon ee = 0$ | SymPy | ⬜ |
| 5 | 出射标架重构度规 | 手动 | ⬜ |
| 6 | 出射 $R_a = 0$ | SymPy | ⬜ |
| 7 | 出射 $T_a + \epsilon\sigma e = 0$ | SymPy | ⬜ |
| 8 | 出射 $F_a + \frac{1}{2\ell^2}\epsilon ee = 0$ | SymPy | ⬜ |
| 9 | $b$ 参数独立性（自由参数不影响 EOM） | SymPy | ⬜ |

## 7. 等待下一步

- SymPy 验证脚本编写与执行
- 所有检查项完成
- 输出最终验证报告
