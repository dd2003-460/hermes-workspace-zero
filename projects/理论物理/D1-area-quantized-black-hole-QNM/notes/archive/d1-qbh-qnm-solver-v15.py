#!/usr/bin/env python3
"""
Schwarzschild QNM v15 — 2D Direct Optimization + Efficient Integration
======================================================================

**核心方法**：
1. 直接在 r 空间积分 Regge-Wheeler 方程（避免 r* 变换的数值误差）
2. 2D 优化搜索 (Re[ω], Im[ω])
3. 多起点策略确保找到全局最小

**BC 定义**：|Ψ' + iωΨ| / (|Ψ| + |Ψ'|)，在无穷远 r_max 评估
**QNM 条件**：BC_violation → 0
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import time

print(f"NumPy: {np.__version__}")
print("=" * 70)

def regge_wheeler_ode(r, y, omega, l, M):
    """Regge-Wheeler 方程写成二阶 ODE 系统"""
    rs = 2.0 * M
    f = 1.0 - rs / r
    V = f * l * (l + 1) / (r**2)
    
    dYdr = np.zeros(2, dtype=complex)
    dYdr[0] = y[1]
    dYdr[1] = -(omega**2 - V) * y[0]
    return dYdr

def bc_violation_at_inf(r_max, omega, l, M, r_horizon=None, verbose=False):
    """
    从视界附近积分到 r_max，计算 BC 违反
    视界初值：出射波 Ψ = (r - rs) * exp(-iωr*)
    """
    rs = 2.0 * M
    
    if r_horizon is None:
        r_horizon = rs * 1.005
    
    # 乌龟坐标
    def rstar(r):
        return r + rs * np.log(r/rs - 1)
    
    r_star_horizon = rstar(r_horizon)
    r_star_max = rstar(r_max)
    
    # 视界初值：出射波 exp(-iωr*)
    psi0 = np.exp(-1j * omega * r_star_horizon)
    dpsi0 = -1j * omega * psi0
    
    y0 = [psi0, dpsi0]
    
    # 积分范围
    r_evals = np.linspace(r_horizon, r_max, 3000)
    
    try:
        sol = solve_ivp(
            lambda r, y: regge_wheeler_ode(r, y, omega, l, M),
            [r_horizon, r_max],
            y0,
            method='RK45',
            t_eval=r_evals,
            rtol=1e-10,
            atol=1e-12,
            dense_output=True,
            max_step=0.05
        )
    except:
        return 2.0, None
    
    psi_inf = sol.y[0, -1]
    dpsi_inf = sol.y[1, -1]
    
    bc_val = abs(dpsi_inf + 1j * omega * psi_inf)
    norm = abs(psi_inf) + abs(dpsi_inf) + 1e-30
    
    bc_viol = bc_val / norm
    
    if verbose:
        print(f"    BC 违反 = {bc_viol:.6e}")
        print(f"    |Ψ| = {abs(psi_inf):.2e}, |Ψ'| = {abs(dpsi_inf):.2e}")
    
    return bc_viol, (psi_inf, dpsi_inf)

def bc_objective(params, omega_ref, l, n, M, offset_log=False):
    """
    优化目标：|BC|^2
    params = [log|ω_R|, ω_I]  使用 log 提高实部优化稳定性
    """
    omega_R = np.exp(params[0])  # 保证 ω_R > 0
    omega_I = params[1]
    
    omega = complex(omega_R, omega_I)
    
    # 快速判断：如果 |ω| 偏离参考值太多，给大惩罚
    if abs(omega) > 3 * abs(omega_ref):
        return 10.0
    
    bc_viol, _ = bc_violation_at_inf(80.0, omega, l, M, verbose=False)
    return bc_viol

def find_qnm_v15(l, n, M=1.0):
    """
    使用多起点 Nelder-Mead 搜索 QNM
    """
    rs = 2.0 * M
    
    # 参考值（用于确定搜索范围）
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
        # WKB 估计
        omega_R = l * 0.5
        omega_I = -(0.089 + 0.186 * n)
        omega_ref = complex(omega_R, omega_I)
    
    print(f"\n  l={l}, n={n}:", end=" ")
    print(f"参考值 ω = ({omega_ref.real:.6f} - {abs(omega_ref.imag):.6f}i)", end="")
    
    # 多起点搜索
    best_bc = 2.0
    best_omega = None
    best_params = None
    
    # 定义起点集合：参考值附近的不同偏移
    starts = []
    for dr in [-0.02, 0, 0.02]:
        for di in [-0.01, 0, 0.01]:
            starts.append([np.log(abs(omega_ref.real + dr)), omega_ref.imag + di])
    
    for start_idx, start in enumerate(starts):
        result = minimize(
            bc_objective,
            start,
            args=(omega_ref, l, n, M),
            method='Nelder-Mead',
            options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': 200, 'adaptive': True}
        )
        
        if result.fun < best_bc:
            best_bc = result.fun
            best_params = result.x
            best_omega = complex(np.exp(result.x[0]), result.x[1])
    
    omega_found = best_omega
    bc_final = best_bc
    
    print(f"\n  搜索完成:", end=" ")
    if omega_found is not None:
        print(f"ω = ({omega_found.real:.8f} - {abs(omega_found.imag):.8f}i)")
        print(f"  BC 违反 = {bc_final:.6e}")
        
        if omega_ref is not None:
            rel_err = abs(omega_found - omega_ref) / abs(omega_ref)
            status = "✓" if rel_err < 0.05 else "⚠"
            print(f"  {status} 相对误差 = {rel_err:.6f}")
    else:
        print("未找到")
    
    return omega_found, bc_final

# ============================================================================
# 主程序
# ============================================================================

print("\nSchwarzschild QNM — v15 Direct Optimization")
print("2D Nelder-Mead 搜索 (5 起点)")
print("=" * 70)

known_qnm = {
    (2, 0): complex(0.37373134, -0.08896258),
    (2, 1): complex(0.37329352, -0.27458937),
    (2, 2): complex(0.37265595, -0.46975278),
    (3, 0): complex(0.59187029, -0.05853522),
    (3, 1): complex(0.58971841, -0.26880432),
    (4, 0): complex(0.75906205, -0.04402477),
}

results = []
t0 = time.time()

for key, omega_ref in sorted(known_qnm.items()):
    t_start = time.time()
    omega_found, bc = find_qnm_v15(*key)
    results.append((key, omega_found, bc, time.time() - t_start))

total_time = time.time() - t0

print("\n" + "=" * 70)
print("总结")
print("=" * 70)
print(f"{'(l,n)':<10} {'计算值':>30} {'BC违反':>12} {'误差':>10} {'耗时':>6}")
print("-" * 70)

for (l, n), omega, bc, t in results:
    if omega is not None:
        val = f"({omega.real:.6f} - {abs(omega.imag):.6f}i)"
        rel_err = abs(omega - known_qnm[(l,n)]) / abs(known_qnm[(l,n)])
        err_str = f"{rel_err:.6f}"
    else:
        val = "未找到"
        err_str = "N/A"
    
    status = "✓" if omega is not None and abs(omega - known_qnm[(l,n)]) / abs(known_qnm[(l,n)]) < 0.05 else "⚠"
    print(f"{status} ({l},{n})  {val:>30} {bc:>12.6e} {err_str:>10} {t:6.1f}s")

print(f"\n总耗时: {total_time:.1f}s")
print("=" * 70)
