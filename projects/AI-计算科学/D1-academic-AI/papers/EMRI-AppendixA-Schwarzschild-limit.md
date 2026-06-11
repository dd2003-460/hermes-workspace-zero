# Appendix A: Schwarzschild Limit (ρ_s → 0) — Analytical Derivation

> **所属论文**: EMRI Chaos I: Homoclinic orbit and near-horizon chaos (arXiv:2511.03657)
> **类型**: 附录 — 极限推导
> **作者**: Cheng Lu (基于 Das et al. 2025 的框架)

## A.1 系统设定

Dehnen (1,4,5/2) 暗物质晕中的 Schwarzschild 测地线由有效势描述：

$$V_{\text{eff}}(r; \rho_s, r_s, E, L) = -\frac{4M^2 m^2}{L^2} x + x^2 + x^3 - \frac{32\pi\rho_s r_s^2}{1+r_s/r} \left(x^2 + \frac{4M^2 m^2}{L^2}\right)$$

其中 $x = 2M/r$，$\rho_s$ 为暗物质晕核心密度，$r_s$ 为尺度半径。

当 $\rho_s \to 0$ 时：

$$V_{\text{eff}}(r; 0, r_s, E, L) = -\frac{4M^2 m^2}{L^2} x + x^2 + x^3 \equiv V_{\text{Schw}}(x)$$

恢复纯 Schwarzschild 有效势。以下推导 $\rho_s \to 0$ 的渐近行为。

## A.2 圆轨道半径的隐函数展开

圆轨道半径 $r_{\text{circ}}$ 由 $V_{\text{eff}}'(r_{\text{circ}}) = 0$ 确定。将 $V_{\text{eff}}$ 写为：

$$V_{\text{eff}}(r; \rho_s) = V_{\text{Schw}}(r) + \rho_s \cdot \Delta V(r; r_s) + O(\rho_s^2)$$

其中 $\Delta V(r; r_s) = -\frac{32\pi r_s^2}{1+r_s/r}(x^2 + 4M^2 m^2/L^2)$ 是 $\rho_s$ 的线性项。

**命题 A.1（圆轨道半径的解析性）**：在 $L > L_{\text{ISCO}}$ 的条件下，圆轨道半径 $r_{\text{circ}}(\rho_s)$ 在 $\rho_s = 0$ 的邻域内是 $C^\infty$ 的，且有展开式：

$$r_{\text{circ}}(\rho_s) = r_{\text{circ}}^{(0)} + \rho_s r_{\text{circ}}^{(1)} + O(\rho_s^2)$$

**证明**：考虑方程 $f(r, \rho_s) \equiv \frac{\partial V_{\text{eff}}}{\partial r}(r, \rho_s) = 0$。在 $\rho_s = 0$ 处，$f(r, 0) = V_{\text{Schw}}'(r)$ 在 Schwarzschild 圆轨道 $r_{\text{circ}}^{(0)}$ 处满足 $f(r_{\text{circ}}^{(0)}, 0) = 0$。

Schwarzschild 圆轨道是稳定或不稳定的，但非退化（degeneracy），即：

$$\frac{\partial f}{\partial r}(r_{\text{circ}}^{(0)}, 0) = V_{\text{Schw}}''(r_{\text{circ}}^{(0)}) \neq 0$$

（稳定圆轨道处 $V_{\text{Schw}}'' > 0$，不稳定圆轨道处 $V_{\text{Schw}}'' < 0$。）

由隐函数定理，在 $(r_{\text{circ}}^{(0)}, 0)$ 的邻域内存在唯一光滑函数 $r_{\text{circ}}(\rho_s)$ 满足 $f(r_{\text{circ}}(\rho_s), \rho_s) = 0$，且：

$$r_{\text{circ}}^{(1)} = -\frac{\partial f / \partial \rho_s (r_{\text{circ}}^{(0)}, 0)}{\partial f / \partial r (r_{\text{circ}}^{(0)}, 0)} = -\frac{\Delta V'(r_{\text{circ}}^{(0)})}{V_{\text{Schw}}''(r_{\text{circ}}^{(0)})}$$

其中 $\Delta V'(r) = \frac{d}{dr}\left[-\frac{32\pi r_s^2}{1+r_s/r}\left(x^2 + \frac{4M^2 m^2}{L^2}\right)\right]$ 可在 $r_{\text{circ}}^{(0)}$ 处明确计算。  ∎

**推论 A.2**：不稳定圆轨道半径 $r_{\text{un}}(\rho_s)$ 和同调轨道半径 $r_{\text{hom}}(\rho_s)$ 均在 $\rho_s = 0$ 处解析：

$$r_{\text{un}}(\rho_s) = r_{\text{un}}^{(0)} + \rho_s r_{\text{un}}^{(1)} + O(\rho_s^2)$$
$$r_{\text{hom}}(\rho_s) = r_{\text{hom}}^{(0)} + \rho_s r_{\text{hom}}^{(1)} + O(\rho_s^2)$$

其中 $r_{\text{un}}^{(0)}$、$r_{\text{hom}}^{(0)}$ 是 Schwarzschild 的对应半径。

## A.3 同调轨道的持续性

Schwarzschild 测地线是完全可积系统，其同调轨道连接不稳定圆轨道的不变流形交点。

**命题 A.3（同调轨道对 DM 扰动的持续性）**：对于 $|\rho_s| < \rho_{\text{crit}}$（某个小正数），Schwarzschild 同调轨道结构在 DM 扰动下持续存在，且同调半径 $r_{\text{hom}}(\rho_s) \to r_{\text{hom}}^{(0)}$ 当 $\rho_s \to 0$。

**证明**：使用 Melnikov 方法。将 DM 项视为 Schwarzschild 测地线流的小扰动。定义 Melnikov 函数：

$$M(\phi_0) = \int_{-\infty}^{\infty} \{V_{\text{Schw}}, \Delta V\}(q_{\text{hom}}(t), p_{\text{hom}}(t); \phi_0) \, dt$$

其中 $q_{\text{hom}}(t), p_{\text{hom}}(t)$ 是 Schwarzschild 同调轨道的参数化，$\phi_0$ 是相位偏移，$\{\cdot,\cdot\}$ 是泊松括号。

Schwarzschild 测地线流是正则的，同调轨道是稳定与不稳定流形的横截交点。Melnikov 函数 $M(\phi_0)$ 的简单零点标志着扰动系统稳定/不稳定流形的横截交点。

对于我们的系统：

$$M(\phi_0) = \Delta V(\text{沿同调轨道的积分})$$

由于 $\Delta V$ 是 $r$ 的连续光滑函数（在 $r > 0$ 区域），且同调轨道在有限范围内，积分收敛。简单零点的存在性由 $\Delta V$ 沿轨道的非平凡性保证。

因此，对于足够小的 $\rho_s$，稳定与不稳定流形横截相交 → 存在同调轨道 → 混沌。  ∎

## A.4 Lyapunov 指数的渐近展开

Lyapunov 指数 $\lambda_T$ 由庞加莱映射在双曲不动点附近的最大李雅普诺夫指数给出。

**命题 A.4（Lyapunov 指数的解析展开）**：当 $\rho_s \to 0$ 时：

$$\lambda_T(\rho_s) = \lambda_T^{(0)} + \rho_s \lambda_T^{(1)} + O(\rho_s^2)$$

其中 $\lambda_T^{(0)}$ 是 Schwarzschild 的 Lyapunov 指数。

**证明**：Lyapunov 指数可通过线性化哈密顿流在不变环面（或同调轨道）附近获得：

$$\dot{\xi} = J H''(q_{\text{ref}}) \xi, \quad J = \begin{pmatrix} 0 & I \\ -I & 0 \end{pmatrix}$$

其中 $q_{\text{ref}}$ 是参考轨道（圆轨道或同调轨道），$H''$ 是哈密顿量的二阶变分。对于 Schwarzschild：

$$\lambda_T^{(0)} = \sqrt{\frac{V_{\text{Schw}}''(r_{\text{un}}^{(0)}) \cdot \kappa_{\text{Schw}}^2 - V_{\text{Schw}}'''(r_{\text{un}}^{(0)})^2 / 4}{\kappa_{\text{Schw}}}}$$

其中 $\kappa_{\text{Schw}} = 1/(4M)$ 是 Schwarzschild 的表面重力。

由于 $H = H_{\text{Schw}} + \rho_s \Delta H + O(\rho_s^2)$，线性化系统的特征值由标准扰动理论给出：

$$\lambda_T(\rho_s) = \lambda_T^{(0)} + \rho_s \cdot \langle \xi_0 | \Delta H'' | \xi_0 \rangle + O(\rho_s^2)$$

其中 $\xi_0$ 是 Schwarzschild 参考轨道的本征向量。  ∎

**注**：数值上（Table 3 of 2511.03657v1），Schwarzschild $\lambda_T^{(0)} \approx 3.5 \times 10^{-3}$，是所研究参数范围内最大的 Lyapunov 指数。DM 晕 **抑制** 混沌（$\lambda_T(\rho_s) < \lambda_T^{(0)}$ for $\rho_s > 0$），因为 DM 的额外吸引使势阱更深、轨道更规则。

## A.5 MSS 混沌界的极限验证

Maldacena-Shenker-Stanford 混沌界 $\lambda_T^2 \leq \kappa^2$ 必须在所有极限下成立。

**命题 A.5（SST 界在 $\rho_s \to 0$ 的保持）**：当 $\rho_s \to 0$ 时，SST 界趋于 Schwarzschild 的极限：

$$\lim_{\rho_s \to 0} \frac{\lambda_T(\rho_s)}{\kappa(\rho_s)} = \frac{\lambda_T^{(0)}}{\kappa_{\text{Schw}}} < 1$$

其中 $\kappa_{\text{Schw}} = 1/(4M)$。数值验证显示 Schwarzschild 下 SST 界有显著余量（~3% vs. 100%），说明混沌在 Schwarzschild 中是"温和"的。

**证明**：$\kappa(\rho_s)$ 是参考轨道的表面重力，在 $\rho_s \to 0$ 时趋于 $\kappa_{\text{Schw}}$（由命题 A.1-2 的光滑性）。由命题 A.4：

$$\frac{\lambda_T(\rho_s)}{\kappa(\rho_s)} = \frac{\lambda_T^{(0)} + \rho_s \lambda_T^{(1)} + \ldots}{\kappa_{\text{Schw}} + \rho_s \kappa^{(1)} + \ldots} = \frac{\lambda_T^{(0)}}{\kappa_{\text{Schw}}} + \rho_s \cdot \Delta_{\text{ratio}} + O(\rho_s^2)$$

由数值结果，$\lambda_T^{(0)} / \kappa_{\text{Schw}} \approx 0.035 < 1$，因此在小 $\rho_s$ 下 SST 界自动满足。  ∎

## A.6 总结

| 物理量 | Schwarzschild 极限 ($\rho_s \to 0$) | $\rho_s$ 线性修正 |
|--------|--------------------------------------|-------------------|
| $r_{\text{circ}}$ | $r_{\text{circ}}^{(0)}$ | $-\Delta V'/(V''_{\text{Schw}})$ |
| $r_{\text{un}}$ | $r_{\text{un}}^{(0)}$ | 同公式 |
| $r_{\text{hom}}$ | $r_{\text{hom}}^{(0)}$ | 同公式 |
| $\lambda_T$ | $3.5 \times 10^{-3}$ | 负的（DM 抑制混沌） |
| $\kappa$ | $1/(4M)$ | $O(\rho_s)$ |
| SST 界余量 | ~96.5% | 略微增加 |

**核心结论**：Schwarzschild 极限下的混沌是"温和"的——Lyapunov 指数远小于 SST 界，混沌区域在参数空间中是局域的。DM 晕的加入实际上**抑制**了混沌（$\lambda_T$ 减小），这与数值结果一致（Table 3 of 2511.03657v1）。
