#!/usr/bin/env python3
"""
AIM v2: robust AIM with careful scaling.

Key insight from Dehghan-Safari 2011: the AIM convergence criterion works
when BOTH evaluation points keep finite lambda values after normalization.
If one point overflows/underflows before the other, D is meaningless.

Strategy:
1. Use evaluation points xa=0.35, xb=0.65 (away from singularities)
2. Always scale every step (don't wait for overflow). Use scale=1 when not needed.
3. Track step-by-step |lambda| to debug.
4. Use small N (7-12) where values are manageable.
"""

import numpy as np

M = 1.0

def get_coeffs(x, omega, l=2, formulation="dehghan"):
    """Compute lambda_0, mu_0 and derivatives."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)

    # Base RW coefficients in x coords
    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a_base = -dlnP
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b_base = P**2 * (omega**2 - V)

    if formulation == "raw":
        # No gauge transform: lambda_0 = -a_base, mu_0 = -b_base
        return -a_base, -b_base

    elif formulation == "dehghan":
        # Dehghan gauge: G = F^(iw) * x^(-iw) * (1-x)^(iw) * exp(-iw/(1-x))
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
        # Cho six-factor ansatz
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

    raise ValueError(f"Unknown formulation: {formulation}")


def aim_step(la, ma, dla, dmu):
    """One AIM step. Returns new lambda, mu, dla, dmu."""
    ln = la**2 + dla - ma
    mn = la * dmu - ma * dla + ma**2
    dla_n = 2 * la * dla - dmu
    dmu_n = 2 * ma * dmu
    return ln, mn, dla_n, dmu_n


def aim_run(get_coeffs, omega, N=10, xa=0.35, xb=0.65, verbose=False):
    """Robust AIM with per-step normalization.

    Normalizes BOTH points by the same factor each step.
    Uses scale = max(|values|) / TARGET where TARGET = 1e50.
    This keeps values well below overflow while above underflow.
    """
    TARGET = 1e50
    dx_num = 1e-6

    la_a, ma_a = get_coeffs(xa, omega)
    la_b, ma_b = get_coeffs(xb, omega)
    dla_a = (get_coeffs(xa + dx_num, omega)[0] - get_coeffs(xa - dx_num, omega)[0]) / (2 * dx_num)
    dmu_a = (get_coeffs(xa + dx_num, omega)[1] - get_coeffs(xa - dx_num, omega)[1]) / (2 * dx_num)
    dla_b = (get_coeffs(xb + dx_num, omega)[0] - get_coeffs(xb - dx_num, omega)[0]) / (2 * dx_num)
    dmu_b = (get_coeffs(xb + dx_num, omega)[1] - get_coeffs(xb - dx_num, omega)[1]) / (2 * dx_num)

    for k in range(N):
        la_prev_a = la_a
        la_prev_b = la_b

        ln_a, mn_a, dla_na, dmu_na = aim_step(la_a, ma_a, dla_a, dmu_a)
        ln_b, mn_b, dla_nb, dmu_nb = aim_step(la_b, ma_b, dla_b, dmu_b)

        # Global scale: bring max value down to TARGET
        max_val = max(abs(ln_a), abs(ln_b), abs(mn_a), abs(mn_b),
                      abs(dla_na), abs(dmu_na), abs(dla_nb), abs(dmu_nb))
        scale = max_val / TARGET if max_val > TARGET else 1.0

        la_prev_a /= scale
        la_prev_b /= scale

        la_a, ma_a, dla_a, dmu_a = ln_a / scale, mn_a / scale, dla_na / scale, dmu_na / scale
        la_b, ma_b, dla_b, dmu_b = ln_b / scale, mn_b / scale, dla_nb / scale, dmu_nb / scale

        if verbose:
            print(f"  k={k:2d}: |la|_a={abs(la_a):.4e}, |la|_b={abs(la_b):.4e}, "
                  f"scale={scale:.4e}, max={max_val:.4e}")

    theta_a = la_prev_a / la_a
    theta_b = la_prev_b / la_b
    D = abs(theta_a - theta_b)

    return D, theta_a, theta_b


# ---- Run ----
print("=" * 70)
print("AIM v2 - Robust Normalization")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j

for form in ["raw", "dehghan", "cho"]:
    print(f"\n--- {form.upper()} formulation ---")
    xa, xb = 0.35, 0.65
    for label, x in [("xa", xa), ("xb", xb)]:
        lam, mu = get_coeffs(x, omega_ref, formulation=form)
        print(f"  {label}={x}: lam0={lam:.6e}, mu0={mu:.6e}")

    # Convergence vs N
    for N in [4, 5, 6, 7, 8, 9, 10, 12]:
        D, ta, tb = aim_run(lambda x, w: get_coeffs(x, w, formulation=form),
                            omega_ref, N=N)
        print(f"  N={N:2d}: D={D:.6e}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}")

# Fine scan near QNM (dehghan formulation, N=8)
print(f"\n--- Fine scan near QNM (dehghan, N=8) ---")
fn = lambda x, w: get_coeffs(x, w, formulation="dehghan")
for wr in np.arange(0.36, 0.388, 0.004):
    for wi in np.arange(-0.105, -0.065, 0.005):
        w = wr + 1j * wi
        D, _, _ = aim_run(fn, w, N=8)
        if D < 1:
            print(f"  w={wr:.3f}{wi:+.3f}j: D={D:.4f} ***")
        elif D < 10:
            print(f"  w={wr:.3f}{wi:+.3f}j: D={D:.2f} *")

# Fine scan near QNM (cho formulation, N=8)
print(f"\n--- Fine scan near QNM (cho, N=8) ---")
fc = lambda x, w: get_coeffs(x, w, formulation="cho")
for wr in np.arange(0.36, 0.388, 0.004):
    for wi in np.arange(-0.105, -0.065, 0.005):
        w = wr + 1j * wi
        D, _, _ = aim_run(fc, w, N=8)
        if D < 1:
            print(f"  w={wr:.3f}{wi:+.3f}j: D={D:.4f} ***")
        elif D < 10:
            print(f"  w={wr:.3f}{wi:+.3f}j: D={D:.2f} *")

# Verbose run at reference omega
print(f"\n--- Verbose run (dehghan, N=10, omega={omega_ref:.4f}) ---")
aim_run(fn, omega_ref, N=10, verbose=True)

print(f"\n--- Verbose run (cho, N=10, omega={omega_ref:.4f}) ---")
aim_run(fc, omega_ref, N=10, verbose=True)
