#!/usr/bin/env python3
"""
v19 independent verification of the paper's SNR claims.
Compares:
  1. The paper's formula (with |T|^4 * f^-6 / P_N^2)
  2. The script's formula (with |T|^2 coupling, no f^-6)
  3. Direct dimensional analysis
"""
import numpy as np

c = 299792458.0
G = 6.674e-11
h_bar = 1.055e-34

# === Parameters ===
H0 = 2.18e-18  # Hz
Omega_GW = 1e-8
gamma = 0.5    # ORF (paper uses Gamma=0.5, NOT -0.188)
K_sky = 0.53
L = 0.17e9     # 0.17 Gm = 170 Mm
T_obs = 3.2e7  # 1 year
df_frac = 0.1

# === Noise model (from paper: Sr clock noise) ===
h0 = 2e-34     # Hz^-1
h_1 = 1e-35    # Hz
h2 = 1e-44     # Hz^2

def P_N_paper(f):
    """Paper noise model: h0 + h_1/f + h2*f^2"""
    f = np.maximum(f, 1e-20)
    return h0 + h_1 / f + h2 * f**2

def P_N_script(f):
    """Script noise model: QPN + PSN + AN (from 07-space-olc-snr.py)"""
    nu = 430e12
    N_atoms = 7e6
    T_interp = 160.0
    delta_L = 0.030  # mHz
    eta = 0.5
    P_L = 3e-12
    S_L = 9e-30

    # QPN
    N_QPN = 2.0 / ((2.0 * np.pi * nu)**2 * N_atoms * T_interp)

    # PSN
    denom = (2.0 * np.pi * f)**2 + eta * P_L * delta_L / (2.0 * np.pi * h_bar * nu)
    N_PSN = 2.0 * f**2 * delta_L / (nu**2 * np.maximum(denom, 1e-50))

    # AN
    N_AN = 2.0 * (L / c)**2 * S_L / ((2.0 * np.pi * f)**4)

    return N_QPN + N_PSN + N_AN

# === Transfer functions ===
def T_paper(f):
    """Paper transfer function: T ~ (2pi*f*L/c) * K_sky
    So |T|^4 = (2pi*f*L/c)^4 * K_sky^4
    """
    t_base = 2.0 * np.pi * f * L / c
    return t_base * K_sky

def T_script(f):
    """Script coupling: |T|^2 = (2pi*f*L/c)^2 * K_sky^2
    So |T| = 2pi*f*L/c * K_sky (same as paper for the linear term)
    """
    t_base = 2.0 * np.pi * f * L / c
    return t_base * K_sky

# === GW PSD conventions ===
def P_h_hu(f):
    """Hu convention: (3H0^2 / 2pi^2) * Omega_GW / f^3"""
    return (3.0 * H0**2 / (2.0 * np.pi**2)) * Omega_GW / f**3

def P_h_script(f):
    """Script convention: (2H0^2 / pi^2) * Omega_GW * f^-3"""
    return (2.0 * H0**2 / np.pi**2) * Omega_GW * f**(-3.0)

# === Integration grid ===
f_min = 1e-4
f_max = 1e3
N_pts = 500000
f = np.logspace(np.log10(f_min), np.log10(f_max), N_pts)
df = np.gradient(f)

# ====================================================================
# PAPER'S FORMULA (Eq. 1204, 1247)
# SNR^2 = 2 T_obs * Gamma^2 * Omega_GW^2 * (3H0^2/2pi^2)^2
#         * Integral[ |T|^4 * f^-6 / P_N^2 df ]
# ====================================================================
def integral_paper():
    """Integral from the paper: |T|^4 * f^-6 / P_N^2"""
    T = T_paper(f)
    T4 = T**4
    PN = P_N_paper(f)

    integrand = T4 * (f**(-6)) / (PN**2)

    # Numerical integration
    integral_val = np.trapezoid(integrand, f)
    return integral_val, integrand

# ====================================================================
# SCRIPT'S FORMULA
# S_corr = S_h * |T|^2 where S_h = (2H0^2/pi^2) * Omega_GW * f^-3
# dSNR^2/df = 2 T_obs * Gamma^2 * S_corr^2 / S_y^2
#           = 2 T_obs * Gamma^2 * S_h^2 * |T|^4 / S_y^2
# Note: S_h^2 ~ f^-6, so this ALSO has f^-6 scaling!
# ====================================================================
def integral_script():
    """Integral from the script: S_h^2 * |T|^4 / S_y^2"""
    S_h = P_h_script(f)
    T = T_script(f)
    T4 = T**4
    S_y = P_N_script(f)

    integrand = (S_h**2) * T4 / (S_y**2)

    integral_val = np.trapezoid(integrand, f)
    return integral_val, integrand

# ====================================================================
# Run calculations
# ====================================================================
print("=" * 80)
print("v19 INDEPENDENT VERIFICATION")
print("=" * 80)

# --- Paper integral ---
print("\n--- Paper Formula (Eq. 1204) ---")
print(f"  Gamma = {gamma}")
print(f"  H0 = {H0} Hz")
print(f"  (3H0^2/2pi^2)^2 = {(3*H0**2/(2*np.pi**2))**2:.4e}")
print(f"  P_N model: h0={h0}, h_1={h_1}, h2={h2}")

integral_paper_val, integrand_paper = integral_paper()
print(f"\n  Integral[|T|^4 * f^-6 / P_N^2 df] = {integral_paper_val:.4e}")
print(f"  Dimensional check:")
print(f"    |T|^4: dimensionless^4")
print(f"    f^-6: Hz^-6")
print(f"    P_N^2: (Hz^-1)^2 = Hz^-2")
print(f"    Integrand: Hz^-6 / Hz^-2 = Hz^-4")
print(f"    Integral over df: Hz^-4 * Hz = Hz^-3")
print(f"    But paper claims Hz^-5 -- INCONSISTENT!")

# Paper SNR calculation
paper_snr2 = 2 * T_obs * gamma**2 * Omega_GW**2 * (3*H0**2/(2*np.pi**2))**2 * integral_paper_val
paper_snr = np.sqrt(paper_snr2)
print(f"\n  SNR^2 = 2*T_obs*Gamma^2*Omega_GW^2*(3H0^2/2pi^2)^2 * Integral")
print(f"        = 2*{T_obs}*{gamma**2}*{Omega_GW**2}*{(3*H0**2/(2*np.pi**2))**2:.4e}*{integral_paper_val:.4e}")
print(f"        = {paper_snr2:.4e}")
print(f"  SNR = {paper_snr:.4e}")

# --- Script integral ---
print("\n--- Script Formula (S_h * |T|^2 coupling) ---")
integral_script_val, integrand_script = integral_script()
print(f"\n  Integral[S_h^2 * |T|^4 / S_y^2 df] = {integral_script_val:.4e}")

# Now extract the factor before integral
pre_factor = 2 * T_obs * gamma**2
script_snr2 = pre_factor * integral_script_val
script_snr = np.sqrt(script_snr2)
print(f"\n  SNR^2 = 2*T_obs*Gamma^2 * Integral = {pre_factor} * {integral_script_val:.4e}")
print(f"        = {script_snr2:.4e}")
print(f"  SNR = {script_snr:.4e}")

# --- Key comparison ---
print("\n" + "=" * 80)
print("KEY COMPARISON")
print("=" * 80)
print(f"\n  Paper formula (with P_N_paper):    SNR = {paper_snr:.4e}")
print(f"  Script formula (with P_N_script):  SNR = {script_snr:.4e}")
print(f"\n  Paper claims SNR = 9.67e-6")
print(f"  Discrepancy ratio: {paper_snr / 9.67e-6:.1f}x")
print(f"  Script ratio: {script_snr / 9.67e-6:.1f}x")

# --- Noise model comparison ---
print("\n" + "=" * 80)
print("NOISE MODEL COMPARISON")
print("=" * 80)
test_freqs = [0.001, 0.01, 0.1, 1.0, 10.0]
for f_test in test_freqs:
    PN_paper = P_N_paper(f_test)
    PN_script = P_N_script(f_test)
    print(f"  f={f_test:.3f} Hz: P_N_paper={PN_paper:.4e}, P_N_script={PN_script:.4e}, ratio={PN_paper/PN_script:.2e}")

# --- Convention comparison ---
print("\n" + "=" * 80)
print("CONVENTION COMPARISON (Hu vs Script)")
print("=" * 80)
f_test = 0.1
P_h_hu_val = P_h_hu(f_test)
P_h_script_val = P_h_script(f_test)
print(f"  f={f_test} Hz:")
print(f"    P_h_Hu (3H0^2/2pi^2 * Om/f^3) = {P_h_hu_val:.4e}")
print(f"    P_h_script (2H0^2/pi^2 * Om * f^-3) = {P_h_script_val:.4e}")
print(f"    Ratio Hu/script = {P_h_hu_val/P_h_script_val:.4f}")
print(f"    Expected ratio (9/4 = 2.25)")
print(f"    Note: (9/4)^2 = 8.0625 for SNR^2")

# --- Frequency contribution analysis ---
print("\n" + "=" * 80)
print("FREQUENCY CONTRIBUTION ANALYSIS")
print("=" * 80)
print("\nPaper integrand contributions by frequency band:")
bands = [(1e-4, 1e-2), (1e-2, 0.1), (0.1, 1.0), (1.0, 10.0), (10.0, 100.0)]
for f_lo, f_hi in bands:
    mask = (f >= f_lo) & (f < f_hi)
    contrib = np.trapezoid(integrand_paper[mask], f[mask])
    print(f"  [{f_lo:.0e}, {f_hi:.0e}] Hz: contrib = {contrib:.4e} ({100*contrib/integral_paper_val:.1f}%)")

# --- Dimensional analysis of the paper's integral ---
print("\n" + "=" * 80)
print("DIMENSIONAL ANALYSIS OF INTEGRALS")
print("=" * 80)
print("\nPaper formula integrand: |T|^4 * f^-6 / P_N^2")
print("  |T| is dimensionless (transfer function)")
print("  f^-6: Hz^-6")
print("  P_N: Hz^-1 (power spectral density of frequency fluctuations)")
print("  P_N^2: Hz^-2")
print("  Integrand: Hz^-6 / Hz^-2 = Hz^-4")
print("  After df: Hz^-4 * Hz = Hz^-3")
print("  But paper labels it as Hz^-5 -- THIS IS WRONG!")

print("\nScript formula integrand: S_h^2 * |T|^4 / S_y^2")
print("  S_h: Hz^-1 (PSD of frequency fluctuations from GW)")
print("  S_h^2: Hz^-2")
print("  |T|^4: dimensionless")
print("  S_y^2: Hz^-2 (PSD^2)")
print("  Integrand: Hz^-2 / Hz^-2 = dimensionless")
print("  After df: dimensionless * Hz = Hz")
print("  Then * T_obs (s): dimensionless -- CORRECT for SNR^2")

# --- What the paper's integral ACTUALLY should be ---
print("\n" + "=" * 80)
print("WHAT THE INTEGRAL VALUE SHOULD BE")
print("=" * 80)
# The paper's formula with correct P_N_paper
# Let's compute what P_N_paper at peak frequency gives
f_peak_paper = f[np.argmax(integrand_paper)]
print(f"\nPaper integrand peaks at f = {f_peak_paper:.4f} Hz")
print(f"P_N_paper at peak = {P_N_paper(f_peak_paper):.4e}")

# The script's peak
f_peak_script = f[np.argmax(integrand_script)]
print(f"Script integrand peaks at f = {f_peak_script:.4f} Hz")
print(f"P_N_script at peak = {P_N_script(f_peak_script):.4e}")

# Compute the paper integral with the CORRECT formula
# SNR^2 = 2 T_obs Gamma^2 \int df S_h^2 |T|^4 / P_N^2
# where S_h = (3H0^2/2pi^2) * Omega_GW / f^3
# This is just the Hu-conv. version of the script formula
S_h_hu = P_h_hu(f)
integrand_hu = (S_h_hu**2) * T_paper(f)**4 / (P_N_paper(f)**2)
integral_hu = np.trapezoid(integrand_hu, f)
snr2_hu = 2 * T_obs * gamma**2 * integral_hu
snr_hu = np.sqrt(snr2_hu)
print(f"\nHu-convention with P_N_paper:")
print(f"  Integral[S_h^2*|T|^4/P_N^2 df] = {integral_hu:.4e}")
print(f"  SNR = {snr_hu:.4e}")

# Now try the paper's formula literally: |T|^4 * f^-6 / P_N^2
# with no S_h factor (this is what Eq. 1204 reduces to after pulling out constants)
integrand_literal = T_paper(f)**4 * f**(-6) / (P_N_paper(f)**2)
integral_literal = np.trapezoid(integrand_literal, f)
snr2_literal = 2 * T_obs * gamma**2 * Omega_GW**2 * (3*H0**2/(2*np.pi**2))**2 * integral_literal
snr_literal = np.sqrt(snr2_literal)
print(f"\nPaper's literal formula (pulling out all constants):")
print(f"  Integral[|T|^4 * f^-6 / P_N^2 df] = {integral_literal:.4e}")
print(f"  This equals the Hu-convention integral / (3H0^2/2pi^2)^2 / Omega_GW^2")
print(f"  Check: integral_hu / ((3H0^2/(2pi^2))^2 * Omega_GW^2) = {integral_hu / ((3*H0**2/(2*np.pi**2))**2 * Omega_GW**2):.4e}")
print(f"  SNR = {snr_literal:.4e}")

# Verify: these should match
print(f"\n  SNR consistency check: {snr_hu:.4e} vs {snr_literal:.4e}")
print(f"  Match: {np.isclose(snr_hu, snr_literal)}")
