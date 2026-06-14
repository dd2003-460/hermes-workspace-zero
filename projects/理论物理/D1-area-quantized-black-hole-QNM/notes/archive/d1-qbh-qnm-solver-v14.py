#!/usr/bin/env python3
"""
Schwarzschild QNM 求解器 v14 — Shooting Method (Monodromy)
=============================================================

**核心方法**：
1. 从视界积分两个线性独立的初值条件，得到 monodromy 矩阵 M(ω)
2. 找到线性组合系数，使得组合解满足无穷远出射边界条件
3. 边界条件违反值作为 ω 的函数，在 QNM 实部处有尖点最小值

**关键原理**：
- 视界初值固定为出射波 Ψ ~ exp(-iωr*), Ψ' = -iωΨ
- 不同虚部 Im(ω) 给出不同的视界初值，产生不同的 "出射波"
- 只有当 ω = ω_QNM（复频率）时，无穷远处 BC 违反 = 0
- 固定 Im(ω)，扫描 Re(ω)，BC 违反在 Re(ω_QNM) 处有局部最小值

**验证**：对比 Kokkotas & Schutz 1992 Table I
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
import time
import warnings
warnings.filterwarnings('ignore')

print(f"NumPy: {np.__version__}")
print("=" * 70)

# ============================================================================
# Regge-Wheeler 势 (l=2 为主)
# ============================================================================

def rw_potential(r, l=2, M=1.0):
    """标准 Schwarzschild Regge-Wheeler 势 (s=-2)"""
    rs = 2.0 * M
    f = 1.0 - rs / r
    return f * l * (l + 1) / (r ** 2)

# ============================================================================
# 乌龟坐标变换
# ============================================================================

def r_to_rstar(r, M=1.0):
    """r → r* 变换: r* = r + 2M ln(r/2M - 1)"""
    rs = 2.0 * M
    return r + rs * np.log(r / rs - 1.0)

def rstar_to_r(rstar, M=1.0, r_init=None):
    """r* → r 反变换（Newton 迭代）"""
    if r_init is None:
        r_init = max(rstar + 2.0 * M, 2.001 * M)
    rs = 2.0 * M
    r = r_init
    for _ in range(50):
        f_r = r + rs * np.log(r / rs - 1.0) - rstar
        df_dr = 1.0 + rs / (r - rs)
        dr = f_r / df_dr
        r -= dr
        if abs(dr) < 1e-15:
            break
    return r

# ============================================================================
# 积分 Regge-Wheeler 方程
# ============================================================================

def integrate_rw(r_star_start, r_star_end, y0, omega, l, M, n_points=5000):
    """
    从 r_star_start 积分到 r_star_end
    
    方程: d²Ψ/dr*² + (ω² - V_l)Ψ = 0
    
    返回: (r_star_evals, psi, dpsi)
    """
    def ode(r_star, y):
        r = rstar_to_r(r_star, M, y[0] / max(abs(y[0]), 1e-10) * 3.0)
        V = rw_potential(r, l, M)
        return [y[1], -(omega**2 - V) * y[0]]

    r_star_evals = np.linspace(r_star_start, r_star_end, n_points)

    sol = solve_ivp(
        ode,
        [r_star_start, r_star_end],
        y0,
        method='RK45',
        t_eval=r_star_evals,
        max_step=0.05,
        rtol=1e-10,
        atol=1e-12,
        dense_output=True
    )

    psi = sol.y[0]
    dpsi = sol.y[1]
    return sol.y[0], sol.y[1]

# ============================================================================
# Monodromy 矩阵
# ============================================================================

def compute_monodromy(r_star_horizon, r_star_infinity, omega, l, M, n_points=5000):
    """
    计算 monodromy 矩阵 M(ω)

    M = [Ψ1(r_inf), Ψ2(r_inf)]  2x2 矩阵
    其中 Ψi 是对应于不同视界初值的解

    初值条件:
    - 组1: Ψ=1, Ψ'=-iω  (对应于 Ψ ~ exp(-iωr*))
    - 组2: Ψ=i, Ψ'=-iω*i = ω  (正交初值)
    """
    y0_1 = [1.0, -1j * omega]
    y0_2 = [1.0j, -1j * omega * 1.0j]

    psi1, dpsi1 = integrate_rw(r_star_horizon, r_star_infinity, y0_1, omega, l, M, n_points)
    psi2, dpsi2 = integrate_rw(r_star_horizon, r_star_infinity, y0_2, omega, l, M, n_points)

    # Monodromy 矩阵: M[i,j] = jth 初值条件在无穷远的第 i 个分量
    M_mat = np.array([
        [psi1[-1], psi2[-1]],
        [dpsi1[-1], dpsi2[-1]]
    ])

    return M_mat

# ============================================================================
# 边界条件违反
# ============================================================================

def bc_violation_monodromy(M_mat, omega, M_phys=1.0):
    """
    找到使得组合解满足无穷远出射 BC 的最小违反程度

    出射波: Ψ' + iωΨ = 0

    对于线性组合 c1*Psi1 + c2*Psi2:
    BC(c) = c1*(Ψ1' + iωΨ1) + c2*(Ψ2' + iωΨ2)
          = c1*B1 + c2*B2

    我们需要 ||c|| = 1 使得 BC(c) = 0
    这是一个 1x2 系统: [B1, B2] · [c1, c2] = 0

    最小违反 = |B| / ||B|| (当组合正交于 B 时违反为 0)
    """
    B = np.array([
        M_mat[1, 0] + 1j * omega * M_mat[0, 0],  # BC for solution 1
        M_mat[1, 1] + 1j * omega * M_mat[0, 1]   # BC for solution 2
    ])

    bc_viol = np.abs(B) / (np.abs(M_mat[0, :]) + np.abs(M_mat[1, :]) + 1e-30)

    return np.min(bc_viol)

# ============================================================================
# 扫描函数
# ============================================================================

def scan_frequency_range(r_star_horizon, r_star_infinity, omega_range, omega_vals, l, M, n_points=5000):
    """
    扫描频率范围，计算每个 ω 的 BC 违反
    """
    results = []

    for omega in omega_vals:
        # 扫描不同虚部
        for imag_offset in [-0.02, 0.0, 0.02]:
            omega_test = complex(omega, -0.089 + imag_offset)  # 以 n=0 为中心

            try:
                M_mat = compute_monodromy(r_star_horizon, r_star_infinity, omega_test, l, M, n_points)
                bc = bc_violation_monodromy(M_mat, omega_test, M)
                results.append((omega, imag_offset, bc))
            except Exception as e:
                results.append((omega, imag_offset, float('inf')))

    return results

# ============================================================================
# 寻找最小值
# ============================================================================

def find_local_minima(bc_violations, omega_vals):
    """
    在 BC 违反曲线中找出局部最小值（候选 QNM）
    """
    minima = []
    for i in range(2, len(bc_violations) - 2):
        if (bc_violations[i] < bc_violations[i-1] and
            bc_violations[i] < bc_violations[i+1] and
            bc_violations[i] < bc_violations[i-2] and
            bc_violations[i] < bc_violations[i+2]):
            minima.append((omega_vals[i], bc_violations[i]))

    return minima

# ============================================================================
# 主求解
# ============================================================================

def solve_qnm_shooting(l, n, M=1.0):
    """
    使用 shooting method 求解 QNM
    """
    rs = 2.0 * M

    # 视界和无穷远的 r*
    r_horizon = rs * 1.005
    r_star_horizon = r_to_rstar(r_horizon, M)
    r_star_infinity = 80.0  # 截断

    # 以 WKB 初值为中心扫描
    omega_wkb = complex(
        l * 0.5,
        -(0.089 + 0.186 * n)
    )

    # 精细扫描
    omega_scan = np.linspace(omega_wkb.real - 0.2, omega_wkb.real + 0.2, 200)

    print(f"\n  l={l}, n={n}:")
    print(f"  WKB 初值: ω_g = {omega_wkb.real:.4f} - {abs(omega_wkb.imag):.4f}i")
    print(f"  扫描 Re(ω) ∈ [{omega_scan[0]:.4f}, {omega_scan[-1]:.4f}]")

    # 扫描不同虚部偏移
    all_violations = []
    all_omegas = []

    for imag_offset in [-0.04, -0.02, 0.0, 0.02, 0.04]:
        test_omega = omega_wkb + 1j * imag_offset

        violations = []
        for omega in omega_scan:
            omega_test = complex(omega, test_omega.imag)

            try:
                M_mat = compute_monodromy(r_star_horizon, r_star_infinity, omega_test, l, M, 8000)
                bc = bc_violation_monodromy(M_mat, omega_test, M)
                violations.append((omega, bc, imag_offset))
            except:
                violations.append((omega, float('inf'), imag_offset))

        all_violations.extend(violations)

    # 找全局最小
    best = min(all_violations, key=lambda x: x[1])
    print(f"  最小 BC 违反: {best[1]:.6e} at Re(ω)={best[0]:.6f}, Im(ω)偏移={best[2]:+.4f}")

    # 精细扫描最小值附近
    fine_range = best[0] * 0.8, best[0] * 1.2
    fine_scan = np.linspace(fine_range[0], fine_range[1], 500)

    best_bc = float('inf')
    best_omega = None

    for omega in fine_scan:
        for imag_offset in [-0.01, 0.0, 0.01]:
            omega_test = complex(omega, omega_wkb.imag + imag_offset)

            try:
                M_mat = compute_monodromy(r_star_horizon, r_star_infinity, omega_test, l, M, 10000)
                bc = bc_violation_monodromy(M_mat, omega_test, M)

                if bc < best_bc:
                    best_bc = bc
                    best_omega = omega_test
            except:
                pass

    if best_omega is not None:
        print(f"  最佳: ω = ({best_omega.real:.8f} - {abs(best_omega.imag):.8f}i)")
        print(f"  BC 违反 = {best_bc:.6e}")
    else:
        print(f"  未找到有效解")
        best_omega = None

    return best_omega, best_bc

# ============================================================================
# 基准测试
# ============================================================================

known_qnm = {
    (2, 0): complex(0.37373134, -0.08896258),
    (2, 1): complex(0.37329352, -0.27458937),
    (2, 2): complex(0.37265595, -0.46975278),
    (3, 0): complex(0.59187029, -0.05853522),
    (3, 1): complex(0.58971841, -0.26880432),
    (4, 0): complex(0.75906205, -0.04402477),
}

print("\n" + "=" * 70)
print("Schwarzschild QNM — Shooting Method v14 (Monodromy)")
print("=" * 70)

results = []
t0 = time.time()

for (l, n), omega_ref in sorted(known_qnm.items()):
    t_start = time.time()
    omega_found, bc_viol = solve_qnm_shooting(l, n)

    if omega_found is not None:
        rel_err = abs(omega_found - omega_ref) / abs(omega_ref)
        status = "✓" if rel_err < 0.1 else "⚠"
        print(f"    {status} 相对误差 = {rel_err:.6f}")
    else:
        rel_err = None
        print(f"    ✗ 未找到")

    results.append((l, n, omega_found, bc_viol, rel_err, time.time() - t_start))

total_time = time.time() - t0

print("\n" + "=" * 70)
print("总结")
print("=" * 70)
print(f"{'(l,n)':<10} {'计算值':>30} {'BC违反':>12} {'误差':>10}")
print("-" * 65)

for l, n, omega, bc, err, t in results:
    if omega is not None:
        val = f"({omega.real:.6f} - {abs(omega.imag):.6f}i)"
        err_str = f"{err:.6f}" if err is not None else "N/A"
    else:
        val = "未找到"
        err_str = "N/A"
    print(f"({l},{n})  {val:>30} {bc:>12.6e} {err_str:>10}")

print(f"\n  总耗时: {total_time:.1f}s")
print("=" * 70)
