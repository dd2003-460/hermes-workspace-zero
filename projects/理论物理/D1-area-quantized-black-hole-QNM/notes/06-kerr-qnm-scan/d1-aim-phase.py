#!/usr/bin/env python3
"""
AIM convergence via phase alignment.

At the QNM eigenvalue, theta_N(x) = lambda_{N-1}/lambda_N becomes x-independent.
The magnitude varies with x, but the PHASE should be the same at all x.

Convergence criterion: D_phase = |arg(theta_a) - arg(theta_b)| → 0

This avoids the magnitude-matching problem where one point underflows while
the other doesn't.
"""

import numpy as np

M = 1.0


def get_coeffs(x, omega, l=2):
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)
    P = 2 / (x * (1 - x)**2)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    a_base = -dlnP
    V = (1 - 2 * M / r) * (l * (l + 1) / r**2 - 2 * M / r**3)
    b_base = P**2 * (omega**2 - V)
    return -a_base, -b_base


def aim_at_x(omega, x, N=8):
    """AIM at single point. Returns (theta, la_final, log_abs_la_final)."""
    dx_num = 1e-6
    la, ma = get_coeffs(x, omega)
    dla = (get_coeffs(x + dx_num, omega)[0] - get_coeffs(x - dx_num, omega)[0]) / (2 * dx_num)
    dmu = (get_coeffs(x + dx_num, omega)[1] - get_coeffs(x - dx_num, omega)[1]) / (2 * dx_num)

    log_scale_cum_a = 0.0  # cumulative log scaling for this point

    for k in range(N):
        la_prev = la
        ln = la**2 + dla - ma
        mn = la * dmu - ma * dla + ma**2
        dla_n = 2 * la * dla - dmu
        dmu_n = 2 * ma * dmu

        max_val = max(abs(ln), abs(mn), abs(dla_n), abs(dmu_n))
        scale = max_val / 1e40 if max_val > 1e40 else 1.0
        log_scale_cum_a += np.log(scale)

        la_prev /= scale

        la = ln / scale
        ma = mn / scale
        dla = dla_n / scale
        dmu = dmu_n / scale

    theta = la_prev / la
    return theta, abs(la), log_scale_cum_a


def aim_phase_diff(omega, N=8, xa=0.35, xb=0.65):
    """Compute phase difference and magnitude ratio at two points."""
    ta, ma_val, log_s_a = aim_at_x(omega, xa, N)
    tb, mb_val, log_s_b = aim_at_x(omega, xb, N)

    phase_a = np.angle(ta)
    phase_b = np.angle(tb)
    phase_diff = abs(phase_a - phase_b)
    if phase_diff > np.pi:
        phase_diff = 2 * np.pi - phase_diff

    mag_a = abs(ta)
    mag_b = abs(tb)
    mag_ratio = abs(np.log(mag_a) - np.log(mag_b)) if mag_a > 0 and mag_b > 0 else 1e30

    return phase_diff, mag_ratio, phase_a, phase_b, mag_a, mag_b, ta, tb


print("=" * 70)
print("AIM: Phase Convergence Criterion")
print("=" * 70)

omega_ref = 0.37367 - 0.08896j

# Check phase behavior at exact QNM
print(f"\n--- Phase analysis at omega={omega_ref:.4f} ---")
for N in [3, 4, 5, 6, 7, 8, 10]:
    pd, mr, pa, pb, ma, mb, ta, tb = aim_phase_diff(omega_ref, N)
    print(f"  N={N:2d}: phase_diff={pd:.6f}, |phase_a|={abs(pa):.4f}, |phase_b|={abs(pb):.4f}, "
          f"|theta_a|={ma:.4e}, |theta_b|={mb:.4e}, log_mag_diff={mr:.4f}")
    print(f"       theta_a={ta:.6e}, theta_b={tb:.6e}")

# Scan phase_diff across omega grid
print(f"\n--- Phase scan (N=7) ---")
best_pd, best_w = 10, None
for wr in np.arange(0.34, 0.40, 0.004):
    for wi in np.arange(-0.12, -0.055, 0.006):
        w = wr + 1j * wi
        pd, mr, pa, pb, ma, mb, ta, tb = aim_phase_diff(w, N=7)
        if pd < best_pd:
            best_pd = pd
            best_w = w
        star = " ***" if pd < 0.01 else (" *" if pd < 0.05 else "")
        if star:
            print(f"  w={wr:.3f}{wi:+.3f}j: phase_diff={pd:.4f}, log_mag_diff={mr:.2f}{star}")

print(f"  Best: w={best_w:.5f}, phase_diff={best_pd:.6f}")

# Finer scan around best
print(f"\n--- Fine phase scan (N=7) around w={best_w:.5f} ---")
wr0, wi0 = best_w.real, best_w.imag
best_pd2, best_w2 = 10, None
for wr in np.arange(wr0 - 0.01, wr0 + 0.011, 0.001):
    for wi in np.arange(wi0 - 0.008, wi0 + 0.009, 0.001):
        w = wr + 1j * wi
        pd, mr, pa, pb, ma, mb, ta, tb = aim_phase_diff(w, N=7)
        if pd < best_pd2:
            best_pd2 = pd
            best_w2 = w
        star = " ***" if pd < 0.01 else (" *" if pd < 0.03 else "")
        if star:
            print(f"  w={wr:.3f}{wi:+.3f}j: phase_diff={pd:.4f}, log_mag_diff={mr:.2f}{star}")

print(f"  Best: w={best_w2:.5f}, phase_diff={best_pd2:.6f}")

# Same for N=6 and N=8
for N in [5, 6, 8]:
    print(f"\n--- Phase scan N={N} ---")
    best_pd3, best_w3 = 10, None
    for wr in np.arange(0.36, 0.39, 0.002):
        for wi in np.arange(-0.105, -0.07, 0.002):
            w = wr + 1j * wi
            pd, mr, pa, pb, ma, mb, ta, tb = aim_phase_diff(w, N=N)
            if pd < best_pd3:
                best_pd3 = pd
                best_w3 = w
    print(f"  Best at N={N}: w={best_w3:.5f}, phase_diff={best_pd3:.6f}")

# Also: test with Cho formulation for reference
print(f"\n{'='*70}")
print(f"Cho formulation for comparison:")
print(f"{'='*70}")

def get_coeffs_cho(x, omega, l=2):
    x = np.clip(x, 1e-10, 1 - 1e-10)
    dlnP = (1 - 3 * x) / (x * (x - 1))
    p1_c = dlnP
    kappa = 2j * omega
    beta_a = 2j * omega
    gamma_a = -2j * omega
    psi_p = kappa / x - beta_a / (1 - x) + gamma_a / (1 - x)**2
    psi_pp = -kappa / x**2 + beta_a / (1 - x)**2 - 2 * gamma_a / (1 - x)**3
    psi_dd = psi_p**2 + psi_pp
    S0 = (16 * omega**2 * x - 32 * omega**2 - 8j * omega * (1 - x)
          + l * (l + 1) - 3 * (1 - x)) / (x * (1 - x)**2)
    p2_c = S0 - psi_dd - p1_c * psi_p
    return -p1_c, -p2_c

def aim_at_x_generic(get_c, omega, x, N=8):
    dx_num = 1e-6
    la, ma = get_c(x, omega)
    dla = (get_c(x + dx_num, omega)[0] - get_c(x - dx_num, omega)[0]) / (2 * dx_num)
    dmu = (get_c(x + dx_num, omega)[1] - get_c(x - dx_num, omega)[1]) / (2 * dx_num)
    for k in range(N):
        la_prev = la
        ln = la**2 + dla - ma
        mn = la * dmu - ma * dla + ma**2
        dla_n = 2 * la * dla - dmu
        dmu_n = 2 * ma * dmu
        max_val = max(abs(ln), abs(mn), abs(dla_n), abs(dmu_n))
        scale = max_val / 1e40 if max_val > 1e40 else 1.0
        la_prev /= scale
        la = ln / scale
        ma = mn / scale
        dla = dla_n / scale
        dmu = dmu_n / scale
    theta = la_prev / la
    return theta

def aim_phase_diff_generic(get_c, omega, N=8):
    ta = aim_at_x_generic(get_c, omega, 0.35, N)
    tb = aim_at_x_generic(get_c, omega, 0.65, N)
    pa = np.angle(ta)
    pb = np.angle(tb)
    pd = abs(pa - pb)
    if pd > np.pi:
        pd = 2 * np.pi - pd
    return pd, abs(ta), abs(tb), pa, pb

for N in [5, 6, 7, 8]:
    print(f"\n--- Cho phase scan N={N} ---")
    best_pd, best_w = 10, None
    for wr in np.arange(0.36, 0.39, 0.002):
        for wi in np.arange(-0.105, -0.07, 0.002):
            w = wr + 1j * wi
            pd, ma, mb, pa, pb = aim_phase_diff_generic(get_coeffs_cho, w, N=N)
            if pd < best_pd:
                best_pd = pd
                best_w = w
    print(f"  Best at N={N}: w={best_w:.5f}, phase_diff={best_pd:.6f}")

    # Check at exact QNM
    pd, ma, mb, pa, pb = aim_phase_diff_generic(get_coeffs_cho, omega_ref, N=N)
    print(f"  At exact QNM: phase_diff={pd:.6f}, |theta_a|={ma:.4e}, |theta_b|={mb:.4e}")
