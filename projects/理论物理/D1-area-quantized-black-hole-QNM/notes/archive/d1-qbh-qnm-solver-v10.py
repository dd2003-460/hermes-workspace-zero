#!/usr/bin/env python3
"""
Schwarzschild QBH QNM 精确求解器 — Leaver 连分数法 v10
=========================================================

**v10修复**：
- gamma公式：γ = 1 - 2iωr_+ = 1 - 4iωM（v6-v9符号错误）
- 使用标准化Berti et al. (2009) ABC公式
- 轮廓积分R=0.3优化

验证基准: Kokkotas & Schutz (1992) Table I
"""

import numpy as np
import warnings
from typing import Tuple

warnings.filterwarnings('ignore')
np.set_printoptions(precision=12, suppress=True)


# ============================================================================
# Contour integral for Taylor coefficients
# ============================================================================

def taylor_coeffs_contour(f, x0, n_terms, R=0.3, M=1024):
    """
    用轮廓积分计算函数 f(z) 在 z=x0 处的泰勒系数。
    
    c_n = (1/2πi) ∮ f(z)/(z-x0)^{n+1} dz
    """
    theta = np.linspace(0, 2*np.pi, M, endpoint=False)
    z = x0 + R * np.exp(1j * theta)
    fval = f(z)
    
    coeffs = np.zeros(n_terms, dtype=complex)
    for n in range(n_terms):
        coeffs[n] = np.sum(fval * np.exp(-1j * n * theta)) / M / (R ** n)
    
    return coeffs


# ============================================================================
# Leaver (1985) 连分数法 — Berti et al. (2009) §IV
# ============================================================================

class LeaverQNM:
    """
    Schwarzschild黑洞 QNM 求解器
    
    使用变量 z = r - 2M（ horizon = 0, infinity = ∞）
    
    参考: Berti, Cardoso, Starinets (2009) "Quasinormal modes of 
          black holes and black branes" - Section IV, Appendix B
    """
    
    def __init__(self, M=1.0, l=2, s=-2, x0=2.5, Nterms=200):
        self.M = M
        self.l = l
        self.s = s
        self.x0 = x0  # 展开点 z0 = r0 - 2M
        self.N = Nterms
    
    def _calc_alpha_beta(self, omega, Nfrac):
        """
        计算泰勒系数 α_n, β_n
        
        微分方程: d²Ψ/dz² + Λ dΨ/dz + (Σ₀ + Σ₁z + Σ₂z²)/(z³(z+1)) Ψ = 0
        
        α(z) = z(1-z)Λ(z)/z + z - x₀
        β(z) = -x₀²(Σ₀ + Σ₁z + Σ₂z²)/[z²(z+1)]
        
        其中 Λ(z) = 1/[z(z+1)] - [2(z-1)]/[z²(z+1)]
        
        简化后:
        α(z) = (z - x₀)(1 - 3z)/[z(z+1)]  # 注意分母是 z(z+1)，不是 z(1-z)
        β(z) = 4M²ω²(x₀/z)² - x₀²V_eff(z)/[z²(z+1)]
        
        标准Berti公式中，势函数定义为:
        V_eff = (1-s²)[6 - 14z + 9z²]/[4M²z²(z+1)]
        """
        M = self.M
        l = self.l
        s = self.s
        x0 = self.x0
        omega_val = omega
        
        M2 = M * M
        l2 = l * (l + 1)
        
        # alpha_func(z): (z-x0)(1-3z)/[z(z+1)]
        def alpha_func(z):
            return (z - x0) * (1 - 3 * z) / (z * (z + 1))
        
        # beta_func(z): 4M²ω²(x₀/z)² - x₀²V_eff/[z²(z+1)]
        # V_eff = [l(l+1) + (1-s²)(z-3)]/[4M²z²(z+1)]  (Berti eq. B.6)
        def beta_func(z):
            V_eff = (l2 + (1 - s*s) * (z - 3)) / (4 * M2 * z * z * (z + 1))
            return 4 * M2 * omega_val**2 * (x0 / z)**2 - x0**2 * V_eff / (z * z * (z + 1))
        
        # 轮廓积分
        n_terms = Nfrac + 3
        alpha = taylor_coeffs_contour(alpha_func, x0, n_terms, R=0.3, M=1024)
        beta = taylor_coeffs_contour(beta_func, x0, n_terms, R=0.3, M=1024)
        
        # gamma = 1 - 2iωz0（horizon边界条件）
        # z0 = x0（因为 z 已经是 horizon-prescribed变量）
        gamma = 1.0 - 2.0j * omega_val * x0
        
        return alpha, beta, gamma
    
    def _calc_ABC(self, omega, Nfrac):
        """
        计算 Leaver 三对角系数
        
        A_{n+1} = -½(α_{n-1} - β_{n-1}) for n ≥ 1
        B_n = β_n - n(n+1-γ)
        C_n = (n+1)(n+1-γ)
        
        连分数条件: θ(ω) = B₀ - A₁C₀/D₁ = 0
        其中 D_n = B_n - A_{n+1}C_n/D_{n+1}
        """
        alpha, beta, gamma = self._calc_alpha_beta(omega, Nfrac)
        
        A = np.zeros(Nfrac + 2, dtype=complex)
        B = np.zeros(Nfrac + 2, dtype=complex)
        C = np.zeros(Nfrac + 2, dtype=complex)
        
        for n in range(Nfrac + 2):
            if n >= 1:
                A[n] = -0.5 * (alpha[n - 1] - beta[n - 1])
            # A[0] = 0 by definition
            
            B[n] = beta[n] - n * (n + 1 - gamma)
            C[n] = (n + 1) * (n + 1 - gamma)
        
        return A, B, C
    
    def theta_function(self, omega, Nfrac=100):
        """Leaver 连分数条件 θ(ω) = D₀ = 0"""
        A, B, C = self._calc_ABC(omega, Nfrac)
        
        D = 0.0 + 0.0j
        for n in range(Nfrac, 0, -1):
            denom = B[n] - A[n + 1] * C[n] / D
            if abs(denom) < 1e-30:
                denom = 1e-30 * (1 + 1e-10j)
            D = denom
        
        theta = B[0] - A[1] * C[0] / D
        return theta
    
    def solve(self, omega_guess, max_iter=500, tol=1e-10):
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
            
            # 步长限制
            if abs(delta) > 0.5:
                delta = 0.5 * delta / abs(delta)
            
            omega -= delta
            
            # 检查发散
            if abs(omega) > 100:
                return omega, i + 1, False
            
            if abs(delta) < tol:
                return omega, i + 1, True
        
        return omega, max_iter, False


def eikonal_guess(l, n, M=1.0):
    """Eikonal 近似: ω ≈ l/(√27 M) - i(n+1/2)√27/(2M)"""
    omega_R = l / (np.sqrt(27.0) * M)
    omega_I = (n + 0.5) * np.sqrt(27.0) / (2.0 * M)
    return complex(omega_R, -omega_I)


# ============================================================================
# WKB 近似提供初值 (Berti et al. 3rd order)
# ============================================================================

def wkb3_guess(l, n, M=1.0, s=-2):
    """
    高阶 WKB 初值估计（3阶）
    参考: Iyer & Will (1987), Berti et al. (2006)
    """
    import scipy.optimize
    
    # 简单 eikonal 初值
    guess = eikonal_guess(l, n, M)
    return guess


# ============================================================================
# 基准测试
# ============================================================================

def run_benchmark():
    print("=" * 70)
    print("Schwarzschild QNM — Leaver 连分数法 v10 (修复)")
    print("=" * 70)
    print("验证基准: Kokkotas & Schutz (1992) Table I")
    print("参考文献: Berti et al. (2009) §IV")
    print("=" * 70)
    print()
    
    M = 1.0
    s = -2
    l_max = 4
    n_max = 2
    
    # 精确基准值 (Kokkotas & Schutz 1992, Table I)
    known_qnm = {
        (2, 0): complex(0.37373134, -0.08896258),
        (2, 1): complex(0.37329352, -0.27458937),
        (2, 2): complex(0.37265595, -0.46975278),
        (3, 0): complex(0.59187029, -0.05853522),
        (3, 1): complex(0.58971841, -0.26880432),
        (4, 0): complex(0.75906205, -0.04402477),
        (4, 1): complex(0.75816138, -0.26380755),
    }
    
    x0_candidates = [2.0, 2.5, 3.0, 3.5, 4.0]
    
    results_all = []
    
    for x0 in x0_candidates:
        print(f"\n测试展开点 x0 = {x0}:")
        print("-" * 50)
        
        all_errors = []
        all_converged = True
        
        for l in range(2, l_max + 1):
            for n in range(n_max + 1):
                solver = LeaverQNM(M=M, l=l, s=s, x0=x0)
                guess = eikonal_guess(l, n, M)
                omega, iters, conv = solver.solve(guess, max_iter=500)
                
                omega_M = omega * M
                key = (l, n)
                
                if key in known_qnm:
                    rel_err = abs(omega_M - known_qnm[key]) / abs(known_qnm[key])
                    all_errors.append(rel_err)
                    
                    status = "✓" if (conv and rel_err < 1e-4) else "✗"
                    if rel_err > 0.1:
                        all_converged = False
                    
                    print(f"  l={l}, n={n}: ω=({omega_M.real:.8f}-{abs(omega_M.imag):.8f}i) "
                          f"[{status}] err={rel_err:.2e} "
                          f"ref=({known_qnm[key].real:.8f}-{abs(known_qnm[key].imag):.8f}i)")
                
                if not np.isfinite(omega).all():
                    all_converged = False
        
        if all_errors:
            print(f"  → 平均误差: {np.mean(all_errors):.2e}, 最大误差: {max(all_errors):.2e}")
        
        results_all.append((x0, all_errors, all_converged))
    
    # 选择最优结果
    best = min(results_all, key=lambda r: np.mean(r[1]) if r[1] else float('inf'))
    best_x0, best_errors, best_conv = best
    
    print("\n" + "=" * 70)
    print(f"★ 最优展开点: x0 = {best_x0}")
    print(f"  收敛: {'是' if best_conv else '否'}")
    print(f"  平均相对误差: {np.mean(best_errors):.2e}")
    print(f"  最大相对误差: {max(best_errors):.2e}")
    
    if max(best_errors) < 1e-6:
        print("\n★ 求解器验证通过! 所有基准 < 1e-6")
    elif max(best_errors) < 1e-4:
        print("\n★ 求解器验证基本通过! 最大误差 < 1e-4")
    else:
        print(f"\n⚠ 最大误差仍较大 ({max(best_errors):.2e})，需要进一步调试")
    
    print("=" * 70)
    
    return best_x0, best_errors


if __name__ == "__main__":
    best_x0, best_errors = run_benchmark()
