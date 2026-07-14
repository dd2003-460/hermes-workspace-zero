#!/usr/bin/env python3
"""
Space-based OLC SNR Analysis for GW detection
==============================================

Per Schaffrath (2025) & Gaudio (2026), ground-based stationary clocks have
zero leading-order GW sensitivity. Only freely-falling (satellite) clocks
satisfy the geodesic equation and are sensitive to GW.

This script performs a complete SNR analysis for a space-based OLC constellation
following Lou et al. (2026) parameters:
  - 4 satellites, solar orbit (60 degree inclination plane)
  - Arm lengths: 0.17 Gm, 2.5 Gm, 3 Gm (three OLC scenarios)
  - Clock type: Sr lattice clock, ν = 430 THz
  - Noise model: QPN + PSN + AN

Compares against LISA, Taiji, TianQin in the same framework.

Input: Lou thesis chapter 5, section 5.1-5.3 parameters
Output: SNR curves, sensitivity comparison plots
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# Physical constants
# ============================================================================
c = 299792458.0
G = 6.674e-11
h_bar = 1.055e-34
H_0 = 67.4 * 1000.0 / 3.096e19  # ~2.18e-18 Hz
A_S = H_0**2 / (2.0 * np.pi**2)  # strain-to-freq factor

# ============================================================================
# Space-based OLC parameters (Lou et al. 2026, chapter 5)
# ============================================================================
OLC_CONF = {
    "name": "OLC space (Lou)",
    "nu": 430e12,             # optical frequency 430 THz (Sr line)
    "N_atoms": 7e6,           # atom number
    "T_interp": 160.0,        # interrogation time (s)
    "eta": 0.5,               # detection efficiency
    "delta_L": 0.030,         # laser linewidth 30 mHz
    "P_L": 3e-12,             # laser power 3 pW
    "S_L": 9e-30,             # acceleration noise 9 fm^2 s^-4 Hz^-1
    "arm_lengths": {
        "L1": 0.17e9,         # 170 Mm (small constellation)
        "L2": 2.5e9,          # 2.5 Gm (medium, LISA-scale)
        "L3": 3.0e9,          # 3 Gm (Taiji-scale)
    },
    # ORF values from our analysis for 60 deg PTA-like
    "gamma": -0.188,          # flat ORF for 60 deg configuration
    "K_sky": 0.53,            # sky-averaged response
    "T_obs": 3.15e7,          # 1 year
    "df_frac": 0.1,           # frequency bin width = f/10
}

# ============================================================================
# Space interferometer parameters (Table 5-1, Lou thesis)
# ============================================================================
INTERFEROMETERS = {
    "LISA": {
        "L": 2.5e9,
        "A2OMS": 225e-24,       # pm^2/Hz -> m^2/Hz
        "A2acc": 9e-30,         # (fm/s^2)^2/Hz -> (m/s^2)^2/Hz
    },
    "Taiji": {
        "L": 3.0e9,
        "A2OMS": 64e-24,
        "A2acc": 9e-30,
    },
    "TianQin": {
        "L": 0.17e9,
        "A2OMS": 1e-24,
        "A2acc": 1e-30,
    },
}

# ============================================================================
# Space OLC noise model (section 5.1.2)
# ============================================================================
def olc_noise_qpn(f):
    """Quantum Projection Noise PSD [Hz^-1].
    N_QPN = 2 / ((2pi nu)^2 * N * T)
    """
    nu = OLC_CONF["nu"]
    N = OLC_CONF["N_atoms"]
    T = OLC_CONF["T_interp"]
    return 2.0 / ((2.0 * np.pi * nu)**2 * N * T)


def olc_noise_psn(f):
    """Photon Shot Noise PSD [Hz^-1].
    N_PSN = 2 * f^2 * delta_L / (nu^2 * [(2pi f)^2 + eta * P_L * delta_L / (2pi h nu)])
    """
    nu = OLC_CONF["nu"]
    delta_L = OLC_CONF["delta_L"]
    eta = OLC_CONF["eta"]
    P_L = OLC_CONF["P_L"]
    f = np.asarray(f, dtype=float)
    denom = (2.0 * np.pi * f)**2 + eta * P_L * delta_L / (2.0 * np.pi * h_bar * nu)
    return 2.0 * f**2 * delta_L / (nu**2 * np.maximum(denom, 1e-50))


def olc_noise_an(f, L=1.0):
    """Acceleration Noise PSD [Hz^-1].
    N_AN = 2 * (L/c)^2 * S_L / ((2pi f)^4)
    Note: S_L is per arm, total AN from two arms is factor of 2.
    """
    S_L = OLC_CONF["S_L"]
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-20)
    return 2.0 * (L / c)**2 * S_L / ((2.0 * np.pi * f)**4)


def olc_total_noise(f, L=1.0):
    """Total OLC noise PSD = QPN + PSN + AN."""
    f_arr = np.asarray(f, dtype=float)
    N_total = olc_noise_qpn(f_arr) + olc_noise_psn(f_arr) + olc_noise_an(f_arr, L)
    return N_total


# ============================================================================
# Interferometer noise model (Michelson TDI, section 5.1.1)
# ============================================================================
def interferometer_noise_psd(f, A2oms, A2acc, L):
    """LISA/Taiji/TianQin strain noise PSD [Hz^-1].
    N_m = A2oms / L^2 + 2(1+cos^2(w pi f L/c)) * A2acc / ((2pi f)^4 * L^2)
    Strain sensitivity h_n = sqrt(N_m / R(f))
    """
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-20)
    N_oms = A2oms / L**2
    term = 2.0 * (1.0 + np.cos(2.0 * np.pi * f * L / c)**2) * A2acc / ((2.0 * np.pi * f)**4 * L**2)
    return N_oms + term


# ============================================================================
# GW coupling
# ============================================================================
def olc_coupling_sq(f, L):
    """Sky-averaged |T_gw(f)|^2 for space-based OLC.
    No trap suppression — freely falling satellites satisfy geodesic equation.
    |T|^2 = (2pi f L/c)^2 * K_sky^2 (flat space approximation for ORF)
    """
    f = np.asarray(f, dtype=float)
    t_base = 2.0 * np.pi * np.abs(f) * L / c
    return t_base**2 * OLC_CONF["K_sky"]**2


def GW_coupling_sq(f):
    """Pure GW strain PSD from SGWB.
    S_h(f) = (2 H_0^2 / pi^2) * Omega_GW * f^{-3}
    """
    f = np.asarray(f, dtype=float)
    return (2.0 * H_0**2 / np.pi**2) * f**(-3.0)


# ============================================================================
# SNR computation (Sacks 1967, Vecchio 1997)
# ============================================================================
def olc_snr_per_hz(f, Omega_GW, L):
    """SNR spectral density for space OLC.
    d(SNR^2)/df = 2 * T_obs * gamma^2 * S_corr^2 / S_y^2

    S_corr(f) = S_h(f) * |T|^2
    S_y^2(f) = N_total(f)
    """
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-20)
    S_h = GW_coupling_sq(f) * Omega_GW
    S_corr = S_h * olc_coupling_sq(f, L)
    S_y = olc_total_noise(f, L)

    dSNR2_df = 2.0 * OLC_CONF["T_obs"] * OLC_CONF["gamma"]**2 * S_corr**2 / np.maximum(S_y**2, 1e-100)
    dSNR_df = np.sqrt(np.maximum(dSNR2_df, 0.0))
    return dSNR_df, dSNR2_df, S_corr, S_y


def total_snr(f, Omega_GW, L):
    """Integrated SNR = sqrt(integrate d(SNR^2)/df)."""
    _, dSNR2_df, _, _ = olc_snr_per_hz(f, Omega_GW, L)
    snr2 = np.trapezoid(dSNR2_df, f)
    return np.sqrt(max(snr2, 0.0))


def interferometer_snr_per_hz(f, Omega_GW, L, A2oms, A2acc):
    """SNR spectral density for space interferometer.
    d(SNR^2)/df = 2 * T_obs * gamma^2 * S_corr^2 / S_noise^2
    S_h_noise^2 = interferometer_noise_psd(f)
    """
    f = np.asarray(f, dtype=float)
    f = np.maximum(f, 1e-20)
    S_h = GW_coupling_sq(f) * Omega_GW
    # Interferometer measures phase directly: coupling ~ (2pi f L/c)^2
    t_int_sq = (2.0 * np.pi * f * L / c)**2
    S_corr = S_h * t_int_sq
    S_h_noise = interferometer_noise_psd(f, A2oms, A2acc, L)

    gamma_int = 0.5  # sky-averaged ORF for interferometers (approx.)
    dSNR2_df = 2.0 * OLC_CONF["T_obs"] * gamma_int**2 * S_corr**2 / np.maximum(S_h_noise**2, 1e-100)
    dSNR_df = np.sqrt(np.maximum(dSNR2_df, 0.0))
    return dSNR_df, dSNR2_df


# ============================================================================
# Main analysis
# ============================================================================
def analyze_all():
    """Run full space OLC SNR analysis and produce plots."""
    f_min, f_max = 1e-15, 10.0  # Hz (covers from ~ GW wavelength to 1 Hz)
    f = np.logspace(np.log10(f_min), np.log10(f_max), 2000)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # === Plot 1: SNR spectral density for different arm lengths ===
    ax1 = axes[0, 0]
    Omega_GW = 1e-8
    colors = ["blue", "green", "red"]
    labels = ["0.17 Gm", "2.5 Gm", "3.0 Gm"]
    for i, (name, L) in enumerate(OLC_CONF["arm_lengths"].items()):
        dSNR_df, _, _, _ = olc_snr_per_hz(f, Omega_GW, L)
        ax1.semilogy(f, dSNR_df, linewidth=2, color=colors[i], label=f"OLC L={name}")

    # LISA SNR for comparison
    LISA = INTERFEROMETERS["LISA"]
    dSNR_L, _ = interferometer_snr_per_hz(f, Omega_GW, LISA["L"],
                                               LISA["A2OMS"], LISA["A2acc"])
    ax1.semilogy(f, dSNR_L, linewidth=2, color="cyan", linestyle="--",
                 label=f"LISA (L=2.5 Gm)")

    ax1.set_xlabel("Frequency [Hz]")
    ax1.set_ylabel("d(SNR)/d√[Hz]")
    ax1.set_title(f"SNR spectral density (Ω_GW={Omega_GW}, 1 yr)")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # === Plot 2: Total SNR vs observation time ===
    ax2 = axes[0, 1]
    L_vals = list(OLC_CONF["arm_lengths"].values())
    T_obs_vals = np.logspace(5, 8, 50)  # 1 day to 100 years

    for L in L_vals:
        snrs = []
        for T in T_obs_vals:
            # SNR scales as sqrt(T_obs)
            dSNR_df, _, _, _ = olc_snr_per_hz(f, Omega_GW, L)
            # Recompute with this T_obs
            _, dSNR2_df, _, _ = olc_snr_per_hz(f, Omega_GW, L)
            snr2_ref = np.trapezoid(dSNR2_df, f)
            snr_scaled = np.sqrt(max(snr2_ref, 0) * T / OLC_CONF["T_obs"])
            snrs.append(snr_scaled)
        ax2.semilogy(T_obs_vals, snrs, linewidth=2, color=colors[L_vals.index(L)],
                     label=f"OLC L={list(OLC_CONF['arm_lengths'].keys())[L_vals.index(L)]}")

    # LISA SNR vs time
    LISA = INTERFEROMETERS["LISA"]
    dSNR_L, dSNR2_L = interferometer_snr_per_hz(f, Omega_GW, LISA["L"],
                                                  LISA["A2OMS"], LISA["A2acc"])
    snr2_L_ref = np.trapezoid(dSNR2_L, f)
    snr_L = np.sqrt(max(snr2_L_ref, 0) * T_obs_vals / OLC_CONF["T_obs"])
    ax2.semilogy(T_obs_vals, snr_L, linewidth=2, color="cyan", linestyle="--",
                 label="LISA")

    ax2.set_xlabel("Observation time [s]")
    ax2.set_ylabel("Total SNR")
    ax2.set_title(f"SNR vs T_obs (Ω_GW={Omega_GW})")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # === Plot 3: Sensitivity curves h_n(f) ===
    ax3 = axes[1, 0]
    for name, L in OLC_CONF["arm_lengths"].items():
        N_total = olc_total_noise(f, L)
        h_n_olc = np.sqrt(N_total / OLC_CONF["T_obs"])
        # Apply ORF and coupling: effective strain sensitivity
        h_eff = h_n_olc / np.sqrt(2 * OLC_CONF["gamma"]**2 * olc_coupling_sq(f, L) / np.maximum(GW_coupling_sq(f), 1e-100))
        ax3.semilogy(f, h_eff, linewidth=2, color=colors[L in OLC_CONF["arm_lengths"].values()],
                     label=f"OLC L={name}")

    # Interferometer sensitivities
    for iname, (iname_, ipar) in enumerate(INTERFEROMETERS.items()):
        h_n_int = np.sqrt(interferometer_noise_psd(f, ipar["A2OMS"], ipar["A2acc"], ipar["L"]))
        colors_int = ["magenta", "orange", "brown"]
        ax3.semilogy(f, h_n_int, linewidth=2, color=colors_int[iname],
                     linestyle="--", label=f"{iname_} (L={ipar['L']/1e9:.2f} Gm)")

    ax3.set_xlabel("Frequency [Hz]")
    ax3.set_ylabel("Effective strain sensitivity [Hz⁻¹/²]")
    ax3.set_title("Strain sensitivity comparison (1 yr)")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # === Plot 4: Noise budget breakdown for 2.5 Gm arm ===
    ax4 = axes[1, 1]
    L_mid = OLC_CONF["arm_lengths"]["L2"]
    N_qpn = olc_noise_qpn(f)
    N_psn = olc_noise_psn(f)
    N_an = olc_noise_an(f, L_mid)

    N_qpn_full = np.full_like(f, np.sqrt(N_qpn))
    N_total_arr = np.sqrt(N_qpn + N_psn + N_an)
    ax4.loglog(f, N_qpn_full, linewidth=2, label="QPN")
    ax4.loglog(f, np.sqrt(N_psn), linewidth=2, label="PSN")
    ax4.loglog(f, np.sqrt(N_an), linewidth=2, label="Acceleration noise")
    ax4.loglog(f, N_total_arr, linewidth=2, color="black",
               label="Total")

    ax4.set_xlabel("Frequency [Hz]")
    ax4.set_ylabel("Noise PSD [Hz⁻¹/²]")
    ax4.set_title(f"Space OLC noise budget (L={L_mid/1e9:.1f} Gm)")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/space_olc_snr_comparison.png",
                dpi=150, bbox_inches="tight")
    print(f"Plot saved: space_olc_snr_comparison.png")

    # === Print key numbers ===
    print("\n" + "=" * 60)
    print("SPACE OLC SNR ANALYSIS RESULTS")
    print("=" * 60)
    for name, L in OLC_CONF["arm_lengths"].items():
        snr_val = total_snr(f, Omega_GW, L)
        dSNR, _, _, _ = olc_snr_per_hz(f, Omega_GW, L)
        peak_freq = f[np.argmax(dSNR)]
        LISA_v = INTERFEROMETERS["LISA"]
        snr_lisa = total_snr(f, Omega_GW, LISA_v["L"]) if L == LISA_v["L"] else None
        print(f"\nOLC L={name} ({L/1e9:.2f} Gm):")
        print(f"  SNR(Ω_GW={Omega_GW}, 1yr) = {snr_val:.2e}")
        print(f"  Peak SNR frequency = {peak_freq:.2e} Hz")
        if snr_lisa is not None:
            print(f"  LISA SNR (same param) = {snr_lisa:.2e}")
            print(f"  Ratio OLC/LISA = {snr_val/snr_lisa:.2e}")
    print("=" * 60)

    return fig


# ============================================================================
# Interactive run
# ============================================================================
if __name__ == "__main__":
    fig = analyze_all()

    # Also print the SNR for all Ω_GW values
    f_full = np.logspace(-15, np.log10(10.0), 2000)
    print("\n" + "=" * 60)
    print("SNR at different Ω_GW values (L=2.5 Gm, 1 yr observation)")
    print("=" * 60)
    for ogw in [1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5]:
        snr_val = total_snr(f_full, ogw, OLC_CONF["arm_lengths"]["L2"])
        print(f"  Ω_GW = {ogw:.0e}: SNR = {snr_val:.4f}")
    print("=" * 60)

    print(f"\nPeak frequencies for Ω_GW={1e-8}:")
    for name, L in OLC_CONF["arm_lengths"].items():
        dSNR, _, _, _ = olc_snr_per_hz(f_full, 1e-8, L)
        peak = f_full[np.argmax(dSNR)]
        print(f"  L={name}: f_peak = {peak:.2e} Hz, SNR = {total_snr(f_full, 1e-8, L):.4f}")
