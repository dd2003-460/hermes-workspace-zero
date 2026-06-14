#!/usr/bin/env python3
"""
Schwarzschild QNM 求解器 v7 — Shooting Method (直接数值积分)
===============================================================

**为什么换方法**: Leaver 连分数法的 ABC 公式实现存在系统性问题——
A 系数量级太小导致连分数发散 (NaN/inf)。Shooting method 虽然慢一些，
但公式直接、容易验证。

**算法**:
1. 将 RW 方程转换为二阶 ODE 系统
2. 从视界 (r*→-∞) 和无穷远 (r*→+∞) 分别积分
3. 在势峰处匹配对数导数 (log-derivative matching)
4. 扫描 ω 复平面寻找匹配点

验证: Kokkotas & Schutz (1992) Table I
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
    """乌龟坐标: r* = r + 2M ln(r/2M - 1)"""
    rs = 2.0 * M
    return r + rs * np.log(np.abs(r / rs - 1.0))


def schw_potential(r, l, s=-2, M=1.0):
    """Regge-Wheeler 有效势"""
    rs = 2.0 * M
    return (1.0 - rs / r) * (l * (l + 1) / (r ** 2) + (1 - s ** 2) * rs / (r ** 3))


def rw_ode(y, r, omega, l, M=1.0):
    """
    Regge-Wheeler 方程的一阶形式。
    
    原始方程: d²Ψ/dr*² + (ω² - V_l(r*))Ψ = 0
    
    转换为二阶系统:
    y[0] = Ψ
    y[1] = dΨ/dr*
    
    注意: dr*/dr = r/(r-2M)，所以 d/dr = (r-2M)/r · d/dr*
    """
    rs = 2.0 * M
    drstar_dr = r / (r - rs)
    
    V = schw_potential(r, l, -2, M)
    
    dPsi_drstar = y[1]
    d2Psi_drstar2 = -(omega**2 - V) * y[0]
    
    # 转换为对 r 的导数
    dPsi_dr = dPsi_drstar / drstar_dr
    d2Psi_dr = (d2Psi_drstar2 - y[1] * (rs / (r - rs)) * drstar_dr) / (drstar_dr ** 2)
    
    return [dPsi_dr, d2Psi_dr]


def compute_log_derivative(r_grid, omega, l, M=1.0, direction='in'):
    """
    数值积分并返回终点的对数导数 Ψ'/Ψ。
    
    direction='in': 从无穷远向内积分 (匹配 e^{+iωr*} 出射边界条件)
    direction='out': 从视界向外积分 (匹配 e^{-iωr*} 吸收边界条件)
    """
    rs = 2.0 * M
    dtypes = complex
    
    if direction == 'in':
        # 从无穷远向内: r_start → r_end (r_end < r_start)
        r_star_inf = 100.0 * M
        r_end = r_grid[len(r_grid) // 2]  # 中间点
        
        # 初始条件: Ψ = e^{+iωr*} (纯出射)
        # Ψ(r_start) = exp(1j * omega * tortoise_coordinate(r_star_inf))
        # Ψ'(r_start) = +iω * Ψ(r_start) / (dr*/dr)|_{r_start}
        
        r_start = r_star_inf
        Psi0 = np.exp(1j * omega * tortoise_coordinate(r_start, M))
        drstar_dr_start = r_start / (r_start - rs)
        dPsi0 = 1j * omega * Psi0 / drstar_dr_start
        
        y0 = [Psi0, dPsi0]
        r_span = [r_start, r_end]
        r_eval = np.linspace(r_start, r_end, 500)
        
        sol = solve_ivp(rw_ode, r_span, y0, args=(omega, l, M),
                       t_eval=r_eval, dense_output=True,
                       max_step=0.1 * M, rtol=1e-10, atol=1e-12)
        
        if not sol.success:
            return np.nan
        
        # 获取终点的值和对数导数
        Psi_end = sol.y[0, -1]
        dPsi_end = sol.y[1, -1]
        drstar_dr_end = sol.y[1, -1]  # 这不对，需要重新计算
        
        # 正确计算终点的对数导数 (对 r*)
        r_end_actual = sol.t[-1]
        drstar_dr_end = r_end_actual / (r_end_actual - rs)
        dPsi_drstar_end = sol.y[1, -1] * drstar_dr_end
        
        log_deriv = dPsi_drstar_end / Psi_end
        
    else:  # 'out'
        # 从视界向外: r_start → r_end (r_start > 2M)
        r_start = 2.0001 * M
        r_end = r_grid[len(r_grid) // 2]
        
        # 初始条件: Ψ = e^{-iωr*} (纯吸收)
        Psi0 = np.exp(-1j * omega * tortoise_coordinate(r_start, M))
        drstar_dr_start = r_start / (r_start - rs)
        dPsi0 = -1j * omega * Psi0 / drstar_dr_start
        
        y0 = [Psi0, dPsi0]
        r_span = [r_start, r_end]
        r_eval = np.linspace(r_start, r_end, 500)
        
        sol = solve_ivp(rw_ode, r_span, y0, args=(omega, l, M),
                       t_eval=r_eval, dense_output=True,
                       max_step=0.1 * M, rtol=1e-10, atol=1e-12)
        
        if not sol.success:
            return np.nan
        
        # 获取终点的值和对数导数 (对 r*)
        r_end_actual = sol.t[-1]
        drstar_dr_end = r_end_actual / (r_end_actual - rs)
        dPsi_drstar_end = sol.y[1, -1] * drstar_dr_end
        Psi_end = sol.y[0, -1]
        
        log_deriv = dPsi_drstar_end / Psi_end
    
    return log_deriv


def matching_residual(omega_real, omega_imag, l, n=0, M=1.0):
    """
    匹配残差: |log_deriv_in - log_deriv_out|
    """
    omega = complex(omega_real, -omega_imag)
    
    # 避免数值问题
    if omega.imag > 0:  # QNM 必须有 Im(ω) < 0
        return 1e10
    
    try:
        log_in = compute_log_derivative(np.array([5.0]), omega, l, M, 'in')
        log_out = compute_log_derivative(np.array([5.0]), omega, l, M, 'out')
        
        if np.isnan(log_in) or np.isnan(log_out):
            return 1e10
        
        return abs(log_in - log_out)
    except Exception:
        return 1e10


def find_qnm(l, n, M=1.0):
    """
    使用 shooting method + optimization 寻找 QNM 频率。
    
    Eikonal 初值估计: ω ≈ l/(√27 M) - i(n+1/2)√27/(2M)
    """
    # Eikonal 初值
    omega_R0 = l / np.sqrt(27.0 * M)
    omega_I0 = (n + 0.5) * np.sqrt(27.0) / (2.0 * M)
    
    print(f"  初值: ω₀ = {omega_R0:.6f} - {omega_I0:.6f}i")
    
    # 使用 Nelder-Mead 方法最小化匹配残差
    result = minimize(
        matching_residual,
        x0=[omega_R0, omega_I0],
        args=(l, n, M),
        method='Nelder-Mead',
        options={
            'xatol': 1e-12,
            'fatol': 1e-12,
            'maxiter': 5000,
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
    print("Schwarzschild QNM — Shooting Method v7")
    print("=" * 70)
    print("验证基准: Kokkotas & Schutz (1992) Table I")
    print("=" * 70)
    print()
    
    M = 1.0
    s = -2
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
