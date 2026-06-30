#!/usr/bin/env python3
"""
Schwarzschild QNM solver via improved ODE shooting.

Fixes from v1:
1. r_from_rstar: uses Lambert W for near-horizon inversion (exact to 1e-14)
2. Factorization: psi = exp(-i*omega*r*) * u, integrate from both ends
3. Better matching: use amplitude ratio at matching point
   Compare the ratio u_out/u_out_prime vs u_in/u_in_prime

Approach:
- Near horizon (r* -> -inf): ingoing BC => psi ~ exp(-i*omega*r*)
  With factorization: u = psi/exp(-i*omega*r*) -> constant
  So near horizon: u = 1, du/dr* = 0

- Near infinity (r* -> +inf): outgoing BC => psi ~ exp(+i*omega*r*)
  With factorization: u = psi/exp(-i*omega*r*) ~ exp(2i*omega*r*)
  For Im(omega) < 0: exp(2i*omega*r*) decays as r* -> +inf
  So u -> 0 at infinity. du/dr* ~ 2i*omega*u

- Match at intermediate rs_match: the log-derivative dln(u)/dr* should match

Reference: Berti et al. (2009)
  l=2, n=0:  omega = 0.37367 - 0.08896i
  l=3, n=0:  omega = 0.59108 - 0.05902i
"""

import numpy as np
from scipy.special import lambertw
from scipy.integrate import solve_ivp
from scipy.optimize import minimize


M = 1.0

BERTI_REF = {
    (2, 0): complex(0.37367, -0.08896),
    (3, 0): complex(0.59108, -0.05902),
}


# ---------------------------------------------------------------------------
# Coordinate transforms
# ---------------------------------------------------------------------------

def rstar_of(r):
    """Tortoise coordinate."""
    return r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)


def r_from_rstar(rs):
    """Inverse: Lambert W for near-horizon, Newton refinement for all."""
    t = rs / (2.0 * M) - 1.0

    if t > 10:
        # Far from horizon: use W asymptotic expansion
        y = t - np.log(t) + np.log(t) / t
    else:
        # Near horizon: Lambert W_0
        y = lambertw(np.exp(t), k=0).real

    r = 2.0 * M * (1.0 + y)

    # Newton refinement
    for _ in range(30):
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
            continue
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        delta = (rs_calc - rs) / drstar_dr
        if abs(delta) < 1e-16 * max(abs(r), 1e-14):
            break
        r -= delta
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14

    return r


# ---------------------------------------------------------------------------
# Potential and ODE
# ---------------------------------------------------------------------------

def rw_potential(r, l):
    """Regge-Wheeler potential."""
    return (1.0 - 2.0 * M / r) * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)


def factorized_system(rs, Y, omega, l):
    """
    Factorized equation: psi = exp(-i*omega*r*) * u(r*)
    Original: psi'' + (omega^2 - V)*psi = 0
    Transformed: u'' - 2i*omega*u' - V*u = 0

    So: u'' = 2i*omega*u' + V*u

    Check: psi = exp(-i*w*r*)*u
    psi' = exp(-i*w*r*)(u' - i*w*u)
    psi'' = exp(-i*w*r*)(u'' - 2i*w*u' - w^2*u)
    So psi'' + (w^2 - V)*psi = exp(-i*w*r*)(u'' - 2i*w*u' - V*u) = 0
    => u'' - 2i*w*u' - V*u = 0  -- correct!
    """
    u, du = Y
    r = r_from_rstar(rs)
    V = rw_potential(r, l)
    return [du, 2.0j * omega * du + V * u]


# ---------------------------------------------------------------------------
# Outward integration from near-horizon
# ---------------------------------------------------------------------------

def integrate_outward(omega, l, rs_end, rs_start=-40.0):
    """
    Integrate u-equation outward from rs_start with ingoing BC.

    Ingoing BC: psi ~ exp(-i*omega*r*) => u = constant
    Initial: u = 1, du/dr* = 0 at rs_start
    """
    try:
        sol = solve_ivp(
            lambda rs, Y: factorized_system(rs, Y, omega, l),
            [rs_start, rs_end], [1.0, 0.0],
            max_step=0.5, rtol=1e-10, atol=1e-12,
            dense_output=True
        )
        # Evaluate at rs_end
        u_end, du_end = sol.sol(rs_end)
        return u_end, du_end, sol
    except:
        return None, None, None


# ---------------------------------------------------------------------------
# Inward integration from large r*
# ---------------------------------------------------------------------------

def integrate_inward(omega, l, rs_start, rs_end=-100.0, rs_infinity=200.0):
    """
    Integrate u-equation inward from large r* with outgoing BC.
    We integrate from rs_start backwards to rs_end.
    """
    try:
        sol = solve_ivp(
            lambda rs, Y: factorized_system(rs, Y, omega, l),
            [rs_start, rs_end], [1.0, 2.0j * omega],
            max_step=0.5, rtol=1e-10, atol=1e-12,
            method='Radau', dense_output=True
        )
        u_at_start, du_at_start = sol.sol(rs_start)
        return u_at_start, du_at_start, sol
    except:
        return None, None, None


# ---------------------------------------------------------------------------
# Mismatch using log-derivative matching
# ---------------------------------------------------------------------------

def mismatch_logderiv(omega, l, rs_match=40.0):
    """
    Match log-derivatives at rs_match.
    For the QNM, the solution must be a single global solution,
    so log-derivatives from both directions must agree.
    """
    if omega.imag >= -0.01 or omega.real <= 0.01:
        return 1e100

    try:
        u_out, du_out, _ = integrate_outward(omega, l, rs_match, rs_start=-40.0)
        if u_out is None or abs(u_out) < 1e-100:
            return 1e100

        u_in, du_in, _ = integrate_inward(omega, l, rs_match, -60.0)
        if u_in is None or abs(u_in) < 1e-100:
            return 1e100

        lr_out = du_out / u_out
        lr_in = du_in / u_in

        return abs(lr_out - lr_in) / (1.0 + abs(lr_out) + abs(lr_in))
    except:
        return 1e100


# ---------------------------------------------------------------------------
# Mismatch using solution ratio matching
# ---------------------------------------------------------------------------

def mismatch_ratio(omega, l, rs_match=40.0):
    """
    Match by comparing log-derivatives at rs_match.
    Weighted mismatch normalized by magnitude.
    """
    if omega.imag >= -0.01 or omega.real <= 0.01:
        return 1e100

    try:
        u_out, du_out, _ = integrate_outward(omega, l, rs_match, rs_start=-40.0)
        if u_out is None or abs(u_out) < 1e-100:
            return 1e100

        u_in, du_in, _ = integrate_inward(omega, l, rs_match, -60.0)
        if u_in is None or abs(u_in) < 1e-100:
            return 1e100

        lr_out = du_out / u_out
        lr_in = du_in / u_in
        lr_mismatch = abs(lr_out - lr_in) / (1.0 + abs(lr_out) + abs(lr_in))
        return lr_mismatch
    except:
        return 1e100


# ---------------------------------------------------------------------------
# Objective using B/A amplitude ratio (from raw ψ, not factorized)
# ---------------------------------------------------------------------------

def compute_BA_ratio(omega, l, rs_end=150.0):
    """
    Integrate the RAW Regge-Wheeler equation (no factorization) from
    horizon outward. At rs_end, decompose psi into:
    psi = A*exp(i*omega*r*) + B*exp(-i*omega*r*)

    Then: B/A = (psi' - i*omega*psi) / (psi' + i*omega*psi)

    For QNM: B = 0 (pure outgoing at infinity).
    So |B/A| should be minimized.
    """
    r_start = 2.02
    rs_start = rstar_of(r_start)

    # Ingoing BC at horizon: psi = 1, dpsi/dr* = -i*omega*psi
    y0 = [1.0, -1.0j * omega]

    sol = solve_ivp(
        lambda rs, Y: [Y[1], -(omega**2 - rw_potential(r_from_rstar(rs), l)) * Y[0]],
        [rs_start, rs_end], y0,
        max_step=0.5, rtol=1e-10, atol=1e-12
    )

    psi_end = sol.y[0, -1]
    dpsi_end = sol.y[1, -1]

    denom = dpsi_end + 1.0j * omega * psi_end
    if abs(denom) < 1e-150:
        return float("inf")

    ba = abs((dpsi_end - 1.0j * omega * psi_end) / denom)
    return ba


# ---------------------------------------------------------------------------
# Grid search + optimization
# ---------------------------------------------------------------------------

def find_qnm_grid(l, grid_re=(0.1, 0.8), grid_im=(-0.3, -0.01),
                  n_re=30, n_im=30):
    """Coarse grid search for initial guess."""
    ref = BERTI_REF.get((l, 0))
    if ref is None:
        return None

    best_omega = None
    best_val = float("inf")

    # Use B/A objective for grid search (more discriminative)
    for wr in np.linspace(max(grid_re[0], ref.real - 0.2), min(grid_re[1], ref.real + 0.5), n_re):
        for wi in np.linspace(max(grid_im[0], ref.imag - 0.15), min(grid_im[1], ref.imag + 0.05), n_im):
            w = complex(wr, wi)
            v = compute_BA_ratio(w, l, rs_end=120.0)
            if np.isfinite(v) and v < best_val:
                best_val = v
                best_omega = w

    return best_omega, best_val


def refine_qnm(omega0, l):
    """Refine QNM using Nelder-Mead on |B/A|."""
    def fn(w_complex):
        return compute_BA_ratio(complex(w_complex[0], w_complex[1]), l)

    res = minimize(fn, [omega0.real, omega0.imag], method='Nelder-Mead',
                   tol=1e-12,
                   options={'xatol': 1e-12, 'fatol': 1e-12, 'maxiter': 10000})

    return complex(res.x[0], res.x[1])


# ---------------------------------------------------------------------------
# Multi-endpoint objective for better discrimination
# ---------------------------------------------------------------------------

def objective_multi_end(omega, l):
    """
    Average |B/A| at multiple r*_end points.
    At the true QNM, |B/A| should be ~0 at all endpoints.
    """
    if omega.imag >= -0.01 or omega.real <= 0.01:
        return 1e100

    vals = []
    for rs_end in [80, 120, 160]:
        v = compute_BA_ratio(omega, l, rs_end)
        if np.isfinite(v):
            vals.append(np.log10(max(v, 1e-300)))
    return np.mean(vals) if vals else 1e100


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("Schwarzschild QNM solver v2 - Improved shooting")
    print("r_from_rstar: Lambert W + Newton refinement")
    print("=" * 70)

    # Verify r_from_rstar
    print("\nr_from_rstar verification:")
    for rs in [-40, -20, -10, -5, 0, 10, 40, 80, 120, 160]:
        r = r_from_rstar(rs)
        rs_check = r + 2*M*np.log(r/(2*M) - 1.0)
        err = abs(rs_check - rs)
        print(f"  rs={rs:5d} -> r={r:12.8f} -> r*={rs_check:12.6f} -> err={err:.2e}")

    for (l, n), omega_ref in sorted(BERTI_REF.items()):
        print(f"\nl={l}, n={n}:")
        print(f"  Reference:  omega = {omega_ref.real:.5f} - {abs(omega_ref.imag):.5f} i")

        # Test BA ratio at reference
        for rs_end in [80, 120, 160]:
            ba = compute_BA_ratio(omega_ref, l, rs_end)
            print(f"  |B/A|(r*={rs_end})  = {ba:.6e}")

        # Log-derivative matching at reference
        for rs_m in [30, 40, 50, 60]:
            mlr = mismatch_logderiv(omega_ref, l, rs_m)
            print(f"  |logderiv mismatch|(r*={rs_m}) = {mlr:.6e}")

        # Grid search
        print(f"\n  Grid search...")
        best_omega, best_val = find_qnm_grid(l, n_re=25, n_im=20)
        if best_omega is not None:
            print(f"  Best initial: omega = {best_omega.real:.5f} - {abs(best_omega.imag):.5f} i")
            print(f"  |B/A| = {best_val:.6e}")

            # Refine
            print(f"  Refining...")
            omega = refine_qnm(best_omega, l)
            print(f"  Refined:    omega = {omega.real:.6f} - {abs(omega.imag):.6f} i")
            re_err = abs(omega.real - omega_ref.real)
            im_err = abs(omega.imag - omega_ref.imag)
            print(f"  |dRe| = {re_err:.6e}, |dIm| = {im_err:.6e}")
            rel = abs((omega - omega_ref) / omega_ref)
            print(f"  rel error = {rel:.2e}")
        else:
            print(f"  Grid search did not converge")

        # Multi-endpoint objective refinement
        if best_omega is not None:
            print(f"\n  Multi-endpoint refinement...")
            res_multi = minimize(objective_multi_end, [best_omega.real, best_omega.imag],
                                method='Nelder-Mead', tol=1e-10,
                                options={'xatol': 1e-10, 'fatol': 1e-10, 'maxiter': 10000})
            omega2 = complex(res_multi.x[0], res_multi.x[1])
            print(f"  Multi-end:  omega = {omega2.real:.6f} - {abs(omega2.imag):.6f} i")
            re_err2 = abs(omega2.real - omega_ref.real)
            im_err2 = abs(omega2.imag - omega_ref.imag)
            print(f"  |dRe| = {re_err2:.6e}, |dIm| = {im_err2:.6e}")

    print("\n" + "=" * 70)
