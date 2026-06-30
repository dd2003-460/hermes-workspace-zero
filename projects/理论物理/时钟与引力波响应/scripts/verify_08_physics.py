#!/usr/bin/env python3
"""Verification of 08-space-olc-band-comparison.py physics."""
import numpy as np

c = 299792458.0
H_0 = 67.4 * 1000.0 / 3.096e19
T_obs = 3.15e7

# ============ Reproduce the core functions ============

def gw_strain_psd(f, Omega):
    f = np.maximum(f, 1e-20)
    return 2.0 * H_0**2 / np.pi**2 * Omega / f**3

def characteristic_strain_squared(f, Omega):
    return f * gw_strain_psd(f, Omega)

def olc_total_noise(f, nu, N, T, delta_L, eta, P_L, S_L, L):
    f = np.maximum(f, 1e-20)
    qpn = 2.0 / ((2*np.pi*nu)**2 * N * T)
    h_nu = 1.055e-34 / (2*np.pi)
    denom = (2*np.pi*f)**2 + eta*P_L*delta_L / (2*np.pi*h_nu*nu)
    psn = 2*f**2*delta_L / (nu**2 * np.maximum(denom, 1e-50))
    an = 2*(L/c)**2 * S_L / ((2*np.pi*f)**4)
    return qpn + psn + an

def olc_coupling(f, L, K):
    return (2*np.pi*f*L/c)**2 * K**2

def dSNR2_olc(f, Omega, L, K, g2, T_obs, params):
    f = np.maximum(f, 1e-20)
    S_h = gw_strain_psd(f, Omega)
    coupling = olc_coupling(f, L, K)
    S_corr = S_h * coupling
    S_y = olc_total_noise(f, params["nu"], params["N"], params["T"],
                          params["delta_L"], params["eta"], params["P_L"],
                          params["S_L"], L)
    return 2 * T_obs * g2 * S_corr**2 / np.maximum(S_y**2, 1e-100)

def integrated_snr(dS2_arr, log_f):
    return np.sqrt(max(np.trapezoid(np.maximum(dS2_arr, 0), log_f), 0))

OLC = {"nu": 430e12, "N": 7e6, "T": 160, "delta_L": 0.03, "eta": 0.5,
       "P_L": 3e-12, "S_L": 9e-30, "g2": 0.188**2, "K": 0.53}

log_f = np.log(np.logspace(np.log10(1e-6), np.log10(1.0), 3000))
f_vals = np.exp(log_f)

# ============ Check 1: OLC dSNR²/df L-scaling invariance ============
print("=" * 60)
print("CHECK 1: OLC dSNR²/df L-scaling invariance")
print("=" * 60)

L_test = [0.17e9, 0.5e9, 2.5e9, 5.0e9, 10.0e9]
om_test = 1e-8
snrs = []
for L in L_test:
    dS2 = dSNR2_olc(f_vals, om_test, L, OLC["K"], OLC["g2"], T_obs, OLC)
    snr = integrated_snr(dS2, log_f)
    snrs.append(snr)
    print(f"  L={L/1e9:7.2f} Gm: SNR={snr:.6f}")

ratio_max = max(snrs) / min(snrs)
print(f"  Ratio max/min = {ratio_max:.6f}")
check1_pass = ratio_max / min(snrs) < 2.0  # within factor of 2
# Actually let me be more strict: if truly scale-invariant, ratio should be < 1.01
check1_pass = ratio_max < 1.1
print(f"  PASS: {check1_pass} (scale-invariant if ratio < 1.1)")

# ============ Check 2: Why L cancels ============
print("\n" + "=" * 60)
print("CHECK 2: Analytical L-cancellation in OLC formulas")
print("=" * 60)

L1 = 2.5e9
L2 = 10.0e9
om = 1e-7
f_p = 1e-4  # peak frequency band

# Compute coupling ratio
coup1 = olc_coupling(np.array([f_p]), L1, OLC["K"])
coup2 = olc_coupling(np.array([f_p]), L2, OLC["K"])
coup_ratio = float(coup2[0]) / float(coup1[0])
print(f"  Coupling at f={f_p}: L2/L1 ratio = {coup_ratio:.4f} (expected L² ratio = {(L2/L1)**2:.4f})")

# Compute ACC noise ratio
n1_acc = 2*(L1/c)**2 * OLC["S_L"] / ((2*np.pi*f_p)**4)
n2_acc = 2*(L2/c)**2 * OLC["S_L"] / ((2*np.pi*f_p)**4)
n_acc_ratio = n2_acc / n1_acc
print(f"  ACC noise: L2/L1 ratio = {n_acc_ratio:.4f} (expected L² ratio = {(L2/L1)**2:.4f})")

# In S_corr = S_h * coupling, S_h doesn't depend on L
# So S_corr² ∝ L⁴ for fixed Ω and f

# In S_y = QPN + PSN + ACC
# QPN and PSN don't depend on L (they are instrument noise)
# ACC ∝ L²
# If ACC dominates, then S_y² ∝ L⁴, and S_corr²/S_y² is L-independent

# Check if ACC dominates at the frequency where coupling is strongest
for nm, L_nm in [("OLC", L1), ("OLC L2", L2)]:
    Nq = 2.0/((2*np.pi*OLC["nu"])**2 * OLC["N"] * OLC["T"])
    h_nu = 1.055e-34/(2*np.pi)
    denom = (2*np.pi*f_p)**2 + OLC["eta"]*OLC["P_L"]*OLC["delta_L"]/(2*np.pi*h_nu*OLC["nu"])
    psn_v = 2*f_p**2*OLC["delta_L"]/(OLC["nu"]**2*denom)
    acc_v = 2*(L_nm/c)**2 * OLC["S_L"] / ((2*np.pi*f_p)**4)
    print(f"  {nm} noise at {f_p} Hz: QPN={Nq:.2e} PSN={psn_v:.2e} ACC={acc_v:.2e}")

# ============ Check 3: Interferometer noise floor ============
print("\n" + "=" * 60)
print("CHECK 3: Interferometer noise floor h_c_min")
print("=" * 60)

def interf_noise_psd(f, A2oms, A2acc, L):
    f = np.maximum(f, 1e-20)
    N_oms = A2oms / L**2
    term = 2*(1+np.cos(2*np.pi*f*L/c)**2) * A2acc / ((2*np.pi*f)**4*L**2)
    return N_oms + term

interfs = {
    "LISA": (2.5e9, 225e-24, 9e-30),
    "Taiji": (3.0e9, 64e-24, 9e-30),
    "TianQin": (0.17e9, 1e-24, 1e-30),
}

for nm, (L, A2oms, A2acc) in interfs.items():
    f_test = 3e-3
    sn = interf_noise_psd(np.array([f_test]), A2oms, A2acc, L)[0]
    h_c_min = np.sqrt(sn / T_obs)
    print(f"  {nm}: S_n(3mHz) = {sn:.2e}, h_c_min = {h_c_min:.2e}")

# Reasonable range: LISA h_c_min ~1e-20 to 1e-19 at 3mHz
# 1e-24 would be TOO small (too sensitive)
check3_pass = True  # Will assess from output
for nm, (L, A2oms, A2acc) in interfs.items():
    sn = interf_noise_psd(np.array([3e-3]), A2oms, A2acc, L)[0]
    h_c_min = np.sqrt(sn / T_obs)
    # OMS dominates for LISA at 3mHz
    sn_oms = A2oms / L**2
    if sn_oms < 1e-42 or sn_oms > 1e-38:
        check3_pass = False
        print(f"  WARNING: {nm} OMS noise out of expected range")
print(f"  CHECK 3 PASS: {check3_pass}")

# ============ Check 4: OLC Ω₅ value ============
print("\n" + "=" * 60)
print("CHECK 4: OLC Ω₅ ≈ 8.9e-6 verification")
print("=" * 60)

L_check = 2.5e9
for om in [5e-6, 8e-6, 8.9e-6, 1e-5, 2e-5]:
    dS2 = dSNR2_olc(f_vals, om, L_check, OLC["K"], OLC["g2"], T_obs, OLC)
    snr = integrated_snr(dS2, log_f)
    print(f"  Ω={om:.1e}: SNR={snr:.3f}")

# Interpolate for SNR=5
check4_pass = True  # Will check from output

# ============ Check 5: TianQin N_eff vs LISA ============
print("\n" + "=" * 60)
print("CHECK 5: TianQin sensitivity reasonableness")
print("=" * 60)

# TianQin has much shorter arm (0.17 Gm vs LISA 2.5 Gm)
# This means f_peak is much higher ~ c/(2L)
# f_LISA_peak ~ 60 mHz, f_TianQin_peak ~ 880 mHz
f_peak_lisa = c / (2 * 2.5e9)
f_peak_taiji = c / (2 * 3.0e9)
f_peak_tianqin = c / (2 * 0.17e9)
print(f"  f_peak: LISA={f_peak_lisa:.1f} mHz, Taiji={f_peak_taiji:.1f} mHz, TianQin={f_peak_tianqin*1e3:.0f} Hz")

# TianQin peak is in 880 Hz — well above GW sensitivity band
# Its Ω₅ should be higher (worse sensitivity) than LISA
# Check: is TianQin Ω₅ = 3.66e-7 reasonable vs LISA 1e-7?
# Actually TianQin has better OMS noise (1e-24 vs 225e-24)
# But much shorter arm means different frequency response
print(f"  TianQin Ω₅ / LISA Ω₅ = {3.66e-7 / 1e-7:.1f}x")
print(f"  (TianQin should be roughly comparable or slightly worse due to very different frequency response)")

# ============ Summary ============
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
confidence = 0.85 if check1_pass and check3_pass else 0.5
print(f"  OLC L-invariance: {'PASS' if check1_pass else 'FAIL'}")
print(f"  Interferometer noise: {'PASS' if check3_pass else 'FAIL'}")
print(f"  Overall confidence: {confidence:.2f}")
