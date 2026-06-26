#!/usr/bin/env python3
"""
AIM v3: close evaluation points + independent per-point normalization.

Two fixes:
1. xa=0.45, xb=0.55 — similar coefficient magnitudes, similar growth rates
2. Each point has its own independent normalization — no global scale crushing one point

If both points grow at similar rates, N=8-12 should be enough for theta convergence
before either point underflows.
"""

import numpy as np

M = 1.0


def get_coeffs(x, omega, l=2, formulation="dehghan"):
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)
    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a_base = -dlnP
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b_base = P**2 * (omega**2 - V)

    if formulation == "raw":
        return -a_base, -b_base

    elif formulation == "dehghan":
        F_over_F = 2 * (2 * x - 1) / (x * (1 - x))
        alpha = -1j * omega
        beta = 1j * omega
        gamma_v = -1j * omega
        ggg = alpha * (F_over_F + 1 / x) - beta / (1 - x) + gamma_v / (1 - x)**2
        dx_n = 1e-7
        xp = min(x + dx_n, 0.99999)
        xm = max(x - dx_n, 1e-8)
        Fp = 2 * (2 * xp - 1) / (xp * (1 - xp))
        gp = alpha * (Fp + 1 / xp) - beta / (1 - xp) + gamma_v / (1 - xp)**2
        Fm = 2 * (2 * xm - 1) / (xm * (1 - xm))
        gm = alpha * (Fm + 1 / xm) - beta / (1 - xm) + gamma_v / (1 - xm)**2
        dggg = (gp - gm) / (2 * dx_n)
        p1 = a_base + 2 * ggg
        p2 = b_base + a_base * ggg + 2 * ggg**2 + dggg
        return -p1, -p2

    elif formulation == "cho":
        p1_c = dlnP
        kappa = 2j * omega
        beta_a = 2j * omega
        gamma_a = -2j * omega
        psi_p = kappa / x - beta_a / (1 - x) + gamma_a / (1 - x)**2
        psi_pp = -kappa / x**2 + beta_a / (1 - x)**2 - 2 * gamma_a / (1 - x)**3
        psi_dd = psi_p**2 + psi_pp
        S0 = (16 * omega**2 * x - 32 * omega**2 - 8j * omega * (1 - x)
              + l * (l + 1) - 3 * (1 - x)) / (x * (1 - x)**2)
        p2_c = S0 - psi_dd - p1_c * psi_p
        return -p1_c, -p2_c

    raise ValueError(f"Unknown: {formulation}")


def aim_single(get_coeffs, omega, x, N=8):
    """AIM at single point with independent normalization."""
    dx_num = 1e-6
    la, ma = get_coeffs(x, omega)
    dla = (get_coeffs(x + dx_num, omega)[0] - get_coeffs(x - dx_num, omega)[0]) / (2 * dx_num)
    dmu = (get_coeffs(x + dx_num, omega)[1] - get_coeffs(x - dx_num, omega)[1]) / (2 * dx_num)

    for k in range(N):
        la_prev = la
        ln = la**2 + dla - ma
        mn = la * dmu - ma * dla + ma**2
        dla_n = 2 * la * dla - dmu
        dmu_n = 2 * ma * dmu

        max_val = max(abs(ln), abs(mn), abs(dla_n), abs(dmu_n))
        scale = max_val / 1e40 if max_val > 1e40 else 1.0

        la_prev /= scale
        la, ma, dla, dmu = ln/scale, mn/scale, dla_n/scale, dmu_n/scale

    theta = la_prev / la
    return theta, abs(la)


def aim_compare(get_coeffs, omega, N=8, xa=0.45, xb=0.55):
    """Compare two points with independent normalization."""
    ta, la_a = aim_single(get_coeffs, omega, xa, N)
    tb, la_b = aim_single(get_coeffs, omega, xb, N)

    D = abs(ta - tb)
    phase_a = np.angle(ta)
    phase_b = np.angle(tb)
    pd = abs(phase_a - phase_b)
    if pd > np.pi:
        pd = 2 * np.pi - pd

    return D, pd, ta, tb, la_a, la_b


# ---- Run ----
print("=" * 70)
print("AIM v3: Close Points + Independent Normalization")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j

# First: check coefficient magnitudes at close points
print(f"\n--- Coefficients at xa=0.45, xb=0.55 ---")
for form in ["dehghan", "cho", "raw"]:
    print(f"\n  {form}:")
    for x in [0.45, 0.55]:
        lam, mu = get_coeffs(x, omega_ref, formulation=form)
        print(f"    x={x}: |lam|={abs(lam):.4e}, |mu|={abs(mu):.4e}")

# Theta at reference QNM — how do ta, tb behave at close points?
print(f"\n--- At reference QNM (omega={omega_ref:.4f}) ---")
for form in ["dehghan", "cho"]:
    print(f"\n  {form}:")
    gc = lambda x, w, f=form: get_coeffs(x, w, formulation=f)
    for N in [4, 5, 6, 7, 8, 9, 10]:
        D, pd, ta, tb, la_a, la_b = aim_compare(gc, omega_ref, N, xa=0.45, xb=0.55)
        print(f"    N={N}: D={D:.6e}, phase_diff={pd:.6f}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}, |la_a|={la_a:.4e}, |la_b|={la_b:.4e}")

# Scan D across omega grid
for form in ["dehghan", "cho"]:
    print(f"\n--- D scan ({form}, N=7, xa=0.45, xb=0.55) ---")
    gc = lambda x, w, f=form: get_coeffs(x, w, formulation=f)
    best_D, best_w = 1e30, None
    for wr in np.arange(0.34, 0.40, 0.005):
        for wi in np.arange(-0.12, -0.05, 0.005):
            w = wr + 1j * wi
            D, pd, ta, tb, la_a, la_b = aim_compare(gc, w, N=7)
            if D < best_D:
                best_D = D
                best_w = w
            star = " ***" if D < 0.1 else (" *" if D < 1 else "")
            if star:
                print(f"    w={wr:.3f}{wi:+.3f}j: D={D:.4f}, |la_a|={la_a:.2e}, |la_b|={la_b:.2e}{star}")
    print(f"    Best: w={best_w:.5f}, D={best_D:.6e}")

    # Fine scan
    print(f"\n--- Fine D scan ({form}, N=8, xa=0.45, xb=0.55) ---")
    wr0 = max(0.35, min(best_w.real, 0.39))
    wi0 = max(-0.11, min(best_w.imag, -0.06))
    best_D2, best_w2 = 1e30, None
    for wr in np.arange(wr0 - 0.015, wr0 + 0.016, 0.002):
        for wi in np.arange(wi0 - 0.01, wi0 + 0.011, 0.002):
            w = wr + 1j * wi
            D, pd, ta, tb, la_a, la_b = aim_compare(gc, w, N=8)
            if D < best_D2:
                best_D2 = D
                best_w2 = w
            star = " ***" if D < 0.05 else (" *" if D < 0.5 else "")
            if star:
                print(f"    w={wr:.3f}{wi:+.3f}j: D={D:.4f}, |la_a|={la_a:.2e}, |la_b|={la_b:.2e}{star}")
    print(f"    Best: w={best_w2:.5f}, D={best_D2:.6e}")


# Also try with 3 points for cross-validation
print(f"\n--- Three-point test (dehghan, N=7, xa=0.42, xb=0.50, xc=0.58) ---")
gc = lambda x, w: get_coeffs(x, w, formulation="dehghan")
for w_test in [omega_ref, 0.37 + 1j*(-0.09), 0.38 + 1j*(-0.085), 0.374 + 1j*(-0.089)]:
    ta, _ = aim_single(gc, w_test, 0.42, 7)
    tb, _ = aim_single(gc, w_test, 0.50, 7)
    tc, _ = aim_single(gc, w_test, 0.58, 7)
    D_ab = abs(ta - tb)
    D_bc = abs(tb - tc)
    D_ac = abs(ta - tc)
    print(f"  w={w_test:.4f}: D_ab={D_ab:.4e}, D_bc={D_bc:.4e}, D_ac={D_ac:.4e}")
    print(f"    ta={ta:.6e}, tb={tb:.6e}, tc={tc:.6e}")
