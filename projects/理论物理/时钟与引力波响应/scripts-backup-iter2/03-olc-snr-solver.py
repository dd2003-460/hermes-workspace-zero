#!/usr/bin/env python3
"""
OLC SNR 综合计算器 v3 — SGWB 交叉关联信噪比
===============================================

物理框架：
- OLC 测量：光往返时间延迟 → 频率偏移 dy
- 噪声 S_y：Sr 钟 Allan 方差 → PSD (h_0/f^0 + h_-1/f^1 + h_2/f^2)
- GW 响应：T_gw = (2pi f L/c) × sinc，Sky-averaged |T|^2

关键公式 (Sacks 1967, Kremske+ 2005):
    (SNR)^2 = 2 T_obs int_0^inf df gamma^2(f) S_corr^2(f) / S_N^2(f)

其中：
    S_corr(f) = f^(-3) * A_S * Omega_GW  [fractional freq PSD induced by GW]
    S_N(f)    = S_y(f)                     [measured noise PSD]

A_S = (H_0^2) / (2 pi^2)  [strain-to-freq conversion factor]

"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import importlib.util
import time

c = 299792458.0
H_0 = 67.4 * 1000.0 / 3.096e19  # H_0 in Hz = 67.4 km/s/Mpc -> ~2.18e-18 Hz
A_S = H_0**2 / (2.0 * np.pi**2)  # ~8.15e-37 Hz^-1 * s^2
# Omega_GW = (1/pi) (c^3 / 8G) S_h(f) / f^3  => S_h = (pi/c^3) * 8G * Omega * f^3 / (c^3/8G)
# Standard: S_h(f) = (2 H_0^2 / pi^2) Omega_GW f^{-3} in dimensionless strain^2/Hz
# => S_corr = T^2 * S_h = (2 H_0^2 / pi^2) Omega_GW f^{-3} T^2

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

noise = _load_module("noise",
    "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/02-olc-noise-spectrum.py")

# --- parameters ---
L_olc = 10.0           # OLC arm length (m)
gamma_olc = -0.188     # flat ORF, 60 deg arm angle
K_arm = 0.53           # sky-averaged response factor (from noise analysis)

def sr_clock_s_y(f):
    """Sr clock fractional frequency noise PSD S_y(f) in Hz^-1."""
    coeffs = noise.sr_clock_coeffs()
    return noise.noise_psd(f, coeffs)

def olc_t_gw_sq(f):
    """Sky-averaged |T_gw(f)|^2 — GW-induced fractional frequency coupling.
    T_gw = (2pi f L/c) * sinc(terms) -> ~ 2pi f L/c for small f
    Sky-averaged: |T|^2 ~ (2pi f L/c)^2 * K^2
    """
    f = np.asarray(f, dtype=float)
    t_base = 2.0 * np.pi * np.abs(f) * L_olc / c
    return t_base**2 * K_arm**2

def olc_s_corr(f, Omega_GW):
    """GW-induced fractional frequency PSD S_corr(f).
    S_corr(f) = (2 H_0^2 / pi^2) * Omega_GW * f^{-3} * |T|^2
    Units: Hz^-1 (fractional freq squared per Hz)
    """
    f = np.asarray(f, dtype=float)
    S_h = (2.0 * H_0**2 / np.pi**2) * Omega_GW * f**(-3.0)
    return S_h * olc_t_gw_sq(f)

def snr_per_hz(f, Omega_GW=1e-8, T_obs=1.0):
    """SNR spectral density.
    d(SNR^2)/df = 2 * T_obs * gamma^2 * S_corr^2 / S_y^2
    """
    f = np.asarray(f, dtype=float)
    S_corr = olc_s_corr(f, Omega_GW)
    S_y = sr_clock_s_y(f)
    dSNR2_df = 2.0 * T_obs * gamma_olc**2 * S_corr**2 / (S_y**2)
    dSNR_df = np.sqrt(np.maximum(dSNR2_df, 0.0))
    return dSNR_df, dSNR2_df, S_corr, S_y

def total_snr(f, Omega_GW, T_obs):
    """Integrated SNR = sqrt(integrate d(SNR^2)/df over f)."""
    _, dSNR2_df, _, _ = snr_per_hz(f, Omega_GW, T_obs)
    snr2 = np.trapezoid(dSNR2_df, f)
    return np.sqrt(max(snr2, 0.0))

# ---------------------------------------------------------------------------
# LISA comparison model (Liu et al. 2011, design sensitivity)
# ---------------------------------------------------------------------------

def lisa_strain_noise_psd(f):
    """LISA strain noise PSD S_h(f) [Hz^-1].
    Based on simplified design sensitivity from Liu et al. (2011).
    """
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-6)

    L_lisa = 2.5e9          # 2.5 Mm arm length
    f_star = 19.09e-3       # characteristic frequency

    # Simplified design curve (approximation)
    # Dominant: acceleration noise (3e-15 m/s2/rtHz) + displacement noise
    P_a = 3e-15 * (1.0 + (4e-3 / f)**2) / (1.0 + (f / 8e-3)**2)
    P_d = 1.5e-11

    # h = sqrt(P_a^2 / (2pi f)^4 + P_d^2) / L  -> strain sensitivity
    h_acc = P_a / ((2.0 * np.pi * f)**2)
    h_disp = P_d
    S_h = (h_acc**2 + h_disp**2) / L_lisa**2
    return S_h

def lisa_s_corr(f, Omega_GW):
    """LISA GW-induced phase PSD (in dimensionless units).
    LISA measures phase/strain directly: S_corr = (2 H_0^2 / pi^2) * Omega * f^{-3} * |T|^2
    where |T|^2 ~ (f/f_star)^2 for LISA (interferometer with long arm).
    """
    f = np.asarray(f, dtype=float)
    L_lisa = 2.5e9
    f_star_lisa = c / (2.0 * np.pi * L_lisa)  # ~ 20 mHz
    t_lisa_sq = ((2.0 * np.pi * np.abs(f) * L_lisa / c)**2)
    S_h = (2.0 * H_0**2 / np.pi**2) * Omega_GW * f**(-3.0)
    return S_h * t_lisa_sq

def lisa_snr_per_hz(f, Omega_GW=1e-7, T_obs=1.0):
    """LISA SNR spectral density."""
    f = np.asarray(f, dtype=float)
    S_corr = lisa_s_corr(f, Omega_GW)
    S_h_noise = lisa_strain_noise_psd(f)
    # For LISA, the noise is already in strain units
    # But we need to be careful: LISA phase noise -> fractional freq noise
    # LISA phase noise ~ 1.5e-11 m/rtHz -> freq noise ~ 2pi f * 1.5e-11
    # In fractional freq units: S_y_lisa = (2pi f * 1.5e-11 / L_lisa)^2 * L_lisa^2
    # Simplified: S_y_lisa = S_h_noise (strain noise in same units)
    S_y = S_h_noise
    gamma_lisa = 0.5
    dSNR2_df = 2.0 * T_obs * gamma_lisa**2 * S_corr**2 / (S_y**2)
    dSNR_df = np.sqrt(np.maximum(dSNR2_df, 0.0))
    return dSNR_df, dSNR2_df

# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_snr_vs_time(f, Omega_GW):
    """SNR vs observation time."""
    snr_all = []
    T_vals = np.logspace(3, 7.5, 50)
    for T_obs in T_vals:
        snr_all.append(total_snr(f, Omega_GW, T_obs))

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.semilogy(T_vals, snr_all, linewidth=2, label=f'OLC (Sr, L=10m)')

    # LISA: approximate curve at Omega_GW=1e-7
    T_ref = np.array([1e4, 3.15e7])
    # LISA estimate: SNR~10 at 1yr for Omega_GW=1e-7 (approximate)
    snr_lisa_ref = 10.0 * np.sqrt(T_ref / 3.15e7) * np.sqrt(Omega_GW / 1e-7)
    ax.semilogy(T_ref, snr_lisa_ref, '--', linewidth=2, label='LISA (est.)')

    ax.axhline(y=3.0, color='red', linestyle=':', linewidth=1, alpha=0.5, label='SNR = 3 (detection)')
    ax.set_xlabel('Observation time T_obs (s)')
    ax.set_ylabel(r'Total SNR')
    ax.set_title(f'OLC SGWB Detection SNR vs Time (Omega_GW = {Omega_GW})')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    plt.tight_layout()
    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_snr_vs_time.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_snr_vs_time.png")
    plt.close()
    return fig

def plot_snr_spectrum_comparison(Omega_GW):
    """Compare SNR spectral density for OLC and LISA."""
    f_olc = np.logspace(-3, 2, 500)
    f_lisa = np.logspace(-3, 2, 500)

    dSNR_df_olc, _, S_corr_olc, S_y_olc = snr_per_hz(f_olc, Omega_GW)

    # LISA
    _, dSNR2_lisa = lisa_snr_per_hz(f_lisa, 1e-7)  # Use Omega=1e-7 for LISA
    dSNR_df_lisa = np.sqrt(np.maximum(dSNR2_lisa, 0))

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(f_olc, dSNR_df_olc, linewidth=2, label='OLC (Sr, L=10m, Omega=1e-8)')

    mask_lisa = (f_lisa > 5e-4) & (f_lisa < 0.2)
    if np.any(mask_lisa):
        # Scale to same Omega_GW: SNR scales as Omega_GW, so just scale
        dSNR_scaled = dSNR_df_lisa * np.sqrt(Omega_GW / 1e-7)
        ax.plot(f_lisa[mask_lisa], dSNR_scaled[mask_lisa], '--', linewidth=2,
                label='LISA (Omega=1e-7, scaled)')

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel(r'dSNR/df (T_obs=1s)')
    ax.set_title('SNR Spectral Density: OLC vs LISA')
    ax.legend(fontsize=9)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_snr_spectrum.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_snr_spectrum.png")
    plt.close()
    return fig

def plot_olc_fbands():
    """OLC SNR distribution across frequency bands."""
    f = np.logspace(-3, 3, 500)
    Omega_GW = 1e-8
    T_obs = 3.15e7  # 1 year

    bands = [
        ('0.001-0.01 Hz', 0.001, 0.01),
        ('0.01-0.1 Hz', 0.01, 0.1),
        ('0.1-1 Hz', 0.1, 1.0),
        ('1-10 Hz', 1.0, 10.0),
        ('10-100 Hz', 10.0, 100.0),
        ('100-1000 Hz', 100.0, 1000.0),
    ]

    band_snrs = []
    for name, f_min, f_max in bands:
        mask = (f >= f_min) & (f < f_max)
        if np.sum(mask) < 3:
            continue
        f_band = f[mask]
        _, dSNR2_band, _, _ = snr_per_hz(f_band, Omega_GW, T_obs)
        snr2 = np.trapezoid(dSNR2_band, f_band)
        snr = np.sqrt(max(snr2, 0))
        band_snrs.append((name, snr))
        print(f"  SNR [{f_min}-{f_max}] (1yr, Omega={Omega_GW}): {snr:.3e}")

    labels = [x[0] for x in band_snrs]
    values = [x[1] for x in band_snrs]

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    x = np.arange(len(band_snrs))
    colors = ['#377eb8', '#ff7f00', '#4daf4a', '#e41a1c', '#984ea3', '#f781bf']
    bars = ax.bar(x, values, color=colors[:len(band_snrs)], alpha=0.7)
    ax.set_xlabel('Frequency Band')
    ax.set_ylabel(r'Total SNR (1yr, Omega_GW = 1e-8)')
    ax.set_title('SNR Distribution Across Frequency Bands (OLC)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yscale('log')

    for i, (name, val) in enumerate(band_snrs):
        if val > 0:
            ax.text(i, max(val * 3, 1e-40), f'{val:.3e}', ha='center', fontsize=6)

    plt.tight_layout()
    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_snr_fbands.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_snr_fbands.png")
    plt.close()
    return fig

def plot_coupling_analysis():
    """Show S_corr vs S_y — why OLC is insensitive to SGWB."""
    f = np.logspace(-3, 3, 500)
    Omega_GW = 1e-8

    S_corr, S_y = olc_s_corr(f, Omega_GW), sr_clock_s_y(f)
    ratio = S_corr / S_y

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(f, S_corr, linewidth=2, label='S_corr (GW-induced)')
    ax.plot(f, S_y, linewidth=2, label='S_y (Sr clock noise)')
    ax2 = ax.twinx()
    ax2.semilogy(f, ratio, 'r-', linewidth=2, label='S_corr/S_y (signal/noise)')

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('PSD (Hz$^{-1}$)')
    ax2.set_ylabel('Ratio S_corr / S_y', color='r')
    ax2.set_title(f'GW Signal vs Clock Noise (Omega_GW = {Omega_GW})')
    ax.set_xscale('log')
    ax.legend(loc='upper left', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    outpath = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_snr_coupling.png'
    plt.savefig(outpath, dpi=200)
    print(f"  Saved: olc_snr_coupling.png")
    plt.close()
    return fig

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("OLC SNR 综合计算器 v3 — SGWB 交叉关联信噪比")
    print("=" * 60)
    print(f"\nParameters: L={L_olc}m, Gamma={gamma_olc}, H_0={H_0:.2e} Hz")
    print(f"A_S = H_0^2/(2pi^2) = {A_S:.3e} Hz^-1")

    t0 = time.time()

    # Frequency range
    f = np.logspace(-3, 3, 1000)  # 0.001 Hz to 1 kHz

    # Check key quantities
    print(f"\nf range: {f[0]:.3e} - {f[-1]:.1f} Hz ({len(f)} points)")
    Omega_GW = 1e-8

    print(f"\n--- Key quantities check at selected f ---")
    for fi in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]:
        t_sq = olc_t_gw_sq(np.array([fi]))[0]
        S_c = olc_s_corr(np.array([fi]), Omega_GW)[0]
        S_n = sr_clock_s_y(np.array([fi]))[0]
        ratio = S_c / S_n if S_n > 0 else 0
        print(f"  f={fi:5.2f} Hz: |T|^2={t_sq:.3e}, S_corr={S_c:.3e}, S_y={S_n:.3e}, ratio={ratio:.3e}")

    # --- SNR vs observation time ---
    print(f"\n--- Total SNR (Omega_GW={Omega_GW}) ---")
    T_obs_vals = [3600.0, 86400.0, 3.15e7]  # 1h, 1d, 1yr
    for T_obs in T_obs_vals:
        snr = total_snr(f, Omega_GW, T_obs)
        T_hours = T_obs / 3600.0
        print(f"  T_obs = {T_hours:7.1f}h: SNR = {snr:.3e}")

    # --- SNR bands ---
    print(f"\n--- Frequency band breakdown (1yr) ---")
    T_obs_1yr = 3.15e7
    _, dSNR2, _, _ = snr_per_hz(f, Omega_GW, T_obs_1yr)
    total_snr2 = np.trapezoid(dSNR2, f)
    total_snr_1yr = np.sqrt(max(total_snr2, 0))
    print(f"  Total (integrated): SNR = {total_snr_1yr:.3e}")

    # --- LISA reference ---
    print(f"\n--- LISA reference ---")
    for fi in [1e-3, 5e-3, 1e-2, 5e-2, 1e-1]:
        sh = lisa_strain_noise_psd(np.array([fi]))[0]
        print(f"  LISA S_h@{fi:.3f} Hz = {sh:.3e} Hz^-1")

    # --- Plots ---
    print(f"\n--- Generating plots ---")
    plot_snr_vs_time(f, Omega_GW)
    plot_snr_spectrum_comparison(Omega_GW)
    plot_olc_fbands()
    plot_coupling_analysis()

    # Save data
    _, dSNR2, S_corr, S_y = snr_per_hz(f, Omega_GW, T_obs_1yr)
    dSNR_df = np.sqrt(np.maximum(dSNR2, 0))
    np.save('/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/olc_snr_data.npy', {
        'f': f,
        'gamma': gamma_olc,
        'S_y': sr_clock_s_y(f),
        'S_corr': S_corr,
        'S_y_noise': S_y,
        'Omega_GW': Omega_GW,
        'dSNR_df': dSNR_df,
        'total_snr_1yr': total_snr_1yr,
    })
    print("  Saved: olc_snr_data.npy")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    print("=" * 60)

if __name__ == '__main__':
    main()
