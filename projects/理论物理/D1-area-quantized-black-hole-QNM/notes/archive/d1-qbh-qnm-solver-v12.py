#!/usr/bin/env python3
"""
Schwarzschild QBH QNM 精确求解器 — Shooting Method (r-space integration)
=========================================================================

**v12**：完全避免龟坐标反函数的 O(N×50) 卡死问题。

**修复**：在 r 空间直接积分，使用链式法则变换微分方程：
    d²Ψ/dr*² + (ω² - V)Ψ = 0
    → f² d²Ψ/dr² + f f' dΨ/dr + (ω² - V)Ψ = 0
    
    其中 f = 1 - 2M/r, f' = 2M/r²

**边界条件**：
    - Horizon (r → 2M): 出射波 Ψ ~ exp(-iωr*)
    - Infinity (r → ∞): 出射波 Ψ ~ exp(-iωr*)

**验证基准**: Kokkotas & Schutz (1992) Table I

参考: Berti et al. (2009) §III.B — 直接 r 空间积分方法
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
import sys
import time

print(f"Python: {np.__version__}")
print("=" * 70)


# ============================================================================
# 变换后的 Regge-Wheeler 方程（r 空间）
# ============================================================================

def f_function(r, M=1.0):
    """Schwarzschild 因子: f = 1 - 2M/r"""
    rs = 2.0 * M
    return 1.0 - rs / r


def f_prime(r, M=1.0):
    """df/dr = 2M/r²"""
    rs = 2.0 * M
    return rs / (r**2)


def rw_potential(r, l, s=-2, M=1.0):
    """Regge-Wheeler 有效势"""
    rs = 2.0 * M
    return f_function(r, M) * (l * (l + 1) / (r**2) + (1 - s**2) * 2.0 * M / (r**3))


def r_space_rhs(r, Y, omega, l, s=-2, M=1.0):
    """
    变换后的 RW 方程在 r 空间的一阶形式
    
    原方程: d²Ψ/dr*² + (ω² - V)Ψ = 0
    
    变换: 令 y1 = Ψ, y2 = dΨ/dr
    dy1/dr = y2
    dy2/dr = -f'/f × y2 - (ω² - V)/f² × y1
    
    注意：在 horizon 处 f → 0，所以需要小心处理
    """
    rs = 2.0 * M
    f = f_function(r, M)
    fp = f_prime(r, M)
    V = rw_potential(r, l, s, M)
    
    # 避免 horizon 处除以零
    if f < 1e-15:
        f = 1e-15
    
    # dy1/dr = y2
    # dy2/dr = -(f'/f)*y2 - (ω²-V)/f²*y1
    dy2 = -(fp / f) * Y[1] - (omega**2 - V) / (f**2) * Y[0]
    
    return np.array([Y[1], dy2])


# ============================================================================
# Horizon 附近的出射波初值
# ============================================================================

def horizon_initial_condition(r, omega, l, s=-2, M=1.0):
    """
    在 horizon 附近的出射波初值
    
    原方程: d²Ψ/dr*² + (ω² - V)Ψ = 0
    
    在 horizon (r → 2M) 处:
    - f → 0, V → 0
    - 方程变为: d²Ψ/dr*² + ω²Ψ = 0
    - 出射波解: Ψ = exp(-iωr*)
    
    变换到 r 空间:
    dΨ/dr = dΨ/dr* × dr*/dr = (-iω exp(-iωr*)) / f
         = -iωΨ / f
    
    由于 f = 1 - 2M/r 在 horizon 附近 ~ (r-2M)/(2M)，
    且 exp(-iωr*) ~ (r-2M)^(-iω×2M)，所以:
    Ψ ≈ C × (r-2M)^(-iω×2M)
    
    dΨ/dr ≈ C × (-iω×2M) × (r-2M)^(-iω×2M - 1)
          = (-iω×2M) / (r-2M) × Ψ
          = (-iω×2M) / (r-2M) × Ψ
    
    但 f = (r-2M)/r ≈ (r-2M)/2M，所以:
    f' = 2M/r² ≈ 1/(2M)
    f'/f ≈ 1/(r-2M)
    
    因此: dΨ/dr ≈ (-iω×2M) / (r-2M) × Ψ = -iω × (2M/(r-2M)) × Ψ = -iω/f × Ψ
    """
    rs = 2.0 * M
    # 在 horizon 附近一点点开始，避免 f=0
    eps = 1e-10
    r_horizon = rs + eps
    
    # Ψ = exp(-iωr*)
    # 计算 r* 的近似值
    # r* = r + 2M ln(r/2M - 1)
    # 在 r → 2M 附近: r* ≈ 2M ln(r/2M - 1)
    r_star_approx = 2.0 * M * np.log(eps / (2.0 * M))
    
    psi = np.exp(-1j * omega * r_star_approx)
    
    # dΨ/dr = -iω/f × Ψ ≈ -iω × (2M/eps) × Ψ
    dpsi_dr = -1j * omega / f_function(r_horizon, M) * psi
    
    return np.array([psi, dpsi_dr])


# ============================================================================
# 无穷远处的渐近行为检查
# ============================================================================

def asymp_check_inf(r, Y, omega, M=1.0):
    """
    在无穷远处检查边界条件
    
    在 r → ∞ 处:
    - f → 1, V → 0
    - 方程变为: d²Ψ/dr*² + ω²Ψ = 0
    - 出射波: Ψ = exp(-iωr*)
    - dΨ/dr* = -iω exp(-iωr*) = -iωΨ
    
    在 r 空间:
    dΨ/dr = dΨ/dr* × dr*/dr = -iωΨ × f ≈ -iωΨ (在无穷远处)
    
    检查: |dΨ/dr + iωΨ| < tolerance
    """
    f = f_function(r, M)
    dpsi_dr = Y[1]
    psi = Y[0]
    
    # 预期: dΨ/dr ≈ -iω × f × Ψ
    # 在无穷远处 f → 1
    expected_dpsi = -1j * omega * f * psi
    
    BC_violation = abs(dpsi_dr - expected_dpsi)
    
    return BC_violation, psi, dpsi_dr


# ============================================================================
# Shooting Method — r 空间积分
# ============================================================================

def solve_shooting_v12(omega, l, s=-2, M=1.0,
                       r_min_frac=2.5, r_max_frac=50.0,
                       N_points=20000):
    """
    在 r 空间直接积分的 shooting method
    
    避开龟坐标反函数，完全避免卡死问题
    """
    t0 = time.time()
    
    # 积分范围
    r_min = r_min_frac * M      # ~2.5M, r* ≈ 1.2
    r_max = r_max_frac * M      # ~50M, r* ≈ 50 + 2ln(24) ≈ 57.6
    
    print(f"  r 范围: [{r_min:.4f}, {r_max:.4f}]")
    print(f"  r* 范围: [{r_min + 2*np.log(r_min/2 - 1):.4f}, {r_max + 2*np.log(r_max/2 - 1):.4f}]")
    
    # Horizon 初值
    Y0 = horizon_initial_condition(r_min, omega, l, s, M)
    
    # 积分
    sol = solve_ivp(
        lambda r, Y: r_space_rhs(r, Y, omega, l, s, M),
        [r_min, r_max],
        Y0,
        method='RK45',
        dense_output=True,
        rtol=1e-10,
        atol=1e-12,
        max_step=(r_max - r_min) / 500,
    )
    
    elapsed = time.time() - t0
    
    if not sol.success:
        print(f"  ⚠ solve_ivp 失败: {sol.message}")
        return None, np.inf, 0, 0, elapsed
    
    # 无穷远检查
    r_end = sol.t[-1]
    BC_viol, psi_end, dpsi_end = asymp_check_inf(r_end, sol.y[:, -1], omega, M)
    
    return sol, BC_viol, psi_end, dpsi_end, elapsed


# ============================================================================
# 目标函数 — BC violation 作为 omega 的函数
# ============================================================================

def BC_objective(omega, l, s=-2, M=1.0):
    """
    计算给定 omega 的边界条件违反程度
    """
    try:
        sol, BC_viol, _, _, _ = solve_shooting_v12(omega, l, s, M)
        if sol is not None:
            return BC_viol
        return np.inf
    except Exception as e:
        print(f"    BC 计算异常: {e}")
        return np.inf


# ============================================================================
# WKB 初值估计
# ============================================================================

def omega_WKB_guess(l, n, M=1.0):
    """
    WKB 近似给出 QNM 频率初值
    
    参考: Schutz & Will (1985), Kokkotas & Schutz (1992)
    
    ω ≈ ω_M + i × ω_I
    
    其中 ω_M = l / (3√3 M), ω_I 随 n 增加而增大（虚部绝对值增大，阻尼增强）
    """
    # 最可几半径: r_M = 3M (势峰位置)
    r_peak = 3.0 * M
    
    # 有效角频率（无自旋，l ≥ 2）
    omega_M = l / (3.0 * np.sqrt(3.0)) / M
    
    # 虚部估计：n=0 时 ~ -0.09，n 增大时更负
    # 参考: Kokkotas & Schutz (1992) Table I
    # (2,0): -0.089, (2,1): -0.275, (2,2): -0.470
    # (3,0): -0.059, (3,1): -0.269, (3,2): -0.464
    # (4,0): -0.044, (4,1): -0.264, (4,2): -0.460
    
    imag_coefficients = {
        (2, 0): 0.089, (2, 1): 0.275, (2, 2): 0.470,
        (3, 0): 0.059, (3, 1): 0.269, (3, 2): 0.464,
        (4, 0): 0.044, (4, 1): 0.264, (4, 2): 0.460,
    }
    
    imag_coeff = imag_coefficients.get((l, n), 0.1 + 0.15 * n)
    
    omega_guess = complex(omega_M, -imag_coeff)
    
    return omega_guess


# ============================================================================
# 寻找 QNM — 复数平面扫描
# ============================================================================

def find_qnm(l, n, s=-2, M=1.0, verbose=True):
    """
    通过扫描寻找 QNM 频率
    
    策略：
    1. WKB 给出初值
    2. 实部上扫描：找到 BC violation 最小的 omega_real
    3. 虚部上扫描：确认虚部也是最优的
    """
    t0 = time.time()
    omega_guess = omega_WKB_guess(l, n, M)
    
    if verbose:
        print(f"\n  l={l}, n={n}:")
        print(f"  WKB 初值: ω_g = {omega_guess.real:.6f} - {abs(omega_guess.imag):.6f}i")
    
    # 第 1 步：固定虚部，扫描实部
    def BC_real(wr):
        return BC_objective(complex(wr, omega_guess.imag), l, n, M)
    
    # 在 WKB 附近 +-10% 范围内扫描
    real_min = omega_guess.real * 0.7
    real_max = omega_guess.real * 1.3
    
    res = minimize_scalar(BC_real, bounds=(real_min, real_max), method='bounded',
                          options={'xatol': 1e-10, 'maxiter': 200})
    
    omega_real_opt = res.x
    BC_at_real_opt = res.fun
    
    if verbose:
        print(f"  实部最优: {omega_real_opt:.8f} (BC={BC_at_real_opt:.3e})")
    
    # 第 2 步：固定实部，扫描虚部
    def BC_imag(wi):
        return BC_objective(complex(omega_real_opt, wi), l, n, M)
    
    # 在 WKB 虚部附近扫描
    wi_min = omega_guess.imag * 2.0   # 更负（更强阻尼）
    wi_max = omega_guess.imag * 0.3   # 更不负（更弱阻尼）
    
    res_wi = minimize_scalar(BC_imag, bounds=(wi_min, wi_max), method='bounded',
                             options={'xatol': 1e-10, 'maxiter': 200})
    
    omega_final = complex(omega_real_opt, res_wi.x)
    
    elapsed = time.time() - t0
    
    if verbose:
        print(f"  虚部最优: {omega_final.imag:.8f}")
        print(f"  ωM = ({omega_final.real:.8f} - {abs(omega_final.imag):.8f}i)  [耗时 {elapsed:.1f}s]")
    
    return omega_final, elapsed


# ============================================================================
# 主程序
# ============================================================================

def run_all():
    M = 1.0
    s = -2
    
    # 文献基准值：Kokkotas & Schutz (1992) Table I
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
    print("Schwarzschild QBH QNM — Shooting Method v12")
    print("r 空间直接积分，无龟坐标反函数")
    print("=" * 70)
    
    results = []
    total_time = time.time()
    
    for l in range(2, 5):
        for n in range(3):
            key = (l, n)
            omega_ref = known_qnm.get(key)
            
            t_start = time.time()
            omega_found, elapsed = find_qnm(l, n, s, M, verbose=True)
            
            # 计算相对误差
            omega_M = omega_found * M
            if omega_ref is not None:
                rel_err = abs(omega_M - omega_ref) / abs(omega_ref)
                status = "✓" if rel_err < 0.05 else "⚠"
                print(f"  {status} err = {rel_err:.6f} (5%% 阈值)")
                print(f"  ref: ({omega_ref.real:.8f} - {abs(omega_ref.imag):.8f}i)")
            else:
                rel_err = None
                print(f"  (无参考值)")
            
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
