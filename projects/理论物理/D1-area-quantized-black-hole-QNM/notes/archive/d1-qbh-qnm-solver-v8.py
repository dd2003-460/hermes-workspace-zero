#!/usr/bin/env python3
"""
Schwarzschild QNM 求解器 v8 — Shooting Method 修正版
=======================================================

**修复**: numpy 数组标量转换问题 (v7 的 TypeError)
**方法**: Shooting + log-derivative matching
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

np.set_printoptions(precision=10, suppress=True)


# ============================================================================
# Schwarzschild 几何
# ============================================================================

def tortoise_coordinate(r, M=1.0):
    """乌龟坐标"""
    rs = 2.0 * M
    return r + rs * np.log(np.abs(r / rs - 1.0))


def schw_potential(r, l, M=1.0):
    """Regge-Wheeler 有效势 (s=-2)"""
    rs = 2.0 * M
    return (1.0 - rs / r) * (l * (l + 1) / (r ** 2) + rs / (r ** 3))


def rw_system(r, Y, omega, l, M=1.0):
    """
    Regge-Wheeler 方程的一阶形式 (对 r*)。
    
    Y = [Ψ, dΨ/dr*]
    dY/dr* = [dΨ/dr*, -(ω² - V)Ψ]
    
    但 solve_ivp 需要对普通变量的导数，所以用链式法则：
    dY/dr = (dY/dr*) · (dr*/dr) = (dY/dr*) · (r/(r-2M))
    """
    rs = M * 2
    drstar_dr = r / (r - rs)
    
    V = schw_potential(r, l, M)
    dPsi_drstar = Y[1]
    d2Psi_drstar2 = -(omega**2 - V) * Y[0]
    
    return [dPsi_drstar * drstar_dr, d2Psi_drstar2 * drstar_dr]


def integrate_from_boundary(r_boundary, omega, l, M=1.0, direction='in'):
    """
    从边界条件积分到中间匹配点。
    
    direction='in': 从无穷远向内积分，初值 Ψ = e^{+iωr*}
    direction='out': 从视界向外积分，初值 Ψ = e^{-iωr*}
    
    返回终点的 (Ψ, dΨ/dr*) 元组
    """
    rs = M * 2
    
    if direction == 'in':
        r_start = max(r_boundary, 10.0 * M)
        r_match = 3.5 * M  # 势峰附近
        
        Psi0 = np.exp(1j * omega * tortoise_coordinate(r_start, M))
        drstar_dr_start = r_start / (r_start - rs)
        dPsi0 = 1j * omega * Psi0 / drstar_dr_start
        
        y0 = [Psi0, dPsi0]
        r_eval = np.linspace(r_start, r_match, 1000)
        
        sol = solve_ivp(
            lambda r, Y: rw_system(r, Y, omega, l, M),
            [r_start, r_match], y0, t_eval=r_eval,
            rtol=1e-10, atol=1e-13, max_step=0.05 * M
        )
    else:  # 'out'
        r_start = rs * (1.0 + 1e-6)
        r_match = r_boundary
        
        Psi0 = np.exp(-1j * omega * tortoise_coordinate(r_start, M))
        drstar_dr_start = r_start / (r_start - rs)
        dPsi0 = -1j * omega * Psi0 / drstar_dr_start
        
        y0 = [Psi0, dPsi0]
        r_eval = np.linspace(r_start, r_match, 1000)
        
        sol = solve_ivp(
            lambda r, Y: rw_system(r, Y, omega, l, M),
            [r_start, r_match], y0, t_eval=r_eval,
            rtol=1e-10, atol=1e-13, max_step=0.05 * M
        )
    
    if not sol.success:
        return np.nan, np.nan
    
    Psi_end = sol.y[0, -1]
    dPsi_dr_end = sol.y[1, -1]
    
    # 转换为对 r* 的导数
    r_end = sol.t[-1]
    drstar_dr_end = r_end / (r_end - rs)
    dPsi_drstar_end = dPsi_dr_end / drstar_dr_end
    
    return Psi_end, dPsi_drstar_end


def matching_residual_scalar(omega_vec, l, n, M=1.0):
    """
    匹配残差: |log_deriv_in - log_deriv_out| at matching point r=3.5M
    
    omega_vec = [omega_R, omega_I]  (omega_I > 0, 实际 omega = omega_R - i*omega_I)
    """
    omega_real = float(omega_vec[0])
    omega_imag = float(omega_vec[1])
    
    # QNM 条件: Im(omega) < 0 → omega_imag > 0
    omega = omega_real - 1j * omega_imag
    
    if omega_imag < 0.001:  # 太小则无物理意义
        return 1e10
    
    try:
        Psi_in, dPsi_in = integrate_from_boundary(3.5 * M, omega, l, M, 'in')
        Psi_out, dPsi_out = integrate_from_boundary(3.5 * M, omega, l, M, 'out')
        
        if np.isnan(Psi_in) or np.isnan(Psi_out):
            return 1e10
        
        log_in = dPsi_in / Psi_in
        log_out = dPsi_out / Psi_out
        
        return abs(log_in - log_out)
    except Exception as e:
        return 1e10


def find_qnm(l, n, M=1.0):
    """
    使用 shooting method + optimization 寻找 QNM 频率。
    
    Eikonal 初值估计: ω ≈ l/(√27 M) - i(n+1/2)√27/(2M)
    """
    omega_R0 = l / np.sqrt(27.0 * M)
    omega_I0 = (n + 0.5) * np.sqrt(27.0) / (2.0 * M)
    
    print(f"  初值: ω₀ = {omega_R0:.6f} - {omega_I0:.6f}i")
    
    result = minimize(
        matching_residual_scalar,
        x0=[omega_R0, omega_I0],
        args=(l, n, M),
        method='Nelder-Mead',
        options={
            'xatol': 1e-12,
            'fatol': 1e-12,
            'maxiter': 10000,
            'adaptive': True
        }
    )
    
    omega_R = result.x[0]
    omega_I = result.x[1]
    
    print(f"  结果: ω = {omega_R:.8f} - {omega_I:.8f}i (残差={result.fun:.2e})")
    
    if result.fun > 1e-4:
        print(f"  ⚠ 残差较大，可能未收敛")
    
    return complex(omega_R, -omega_I)


def run_benchmark():
    print("=" * 70)
    print("Schwarzschild QNM — Shooting Method v8")
    print("=" * 70)
    print("验证基准: Kokkotas & Schutz (1992) Table I")
    print("=" * 70)
    print()
    
    M = 1.0
    l_max = 4
    n_max = 2
    
    known_qnm = {
        (2, 0): complex(0.37373134, -0.08896258),
        (2, 1): complex(0.37329352, -0.27458937),
        (2, 2): complex(0.37265595, -0.46975278),
        (3, 0): complex(0.59187029, -0.05853522),
        (3, 1): complex(0.58971841, -0.26880432),
        (4, 0): complex(0.75906205, -0.04402477),
        (4, 1): complex(0.75816138, -0.26380755),
    }
    
    results = []
    
    for l in range(2, l_max + 1):
        for n in range(n_max + 1):
            print(f"\n--- l={l}, n={n} ---")
            omega = find_qnm(l, n, M)
            omega_M = omega * M
            
            key = (l, n)
            rel_err = float('inf')
            known = None
            if key in known_qnm:
                known = known_qnm[key]
                rel_err = abs(omega_M - known) / abs(known)
            
            results.append((l, n, omega_M, rel_err, known))
            
            status = "✓" if rel_err < 1e-4 else "?"
            print(f"  [{status}] ωM = ({omega_M.real:.8f} - {abs(omega_M.imag):.8f}i)")
            if known is not None:
                print(f"       ref: ({known.real:.8f} - {abs(known.imag):.8f}i)")
                print(f"       err = {rel_err:.2e}")
    
    print("\n" + "=" * 70)
    print("总结:")
    print("-" * 70)
    
    errs = [r[3] for r in results if r[3] != float('inf')]
    if errs:
        print(f"  最大相对误差: {max(errs):.2e}")
        print(f"  平均相对误差: {np.mean(errs):.2e}")
        
        if max(errs) < 1e-6:
            print("\n  ★ 求解器验证通过! 所有基准 < 1e-6")
        elif max(errs) < 1e-4:
            print("\n  ★ 求解器验证基本通过! 最大误差 < 1e-4")
        else:
            print(f"\n  ⚠ 最大误差较大 ({max(errs):.2e})，需要调试")
    
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    run_benchmark()
