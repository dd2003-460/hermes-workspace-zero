#!/usr/bin/env python3
"""
Fast shooting method for Schwarzschild QNMs using fixed-step RK4.
Determines true eigenvalues for c=2 and c=6 Regge-Wheeler potentials.
Faster than solve_ivp because it uses vectorized operations.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

def r_from_rstar(rs):
    """Invert r* = r + 2M ln(r/2M - 1) using Newton's method."""
    r = max(rs * 0.5 + M, 2.5)  # better initial guess
    for _ in range(30):
        f = r + 2*M*np.log(r/(2*M) - 1) - rs
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15:
            break
        r = r - f/df
        if r <= 2.0*M:
            r = 2.0*M + 1e-10
        if abs(f) < 1e-14:
            break
    return max(r, 2.0001)


def rw_potential(r, l, c_coeff):
    """Regge-Wheeler potential."""
    return (1 - 2*M/r) * (l*(l+1)/r**2 - c_coeff*M/r**3)


def integrate_bc(bc_type, rs_target, omega, l, c_coeff):
    """
    Integrate from boundary to rs_target.
    bc_type = 'ingoing' (from horizon) or 'outgoing' (from infinity)

    System: dy/dr* = A(y), where y = [psi, dpsi/dr*]
    """
    if bc_type == 'ingoing':
        rs_start = -50.0
        N = 5000
        drs = (rs_target - rs_start) / N
        # Ingoing BC at horizon: psi ~ exp(-i*omega*r*)
        psi = np.exp(-1j * omega * rs_start)
        dpsi = -1j * omega * psi
    else:  # outgoing
        rs_start = 70.0
        N = 5000
        drs = (rs_target - rs_start) / N
        # Outgoing BC at infinity: psi ~ exp(i*omega*r*)
        psi = np.exp(1j * omega * rs_start)
        dpsi = 1j * omega * psi

    for _ in range(N):
        r = r_from_rstar(rs_start)
        V = rw_potential(r, l, c_coeff)
        # RK4
        k1_y = dpsi
        k1_d = -(omega**2 - V) * psi

        r = r_from_rstar(rs_start + drs/2)
        V = rw_potential(r, l, c_coeff)
        k2_y = dpsi + 0.5*drs*k1_d
        k2_d = -(omega**2 - V) * (psi + 0.5*drs*k1_y)

        r = r_from_rstar(rs_start + drs/2)
        V = rw_potential(r, l, c_coeff)
        k3_y = dpsi + 0.5*drs*k2_d
        k3_d = -(omega**2 - V) * (psi + 0.5*drs*k2_y)

        r = r_from_rstar(rs_start + drs)
        V = rw_potential(r, l, c_coeff)
        k4_y = dpsi + drs*k3_d
        k4_d = -(omega**2 - V) * (psi + drs*k3_y)

        psi += (drs/6) * (k1_y + 2*k2_y + 2*k3_y + k4_y)
        dpsi += (drs/6) * (k1_d + 2*k2_d + 2*k3_d + k4_d)

        # Keep values bounded
        if abs(psi) > 1e28:
            psi /= abs(psi) * 1e-27
            dpsi /= abs(psi) * 1e-27

    return psi, dpsi


def wronskian_norm(omega, l, c_coeff):
    """Compute normalized Wronskian at rs=0."""
    phi_h, dphi_h = integrate_bc('ingoing', 0.0, omega, l, c_coeff)
    phi_inf, dphi_inf = integrate_bc('outgoing', 0.0, omega, l, c_coeff)
    W = dphi_h * phi_inf - phi_h * dphi_inf
    norm = max(abs(phi_h), abs(dphi_h), abs(phi_inf), abs(dphi_inf), 1.0)
    return abs(W) / norm


def log_omega(omega, l, c_coeff):
    """
    Better objective: use log-derivative matching.
    We integrate both sides and compute |dln/drs| difference.
    """
    rs_m = 10.0
    phi_h, dphi_h = integrate_bc('ingoing', rs_m, omega, l, c_coeff)
    phi_inf, dphi_inf = integrate_bc('outgoing', rs_m, omega, l, c_coeff)

    if abs(phi_h) < 1e-100 or abs(phi_inf) < 1e-100:
        return 1e100

    # The Wronskian approach
    W = dphi_h * phi_inf - phi_h * dphi_inf
    # Normalize by typical values at rs_m
    norm = abs(phi_h) + abs(phi_inf) + abs(dphi_h) + abs(dphi_inf) + 1e-100
    return abs(W) / norm


# Quick test: compute several W values in parallel using vectorization
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}
CARDOSO = {(2, 0): complex(0.48982, -0.04314), (3, 0): complex(0.68294, -0.04298)}

print("=" * 70)
print("Fast Shooting Method for Schwarzschild QNMs")
print("=" * 70)

# Test at reference points
print("\nWronskian at reference points:")
for l in [2, 3]:
    for c_coeff in [2, 6]:
        ref = BERTI[l]
        wn = wronskian_norm(ref, l, c_coeff)
        cardo = CARDOSO.get((l, 0))
        wn_cardo = None
        if cardo:
            wn_cardo = wronskian_norm(cardo, l, c_coeff)
        print(f"  l={l}, c={c_coeff}:")
        print(f"    Berti  ({ref.real:.5f} + {ref.imag:.5f}i): |W|/norm = {wn:.6e}")
        if wn_cardo:
            print(f"    CARDOSO({cardo.real:.5f} + {cardo.imag:.5f}i): |W|/norm = {wn_cardo:.6e}")

# Grid scan for c=6, l=2
print("\nGrid scan c=6, l=2:")
best_26_w, best_26_v = None, 1e100
for r in np.arange(0.2, 0.9, 0.05):
    for i in np.arange(-0.12, 0.0, 0.01):
        w = complex(r, i)
        v = wronskian_norm(w, 2, 6)
        if v < best_26_v:
            best_26_v = v
            best_26_w = w
print(f"  Best: {best_26_w.real:.4f} + {best_26_w.imag:.4f}i : {best_26_v:.6e}")
print(f"  Berti:     0.37367 - 0.08896i")
print(f"  CARDOSO:   0.48982 - 0.04314i")

# Refine
obj = lambda x: wronskian_norm(complex(x[0], x[1]), 2, 6)
r = minimize(obj, [best_26_w.real, best_26_w.imag],
             method='Nelder-Mead', options={'xatol': 1e-14, 'fatol': 1e-18, 'maxiter': 20000, 'adaptive': True})
omega_26 = complex(r.x[0], r.x[1])
print(f"  Refined c=6, l=2: {omega_26.real:.6f} + {omega_26.imag:.6f}i (|W|/norm={r.fun:.3e})")

# Grid scan for c=6, l=3
print("\nGrid scan c=6, l=3:")
best_36_w, best_36_v = None, 1e100
for r in np.arange(0.4, 1.2, 0.05):
    for i in np.arange(-0.12, 0.0, 0.01):
        w = complex(r, i)
        v = wronskian_norm(w, 3, 6)
        if v < best_36_v:
            best_36_v = v
            best_36_w = w
print(f"  Best: {best_36_w.real:.4f} + {best_36_w.imag:.4f}i : {best_36_v:.6e}")
print(f"  Berti: 0.59108 - 0.05902i")
print(f"  CARDOSO: 0.68294 - 0.04298i")

r = minimize(obj := lambda x: wronskian_norm(complex(x[0], x[1]), 3, 6),
             [best_36_w.real, best_36_w.imag],
             method='Nelder-Mead', options={'xatol': 1e-14, 'fatol': 1e-18, 'maxiter': 20000, 'adaptive': True})
omega_36 = complex(r.x[0], r.x[1])
print(f"  Refined c=6, l=3: {omega_36.real:.6f} + {omega_36.imag:.6f}i (|W|/norm={r.fun:.3e})")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"\n  c=6, l=2 QNM = {omega_26.real:.6f} + {omega_26.imag:.6f}i")
print(f"  Berti:  0.37367 - 0.08896i")
print(f"  CARDOSO: 0.48982 - 0.04314i")
print(f"\n  c=6, l=3 QNM = {omega_36.real:.6f} + {omega_36.imag:.6f}i")
print(f"  Berti:  0.59108 - 0.05902i")
print(f"  CARDOSO: 0.68294 - 0.04298i")
print("\n=== Done ===")
