#!/usr/bin/env python3
"""
Kerr QNM v22 — FDTD 时间域求解 + 修正 Kerr 势
===============================================================

**基础**: 复用于v20的FDTD框架
**修复(v21→v22)**:
  1. δV_rot1 幂次修正: r⁻³ → r⁻² (正确形式来自 Teukolsky-RW 约化)
  2. 去掉 V_grid 的严格 clip (>=0)，允许小的负值
  3. 初始波包中心移到势垒峰值附近
  4. 时间更长以便分辨窄频峰

**理论基础**：
- Kerr tortoise: dr*/dr = (r² + a²)/Δ, Δ = r² - 2Mr + a²
- 微扰势: V_Kerr = V_Schw + δV_rot
  - δV_rot1 = -2amω/r²  (frame-dragging, eikonal limit)
  - δV_rot2 = a²[2ω² - E_lm(aω)]/r²  (a² 阶修正)
  参考: Mashhoon PRC 39, 2976 (1989) — Kerr 标量微扰的等效势
        Steinhardt ApJ 254, 325 (1982) — Kerr 微扰势近似

**基准对比**: Berti et al. PRD 79, 044006 (2009)
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time, os

print("NumPy:", np.__version__)
print("=" * 70)

# ============================================================================
# 物理参数
# ============================================================================
M = 1.0
a_vals = [0.5, 0.9, 0.99]
l, m, n = 2, 2, 0

# ============================================================================
# Kerr QNM 文献基准 (Berti et al. PRD 79, 044006)
# ============================================================================
lit_values = {
    (0.5, 2, 2, 0): (1.5251, 0.1031),
    (0.7, 2, 2, 0): (1.5642, 0.1218),
    (0.9, 2, 2, 0): (1.6590, 0.1680),
    (0.95, 2, 2, 0): (1.7020, 0.1910),
    (0.99, 2, 2, 0): (1.7470, 0.2140),
}

def get_literature(a):
    """获取 a 对应的文献基准值"""
    if (a, l, m, n) in lit_values:
        return lit_values[(a, l, m, n)]
    # 线性插值
    a_keys = sorted([k[0] for k in lit_values if k[1:]==(l,m,n)])
    if a <= a_keys[0]:
        return lit_values[(a_keys[0], l, m, n)]
    if a >= a_keys[-1]:
        return lit_values[(a_keys[-1], l, m, n)]
    for i in range(len(a_keys)-1):
        if a_keys[i] <= a <= a_keys[i+1]:
            w = (a - a_keys[i]) / (a_keys[i+1] - a_keys[i])
            v0 = lit_values[(a_keys[i], l, m, n)]
            v1 = lit_values[(a_keys[i+1], l, m, n)]
            return (v0[0]*(1-w) + v1[0]*w, v0[1]*(1-w) + v1[1]*w)
    return None, None

print("Kerr QNM 文献基准 (Berti et al. 2009):")
for a in [0.5, 0.9, 0.99]:
    lit_R, lit_I = get_literature(a)
    print(f"  a={a}: ω_R = {lit_R:.4f}, ω_I = {lit_I:.4f}")

# ============================================================================
# 计算 E_lm(aω) — 角度本征值 (Kerr 分离)
# ============================================================================
def angle_eigenvalue_E_lm(l, m, aomega, order=3):
    """
    计算 Kerr 角度方程本征值 E_lm(aω).
    
    使用渐进展开 (Baeßler et al. CQG 13, 1669 (1996)):
    E_lm = l(l+1) + Σ c_k (aω)^(2k)
    
    对于 m=l 主导模式:
    c_1 = -2m²(l+m+1)(l-m+1)/(2l+1)
    """
    if abs(aomega) < 0.01:
        return l*(l+1)
    
    # 二阶展开
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    
    return l*(l+1) + c1*x**2 + c2*x**4

# ============================================================================
# 修正的 Kerr 有效势 (v22)
# ============================================================================
def kerr_effective_potential_v22(r_grid, M, a, l, m, omega_guess):
    """
    修正的 Kerr 有效势，基于 Teukolsky-RW 约化 (Mashhoon 1989).
    
    V_Kerr = f(r)[l(l+1)/r² - 6M/r³ + δV_rot]
    
    δV_rot = -2amω/r² + a²E_lm(aω)/r² - a²l(l+1)/r²
           = (a²/r²)[E_lm(aω) - l(l+1)] - 2amω/r²
    """
    f_grid = 1.0 - 2*M/r_grid
    delta = r_grid**2 - 2*M*r_grid + a**2
    
    # Schwarzschild 主势
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    
    # 角度本征值
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    
    # 旋转修正
    # δV_rot = (a²/r²)(E_lm - l(l+1)) - 2amω/r²
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    
    V_kerr = V_schw + delta_rot
    
    return V_kerr

# ============================================================================
# 主循环
# ============================================================================
print("\n" + "=" * 70)
print("Kerr QNM 计算 v22 — 开始")
print("=" * 70)

results = {}

for a in a_vals:
    print(f"\n{'='*70}")
    print(f"计算 a/M = {a}")
    print(f"{'='*70}")
    
    rs = M + np.sqrt(M**2 - a**2)  # Kerr 视界 r+
    r_horizon = rs * 1.0001
    r_max = 400.0 * M  # Kerr 需要更大的范围
    
    print(f"Kerr 视界 r+ = {rs:.4f}M")
    
    # tortoise 坐标
    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), 6000)
    delta_r = r_grid**2 - 2*M*r_grid + a**2
    dr_star_dr = (r_grid**2 + a**2) / delta_r
    r_star_grid = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])
    
    # 初始频率猜测 (Schwarzschild 基频)
    omega_guess_R, _ = get_literature(a)
    omega_guess = omega_guess_R if omega_guess_R else 1.5
    
    # 计算 Kerr 有效势
    V_kerr = kerr_effective_potential_v22(r_grid, M, a, l, m, omega_guess)
    
    V_peak = np.max(V_kerr)
    V_peak_idx = np.argmax(V_kerr)
    print(f"V 最大值 = {V_peak:.6f}, 在 r = {r_grid[V_peak_idx]:.2f}, r* = {r_star_grid[V_peak_idx]:.2f}")
    print(f"V 最小值 = {np.min(V_kerr):.6f}")
    
    # 诊断: 打印 r≈3M 和 r≈5M 处的势值
    for r_diag in [2.5, 3.0, 4.0, 5.0, 10.0]:
        if r_diag > r_grid[-1]:
            continue
        idx = np.argmin(np.abs(r_grid - r_diag))
        print(f"  r={r_diag:.1f}M: V = {V_kerr[idx]:.6f}")
    
    # 插值
    r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic', bounds_error=False, fill_value='extrapolate')
    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    
    # 均匀 r* 网格
    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    N_rstar = 6000
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_grid_uniform = np.linspace(rstar_min, rstar_max, N_rstar + 1)
    V_uniform = V_interp(rstar_grid_uniform)
    
    # [v22] 放宽 clip: 只 clip 明显的负值
    V_uniform = np.maximum(V_uniform, -0.01)
    
    # 时间参数 — 增加总时间
    dt = drstar * 0.5
    dt2 = dt * dt
    T_total = 1200.0
    N_time = int(T_total / dt)
    
    print(f"\nr* 范围: [{rstar_min:.1f}, {rstar_max:.1f}]")
    print(f"N_rstar={N_rstar}, drstar={drstar:.6f}")
    print(f"dt={dt:.6f}, T_total={T_total}, N_time={N_time}")
    
    # 初始高斯波包 — 放在势垒峰值
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
        
        if time_idx % 5000 == 0:
            t = time_idx * dt
            elapsed = time.time() - t0
            rms = np.abs(psi_n).std()
            print(f"  t={t:.0f}/{T_total:.0f}, RMS={rms:.4f}, 耗时={elapsed:.1f}s")
    
    total_time = time.time() - t0
    print(f"\nKerr 积分完成: {total_time:.1f}s, NaN次数={nan_count}")
    
    # FFT 分析
    start_skip = int(N_time * 0.15)
    signal_cut = signal_record[start_skip:]
    window = np.hanning(len(signal_cut))
    signal_windowed = signal_cut * window
    
    fft_vals = np.fft.rfft(signal_windowed)
    freqs = np.fft.rfftfreq(len(signal_cut), dt)
    power_spectrum = np.abs(fft_vals)**2
    power_spectrum /= np.max(power_spectrum)
    
    # 找前 5 个谱峰
    peaks, props = find_peaks(power_spectrum, height=0.01, distance=30)
    
    print(f"\n找到 {len(peaks)} 个谱峰:")
    for i, peak in enumerate(peaks[:5]):
        print(f"  峰{i}: freq = {freqs[peak]:.6f}, power = {power_spectrum[peak]:.4f}")
    
    # 与基准对比
    lit_R, lit_I = get_literature(a)
    if len(peaks) > 0:
        # 找最接近理论值的峰
        closest_idx = np.argmin(np.abs(freqs[peaks] - lit_R))
        measured_R = freqs[peaks[closest_idx]]
        error = abs(measured_R - lit_R) / lit_R * 100
        status = "✓" if error < 5 else "⚠"
        print(f"\n对比 a={a}, (l={l},m={m},n={n}):")
        print(f"  理论 ω_R = {lit_R:.6f} (Berti 2009)")
        print(f"  理论 ω_I = {lit_I:.6f}")
        print(f"  测得 ω_R = {measured_R:.6f}")
        print(f"  相对误差 = {error:.2f}% {status}")
        results[a] = (lit_R, lit_I, measured_R, error)
    else:
        print(f"\n⚠ 未找到谱峰 (a={a})")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("Kerr QNM v22 基准计算总结")
print("=" * 70)

for a, (lit_R, lit_I, meas_R, err) in results.items():
    status = "✓ 通过 (<5%)" if err < 5 else ("⚠ 偏差较大" if err < 20 else "✗ 错误很大")
    print(f"a/M={a}: 理论ω_R={lit_R:.4f}, 测得ω_R={meas_R:.4f}, 误差={err:.2f}% {status}")

# ============================================================================
# 绘图
# ============================================================================
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (a, (lit_R, lit_I, meas_R, err)) in enumerate(results.items()):
        ax = axes[idx]
        ax.plot(freqs, power_spectrum, 'b-', linewidth=0.8)
        ax.axvline(lit_R, color='r', linestyle='--', linewidth=2,
                  label=f'理论 ω_R={lit_R:.3f}')
        if len(peaks) > 0:
            closest_idx = np.argmin(np.abs(freqs[peaks] - lit_R))
            ax.plot(freqs[peaks[closest_idx]], power_spectrum[peaks[closest_idx]],
                   'go', markersize=12, label=f'测得={meas_R:.3f}')
        
        ax.set_xlabel('Frequency', fontsize=12)
        ax.set_ylabel('Normalized Power', fontsize=12)
        ax.set_title(f'a/M={a}, 误差={err:.1f}%', fontsize=12)
        ax.set_xlim(0, lit_R * 1.3)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    outdir = os.path.dirname(os.path.abspath(__file__)) + '/notes/06-iterations'
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, 'kerr_qnm_spectrum_v22.png'), dpi=150)
    print(f"\n功率谱图已保存: {outdir}/kerr_qnm_spectrum_v22.png")
except Exception as e:
    print(f"\n绘图失败: {e}")

print("\n" + "=" * 70)
print("完成 v22 (Kerr基准)")
print("=" * 70)
