#!/usr/bin/env python3
"""
Teukolsky + AIM v7: Kerr QNM Solver
=====================================
Clean implementation matching d1-clean-solver.py exactly.

1. Log-derivative matching on RW ODE (ground truth)
2. AIM on Teukolsky coefficients with new convergence metric

Test: at a=0, must reproduce Berti grav = 0.37367-0.08896i for l=2.
"""

import numpy as np
from scipy.integrate import solve_ivp

M = 1.0
s = -2


# =====================================================================
# Method 1: Log-derivative matching on RW ODE
# =====================================================================

def pot(r, l=2):
    """Gravitational RW potential: V = f*(l(l+1)-6M/r)/r^2"""
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1) - 6.0 * M / r) / r**2


def rhs_rt(r, y, omega, pot_fn):
    """
    State: y = [psi, dpsi/dr] (derivative wrt radial coordinate r).
    From d²ψ/dr*² + (ω²-V)ψ = 0 and d²ψ/dr*² = f·d²ψ/dr² + f'·dpsi/dr:
      f·d²ψ/dr² + f'·dpsi/dr = -(ω²-V)·psi
      d²ψ/dr² = -(ω²-V)/f · psi - f'/f · dpsi/dr
    """
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot_fn(r)
    dy0 = y[1]
    dy1 = -(omega**2 - V) / f * y[0] - f_prime / f * y[1]
    return np.array([dy0, dy1])


def r_star(r):
    """Tortoise coordinate for infinity BC."""
    x = r / (2.0 * M)
    return r + 2.0 * M * np.log(x - 1.0) + 3.0 * M * np.log(3.0 * x / 2.0 - 1.0)


def log_deriv(omega, pot_fn, r_match, direction='L', eps=1e-8, r_inf=80.0):
    """Compute dpsi/dr / psi (= dpsi/dr* / psi, since dpsi/dr* = f·dpsi/dr and f→1 at r_match)."""
    if direction == 'L':
        r0 = 2.0 * M + eps
        # Horizon: psi = 1, dpsi/dr* = -iω (ingoing)
        y0 = np.array([1.0, -1j * omega])
        sol = solve_ivp(rhs_rt, [r0, r_match], y0, method='RK45',
                        args=(omega, pot_fn), dense_output=True,
                        max_step=0.5, atol=1e-14, rtol=1e-11)
    else:
        # Infinity: psi = exp(iω r*), dpsi/dr* = iω · exp(iω r*)
        # Must use the exponentially large amplitude, NOT y0=[1, iω]
        # (roundoff at r_inf would be amplified exponentially inward)
        psi_rinf = np.exp(1j * omega * r_star(r_inf))
        y0 = np.array([psi_rinf, 1j * omega * psi_rinf])
        sol = solve_ivp(rhs_rt, [r_inf, r_match], y0, method='RK45',
                        args=(omega, pot_fn), dense_output=True,
                        max_step=0.5, atol=1e-14, rtol=1e-11)

    if not sol.success:
        return None
    psi, dpsi_drstar = sol.sol(r_match)
    if abs(psi) < 1e-30:
        return None
    return dpsi_drstar / psi


def shoot(omega, pot_fn, r_match):
    """Log-derivative matching. Returns rel_dist, rL, rR."""
    rL = log_deriv(omega, pot_fn, r_match, direction='L')
    rR = log_deriv(omega, pot_fn, r_match, direction='R')
    if rL is None or rR is None:
        return np.inf, None, None
    rel_dist = abs(rL - rR) / abs(rR)
    return rel_dist, rL, rR


# =====================================================================
# Method 2: AIM on Teukolsky coefficients (same as v7 draft)
# =====================================================================

def teukolsky_coeffs_x(x, omega, l=2, m=2, a=0.0):
    """Teukolsky ODE in Poincare coordinate x = 1 - r_+/r.
    d²R/dx² = A_coeff * dR/dx + B_coeff * R
    """
    x = np.clip(x, 1e-10, 1 - 1e-10)
    rp = M + np.sqrt(max(M**2 - a**2, 0))
    rm = M - np.sqrt(max(M**2 - a**2, 0))
    r = rp / (1.0 - x)
    dr_dx = rp / (1.0 - x)**2
    d2r_dx2 = 2.0 * rp / (1.0 - x)**3

    Delta = (r - rp) * (r - rm)
    dDelta_dr = 2.0 * r - 2.0 * M
    P_r = (s + 1.0) * dDelta_dr / Delta
    K = (r**2 + a**2) * omega - a * m
    U = K**2 / Delta**2 - 4.0 * s * omega * r / Delta + l * (l + 1)

    A_coeff = d2r_dx2 / dr_dx - dr_dx * P_r
    B_coeff = -dr_dx**2 * U
    return A_coeff, B_coeff


def aim_teukolsky_full(omega, l, a, m, N=120, xa=0.3, xb=0.7):
    """AIM on Teukolsky coefficients with new convergence metric."""
    dx = 1e-8
    MAX_S = 1e80

    def get_coeffs(xpt):
        return teukolsky_coeffs_x(xpt, omega, l, m, a)

    Aa, Ba = get_coeffs(xa)
    Ap, Bp = get_coeffs(xa + dx)
    Am, Bm = get_coeffs(xa - dx)
    dAdx_a = (Ap - Am) / (2 * dx)
    dBdx_a = (Bp - Bm) / (2 * dx)

    Ab, Bb = get_coeffs(xb)
    Ap, Bp = get_coeffs(xb + dx)
    Am, Bm = get_coeffs(xb - dx)
    dAdx_b = (Ap - Am) / (2 * dx)
    dBdx_b = (Bp - Bm) / (2 * dx)

    lsa, msa = Aa, Ba
    lsb, msb = Ab, Bb
    dla, dqa = dAdx_a, dBdx_a
    dlb, dqb = dAdx_b, dBdx_b

    history = []

    for k in range(1, N + 1):
        lna = lsa**2 + dla - msa
        mna = lsa * dqa - msa * dla + msa**2
        ln_b = lsb**2 + dlb - msb
        mn_b = lsb * dqb - msb * dlb + msb**2

        scale = max(abs(lna), abs(mna), abs(ln_b), abs(mn_b), 1e-30)
        if scale > MAX_S:
            lna /= scale; mna /= scale; ln_b /= scale; mn_b /= scale
            dla /= scale; dqa /= scale; dlb /= scale; dqb /= scale
            lsa /= scale; msa /= scale; lsb /= scale; msb /= scale

        dla_new = 2.0 * lsa * dla - dqa
        dqb_a = 2.0 * msa * dqa
        dlb_new = 2.0 * lsb * dlb - dqb
        dqb_b = 2.0 * msb * dqb

        if scale > MAX_S:
            dla_new /= scale; dqb_a /= scale
            dlb_new /= scale; dqb_b /= scale

        lsa, msa = lna, mna
        lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqb_a
        dlb, dqb = dlb_new, dqb_b

        history.append((k, abs(lsa), abs(lsb)))

    metric = abs(lsa - lsb) / (abs(lsa) + abs(lsb) + 1e-30)
    return metric, lsa, lsb, history


# =====================================================================
# Tests
# =====================================================================

print("=" * 70)
print("Teukolsky + AIM v7 — Corrected RHS")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j
l = 2
m = 2

# ---- Test A: Log-derivative matching (ground truth) ----
print(f"\n--- Test A: Log-derivative matching (ground truth) ---")
print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

for rm in [50, 100, 150, 200]:
    rd, rL, rR = shoot(omega_ref, pot, rm)
    print(f"  grav pot, r_match={rm:3d}: rel_dist={rd:.6e}, rL={rL:.6f}, rR={rR:.6f}")

# Also test scalar potential
print(f"\n  Scalar potential:")
for rm in [50, 100, 150, 200]:
    pot_s = lambda r, l=l: (1.0 - 2.0 * M / r) * l * (l + 1) / r**2
    rd, rL, rR = shoot(omega_ref, pot_s, rm)
    print(f"    r_match={rm:3d}: rel_dist={rd:.6e}")

# ---- Test B: AIM metric scan ----
print(f"\n--- Test B: AIM metric scan at a=0 ---")
print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

min_met, best = np.inf, None
for wr in np.linspace(0.30, 0.45, 30):
    for wi in np.linspace(-0.15, -0.02, 25):
        met, _, _, _ = aim_teukolsky_full(wr + 1j * wi, l, 0.0, m, N=120)
        if met < min_met:
            min_met, best = met, (wr, wi)
print(f"  Coarse min: omega = {best[0]:.5f} {best[1]:+.5f}i, metric = {min_met:.6e}")

min_met2, best2 = np.inf, best
for wr in np.linspace(max(best[0] - 0.05, 0.2), min(best[0] + 0.05, 0.5), 25):
    for wi in np.linspace(best[1] - 0.03, best[1] + 0.03, 20):
        met, _, _, _ = aim_teukolsky_full(wr + 1j * wi, l, 0.0, m, N=120)
        if met < min_met2:
            min_met2, best2 = met, (wr, wi)
print(f"  Fine min: omega = {best2[0]:.5f} {best2[1]:+.5f}i, metric = {min_met2:.6e}")

# ---- Test C: AIM convergence at true vs false eigenvalue ----
print(f"\n--- Test C: AIM convergence history ---")
for label, omega_test in [("True (Berti grav)", omega_ref),
                           ("False (scan min)", 0.28 - 0.17j)]:
    met, lsa, lsb, hist = aim_teukolsky_full(omega_test, l, 0.0, m, N=120)
    print(f"\n  {label}: {omega_test}")
    print(f"    Final: lsa={lsa:.6f}, lsb={lsb:.6f}, metric={met:.6e}")
    for N_check in [10, 20, 40, 60, 80, 100, 120]:
        k, ma, mb = hist[N_check - 1]
        print(f"    N={N_check:3d}: |lsa|={ma:.4e}, |lsb|={mb:.4e}")
