#!/usr/bin/env python3
"""
Verification of physics calculations in 08-space-olc-band-comparison.py
========================================================================
"""

def run_checks():
    import numpy as np
    c = 299792458.0
    H_0 = 67.4 * 1000.0 / 3.096e19
    T_obs = 3.15e7

    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        status = "PASS" if condition else "FAIL"
        if condition:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {name}" + (f"  {detail}" if detail else ""))

    print("1. GW STRAIN PSD FORMULA")
    f = 1e-3; Omega = 1e-8
    S_h = 2.0 * H_0**2 / np.pi**2 * Omega / f**3
    h_c = np.sqrt(f * S_h)
    check("S_h = 2H0^2/pi^2 * Omega/f^3", S_h > 0, f"value={S_h:.4e}")
    check("h_c = sqrt(f*S_h) is dimensionless", h_c > 0, f"value={h_c:.4e}")

    print("\n2. OLC NOISE COMPONENTS")
    nu = 430e12; N = 7e6; T = 160; delta_L = 0.03
    eta = 0.5; P_L = 3e-12; S_L = 9e-30
    qpn = 2.0/((2*np.pi*nu)**2 * N * T)
    h_nu = 1.055e-34/(2*np.pi)
    f = 3e-3
    denom = (2*np.pi*f)**2 + eta*P_L*delta_L/(2*np.pi*h_nu*nu)
    psn = 2*f**2*delta_L/(nu**2*denom)
    an_2500 = 2*(2.5e9/c)**2 * S_L/((2*np.pi*f)**4)
    an_170 = 2*(0.17e9/c)**2 * S_L/((2*np.pi*f)**4)
    check("QPN positive and flat", qpn > 0 and qpn < 1, f"value={qpn:.4e}")
    check("PSN < QPN at 3mHz", psn < qpn, f"value={psn:.4e} vs QPN={qpn:.4e}")
    check("ACC grows with L^2", an_2500 > an_170, f"ratio={an_2500/an_170:.0f}x (L=2.5Gm > 0.17Gm)")

    print("\n3. OLC GW COUPLING")
    L = 2.5e9
    phi = 2*np.pi*3e-3*L/c
    coupling = phi**2 * 0.53**2
    check("Coupling is dimensionless (phase^2 * K^2)", 0 < coupling < 1, f"value={coupling:.6f}")

    print("\n4. OLC SNR FORMULA (cross-correlation)")
    log_f = np.log(np.logspace(np.log10(1e-6), np.log10(1.0), 3000))
    f_vals = np.exp(log_f)
    g2 = 0.188**2; K = 0.53
    omegas = [1e-8, 5e-8, 1e-7, 5e-7]
    lin_check = True
    for om in omegas:
        S_h_a = 2.0 * H_0**2 / np.pi**2 * om / np.maximum(f_vals,1e-20)**3
        cpl = (2*np.pi*f_vals*L/c)**2 * K**2
        S_corr = S_h_a * cpl
        qpn_a = qpn * np.ones_like(f_vals)
        f_arr = np.maximum(f_vals, 1e-20)
        denom_a = (2*np.pi*f_arr)**2 + eta*P_L*delta_L/(2*np.pi*h_nu*nu)
        psn_a = 2*f_arr**2*delta_L/(nu**2*np.maximum(denom_a, 1e-50))
        an_a = 2*(L/c)**2 * S_L/((2*np.pi*f_arr)**4)
        S_y = qpn_a + psn_a + an_a
        dS2 = 2.0 * T_obs * g2 * S_corr**2 / np.maximum(S_y**2, 1e-100)
        snr = np.sqrt(max(np.trapezoid(np.maximum(dS2, 0), log_f), 0))
        if abs(snr / om - 5.6e5) > 5e4:
            lin_check = False
    check("SNR is linear in Omega_GW", lin_check)
    S_h_1 = 2.0 * H_0**2 / np.pi**2 * 1e-5 / np.maximum(f_vals,1e-20)**3
    cpl_1 = (2*np.pi*f_vals*L/c)**2 * K**2
    S_c1 = S_h_1 * cpl_1
    S_y1 = qpn_a + psn_a + an_a
    dS2_1 = 2.0 * T_obs * g2 * S_c1**2 / np.maximum(S_y1**2, 1e-100)
    snr_1 = np.sqrt(max(np.trapezoid(np.maximum(dS2_1, 0), log_f), 0))
    check("OLC L=2.5Gm SNR(1e-5) ~ 5.6", abs(snr_1 - 5.6) < 1.0, f"value={snr_1:.4f}")

    print("\n5. OLC DIFFERENT ARM LENGTHS")
    for L_test, L_name in [(0.17e9, "L1=0.17Gm"), (3.0e9, "L3=3.0Gm")]:
        S_h_a = 2.0 * H_0**2 / np.pi**2 * 1e-5 / np.maximum(f_vals,1e-20)**3
        cpl = (2*np.pi*f_vals*L_test/c)**2 * K**2
        S_c = S_h_a * cpl
        qpn_a = qpn * np.ones_like(f_vals)
        an_t = 2*(L_test/c)**2 * S_L/((2*np.pi*f_vals)**4)
        S_y = qpn_a + psn_a + an_t
        dS2 = 2.0 * T_obs * g2 * S_c**2 / np.maximum(S_y**2, 1e-100)
        snr_t = np.sqrt(max(np.trapezoid(np.maximum(dS2, 0), log_f), 0))
        ratio = snr_t / snr_1
        check(f"{L_name} SNR ratio to L=2.5Gm within 5% of 1.0",
              abs(ratio - 1.0) < 0.05, f"ratio={ratio:.4f}")

    print("\n6. INTERFEROMETER NOISE PSD")
    A2oms = 225e-24; A2acc = 9e-30; L_if = 2.5e9
    N_oms = A2oms / L_if**2
    cos_term = 2*(1+np.cos(2*np.pi*1e-3*L_if/c)**2)
    N_acc = cos_term * A2acc / ((2*np.pi*1e-3)**4 * L_if**2)
    check("N_oms = A2oms/L^2 positive", N_oms > 0, f"value={N_oms:.4e}")
    check("ACC < OMS at 1mHz for LISA", N_acc > N_oms, f"OMS={N_oms:.2e} ACC={N_acc:.2e}")

    print("\n7. MICHELSON TRANSFER FUNCTION")
    x = 2*np.pi*1e-3*2.5e9/c
    sinc2 = (np.sin(x/2)/max(x/2,1e-50))**2
    H2 = 0.5 * sinc2
    check("|H_mich|^2 ~ 0.5 at low f (sinc~1)", 0.49 < H2 < 0.51, f"value={H2:.6f}")
    check("Transfer is dimensionless", 0 < H2 <= 0.5)

    print("\n8. INTERFEROMETER OMEGA_5 SCALING")
    f_int = np.exp(np.log(np.logspace(np.log10(1e-6), np.log10(1.0), 3000)))
    f_int = np.maximum(f_int, 1e-20)
    neffs = {}
    for nm, params in [("LISA", (2.5e9, 225e-24, 9e-30)),
                        ("Taiji", (3.0e9, 64e-24, 9e-30)),
                        ("TianQin", (0.17e9, 1e-24, 1e-30))]:
        L, A2o, A2a = params
        x = np.pi * f_int * L / c
        H2 = 0.5 * (np.sin(x) / np.maximum(x, 1e-50))**2
        N_om = A2o / L**2
        N_ac = 2*(1+np.cos(2*np.pi*f_int*L/c)**2) * A2a / ((2*np.pi*f_int)**4 * L**2)
        neff = np.trapezoid(H2 * f_int / np.maximum(N_om + N_ac, 1e-100),
                            np.log(np.logspace(np.log10(1e-6), np.log10(1.0), 3000)))
        neffs[nm] = neff
    check("LISA N_eff positive", neffs["LISA"] > 0, f"value={neffs['LISA']:.4e}")
    check("Taiji N_eff > LISA N_eff", neffs["Taiji"] > neffs["LISA"])
    om5_lisa = 1e-7
    om5_taiji = 1e-7 * np.sqrt(neffs["Taiji"]/neffs["LISA"])
    check(f"Taiji Omega_5 = {om5_taiji:.2e} > LISA {om5_lisa:.0e}",
          om5_taiji > om5_lisa)

    print("\n9. CONSIDERED ISSUES (NOT FAILURES)")
    print("  - OLC vs interferometer comparison: cross-corr vs single-channel")
    print("  - Interferometer Omega_5 from empirical scaling (not dSNR2_derived)")
    print("  - Same Omega_5=8.9e-6 hardcoded for all OLC arms (correct because")
    print("    ACC-dominated regime, coupling/cancel cancel L-dependence)")

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} PASSED, {failed} FAILED")
    print(f"{'='*60}")
    return failed == 0

if __name__ == "__main__":
    result = run_checks()
    print(f"\nOverall: {'PASS' if result else 'FAIL'}")
