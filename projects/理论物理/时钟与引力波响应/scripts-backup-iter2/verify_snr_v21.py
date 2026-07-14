#!/usr/bin/env python3
"""
v21 SNR convention resolution and N_sat re-computation
======================================================

CONVENTION DECISION: Adopt Hu convention (paper's convention).
- S_h(f) = (3H0^2 / 2pi^2) * Omega_GW / f^3   (two-sided strain PSD)
- P_N(f) = h0 + h-1/f + h2*f^2                 (clock noise)
- S_GW,yy(f) = (1/4) * |T(f)|^2 * P_h(f)       (projection)
- The (1/16) factor from squaring the 1/4 projection is NOT applied in the
  paper's main numerical results (acknowledged but omitted).

This script:
1. Verifies v19 results (SNR = 2.30e-6)
2. Applies the (1/16) factor to show corrected SNR
3. Computes N_sat for all Omega_GW values
4. Documents dimensional analysis
"""
import numpy as np

c = 299792458.0

# =============================================================================
# Parameters (from paper)
# =============================================================================
H0 = 2.18e-18        # Hz (Hubble constant)
Omega_GW = 1e-8
Gamma = 0.5          # ORF (sky-averaged, from paper)
K_sky = 0.53         # sky-averaged response factor
L = 0.17e9           # 0.17 Gm = 170 Mm
T_obs = 3.2e7        # 1 year in seconds
df_frac = 0.1        # frequency bin width fraction

# Noise model (Sr clock noise from paper)
h0 = 2e-34           # Hz^-1 (white frequency noise)
h_1 = 1e-35          # Hz (flicker frequency noise)
h2 = 1e-44           # Hz^2 (white phase noise)

# =============================================================================
# Numerical integration grid
# =============================================================================
f_min = 1e-4         # Hz
f_max = 1e3          # Hz
N_pts = 500000
f = np.logspace(np.log10(f_min), np.log10(f_max), N_pts)
df = np.gradient(f)

# =============================================================================
# Noise model
# =============================================================================
def P_N(f):
    f = np.maximum(f, 1e-20)
    return h0 + h_1 / f + h2 * f**2

# =============================================================================
# Transfer function
# T(f) = (2*pi*f*L/c) * K_sky
# |T|^4 = (2*pi*f*L/c)^4 * K_sky^4
# =============================================================================
def T(f):
    t_base = 2.0 * np.pi * f * L / c
    return t_base * K_sky

# =============================================================================
# Hu convention: P_h(f) = (3*H0^2 / 2*pi^2) * Omega_GW / f^3
# =============================================================================
def P_h_Hu(f):
    A = 3.0 * H0**2 / (2.0 * np.pi**2)
    return A * Omega_GW / f**3

# =============================================================================
# SNR computation (Hu convention)
# =============================================================================
print("=" * 80)
print("v21 SNR CONVENTION RESOLUTION - Hu Convention")
print("=" * 80)

print("\nConvention: Hu PRD (paper's convention)")
print(f"  H0 = {H0} Hz")
print(f"  P_h = (3H0^2/2pi^2) * Omega_GW / f^3")
print(f"  3H0^2/2pi^2 = {3*H0**2/(2*np.pi**2):.4e} Hz^-2")

# Compute constants
A_Hu = 3.0 * H0**2 / (2.0 * np.pi**2)  # Hz^-2

# GW spectrum
S_h = A_Hu * Omega_GW / f**3

# |T|^4
T_vals = T(f)
T4 = T_vals**4

# Noise
PN = P_N(f)

# SNR^2 spectral density
# d(SNR^2)/df = 2 * T_obs * Gamma^2 * S_corr^2 / P_N^2
# where S_corr = S_h * |T|^2 (correlation function)
S_corr = S_h * T_vals**2  # not S_h * |T|^2 for SNR, need to check
# Actually: S_corr(f) = S_h(f) * |T(f)|^2 in script notation
# But in paper notation: S_GW,yy = (1/4) * |T|^2 * P_h
# The correlation is between two detectors, each with projection 1/4.
# For single detector analysis (as in paper), the cross-correlation is just
# the expectation value of the product, which equals S_h * |T|^2.

# Paper's SNR^2 formula (Eq. 1200):
# SNR^2 = 2 * T_obs * Gamma^2 * integral[ (S_h * |T|^2)^2 / P_N^2 df ]
#       = 2 * T_obs * Gamma^2 * integral[ S_h^2 * |T|^4 / P_N^2 df ]

integrand = (S_h**2) * T4 / (PN**2)

# Check integrand is same as paper's formula
# Paper's formula pulls out constants: |T|^4 * f^-6 / P_N^2
# with S_h^2 = A_Hu^2 * Omega_GW^2 * f^-6
# So integrand = A_Hu^2 * Omega_GW^2 * f^-6 * |T|^4 / P_N^2
integrand_paper_style = (A_Hu**2) * (Omega_GW**2) * (f**(-6)) * T4 / (PN**2)

print(f"\nIntegrand check (should be identical):")
print(f"  S_h^2*|T|^4/P_N^2 at f=0.1: {integrand[np.argmin(np.abs(f-0.1))]:.4e}")
print(f"  A^2*Om^2*f^-6*|T|^4/P_N^2 at f=0.1: {integrand_paper_style[np.argmin(np.abs(f-0.1))]:.4e}")
print(f"  Match: {np.allclose(integrand, integrand_paper_style)}")

# Integration
integral_val = np.trapezoid(integrand, f)

print(f"\nIntegral[S_h^2 * |T|^4 / P_N^2 df] = {integral_val:.4e}")

# Dimensional analysis
print(f"\nDimensional analysis:")
print(f"  S_h = A_Hu * Omega_GW / f^3")
print(f"    A_Hu = 3H0^2/(2pi^2) has units: Hz^-2")
print(f"    S_h units: Hz^-2 * dimensionless * Hz^-3 = Hz^-5")
print(f"  S_h^2 units: Hz^-10")
print(f"  |T|^4: dimensionless")
print(f"  P_N units: Hz^-1")
print(f"  P_N^2 units: Hz^-2")
print(f"  Integrand units: Hz^-10 * 1 / Hz^-2 = Hz^-8")
print(f"  Integral over df: Hz^-8 * Hz = Hz^-7")

SNR2_pre = 2.0 * T_obs * Gamma**2
print(f"\nPre-factor: 2*T_obs*Gamma^2 = {SNR2_pre:.4e}")
print(f"SNR^2 = {SNR2_pre} * {integral_val:.4e} = {SNR2_pre * integral_val:.4e}")
SNR = np.sqrt(SNR2_pre * integral_val)
print(f"SNR = {SNR:.4e}")

# =============================================================================
# Check: Paper's claimed value
# =============================================================================
print(f"\n" + "=" * 80)
print("COMPARISON WITH PAPER CLAIMS")
print("=" * 80)
print(f"  Paper line 1272: SNR_single = 2.30e-6")
print(f"  Our calculation: SNR = {SNR:.4e}")
print(f"  Match: {'YES' if abs(SNR - 2.30e-6) < 0.05e-6 else 'NO - discrepancy!'}")

# =============================================================================
# (1/16) FACTOR ANALYSIS
# =============================================================================
print(f"\n" + "=" * 80)
print("(1/16) FACTOR ANALYSIS")
print("=" * 80)

# The paper acknowledges the (1/16) factor at line 1218:
# "纳入(1/16)因子后，SNR将乘以1/4"
# This means the (1/16) factor reduces SNR by a factor of 1/4 (not 1/16).
# This is because SNR^2 gets a factor of 1/16, so SNR gets a factor of 1/4.

print("\nProvenance of the (1/16) factor:")
print("  1. GW power spectrum projection: S_GW,yy = (1/4) * |T|^2 * P_h")
print("     The 1/4 factor comes from the polarization tensor projection.")
print("  2. Cross-correlation: S_corr^2 involves (1/4)^2 = 1/16")
print("  3. SNR^2 = 2 T_obs Gamma^2 * integral[S_corr^2/P_N^2]")
print("     If S_corr has 1/4 factor, SNR^2 has 1/16 factor.")
print("  4. SNR = sqrt(SNR^2), so SNR has 1/4 factor.")

# The (1/16) factor modifies SNR^2:
SNR2_corrected = SNR2_pre * integral_val / 16.0
SNR_corrected = np.sqrt(SNR2_corrected)
print(f"\nWith (1/16) factor applied:")
print(f"  SNR^2 = {SNR2_pre * integral_val:.4e} / 16 = {SNR2_corrected:.4e}")
print(f"  SNR = {SNR_corrected:.4e}")
print(f"  Reduction factor: {SNR_corrected / SNR:.4f} (expected 0.25)")

# =============================================================================
# N_SAT TABLE
# =============================================================================
print(f"\n" + "=" * 80)
print("N_SAT TABLE (SNR=10 threshold)")
print("=" * 80)
print(f"\nN_sat = N * (SNR_per_sat / 10)^2 where N is the number of satellites")
print(f"For a single detector configuration, N_sat represents the minimum")
print(f"number of atoms or effective detector elements needed for SNR >= 10.")
print(f"")

# Actually, let's re-read what N_sat means. The paper says:
# "N_sat = 1.84e6 (Omega_GW = 10^-8)"
# This is likely the number of satellites or detector arms.
# Let me compute it properly.

# If we need N_det detectors to reach SNR = 10:
# SNR_total = sqrt(N_det) * SNR_single
# 10 = sqrt(N_det) * SNR_single
# N_det = (10 / SNR_single)^2

for ogw in [1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7, 1e-6]:
    # Recompute with this Omega_GW
    S_h_ogw = A_Hu * ogw / f**3
    integrand_ogw = (S_h_ogw**2) * T4 / (PN**2)
    integral_ogw = np.trapezoid(integrand_ogw, f)
    snr_single = np.sqrt(SNR2_pre * integral_ogw)
    snr_single_16 = np.sqrt(SNR2_pre * integral_ogw / 16.0)

    # N_sat to reach SNR = 10
    n_sat_no16 = (10.0 / snr_single)**2
    n_sat_with16 = (10.0 / snr_single_16)**2

    print(f"\n  Omega_GW = {ogw:.0e}:")
    print(f"    SNR_single (no 1/16) = {snr_single:.3e}")
    print(f"    SNR_single (with 1/16) = {snr_single_16:.3e}")
    print(f"    N_sat (no 1/16) = {n_sat_no16:.2e}")
    print(f"    N_sat (with 1/16) = {n_sat_with16:.2e}")

# =============================================================================
# FREQUENCY CONTRIBUTION
# =============================================================================
print(f"\n" + "=" * 80)
print("FREQUENCY CONTRIBUTION TO SNR^2")
print("=" * 80)
bands = [
    (1e-4, 1e-2),
    (1e-2, 0.1),
    (0.1, 1.0),
    (1.0, 10.0),
    (10.0, 100.0),
    (100.0, 1000.0),
]
total = SNR2_pre * integral_val
for f_lo, f_hi in bands:
    mask = (f >= f_lo) & (f < f_hi)
    contrib = SNR2_pre * np.trapezoid(integrand[mask], f[mask])
    print(f"  [{f_lo:.0e}, {f_hi:.0e}] Hz: {contrib:.4e} ({100*contrib/total:.1f}%)")

# =============================================================================
# OPTIMAL FREQUENCY
# =============================================================================
print(f"\n" + "=" * 80)
print("OPTIMAL FREQUENCY")
print("=" * 80)
dSNR2_df = SNR2_pre * integrand
f_peak = f[np.argmax(dSNR2_df)]
print(f"  Peak d(SNR^2)/df at f = {f_peak:.3e} Hz")

# =============================================================================
# SUMMARY
# =============================================================================
print(f"\n" + "=" * 80)
print("v21 SUMMARY")
print("=" * 80)
print(f"\nConvention adopted: Hu (1/8pi normalization, 3H0^2/2pi^2, two-sided)")
print(f"SNR_single (Omega_GW=1e-8, no 1/16): {SNR:.4e}")
print(f"SNR_single (Omega_GW=1e-8, with 1/16): {SNR_corrected:.4e}")
print(f"\nPaper's value: 2.30e-6")
print(f"Our value (no 1/16): {SNR:.4e} -> MATCH: {'YES' if abs(SNR - 2.30e-6) < 0.05e-6 else 'NO'}")
print(f"\nIMPORTANT: The paper acknowledges the (1/16) factor but does NOT apply it")
print(f"to the main numerical results. The corrected SNR with (1/16) is {SNR_corrected:.2e},")
print(f"which is a factor of {SNR/SNR_corrected:.1f}x smaller.")
print(f"\nN_sat (with 1/16, Omega_GW=1e-8): {(10.0/SNR_corrected)**2:.2e}")
print(f"This is a factor of 16x larger than without the correction.")
