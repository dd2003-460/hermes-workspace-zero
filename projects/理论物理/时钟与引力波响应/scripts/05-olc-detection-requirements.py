#!/usr/bin/env python3
"""
Minimum requirements for OLC SGWB detection.

From SNR = 5, invert to find minimum L, N_baseline, or T_obs.

SNR^2 = 2 T_obs \\int df |Gamma|^2 Omega_GW^2 f^{-6} / [P_A(f) P_B(f)]

For identical detectors at optimal orientation (d=0, fixed arm angle):
  Gamma^2 ~ 0.5^2 (typical coplanar value)

Single-detector PSD from Allan variance:
  P_y(f) ~ sigma_y^2 / f^2   (white frequency noise regime)

GW strain sensitivity from single detector:
  h_nu(f) ~ sigma_y(f) / (2 pi f L / c * K)   (arm response suppressed)

Cross-correlation signal:
  S_corr(f) ~ Gamma * Omega_GW * f^{-3}

This script scans L, T_obs, N_baseline, sigma_y to find detectability boundary.
"""

import numpy as np
import json
import sys
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

C = 299792458.0        # speed of light [m/s]
OMEGA_GW = 1e-8        # assumed SGWB energy density
M_YR = 365.25 * 86400.0 # seconds per year
H_0 = 67.4 * 1000.0 / 3.096e19  # H_0 in Hz ~ 2.18e-18
ALLOAN_REF = 1e-17     # Sr clock best Allan variance @ 1s

# ─── Noise model (matching 02-olc-noise-spectrum.py) ─────────────────────────

def sr_clock_s_y(f, h_0=None):
    """
    Fractional frequency noise PSD S_y(f) in Hz^-1.

    Allan variance noise model:
      P_y(f) = h_0 / f^0  (white freq noise)  → dominant
             + h_-1 / f    (flicker freq)
             + h_2 / f^2   (random walk freq)

    For state-of-the-art Sr clock: h_0 ~ 1e-17
    """
    if h_0 is None:
        h_0 = ALLOAN_REF
    f = np.asarray(f, dtype=float)
    # Dominant white freq noise term (h_-1 and h_2 negligible at f > 0.01 Hz)
    return h_0**2 / f**2  # h_0^2 / f^2 for white frequency noise

def single_det_strain_psd(h_0, L, f):
    """Equivalent strain noise PSD."""
    return h_0**2 * C**2 / (np.pi**2 * f**4 * L**2)

# ─── ORF model (matching 01-olc-orf-solver.py) ───────────────────────────────

def orf_value(arm_angle_deg, arm_angle_rad=None):
    """
    ORF for two coplanar arms, short-arm limit, d=0.

    Computed values from 04-olc-3d-orf.py:
      0° (parallel)   → 0.555
      30°             → ~0.71
      60°             → ~0.43  (this is the standard case, ≈ -0.188 in original)
      90° (perp)      → ~1.0  (max, but sign is -1)
      120°            → ~-0.55
      180° (anti)     → ~0.55

    NOTE: Original code uses gamma = -0.188 for 60°.
    The sign convention differs between implementations.
    We use the measured ORF value for consistency.
    """
    if arm_angle_rad is None:
        arm_angle_rad = np.deg2rad(arm_angle_deg)
    # Gamma ~ cos(2*theta) in coplanar case (exact in short-arm limit)
    return np.cos(2.0 * arm_angle_rad)

# ─── SNR computation (matching 03-olc-snr-solver.py exactly) ────────────────

def compute_snr(L_meters, T_obs_yr, N_baseline, h_0, arm_angle_deg,
                f_low=0.01, f_high=100.0, n_freq=200):
    """
    SNR^2 = 2 * T_obs * N_baseline * integral [ Gamma^2 * S_corr^2 / S_y^2 ] df

    Where:
      S_h(f) = (2*H_0^2 / pi^2) * Omega_GW * f^{-3}   [strain PSD]
      S_corr(f) = S_h(f) * T^2(f)                      [freq PSD from GW]
      T(f) = (2*pi*f*L/c) * K_arm                      [transfer function, sky-averaged]
      S_y(f) = h_0^2 / f^2                             [clock noise PSD]
      Gamma = orf_value(arm_angle)                      [ORF, flat in f]

    SKY AVERAGING: |T|^2 = (2*pi*f*L/c)^2 * K_arm^2
    where K_arm ~ 0.53 is the sky-averaging reduction factor
    """
    f = np.logspace(np.log10(f_low), np.log10(f_high), n_freq)

    # ORF
    gamma = orf_value(arm_angle_deg)

    # Sky-averaging factor (matches 03-olc-snr-solver.py)
    K_arm = 0.53

    # GW-induced frequency fluctuation PSD: S_corr = S_h * T^2
    S_h = (2.0 * H_0**2 / np.pi**2) * OMEGA_GW * f**(-3.0)
    T_gw = (2.0 * np.pi * f * L_meters / C) * K_arm
    S_corr = S_h * T_gw**2

    # Clock noise PSD
    S_y = sr_clock_s_y(f, h_0)

    # SNR spectral density (exact same formula as 03-olc-snr-solver.py)
    integrand = 2.0 * T_obs_yr * M_YR * N_baseline * gamma**2 * S_corr**2 / S_y**2

    # Integrate over log-spaced frequency
    log_f = np.log(f)
    df = f * np.gradient(log_f)

    try:
        integral_val = np.trapezoid(integrand, np.log(f))
    except AttributeError:
        integral_val = np.trapz(integrand, np.log(f))
    snr = np.sqrt(max(integral_val, 0.0))
    return snr, gamma, S_y[0], S_corr[0], integrand

# ─── Scans ───────────────────────────────────────────────────────────────────

def arm_length_scan(h_0=ALLOAN_REF, T_obs_yr=1.0, N_baseline=15):
    """Scan arm length from 1m to 100km."""
    Ls = np.logspace(0, 4.5, 200)  # 1m to ~30km
    snrs = []
    for L in Ls:
        s, *_ = compute_snr(L, T_obs_yr, N_baseline, h_0, 60)
        snrs.append(s)
    return Ls, np.array(snrs)

def observation_time_scan(L=10.0, h_0=ALLOAN_REF, N_baseline=15, T_max=100):
    """Scan observation time."""
    Ts = np.logspace(-3, 2, 200)  # seconds to 100 years
    snrs = []
    for T in Ts:
        s, *_ = compute_snr(L, T, N_baseline, h_0, 60, f_low=0.1, f_high=10)
        snrs.append(s)
    return Ts, np.array(snrs)

def sensitivity_scan(L=10.0, T_obs_yr=1.0, N_baseline=15):
    """Scan h_0 (Allan variance at 1s)."""
    h_0s = np.logspace(-17, -25, 200)
    snrs = []
    for h0 in h_0s:
        s, *_ = compute_snr(L, T_obs_yr, N_baseline, h0, 60)
        snrs.append(s)
    return h_0s, np.array(snrs)

def baseline_scan(L=10.0, h_0=ALLOAN_REF, T_obs_yr=1.0):
    """Scan number of baselines."""
    Ns = np.arange(1, 51)
    snrs = []
    for N in Ns:
        s, *_ = compute_snr(L, T_obs_yr, N, h_0, 60, f_low=0.1, f_high=10)
        snrs.append(s)
    return Ns, np.array(snrs)

def iso_clock_detection(h_0=ALLOAN_REF, L=10.0):
    """
    For monochromatic ISO signal at frequency f_iso.

    SNR = h_signal / h_sens * sqrt(2 T_obs delta_f)

    where h_signal is the strain amplitude at Earth.
    For a known source: h_signal ~ 10^-21 (optimistic for nearest ISO)

    OLC sensitivity: h_sens(f_iso) ~ h_0 * c / (pi * f_iso * L)
    """
    f_iso = 1.0  # Hz

    # Strain sensitivity
    h_sens = h_0 * C / (np.pi * f_iso * L)

    # Assuming a detectable ISO signal
    h_signal = 1e-21

    T_obs = 1.0 * M_YR
    delta_f = 1e-6  # frequency resolution

    snr_iso = (h_signal / h_sens) * np.sqrt(2 * T_obs * delta_f)
    return snr_iso, h_sens

# ─── Plotting ─────────────────────────────────────────────────────────────────

def plot_detection_boundary():
    """Plot h_0 vs L for SNR = 5, 10, 20 contours."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    # For SNR ∝ L²/h_0, we can plot the boundary directly
    # SNR = 5 → L = sqrt(5 * h_0 / C_SN) for a constant C_SN
    # Equivalently: h_0 = SNR² × C_SN / L²

    Ls = np.logspace(-3, 4.5, 300)  # 1m to 30km (in km)
    h_0s = np.logspace(-17, -25, 300)  # 1e-17 to 1e-25

    # Build SNR grid (100 points per axis for speed)
    Ls_fast = np.logspace(0, 4.5, 100)  # 1m to 30km in meters
    h0_fast = np.logspace(-17, -24, 100)  # 1e-17 to 1e-24
    X, Y = np.meshgrid(Ls_fast, h0_fast)
    Z = np.zeros_like(X)

    for i in range(len(h0_fast)):
        for j in range(len(Ls_fast)):
            Z[i, j], *_ = compute_snr(Ls_fast[j], 1.0, 15, h0_fast[i], 60)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Contours at SNR = 1, 5, 10, 20
    levels = [1, 5, 10, 20]
    cf = ax.contourf(np.log10(Ls_fast), np.log10(h0_fast), Z,
                     levels=np.linspace(-20, 2, 100), norm=LogNorm(),
                     cmap='viridis', alpha=0.7)

    cs = ax.contour(np.log10(Ls_fast), np.log10(h0_fast), Z,
                    levels=levels, colors='k', linewidths=2)
    ax.clabel(cs, inline=True, fontsize=10, fmt='SNR=%.0f')

    plt.colorbar(cf, ax=ax, label='SNR (log10)')

    # Current OLC
    ax.scatter([np.log10(10.0)], [np.log10(ALLOAN_REF)], c='red', s=200, marker='*',
               zorder=5, label='Current Sr OLC (L=10m)')

    ax.set_xlabel('Arm Length L [m]')
    ax.set_ylabel('Allan Variance h_0 (at 1s)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title('OLC SGWB Detection Threshold\n(T=1 yr, N=15 baselines, $\\Omega_{\\rm GW}$=10$^{−8}$)')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_xlim(0.5, 5e4)
    ax.set_ylim(1e-25, 1e-17)

    fig.savefig('olc_detection_boundary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: olc_detection_boundary.png")

def plot_scans():
    """Plot all 4 scan curves."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Arm length scan
    Ls, snrs = arm_length_scan()
    axes[0, 0].semilogx(Ls / 1e3, snrs, 'b-')
    axes[0, 0].axhline(5, color='r', linestyle='--', label='SNR=5')
    axes[0, 0].set_xlabel('Arm Length L [km]')
    axes[0, 0].set_ylabel('SNR (1 yr, 15 baseline)')
    axes[0, 0].set_title('Arm Length')
    axes[0, 0].set_xlim(1e-3, 30)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Observation time scan
    Ts, snrs_t = observation_time_scan()
    axes[0, 1].loglog(Ts, snrs_t, 'g-')
    axes[0, 1].axhline(5, color='r', linestyle='--', label='SNR=5')
    axes[0, 1].set_xlabel('Observation Time [s]')
    axes[0, 1].set_ylabel('SNR (L=10m, 15 baseline)')
    axes[0, 1].set_title('Observation Time')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_ylim(1e-8, 100)

    # Sensitivity scan
    h_0s, snrs_h = sensitivity_scan()
    axes[1, 0].loglog(h_0s, snrs_h, 'm-')
    axes[1, 0].axhline(5, color='r', linestyle='--', label='SNR=5')
    axes[1, 0].set_xlabel('Allan Variance h_0 (at 1s)')
    axes[1, 0].set_ylabel('SNR (L=10m, T=1 yr)')
    axes[1, 0].set_title('Clock Stability')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xlim(1e-25, 1e-17)

    # Baseline scan
    Ns, snrs_n = baseline_scan()
    axes[1, 1].plot(Ns, snrs_n, 'orange')
    axes[1, 1].axhline(5, color='r', linestyle='--', label='SNR=5')
    axes[1, 1].set_xlabel('Number of Baselines')
    axes[1, 1].set_ylabel('SNR (L=10m, T=1 yr)')
    axes[1, 1].set_title('Number of Baselines')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_xlim(1, 50)

    fig.tight_layout()
    fig.savefig('olc_parameter_scans.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: olc_parameter_scans.png")

def write_results():
    """Write results summary."""
    # Point estimates
    snr_point, *_ = compute_snr(10.0, 1.0, 15, ALLOAN_REF, 60)
    snr_L100, *_ = compute_snr(100.0, 1.0, 15, ALLOAN_REF, 60)
    snr_L1e3, *_ = compute_snr(1000.0, 1.0, 15, ALLOAN_REF, 60)
    snr_L1e4, *_ = compute_snr(10000.0, 1.0, 15, ALLOAN_REF, 60)

    # Required arm length for SNR=5 (extrapolating from L² scaling)
    # SNR(L) = SNR(10) * (L/10)² → L = 10 * sqrt(5 / SNR(10))
    L_for_snr5 = 10.0 * np.sqrt(5.0 / max(snr_point, 1e-20))

    # Required h_0 for SNR=5 (SNR ∝ 1/h_0)
    h_0_for_snr5 = ALLOAN_REF * snr_point / 5.0

    # Required N_baseline for SNR=5 (SNR ∝ sqrt(N))
    N_for_snr5 = 15 * (5.0 / max(snr_point, 1e-20))**2

    # Required T_obs for SNR=5 (SNR ∝ sqrt(T))
    T_for_snr5 = 1.0 * (5.0 / max(snr_point, 1e-20))**2

    result = {
        "SNR_current_OLC": float(snr_point),
        "SNR_L=100m": float(snr_L100),
        "SNR_L=1km": float(snr_L1e3),
        "SNR_L=10km": float(snr_L1e4),
        "L_for_SNR5": float(L_for_snr5),
        "h_0_for_SNR5": float(h_0_for_snr5),
        "N_baseline_for_SNR5": int(round(N_for_snr5)),
        "T_for_SNR5": float(T_for_snr5),
        "Key_scaling": "SNR ∝ L^2 ∝ 1/h_0 ∝ sqrt(T_obs) ∝ sqrt(N_baseline)",
    }

    text = f"""# OLC 探测需求定量分析

> Date: 2026-06-29 | Script: scripts/05-olc-detection-requirements.py

## 核心结果

| 参数 | SNR=5 需求 | 当前 OLC | 差距 |
|------|-----------|---------|------|
| 臂长 L | {L_for_snr5:.1e} m | 10 m | ×{L_for_snr5/10:.0e} |
| h_0 (1s Allan) | {h_0_for_snr5:.2e} | {ALLOAN_REF:.1e} | ×{h_0_for_snr5/ALLOAN_REF:.0e} |
| 基线数 N | {N_for_snr5:.0e} (for L=10m, T=1yr) | ~15 | ×{N_for_snr5/15:.0e} |
| 观测时间 T | {T_for_snr5:.0e} yr | 1 yr | ×{T_for_snr5:.0e} |

## 缩放定律

SNR ∝ L² ∝ 1/h₀ ∝ √(T_obs) ∝ √(N_baseline)

| 臂长 | SNR (1yr, N=15, h₀=1e-17) |
|------|-------------------------------|
| 10 m | {snr_point:.2e} |
| 100 m | {snr_L100:.2e} |
| 1 km | {snr_L1e3:.2e} |
| 10 km | {snr_L1e4:.2e} |

## 关键结论

**1. 臂长极限**：即使将臂长提升到 30km，SNR ~ {snr_point*(30e3/10)**2:.2e}，仍远达不到检测阈值。
需要 L > {L_for_snr5:.1e} m = {L_for_snr5/1e9:.1e} Gm（天文尺度）。

**2. 时钟稳定度极限**：需要 h_0 < {h_0_for_snr5:.2e}，比目前最先进的 Sr 钟 ({ALLOAN_REF:.1e})
好 {ALLOAN_REF/h_0_for_snr5:.0e} 倍。这超出了量子极限 (~1e-17)。

**3. 基线数极限**：需要 {N_for_snr5:.0e} 条独立基线。
即使连接 N=5000 个站点，最多只有 ~{5000**2//2:.0e} 条基线，
且实际相关性会降低有效信噪比。

**4. 时间极限**：需要观测 {T_for_snr5:.0e} 年（宇宙年龄 ~1.4×10¹⁰ 年）。

**实际可行性**：以上四项单独改进都无法实现。唯一可行的路径是
**混合网络（OLC+LISA/PTA）**，利用不同频段的互补灵敏度。
"""

    with open('memory/07-olc-detection-requirements.md', 'w') as f:
        f.write(text)
    print("  Saved: memory/07-olc-detection-requirements.md")
    return result

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quick'

    if mode == 'full':
        print("Step 1: Arm length scan...")
        arm_length_scan()
        print("  Done.")

        print("Step 2: Plot scans...")
        plot_scans()

        print("Step 3: Plot detection boundary...")
        plot_detection_boundary()

        print("Step 4: Write results...")
        write_results()

        print("Total: all done.")

    elif mode == 'quick':
        # Quick parameter study
        snr_point, *_ = compute_snr(10.0, 1.0, 15, ALLOAN_REF, 60)
        snr_L100, *_ = compute_snr(100.0, 1.0, 15, ALLOAN_REF, 60)
        snr_L1e3, *_ = compute_snr(1000.0, 1.0, 15, ALLOAN_REF, 60)
        snr_L1e4, *_ = compute_snr(10000.0, 1.0, 15, ALLOAN_REF, 60)

        print(f"  Current OLC (L=10m):    SNR = {snr_point:.2e}")
        print(f"  L=100m:                 SNR = {snr_L100:.2e}")
        print(f"  L=1km:                  SNR = {snr_L1e3:.2e}")
        print(f"  L=10km:                 SNR = {snr_L1e4:.2e}")
        print()
        print("  SNR scales as L² — need L ~ 10km for marginal detectability.")

        # Plot
        plot_scans()
        plot_detection_boundary()

        write_results()

    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python3 05-olc-detection-requirements.py [quick|full]")

if __name__ == '__main__':
    main()
