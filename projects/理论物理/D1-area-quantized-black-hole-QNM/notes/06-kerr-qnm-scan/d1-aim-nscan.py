#!/usr/bin/env python3
"""
Scan D at N=4,5,6 to find the convergence window before saturation.

Key: N=7 saturates at all omega with close points. N=4-6 should show
real convergence at the QNM vs noise at non-QNM values.

Use relative difference: rel_D = |theta_a/|theta_a| - theta_b/|theta_b||
to cancel out scaling artifacts within each point.
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


def aim_single_verbose(get_coeffs, omega, x, N=8):
    """AIM at single point. Returns theta, la_final, and per-step |la| history."""
    dx_num = 1e-6
    la, ma = get_coeffs(x, omega)
    dla = (get_coeffs(x + dx_num, omega)[0] - get_coeffs(x - dx_num, omega)[0]) / (2 * dx_num)
    dmu = (get_coeffs(x + dx_num, omega)[1] - get_coeffs(x - dx_num, omega)[1]) / (2 * dx_num)

    history = []

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

        history.append((k, abs(la), abs(la_prev), scale, max_val))

    theta = la_prev / la
    return theta, abs(la), history


def aim_compare_full(get_coeffs, omega, N=8, xa=0.45, xb=0.55):
    """Full comparison with normalized theta."""
    ta, la_a, hist_a = aim_single_verbose(get_coeffs, omega, xa, N)
    tb, la_b, hist_b = aim_single_verbose(get_coeffs, omega, xb, N)

    D = abs(ta - tb)
    # Normalized comparison: compare phases of theta (cancels magnitude from scaling)
    if abs(ta) > 0 and abs(tb) > 0:
        theta_a_norm = ta / abs(ta)
        theta_b_norm = tb / abs(tb)
        rel_D = abs(theta_a_norm - theta_b_norm)
    else:
        rel_D = 2.0  # max possible

    return D, rel_D, ta, tb, la_a, la_b


omega_ref = 0.37367 - 0.08896j

print("=" * 70)
print("AIM: Finding the N window for convergence detection")
print("=" * 70)

gc = lambda x, w: get_coeffs(x, w, formulation="dehghan")

# Step 1: detailed look at reference QNM for each N
print(f"\n--- Reference QNM (omega={omega_ref:.5f}) ---")
for N in [3, 4, 5, 6]:
    D, rel_D, ta, tb, la_a, la_b = aim_compare_full(gc, omega_ref, N)
    print(f"  N={N}: D={D:.4e}, rel_D={rel_D:.4f}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}, la_a={la_a:.4e}, la_b={la_b:.4e}")
    print(f"    ta={ta:.6e}, tb={tb:.6e}")

# Step 2: scan rel_D and raw D at N=4,5,6 for nearby omega values
print(f"\n--- Fine scan around reference QNM ---")
for N in [4, 5, 6]:
    print(f"\n  N={N}:")
    results = []
    for wr in np.arange(0.36, 0.39, 0.005):
        for wi in np.arange(-0.11, -0.06, 0.005):
            w = wr + 1j * wi
            D, rel_D, ta, tb, la_a, la_b = aim_compare_full(gc, w, N)
            dist = abs(w - omega_ref)
            results.append((D, rel_D, w, la_a, la_b, dist))

    results.sort(key=lambda r: r[1])  # sort by rel_D
    print(f"    Top 5 by rel_D:")
    for D, rel_D, w, la_a, la_b, dist in results[:5]:
        print(f"      w={w:.4f}: D={D:.4e}, rel_D={rel_D:.4f}, la_a={la_a:.2e}, la_b={la_b:.2e}, dist_to_ref={dist:.4f}")

    # Also show values at reference
    ref_D = next(r[0] for r in results if abs(r[2] - omega_ref) < 0.001)
    ref_rel = next(r[1] for r in results if abs(r[2] - omega_ref) < 0.001)
    print(f"    At ref: D={ref_D:.4e}, rel_D={ref_rel:.4f}")

    # Show bottom 3 (worst rel_D)
    print(f"    Worst 3 by rel_D:")
    for D, rel_D, w, la_a, la_b, dist in results[-3:]:
        print(f"      w={w:.4f}: D={D:.4e}, rel_D={rel_D:.4f}, la_a={la_a:.2e}, la_b={la_b:.2e}")

# Step 3: cho formulation
print(f"\n{'='*60}")
print(f"Cho formulation:")
print(f"{'='*60}")
gc_cho = lambda x, w: get_coeffs(x, w, formulation="cho")

print(f"\n--- Reference QNM (Cho) ---")
for N in [3, 4, 5, 6]:
    D, rel_D, ta, tb, la_a, la_b = aim_compare_full(gc_cho, omega_ref, N)
    print(f"  N={N}: D={D:.4e}, rel_D={rel_D:.4f}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}")

print(f"\n--- Fine scan (Cho) ---")
for N in [4, 5, 6]:
    print(f"\n  N={N}:")
    results = []
    for wr in np.arange(0.36, 0.39, 0.005):
        for wi in np.arange(-0.11, -0.06, 0.005):
            w = wr + 1j * wi
            D, rel_D, ta, tb, la_a, la_b = aim_compare_full(gc_cho, w, N)
            results.append((D, rel_D, w, la_a, la_b))

    results.sort(key=lambda r: r[1])
    print(f"    Top 5 by rel_D:")
    for D, rel_D, w, la_a, la_b in results[:5]:
        print(f"      w={w:.4f}: D={D:.4e}, rel_D={rel_D:.4f}")
    print(f"    Worst 3:")
    for D, rel_D, w, la_a, la_b in results[-3:]:
        print(f"      w={w:.4f}: D={D:.4e}, rel_D={rel_D:.4f}")
