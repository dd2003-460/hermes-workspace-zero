#!/usr/bin/env python3
"""
Diagnostic: compare Teukolsky vs Dehghan-Safari coefficients at a=0.
Goal: find where the Teukolsky formulation deviates from the verified RW+AIM.
"""

import numpy as np

M = 1.0
omega = 0.37367 - 0.08896j  # expected l=2 QNM

# =====================================================================
# Dehghan-Safari coefficients (verified working)
# =====================================================================

def dehghan_coeffs(x, omega, l=2):
    r = 2*M/(1-x)

    # dr*/dx
    drstar_dr = r**2/(r-2*M)**2
    dr_dx = 2*M/(1-x)**2
    rstar_prime = drstar_dr * dr_dx

    # d2r*/dx2
    f_r = r**2/(r-2*M)**2
    g_x = 2*M/(1-x)**2
    df_dx = -4*M*r/(r-2*M)**3 * g_x
    dg_dx = 4*M/(1-x)**3
    rstar_double_prime = df_dx*g_x + f_r*dg_dx

    P = 1.0 / rstar_prime**2
    Q = -rstar_double_prime / rstar_prime**3
    Q_over_P = Q * rstar_prime**2  # = -rstar_double_prime/rstar_prime

    # RW potential
    f = 1.0 - 2*M/r
    V = f*(l*(l+1)/r**2 - 6*M/r**3)

    # Gauge: g = F^(iw) * x^(-iw) * (1-x)^(iw), F = r^2/(r-2M)^2
    F_val = r**2/(r-2*M)**2
    dF_dr = -4*M*r/(r-2*M)**3
    dF_dx = dF_dr * dr_dx
    ln_g_prime = 1j*omega*(dF_dx/F_val - 1.0/x + 1.0/(1-x))

    # (ln g)''
    dh_dr = (8*M*r - 8*M**2)/(r-2*M)**4
    dh_dx = dh_dr * dr_dx
    di_dx = 4*M/(1-x)**3
    d2F_dx2 = dh_dx * 2*M/(1-x)**2 + (-4*M*r/(r-2*M)**3) * di_dx
    F_prime_F = dF_dx / F_val
    dF_prime_F_dx = (d2F_dx2*F_val - dF_dx**2) / F_val**2
    ln_g_double_prime = 1j*omega*(dF_prime_F_dx + 1.0/x**2 + 1.0/(1-x)**2)

    # lambda_0 = 2*ln_g' + Q_over_P
    # mu_0 = ln_g'' + ln_g'^2 + Q_over_P*ln_g' + (w^2-V)*r*'^2
    lam_D = 2*ln_g_prime + Q_over_P
    mu_D = ln_g_double_prime + ln_g_prime**2 + Q_over_P*ln_g_prime + (omega**2 - V)*rstar_prime**2

    return lam_D, mu_D, rstar_prime, Q_over_P

# =====================================================================
# Teukolsky coefficients (under test)
# =====================================================================

def teuk_coeffs_from_v1(x, omega, l=2, m=2, a=0.0, s=-2):
    """Replicate the v1 computation exactly to diagnose."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r_plus = M + np.sqrt(M**2 - a**2)
    r_minus = M - np.sqrt(M**2 - a**2)
    delta_r = r_plus - r_minus

    r = r_plus / (1 - x)
    dr_dx = r_plus / (1 - x)**2
    Delta = (r - r_plus) * (r - r_minus)
    dDelta_dr = 2*r - 2*M
    K = (r**2 + a**2) * omega - a * m

    # Teukolsky equation
    U = K**2 / Delta - 4*s*omega*r / Delta + l*(l+1)
    P_r = (s + 1) * dDelta_dr / Delta
    Q_r = U / Delta

    # Coordinate transform
    d2r_dx2 = 2 * r_plus / (1 - x)**3

    # A_coeff = d2r_dx2/dr_dx - dr_dx*P_r
    # B_coeff = -dr_dx^2 * Q_r
    # ODE: R''_x = A_coeff * R'_x + B_coeff * R

    A_coeff = d2r_dx2 / dr_dx - dr_dx * P_r
    B_coeff = -dr_dx**2 * Q_r

    # Gauge: g = F^(iw) * x^(-iw) * (1-x)^(iw)
    # F = (r^2+a^2)/Delta
    r2_plus_a2 = r**2 + a**2
    dlnF_dr = (2*r*Delta - r2_plus_a2*dDelta_dr) / (Delta * r2_plus_a2)
    dlnF_dx = dlnF_dr * dr_dx
    ln_g_prime = 1j*omega * (dlnF_dx - 1.0/x + 1.0/(1-x))

    # (ln g)'' via finite difference
    dx_num = 1e-8
    def dlnF_at_xval(xv):
        rv = r_plus / (1 - xv)
        Dv = (rv - r_plus) * (rv - r_minus)
        dDv_dr = 2*rv - 2*M
        ddrv = r_plus / (1-xv)**2
        num = 2*rv*Dv - (rv**2+a**2)*dDv_dr
        return num / (Dv * (rv**2+a**2)) * ddrv

    dlnF_p = dlnF_at_xval(min(x + dx_num, 0.999999))
    dlnF_m = dlnF_at_xval(max(x - dx_num, 1e-10))
    d2lnF_dx2 = (dlnF_p - dlnF_m) / (2*dx_num)
    ln_g_double_prime = 1j*omega * (d2lnF_dx2 + 1.0/x**2 + 1.0/(1-x)**2)

    # lambda_0 = A_coeff - 2*ln_g_prime
    # mu_0 = A_coeff*ln_g_prime + B_coeff - ln_g_double_prime - ln_g_prime^2
    lam_T = A_coeff - 2*ln_g_prime
    mu_T = A_coeff*ln_g_prime + B_coeff - ln_g_double_prime - ln_g_prime**2

    return lam_T, mu_T, A_coeff, B_coeff, ln_g_prime, ln_g_double_prime

# =====================================================================
# Compare at a=0
# =====================================================================
print("=" * 70)
print("Coefficient comparison at a=0, l=2, omega =", omega)
print("=" * 70)

for x in [0.1, 0.3, 0.5, 0.7, 0.9]:
    lam_D, mu_D, rstar_p, QoP = dehghan_coeffs(x, omega)
    lam_T, mu_T, A_c, B_c, lg_p, lg_d = teuk_coeffs_from_v1(x, omega, l=2, m=2, a=0.0, s=-2)

    print(f"\n--- x = {x:.1f} ---")
    print(f"  Dehghan:  lambda_0 = {lam_D:.6e}, mu_0 = {mu_D:.6e}")
    print(f"  Teukolsky: lambda_0 = {lam_T:.6e}, mu_0 = {mu_T:.6e}")
    print(f"  lambda diff: |lam_D - lam_T| = {abs(lam_D - lam_T):.6e}")
    print(f"  mu diff: |mu_D - mu_T| = {abs(mu_D - mu_T):.6e}")
    print(f"  r*' = {rstar_p:.6e}")
    print(f"  Q_over_P (Dehghan) = {QoP:.6e}")
    print(f"  A_coeff (Teuk) = {A_c:.6e}")
    print(f"  B_coeff (Teuk) = {B_c:.6e}")
    print(f"  (ln g)' Dehghan-style = ", end="")
    # Compute what Dehghan's (ln g)' would be at this x
    r = 2*M/(1-x)
    F_val = r**2/(r-2*M)**2
    dF_dr = -4*M*r/(r-2*M)**3
    dr_dxF = 2*M/(1-x)**2
    dF_dx = dF_dr * dr_dxF
    lg_D = 1j*omega*(dF_dx/F_val - 1.0/x + 1.0/(1-x))
    print(f"{lg_D:.6e}")
    print(f"  (ln g)' Teuk = {lg_p:.6e}")
    print(f"  (ln g)' diff = {abs(lg_D - lg_p):.6e}")

# =====================================================================
# Analytical check: what should A_coeff be for Teukolsky at a=0?
# =====================================================================
print("\n" + "=" * 70)
print("Analytical check of coordinate transformation")
print("=" * 70)

# For Teukolsky at a=0:
#   Delta = r(r-2M), Delta' = 2r-2M
#   P_r = (s+1)*Delta'/Delta = -Delta'/Delta (for s=-2)
#   x = 1 - 2M/r, dr/dx = 2M/(1-x)^2, d2r/dx2 = 4M/(1-x)^3
#   A_coeff = d2r/dx2/dr/dx - dr/dx * P_r
#           = 2/(1-x) - dr/dx * (-Delta'/Delta)
#           = 2/(1-x) + dr/dx * Delta'/(r(r-2M))

# For RW (via tortoise):
#   psi''_x = (r*''/r*')*psi'_x - (w^2-V)*(r*')^2*psi
#   lam_raw = r*''/r*'
#   Dehghan: Q_over_P = -r*''/r*'

# Let's compute both at x=0.5
x = 0.5
r = 2*M/(1-x)  # = 4M
Delta = r*(r-2*M)
Delta_prime = 2*r - 2*M
dr_dx = 2*M/(1-x)**2
d2r_dx2 = 4*M/(1-x)**3

P_r = -Delta_prime / Delta  # s=-2: (s+1) = -1

A_coeff_manual = d2r_dx2/dr_dx + dr_dx * Delta_prime / Delta  # -P_r = Delta'/Delta for s=-2

# r*' for Schwarzschild
rstar_dr = r**2 / (r*(r-2*M))  # = r/(r-2M)
rstar_prime = rstar_dr * dr_dx  # dr*/dx
# d/dr* of r*/dx
d_rstar_dr_dr = (r-2*M - r)/(r-2*M)**2  # = -2M/(r-2M)^2
rstar_double_prime = d_rstar_dr_dr * dr_dx**2 + rstar_dr * d2r_dx2

print(f"\nAt x=0.5, r={r:.1f}:")
print(f"  dr/dx = {dr_dx:.4f}")
print(f"  d2r/dx2 = {d2r_dx2:.4f}")
print(f"  Delta = {Delta:.4f}, Delta' = {Delta_prime:.4f}")
print(f"  P_r (Teuk s=-2) = {P_r:.6f}")
print(f"  A_coeff (Teuk) = {A_coeff_manual:.6f}")
print(f"  r*' = {rstar_prime:.6f}")
print(f"  r*'' = {rstar_double_prime:.6f}")
print(f"  r*''/r*' = {rstar_double_prime/rstar_prime:.6f}")
print(f"  -r*''/r*' = {-rstar_double_prime/rstar_prime:.6f}")
print(f"  -P_x (Teuk) = -A_coeff = {-A_coeff_manual:.6f}")
print()
print(f"  If Teuk has gauge R = h*psi with h = Delta:")
print(f"    dh/dx = dDelta/dr * dr/dx = {Delta_prime * dr_dx:.6f}")
print(f"    h'/h = {(Delta_prime * dr_dx) / Delta:.6f}")
print(f"    2h'/h = {2*(Delta_prime*dr_dx)/Delta:.6f}")
print(f"    A_Teuk - 2h'/h = {A_coeff_manual - 2*(Delta_prime*dr_dx)/Delta:.6f}")
print(f"    (This should equal Dehghan's Q_over_P = -r*''/r*' if R = Delta*psi)")

# Check: is R = r*psi or R = Delta*psi?
# Actually the relation depends on conventions. Let me try h=r and h=Delta.
print()
print(f"  If R = r*psi:")
print(f"    h'/h = dr/dx/r = {dr_dx/r:.6f}")
print(f"    A_Teuk - 2h'/h = {A_coeff_manual - 2*dr_dx/r:.6f}")
print(f"  If R = sqrt(Delta)*psi:")
print(f"    h'/h = (1/2)*Delta'/Delta * dr/dx = {(0.5)*Delta_prime/Delta*dr_dx:.6f}")
print(f"    A_Teuk - 2h'/h = {A_coeff_manual - Delta_prime*dr_dx/Delta:.6f}")
