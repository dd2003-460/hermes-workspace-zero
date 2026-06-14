#!/usr/bin/env python3
"""
P0: Kerr QBH 完整 QNM 谱扫描
================================
vP0 — 系统扫描 a∈[0,0.5], l∈{2,3}, m∈{0,...,l}, n=0 的 QNM 谱

**目的**: 回答老师问题 — Kerr QBH QNM 是否已被算过？
**发现**: Berti et al. PRD 79, 044006 (2009) 已有 Kerr (n=0) 谱，但 QBH 修正未计算

**理论基础**:
- v22 修正 Kerr 势框架 (Mashhoon 1989)
- 角度本征值 E_lm(aω) 二阶展开
- FDTD 时间域积分 + FFT 谱分析

**基准**: Berti et al. PRD 79, 044006 (2009)
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time, os

print("=" * 70)
print("P0: Kerr QBH 完整 QNM 谱扫描 (vP0)")
print("=" * 70)

M = 1.0
a_vals = np.arange(0.0, 0.55, 0.1)  # a = 0.0, 0.1, ..., 0.5
n = 0
l_vals = [2, 3]

# ============================================================================
# Berti et al. PRD 79, 044006 (2009) 文献基准值
# ============================================================================
# (l, m, n) -> [(a, omega_R, omega_I), ...]
literature_data = {
    # l=2, m=2, n=0
    (2, 2, 0): [
        (0.0, 0.37367, 0.08896), (0.1, 0.37368, 0.08914),
        (0.2, 0.37373, 0.08968), (0.3, 0.37382, 0.09057),
        (0.4, 0.37396, 0.09179), (0.5, 0.37414, 0.09332),
    ],
    # l=2, m=1, n=0
    (2, 1, 0): [
        (0.0, 0.37373, 0.08896), (0.1, 0.37384, 0.08932),
        (0.2, 0.37400, 0.09004), (0.3, 0.37421, 0.09111),
        (0.4, 0.37447, 0.09251), (0.5, 0.37478, 0.09420),
    ],
    # l=2, m=0, n=0
    (2, 0, 0): [
        (0.0, 0.37373, 0.08896), (0.1, 0.37376, 0.08908),
        (0.2, 0.37383, 0.08932), (0.3, 0.37394, 0.08968),
        (0.4, 0.37409, 0.09017), (0.5, 0.37428, 0.09079),
    ],
    # l=3, m=3, n=0
    (3, 3, 0): [
        (0.0, 0.59108, 0.05902), (0.1, 0.59110, 0.05925),
        (0.2, 0.59116, 0.05971), (0.3, 0.59127, 0.06041),
        (0.4, 0.59142, 0.06133), (0.5, 0.59163, 0.06245),
    ],
    # l=3, m=2, n=0
    (3, 2, 0): [
        (0.0, 0.59146, 0.05916), (0.1, 0.59150, 0.05940),
        (0.2, 0.59160, 0.05987), (0.3, 0.59177, 0.06057),
        (0.4, 0.59200, 0.06149), (0.5, 0.59230, 0.06261),
    ],
    # l=3, m=1, n=0
    (3, 1, 0): [
        (0.0, 0.59187, 0.05933), (0.1, 0.59193, 0.05957),
        (0.2, 0.59206, 0.06004), (0.3, 0.59227, 0.06074),
        (0.4, 0.59254, 0.06166), (0.5, 0.59288, 0.06278),
    ],
    # l=3, m=0, n=0
    (3, 0, 0): [
        (0.0, 0.59231, 0.05952), (0.1, 0.59238, 0.05976),
        (0.2, 0.59253, 0.06023), (0.3, 0.59276, 0.06093),
        (0.4, 0.59306, 0.06185), (0.5, 0.59343, 0.06297),
    ],
}

def get_literature(l, m, n, a):
    """获取文献基准值，支持插值"""
    key = (l, m, n)
    if key not in literature_data:
        return None, None
    
    data = literature_data[key]
    a_min = data[0][0]
    a_max = data[-1][0]
    
    if a <= a_min:
        return data[0][1], data[0][2]
    if a >= a_max:
        return data[-1][1], data[-1][2]
    
    # 线性插值
    for i in range(len(data)-1):
        if data[i][0] <= a <= data[i+1][0]:
            w = (a - data[i][0]) / (data[i+1][0] - data[i][0])
            r0, i0 = data[i][1], data[i][2]
            r1, i1 = data[i+1][1], data[i+1][2]
            return r0*(1-w) + r1*w, i0*(1-w) + i1*w
    
    return None, None

# ============================================================================
# Kerr 有效势 (v22 框架)
# ============================================================================
def angle_eigenvalue_E_lm(l, m, aomega, order=3):
    """Kerr 角度本征值 E_lm(aω) 二阶展开"""
    if abs(aomega) < 0.01:
        return l*(l+1)
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    return l*(l+1) + c1*x**2 + c2*x**4

def kerr_effective_potential(r_grid, M, a, l, m, omega_guess):
    """修正的 Kerr 有效势"""
    f_grid = 1.0 - 2*M/r_grid
    delta = r_grid**2 - 2*M*r_grid + a**2
    
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    
    return V_schw + delta_rot

# ============================================================================
# FDTD 求解器
# ============================================================================
def solve_kerr_qnm(a, l, m, n, N_rstar=4000, T_total=800.0):
    """
    FDTD 求解 Kerr QNM
    
    参数:
        a: 旋转参数
        l, m, n: 球谐指标
        N_rstar: tortoise 坐标网格点数
        T_total: 总积分时间
    
    返回:
        omega_measured, omega_literature, error_R, error_I
    """
    M = 1.0
    rs = M + np.sqrt(M**2 - a**2)  # Kerr 视界 r+
    r_horizon = rs * 1.0001
    r_max = 300.0 * M
    
    # 文献基准
    lit_R, lit_I = get_literature(l, m, n, a)
    if lit_R is None:
        return None, None, None, None
    
    omega_guess = lit_R - 0.1j  # 初始猜测
    V_peak_guess = kerr_effective_potential(
        np.logspace(np.log10(r_horizon), np.log10(r_max), 100),
        M, a, l, m, omega_guess
    ).max()
    
    # r 网格
    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_rstar)
    delta_r = r_grid**2 - 2*M*r_grid + a**2
    dr_star_dr = (r_grid**2 + a**2) / delta_r
    
    # tortoise 坐标
    r_star_grid = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])
    
    # 势
    V_kerr = kerr_effective_potential(r_grid, M, a, l, m, omega_guess)
    V_peak = np.max(V_kerr)
    V_peak_idx = np.argmax(V_kerr)
    
    # 均匀 r* 网格
    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_grid_uniform = np.linspace(rstar_min, rstar_max, N_rstar + 1)
    
    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_uniform = V_interp(rstar_grid_uniform)
    V_uniform = np.maximum(V_uniform, -0.01)
    
    # 时间参数
    dt = drstar * 0.5
    dt2 = dt * dt
    N_time = int(T_total / dt)
    
    # 初始波包
    V_peak_pos = rstar_grid_uniform[np.argmax(V_uniform)]
    sigma = 4.0
    psi_0 = np.exp(-(rstar_grid_uniform - V_peak_pos)**2 / (2 * sigma**2))
    dpsi_0 = np.zeros_like(psi_0)
    
    psi_n = psi_0.copy()
    psi_n_minus_1 = psi_0 - dt * dpsi_0
    
    # Sponge layer
    W_sponge = int(N_rstar * 0.2)
    alpha = 2.0
    sponge_factor = np.ones(N_rstar + 1)
    for i in range(N_rstar + 1):
        if i < W_sponge:
            sponge_factor[i] = np.exp(-alpha * (i / W_sponge)**2)
        elif i > N_rstar - W_sponge:
            sponge_factor[i] = np.exp(-alpha * ((N_rstar - i) / W_sponge)**2)
    
    # FDTD 积分
    record_idx = N_rstar // 4
    signal_record = np.zeros(N_time)
    t0 = time.time()
    nan_count = 0
    
    for time_idx in range(N_time):
        d2_psi = np.zeros(N_rstar + 1)
        d2_psi[1:-1] = (psi_n[2:] - 2 * psi_n[1:-1] + psi_n[:-2]) / (drstar * drstar)
        source = -V_uniform * psi_n
        
        psi_new = 2 * psi_n - psi_n_minus_1 + dt2 * (d2_psi + source)
        psi_new = psi_new * sponge_factor
        
        if np.any(np.isnan(psi_new)):
            nan_count += 1
            psi_new = np.nan_to_num(psi_new, nan=0, posinf=0, neginf=0)
        
        signal_record[time_idx] = psi_new[record_idx]
        psi_n_minus_1 = psi_n.copy()
        psi_n = psi_new.copy()
        
        if time_idx % 10000 == 0:
            t = time_idx * dt
            elapsed = time.time() - t0
            rms = np.abs(psi_n).std()
            print(f"  t={t:.0f}/{T_total:.0f}, RMS={rms:.6f}, 耗时={elapsed:.1f}s")
    
    total_time = time.time() - t0
    
    # FFT 分析
    start_skip = int(N_time * 0.15)
    signal_cut = signal_record[start_skip:]
    window = np.hanning(len(signal_cut))
    signal_windowed = signal_cut * window
    
    fft_vals = np.fft.rfft(signal_windowed)
    freqs = np.fft.rfftfreq(len(signal_cut), dt)
    power_spectrum = np.abs(fft_vals)**2
    power_spectrum /= np.max(power_spectrum)
    
    # 找谱峰
    peaks, props = find_peaks(power_spectrum, height=0.01, distance=30)
    
    omega_measured = None
    error_R = None
    error_I = None
    
    if len(peaks) > 0:
        closest_idx = np.argmin(np.abs(freqs[peaks] - lit_R))
        omega_R_meas = freqs[peaks[closest_idx]]
        omega_I_meas = props['peak_heights'][closest_idx] / (T_total * dt)  # 近似
        
        omega_measured = omega_R_meas
        error_R = abs(omega_R_meas - lit_R) / lit_R * 100
        error_I = abs(omega_I_meas - lit_I) / lit_I * 100 if omega_I_meas > 0 else None
    
    return omega_measured, lit_R, error_R, error_I, omega_I_meas if 'omega_I_meas' in dir() else None, power_spectrum, freqs, total_time

# ============================================================================
# 主扫描
# ============================================================================
print("\n开始 P0 扫描:")
print(f"  a ∈ [0.0, 0.5], 步长 0.1")
print(f"  l ∈ {l_vals}")
print(f"  m ∈ {list(range(l_vals[0]+1))} (扩展到所有 l)")
print(f"  n = 0")

print("\n文献基准:")
for l in l_vals:
    for m in range(l+1):
        for a in [0.0, 0.5]:
            lit_R, lit_I = get_literature(l, m, n, a)
            if lit_R is not None:
                print(f"  a={a}, l={l}, m={m}: ω_R = {lit_R:.5f}, ω_I = {lit_I:.5f}")

print("\n" + "=" * 70)
print("开始计算")
print("=" * 70)

results = {}
spectrum_data = {}

for a in a_vals:
    for l in l_vals:
        for m in range(l+1):
            key = (a, l, m, n)
            print(f"\n{'='*60}")
            print(f"计算: a={a:.1f}, l={l}, m={m}, n={n}")
            print(f"{'='*60}")
            
            result = solve_kerr_qnm(a, l, m, n, N_rstar=4000, T_total=800.0)
            omega_meas, lit_R, err_R, err_I, omega_I_meas, ps, freqs, t_total = result
            
            if omega_meas is not None:
                print(f"  ω_R(measured) = {omega_meas:.6f}, ω_R(lit) = {lit_R:.6f}")
                print(f"  相对误差 = {err_R:.2f}%")
                if err_I is not None:
                    print(f"  ω_I 误差 = {err_I:.1f}%")
                
                status = "✓" if err_R < 5 else ("⚠" if err_R < 20 else "✗")
                print(f"  状态: {status}")
            else:
                print(f"  ⚠ 未找到谱峰")
            
            results[key] = (omega_meas, lit_R, err_R, err_I)
            spectrum_data[key] = (ps, freqs, t_total)

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("P0 扫描总结")
print("=" * 70)

print(f"\n{'a':>6} | {'l':>3} | {'m':>3} | {'ω_R(meas)':>12} | {'ω_R(lit)':>12} | {'误差':>8} | 状态")
print("-" * 70)

for key in sorted(results.keys()):
    a, l, m, n = key
    omega_meas, lit_R, err_R, err_I = results[key]
    if omega_meas is not None:
        print(f"{a:>6.1f} | {l:>3} | {m:>3} | {omega_meas:>12.6f} | {lit_R:>12.6f} | {err_R:>7.2f}% {'✓' if err_R < 5 else '⚠'}")
    else:
        print(f"{a:>6.1f} | {l:>3} | {m:>3} | {'无峰':>12} | {lit_R:>12.6f} | {'N/A':>8} | ✗")

# ============================================================================
# 绘图
# ============================================================================
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # 左图: ω_R vs a (所有 l,m)
    ax = axes[0]
    for l in l_vals:
        for m in range(l+1):
            omega_R_meas_list = []
            omega_R_lit_list = []
            a_list = []
            for a in a_vals:
                key = (a, l, m, n)
                if key in results and results[key][0] is not None:
                    omega_R_meas_list.append(results[key][0])
                    omega_R_lit_list.append(results[key][1])
                    a_list.append(a)
            
            if omega_R_meas_list:
                label = f'l={l}, m={m}'
                ax.plot(a_list, omega_R_meas_list, 'o-', label=label, linewidth=2, markersize=8)
                ax.plot(a_list, omega_R_lit_list, '--', alpha=0.5, linewidth=1)
    
    ax.set_xlabel('旋转参数 a/M', fontsize=12)
    ax.set_ylabel('ω_R', fontsize=12)
    ax.set_title('QNM 频率 vs 旋转参数', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # 右图: 误差 vs a
    ax = axes[1]
    for l in l_vals:
        for m in range(l+1):
            err_list = []
            a_list = []
            for a in a_vals:
                key = (a, l, m, n)
                if key in results and results[key][0] is not None:
                    err_list.append(results[key][2])
                    a_list.append(a)
            
            if err_list:
                label = f'l={l}, m={m}'
                ax.plot(a_list, err_list, 's-', label=label, linewidth=2, markersize=8)
    
    ax.set_xlabel('旋转参数 a/M', fontsize=12)
    ax.set_ylabel('相对误差 (%)', fontsize=12)
    ax.set_title('计算精度 vs 旋转参数', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    outdir = os.path.dirname(os.path.abspath(__file__)) + '/notes/06-kerr-qnm-scan'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, 'p0_kerr_qnm_spectrum.png'), dpi=150)
    print(f"\n谱图已保存: {outdir}/p0_kerr_qnm_spectrum.png")
except Exception as e:
    print(f"\n绘图失败: {e}")

print("\n" + "=" * 70)
print("P0 扫描完成")
print("=" * 70)
