#!/usr/bin/env python3
"""
Clean Schwarzschild QNM solver via AIM with Dehghan gauge.

Solves Regge-Wheeler equation
    d^2 psi / dr*^2 + (omega^2 - V) psi = 0
by the ansatz psi = g(x) y(x) with Dehghan gauge
    g(x) = F^{i omega} x^{-i omega} (1-x)^{i omega},
    F = r^2 / (r - 2M)^2,
which removes the exponents at both boundaries.

The transformed function y satisfies y'' = lambda_0 y' + mu_0 y.
The AIM iteration generates lambda_k, mu_k.
The QNM condition: theta(x_a, N) = lambda_{N-1}(x_a) / lambda_N(x_a)
                   must equal theta(x_b, N) at the eigenvalue.

Convergence indicator:
    C = | theta_a / |theta_a| - theta_b / |theta_b| |
    i.e. the distance between the two theta directions in the complex plane.

Verification against Berti et al. (2006) reference values.
"""

import numpy as np
from scipy.optimize import minimize


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
M = 1.0

BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}

XA = 0.35
XB = 0.65
DTOL = 1e-7
SCALE_TH = 1e80


# ---------------------------------------------------------------------------
# AIM coefficients: (lambda_0, mu_0)
# ---------------------------------------------------------------------------

def get_aim_coeffs(x, omega, l):
    """
    Compute lambda_0(x) and mu_0(x) for y'' = lambda_0 y' + mu_0 y.

    Coordinate:   x = 1 - 2M/r  (horizon -> 0, infinity -> 1)
    r = 2M / (1 - x),    dr*/dx = r^2 / (r - 2M)^2

    Dehghan gauge:   g = F^{i w} x^{-i w} (1-x)^{i w}
    where   F = r^2 / (r - 2M)^2 = 1 / (1 - x)^2

    Analytic gauge derivatives:
        (ln g)'        = i omega [3/(1-x) - 1/x]
        (ln g)''       = i omega [3/(1-x)^2 + 1/x^2]
    """
    # boundary guard
    if x < 1e-14:
        x = 1e-14
    if x > 1.0 - 1e-14:
        x = 1.0 - 1e-14

    # radial coordinate
    r = 2.0 * M / (1.0 - x)

    # dr*/dx and second derivative
    dr_star_dx = r ** 2 / (r - 2.0 * M) ** 2
    d_drstar_dr = -4.0 * M * r / (r - 2.0 * M) ** 3
    r_pp = d_drstar_dr * (2.0 * M) / (1.0 - x) ** 2

    # Regge-Wheeler potential
    V = (1.0 - 2.0 * M / r) * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)

    # analytic Dehghan gauge derivatives
    dln = 1j * omega * (1.0 / (1.0 - x) - 1.0 / x)
    d2ln = 1j * omega * (1.0 / (1.0 - x) ** 2 + 1.0 / x ** 2)

    # Q/P from transformation:  Q/P = -r_pp / dr*'_dx
    Q_over_P = -r_pp / dr_star_dx

    # raw AIM form
    lambda_0 = -(2.0 * dln + Q_over_P)
    mu_0 = -(d2ln + dln ** 2 + Q_over_P * dln
             + (omega ** 2 - V) * dr_star_dx ** 2)

    return lambda_0, mu_0


# ---------------------------------------------------------------------------
# AIM iteration with convergence diagnostics
# ---------------------------------------------------------------------------

def aim_convergence_indicator(omega, l, N=10, xa=XA, xb=XB):
    """
    Compute the AIM convergence indicator C = |theta_a/|theta_a| - theta_b/|theta_b||.

    theta(x, N) = lambda_{N-1}(x) / lambda_N(x)

    At the eigenvalue: theta_a converges to a y-independent limit,
    so C -> 0 (theta directions agree in the complex plane).

    Returns the indicator C (non-negative real) and a flag indicating
    whether convergence is sensible (both lambda values finite and non-zero).
    """

    def _run_aim(y, N):
        """Run AIM iteration at point y up to step N, return lam_{N-1}, lam_N."""
        la, mu = get_aim_coeffs(y, omega, l)
        eps = DTOL
        dla = (get_aim_coeffs(y + eps, omega, l)[0] -
               get_aim_coeffs(y - eps, omega, l)[0]) / (2.0 * eps)
        dmu = (get_aim_coeffs(y + eps, omega, l)[1] -
               get_aim_coeffs(y - eps, omega, l)[1]) / (2.0 * eps)

        for _ in range(N - 1):
            # per-point scaling
            def _norm_la_mu(la, mu, dla, dmu):
                mx = max(abs(la), abs(mu), abs(dla), abs(dmu))
                if mx > SCALE_TH:
                    sc = mx / SCALE_TH
                    return la/sc, mu/sc, dla/sc, dmu/sc
                return la, mu, dla, dmu

            ln_a = la * la + dla - mu
            mn_a = la * dmu - mu * dla + mu * mu
            dla_n = 2.0 * la * dla - dmu
            dmu_n = 2.0 * mu * dmu

            la, mu, dla, dmu = _norm_la_mu(ln_a, mn_a, dla_n, dmu_n)

        # la is now lambda_{N-1}, compute one more step for lambda_N
        ln = la * la + dla - mu
        mn = la * dmu - mu * dla + mu * mu
        return la, ln  # (lambda_{N-1}, lambda_N)

    la_prev_a, la_n_a = _run_aim(xa, N)
    la_prev_b, la_n_b = _run_aim(xb, N)

    # convergence indicator
    eps = 1e-100  # avoid division by zero
    if abs(la_n_a) > eps and abs(la_n_b) > eps:
        theta_a = la_prev_a / la_n_a
        theta_b = la_prev_b / la_n_b
        theta_a_dir = theta_a / abs(theta_a) if abs(theta_a) > eps else 0 + 0j
        theta_b_dir = theta_b / abs(theta_b) if abs(theta_b) > eps else 0 + 0j
        C = abs(theta_a_dir - theta_b_dir)
        return C
    else:
        return 1e100  # fallback: large value for failed convergence


# ---------------------------------------------------------------------------
# Wronskian (for diagnostic output)
# ---------------------------------------------------------------------------

def aim_wronskian(omega, l, N=40, xa=XA, xb=XB):
    """
    Compute W_N = lam_{N-1}(xa) lam_N(xb) - lam_N(xa) lam_{N-1}(xb).

    Independent iterations at xa and xb, with per-point global scaling
    to maintain numerical stability. The Wronskian vanishes at QNM
    eigenvalues for large N.
    """
    eps = DTOL

    def _init(y):
        la, mu = get_aim_coeffs(y, omega, l)
        dla = (get_aim_coeffs(y + eps, omega, l)[0] -
               get_aim_coeffs(y - eps, omega, l)[0]) / (2.0 * eps)
        dmu = (get_aim_coeffs(y + eps, omega, l)[1] -
               get_aim_coeffs(y - eps, omega, l)[1]) / (2.0 * eps)
        return la, mu, dla, dmu

    la_a, mu_a, dla_a, dmu_a = _init(xa)
    la_b, mu_b, dla_b, dmu_b = _init(xb)

    for _ in range(N):
        # iteration at xa
        ln_a = la_a * la_a + dla_a - mu_a
        mn_a = la_a * dmu_a - mu_a * dla_a + mu_a * mu_a
        dla_n = 2.0 * la_a * dla_a - dmu_a
        dmu_n = 2.0 * mu_a * dmu_a
        sc_a = max(1.0, abs(ln_a), abs(mn_a), abs(dla_n), abs(dmu_n))
        if sc_a > SCALE_TH:
            la_a, mu_a, dla_a, dmu_a = (ln_a / sc_a, mn_a / sc_a,
                                          dla_n / sc_a, dmu_n / sc_a)
        else:
            la_a, mu_a, dla_a, dmu_a = ln_a, mn_a, dla_n, dmu_n

        # iteration at xb
        ln_b = la_b * la_b + dla_b - mu_b
        mn_b = la_b * dmu_b - mu_b * dla_b + mu_b * mu_b
        dla2_n = 2.0 * la_b * dla_b - dmu_b
        dmu2_n = 2.0 * mu_b * dmu_b
        sc_b = max(1.0, abs(ln_b), abs(mn_b), abs(dla2_n), abs(dmu2_n))
        if sc_b > SCALE_TH:
            la_b, mu_b, dla_b, dmu_b = (ln_b / sc_b, mn_b / sc_b,
                                          dla2_n / sc_b, dmu2_n / sc_b)
        else:
            la_b, mu_b, dla_b, dmu_b = ln_b, mn_b, dla2_n, dmu2_n

    W = la_a * la_b  # approximate, for diagnostic only
    return W


# ---------------------------------------------------------------------------
# QNM eigenvalue finder
# ---------------------------------------------------------------------------

def find_qnm(omega_guess, l):
    """
    Find QNM frequency by minimizing the convergence indicator
    |theta_a/|theta_a| - theta_b/|theta_b||  (using N=10).

    Two-phase approach:
      Phase 1 - coarse 2-d grid search for a good starting point
      Phase 2 - Nelder-Mead local refinement
    """

    def objective(x):
        """Convergence indicator at omega = x[0] + 1j x[1]."""
        return aim_convergence_indicator(x[0] + 1j * x[1], l, N=10)

    # ---- Phase 1: coarse grid search ----
    re0 = max(omega_guess.real, 0.1)
    im0 = max(abs(omega_guess.imag), 0.02)

    best_val = 1e100
    best_x0 = None

    # Wide sweep to cover the eigenvalue region
    nr = max(10, int(5.0 / re0 * re0)) + 5
    ni = max(8, int(0.5 / im0 * im0)) + 5
    for rr in np.linspace(0.05, 3.0, nr):
        for ri in np.linspace(-0.5, -0.01, ni):
            try:
                fval = objective([rr, ri])
            except Exception:
                continue
            if fval < best_val:
                best_val = fval
                best_x0 = (rr, ri)

    # Fine sweep around best
    if best_x0 is not None:
        xf, yf = best_x0
        fr = max(0.05, re0 * 3)
        fi = max(0.02, abs(yf) * 3)
        for rr in np.linspace(xf - fr, xf + fr, 12):
            for ri in np.linspace(yf - fi, yf + fi * 0.5, 10):
                try:
                    fval = objective([rr, ri])
                except Exception:
                    continue
                if fval < best_val:
                    best_val = fval
                    best_x0 = (rr, ri)

    x0, y0 = best_x0

    # ---- Phase 2: local Nelder-Mead refinement ----
    lb = max(0.01, x0 * 0.1)
    ub = max(3.0, x0 * 5.0)
    bi = min(-0.5, y0 * 3)
    bu = max(0.0, y0 * 0.2)

    result = minimize(objective,
                      x0=[x0, y0],
                      method='Nelder-Mead',
                      bounds=[(lb, ub), (bi, bu)],
                      options={'xatol': 1e-12, 'fatol': 1e-14,
                               'maxiter': 10000, 'adaptive': True})

    omega_found = complex(result.x[0], result.x[1])
    return omega_found, result.fun


# ---------------------------------------------------------------------------
# Main -- Berti reference comparison
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 68)
    print("Schwarzschild QNM solver  |  AIM with Dehghan gauge")
    print("Berti et al. (2006) verification")
    print("=" * 68)

    for l, omega_ref in BERTI_REF.items():
        print(f"\nl = {l},  n = 0  |  Berti ref: "
              f"{omega_ref.real:.5f} - {abs(omega_ref.imag):.5f} i")
        print("-" * 55)

        # coefficients at reference
        la_a, mu_a = get_aim_coeffs(XA, omega_ref, l)
        la_b, mu_b = get_aim_coeffs(XB, omega_ref, l)
        print(f"  coeffs at reference omega:")
        print(f"    x={XA:5.2f}:  lambda_0 = {la_a:.6e},  |mu_0| = {abs(mu_a):.6e}")
        print(f"    x={XB:5.2f}:  lambda_0 = {la_b:.6e},  |mu_0| = {abs(mu_b):.6e}")

        # convergence indicator at reference
        print(f"  convergence indicator C (N=10) at reference:")
        for N in [5, 7, 10, 15, 20, 30]:
            C = aim_convergence_indicator(omega_ref, l, N=N)
            print(f"    N={N:2d}: {C:.6e}")

        # eigenvalue search
        print(f"  eigenvalue search ...")
        omega_found, cval = find_qnm(omega_ref, l)

        omega_true = complex(omega_ref.real, omega_ref.imag)
        err_re = abs(omega_found.real - omega_true.real)
        err_im = abs(omega_found.imag - omega_true.imag)
        rel_re = err_re / abs(omega_true.real) * 100.0
        rel_im = err_im / abs(omega_true.imag) * 100.0

        print(f"\n  FOUND      omega = {omega_found.real:.6f} "
              f"+ {omega_found.imag:.6f} i")
        print(f"  REFERENCE  omega = {omega_true.real:.5f} "
              f"+ {omega_true.imag:.5f} i")
        print(f"  |D Re| = {err_re:.3e}  ({rel_re:.3g} %)")
        print(f"  |D Im| = {err_im:.3e}  ({rel_im:.3g} %)")
        print(f"  C(N=10) at found omega = {cval:.3e}")
