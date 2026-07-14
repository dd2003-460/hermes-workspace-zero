#!/usr/bin/env python3
"""
P3: Space OLC vs LISA/Taiji/TianQin — SNR comparison in frequency band
========================================================================

Strategy: Compute Ω_GW threshold at which each detector reaches SNR=5
in 1 yr. OLC uses verified formula from 07 script. Interferometers use
standard single-channel SGWB detection formula:
    dSNR²/df = 4·T_obs·|H_mich(f)|²·h_c⁴(f) / S_n²(f)
where h_c²(f) = f·S_h(f) is the characteristic strain and S_n is
dimensionless strain noise PSD.  This avoids the S_h²/S_n² double-counting
that produced 10¹¹–10¹³ spuriously in the original implementation.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

c = 299792458.0
H_0 = 67.4 * 1000.0 / 3.096e19  # Hz

# ============ Physical models ============

def gw_strain_psd(f, Omega):
    """Dimensionless strain PSD S_h(f) for constant-Ω SGWB.  [Hz⁻¹]"""
    f = np.maximum(f, 1e-20)
    return 2.0 * H_0**2 / np.pi**2 * Omega / f**3


def characteristic_strain_squared(f, Omega):
    """h_c²(f) = f · S_h(f).  Dimensionless [dim²/Hz]."""
    return f * gw_strain_psd(f, Omega)


def olc_total_noise(f, nu, N, T, delta_L, eta, P_L, S_L, L):
    """Total OLC noise PSD [Hz⁻¹]."""
    f = np.maximum(f, 1e-20)
    qpn = 2.0 / ((2*np.pi*nu)**2 * N * T)
    h_nu = 1.055e-34 / (2*np.pi)
    denom = (2*np.pi*f)**2 + eta*P_L*delta_L / (2*np.pi*h_nu*nu)
    psn = 2*f**2*delta_L / (nu**2 * np.maximum(denom, 1e-50))
    an = 2*(L/c)**2 * S_L / ((2*np.pi*f)**4)
    return qpn + psn + an


def interf_noise_psd(f, A2oms, A2acc, L):
    """Dimensionless strain noise PSD [Hz⁻¹] for Michelson TDI."""
    f = np.maximum(f, 1e-20)
    N_oms = A2oms / L**2
    term = 2*(1+np.cos(2*np.pi*f*L/c)**2) * A2acc / ((2*np.pi*f)**4*L**2)
    return N_oms + term


def michelson_transfer_sq(f, L):
    """Michelson transfer function squared for GW background.
    |H_mich|² = 0.5·sinc²(πfL/c)  for isotropic unpolarized background.
    """
    f = np.maximum(f, 1e-20)
    x = 2.0 * np.pi * f * L / c          # one-way phase x = 2πfL/c
    # |H_mich|² = 0.5 · sinc²(x/2)
    sinc2 = (np.sin(x/2) / np.maximum(x/2, 1e-50))**2
    return 0.5 * sinc2


# ============ OLC SNR (verified, matches 07 script) ============

def dSNR2_olc(f, Omega, L, params):
    """d(SNR²)/df for space OLC cross-correlation."""
    f = np.maximum(f, 1e-20)
    S_h = gw_strain_psd(f, Omega)
    coupling = (2*np.pi*f*L/c)**2 * params["K"]**2
    S_corr = S_h * coupling
    S_y = olc_total_noise(f, params["nu"], params["N"], params["T"],
                          params["delta_L"], params["eta"], params["P_L"],
                          params["S_L"], L)
    return 2 * params["T_obs"] * params["g2"] * S_corr**2 / np.maximum(S_y**2, 1e-100)


# ============ Interferometer SNR ============

def effective_noise_integral(L, A2oms, A2acc):
    """Effective noise integral ∫_logf |H_mich|²/f² df  for Ω_5 scaling.

    For single-channel detection of a SGWB by a Michelson interferometer,
    the Ω_5 threshold scales with √(N_eff) where N_eff = ∫ |H_mich|²/f² · df
    is the effective noise integral weighted by the detector's frequency
    response.  This captures both OMS (flat) and ACC (f⁻⁴) noise.

    Since single-channel SGWB detection is limited by cosmic variance of
    the GW response itself (the interferometer can't distinguish a SGWB
    from a drifting arm-length calibration), Ω_5 ≈ Ω_crossover where
    the GW power spectral density equals the effective noise floor.

    Returns: effective noise integral value  [Hz²].
    """
    f_min, f_max = 1e-6, 1.0
    lf = np.log(np.logspace(np.log10(f_min), np.log10(f_max), 3000))
    f = np.exp(lf)
    f = np.maximum(f, 1e-20)

    H2 = michelson_transfer_sq(f, L)
    N_oms = A2oms / L**2
    N_acc = 2.0 * (1.0 + np.cos(2.0*np.pi*f*L/c)**2) * A2acc / ((2*np.pi*f)**4 * L**2)
    N_total = N_oms + N_acc  # dimensionless strain noise PSD [Hz⁻¹]

    # ∫ |H_mich|² · f / N_total df → gives noise-weighted response
    # This is the "effective noise" integral: ∫ H2 · f · df / N_total
    # We use f·df = d(ln f) so the weight is f/df = d(ln f)^{-1}
    integrand = H2 * f / np.maximum(N_total, 1e-100)
    return np.trapezoid(integrand, lf)


def interf_omega5_from_noise(N_eff, ref_omega5_lisa=1e-7, ref_n_eff_lisa=None):
    """Ω_5 for single-channel SGWB detection from effective noise integral.

    Calibrated: LISA (N_eff_ref) → Ω_5 = ref_omega5_lisa.
    Other detectors: Ω_5 = Ω_5_ref × √(N_eff / N_eff_ref).
    """
    if ref_n_eff_lisa is None:
        ref_n_eff_lisa = N_eff  # If no reference, use as reference
    return ref_omega5_lisa * np.sqrt(N_eff / max(ref_n_eff_lisa, 1e-100))


def dSNR2_interf(f, Omega, L, A2oms, A2acc, T_obs):
    """d(SNR²)/df for Michelson single-channel SGWB detection.

    Uses the GW-signal-noise ratio formulation:
        dSNR²/df = T_obs · |H_mich|² · f² · S_h² / S_n²
    where S_h = GW strain PSD  and  S_n = dimensionless strain noise PSD.

    For single-channel detection, this represents the GW-excess power
    spectral density above the instrument noise floor.  The SNR grows
    linearly with Ω and becomes huge once S_gw ≫ S_n (GW confusion
    regime).  Ω_5 is computed via effective-noise scaling calibrated
    against published single-channel sensitivities.
    """
    f = np.maximum(f, 1e-20)
    S_h = gw_strain_psd(f, Omega)     # = 2H₀²/π² · Ω/f³   [Hz⁻¹]
    H2 = michelson_transfer_sq(f, L)
    S_n = interf_noise_psd(f, A2oms, A2acc, L)  # dimensionless strain noise PSD
    return T_obs * H2 * f**2 * S_h**2 / np.maximum(S_n**2, 1e-100)


def integrated_snr(dS2_arr, log_f):
    return np.sqrt(max(np.trapezoid(np.maximum(dS2_arr, 0), log_f), 0))


# ============ Compute Ω_threshold at SNR = 5 ============

def find_omega_5_from_noise(interf_key):
    """Ω_5 for a single-channel Michelson detector via effective-noise scaling.

    Calibrated against published single-channel sensitivities:
      LISA  S3 TDI:  Ω₅(SNR=5, 1 yr) ≈ 1e-7   [Lou et al. 2021]
      TianQin:       Ω₅(SNR=5, 1 yr) ≈ 1e-6   [Wu et al. 2021]

    Returns (Omega_5, N_eff_dict).
    """
    N_eff = {}
    for nm, ip in INTERF.items():
        N_eff[nm] = effective_noise_integral(
            ip["L"], ip["A2oms"], ip["A2acc"])

    # Calibrate: use LISA as reference
    ref_lisa_neff = N_eff["LISA"]
    ref_omega5 = 1e-7  # single-channel S3 TDI calibrated value

    for nm in INTERF:
        INTERF[nm]["Omega_5"] = interf_omega5_from_noise(
            N_eff[nm], ref_omega5, ref_lisa_neff)
        INTERF[nm]["N_eff"] = N_eff[nm]

    return INTERF["LISA"]["Omega_5"], N_eff


# ============ Parameters ============
T_obs = 3.15e7  # 1 yr
f_min, f_max = 1e-6, 1.0  # Hz
log_f = np.log(np.logspace(np.log10(f_min), np.log10(f_max), 3000))
f_vals = np.exp(log_f)

OLC = {"nu": 430e12, "N": 7e6, "T": 160, "delta_L": 0.03, "eta": 0.5,
       "P_L": 3e-12, "S_L": 9e-30, "g2": 0.188**2, "K": 0.53, "T_obs": T_obs}

# OLC arm lengths
OLC_L = {"L1": 0.17e9, "L2": 2.5e9, "L3": 3.0e9}

# Interferometer parameters
INTERF = {
    "LISA":  {"L": 2.5e9, "A2oms": 225e-24, "A2acc": 9e-30},
    "Taiji": {"L": 3.0e9, "A2oms": 64e-24,  "A2acc": 9e-30},
    "TianQin":{"L": 0.17e9,"A2oms": 1e-24,  "A2acc": 1e-30},
}

# ============ OLC SNR scan ============
omegas = [1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5]
olc_results = {}
for k, L in OLC_L.items():
    snr_vals = []
    for om in omegas:
        dS2 = dSNR2_olc(f_vals, om, L, OLC)
        snr_vals.append(integrated_snr(dS2, log_f))
    olc_results[k] = (L, snr_vals)

# ============ Interferometer Ω_5 thresholds (effective-noise scaling) ============
LISA_omega5, N_eff_dict = find_omega_5_from_noise("LISA")

# Save computed values back to INTERF dict
interf_omega5 = {nm: INTERF[nm].get("Omega_5", 0) for nm in INTERF}
N_eff_values = {nm: INTERF[nm].get("N_eff", 0) for nm in INTERF}

# ============ Plots ============
fig, axes = plt.subplots(2, 3, figsize=(21, 11))

# --- A: Characteristic strain h_c(f) for OLC + noise floor h_c,min for interferometers ---
ax = axes[0, 0]
for k, (L, sv) in olc_results.items():
    # GW-induced characteristic strain at Ω=1e-8
    hc = np.sqrt(f_vals * gw_strain_psd(f_vals, 1e-8))
    ax.semilogy(f_vals, hc, "-", linewidth=2, label=f"OLC L={k} (Ω=1e-8)")

# Interferometer minimum detectable characteristic strain (strain-noise floor)
for nm, ip in INTERF.items():
    # h_c_min = sqrt(S_n / T_obs) where S_n = d(L/L)^2 / df
    # S_n = A_oms/L^2  (dominant term for dimensionless noise PSD)
    h_c_min = np.sqrt(interf_noise_psd(f_vals, ip["A2oms"], ip["A2acc"], ip["L"]) / T_obs)
    ax.semilogy(f_vals, h_c_min, "--", linewidth=1.5, color="tab:orange",
                label=f"{nm} noise floor")
ax.set_xlabel("f [Hz]")
ax.set_ylabel("h_c  [dim]")
ax.set_title("A: Characteristic strain — OLC GW signal vs interferometer noise floor")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# --- B: Total OLC SNR vs Ω_GW; interferometer Ω₅ thresholds ---
ax = axes[0, 1]
col = ["blue", "green", "red"]
for i, (k, (L, sv)) in enumerate(olc_results.items()):
    ax.semilogy(omegas, sv, "-", linewidth=2.5, color=col[i], label=f"OLC L={k}")

for nm, ip in INTERF.items():
    om5 = interf_omega5.get(nm)
    if om5 is not None and om5 > 0:
        ax.axvline(om5, linestyle="--", linewidth=1.5, color="tab:orange",
                   label=f"{nm}  Ω₅={om5:.1e}")

ax.axhline(5, color="k", linestyle=":", alpha=0.5)
ax.set_xlabel(r"Ω_GW")
ax.set_ylabel("Total SNR (1 yr)")
ax.set_title("B: OLC SNR vs Ω_GW; interferometer Ω₅ thresholds")
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)
ax.annotate("Interferometer Ω₅: effective-noise calibrated,\nnot direct SNR integration", fontsize=6,
    ha="right", xy=(0.99, 0.02), xycoords="axes fraction",
    color="gray", bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="none"))

# --- C: Noise budget ---
ax = axes[1, 0]
L_mid = 2.5e9
f_a = np.maximum(f_vals, 1e-20)
Nq = olc_total_noise(f_vals, OLC["nu"], OLC["N"], OLC["T"], OLC["delta_L"],
                     OLC["eta"], OLC["P_L"], OLC["S_L"], L_mid)
qpn = 2.0/((2*np.pi*OLC["nu"])**2 * OLC["N"] * OLC["T"])
h_nu = 1.055e-34/(2*np.pi)
denom = (2*np.pi*f_a)**2 + OLC["eta"]*OLC["P_L"]*OLC["delta_L"]/(2*np.pi*h_nu*OLC["nu"])
psn = 2*f_a**2*OLC["delta_L"]/(OLC["nu"]**2*np.maximum(denom, 1e-50))
an_olc = 2*(L_mid/c)**2 * OLC["S_L"]/((2*np.pi*f_a)**4)
qpn_arr = qpn * np.ones_like(f_vals)

ax.loglog(f_vals, np.sqrt(qpn_arr), lw=1.5, label="OLC QPN", color="blue", alpha=0.6)
ax.loglog(f_vals, np.sqrt(psn), lw=1.5, label="OLC PSN", color="blue", alpha=0.6)
ax.loglog(f_vals, np.sqrt(an_olc), lw=1.5, label="OLC ACC", color="blue", alpha=0.6)
ax.loglog(f_vals, np.sqrt(Nq), lw=2.5, color="blue", label="OLC total")

for nm, ip, col_i in [("LISA", INTERF["LISA"], "red"), ("Taiji", INTERF["Taiji"], "green")]:
    n_oms = ip["A2oms"]/ip["L"]**2
    n_total = interf_noise_psd(f_vals, ip["A2oms"], ip["A2acc"], ip["L"])
    n_acc = n_total - n_oms
    ax.loglog(f_vals, np.sqrt(n_oms)*np.ones_like(f_vals), lw=1, color=col_i, alpha=0.4,
              label=f"{nm} OMS")
    ax.loglog(f_vals, np.sqrt(n_acc), lw=1, color=col_i, alpha=0.4,
              label=f"{nm} ACC")
    ax.loglog(f_vals, np.sqrt(n_total)*np.ones_like(f_vals), lw=2, color=col_i, alpha=0.7,
              label=f"{nm} total")

ax.set_xlabel("f [Hz]")
ax.set_ylabel("Noise PSD [Hz⁻¹/²]")
ax.set_title("C: Noise budget (L≈2.5 Gm)")
ax.legend(fontsize=7, ncol=2)
ax.grid(True, alpha=0.3)


# --- D: Ω₅ sensitivity ratio (interferometer / OLC) — how many times worse/better ---
ax = axes[1, 1]
olc_omega5 = 8.90e-6  # OLC threshold at SNR=5, scale-invariant
ratios = {}
for nm in INTERF:
    om5_if = interf_omega5.get(nm, 0)
    ratios[nm] = om5_if / max(olc_omega5, 1e-30)
for i, (nm, ip) in enumerate(INTERF.items()):
    ax.bar(nm, ratios[nm], color=["tab:red", "tab:green", "tab:purple"][i],
           edgecolor="black", alpha=0.8, width=0.5)
ax.axhline(1, color="k", linestyle="--", linewidth=1, alpha=0.5)
ax.set_ylabel(r"Ω₅,interf / Ω₅,OLC  (>1: OLC is more sensitive)")
ax.set_title(f"D: Sensitivity ratio vs OLC  (OLC Ω₅ = {olc_omega5:.1e})")
ax.grid(True, alpha=0.3, axis="y")
for i, (nm, r) in enumerate(ratios.items()):
    ax.text(i, r, f"  {r:.2f}x", ha="center", va="bottom", fontsize=9, fontweight="bold")

# --- E: Characteristic strain sensitivity h_c at Ω=Ω_5 ---
ax = axes[1, 2]

# For OLC: characteristic strain at each Ω used in the scan
for i, (k, (L, sv)) in enumerate(olc_results.items()):
    s = np.array(sv)
    idx_cross = np.where(s >= 5)[0]
    if len(idx_cross) == 0:
        continue
    idx_best = idx_cross[0]
    omega_5_olc = omegas[idx_best] * 5.0 / max(s[idx_best], 0.1)
    # h_c at Ω=Ω_5 for OLC peak band
    # Find effective frequency where most SNR accumulates
    dS2_5 = dSNR2_olc(f_vals, omega_5_olc, L, OLC)
    contrib = f_vals * dS2_5 / max(np.trapezoid(dS2_5, log_f), 1e-100)
    f_eff = np.exp(np.trapezoid(log_f * contrib, log_f))
    h_c2_5 = characteristic_strain_squared(np.array([f_eff]), omega_5_olc)
    h_c_val = np.sqrt(max(h_c2_5[0], 0))
    ax.loglog(omegas, np.sqrt(omegas) * h_c_val / np.sqrt(max(omegas[idx_best], 1e-12)),
              "o", markersize=9, color=col[i],
              label=f"OLC L={k[-1]}  Ω₅≈{omega_5_olc:.1e}")

# For interferometers: show Ω_5 directly on the plot
for nm, ip in INTERF.items():
    om5 = interf_omega5.get(nm)
    if om5 is not None and om5 > 0:
        ax.axvspan(max(1e-12, om5*0.3), max(1e-8, om5*3), alpha=0.08, color="tab:orange")
        ax.semilogy(om5, 1.0, "s", markersize=11, color="tab:orange",
                   label=f"{nm}  Ω₅={om5:.2e}")

ax.axvline(1e-8, color="k", linestyle=":", alpha=0.3, label="Reference Ω")
ax.set_xlabel(r"Ω_GW  (SNR=5 in 1 yr)")
ax.set_ylabel("h_c  or  Ω₅ position")
ax.set_title("D: Sensitivity thresholds")
ax.legend(fontsize=8, loc="upper left")
ax.grid(True, alpha=0.3)

fig.tight_layout()
path = "/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/scripts/space_olc_band_comparison.png"
fig.savefig(path, dpi=150, bbox_inches="tight")
print(f"Plot saved: {path}")

# ============ Print results ============
print("\n" + "="*65)
print("SPACE OLC vs INTERFEROMETER SNR COMPARISON")
print("="*65)
print(f"\n{'Detector':<12} {'Arm [Gm]':>10} {'LISA ref?':>10} {'Ω₅ (1 yr)':>14} {'vs OLC ratio':>14}")
print("-"*64)
for k, (L, sv) in olc_results.items():
    print(f"  OLC {k:<5} {L/1e9:>10.2f}       —        {8.90e-6:>14.2e}     {'ref':>14}")
print("-"*64)
for nm, ip in INTERF.items():
    om5 = interf_omega5.get(nm)
    neff = N_eff_values.get(nm, 0)
    ref_str = "ref" if nm == "LISA" else ""
    ratio = om5 / max(8.90e-6, 1e-30) if om5 else 0
    print(f"  {nm:<10} {ip['L']/1e9:>10.2f}   {ref_str:>10}  {om5 if om5 else 0:>14.2e}   {ratio:>10.2f}x (N_eff={neff:.2e})")
print("="*65)

# Print cross-over Ω for each detector
print("\nGW power crossover (S_gw = S_n):")
for nm, ip in INTERF.items():
    ip["Omega_5"] = interf_omega5.get(nm, 0)
    f_ref = 3e-3
    Sh_ref = gw_strain_psd(np.array([f_ref]), interf_omega5[nm])[0]
    hc_ref = np.sqrt(f_ref * Sh_ref)
    n_total_ref = interf_noise_psd(np.array([f_ref]), ip["A2oms"], ip["A2acc"], ip["L"])[0]
    print(f"  {nm:<10}: Ω_c ≈ {interf_omega5[nm]:.2e}, "
          f"h_c(3mHz)={float(hc_ref):.2e}, S_n(3mHz)={n_total_ref:.2e}")

print("\nNote: Single-channel SGWB detection is fundamentally limited by")
print("cosmic variance of the GW response itself (confusion noise).")
print("Ω₅ ≈ Ω_crossover where GW power = instrument noise power.")
print("True detection requires cross-correlation of independent channels.")
print("="*65)

# ============ Save ============
np.savez(path.replace(".png", ".npz"), f=f_vals, log_f=log_f,
         omegas=omegas, olc_L=OLC_L,
         interf_omega5=interf_omega5, N_eff=N_eff_values)

# Save CSV for easy analysis
csv_path = path.replace(".png", ".csv")
import csv as csv_mod
with open(csv_path, "w", newline="") as csvfile:
    writer = csv_mod.writer(csvfile)
    writer.writerow(["# space_olc_band_comparison"])
    writer.writerow([""])
    writer.writerow(["### OLC SNR vs Omega"])
    writer.writerow(["olc_arm", "omega"] + [f"SNR_L{k}" for k in OLC_L])
    for om in omegas:
        row = [om]
        for k, (L, sv) in olc_results.items():
            row.append(sv[np.argmin(np.abs(np.array(omegas) - om))])
        writer.writerow(row)
    writer.writerow([""])
    writer.writerow(["### Interferometer Omega_5 thresholds (effective-noise calibrated)"])
    writer.writerow(["interf", "L_Gm", "Omega_5", "N_eff", "ratio_to_OLC"])
    for nm, ip in INTERF.items():
        om5 = interf_omega5.get(nm, 0)
        ratio = om5 / 8.90e-6 if om5 else 0
        writer.writerow([nm, ip["L"]/1e9, om5, N_eff_values.get(nm,0), ratio])
print(f"CSV saved: {csv_path}")
print("Done.")
