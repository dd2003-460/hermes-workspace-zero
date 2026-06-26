#!/usr/bin/env python3
"""Test Teukolsky AIM with no gauge transform — just the raw ODE coefficients."""

import numpy as np
from scipy.optimize import minimize

M = 1.0

# ---- Teukolsky ODE in x = 1 - r_+/r ----

def teuk_raw_coeffs(x, omega, l=2, m=2, a=0.0, s=-2):
    """Teukolsky ODE coefficients without any gauge: R''_x = lambda_0 * R'_x + mu_0 * R"""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r_plus = M + np.sqrt(M**2 - a**2)
    r_minus = M - np.sqrt(M**2 - a**2)
    delta_r = r_plus - r_minus

    r = r_plus / (1 - x)
    dr_dx = r_plus / (1 - x)**2
    d2r_dx2 = 2 * r_plus / (1 - x)**3

    Delta = (r - r_plus) * (r - r_minus)
    dDelta_dr = 2 * r - 2 * M
    K = (r**2 + a**2) * omega - a * m

    # Spheroidal eigenvalue (for a=0: A = l(l+1))
    A_lms = l * (l + 1)

    # Teukolsky equation: R'' + P_r*R' + Q_r*R = 0
    P_r = (s + 1) * dDelta_dr / Delta
    U = K**2 / Delta - 4 * s * omega * r / Delta + A_lms
    Q_r = U / Delta

    # Coordinate transform: d^2R/dx^2 = d2r_dx2*dR/dr + dr_dx^2*d^2R/dr^2
    # Substituting d^2R/dr^2 = -P_r*R' - Q_r*R:
    # d^2R/dx^2 = (d2r_dx2/dr_dx - dr_dx*P_r)*dR/dx - dr_dx^2*Q_r*R
    # So lambda_raw = d2r_dx2/dr_dx - dr_dx*P_r
    #    mu_raw     = -dr_dx^2*Q_r

    A_coeff = d2r_dx2 / dr_dx - dr_dx * P_r
    B_coeff = -dr_dx**2 * Q_r

    # For AIM form y'' = lambda_0*y' + mu_0*y:
    lambda_0 = A_coeff
    mu_0 = B_coeff

    return lambda_0, mu_0

# ---- RW raw coefficients (from working code) ----

def rw_raw_coeffs(x, omega, l=2):
    """RW ODE coefficients from the verified working code."""
    r = 2 * M / (1 - x)
    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a_base = -dlnP
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b_base = P**2 * (omega**2 - V)
    # ODE: psi'' + a_base*psi' + b_base*psi = 0
    # AIM form: psi'' = -a_base*psi' - b_base*psi
    return -a_base, -b_base

# ---- AIM solver ----

def aim_run(coeffs_func, omega, N=8, xa=0.35, xb=0.65):
    TARGET = 1e50
    dx = 1e-6

    la_a, ma_a = coeffs_func(xa, omega)
    la_b, ma_b = coeffs_func(xb, omega)

    dla_a = (coeffs_func(xa+dx, omega)[0] - coeffs_func(xa-dx, omega)[0]) / (2*dx)
    dmu_a = (coeffs_func(xa+dx, omega)[1] - coeffs_func(xa-dx, omega)[1]) / (2*dx)
    dla_b = (coeffs_func(xb+dx, omega)[0] - coeffs_func(xb-dx, omega)[0]) / (2*dx)
    dmu_b = (coeffs_func(xb+dx, omega)[1] - coeffs_func(xb-dx, omega)[1]) / (2*dx)

    for k in range(N):
        la_prev_a, la_prev_b = la_a, la_b
        ln_a = la_a**2 + dla_a - ma_a
        mn_a = la_a*dmu_a - ma_a*dla_a + ma_a**2
        dla_na = 2*la_a*dla_a - dmu_a
        dmu_na = 2*ma_a*dmu_a

        ln_b = la_b**2 + dla_b - ma_b
        mn_b = la_b*dmu_b - ma_b*dla_b + ma_b**2
        dla_nb = 2*la_b*dla_b - dmu_b
        dmu_nb = 2*ma_b*dmu_b

        max_val = max(abs(ln_a), abs(ln_b), abs(mn_a), abs(mn_b),
                      abs(dla_na), abs(dmu_na), abs(dla_nb), abs(dmu_nb))
        scale = max_val / TARGET if max_val > TARGET else 1.0

        la_prev_a /= scale; la_prev_b /= scale
        la_a, ma_a, dla_a, dmu_a = ln_a/scale, mn_a/scale, dla_na/scale, dmu_na/scale
        la_b, ma_b, dla_b, dmu_b = ln_b/scale, mn_b/scale, dla_nb/scale, dmu_nb/scale

    theta_a = la_prev_a / la_a
    theta_b = la_prev_b / la_b
    D = abs(theta_a - theta_b)
    return D, theta_a, theta_b

# ---- Tests ----

print("=" * 70)
print("Comparing raw (no-gauge) AIM for RW vs Teukolsky at a=0")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j

# First compare coefficients at a=0
print("\n--- Coefficient comparison at a=0 ---")
for x in [0.35, 0.5, 0.65]:
    rw_l, rw_m = rw_raw_coeffs(x, omega_ref, l=2)
    tk_l, tk_m = teuk_raw_coeffs(x, omega_ref, l=2, m=2, a=0.0, s=-2)
    print(f"\n  x={x:.2f}:")
    print(f"    RW:      lambda_0={rw_l:.6e}, mu_0={rw_m:.6e}")
    print(f"    Teuk:    lambda_0={tk_l:.6e}, mu_0={tk_m:.6e}")
    print(f"    diff:    |dlam|={abs(tk_l-rw_l):.6e}, |dmu|={abs(tk_m-rw_m):.6e}")

# Test RW AIM (should converge)
print("\n--- RW raw AIM at QNM (l=2) ---")
rw_fn = lambda x, w: rw_raw_coeffs(x, w, l=2)
for N in [4, 5, 6, 7]:
    D, ta, tb = aim_run(rw_fn, omega_ref, N=N)
    print(f"  N={N}: D={D:.6e}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}")

# Test Teukolsky AIM at a=0 (should also converge if coefficients correct)
print("\n--- Teukolsky raw AIM at a=0, l=2, m=2 ---")
tk_fn = lambda x, w: teuk_raw_coeffs(x, w, l=2, m=2, a=0.0, s=-2)
for N in [4, 5, 6, 7]:
    D, ta, tb = aim_run(tk_fn, omega_ref, N=N)
    print(f"  N={N}: D={D:.6e}, |ta|={abs(ta):.4e}, |tb|={abs(tb):.4e}")

# Fine scan for Teukolsky (if the function has a minimum somewhere)
print("\n--- Teukolsky AIM score scan (N=6) ---")
for wr in np.linspace(0.2, 0.6, 9):
    row = ""
    for wi in np.linspace(-0.15, -0.02, 7):
        D, _, _ = aim_run(tk_fn, wr+1j*wi, N=6)
        if D < 1e-10:
            row += " # "
        elif D < 1:
            row += " * "
        elif D < 100:
            row += ". "
        else:
            row += ": "
        # Pad to 10 chars
        d_str = f"{D:.1e}"
    print(f"  wr={wr:.2f}: {row}")
    # Print actual values
    vals = []
    for wi in np.linspace(-0.15, -0.02, 7):
        D, _, _ = aim_run(tk_fn, wr+1j*wi, N=6)
        vals.append(f"{D:.2e}")
    print(f"         {'  '.join(vals)}")

# Fine scan for RW (should show minimum near QNM)
print("\n--- RW AIM score scan (N=6) ---")
for wr in np.linspace(0.25, 0.5, 11):
    vals = []
    for wi in np.linspace(-0.15, -0.02, 7):
        D, _, _ = aim_run(rw_fn, wr+1j*wi, N=6)
        vals.append(f"{D:.2e}")
    print(f"  wr={wr:.2f}: {'  '.join(vals)}")
