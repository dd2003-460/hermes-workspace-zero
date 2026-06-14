#!/usr/bin/env python3
"""
Schwarzschild QNM v18 — 时间域积分 + FFT 方法（复数修正版）
=============================================================

**核心策略**：
1. 时间演化方程用复数psi：∂²ψ/∂t² = ∂²ψ/∂r*² - V(r*)ψ
2. 高斯波包激发，记录远场实部信号
3. FFT 提取 QNM 频率
"""

import numpy as np
from scipy.interpolate import interp1d
import time
import os

print("NumPy:", np.__version__)
print("=" * 70)

# ============================================================================
# 物理参数
# ============================================================================

M = 1.0  # 黑洞质量
rs = 2.0 * M  # 史瓦西半径

# ============================================================================
# 构建 r(r*) 映射（正算，避免牛顿法发散）
# ============================================================================

r_horizon = rs * 1.0001
r_max = 100.0 * M

N_r = 3000
r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_r)

# 正算 r* = r + 2M ln(r/2M - 1)
r_star_grid = r_grid + rs * np.log(r_grid / rs - 1.0)

# 插值函数
r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic', fill_value='extrapolate')

# 计算 V_l(r*) 网格，l=2 时 l(l+1)=6
f_grid = 1.0 - rs / r_grid
V_l2_grid = f_grid * 6.0 / (r_grid * r_grid)

print(f"r 范围: [{r_horizon:.6f}, {r_max:.1f}]")
print(f"r* 范围: [{r_star_grid[0]:.1f}, {r_star_grid[-1]:.1f}]")
print(f"V 最大值: {np.max(V_l2_grid):.6f} at r* = {r_star_grid[np.argmax(V_l2_grid)]:.2f}")

# ============================================================================
# 物理网格（r* 均匀）
# ============================================================================

rstar_min = r_star_grid[0] - 2
rstar_max = r_star_grid[-1] + 20
N_rstar = 2000
drstar = (rstar_max - rstar_min) / N_rstar

rstar_grid = np.linspace(rstar_min, rstar_max, N_rstar + 1)

# 插值 V(r*) 到 rstar_grid
V_interp = interp1d(r_star_grid, V_l2_grid, kind='cubic', fill_value='extrapolate')
V_grid = V_interp(rstar_grid)

print(f"\nr* 网格: [{rstar_min:.1f}, {rstar_max:.1f}]")
print(f"网格点数: {N_rstar + 1}")
print(f"drstar = {drstar:.4f}")
print(f"V(r*) 最大值 = {np.max(V_grid):.6f}")

# ============================================================================
# 有限差分方案
# ============================================================================

dt = 0.04  # 时间步长
dt2 = dt * dt
T_total = 400.0  # 总时间
N_time = int(T_total / dt)

print(f"\n时间参数:")
print(f"dt = {dt}, drstar = {drstar:.4f}")
print(f"CFL: dt/dr = {dt/drstar:.4f} (需 < 1)")
print(f"T_total = {T_total}, N_time = {N_time}")

# ============================================================================
# 初始化（复数）
# ============================================================================

V_peak_idx = np.argmax(V_grid)
V_peak_pos = rstar_grid[V_peak_idx]
sigma = 5.0

print(f"\n波包中心: r* = {V_peak_pos:.2f}")

# 高斯波包（实数）
psi_init = np.exp(-(rstar_grid - V_peak_pos)**2 / 2.0 / sigma**2)

# 初速度：匹配出射波（复数）
omega_guess = 0.4 - 0.1j
dpsi_init = -1j * omega_guess * psi_init

# 初始化：复数数组！
psi_n = psi_init.astype(complex) + 0j
psi_n_minus_1 = (psi_n - dt * dpsi_init).astype(complex)

# 记录远场信号
record_idx = np.argmin(np.abs(rstar_grid - 60))
signal_record = np.zeros(N_time + 1)

# ============================================================================
# 时间积分
# ============================================================================

print("\n开始时间积分...")
t0 = time.time()
nan_count = 0

for n in range(N_time):
    # ∂²ψ/∂r*² 二阶中心差分（复数）
    d2psi_dr2 = (psi_n[2:] - 2*psi_n[1:-1] + psi_n[:-2]) / drstar**2
    
    # 时间演化（复数）
    rhs = d2psi_dr2 - V_grid[1:-1] * psi_n[1:-1]
    psi_internal = 2*psi_n[1:-1] - psi_n_minus_1[1:-1] + dt2 * rhs
    
    # 边界条件
    psi_new = np.zeros_like(psi_n)
    psi_new[0] = psi_new[1]  # 左边界：零梯度
    psi_new[-1] = psi_new[-2]  # 右边界：零梯度
    psi_new[1:-1] = psi_internal
    
    # NaN 检查
    if np.any(np.isnan(psi_new)):
        nan_count += 1
        if nan_count < 3:
            print(f"  警告: 时间步 {n} 出现 NaN")
        # 截断 NaN
        psi_new = np.nan_to_num(psi_new, nan=0+0j, posinf=0+0j, neginf=0+0j)
    
    # 记录远场信号（实部）
    signal_record[n] = psi_new[record_idx].real
    
    # 更新
    psi_n_minus_1 = psi_n.copy()
    psi_n = psi_new.copy()
    
    if n % 500 == 0:
        elapsed = time.time() - t0
        rms = np.abs(psi_n).std()
        print(f"  t={n*dt:.0f}/{T_total:.0f}, RMS={rms:.4f}, 耗时={elapsed:.1f}s")

total_time = time.time() - t0
print(f"\n积分完成: {total_time:.1f}s, NaN次数={nan_count}")

# ============================================================================
# FFT 分析
# ============================================================================

print("\n进行 FFT 分析...")

# 汉宁窗
window = np.hanning(N_time + 1)
signal_windowed = signal_record * window

# FFT
N_fft = len(signal_windowed)
fft_vals = np.fft.rfft(signal_windowed)
freqs = np.fft.rfftfreq(N_fft, dt)
power_spectrum = np.abs(fft_vals)**2

# 归一化
power_spectrum /= np.max(power_spectrum)

# 找峰值
from scipy.signal import find_peaks

peaks, props = find_peaks(power_spectrum, height=0.05, distance=30)

print(f"\n找到 {len(peaks)} 个谱峰:")
print(f"{'峰号':<6} {'频率':>12}")
print("-" * 20)

for i, peak in enumerate(peaks[:10]):
    print(f"{i:<6} {freqs[peak]:>12.6f}")

# ============================================================================
# 与理论值对比
# ============================================================================

print("\n" + "=" * 70)
print("与理论 QNM 频率对比")
print("=" * 70)

known_qnm = {
    (2, 0): (0.37373134, 0.08896258),
    (2, 1): (0.37329352, 0.27458937),
    (2, 2): (0.37265595, 0.46975278),
    (3, 0): (0.59187029, 0.05853522),
    (3, 1): (0.58971841, 0.26880432),
    (4, 0): (0.75906205, 0.04402477),
}

print(f"\n测量 vs 理论频率 ω_R:")
print(f"{'(l,n)':<10} {'理论':>12} {'测量':>12} {'误差':>10}")
print("-" * 46)

for (l, n), (theory_R, theory_I) in sorted(known_qnm.items()):
    if len(peaks) > 0:
        closest_idx = np.argmin(np.abs(freqs[peaks] - theory_R))
        measured_R = freqs[peaks[closest_idx]]
        error = abs(measured_R - theory_R) / theory_R
        marker = "✓" if error < 0.1 else "⚠"
    else:
        measured_R = np.nan
        error = np.nan
        marker = "?"
    
    print(f"{marker} ({l},{n})  {theory_R:>12.6f} {measured_R:>12.6f} {error:>10.4f}")

# 绘制
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # 信号时域
    axes[0].plot(signal_record[:5000], 'b-', linewidth=0.5)
    axes[0].set_xlabel('Time step')
    axes[0].set_ylabel('ψ(r*=60, t)')
    axes[0].set_title('Far-field Signal (r* = 60)', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    
    # 功率谱
    axes[1].plot(freqs, power_spectrum, 'b-', linewidth=0.5, label='Power Spectrum')
    for (l, n), (theory_R, theory_I) in known_qnm.items():
        axes[1].axvline(theory_R, color='r', linestyle='--', alpha=0.5,
                       label=f'QNM ({l},{n})')
    axes[1].set_xlabel('Frequency (Hz)', fontsize=12)
    axes[1].set_ylabel('Normalized Power', fontsize=12)
    axes[1].set_title('QNM Power Spectrum', fontsize=14)
    axes[1].set_xlim(0, 1.0)
    axes[1].legend(fontsize=8, loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    outdir = '/Users/a1-6/Desktop/workspace/projects/理论物理/D1-area-quantized-black-hole-QNM/notes/04-benchmark'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, 'qnm_power_spectrum_v18.png'), dpi=150)
    print(f"\n功率谱图已保存: {outdir}/qnm_power_spectrum_v18.png")
except ImportError:
    print("\nmatplotlib 未安装，跳过绘图")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)
