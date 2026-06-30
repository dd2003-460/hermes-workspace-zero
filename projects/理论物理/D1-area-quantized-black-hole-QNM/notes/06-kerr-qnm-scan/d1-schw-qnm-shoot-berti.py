#!/usr/bin/env python3
"""
Shooting method: solve d^2psi/dr*^2 + (omega^2 - V) psi = 0 directly.
Test whether Cardoso values are the true eigenvalues of the c=6 RW equation.

This is a simpler, more reliable verification than AIM.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar, minimize

M = 1.0

# Cardoso (2000) values for gravitational QNMs (c=6)
CARDOSO = {
    (2, 0): complex(0.48982, -0.04314),
    (3, 0): complex(0.68294, -0.04298),
}

BERTI = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


def r_from_rstar(rs):
    """Numerically invert r* = r + 2M ln(r/2M - 1) + M ln(r/2M - 1) + r ln(...) - r*"""
    # Standard tortoise coordinate
    # r* = r + 2M ln(r/2M - 1) + M * [terms for higher precision]
    # Actually: r* = r + 2M ln(r/(2M) - 1) + 2M for Schwarzschild
    # But let me use the more precise definition

    def f(r_val):
        if r_val <= 2 * M:
            return -1e10
        return r_val + 2 * M * np.log(r_val / (2 * M) - 1) + M * 0.0

    # Initial guess
    r_guess = rs
    for _ in range(20):
        f_val = f(r_guess) - rs
        df = 1 + 2 * M / (r_guess - 2 * M)
        if abs(df) < 1e-15:
            break
        r_guess -= f_val / df
    return max(r_guess, 2.0 * M + 1e-10)


def regge_wheeler_system(rs, y, omega, l, c_coeff):
    """
    First-order system: dy1/dr* = y2, dy2/dr* = -(omega^2 - V) y1
    y1 = psi, y2 = dpsi/dr*
    """
    r = r_from_rstar(rs)
    if r <= 2 * M:
        return [0, 0]

    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - c_coeff * M / r**3)
    dpsi_drstar = y[1]
    d2psi_drstar2 = -(omega**2 - V) * y[0]
    return [dpsi_drstar, d2psi_drstar2]


def compute_wronskian(omega, l, c_coeff, rs_h=-60, rs_inf=80, rs_m=0):
    """
    Compute the Wronskian at rs_m by integrating from both ends.

    From horizon (rs_h): ingoing BC -> psi = exp(-i omega r*)
    From infinity (rs_inf): outgoing BC -> psi = exp(i omega r*)

    Wronskian = psi_horiz'(rs_m) * psi_infn(rs_m) - psi_horiz(rs_m) * psi_infn'(rs_m)
    """
    # Horizon side: ingoing BC at rs_h
    # psi_h(rs_h) = exp(-i*omega*rs_h)
    # psi_h'(rs_h) = -i*omega * exp(-i*omega*rs_h)
    phase_h = np.exp(-1j * omega * rs_h)
    y0_h = [phase_h, -1j * omega * phase_h]

    sol_h = solve_ivp(lambda rs, y: regge_wheeler_system(rs, y, omega, l, c_coeff),
                      [rs_h, rs_m], y0_h, method='RK45', dense_output=True,
                      max_step=0.5, rtol=1e-10, atol=1e-12)

    # Infinity side: outgoing BC at rs_inf
    # psi_inf(rs_inf) = exp(i*omega*rs_inf)
    # psi_inf'(rs_inf) = i*omega * exp(i*omega*rs_inf)
    phase_inf = np.exp(1j * omega * rs_inf)
    y0_inf = [phase_inf, 1j * omega * phase_inf]

    sol_inf = solve_ivp(lambda rs, y: regge_wheeler_system(rs, y, omega, l, c_coeff),
                        [rs_inf, rs_m], y0_inf, method='RK45', dense_output=True,
                        max_step=0.5, rtol=1e-10, atol=1e-12)

    if sol_h.status != 0 or sol_inf.status != 0:
        return None, None, None

    psi_h = sol_h.sol(rs_m)[0]
    dpsi_h = sol_h.sol(rs_m)[1]
    psi_inf = sol_inf.sol(rs_m)[0]
    dpsi_inf = sol_inf.sol(rs_m)[1]

    W = dpsi_h * psi_inf - psi_h * dpsi_inf
    norm = max(abs(psi_h * psi_inf), abs(dpsi_h * dpsi_inf), 1.0)

    return W, W / norm, (psi_h, dpsi_h, psi_inf, dpsi_inf)


def find_min_wronskian(l, c_coeff, omega_ref, delta_re=0.5, delta_im=0.1):
    """Find omega that minimizes |W/norm| near omega_ref."""

    def objective(x):
        omega = complex(x[0], x[1])
        W, Wn, _ = compute_wronskian(omega, l, c_coeff)
        if Wn is None:
            return 1e10
        return abs(Wn)

    result = minimize(objective, [omega_ref.real, omega_ref.imag],
                      method='Nelder-Mead',
                      options={'xatol': 1e-12, 'fatol': 1e-16,
                               'maxiter': 10000, 'adaptive': True})

    omega_found = complex(result.x[0], result.x[1])
    return omega_found, result.fun


# ===================================================================
# Main
# ===================================================================

print("=" * 70)
print("Shooting Method Verification")
print("=" * 70)

# Test at Berti values
for l in [2, 3]:
    for c_coeff in [2, 6]:
        for label, omega_ref in [("Berti", BERTI[l]), ("Cardoso", CARDOSO.get((l, 0), None))]:
            if omega_ref is None:
                continue
            W, Wn, vals = compute_wronskian(omega_ref, l, c_coeff)
            if W is None:
                print(f"  l={l}, c={c_coeff}, {label} ({omega_ref}): FAILED")
                continue
            print(f"\n  l={l}, c={c_coeff}, {label}: omega = {omega_ref.real:.5f} + {omega_ref.imag:.5f}i")
            print(f"    |W| = {abs(W):.6e}, |W|/norm = {abs(Wn):.6e}")
            if vals:
                phi_h, dphi_h, phi_inf, dphi_inf = vals
                print(f"    |psi_h(rs_m)| = {abs(phi_h):.6e}, |psi_inf(rs_m)| = {abs(phi_inf):.6e}")

# Fine scan around Cardoso for c=6, l=2
print("\n" + "=" * 70)
print("Fine scan: minimize |W/norm| for c=6, l=2")
print("=" * 70)

cardoso_20 = CARDOSO[(2, 0)]
grid_search_result = {}
for dr in np.arange(-0.2, 0.3, 0.05):
    for di in np.arange(-0.03, 0.03, 0.005):
        omega = cardoso_20 + complex(dr, di)
        W, Wn, _ = compute_wronskian(omega, 2, 6)
        if Wn is not None:
            key = f"{omega.real:.2f}{omega.imag:.3f}"
            grid_search_result[key] = (abs(Wn), omega)

sorted_results = sorted(grid_search_result.items(), key=lambda x: x[1][0])[:10]
print("\n  Top 10 minima:")
for key, (Wn_abs, w) in sorted_results:
    print(f"    {w.real:.5f} + {w.imag:.5f}i : |W|/norm = {Wn_abs:.6e}")

# Refine the best minimum
best_key = sorted_results[0][0]
omega_best = sorted_results[0][1][1]
omega_f, min_Wn = find_min_wronskian(2, 6, omega_best)
print(f"\n  Refined minimum: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
print(f"                   |W|/norm = {min_Wn:.6e}")
print(f"  Cardoso ref:     omega = {cardoso_20.real:.5f} + {cardoso_20.imag:.5f}i")
print(f"  Berti ref:       omega = {BERTI[2].real:.5f} + {BERTI[2].imag:.5f}i")

# Repeat for c=6, l=3
print("\n" + "=" * 70)
print("Fine scan: minimize |W/norm| for c=6, l=3")
print("=" * 70)

cardoso_30 = CARDOSO[(3, 0)]
for dr in np.arange(-0.2, 0.3, 0.05):
    for di in np.arange(-0.03, 0.03, 0.005):
        omega = cardoso_30 + complex(dr, di)
        W, Wn, _ = compute_wronskian(omega, 3, 6)
        if Wn is not None:
            key = f"{omega.real:.2f}{omega.imag:.3f}"
            grid_search_result[key] = (abs(Wn), omega)

sorted_results = sorted(grid_search_result.items(), key=lambda x: x[1][0])[:10]
print("\n  Top 10 minima:")
for key, (Wn_abs, w) in sorted_results:
    print(f"    {w.real:.5f} + {w.imag:.5f}i : |W|/norm = {Wn_abs:.6e}")

omega_best = sorted_results[0][1][1]
omega_f, min_Wn = find_min_wronskian(3, 6, omega_best)
print(f"\n  Refined minimum: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
print(f"                   |W|/norm = {min_Wn:.6e}")
print(f"  Cardoso ref:     omega = {cardoso_30.real:.5f} + {cardoso_30.imag:.5f}i")
print(f"  Berti ref:       omega = {BERTI[3].real:.5f} + {BERTI[3].imag:.5f}i")

# Also test c=2, l=2
print("\n" + "=" * 70)
print("Fine scan: minimize |W/norm| for c=2, l=2")
print("=" * 70)

for dr in np.arange(-0.2, 0.3, 0.05):
    for di in np.arange(-0.03, 0.03, 0.005):
        omega = BERTI[2] + complex(dr, di)
        W, Wn, _ = compute_wronskian(omega, 2, 2)
        if Wn is not None:
            key = f"{omega.real:.2f}{omega.imag:.3f}"
            grid_search_result[key] = (abs(Wn), omega)

sorted_results = sorted(grid_search_result.items(), key=lambda x: x[1][0])[:10]
print("\n  Top 10 minima:")
for key, (Wn_abs, w) in sorted_results:
    print(f"    {w.real:.5f} + {w.imag:.5f}i : |W|/norm = {Wn_abs:.6e}")

omega_best = sorted_results[0][1][1]
omega_f, min_Wn = find_min_wronskian(2, 2, omega_best)
print(f"\n  Refined minimum: omega = {omega_f.real:.6f} + {omega_f.imag:.6f}i")
print(f"                   |W|/norm = {min_Wn:.6e}")
print(f"  Berti ref:       omega = {BERTI[2].real:.5f} + {BERTI[2].imag:.5f}i")

print("\n=== Done ===")
