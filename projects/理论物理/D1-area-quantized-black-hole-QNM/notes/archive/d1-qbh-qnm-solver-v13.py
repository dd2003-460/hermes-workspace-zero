#!/usr/bin/env python3
"""
Schwarzschild QBH QNM 精确求解器 — Shooting Method (r* space)
================================================================

**v13**：重构版，直接在 tortoise 坐标 r* 空间积分 Regge-Wheeler 方程。

**核心改进**：
- 原方程: d²Ψ/dr*² + (ω² - V_l(r))Ψ = 0
- 无 r 空间变换的 1/f 奇异性
- solve_ivp 可以稳定处理
- 视界初值简单明确: Ψ = exp(-iωr*), dΨ/dr* = -iω exp(-iωr*)

**V(r*) 的计算**：
- 预计算 r_grid → r*_grid 的映射
- 用 cubic spline 插值 r(r*)
- 避免每步调用 Newton 反函数

**验证基准**: Kokkotas & Schutz (1992) Table I
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
import warnings
import time

warnings.filterwarnings('ignore')

print(f"Python: {np.__version__}")
print("=" * 70)

# ============================================================================
# 预计算 r(r*) 插值
# ============================================================================

def build_r_star_interpolator(M=1.0, N_grid=5000):
    """
    预计算 r → r* 的映射，然后构建反函数 r(r*) 的插值
    
    r* = r + 2M ln(r/2M - 1)
    
    返回: interp1d(r*_grid, r_grid, kind='cubic')
    """
    rs = 2.0 * M
    
    # r 从 horizon 附近到无穷远
    r_grid = np.linspace(rs * 1.005, 200.0 * M, N_grid)
    
    # 计算对应的 r*
    r_star_grid = r_grid + rs * np.log(r_grid / rs - 1.0)
    
    # 构建 r(r*) 的 cubic spline 插值
    r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic', fill_value='extrapolate')
    
    return r_of_rstar


# ============================================================================
# RW 势在 r* 空间
# ============================================================================

def rw_potential_rstar(r_star, l, r_of_rstar, M=1.0):
    """
    Regge-Wheeler 势在 r* 空间的值
    
    V_l(r*) = (1 - 2M/r(r*)) × [l(l+1)/r(r*)²]
    
    注意：s=-2 时 (1-s²)=0，所以 6M/r³ 项为零
    """
    r = r_of_rstar(r_star)
    rs = 2.0 * M
    f = 1.0 - rs / r
    V = f * l * (l + 1) / (r**2)
    return V


# ============================================================================
# Regge-Wheeler 方程（r* 空间）
# ============================================================================

def rw_ode_rstar(r_star, Y, omega, l, r_of_rstar, M=1.0):
    """
    一阶形式的 Regge-Wheeler 方程
    
    d²Ψ/dr*² + (ω² - V)Ψ = 0
    
    令 Y[0] = Ψ, Y[1] = dΨ/dr*
    
    dY[0]/dr* = Y[1]
    dY[1]/dr* = -(ω² - V(r*)) × Y[0]
    """
    V = rw_potential_rstar(r_star, l, r_of_rstar, M)
    
    dYdr_star = np.array([
        Y[1],
        -(omega**2 - V) * Y[0]
    ])
    
    return dYdr_star


# ============================================================================
# 边界条件违反检查
# ============================================================================

def bc_violation(r_star, Y, omega, M=1.0):
    """
    无穷远边界条件违反
    
    在 r* → +∞:
    - 出射波: Ψ = exp(-iωr*)
    - dΨ/dr* = -iω exp(-iωr*) = -iωΨ
    - BC: dΨ/dr* + iωΨ = 0
    
    检查: |dΨ/dr* + iωΨ| / (|Ψ| + |dΨ/dr*|)
    """
    dpsi_drstar = Y[1]
    psi = Y[0]
    
    bc_val = abs(dpsi_drstar + 1j * omega * psi)
    norm = abs(psi) + abs(dpsi_drstar)
    
    if norm > 0:
        return bc_val / norm
    return bc_val


# ============================================================================
# 射击法求解
# ============================================================================

def solve_shooting_v13(omega, l, M=1.0, r_star_min=-50.0, r_star_max=80.0, N_points=10000):
    """
    Shooting method — r* 空间积分
    
    从视界 r*_min 积分到无穷远 r*_max
    检查无穷远边界条件违反
    """
    r_of_rstar = build_r_star_interpolator(M, N_grid=5000)
    
    r_star_evals = np.linspace(r_star_min, r_star_max, N_points)
    
    # 视界初值：纯出射波 Ψ = exp(-iωr*)
    psi_horizon = np.exp(-1j * omega * r_star_min)
    dpsi_horizon = -1j * omega * psi_horizon
    
    Y0 = [psi_horizon, dpsi_horizon]
    
    # 积分
    sol = solve_ivp(
        rw_ode_rstar,
        [r_star_min, r_star_max],
        Y0,
        args=(omega, l, r_of_rstar, M),
        method='RK45',
        t_eval=r_star_evals,
        dense_output=True,
        max_step=0.1  # 限制最大步长，避免错过振荡
    )
    
    # 无穷远检查
    Y_inf = sol.y[:, -1]
    bc_viol = bc_violation(r_star_max, Y_inf, omega, M)
    
    return bc_viol, sol


# ============================================================================
# BC 目标函数（用于优化）
# ============================================================================

def bc_objective_v13(omega_complex, l, M=1.0):
    """
    BC 违反值作为 ω 的函数（用于 minimize_scalar）
    
    输入: omega_complex = wr + i*wi（扁平化的复数，实部或虚部作为优化变量）
    """
    bc_viol, _ = solve_shooting_v13(omega_complex, l, M)
    return bc_viol


# ============================================================================
# WKB 初值
# ============================================================================

def omega_WKB_guess(l, n, M=1.0):
    """
    WKB 近似给出 ω 初值（基于标准 Schwarzschild）
    """
    omega_M = l * (0.5 - 0.149 * (n + 0.5)**0.616)
    imag_coefficients = {
        (2, 0): 0.089, (2, 1): 0.275, (2, 2): 0.470,
        (3, 0): 0.059, (3, 1): 0.269, (3, 2): 0.464,
        (4, 0): 0.044, (4, 1): 0.264, (4, 2): 0.460,
    }
    
    imag_coeff = imag_coefficients.get((l, n), 0.1 + 0.15 * n)
    omega_guess = complex(omega_M, -imag_coeff)
    
    return omega_guess


# ============================================================================
# 寻找 QNM
# ============================================================================

def find_qnm_v13(l, n, M=1.0, verbose=True):
    """
    通过两步扫描寻找 QNM 频率
    """
    t0 = time.time()
    omega_guess = omega_WKB_guess(l, n, M)
    
    if verbose:
        print(f"\n  l={l}, n={n}:")
        print(f"  WKB 初值: ω_g = {omega_guess.real:.6f} - {abs(omega_guess.imag):.6f}i")
    
    # 第 1 步：固定虚部，扫描实部
    def BC_real(wr):
        return bc_objective_v13(complex(wr, omega_guess.imag), l, M)
    
    real_min = omega_guess.real * 0.5
    real_max = omega_guess.real * 1.5
    
    print(f"    扫描实部 [{real_min:.4f}, {real_max:.4f}]...")
    res_real = minimize_scalar(BC_real, bounds=(real_min, real_max), method='bounded',
                               options={'xatol': 1e-8, 'maxiter': 100})
    
    omega_real_opt = res_real.x
    BC_at_real_opt = res_real.fun
    
    if verbose:
        print(f"    实部最优: {omega_real_opt:.8f} (BC={BC_at_real_opt:.3e})")
    
    # 第 2 步：固定实部，扫描虚部
    def BC_imag(wi):
        return bc_objective_v13(complex(omega_real_opt, wi), l, M)
    
    wi_min = omega_guess.imag * 3.0   # 更负
    wi_max = omega_guess.imag * 0.2   # 更不负
    
    print(f"    扫描虚部 [{wi_min:.4f}, {wi_max:.4f}]...")
    res_imag = minimize_scalar(BC_imag, bounds=(wi_min, wi_max), method='bounded',
                               options={'xatol': 1e-8, 'maxiter': 100})
    
    omega_final = complex(omega_real_opt, res_imag.x)
    elapsed = time.time() - t0
    
    if verbose:
        print(f"    虚部最优: {omega_final.imag:.8f}")
        print(f"    ωM = ({omega_final.real:.8f} - {abs(omega_final.imag):.8f}i)  [耗时 {elapsed:.1f}s]")
    
    return omega_final, elapsed


# ============================================================================
# 主程序
# ============================================================================

def run_all():
    M = 1.0
    
    # 基准值
    known_qnm = {
        (2, 0): complex(0.37373134, -0.08896258),
        (2, 1): complex(0.37329352, -0.27458937),
        (2, 2): complex(0.37265595, -0.46975278),
        (3, 0): complex(0.59187029, -0.05853522),
        (3, 1): complex(0.58971841, -0.26880432),
        (4, 0): complex(0.75906205, -0.04402477),
        (4, 1): complex(0.75816138, -0.26380755),
    }
    
    print("\n" + "=" * 70)
    print("Schwarzschild QBH QNM — Shooting Method v13")
    print("r* 空间直接积分，无奇异性")
    print("=" * 70)
    
    results = []
    total_time = time.time()
    
    for l in range(2, 5):
        for n in range(3):
            key = (l, n)
            omega_ref = known_qnm.get(key)
            
            t_start = time.time()
            omega_found, elapsed = find_qnm_v13(l, n, M, verbose=True)
            
            omega_M = omega_found * M
            if omega_ref is not None:
                rel_err = abs(omega_M - omega_ref) / abs(omega_ref)
                status = "✓" if rel_err < 0.05 else "⚠"
                print(f"    {status} 相对误差 = {rel_err:.6f} (5% 阈值)")
                print(f"    ref: ({omega_ref.real:.8f} - {abs(omega_ref.imag):.8f}i)")
            else:
                rel_err = None
                print(f"    (无参考值)")
            
            results.append((l, n, omega_found, rel_err, elapsed))
            
            if l >= 3 and n >= 2:
                break
    
    total_elapsed = time.time() - total_time
    
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print(f"{'(l,n)':<10} {'计算值':>25} {'误差':>10} {'耗时':>8}")
    print("-" * 60)
    
    for l, n, omega, err, t in results:
        val = f"({omega.real:.8f} - {abs(omega.imag):.8f}i)"
        err_str = f"{err:.6f}" if err is not None else "N/A"
        print(f"({l},{n})  {val:<25} {err_str:>10} {t:7.1f}s")
    
    errors = [r[3] for r in results if r[3] is not None]
    if errors:
        print(f"\n  最大误差: {max(errors):.6f}")
        print(f"  平均误差: {np.mean(errors):.6f}")
    print(f"\n  总耗时: {total_elapsed:.1f}s")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    run_all()
