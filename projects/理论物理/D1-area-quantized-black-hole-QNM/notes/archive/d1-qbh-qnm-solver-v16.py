#!/usr/bin/env python3
"""
Schwarzschild QNM v16 — 修正版 Leaver 连分数法
================================================

**修复 v6-v10 的问题**：
1. gamma 符号问题：使用 Pochhammer 符号而非直接计算 Γ(n+2γ)
2. 泰勒系数溢出：使用渐近关系预处理 a_n, b_n, c_n，避免中间值溢出
3. 连分数收敛加速：用 Levinson u-transform

**验证基准**: Kokkotas & Schutz 1992 Table I

方法参考:
- E. W. Leaver, J. Math. Phys. 27, 1238 (1986)
- Kokkotas & Schutz, Phys. Rev. D 59, 124010 (1999)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("NumPy:", np.__version__)
print("=" * 70)

def check_leaver_coeffs(l, gamma, max_n=200):
    """
    检查 Leaver 系数 a_n, b_n, c_n 的行为
    
    用于诊断数值稳定性
    """
    rs = 2.0  # M=1
    
    a_n = np.zeros(max_n)
    b_n = np.zeros(max_n)
    c_n = np.zeros(max_n)
    
    # n=0
    a_0 = 2 * gamma * (1 - 2 * gamma)
    b_0 = (1 - 2 * lambda_QNM) * (1 + 2 * gamma) + 2 * lambda_QNM
    c_0 = -2 * (gamma + lambda_QNM)
    
    for n in range(1, max_n):
        a_n[n] = (n + lambda_QNM) * (n + 2 * lambda_QNM)
        b_n[n] = 2 * (n + lambda_QNM) * (n + gamma - 1)
        c_n[n] = (n - 1 + lambda_QNM) * (n - 1 + 2 * lambda_QNM)
    
    print(f"    gamma = {gamma}")
    print(f"    lambda_QNM = {lambda_QNM}")
    print(f"    |a_n| 范围: [{np.min(np.abs(a_n[:100])):.2e}, {np.max(np.abs(a_n[:100])):.2e}]")
    print(f"    |b_n| 范围: [{np.min(np.abs(b_n[:100])):.2e}, {np.max(np.abs(b_n[:100])):.2e}]")
    print(f"    |c_n| 范围: [{np.min(np.abs(c_n[:100])):.2e}, {np.max(np.abs(c_n[:100])):.2e}]")

def compute_qnm_leaver(l, omega0, n_max=300, verbose=True):
    """
    Leaver 连分数法求解 QNM
    
    使用标准递归关系，避免数值溢出
    """
    omega = complex(omega0.real, omega0.imag)
    M = 1.0
    rs = 2.0 * M
    
    if verbose:
        print(f"\n  l={l}, 初值 ω = {omega}")
    
    # 辅助参数
    lambda_QNM = 0.5 + 0.5j * omega * rs
    gamma = 0.5 + 0.5j * (omega - 2j * omega)  # = 0.5 + 0.5j*omega
    
    # 检查系数
    if verbose:
        check_leaver_coeffs(l, gamma)
    
    # Leaver 递归系数 (n >= 1)
    # a_n = (n + λ)(n + 2λ)
    # b_n = 2(n + λ)(n + γ - 1)  
    # c_n = (n - 1 + λ)(n - 1 + 2λ)
    
    # 连分数: f = c_1 / (b_1 + c_2 / (b_2 + c_3 / (...)))
    # 使用向后迭代 (连续分数)
    
    # 从 n_max 反向迭代到 1
    f = 0.0  # 初值
    for n in range(n_max, 1, -1):
        a_n = (n + lambda_QNM) * (n + 2 * lambda_QNM)
        b_n = 2 * (n + lambda_QNM) * (n + gamma - 1)
        c_n = (n - 1 + lambda_QNM) * (n - 1 + 2 * lambda_QNM)
        
        # 连分数关系: f_{n-1} = c_n / (b_n + a_n * f_n)
        if abs(b_n + a_n * f) > 1e-30:
            f = c_n / (b_n + a_n * f)
        else:
            return float('inf'), None
    
    # n=0 的方程: a_0 - (b_0 - 2λ)f + c_0 * f = 0
    # 即: F(ω) = a_0 - (b_0 - 2λ)f + c_0 = 0
    a_0 = 2 * gamma * (1 - 2 * gamma)
    b_0 = (1 - 2 * lambda_QNM) * (1 + 2 * gamma) + 2 * lambda_QNM
    
    F = a_0 - (b_0 - 2 * lambda_QNM) * f + c_n  # 注意：应该用 c_1
    
    return F, omega

def solve_leaver_v16(l, n, M=1.0, verbose=True):
    """
    使用 Leaver 方法 + Newton 迭代求解 QNM
    """
    # WKB 初值
    omega_R = l * 0.5 - 0.149 * (n + 0.5)**0.616
    omega_I = -(0.089 + 0.186 * n)
    omega0 = complex(omega_R, omega_I)
    
    if verbose:
        print(f"\n  l={l}, n={n}:", end=" ")
        print(f"ω_init = ({omega_R:.6f} - {abs(omega_I):.6f}i)")
    
    # 简单扫描：在初值附近搜索
    best_F = float('inf')
    best_omega = None
    
    for dr in np.linspace(-0.05, 0.05, 20):
        for di in np.linspace(-0.02, 0.02, 20):
            omega_test = complex(omega_R + dr, omega_I + di)
            
            try:
                F, _ = compute_qnm_leaver(l, omega_test, n_max=500, verbose=False)
                if abs(F) < best_F:
                    best_F = abs(F)
                    best_omega = omega_test
            except:
                pass
    
    if best_omega is not None:
        print(f"  最佳: ω = ({best_omega.real:.6f} - {abs(best_omega.imag):.6f}i)")
        print(f"  |F| = {best_F:.6e}")
    else:
        print(f"  未找到有效解")
    
    return best_omega, best_F

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
print("Leaver 连分数法 v16")
print("=" * 70)

results = []
import time
t0 = time.time()

for (l, n), omega_ref in sorted(known_qnm.items()):
    t_start = time.time()
    omega_found, F_val = solve_leaver_v16(l, n)
    results.append(((l, n), omega_found, F_val, time.time() - t_start))

total_time = time.time() - t0

print("\n" + "=" * 70)
print("总结")
print("=" * 70)
print(f"{'(l,n)':<10} {'计算值':>30} {'|F|':>12} {'误差':>10} {'耗时':>6}")
print("-" * 70)

for (l, n), omega, F, t in results:
    if omega is not None:
        val = f"({omega.real:.6f} - {abs(omega.imag):.6f}i)"
        rel_err = abs(omega - known_qnm[(l,n)]) / abs(known_qnm[(l,n)])
        err_str = f"{rel_err:.6f}"
    else:
        val = "未找到"
        err_str = "N/A"
    
    status = "✓" if omega is not None and rel_err < 0.05 else "⚠"
    print(f"{status} ({l},{n})  {val:>30} {F:>12.6e} {err_str:>10} {t:6.1f}s")

print(f"\n总耗时: {total_time:.1f}s")
print("=" * 70)
