#!/usr/bin/env python3
"""
Mixed network OLC+LISA cross-correlation SNR analysis.

Phase 3: 探测 OLC 的唯一可行路径 — 混合网络与 LISA/PTA 联合分析。

核心思想：
- OLC 敏感频段：~0.1-100 Hz（高频）
- LISA 敏感频段：~0.1 mHz-1 Hz（低频）
- 两探测器独立观测 SGWB，混合网络 SNR = sqrt(SNR_OLC^2 + SNR_LISA^2)
- 跨相关项（不同可观测量的交叉相关）无法定义（C1 修复）

单探测器 SNR 公式 (Allen 1987, Thorne 1987):
  d(SNR^2)/df = 2 T_obs gamma^2 [S_corr(f)]^2 / S_noise(f)

SNR 计算公式 (S^2/S_noise 而非 S^2/S_noise^2，C2 修复)。
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

C = 299792458.0
H_0 = 67.4 * 1000.0 / 3.096e19  # ~2.18e-18 Hz
OMEGA_GW = 1e-8
M_YR = 365.25 * 86400.0

# ─── OLC noise model ─────────────────────────────────────────────────────────

def olc_s_y(f, h_0=1e-17):
    """OLC clock noise PSD S_y(f) in Hz^-1 (white freq noise regime)."""
    f = np.asarray(f, dtype=float)
    return h_0**2 / f**2

def olc_t_gw_sq(f, L=10.0):
    """Sky-averaged |T_gw(f)|^2 for OLC. T ~ (2pi f L/c) * K_arm."""
    f = np.asarray(f, dtype=float)
    K_arm = 0.53
    t_base = 2.0 * np.pi * np.abs(f) * L / C
    return (t_base * K_arm)**2

def olc_s_corr(f, Omega_GW=OMEGA_GW, L=10.0):
    """GW-induced fractional freq PSD S_corr = S_h * T^2."""
    f = np.asarray(f, dtype=float)
    S_h = (2.0 * H_0**2 / np.pi**2) * Omega_GW * f**(-3.0)
    return S_h * olc_t_gw_sq(f, L)

def olc_snr_integrated(f, L=10.0, T_obs=1.0, Omega_GW=OMEGA_GW):
    """Integrated OLC SNR."""
    # C2 FIX: S_signal^2 / S_noise (not S_noise^2) — Allen 1987, Thorne 1987
    dSNR2_df = (2.0 * T_obs * M_YR * olc_s_corr(f, Omega_GW, L)**2
                / olc_s_y(f, h_0=1e-17))
    try:
        snr2 = np.trapezoid(dSNR2_df, f)
    except AttributeError:
        snr2 = np.trapz(dSNR2_df, f)
    return np.sqrt(max(snr2, 0.0))

# ─── LISA noise model (Liu et al. 2011 simplified) ───────────────────────────

def lisa_strain_psd(f):
    """LISA strain noise PSD S_h(f) [Hz^-1]."""
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-6)
    L_lisa = 2.5e9
    P_a = 3e-15 * (1.0 + (4e-3 / f)**2) / (1.0 + (f / 8e-3)**2)
    P_d = 1.5e-11
    h_acc = P_a / ((2.0 * np.pi * f)**2)
    h_disp = P_d
    return (h_acc**2 + h_disp**2) / L_lisa**2

def lisa_t_gw_sq(f):
    """LISA arm response |T|^2."""
    L_lisa = 2.5e9
    return (2.0 * np.pi * np.abs(f) * L_lisa / C)**2

def lisa_s_corr(f, Omega_GW=OMEGA_GW):
    """LISA GW-induced strain PSD."""
    f = np.asarray(f, dtype=float)
    S_h = (2.0 * H_0**2 / np.pi**2) * Omega_GW * f**(-3.0)
    return S_h * lisa_t_gw_sq(f)

def lisa_snr_integrated(f, T_obs=1.0, gamma_lisa=0.5, Omega_GW=OMEGA_GW):
    """Integrated LISA SNR."""
    S_corr = lisa_s_corr(f, Omega_GW)
    S_noise = lisa_strain_psd(f)
    # C2 FIX: S_signal^2 / S_noise (not S_noise^2) — Allen 1987
    # C4 FIX: T_obs * M_YR for time in seconds
    dSNR2_df = 2.0 * T_obs * M_YR * gamma_lisa**2 * S_corr**2 / S_noise
    try:
        snr2 = np.trapezoid(dSNR2_df, f)
    except AttributeError:
        snr2 = np.trapz(dSNR2_df, f)
    return np.sqrt(max(snr2, 0.0))

# ─── Cross-correlation SNR (OLC + LISA) ──────────────────────────────────────

def olca_lisa_cross_snr(f, T_obs=1.0, N_base=15,
                         gamma_olc=0.53, gamma_lisa=0.5, Omega_GW=OMEGA_GW):
    """Cross-correlation SNR between OLC and LISA.

    d(SNR^2)/df = 2 T_obs N_base gamma_OLC gamma_LISA S_corr_OLC S_corr_LISA
                  / sqrt(P_noise_OLC P_noise_LISA)^2

    For different detector types, the cross-ORF is small since they
    sample the sky differently. We use gamma_cross = gamma_olc * gamma_lisa * 0.5
    as an order-of-magnitude estimate.
    """
    f = np.asarray(f, dtype=float)
    gamma_cross = gamma_olc * gamma_lisa * 0.5  # conservative estimate

    # OLC detects frequency shift, noise is in Hz
    S_corr_olc = olc_s_corr(f, Omega_GW)
    noise_olc = olc_s_y(f, h_0=1e-17)

    # LISA detects strain directly, noise is in Hz^-1
    S_corr_lisa = lisa_s_corr(f, Omega_GW)
    noise_lisa = lisa_strain_psd(f)

    # C1 FIX: OLC (fractional freq) and LISA (strain) are different observables.
    # Cross-correlation between fundamentally different domains cannot be defined.
    # The cross-term below is kept as a heuristic spectral overlap indicator only.
    dSNR2_df = (2.0 * T_obs * M_YR * N_base * gamma_cross**2
                * S_corr_olc**2 * S_corr_lisa**2
                / (noise_olc * noise_lisa))
    try:
        snr2 = np.trapezoid(dSNR2_df, f)
    except AttributeError:
        snr2 = np.trapz(dSNR2_df, f)
    return np.sqrt(max(snr2, 0.0))

# ─── Combined network SNR ────────────────────────────────────────────────────

def combined_snr(f_common, T_obs=1.0):
    """Total SNR for OLC+LISA mixed network.

    C4 FIX: For independent detectors, SNR_total^2 = SNR_OLC^2 + SNR_LISA^2.
    No cross-correlation term between independent estimators.
    N_base removed — network SNR scales as sqrt(N_baselines), not linearly.
    T_obs in years, converted to seconds via M_YR.
    """
    # OLC dSNR2 per log(f) bin (gamma removed: C3 K_arm=0.53 already in T_gw_sq)
    dSNR2_olc = (2.0 * T_obs * M_YR
                 * olc_s_corr(f_common, OMEGA_GW)**2
                 / olc_s_y(f_common, h_0=1e-17))
    # LISA dSNR2 per log(f) bin (C2 FIX: S_noise^1 not S_noise^2)
    dSNR2_lisa = (2.0 * T_obs * M_YR * 0.5**2
                  * lisa_s_corr(f_common, OMEGA_GW)**2
                  / lisa_strain_psd(f_common))

    # Only keep OLC dSNR^2 in its sensitive band (f > 0.01 Hz)
    dSNR2_olc = np.where(f_common >= 0.01, dSNR2_olc, 0.0)
    # Only keep LISA dSNR^2 in its sensitive band (f < 1 Hz)
    dSNR2_lisa = np.where(f_common <= 1.0, dSNR2_lisa, 0.0)

    combined = dSNR2_olc + dSNR2_lisa

    try:
        snr2 = np.trapezoid(combined, np.log(f_common))
    except AttributeError:
        snr2 = np.trapz(combined, np.log(f_common))
    return np.sqrt(max(snr2, 0.0)), combined

# ─── Plotting ────────────────────────────────────────────────────────────────

def plot_sensitivity_curves():
    """Compare sensitivity curves for OLC, LISA, and mixed network."""
    f = np.logspace(-4, 2, 2000)

    # OLC per-Hz SNR spectral density (C2: noise^1, C4: no N_base, C3: no gamma)
    dSNR2_olc = (2.0 * 1.0 * M_YR
                 * olc_s_corr(f, OMEGA_GW, L=10.0)**2
                 / olc_s_y(f, h_0=1e-17))
    dSNR_df_olc = np.sqrt(np.maximum(dSNR2_olc, 0))

    # LISA per-Hz SNR spectral density (C2: noise^1)
    dSNR2_lisa = (2.0 * 1.0 * M_YR * 0.5**2
                  * lisa_s_corr(f, OMEGA_GW)**2
                  / lisa_strain_psd(f))
    dSNR_df_lisa = np.sqrt(np.maximum(dSNR2_lisa, 0))

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(f, dSNR_df_olc, linewidth=2.5, label='OLC (Sr, L=10m, N=15)')
    ax.plot(f, dSNR_df_lisa, linewidth=2.5, label='LISA (design sensitivity)')

    # Combined
    _, combined = combined_snr(f)
    dSNR_df_combined = np.sqrt(np.maximum(combined, 0))
    ax.plot(f, dSNR_df_combined, linewidth=2.5, linestyle='--',
            label='Mixed network (OLC+LISA combined)')

    ax.axhline(y=3.0, color='red', linestyle=':', alpha=0.5, linewidth=1.5)
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel(r'dSNR/d$f$ (1 yr, $\Omega_{\rm GW}=10^{-8}$)', fontsize=11)
    ax.set_title('Sensitivity Comparison: OLC vs LISA vs Mixed Network', fontsize=13)
    ax.legend(fontsize=10, loc='best')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)

    # Mark sensitivity peaks
    ax.annotate('LISA peak', xy=(f[np.argmax(dSNR_df_lisa)],
          dSNR_df_lisa[np.argmax(dSNR_df_lisa)]),
          fontsize=9, ha='left', alpha=0.7)
    ax.annotate('OLC peak', xy=(f[np.argmax(dSNR_df_olc)],
          dSNR_df_olc[np.argmax(dSNR_df_olc)]),
          fontsize=9, ha='left', alpha=0.7)

    outpath = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_lisa_sensitivity.png"
    plt.savefig(outpath, dpi=200)
    plt.close()
    print(f"  Saved: olc_lisa_sensitivity.png")

    # Save data
    np.savez(outpath.replace('.png', '.npz'),
        f=f, dSNR_df_olc=dSNR_df_olc,
        dSNR_df_lisa=dSNR_df_lisa,
        dSNR_df_combined=dSNR_df_combined)

def plot_frequency_coverage():
    """Show which frequency bands each detector covers for SNR>1."""
    f = np.logspace(-4, 2, 2000)
    T_obs = 1.0  # 1 year

    # C2: noise^1, C4: no N_base, C3: no gamma
    dSNR2_olc = (2.0 * T_obs * M_YR
                 * olc_s_corr(f, OMEGA_GW, L=10.0)**2
                 / olc_s_y(f, h_0=1e-17))
    dSNR2_lisa = (2.0 * T_obs * M_YR * 0.5**2
                  * lisa_s_corr(f, OMEGA_GW)**2
                  / lisa_strain_psd(f))

    # Integrate cumulatively to find SNR(f) at each frequency
    dSNR_df_olc = np.sqrt(np.maximum(dSNR2_olc, 0))
    dSNR_df_lisa = np.sqrt(np.maximum(dSNR2_lisa, 0))

    # Cumulative SNR (integrated from f_min up to f)
    # Use cumsum of dSNR2 * delta_logf as a simple integration
    log_f = np.log(f)
    d_logf = np.gradient(log_f)
    # d_logf has n elements, dSNR2 has n elements
    # Use d_logf[0] for first element, or simpler: rect rule
    cum_olc2 = np.maximum(np.concatenate([[0], np.cumsum(dSNR2_olc[:-1] * d_logf[:-1])]), 0.0)
    cum_lisa2 = np.maximum(np.concatenate([[0], np.cumsum(dSNR2_lisa[:-1] * d_logf[:-1])]), 0.0)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.semilogy(f, np.sqrt(np.maximum(cum_olc2, 0)), linewidth=2.5,
                label='OLC cumulative SNR(f)')
    ax.semilogy(f, np.sqrt(np.maximum(cum_lisa2, 0)), linewidth=2.5,
                label='LISA cumulative SNR(f)')

    # Combined cumulative
    ax.semilogy(f, np.sqrt(np.maximum(cum_olc2 + cum_lisa2, 0)),
                linewidth=2.5, linestyle='--',
                label='Mixed network cumulative SNR(f)')

    ax.axhline(y=5.0, color='green', linestyle=':', alpha=0.5, linewidth=1.5,
               label='SNR = 5 (detection)')
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Cumulative SNR(0→f)', fontsize=12)
    ax.set_title('Cumulative SNR Distribution — OLC vs LISA vs Mixed', fontsize=13)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)

    outpath = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_lisa_cumulative_snr.png"
    plt.savefig(outpath, dpi=200)
    plt.close()
    print(f"  Saved: olc_lisa_cumulative_snr.png")

def plot_snr_vs_observation_time():
    """SNR vs observation time for each detector and the network."""
    Ts = np.logspace(0, 7.5, 100)  # 1s to ~30 Myr

    f = np.logspace(-4, 2, 1000)
    olr = olc_snr_integrated(f, L=10.0, T_obs=1.0)
    lsa = lisa_snr_integrated(f, T_obs=1.0)

    # SNR scales as sqrt(T_obs)
    T_obs_yr = Ts / M_YR
    snr_olc = olr * np.sqrt(T_obs_yr)
    snr_lisa = lsa * np.sqrt(T_obs_yr)
    snr_combined = np.sqrt(snr_olc**2 + snr_lisa**2)

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.semilogy(T_obs_yr, snr_olc, linewidth=2.5, label='OLC alone (15 baselines)')
    ax.semilogy(T_obs_yr, snr_lisa, linewidth=2.5, label='LISA alone')
    ax.semilogy(T_obs_yr, snr_combined, linewidth=2.5, linestyle='--',
                label='Mixed network (OLC+LISA)')

    ax.axhline(y=5.0, color='green', linestyle=':', alpha=0.5, linewidth=1.5,
               label='SNR = 5 (detection)')
    ax.set_xlabel('Observation time (yr)', fontsize=12)
    ax.set_ylabel('Total SNR', fontsize=12)
    ax.set_title('SNR vs Observation Time — OLC+LISA Mixed Network', fontsize=13)
    ax.legend(fontsize=10)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)

    # Mark current OLC SNR
    ax.annotate(f'OLC current SNR = {olr:.2e}',
                xy=(1.0, olr), fontsize=9, color='blue',
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))

    outpath = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_lisa_snr_time.png"
    plt.savefig(outpath, dpi=200)
    plt.close()
    print(f"  Saved: olc_lisa_snr_time.png")

def plot_frequency_band_decomposition():
    """Show SNR distribution across frequency bands for each detector type."""
    Omega_GW = OMEGA_GW
    T_obs = 1.0 * M_YR

    f = np.logspace(-4, 2, 2000)
    # C2: noise^1, C4: no N_base, C3: no gamma
    dSNR2_olc = (2.0 * T_obs
                 * olc_s_corr(f, Omega_GW, L=10.0)**2
                 / olc_s_y(f, h_0=1e-17))
    dSNR2_lisa = (2.0 * T_obs * 0.5**2
                  * lisa_s_corr(f, Omega_GW)**2
                  / lisa_strain_psd(f))

    dSNR_df_olc = np.sqrt(np.maximum(dSNR2_olc, 0))
    dSNR_df_lisa = np.sqrt(np.maximum(dSNR2_lisa, 0))

    bands = [
        ('0.1-1 mHz', 1e-4, 1e-3),
        ('1-10 mHz', 1e-3, 1e-2),
        ('10-100 mHz', 1e-2, 0.1),
        ('0.1-1 Hz', 0.1, 1.0),
        ('1-10 Hz', 1.0, 10.0),
        ('10-100 Hz', 10.0, 100.0),
    ]

    labels = []
    olc_values = []
    lisa_values = []

    for name, f_min, f_max in bands:
        mask_olc = (f >= f_min) & (f < f_max)
        mask_lisa = (f >= f_min) & (f < f_max)
        if not (np.any(mask_olc) or np.any(mask_lisa)):
            continue
        snr2_olc = np.trapezoid(dSNR2_olc[mask_olc], f[mask_olc]) if np.any(mask_olc) else 0
        snr2_lisa = np.trapezoid(dSNR2_lisa[mask_lisa], f[mask_lisa]) if np.any(mask_lisa) else 0
        snr_olc = np.sqrt(max(snr2_olc, 0))
        snr_lisa = np.sqrt(max(snr2_lisa, 0))
        labels.append(name)
        olc_values.append(snr_olc)
        lisa_values.append(snr_lisa)

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(1, 1, figsize=(11, 6))
    bars1 = ax.bar(x - width/2, olc_values, width, label='OLC', alpha=0.8, color='#377eb8')
    bars2 = ax.bar(x + width/2, lisa_values, width, label='LISA', alpha=0.8, color='#e78ac3')
    # Combined
    ax.bar(x + width, np.sqrt(np.array(olc_values)**2 + np.array(lisa_values)**2),
           width*0.6, label='Mixed network', alpha=0.7, color='#66c2a5')

    ax.set_xlabel('Frequency Band', fontsize=11)
    ax.set_ylabel(r'Band SNR (1 yr, $\Omega_{\rm GW}$=10$^{{-8}}$)', fontsize=11)
    ax.set_title('SNR by Frequency Band — OLC vs LISA vs Mixed', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yscale('log')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    for i, (v1, v2) in enumerate(zip(olc_values, lisa_values)):
        ax.text(i - width/2, max(v1 * 3, 1e-30), f'{v1:.2e}',
                ha='center', fontsize=7, rotation=45)
        ax.text(i + width/2, max(v2 * 3, 1e-30), f'{v2:.2e}',
                ha='center', fontsize=7, rotation=45)

    outpath = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_lisa_bands.png"
    plt.savefig(outpath, dpi=200)
    plt.close()
    print(f"  Saved: olc_lisa_bands.png")

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    import pathlib
    f = np.logspace(-4, 2, 2000)

    print("=" * 60)
    print("OLC+LISA Mixed Network SNR Analysis — Phase 3")
    print("=" * 60)

    # Compute SNR values
    print(f"\n--- Per-detector SNR (1 yr, Omega_GW=1e-8) ---")
    snr_olc_1yr = olc_snr_integrated(f, L=10.0, T_obs=1.0)
    print(f"  OLC alone (15 baselines):    SNR = {snr_olc_1yr:.3e}")

    snr_lisa_1yr = lisa_snr_integrated(f, T_obs=1.0)
    print(f"  LISA alone:                  SNR = {snr_lisa_1yr:.3e}")

    snr_cross = olca_lisa_cross_snr(f)
    print(f"  Cross-correlation term:      SNR^2 contribution = {snr_cross**2:.3e}")

    snr_combined, _ = combined_snr(f)
    print(f"  Mixed network (combined):    SNR = {snr_combined:.3e}")

    print(f"\n--- Improvement factor ---")
    if snr_olc_1yr > 1e-30:
        print(f"  Mixed / OLC = {snr_combined / snr_olc_1yr:.1f}x")
    else:
        print(f"  OLC SNR too small to compute ratio")
    if snr_lisa_1yr > 1e-30:
        print(f"  Mixed / LISA = {snr_combined / snr_lisa_1yr:.3e}")

    # Key finding: LISA dominates by many orders of magnitude
    print(f"\n--- Key finding ---")
    if snr_lisa_1yr > snr_olc_1yr * 10:
        print(f"  LISA SNR ({snr_lisa_1yr:.3e}) >> OLC SNR ({snr_olc_1yr:.3e})")
        print(f"  The mixed network gain is dominated by LISA.")
        print(f"  OLC contributes negligibly to total SNR even for detection.")
    elif snr_olc_1yr > snr_lisa_1yr:
        print(f"  OLC SNR ({snr_olc_1yr:.3e}) > LISA SNR ({snr_lisa_1yr:.3e})")
        print(f"  OLC dominates in its frequency band.")
    else:
        print(f"  Both detectors have comparable but tiny SNR.")

    # Compute what L would need to be for OLC to reach SNR=1 in 1yr
    print(f"\n--- OLC arm length for SNR=1 (1yr) ---")
    # SNR ~ L^2, so L ~ sqrt(5/SNR)
    # But OLC uses transfer function T ~ L, so S_corr ~ L^2,
    # and SNR ~ L^2
    L_for_snr5 = 10.0 * np.sqrt(5.0 / max(snr_olc_1yr, 1e-100))
    print(f"  L needed for SNR=5: {L_for_snr5:.3e} m = {L_for_snr5/1e9:.3e} Gm")
    print(f"  L needed for SNR=1: {L_for_snr5/np.sqrt(5):.3e} m = {L_for_snr5/np.sqrt(5)/1e9:.3e} Gm")

    # Generate plots
    print(f"\n--- Generating plots ---")
    plot_sensitivity_curves()
    plot_frequency_coverage()
    plot_snr_vs_observation_time()
    plot_frequency_band_decomposition()

    # Save numerical data
    data_path = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_lisa_data.npz"
    np.savez(data_path,
        f=f,
        snr_olc_1yr=snr_olc_1yr,
        snr_lisa_1yr=snr_lisa_1yr,
        snr_cross_1yr=snr_cross,
        snr_combined_1yr=snr_combined,
        snr_ratio_lisa_olc=snr_lisa_1yr / max(snr_olc_1yr, 1e-100),
        L_for_snr5=L_for_snr5,
    )
    print(f"  Saved: olc_lisa_data.npz")

    # Results summary
    print(f"\n{'='*60}")
    print("Phase 3 KEY FINDING:")
    print("=" * 60)
    if snr_lisa_1yr > snr_olc_1yr:
        ratio = snr_lisa_1yr / max(snr_olc_1yr, 1e-100)
        print(f"  LISA dominates OLC by ~{ratio:.1e}x in total SNR.")
        print(f"  Even a mixed network gains << 1% from OLC contribution.")
        print(f"  Conclusion: OLC+LISA mixed network does NOT significantly")
        print(f"  improve SGWB detection capability for typical Ω_GW models.")
        print(f"  OLC's potential value lies in:")
        print(f"  (1) Orthogonal polarisation coverage (no LISA-like arms)")
        print(f"  (2) Very high-freq corner (kHz+) for certain source types")
        print(f"  (3) Independent systematics verification (not frequency coverage)")
    print("=" * 60)


if __name__ == '__main__':
    main()
