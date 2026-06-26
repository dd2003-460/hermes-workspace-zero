#!/usr/bin/env python3
"""
AIM solver following Dehghan-Safari 2011 formulation.

The key: ODE coefficients must have |lambda_0| > O(1) for the AIM recurrence
to double exponentially. The Dehghan gauge transform of the RW equation
gives polynomial-coefficient ODEs with correct magnitude.
"""

import numpy as np

M = 1.0

def get_coeffs_dehghan(x, omega, l=2):
    """ODE coefficients from RW equation + Dehghan gauge transform.

    Returns lambda_0, mu_0 for the ODE: y'' = lambda_0*y' + mu_0*y

    The Dehghan transformation: R = F^(iw) * x^(-iw) * (1-x)^(iw) * exp(-iw/(1-x)) * u
    removes the known singular behavior at x=0 (horizon) and x=1 (infinity).
    """
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)

    # RW equation in x coords: R_xx + a*R_x + b*R = 0
    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a = -dlnP  # = -(1-3x)/(x*(x-1))
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b = P**2 * (omega**2 - V)

    # Gauge factor g'/g from Dehghan transformation
    # G = F^alpha * x^alpha * (1-x)^beta * exp(gamma/(1-x))
    # alpha=-iw, beta=iw, gamma=-iw
    F_over_F = 2 * (2 * x - 1) / (x * (1 - x))  # F'/F

    alpha = -1j * omega
    beta = 1j * omega
    gamma_val = -1j * omega
    g_over_g = alpha * (F_over_F + 1 / x) - beta / (1 - x) + gamma_val / (1 - x)**2

    # d(g'/g)/dx numerically
    dx_num = 1e-7
    x_p = min(x + dx_num, 0.99999)
    x_m = max(x - dx_num, 1e-8)
    r_p = 2 * M / (1 - x_p)
    Fp = 2 * (2 * x_p - 1) / (x_p * (1 - x_p))
    gp = alpha * (Fp + 1 / x_p) - beta / (1 - x_p) + gamma_val / (1 - x_p)**2
    rm = 2 * M / (1 - x_m)
    Fm = 2 * (2 * x_m - 1) / (x_m * (1 - x_m))
    gm = alpha * (Fm + 1 / x_m) - beta / (1 - x_m) + gamma_val / (1 - x_m)**2
    dg_over_g = (gp - gm) / (2 * dx_num)

    # Transformed ODE: u'' + p1*u' + p2*u = 0
    p1 = a + 2 * g_over_g
    p2 = b + a * g_over_g + 2 * g_over_g**2 + dg_over_g

    # AIM form: y'' = lambda_0*y' + mu_0*y
    return -p1, -p2


def get_coeffs_cho(x, omega, l=2):
    """ODE coefficients from Cho's six-factor ansatz.

    Cho's ansatz: kappa=2iw, beta=2iw, gamma=-2iw
    """
    x = np.clip(x, 1e-10, 1 - 1e-10)
    dlnP = (1 - 3 * x) / (x * (x - 1))

    p1_cho = dlnP

    kappa = 2j * omega
    beta_a = 2j * omega
    gamma_a = -2j * omega

    psi_prime = kappa / x - beta_a / (1 - x) + gamma_a / (1 - x)**2
    psi_pp = -kappa / x**2 + beta_a / (1 - x)**2 - 2 * gamma_a / (1 - x)**3
    psi_dd = psi_prime**2 + psi_pp

    S0 = (16 * omega**2 * x - 32 * omega**2 - 8j * omega * (1 - x)
          + l * (l + 1) - 3 * (1 - x)) / (x * (1 - x)**2)
    p2_cho = S0 - psi_dd - p1_cho * psi_prime

    return -p1_cho, -p2_cho


def aim_run(get_coeffs, omega, N=80, xa=0.3, xb=0.7):
    """AIM with global per-step scaling.

    get_coeffs(x, w) -> (lambda_0, mu_0)
    """
    dx = 1e-6

    # Init at both points
    la_a, ma_a = get_coeffs(xa, omega)
    la_b, ma_b = get_coeffs(xb, omega)

    # Numerical derivatives of lambda_0 and mu_0
    dla_a = (get_coeffs(xa + dx, omega)[0] - get_coeffs(xa - dx, omega)[0]) / (2 * dx)
    dmu_a = (get_coeffs(xa + dx, omega)[1] - get_coeffs(xa - dx, omega)[1]) / (2 * dx)
    dla_b = (get_coeffs(xb + dx, omega)[0] - get_coeffs(xb - dx, omega)[0]) / (2 * dx)
    dmu_b = (get_coeffs(xb + dx, omega)[1] - get_coeffs(xb - dx, omega)[1]) / (2 * dx)

    MAX_S = 1e80

    for k in range(N):
        # Save prev lambda BEFORE computing next
        la_prev_a = la_a
        la_prev_b = la_b

        # Recurrence: lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
        ln_a = la_a**2 + dla_a - ma_a
        ln_b = la_b**2 + dla_b - ma_b
        # mu_{k+1} = lambda_k * mu_k' - mu_k * lambda_k' + mu_k^2
        mu_a = la_a * dmu_a - ma_a * dla_a + ma_a**2
        mu_b = la_b * dmu_b - ma_b * dla_b + ma_b**2
        # Derivative updates (approximate: drop lambda'' and mu'' terms)
        dla_new_a = 2 * la_a * dla_a - dmu_a
        dla_new_b = 2 * la_b * dla_b - dmu_b
        dmu_new_a = 2 * ma_a * dmu_a
        dmu_new_b = 2 * ma_b * dmu_b

        scale = max(abs(ln_a), abs(ln_b), abs(mu_a), abs(mu_b),
                    abs(dla_new_a), abs(dmu_new_a), abs(dla_new_b), abs(dmu_new_b))

        if scale > MAX_S:
            la_prev_a /= scale
            la_prev_b /= scale
            la_a = ln_a / scale
            la_b = ln_b / scale
            ma_a = mu_a / scale
            ma_b = mu_b / scale
            dla_a = dla_new_a / scale
            dla_b = dla_new_b / scale
            dmu_a = dmu_new_a / scale
            dmu_b = dmu_new_b / scale
        else:
            la_a = ln_a
            la_b = ln_b
            ma_a = mu_a
            ma_b = mu_b
            dla_a = dla_new_a
            dla_b = dla_new_b
            dmu_a = dmu_new_a
            dmu_b = dmu_new_b

    theta_a = la_prev_a / la_a
    theta_b = la_prev_b / la_b

    return abs(theta_a - theta_b), theta_a, theta_b


# ---- Diagnostic ----
print("=" * 70)
print("AIM: Dehghan vs Cho - Diagnostic")
print("=" * 70)

omega_test = 0.37367 - 0.08896j

print(f"\n--- Dehghan formulation at omega={omega_test:.4f} ---")
for label, x in [("xa=0.3", 0.3), ("xb=0.7", 0.7)]:
    lam, mu = get_coeffs_dehghan(x, omega_test)
    print(f"  {label}: lam0={lam:.6e}, mu0={mu:.6e}, |lam|={abs(lam):.4e}, |mu|={abs(mu):.4e}")

print(f"\n--- Cho formulation at omega={omega_test:.4f} ---")
for label, x in [("xa=0.3", 0.3), ("xb=0.7", 0.7)]:
    lam, mu = get_coeffs_cho(x, omega_test)
    print(f"  {label}: lam0={lam:.6e}, mu0={mu:.6e}, |lam|={abs(lam):.4e}, |mu|={abs(mu):.4e}")

# AIM convergence at exact QNM
for name, getter in [("Dehghan", get_coeffs_dehghan), ("Cho", get_coeffs_cho)]:
    print(f"\n--- AIM convergence ({name}) at exact QNM ---")
    for N in [10, 15, 20, 30, 40, 50, 60]:
        D, ta, tb = aim_run(getter, omega_test, N=N)
        print(f"  N={N:2d}: D={D:.6e}, theta_a={ta:.6e}, theta_b={tb:.6e}")

# Scan near known QNM
print(f"\n--- Scanning near QNM (Dehghan, N=40) ---")
best_D, best_w = 1e300, None
for wr in np.linspace(0.36, 0.39, 7):
    for wi in np.linspace(-0.11, -0.06, 6):
        w = wr + 1j * wi
        D, _, _ = aim_run(get_coeffs_dehghan, w, N=40)
        star = " *" if D < best_D else "  "
        if D < best_D:
            best_D = D
            best_w = w
        print(f"  w={wr:.4f}{wi:+.3f}j: D={D:.6e}{star}")
print(f"  Best: w={best_w:.5f}, D={best_D:.6e}")

print(f"\n--- Scanning near QNM (Cho, N=40) ---")
best_D, best_w = 1e300, None
for wr in np.linspace(0.36, 0.39, 7):
    for wi in np.linspace(-0.11, -0.06, 6):
        w = wr + 1j * wi
        D, _, _ = aim_run(get_coeffs_cho, w, N=40)
        star = " *" if D < best_D else "  "
        if D < best_D:
            best_D = D
            best_w = w
        print(f"  w={wr:.4f}{wi:+.3f}j: D={D:.6e}{star}")
print(f"  Best: w={best_w:.5f}, D={best_D:.6e}")
