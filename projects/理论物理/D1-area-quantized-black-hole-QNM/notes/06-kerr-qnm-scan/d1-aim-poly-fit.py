#!/usr/bin/env python3
"""
AIM with polynomial fit approach (Dehghan-Safari 2011).

Instead of comparing theta at two x-points (which fails due to different
growth rates), we evaluate theta at 3+ x-values and fit:
  theta_N(x) = A/(x - B)

The eigenvalue omega is such that B(omega) = omega (for the real part).

More precisely: at the eigenvalue, theta_N(x) becomes independent of x,
meaning the coefficient of 1/(x-B) in the theta expansion diverges while
B approaches the eigenvalue.

This approach avoids cross-point normalization entirely. Each x-value has
its own independent normalization.
"""

import numpy as np

M = 1.0


def get_coeffs(x, omega, l=2, formulation="raw"):
    """Compute lambda_0, mu_0 for the AIM ODE: y'' = lambda_0*y' + mu_0*y"""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)

    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a_base = -dlnP
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b_base = P**2 * (omega**2 - V)

    if formulation == "raw":
        return -a_base, -b_base

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


def aim_single_point(get_coeffs, omega, x, N=10):
    """Run AIM at a single x-point with independent normalization.

    Returns (theta_N, la_final) where theta = la_prev / la.
    """
    dx_num = 1e-6
    la, ma = get_coeffs(x, omega)
    dla = (get_coeffs(x + dx_num, omega)[0] - get_coeffs(x - dx_num, omega)[0]) / (2 * dx_num)
    dmu = (get_coeffs(x + dx_num, omega)[1] - get_coeffs(x - dx_num, omega)[1]) / (2 * dx_num)

    TARGET = 1e40

    for k in range(N):
        la_prev = la
        ln = la**2 + dla - ma
        mn = la * dmu - ma * dla + ma**2
        dla_n = 2 * la * dla - dmu
        dmu_n = 2 * ma * dmu

        max_val = max(abs(ln), abs(mn), abs(dla_n), abs(dmu_n))
        scale = max_val / TARGET if max_val > TARGET else 1.0

        la_prev /= scale

        la = ln / scale
        ma = mn / scale
        dla = dla_n / scale
        dmu = dmu_n / scale

    theta = la_prev / la
    return theta


def aim_poly_fit(get_coeffs, omega, N=8, x_values=None):
    """Fit theta_N(x) = A/(x - B) using multiple x-values.

    Returns (B, A, residuals) where B approximates the eigenvalue parameter.
    """
    if x_values is None:
        x_values = np.array([0.3, 0.4, 0.5, 0.6, 0.7])

    thetas = []
    for x in x_values:
        t = aim_single_point(get_coeffs, omega, x, N)
        thetas.append(t)
    thetas = np.array(thetas)

    # Fit: theta(x) = A/(x - B)
    # Rewrite: 1/theta = (x - B)/A = x/A - B/A
    # Linear fit: 1/theta = p1 * x + p0, where p1 = 1/A, p0 = -B/A
    # Then A = 1/p1, B = -p0/p1

    inv_thetas = 1.0 / thetas

    # Linear regression
    x_mean = x_values.mean()
    y_mean = inv_thetas.mean()
    num = np.sum((x_values - x_mean) * (inv_thetas - y_mean))
    den = np.sum((x_values - x_mean)**2)

    p1 = num / den  # slope
    p0 = y_mean - p1 * x_mean  # intercept

    A = 1.0 / p1
    B = -p0 / p1

    # Residuals
    theta_fit = A / (x_values - B)
    resid = np.abs(thetas - theta_fit).mean()

    # Goodness: |residuals| / |thetas|
    norm_resid = resid / np.abs(thetas).mean()

    return B, A, norm_resid, thetas


# ---- Test ----
print("=" * 70)
print("AIM Polynomial Fit")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j

# Check theta values at different x for the reference QNM
print(f"\n--- Theta values vs x at omega={omega_ref:.4f} ---")
for N in [4, 5, 6, 7, 8]:
    fn = lambda x, w: get_coeffs(x, w, formulation="raw")
    x_vals = np.array([0.3, 0.35, 0.4, 0.5, 0.6])
    thetas = np.array([aim_single_point(fn, omega_ref, x, N) for x in x_vals])
    print(f"  N={N}:")
    for x, t in zip(x_vals, thetas):
        print(f"    x={x}: theta={t:.6e}, |theta|={abs(t):.4e}")

    B, A, norm_res, _ = aim_poly_fit(fn, omega_ref, N, x_vals)
    print(f"  Fit: B={B:.6e}, A={A:.6e}, norm_resid={norm_res:.4e}")


# Now: scan for the minimum of norm_resid as a function of omega
# At the QNM, theta becomes x-independent, so norm_resid → 0
print(f"\n--- Scanning norm_resid (raw, N=6) ---")
x_fit = np.array([0.3, 0.35, 0.4, 0.5, 0.6])
fn = lambda x, w: get_coeffs(x, w, formulation="raw")

best_res, best_w = 1e30, None
for wr in np.arange(0.34, 0.40, 0.005):
    for wi in np.arange(-0.12, -0.05, 0.005):
        w = wr + 1j * wi
        B, A, nr, _ = aim_poly_fit(fn, w, N=6, x_values=x_fit)
        if nr < best_res:
            best_res = nr
            best_w = w
        star = " ***" if nr < 0.01 else (" *" if nr < 0.1 else "")
        if star:
            print(f"  w={wr:.3f}{wi:+.3f}j: norm_resid={nr:.4f}, B={B:.6e}{star}")

print(f"\n  Best: w={best_w:.5f}, norm_resid={best_res:.4e}")

# Same for Cho formulation
print(f"\n--- Scanning norm_resid (cho, N=6) ---")
fc = lambda x, w: get_coeffs(x, w, formulation="cho")

best_res, best_w = 1e30, None
for wr in np.arange(0.34, 0.40, 0.005):
    for wi in np.arange(-0.12, -0.05, 0.005):
        w = wr + 1j * wi
        B, A, nr, _ = aim_poly_fit(fc, w, N=6, x_values=x_fit)
        if nr < best_res:
            best_res = nr
            best_w = w
        star = " ***" if nr < 0.01 else (" *" if nr < 0.1 else "")
        if star:
            print(f"  w={wr:.3f}{wi:+.3f}j: norm_resid={nr:.4f}, B={B:.6e}{star}")

print(f"\n  Best: w={best_w:.5f}, norm_resid={best_res:.4e}")

# Same with N=7
print(f"\n--- Scanning norm_resid (raw, N=7) ---")
best_res, best_w = 1e30, None
for wr in np.arange(0.34, 0.40, 0.005):
    for wi in np.arange(-0.12, -0.05, 0.005):
        w = wr + 1j * wi
        B, A, nr, _ = aim_poly_fit(fn, w, N=7, x_values=x_fit)
        if nr < best_res:
            best_res = nr
            best_w = w
        star = " ***" if nr < 0.01 else (" *" if nr < 0.1 else "")
        if star:
            print(f"  w={wr:.3f}{wi:+.3f}j: norm_resid={nr:.4f}, B={B:.6e}{star}")

print(f"\n  Best: w={best_w:.5f}, norm_resid={best_res:.4e}")

# And N=5 (fewer iterations = less underflow)
print(f"\n--- Scanning norm_resid (raw, N=5) ---")
best_res, best_w = 1e30, None
for wr in np.arange(0.36, 0.39, 0.002):
    for wi in np.arange(-0.11, -0.07, 0.002):
        w = wr + 1j * wi
        B, A, nr, _ = aim_poly_fit(fn, w, N=5, x_values=x_fit)
        if nr < best_res:
            best_res = nr
            best_w = w
        if nr < 0.01:
            print(f"  w={wr:.3f}{wi:+.3f}j: norm_resid={nr:.6f}, B={B:.6e} ***")

print(f"\n  Best: w={best_w:.5f}, norm_resid={best_res:.6e}")
