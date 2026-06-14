#!/usr/bin/env python3
"""
Schwarzschild QNM v17 — 修复版 (r* 插值 + Nelder-Mead 2D 优化)
===============================================================

**核心策略**：
1. 预计算 r(r*) 插值（直接 r 网格映射，无 Newton 反变换）
2. Nelder-Mead 2D 优化（~200 次函数评估）
3. r* ∈ [-20, 60]（标准 QNM 计算范围）

**验证基准**: Kokkotas & Schutz 1992 Table I
"""

import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import interp1d
import time
import warnings
warnings.filterwarnings('ignore')

print("NumPy:", np.__version__)
print("=" * 70)

# ============================================================================
# 预计算 r(r*) 插值
# ============================================================================

def build_r_star_map(M=1.0, N_grid=5000):
    """
    预计算 r → r* 的映射，构建反函数 r(r*) 插值
    
    r* = r + 2M ln(r/2M - 1)
    
    返回: (rstar_grid, r_of_rstar_interp, V_interp)
    """
    rs = 2.0 * M
    
    # r 从 horizon 附近到无穷远
    r_grid = np.logspace(np.log10(rs * 1.0001), np.log10(200.0 * M), N_grid)
    
    # 计算对应的 r*
    r_star_grid = r_grid + rs * np.log(r_grid / rs - 1.0)
    
    # 构建 r(r*) 的线性插值
    r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic', fill_value='extrapolate')
    
    # 构建 V(r*) 的插值
    f = 1.0 - rs / r_grid
    V_grid = f * r_grid  # V_l(r) = (1-2M/r) * l(l+1)/r^2, l=2: l(l+1)=6
    V_interp = interp1d(r_star_grid, V_grid, kind='cubic', fill_value='extrapolate')
    
    return r_of_rstar, V_interp

# ============================================================================
# 计算 V_l(r*)（含 l 参数）
# ============================================================================

def rw_potential_rstar_interp(rstar, l, V_l2_interp, M=1.0):
    """
    Regge-Wheeler 势 (l 相关的 V 值通过插值得到)
    V_l(r*) = (1-2M/r(r*)) * l(l+1)/r²
    V_l2_interp 是 l=2 的插值，V_l = V_l2 * l(l+1)/6
    """
    V_l2 = V_l2_interp(rstar)
    return V_l2 * l * (l + 1) / 6.0

# ============================================================================
# 向量化 RK4 积分
# ============================================================================

def integrate_rw_v17(omega, l, rstar_min, rstar_max, V_l_interp, h=0.01):
    """
    固定步长 RK4 积分
    
    Returns: (BC_violation, psi_inf, dpsi_inf)
    """
    n_steps = int((rstar_max - rstar_min) / h)
    
    # 视界初值：出射波
    psi = np.exp(-1j * omega * rstar_min)
    dpsi = -1j * omega * psi
    
    rstar = rstar_min
    
    for i in range(n_steps):
        V1 = rw_potential_rstar_interp(rstar, l, V_l_interp)
        k1_psi = h * dpsi
        k1_dpsi = -h * (omega**2 - V1) * psi
        
        V2 = rw_potential_rstar_interp(rstar + h/2, l, V_l_interp)
        psi_2 = psi + k1_psi/2
        dpsi_2 = dpsi + k1_dpsi/2
        k2_psi = h * dpsi_2
        k2_dpsi = -h * (omega**2 - V2) * psi_2
        
        V3 = rw_potential_rstar_interp(rstar + h/2, l, V_l_interp)
        psi_3 = psi + k2_psi/2
        dpsi_3 = dpsi + k2_dpsi/2
        k3_psi = h * dpsi_3
        k3_dpsi = -h * (omega**2 - V3) * psi_3
        
        V4 = rw_potential_rstar_interp(rstar + h, l, V_l_interp)
        psi_4 = psi + k3_psi
        dpsi_4 = dpsi + k3_dpsi
        k4_psi = h * dpsi_4
        k4_dpsi = -h * (omega**2 - V4) * psi_4
        
        psi += (k1_psi + 2*k2_psi + 2*k3_psi + k4_psi) / 6
        dpsi += (k1_dpsi + 2*k2_dpsi + 2*k3_dpsi + k4_dpsi) / 6
        rstar += h
    
    # BC 违反
    bc_val = abs(dpsi + 1j * omega * psi)
    norm = abs(psi) + abs(dpsi) + 1e-30
    bc_viol = bc_val / norm
    
    return bc_viol, psi, dpsi

# ============================================================================
# 优化目标
# ============================================================================

def bc_objective(params, omega_ref, l, V_l_interp, rstar_min, rstar_max, h):
    omega = complex(params[0], params[1])
    bc_viol, _, _ = integrate_rw_v17(omega, l, rstar_min, rstar_max, V_l_interp, h)
    return bc_viol

# ============================================================================
# 主求解
# ============================================================================

def solve_qnm_v17(l, n, M=1.0):
    rs = 2.0 * M
    
    # 参考值
    known_ref = {
        (2, 0): complex(0.37373134, -0.08896258),
        (2, 1): complex(0.37329352, -0.27458937),
        (2, 2): complex(0.37265595, -0.46975278),
        (3, 0): complex(0.59187029, -0.05853522),
        (3, 1): complex(0.58971841, -0.26880432),
        (4, 0): complex(0.75906205, -0.04402477),
    }
    
    omega_ref = known_ref.get((l, n))
    if omega_ref is None:
        omega_R = l * 0.5
        omega_I = -(0.089 + 0.186 * n)
        omega_ref = complex(omega_R, omega_I)
    
    print(f"\n  l={l}, n={n}:", end=" ")
    print(f"参考 ω = ({omega_ref.real:.6f} - {abs(omega_ref.imag):.6f}i)")
    
    # WKB 初值
    omega_WKB = complex(
        l * 0.5 - 0.149 * (n + 0.5)**0.616,
        -(0.089 + 0.186 * n)
    )
    
    # 预计算 r(r*) 和 V(r*) 插值
    t_build = time.time()
    _, V_interp = build_r_star_map(M, N_grid=5000)
    build_time = time.time() - t_build
    print(f"    V(r*) 预计算完成: {build_time*1000:.0f}ms")
    
    rstar_min, rstar_max = -20.0, 60.0
    h = 0.02
    
    # 多起点 Nelder-Mead
    best_bc = float('inf')
    best_omega = None
    
    starts = [
        [omega_WKB.real - 0.02, omega_WKB.imag],
        [omega_WKB.real, omega_WKB.imag],
        [omega_WKB.real + 0.02, omega_WKB.imag],
        [omega_WKB.real, omega_WKB.imag - 0.01],
        [omega_WKB.real, omega_WKB.imag + 0.01],
    ]
    
    for start in starts:
        result = minimize(
            bc_objective,
            start,
            args=(omega_ref, l, V_interp, rstar_min, rstar_max, h),
            method='Nelder-Mead',
            options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': 300, 'adaptive': True}
        )
        
        if result.fun < best_bc:
            best_bc = result.fun
            best_omega = complex(result.x[0], result.x[1])
    
    print(f"  最佳: ω = ({best_omega.real:.8f} - {abs(best_omega.imag):.8f}i)")
    print(f"  BC 违反 = {best_bc:.6e}")
    
    if omega_ref is not None:
        rel_err = abs(best_omega - omega_ref) / abs(omega_ref)
        status = "✓" if rel_err < 0.01 else "⚠"
        print(f"  {status} 相对误差 = {rel_err:.6f}")
    
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
print("Schwarzschild QNM — v17 (r* 插值 + Nelder-Mead)")
print("=" * 70)

results = []
t0 = time.time()

for (l, n), omega_ref in sorted(known_qnm.items()):
    t_start = time.time()
    omega_found, bc = solve_qnm_v17(l, n)
    results.append((l, n, omega_found, bc, time.time() - t_start))

total_time = time.time() - t0

print("\n" + "=" * 70)
print("总结")
print("=" * 70)
print(f"{'(l,n)':<10} {'计算值':>30} {'BC违反':>12} {'误差':>10} {'耗时':>6}")
print("-" * 70)

for l, n, omega, bc, t in results:
    if omega is not None:
        val = f"({omega.real:.6f} - {abs(omega.imag):.6f}i)"
        rel_err = abs(omega - known_qnm[(l,n)]) / abs(known_qnm[(l,n)])
        err_str = f"{rel_err:.6f}"
    else:
        val = "未找到"
        err_str = "N/A"
    
    status = "✓" if omega is not None and rel_err < 0.01 else "⚠"
    print(f"{status} ({l},{n})  {val:>30} {bc:>12.6e} {err_str:>10} {t:6.1f}s")

print(f"\n总耗时: {total_time:.1f}s")
print("=" * 70)
