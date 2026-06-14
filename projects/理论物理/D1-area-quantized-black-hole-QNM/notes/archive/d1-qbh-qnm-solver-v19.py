#!/usr/bin/env python3
"""
Schwarzschild QNM v19 — FDTD 时间域求解 + FFT
=============================================================

**修正（v18 → v19）**：
1. 正确的 Regge-Wheeler 势: V = f(r)[l(l+1)/r² - 6M/r³]
2. 吸收入射边界条件 (sponge layer, 非反射 Neumann)
3. 纯实数初值条件 (Gaussian + zero velocity)，标准做法
4. 记录远场信号并做 FFT 提取 QNM 频率
"""

import numpy as np
from scipy.interpolate import interp1d
import time, os

print("NumPy:", np.__version__)
print("=" * 70)

# ============================================================================
# 物理参数
# ============================================================================
M = 1.0
rs = 2.0 * M
l = 2  # 引力微扰最低多极子

# ============================================================================
# 构建 r → r* 映射
# ============================================================================
r_horizon = rs * 1.0001
r_max = 200.0 * M
N_r = 5000
r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_r)

# tortoise 坐标: r* = r + 2M ln(r/2M - 1)
r_star_grid = r_grid + rs * np.log(r_grid / rs - 1.0)

# ============================================================================
# 正确的 Regge-Wheeler 势: V = f(r)[l(l+1)/r² - 6M/r³]
# ============================================================================
f_grid = 1.0 - rs / r_grid
V_l2_term = l * (l + 1) / (r_grid * r_grid)
V_6M_term = 6.0 * M / (r_grid ** 3)
V_lw_grid = f_grid * (V_l2_term - V_6M_term)  # <-- 修正

r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic', fill_value='extrapolate')
V_interp = interp1d(r_star_grid, V_lw_grid, kind='cubic', fill_value='extrapolate')

print(f"r 范围: [{r_horizon:.6f}, {r_max:.1f}]")
print(f"r* 范围: [{r_star_grid[0]:.1f}, {r_star_grid[-1]:.1f}]")
V_peak = np.max(V_lw_grid)
V_peak_idx = np.argmax(V_lw_grid)
print(f"V(r*) 最大值 = {V_peak:.6f} at r* = {r_star_grid[V_peak_idx]:.2f}, r = {r_grid[V_peak_idx]:.2f}M")

# ============================================================================
# 均匀 r* 网格
# ============================================================================
rstar_min = r_star_grid[0] - 10
rstar_max = r_star_grid[-1] + 30
N_rstar = 4000
drstar = (rstar_max - rstar_min) / N_rstar
rstar_grid = np.linspace(rstar_min, rstar_max, N_rstar + 1)
V_grid = V_interp(rstar_grid)

print(f"\nr* 网格: [{rstar_min:.1f}, {rstar_max:.1f}]")
print(f"网格点数: {N_rstar + 1}, drstar = {drstar:.6f}")

# ============================================================================
# 时间参数 (CFL < 1)
# ============================================================================
dt = drstar * 0.95  # 接近 CFL 极限以加快速度
dt2 = dt * dt
T_total = 800.0
N_time = int(T_total / dt)

print(f"\n时间参数:")
print(f"dt = {dt:.6f}, drstar = {drstar:.6f}, CFL = {dt/drstar:.3f}")
print(f"T_total = {T_total}, N_time = {N_time}")

# ============================================================================
# 初始条件: Gaussian 波包 (纯实数)
# ============================================================================
V_peak_pos = rstar_grid[V_peak_idx]
sigma = 4.0

print(f"\n高斯波包中心: r* = {V_peak_pos:.2f}, σ = {sigma}")

psi_0 = np.exp(-(rstar_grid - V_peak_pos)**2 / (2 * sigma**2))

# 初速度 = 0 (标准做法: 波包分裂为向内+向外两部分)
# 如果设 dpsi/dt = -iω ψ (复数), 会导致虚数混入, 分析复杂化
dpsi_0 = np.zeros_like(psi_0)

# 用 leapfrog: psi_n_minus_1 = psi_0 - dt * dpsi_0
psi_n = psi_0.copy()  # 实数
psi_n_minus_1 = psi_0 - dt * dpsi_0  # 实数

# ============================================================================
# Sponge layer (吸收入射边界)
# ============================================================================
# 在左右边界各设置宽度 W_sponge 的阻尼层
# 阻尼系数: exp(-alpha * (x/W)^2)，在层内逐渐增大
W_sponge = int(N_rstar * 0.15)  # 15% 的网格
alpha = 2.0

sponge_left = np.ones(N_rstar + 1)
sponge_right = np.ones(N_rstar + 1)

for i in range(W_sponge):
    factor = (i / W_sponge) ** 2
    sponge_left[i] = np.exp(-alpha * factor)
    factor = ((W_sponge - 1 - i) / W_sponge) ** 2
    sponge_right[N_rstar - i] = np.exp(-alpha * factor)

print(f"Sponge layer: 左 {W_sponge} 点, 右 {W_sponge} 点, alpha={alpha}")

# ============================================================================
# 记录远场信号
# ============================================================================
record_idx = np.argmin(np.abs(rstar_grid - 80))  # 远场 r* ≈ 80
signal_record = np.zeros(N_time + 1)

# ============================================================================
# 时间积分 (leapfrog / Verlet)
# ============================================================================
print("\n开始时间积分...")
t0 = time.time()
nan_count = 0

for n in range(N_time):
    # d²ψ/dr*² (二阶中心差分, 内部点)
    d2psi = (psi_n[2:] - 2*psi_n[1:-1] + psi_n[:-2]) / drstar**2
    
    # RHS: d²ψ/dr*² - Vψ (内部点)
    rhs = d2psi - V_grid[1:-1] * psi_n[1:-1]
    
    # Leapfrog step
    psi_internal = 2*psi_n[1:-1] - psi_n_minus_1[1:-1] + dt2 * rhs
    
    # 新场
    psi_new = np.zeros_like(psi_n)
    psi_new[1:-1] = psi_internal
    
    # Sponge BC
    psi_new[0] = sponge_left[0] * psi_new[1]
    psi_new[-1] = sponge_right[-1] * psi_new[-2]
    
    # NaN 检查
    if np.any(np.isnan(psi_new)):
        nan_count += 1
        psi_new = np.nan_to_num(psi_new, nan=0, posinf=0, neginf=0)
        if nan_count <= 2:
            print(f"  ⚠ 时间步 {n} 出现 NaN")
    
    # 记录远场 (实部)
    signal_record[n] = psi_new[record_idx]
    
    # 更新
    psi_n_minus_1 = psi_n.copy()
    psi_n = psi_new.copy()
    
    if n % 2000 == 0:
        elapsed = time.time() - t0
        rms = np.abs(psi_n).std()
        print(f"  t={n*dt:.0f}/{T_total:.0f}, RMS={rms:.4f}, 耗时={elapsed:.1f}s")

total_time = time.time() - t0
print(f"\n积分完成: {total_time:.1f}s, NaN次数={nan_count}")

# ============================================================================
# FFT 分析
# ============================================================================
print("\n" + "=" * 70)
print("FFT 分析")
print("=" * 70)

# 去掉前 20% 的瞬态信号
start_skip = int(N_time * 0.2)
signal_cut = signal_record[start_skip:]
T_cut = len(signal_cut) * dt

window = np.hanning(len(signal_cut))
signal_windowed = signal_cut * window

N_fft = len(signal_windowed)
fft_vals = np.fft.rfft(signal_windowed)
freqs = np.fft.rfftfreq(N_fft, dt)
power_spectrum = np.abs(fft_vals)**2
power_spectrum /= np.max(power_spectrum)

from scipy.signal import find_peaks
peaks, props = find_peaks(power_spectrum, height=0.02, distance=20)

print(f"\n找到 {len(peaks)} 个谱峰 (跳过前 {start_skip} 步瞬态):")
print(f"{'峰号':<6} {'频率':>12}")
print("-" * 20)
for i, peak in enumerate(peaks[:15]):
    print(f"{i:<6} {freqs[peak]:>12.6f}")

# ============================================================================
# 与理论 QNM 对比
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

print(f"\n(l,n)   理论 ω_R        最近峰值         相对误差")
print("-" * 55)

for (l_q, n_q), (theory_R, theory_I) in sorted(known_qnm.items()):
    if len(peaks) > 0:
        # 找理论频率最近的峰值
        closest_idx = np.argmin(np.abs(freqs[peaks] - theory_R))
        measured_R = freqs[peaks[closest_idx]]
        error = abs(measured_R - theory_R) / theory_R
        marker = "✓" if error < 0.10 else "⚠"
        status = "通过" if error < 0.10 else "偏差较大"
    else:
        measured_R = np.nan
        error = np.nan
        marker = "?"
        status = "无峰值"
    
    print(f"{marker} ({l_q},{n_q})  {theory_R:>14.8f} {measured_R:>14.8f} {error:>10.4f}  {status}")

# ============================================================================
# 绘图
# ============================================================================
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 14))
    
    # 时域信号
    axes[0].plot(signal_record[:3000], 'b-', linewidth=0.5)
    axes[0].set_xlabel('Time step')
    axes[0].set_ylabel('ψ(r*=80, t)')
    axes[0].set_title(f'Far-field Signal (r* = 80, t = {min(3000*dt, T_total):.0f})', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    
    # 功率谱
    axes[1].plot(freqs, power_spectrum, 'b-', linewidth=0.8, label='Power Spectrum')
    for (l_q, n_q), (theory_R, theory_I) in known_qnm.items():
        marker_line = '--' if n_q == 0 else ':'
        alpha_val = 0.7 if n_q == 0 else 0.3
        axes[1].axvline(theory_R, color='r', linestyle=marker_line, alpha=alpha_val,
                       linewidth=1.2, label=f'QNM ({l_q},{n_q}) ω_R={theory_R:.3f}')
    axes[1].set_xlabel('Frequency', fontsize=12)
    axes[1].set_ylabel('Normalized Power', fontsize=12)
    axes[1].set_title('QNM Power Spectrum', fontsize=14)
    axes[1].set_xlim(0, 1.2)
    axes[1].legend(fontsize=8, loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    # 势函数
    axes[2].plot(rstar_grid, V_grid, 'k-', linewidth=1.5)
    axes[2].set_xlabel("r* (tortoise coordinate)", fontsize=12)
    axes[2].set_ylabel('V(r*)', fontsize=12)
    axes[2].set_title(f'Regge-Wheeler Potential (l={l}, V_peak={V_peak:.4f})', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    outdir = os.path.dirname(os.path.abspath(__file__)) + '/notes/04-benchmark'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, 'qnm_power_spectrum_v19.png'), dpi=150)
    print(f"\n功率谱图已保存: {outdir}/qnm_power_spectrum_v19.png")
except ImportError:
    print("\nmatplotlib 未安装，跳过绘图")

print("\n" + "=" * 70)
print("完成 v19")
print("=" * 70)
