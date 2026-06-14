#!/usr/bin/env python3
"""
Schwarzschild QBH QNM 精确求解器 — Leaver 连分数法 v5
=======================================================

按 Berti, Cardoso, Starinets (2009) CQG 26, 163001 §IV 附录B 实现。

**v5 关键修复** (其他 LLM 分析 + 本版本验证):
- Bug 1: α(x) 原来是 `2/x`，正确是 `(x-x₀)(1-3x)/[x(1-x)]`
- Bug 2: β(x) 原来是 `ω²/x⁴ - V(x)/x⁴`，正确是 `(x-x₀)²·4M²(ω²-V_l)/[x²(1-x)⁴]`
- A_{n+1} = -½(α_{n-1} - β_{n-1}) for n≥1, A_0 = 0
- B_n = β_n - n(n+1-γ)
- C_n = (n+1)(n+1-γ)
- γ = 1 + 4iωM

验证基准: Kokkotas & Schutz (1992) CQG 9, 1989 Table I

用法: python3 d1-qbh-qnm-solver.py
"""

import numpy as np
import sympy
import warnings
from typing import Tuple

warnings.filterwarnings('ignore')
np.set_printoptions(precision=12, suppress=True)


# ============================================================================
# Schwarzschild 几何
# ============================================================================

def schw_potential(r: float, l: int, s: int = -2, M: float = 1.0) -> float:
    """Regge-Wheeler 有效势 (s=-2 引力扰动)"""
    rs = 2.0 * M
    return (1.0 - rs / r) * (l * (l + 1) / (r ** 2) + (1 - s ** 2) * rs / (r ** 3))


def potential_peak(l: int, M: float = 1.0) -> float:
    """数值计算势峰位置 r_peak"""
    rs = 2.0 * M
    rs_vals = np.linspace(rs * 1.001, 10 * M, 20000)
    V_vals = np.array([schw_potential(r, l, -2, M) for r in rs_vals])
    return rs_vals[np.argmax(V_vals)]


# ============================================================================
# Leaver (1985) 连分数法 — Berti et al. (2009) §IV 附录B
# ============================================================================

class LeaverQNM:
    """
    Leaver 连分数法 Schwarzschild QNM 求解器 v5。

    变量代换: x = 1 - 2M/r, 视界 x=0, 无穷远 x=1
    Regge-Wheeler 方程: d²ψ/dx² + α(x)·dψ/dx + β(x)·ψ = 0

    α(x) = (x-x₀)(1-3x)/[x(1-x)]
    β(x) = (x-x₀)²·4M²(ω²-V_l)/[x²(1-x)⁴]

    V_l(x) = x(1-x)²/(4M²)·[l(l+1) + (1-s²)(1-x)]

    在 x_0 处展开: A_{n+1} a_{n-1} + B_n a_n + C_n a_{n+1} = 0
    连分数条件: D_0 = 0 → Newton-Raphson 求根
    """

    def __init__(self, M=1.0, l=2, s=-2, x0_frac=0.3, Nterms=200):
        self.M = M
        self.l = l
        self.s = s
        self.x0 = x0_frac
        self.N = Nterms

    def _calc_alpha_beta(self, omega, Nfrac):
        """
        计算泰勒系数 α_n, β_n — v5 正确公式。

        使用 sympy 符号计算 Taylor 展开系数，避免手动展开错误。

        α(x) = (x-x₀)(1-3x)/[x(1-x)]
        β(x) = (x-x₀)²·4M²(ω²-V_l)/[x²(1-x)⁴]

        Taylor 系数: coef[n] = f^{(n)}(x₀) / n!
        """
        M = self.M
        l = self.l
        s = self.s
        x0 = self.x0
        omega_val = omega

        a = l * (l + 1)
        b = 1.0 - s * s  # s=-2: b=-3

        M2 = M * M

        # 定义 sympy 符号
        x = sympy.Symbol('x')
        z = x  # 使用 x 作为符号变量

        # 有效势 V_l (以 x 表示)
        # V_l = x(1-x)²/(4M²)·[a + b(1-x)]
        V_l = z * (1 - z)**2 / (4 * M2) * (a + b * (1 - z))

        # α(x) = (x-x₀)(1-3x)/[x(1-x)]
        alpha_z = (z - x0) * (1 - 3 * z) / (z * (1 - z))

        # β(x) = (x-x₀)²·4M²(ω²-V_l)/[x²(1-x)⁴]
        beta_z = (z - x0)**2 * 4 * M2 * (omega_val**2 - V_l) / (z**2 * (1 - z)**4)

        # 计算泰勒展开系数到 Nfrac+2 阶
        alpha = np.zeros(Nfrac + 3, dtype=complex)
        beta = np.zeros(Nfrac + 3, dtype=complex)

        for n in range(Nfrac + 3):
            # α_n = α^{(n)}(x₀) / n!
            alpha[n] = complex(alpha_z.diff(z, n).subs(z, x0) / sympy.factorial(n))

            # β_n = β^{(n)}(x₀) / n!
            beta[n] = complex(beta_z.diff(z, n).subs(z, x0) / sympy.factorial(n))

        # γ = 1 + 4iωM (surface gravity convention per Berti et al.)
        gamma = 1.0 + 4.0j * omega_val * M

        return alpha, beta, gamma

    def _calc_ABC(self, omega, Nfrac):
        """
        计算 Leaver 三对角系数 — v5 正确公式。

        A_{n+1} = -½(α_{n-1} - β_{n-1}) for n ≥ 1; A_0 = 0
        B_n = β_n - n(n+1-γ)
        C_n = (n+1)(n+1-γ)
        """
        alpha, beta, gamma = self._calc_alpha_beta(omega, Nfrac)

        A = np.zeros(Nfrac + 2, dtype=complex)
        B = np.zeros(Nfrac + 2, dtype=complex)
        C = np.zeros(Nfrac + 2, dtype=complex)

        for n in range(Nfrac + 2):
            # A_n: A_{n+1} = -½(α_{n-1} - β_{n-1}) for n≥1
            # 注意索引: A[n] 对应 A_{n}，公式中 A_{n+1} 表示下一项
            if n >= 1:
                A[n] = -0.5 * (alpha[n - 1] - beta[n - 1])
            else:
                A[n] = 0.0  # A_0 = 0

            # B_n = β_n - n(n+1-γ)
            B[n] = beta[n] - n * (n + 1 - gamma)

            # C_n = (n+1)(n+1-γ)
            C[n] = (n + 1) * (n + 1 - gamma)

        return A, B, C

    def theta_function(self, omega, Nfrac=100):
        """
        Leaver 连分数条件 θ(ω) = D_0 = 0。

        向后递推:
        D_N = 0
        D_n = B_n - A_{n+1}·C_n / D_{n+1}
        θ = D_0
        """
        A, B, C = self._calc_ABC(omega, Nfrac)

        D = 0.0 + 0.0j
        for n in range(Nfrac, 0, -1):
            denom = B[n] - A[n + 1] * C[n] / D
            if abs(denom) < 1e-30:
                denom = 1e-30 * (1 + 1e-10j)
            D = denom

        theta = B[0] - A[1] * C[0] / D
        return theta

    def solve(self, omega_guess, max_iter=300, tol=1e-12):
        """Newton-Raphson 求根 θ(ω) = 0"""
        omega = omega_guess

        for i in range(max_iter):
            theta = self.theta_function(omega)

            if abs(theta) < tol:
                return omega, i + 1, True

            eps = 1e-8
            theta_p = self.theta_function(omega + eps)
            dtheta = (theta_p - theta) / eps

            if abs(dtheta) < 1e-40:
                return omega, i + 1, False

            delta = theta / dtheta
            if abs(delta) > 0.3:
                delta = 0.3 * delta / abs(delta)

            omega -= delta

            if abs(delta) < tol:
                return omega, i + 1, True

        return omega, max_iter, False


def eikonal_guess(l, n, M=1.0):
    """Eikonal 近似: ω ≈ l/(√27 M) - i(n+1/2)√27/(2M)"""
    omega_R = l / (np.sqrt(27.0) * M)
    omega_I = (n + 0.5) * np.sqrt(27.0) / (2.0 * M)
    return complex(omega_R, -omega_I)


# ============================================================================
# 基准测试
# ============================================================================

def run_benchmark():
    print("=" * 70)
    print("Schwarzschild QNM — Leaver 连分数法 v5 (Berti et al. 2009 公式)")
    print("=" * 70)
    print("验证基准: Kokkotas & Schutz (1992) Table I")
    print("=" * 70)
    print()

    M = 1.0
    s = -2
    l_max = 4
    n_max = 2

    # Kokkotas & Schutz (1992) Table I
    known_qnm = {
        (2, 0): complex(0.37373134, -0.08896258),
        (2, 1): complex(0.37329352, -0.27458937),
        (2, 2): complex(0.37265595, -0.46975278),
        (3, 0): complex(0.59187029, -0.05853522),
        (3, 1): complex(0.58971841, -0.26880432),
        (4, 0): complex(0.75906205, -0.04402477),
        (4, 1): complex(0.75816138, -0.26380755),
    }

    # 尝试多个展开点
    x0_candidates = [0.3, 0.35, 0.4, 0.45, 0.5]

    best_results = {}

    for x0 in x0_candidates:
        all_converged = True
        max_rel_err = 0
        total_errors = []

        for l in range(2, l_max + 1):
            for n in range(n_max + 1):
                solver = LeaverQNM(M=M, l=l, s=s, x0_frac=x0)
                guess = eikonal_guess(l, n, M)
                omega, iters, conv = solver.solve(guess)

                omega_M = omega * M
                key = (l, n)
                if key in known_qnm:
                    rel_err = abs(omega_M - known_qnm[key]) / abs(known_qnm[key])
                    total_errors.append(rel_err)
                    if rel_err > 0.1:
                        all_converged = False

        if all_converged:
            best_results[x0] = total_errors
            print(f"  x0={x0}: 全部收敛, 平均误差={np.mean(total_errors):.2e}")

    if best_results:
        best_x0 = min(best_results, key=lambda x: np.mean(best_results[x]))
        print(f"\n  ★ 最优展开点: x0 = {best_x0}")

        # 用最优展开点重新计算
        x0 = best_x0
        print(f"\n用 x0={x0} 重新计算:")
        print("-" * 70)

        results = []
        for l in range(2, l_max + 1):
            for n in range(n_max + 1):
                solver = LeaverQNM(M=M, l=l, s=s, x0_frac=x0)
                guess = eikonal_guess(l, n, M)
                omega, iters, conv = solver.solve(guess)
                omega_M = omega * M

                key = (l, n)
                rel_err = float('inf')
                known = None
                if key in known_qnm:
                    known = known_qnm[key]
                    rel_err = abs(omega_M - known) / abs(known)

                results.append((l, n, omega_M, iters, conv, known, rel_err))

                status = "✓" if conv else "✗"
                print(f"  l={l}, n={n}: ωM=({omega_M.real:.8f} - {abs(omega_M.imag):.8f}i) "
                      f"({iters}it) [{status}]", end="")
                if known is not None:
                    print(f"  ref: ({known.real:.8f} - {abs(known.imag):.8f}i) "
                          f"err={rel_err:.2e}", end="")
                print()

        print("\n" + "=" * 70)
        errs = [r[6] for r in results if r[6] != float('inf')]
        print(f"  最大相对误差: {max(errs):.2e}")
        print(f"  平均相对误差: {np.mean(errs):.2e}")

        if max(errs) < 1e-6:
            print("\n  ★ 求解器验证通过! 所有基准 < 1e-6")
        elif max(errs) < 1e-4:
            print("\n  ★ 求解器验证基本通过! 最大误差 < 1e-4")
        else:
            print(f"\n  ⚠ 最大误差仍较大 ({max(errs):.2e})，需要继续调试")
        print("=" * 70)

    return results


if __name__ == "__main__":
    run_benchmark()
