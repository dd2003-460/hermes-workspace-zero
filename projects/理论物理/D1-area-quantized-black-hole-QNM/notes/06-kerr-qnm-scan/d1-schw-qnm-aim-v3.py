#!/usr/bin/env python3
"""
d1-schw-qnm-aim-v3: Fixed AIM with correct scaling and diagnostics.

Key fix: track scale factors per point separately to recover
unnormalized la_prev for correct theta = la_prev/la.

This corrects the normalization bug from v2 where la_prev got
divided by subsequent step scales, making theta meaningless.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}
XA = 0.35
XB = 0.65
DTOL = 1e-7
SCALE_TH = 1e50  # target magnitude per step


# ===================================================================
# AIM Coefficients
# ===================================================================

def get_aim_coeffs(x, omega, l, c_coeff):
    """
    Compute lambda_0(x) and mu_0(x) for y'' = lambda_0 y' + mu_0 y.

    Uses Cho six-factor gauge ansatz as starting point,
    with configurable potential coefficient c_coeff.
    """
    x = np.clip(x, 1e-14, 1.0 - 1e-14)
    r = 2.0 * M / (1.0 - x)

    # Base Regge-Wheeler coefficients in x coordinates
    P = 2.0 / (x * (1.0 - x)**2)
    a_base = (1.0 - 3.0 * x) / (x * (x - 1.0))  # = -d ln P / dx
    V = (1.0 - 2.0 * M / r) * (l * (l + 1.0) / r**2 - c_coeff * M / r**3)
    b_base = P**2 * (omega**2 - V)

    # Raw AIM: lambda_0 = -a_base, mu_0 = -b_base
    # Apply gauge transformation: psi -> psi * exp(chi)
    # lambda_new = lambda_old + 2*chi', mu_new = mu_old + lambda_old*chi' + 2*(chi')^2 + chi''

    # Cho gauge: chi' = 2iω/x - 2iω/(1-x) + 2iω/(1-x)^2
    # (removes singular behavior at both boundaries)
    chi_prime = 2j * omega / x - 2j * omega / (1.0 - x) + 2j * omega / (1.0 - x)**2
    chi_double_prime = -2j * omega / x**2 + 2j * omega / (1.0 - x)**2 - 4j * omega / (1.0 - x)**3

    lambda_0 = -(a_base + 2 * chi_prime)
    mu_0 = -(b_base + a_base * chi_prime + 2 * chi_prime**2 + chi_double_prime)

    return lambda_0, mu_0


# ===================================================================
# AIM iteration with CORRECT scaling (track scale factors)
# ===================================================================

def aim_run_fixed(omega, l, c_coeff, N=10, xa=XA, xb=XB):
    """
    Run AIM iterations at both evaluation points.

    CORRECT scaling: track scale_s_a, scale_s_b per point so we can
    recover the unnormalized lambda_{N-1} for correct theta = la_prev/la.

    Returns (D, C, theta_a, theta_b, la_final_a, la_final_b)
    """
    dx_num = 1e-7

    # Initial coefficients and derivatives
    def _init(y):
        la, mu = get_aim_coeffs(y, omega, l, c_coeff)
        dla = (get_aim_coeffs(y + dx_num, omega, l, c_coeff)[0] -
               get_aim_coeffs(y - dx_num, omega, l, c_coeff)[0]) / (2.0 * dx_num)
        dmu = (get_aim_coeffs(y + dx_num, omega, l, c_coeff)[1] -
               get_aim_coeffs(y - dx_num, omega, l, c_coeff)[1]) / (2.0 * dx_num)
        return la, mu, dla, dmu

    la_a, ma_a, dla_a, dmu_a = _init(xa)
    la_b, ma_b, dla_b, dmu_b = _init(xb)

    # Track cumulative scale factors
    scale_a = 1.0
    scale_b = 1.0
    la_prev_a, la_prev_b = la_a, la_b

    for k in range(N):
        la_prev_a_unscaled = la_a * scale_a  # recover unnormalized la_prev
        la_prev_b_unscaled = la_b * scale_b

        # AIM step
        ln_a = la_a**2 + dla_a - ma_a
        mn_a = la_a * dmu_a - ma_a * dla_a + ma_a**2
        dla_n = 2.0 * la_a * dla_a - dmu_a
        dmu_n = 2.0 * ma_a * dmu_a

        ln_b = la_b**2 + dla_b - ma_b
        mn_b = la_b * dmu_b - ma_b * dla_b + ma_b**2
        dla2_n = 2.0 * la_b * dla_b - dmu_b
        dmu2_n = 2.0 * ma_b * dmu_b

        # Normalize each point independently
        max_a = max(abs(ln_a), abs(mn_a), abs(dla_n), abs(dmu_n))
        max_b = max(abs(ln_b), abs(mn_b), abs(dla2_n), abs(dmu2_n))

        sc_a = max_a / SCALE_TH if max_a > SCALE_TH else 1.0
        sc_b = max_b / SCALE_TH if max_b > SCALE_TH else 1.0

        scale_a *= sc_a
        scale_b *= sc_b

        la_a, ma_a, dla_a, dmu_a = ln_a / sc_a, mn_a / sc_a, dla_n / sc_a, dmu_n / sc_a
        la_b, ma_b, dla_b, dmu_b = ln_b / sc_b, mn_b / sc_b, dla2_n / sc_b, dmu2_n / sc_b

    # Compute theta with correct normalization
    theta_a = la_prev_a_unscaled / la_a if abs(la_a) > 1e-200 else 0 + 0j
    theta_b = la_prev_b_unscaled / la_b if abs(la_b) > 1e-200 else 0 + 0j

    # D = |theta_a - theta_b|
    D = abs(theta_a - theta_b) if (abs(theta_a) > 1e-200 and abs(theta_b) > 1e-200) else 1e100

    # C = directional distance
    eps_dir = 1e-100
    theta_a_dir = theta_a / abs(theta_a) if abs(theta_a) > eps_dir else 0 + 0j
    theta_b_dir = theta_b / abs(theta_b) if abs(theta_b) > eps_dir else 0 + 0j
    C = abs(theta_a_dir - theta_b_dir)

    return D, C, theta_a, theta_b


# ===================================================================
# Diagnostics at known omega values
# ===================================================================

def diagnostics_at(omega, l, c_coeff, N_vals):
    """Print diagnostic values at a given omega."""
    for N in N_vals:
        D, C, ta, tb = aim_run_fixed(omega, l, c_coeff, N=N)
        print(f"    N={N:2d}: D={D:.6e}, C={C:.6e}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}")


# ===================================================================
# Grid search + local optimization
# ===================================================================

def find_eigenvalue(l, c_coeff, omega_guess=None):
    """Find QNM by minimizing C-indicator."""

    def objective(x):
        return aim_run_fixed(x[0] + 1j * x[1], l, c_coeff, N=8)[1]

    if omega_guess is None:
        omega_guess = complex(0.4, -0.09)

    re0 = max(omega_guess.real, 0.1)
    im0 = max(abs(omega_guess.imag), 0.02)

    # Coarse grid
    nr = max(15, int(4.0 / re0) + 5)
    ni = max(10, int(0.15 / im0) + 5)

    best_val = 1e100
    best_x0 = None

    for rr in np.linspace(0.05, 1.5, nr):
        for ri in np.linspace(-0.15, -0.005, ni):
            try:
                fval = objective([rr, ri])
            except Exception:
                continue
            if fval < best_val:
                best_val = fval
                best_x0 = (rr, ri)

    if best_x0 is None:
        return None, 1e100

    x0, y0 = best_x0

    # Fine grid around best
    fr = max(0.1, re0 * 2)
    fi = max(0.05, abs(y0) * 3)

    for rr in np.linspace(x0 - fr, x0 + fr, 15):
        for ri in np.linspace(y0 - fi, y0 + fi * 0.5, 12):
            try:
                fval = objective([rr, ri])
            except Exception:
                continue
            if fval < best_val:
                best_val = fval
                best_x0 = (rr, ri)

    x0, y0 = best_x0

    # Local refinement
    lb = max(0.01, x0 * 0.1)
    ub = max(3.0, x0 * 5.0)
    bi = min(-0.15, y0 * 3)
    bu = max(0.0, y0 * 0.2)

    result = minimize(objective, x0=[x0, y0], method='Nelder-Mead',
                      bounds=[(lb, ub), (bi, bu)],
                      options={'xatol': 1e-12, 'fatol': 1e-14,
                               'maxiter': 10000, 'adaptive': True})

    omega_found = complex(result.x[0], result.x[1])
    return omega_found, result.fun


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AIM v3 - Corrected Scaling")
    print("=" * 70)

    # Test convergence behavior of D and C at a given omega
    print("\n--- Convergence of D and C vs N (c=6, l=2, Berti) ---")
    omega_b = 0.37367 - 0.08896j
    diagnostics_at(omega_b, 2, 6, [5, 6, 7, 8, 9, 10, 12, 15, 20])

    print("\n--- Convergence of D and C vs N (c=6, l=2, Cardoso) ---")
    omega_c = complex(0.48982, -0.04314)
    diagnostics_at(omega_c, 2, 6, [5, 6, 7, 8, 9, 10, 12, 15, 20])

    # Grid scan for c=6, l=2 (looking for minimum C)
    print("\n--- Grid scan C-indicator, c=6, l=2 ---")
    best_C = 1e100
    best_w = None
    best_D = 1e100
    best_wD = None
    for wr in np.arange(0.1, 1.5, 0.05):
        for wi in np.arange(-0.15, -0.005, 0.005):
            w = complex(wr, wi)
            D, C, _, _ = aim_run_fixed(w, 2, 6, N=8)
            if C < best_C and C < 1.0:
                best_C = C
                best_w = w
            if D < best_D:
                best_D = D
                best_wD = w

    print(f"  Best C: {best_C:.6e} at omega={best_w}")
    print(f"  Best D: {best_D:.6e} at omega={best_wD}")
    print(f"  Berti:     0.37367 - 0.08896i")
    print(f"  Cardoso:   0.48982 - 0.04314i")

    # Grid scan for c=6, l=3
    print("\n--- Grid scan C-indicator, c=6, l=3 ---")
    best_C = 1e100
    best_w = None
    best_D = 1e100
    best_wD = None
    for wr in np.arange(0.3, 2.0, 0.05):
        for wi in np.arange(-0.15, -0.005, 0.005):
            w = complex(wr, wi)
            D, C, _, _ = aim_run_fixed(w, 3, 6, N=8)
            if C < best_C and C < 1.0:
                best_C = C
                best_w = w
            if D < best_D:
                best_D = D
                best_wD = w

    print(f"  Best C: {best_C:.6e} at omega={best_w}")
    print(f"  Best D: {best_D:.6e} at omega={best_wD}")
    print(f"  Berti: 0.59108 - 0.05902i")

    # Eigenvalue search
    print("\n--- Eigenvalue search (c=6, l=2) ---")
    omega_f, cval = find_eigenvalue(2, 6)
    print(f"  FOUND: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
    print(f"  C at found = {cval:.6e}")
    print(f"  Berti ref: 0.37367 - 0.08896i")

    print("\n--- Eigenvalue search (c=6, l=3) ---")
    omega_f, cval = find_eigenvalue(3, 6)
    print(f"  FOUND: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
    print(f"  C at found = {cval:.6e}")
    print(f"  Berti ref: 0.59108 - 0.05902i")

    # Test c=2 for comparison
    print("\n--- Eigenvalue search (c=2, l=2) ---")
    omega_f, cval = find_eigenvalue(2, 2)
    print(f"  FOUND: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
    print(f"  C at found = {cval:.6e}")

    print("\n--- Eigenvalue search (c=2, l=3) ---")
    omega_f, cval = find_eigenvalue(3, 2)
    print(f"  FOUND: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
    print(f"  C at found = {cval:.6e}")

    print("\n=== Done ===")
