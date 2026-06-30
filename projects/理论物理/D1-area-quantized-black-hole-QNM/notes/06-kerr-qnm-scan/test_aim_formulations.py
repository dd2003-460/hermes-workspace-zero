#!/usr/bin/env python3
"""
Systematic diagnostic: test multiple AIM formulations & gauge choices
to find which converges to Berti/Cardoso values.

Reference values:
  Berti et al. (2006):
    l=2, n=0:  0.37367 - 0.08896 i  (c=6 gravitational)
    l=3, n=0:  0.59108 - 0.05902 i
  Cardoso (2000):
    l=2, c=6: 0.48982 - 0.04314 i  ??

Tests:
  1. Different V coefficients: c=6, c=2
  2. Different gauges: raw, dehghan_v1 (my version), dehghan_v2 (Dehghan-Safari)
  3. Different convergence criteria: C (directional), D (absolute)
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

# Standard AIM iteration step
def aim_step(la, ma, dla, dmu):
    ln = la**2 + dla - ma
    mn = la * dmu - ma * dla + ma**2
    dla_n = 2 * la * dla - dmu
    dmu_n = 2 * ma * dmu
    return ln, mn, dla_n, dmu_n

def get_coeffs_choice(x, omega, l, c_coeff, gauge):
    """
    Generic coefficient getter supporting multiple formulations.

    Based on the approach from Chanchal Mandal / Cho et al.

    Metric:
      x = 1 - 2M/r
      P = 2/(x(1-x)^2)
      a_base = (1-3x)/(x(1-x))
      b_base = P^2 * (omega^2 - V)
      V = (1 - 2M/r) * (l(l+1)/r^2 - c*M/r^3)

    Gauge transform y -> y·exp(χ):
      new a = old a + 2*chi'
      new b = old b + old_a*chi' + 2*(chi')^2 + chi''
      Returns (-new_a, -new_b) as (lambda_0, mu_0)
    """
    x = np.clip(x, 1e-14, 1-1e-14)
    r = 2.0 * M / (1.0 - x)

    P = 2.0 / (x * (1.0 - x)**2)
    a_base = (1.0 - 3.0 * x) / (x * (x - 1.0))
    V = (1.0 - 2.0 * M / r) * (l*(l+1) / r**2 - c_coeff * M / r**3)
    b_base = P**2 * (omega**2 - V)

    if gauge == "raw":
        return -a_base, -b_base

    elif gauge == "dehghan_v1":
        # My gauge: g = F^{iω}·x^{-iω}·(1-x)^{iω},  F = 1/(1-x)^2
        # ln(g) = -iω·[ln(x) + ln(1-x)]
        chi = 1j * omega * (1.0/(1.0 - x) - 1.0/x)  # chi' numerically
        # We need chi' and chi'' analytically
        # ln(g) = -iω·ln(x) - iω·ln(1-x) + iω·ln(F)
        # F = 1/(1-x)^2, ln(F) = -2·ln(1-x)
        # ln(g) = -iω·ln(x) - 3iω·ln(1-x) -- WRONG (coeff 3)
        # Actually: F^{iω} x^{-iω} (1-x)^{iω}
        # = (1-x)^{-2iω} · x^{-iω} · (1-x)^{iω}
        # = (1-x)^{-iω} · x^{-iω}
        # ln(g) = -iω·ln(x) - iω·ln(1-x)
        dln_g = -1j * omega * (1.0/x + 1.0/(1.0 - x))
        d2ln_g = 1j * omega * (1.0/x**2 + 1.0/(1.0 - x)**2)

        new_a = a_base + 2 * dln_g
        new_b = b_base + a_base * dln_g + 2 * dln_g**2 + d2ln_g
        return -new_a, -new_b

    elif gauge == "dehghan_v2":
        # Dehghan-Safari 2011: G = F^{iω} · x^{-iω} · (1-x)^{iω} · exp(-iω/(1-x))
        F_over_F = 2 * (2 * x - 1) / (x * (1 - x))
        alpha = -1j * omega
        beta = 1j * omega
        gamma_v = -1j * omega
        chi_prime = alpha * (F_over_F + 1/x) - beta/(1-x) + gamma_v/(1-x)**2
        dx_n = 1e-7
        xp = min(x + dx_n, 0.99999)
        xm = max(x - dx_n, 1e-8)
        Fp = 2*(2*xp-1)/(xp*(1-xp))
        gp = alpha*(Fp + 1/xp) - beta/(1-xp) + gamma_v/(1-xp)**2
        Fm = 2*(2*xm-1)/(xm*(1-xm))
        gm = alpha*(Fm + 1/xm) - beta/(1-xm) + gamma_v/(1-xm)**2
        chi_double_prime = (gp - gm) / (2*dx_n)

        new_a = a_base + 2*chi_prime
        new_b = b_base + a_base*chi_prime + 2*chi_prime**2 + chi_double_prime
        return -new_a, -new_b

    elif gauge == "cho":
        # Cho et al. six-factor ansatz
        kappa = 2j * omega
        beta_a = 2j * omega
        gamma_a = -2j * omega
        chi_prime = kappa/x - beta_a/(1-x) + gamma_a/(1-x)**2
        chi_double_prime = -kappa/x**2 + beta_a/(1-x)**2 - 2*gamma_a/(1-x)**3
        new_a = a_base + 2*chi_prime
        new_b = b_base + a_base*chi_prime + 2*chi_prime**2 + chi_double_prime
        return -new_a, -new_b

    raise ValueError(f"Unknown gauge: {gauge}")

def aim_run(xa, xb, omega, l, c_coeff, gauge, N=10):
    """Run AIM for N iterations with per-step global scaling."""
    TARGET = 1e50
    dx_num = 1e-7

    la_a, ma_a = get_coeffs_choice(xa, omega, l, c_coeff, gauge)
    la_b, ma_b = get_coeffs_choice(xb, omega, l, c_coeff, gauge)
    dla_a = (get_coeffs_choice(xa+dx_num, omega, l, c_coeff, gauge)[0] -
             get_coeffs_choice(xa-dx_num, omega, l, c_coeff, gauge)[0]) / (2*dx_num)
    dmu_a = (get_coeffs_choice(xa+dx_num, omega, l, c_coeff, gauge)[1] -
             get_coeffs_choice(xa-dx_num, omega, l, c_coeff, gauge)[1]) / (2*dx_num)
    dla_b = (get_coeffs_choice(xb+dx_num, omega, l, c_coeff, gauge)[0] -
             get_coeffs_choice(xb-dx_num, omega, l, c_coeff, gauge)[0]) / (2*dx_num)
    dmu_b = (get_coeffs_choice(xb+dx_num, omega, l, c_coeff, gauge)[1] -
             get_coeffs_choice(xb-dx_num, omega, l, c_coeff, gauge)[1]) / (2*dx_num)

    la_prev_a, la_prev_b = la_a, la_b

    for k in range(N):
        la_prev_a, la_prev_b = la_a, la_b
        ln_a, mn_a, dla_na, dmu_na = aim_step(la_a, ma_a, dla_a, dmu_a)
        ln_b, mn_b, dla_nb, dmu_nb = aim_step(la_b, ma_b, dla_b, dmu_b)

        max_val = max(abs(ln_a), abs(ln_b), abs(mn_a), abs(mn_b),
                      abs(dla_na), abs(dmu_na), abs(dla_nb), abs(dmu_nb))
        scale = max_val / TARGET if max_val > TARGET else 1.0

        la_a, ma_a, dla_a, dmu_a = ln_a/scale, mn_a/scale, dla_na/scale, dmu_na/scale
        la_b, ma_b, dla_b, dmu_b = ln_b/scale, mn_b/scale, dla_nb/scale, dmu_nb/scale

    theta_a = la_prev_a / la_a if abs(la_a) > 1e-200 else 0
    theta_b = la_prev_b / la_b if abs(la_b) > 1e-200 else 0

    # Both criteria
    D_abs = abs(theta_a - theta_b)
    C_dir = abs(theta_a/abs(theta_a) - theta_b/abs(theta_b)) if abs(theta_a)>1e-100 and abs(theta_b)>1e-100 else 1e100

    return D_abs, C_dir, theta_a, theta_b

def test_at_omega(omega, l, c_coeff, gauge, N=10):
    D, C, ta, tb = aim_run(0.35, 0.65, omega, l, c_coeff, gauge, N=N)
    return D, C

# =====================================================================
# Phase 1: C = 6 (gravitational) with different gauges at Berti
# =====================================================================
print("=" * 80)
print("Phase 1: C=6 gauges at Berti values")
print("=" * 80)

berti_l2 = 0.37367 - 0.08896j
cardoso_l2 = complex(0.48982, -0.04314)
cardoso_l3 = complex(0.68294, -0.04298)
berti_l3 = 0.59108 - 0.05902j

for gauge in ["raw", "dehghan_v1", "dehghan_v2", "cho"]:
    D, C = test_at_omega(berti_l2, 2, 6, gauge, N=8)
    print(f"  gauge={gauge:12s}: C=6, l=2, Berti:  D={D:.4e}, C={C:.4e}")

# =====================================================================
# Phase 2: C = 2 (scalar) with different gauges at Berti
# =====================================================================
print("\nPhase 2: C=2 (scalar) gauges at Berti values")
print("=" * 80)

for gauge in ["raw", "dehghan_v1", "dehghan_v2", "cho"]:
    D, C = test_at_omega(berti_l2, 2, 2, gauge, N=8)
    print(f"  gauge={gauge:12s}: C=2, l=2, Berti:  D={D:.4e}, C={C:.4e}")

# =====================================================================
# Phase 3: GRID SCAN for CHO with c=6 (l=2)
# =====================================================================
print("\nPhase 3: GRID SCAN CHO c=6, l=2")
print("=" * 80)

best_C = 1e100
best_omega = None
best_D = 1e100

for wr in np.arange(0.15, 1.0, 0.025):
    for wi in np.arange(-0.12, -0.005, 0.005):
        w = complex(wr, wi)
        D, C = test_at_omega(w, 2, 6, "cho", N=8)
        if C < best_C and C < 1.0:
            best_C = C
            best_omega = w
            best_D = D

if best_omega:
    print(f"  Best C: {best_C:.6e} at omega = {best_omega.real:.4f} + {best_omega.imag:.4f}i")
    print(f"           D = {best_D:.6e}")
    print(f"  Berti ref:     0.37367 - 0.08896i")
    print(f"  Cardoso ref:   0.48982 - 0.04314i")
else:
    print("  No discriminative minimum found with C")

if best_D < 1.0:
    # Also report best D
    print(f"  Best D: {best_D:.6e} at same point")
else:
    # Find best D separately
    best_D = 1e100
    best_wD = None
    for wr in np.arange(0.15, 1.0, 0.025):
        for wi in np.arange(-0.12, -0.005, 0.005):
            w = complex(wr, wi)
            D, C = test_at_omega(w, 2, 6, "cho", N=8)
            if D < best_D:
                best_D = D
                best_wD = w
    if best_wD:
        print(f"  Best D: {best_D:.6e} at omega = {best_wD.real:.4f} + {best_wD.imag:.4f}i")

# =====================================================================
# Phase 4: GRID SCAN for CHO with c=6 (l=3)
# =====================================================================
print("\nPhase 4: GRID SCAN CHO c=6, l=3")
print("=" * 80)

best_C = 1e100
best_omega = None
best_D = 1e100

for wr in np.arange(0.3, 1.2, 0.025):
    for wi in np.arange(-0.12, -0.005, 0.005):
        w = complex(wr, wi)
        D, C = test_at_omega(w, 3, 6, "cho", N=8)
        if C < best_C and C < 1.0:
            best_C = C
            best_omega = w
            best_D = D

if best_omega:
    print(f"  Best C: {best_C:.6e} at omega = {best_omega.real:.4f} + {best_omega.imag:.4f}i")
    print(f"  Berti ref: 0.59108 - 0.05902i")
else:
    print("  No discriminative minimum found with C")

if best_D < 1.0:
    best_D = 1e100
    best_wD = None
    for wr in np.arange(0.3, 1.2, 0.025):
        for wi in np.arange(-0.12, -0.005, 0.005):
            w = complex(wr, wi)
            D, C = test_at_omega(w, 3, 6, "cho", N=8)
            if D < best_D:
                best_D = D
                best_wD = w
    if best_wD:
        print(f"  Best D: {best_D:.6e} at omega = {best_wD.real:.4f} + {best_wD.imag:.4f}i")

# =====================================================================
# Phase 5: Grid scan with c=2, l=2, CHO
# =====================================================================
print("\nPhase 5: GRID SCAN CHO c=2, l=2")
print("=" * 80)

best_C = 1e100
best_omega = None
best_D = 1e100

for wr in np.arange(0.1, 0.9, 0.025):
    for wi in np.arange(-0.12, -0.005, 0.005):
        w = complex(wr, wi)
        D, C = test_at_omega(w, 2, 2, "cho", N=8)
        if C < best_C and C < 1.0:
            best_C = C
            best_omega = w
            best_D = D

if best_omega:
    print(f"  Best C: {best_C:.6e} at omega = {best_omega.real:.4f} + {best_omega.imag:.4f}i")

# Also find best D
best_D = 1e100
best_wD = None
for wr in np.arange(0.1, 0.9, 0.025):
    for wi in np.arange(-0.12, -0.005, 0.005):
        w = complex(wr, wi)
        D, C = test_at_omega(w, 2, 2, "cho", N=8)
        if D < best_D:
            best_D = D
            best_wD = w
if best_wD:
    print(f"  Best D: {best_D:.6e} at omega = {best_wD.real:.4f} + {best_wD.imag:.4f}i")

print("\n=== Done ===")
