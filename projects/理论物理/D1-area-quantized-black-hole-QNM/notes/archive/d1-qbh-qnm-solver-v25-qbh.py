#!/usr/bin/env python3
"""
Kerr QNM v25 — 引入反射率边界条件 (I-5: 面积量子化修正)
============================================================

**基础**: 复用于v22的FDTD框架（统一网格架构）
**新增**:
  1. 反射率边界条件: 左边界 psi[0] = R * psi[1]
  2. 扫描 R in {0, 1e-30, 1e-20, 1e-10, 1e-6, 1e-3, 0.01, 0.1}
  3. 测量 QNM 频率偏移 delta_omega/omega

**物理意义**:
- R=0: 经典黑洞，纯吸收
- R>0: QBH，视界处有反射（面积量子化修正）

**理论参考**:
- Maggiore PRC 76, 064027 (2007) — 面积量子化
- Agullo PRC 101, 064053 (2020) — 反射率边界条件
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
import time, os

print("=" * 70)
print("Kerr QNM v25 — 面积量子化修正 (反射率边界条件)")
print("=" * 70)

M = 1.0
a_val = 0.5  # 只在 a=0.5 下计算
l, m, n = 2, 2, 0

# Kerr QNM 文献基准 (Berti et al. PRD 79, 044006)
lit_R, lit_I = 1.5251, 0.1031
print(f"\n文献基准 (Berti 2009, a=0.5, l=2,m=2,n=0):")
print(f"  omega_R = {lit_R:.6f}, omega_I = {lit_I:.6f}")

# ============================================================================
# 修正的 Kerr 有效势 (v22)
# ============================================================================
def angle_eigenvalue_E_lm(l, m, aomega, order=3):
    if abs(aomega) < 0.01:
        return l*(l+1)
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    return l*(l+1) + c1*x**2 + c2*x**4

def kerr_effective_potential(r_grid, M, a, l, m, omega_guess):
    f_grid = 1.0 - 2*M/r_grid
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    return V_schw + delta_rot

# ============================================================================
# 反射率边界条件求解器 (基于 v22 网格架构)
# ============================================================================
def solve_qnm_with_reflection(r_horizon, r_max, N_rstar, omega_guess, R_value, T_total=1200.0):
    """
    带反射率边界条件的 FDTD 求解
    
    左边界条件:
    - 经典黑洞 (R=0): psi[0] = 0 (纯吸收)
    - QBH (R>0): psi[0] = R * psi[1] (部分反射)
    
    R_value: 反射率, R in [0, 1]
    """
    a = 0.5
    print(f"    N_rstar={N_rstar}, R={R_value:.2e}")
    
    # 1. 非均匀 r 网格
    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_rstar)
    delta_r = r_grid**2 - 2*M*r_grid + a**2
    dr_star_dr = (r_grid**2 + a**2) / delta_r
    
    # 2. tortoise 坐标
    r_star_grid = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])
    
    # 3. Kerr 有效势
    V_kerr = kerr_effective_potential(r_grid, M, a, l, m, omega_guess)
    
    V_peak = np.max(V_kerr)
    V_peak_idx = np.argmax(V_kerr)
    print(f"    V_max = {V_peak:.6f}, at r={r_grid[V_peak_idx]:.2f}, r*={r_star_grid[V_peak_idx]:.2f}")
    
    # 4. 插值到均匀 r* 网格
    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_grid_uniform = np.linspace(rstar_min, rstar_max, N_rstar + 1)
    
    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_uniform = V_interp(rstar_grid_uniform)
    V_uniform = np.maximum(V_uniform, -0.01)  # clip 负值
    
    # 5. 时间参数
    dt = drstar * 0.5
    dt2 = dt * dt
    N_time = int(T_total / dt)
    
    print(f"    dt={dt:.6f}, N_time={N_time}, T_total={T_total}")
    
    # 6. 初始高斯波包
    V_peak_pos = rstar_grid_uniform[np.argmax(V_uniform)]
    sigma = 4.0
    psi_0 = np.exp(-(rstar_grid_uniform - V_peak_pos)**2 / (2 * sigma**2))
    dpsi_0 = np.zeros_like(psi_0)
    
    psi_n = psi_0.copy()
    psi_n_minus_1 = psi_0 - dt * dpsi_0
    
    # 7. Sponge layer
    W_sponge = int(N_rstar * 0.2)
    alpha = 2.0
    sponge_factor = np.ones(N_rstar + 1)
    for i in range(N_rstar + 1):
        if i < W_sponge:
            sponge_factor[i] = np.exp(-alpha * (i / W_sponge)**2)
        elif i > N_rstar - W_sponge:
            sponge_factor[i] = np.exp(-alpha * ((N_rstar - i) / W_sponge)**2)
    
    # 8. FDTD 积分 (带反射率边界条件)
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
        
        # === 反射率边界条件 ===
        if R_value == 0:
            psi_new[0] = 0.0  # 纯吸收
        else:
            psi_new[0] = R_value * psi_new[1]  # 部分反射
        
        if np.any(np.isnan(psi_new)):
            nan_count += 1
            psi_new = np.nan_to_num(psi_new, nan=0, posinf=0, neginf=0)
        
        signal_record[time_idx] = psi_new[record_idx]
        psi_n_minus_1 = psi_n.copy()
        psi_n = psi_new.copy()
        
        if time_idx % 5000 == 0:
            t = time_idx * dt
            elapsed = time.time() - t0
            rms = np.abs(psi_n).std()
            print(f"    t={t:.0f}/{T_total:.0f}, RMS={rms:.4f}, 耗时={elapsed:.1f}s")
    
    total_time = time.time() - t0
    print(f"    积分完成: {total_time:.1f}s, NaN次数={nan_count}")
    
    # 9. FFT 分析
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
    
    print(f"    找到 {len(peaks)} 个谱峰")
    for i, peak in enumerate(peaks[:5]):
        print(f"      峰{i}: freq = {freqs[peak]:.6f}, power = {power_spectrum[peak]:.4f}")
    
    # 与基准对比
    measured_R = None
    error = None
    if len(peaks) > 0:
        closest_idx = np.argmin(np.abs(freqs[peaks] - lit_R))
        measured_R = freqs[peaks[closest_idx]]
        error = abs(measured_R - lit_R) / lit_R * 100
    
    return power_spectrum, freqs, peaks, measured_R, error, nan_count

# ============================================================================
# 主循环: 扫描反射率
# ============================================================================
print(f"\n{'='*70}")
print(f"扫描反射率 R (a/M = {a_val})")
print(f"{'='*70}")

rs = M + np.sqrt(M**2 - a_val**2)  # Kerr 视界 r+
r_horizon = rs * 1.0001
r_max = 400.0 * M

print(f"\n视界 r+ = {rs:.4f}M")

results = {}
spectrum_data = {}

for R in [0, 1e-30, 1e-20, 1e-10, 1e-6, 1e-3, 0.01, 0.1]:
    print(f"\n{'-'*50}")
    print(f"R = {R:.2e}")
    
    ps, freqs, pk, meas_R, err, nan_c = solve_qnm_with_reflection(
        r_horizon, r_max, 6000, lit_R, R, T_total=1200.0
    )
    
    results[R] = (meas_R, err, nan_c)
    spectrum_data[R] = (ps, freqs)
    
    status_str = ""
    if meas_R is not None:
        status_str = f"omega_R = {meas_R:.6f}, 误差 = {err:.2f}%"
    else:
        status_str = "未找到谱峰"
    print(f"  {status_str}")

# ============================================================================
# 总结: 频率偏移
# ============================================================================
print(f"\n{'='*70}")
print("I-5 结果总结: 频率偏移 delta_omega/omega")
print("="*70)

print(f"\n{'R':>12} | {'omega_R':>12} | {'delta_omega/omega':>18} | {'相对误差':>10} | 状态")
print("-" * 70)

for R, (meas_R, err, nan_c) in results.items():
    if meas_R is not None:
        delta_over = (meas_R - lit_R) / lit_R
        status = "OK" if abs(err) < 5 else ("WARN" if abs(err) < 20 else "FAIL")
        print(f"{R:>12.2e} | {meas_R:>12.6f} | {delta_over:>18.6e} | {err:>9.2f}% {status}")
    else:
        print(f"{R:>12.2e} | {'无峰':>12} | {'N/A':>18} | {'N/A':>10} | FAIL")

# ============================================================================
# 绘图
# ============================================================================
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左图: 功率谱对比
    ax = axes[0]
    colors = plt.cm.viridis(np.linspace(0, 0.9, len([0, 1e-30, 1e-20, 1e-10, 1e-6, 1e-3, 0.01, 0.1])))
    
    R_values = [0, 1e-30, 1e-20, 1e-10, 1e-6, 1e-3, 0.01, 0.1]
    for i, R in enumerate(R_values):
        ps, freqs = spectrum_data[R]
        ax.plot(freqs, ps, label=f'R={R:.2e}', color=colors[i], linewidth=0.8, alpha=0.7)
    
    ax.axvline(lit_R, color='r', linestyle='--', linewidth=2, label='理论 omega_R')
    ax.set_xlabel('Frequency', fontsize=12)
    ax.set_ylabel('Normalized Power', fontsize=12)
    ax.set_title('功率谱 vs 反射率', fontsize=12)
    ax.set_xlim(1.4, 1.7)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # 右图: delta_omega/omega vs R
    ax = axes[1]
    delta_vals = []
    R_plot = []
    for R in R_values:
        meas_R, err, nan_c = results[R]
        if meas_R is not None:
            delta_vals.append((meas_R - lit_R) / lit_R)
            R_plot.append(R)
    
    ax.semilogx(R_plot, delta_vals, 'bo-', linewidth=2, markersize=8)
    ax.axhline(0, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('反射率 R', fontsize=12)
    ax.set_ylabel(r'$\delta\omega/\omega$', fontsize=12)
    ax.set_title('频率偏移 vs 反射率', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    for i, (R, d) in enumerate(zip(R_plot, delta_vals)):
        ax.annotate(f'{d:.2e}', (R, d), textcoords="offset points", xytext=(5, 5), fontsize=7)
    
    plt.tight_layout()
    
    outdir = os.path.dirname(os.path.abspath(__file__)) + '/notes/08-i5-qbh-correction'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, 'qbh_frequency_shift_v25.png'), dpi=150)
    print(f"\n功率谱图已保存: {outdir}/qbh_frequency_shift_v25.png")
except Exception as e:
    print(f"\n绘图失败: {e}")

print("\n" + "="*70)
print("完成 v25 (面积量子化修正)")
print("="*70)
