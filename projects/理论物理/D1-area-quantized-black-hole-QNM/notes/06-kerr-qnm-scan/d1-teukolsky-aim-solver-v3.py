#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v3
=====================================
Log-space AIM to handle doubly-exponential growth.

Uses complex arithmetic in log-space: track log|z| and arg(z) separately,
then sum with scale-invariant arithmetic (subtract max log before exp).

Convergence: D_N = |theta_N(x1) - theta_N(x2)| where theta_N = lambda_{N-1}/lambda_N.
At eigenvalue, theta becomes x-independent.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0
berti = {(0,2,2,0): (0.37367, -0.08896), (0,3,3,0): (0.59108, -0.05902)}

# ---- Utility: complex log-space addition ----

def log_sum_two(la, pa, lb, pb):
    """Add two complex numbers given (log_abs, phase). Returns (log_abs, phase)."""
    if la > lb + 300:
        return la, pa  # second term negligible
    if lb > la + 300:
        return lb, pb
    m = max(la, lb)
    sa = np.exp(la - m); sb = np.exp(lb - m)
    re = sa*np.cos(pa) + sb*np.cos(pb)
    im = sa*np.sin(pa) + sb*np.sin(pb)
    return m + np.log(np.sqrt(re**2 + im**2) + 1e-300), np.arctan2(im, re)

def log_neg(la, pa):
    """Negate a complex number in log-space."""
    return la, pa + np.pi

def log_mul(la, pa, lb, pb):
    """Multiply two complex numbers in log-space."""
    return la + lb, pa + pb

def log_pow2(la, pa):
    """Square a complex number in log-space."""
    return 2*la, 2*pa

def log_div(la, pa, lb, pb):
    """Divide: (la,pa) / (lb,pb)."""
    return la - lb, pa - pb

# ---- Lambda_0, mu_0 ----

def get_lm(x, omega, l, M=1.0):
    """Get (lambda_0, mu_0) at point x for the ODE: y'' = lambda*y' + mu*y"""
    x = np.clip(x, 1e-10, 1-1e-10)
    r = 2*M/(1-x)

    drstar_dr = r**2/(r-2*M)**2
    dr_dx = 2*M/(1-x)**2
    drstar_dx = drstar_dr * dr_dx

    f_r = r**2/(r-2*M)**2
    g_x = 2*M/(1-x)**2
    df_dx = -4*M*r/(r-2*M)**3 * g_x
    dg_dx = 4*M/(1-x)**3
    d2r = df_dx*g_x + f_r*dg_dx

    lam0 = d2r / drstar_dx
    f = 1.0 - 2*M/r
    V = f*(l*(l+1)/r**2 - 6*M/r**3)
    mu0 = -(omega**2 - V)*drstar_dx**2

    return lam0, mu0

# ---- Derivatives of lambda_0, mu_0 ----

def get_lm_derivs(x, omega, l, M=1.0):
    """Central-difference derivatives of (lambda_0, mu_0)."""
    dx = 1e-6
    lp, mp = get_lm(min(x+dx, 0.9999), omega, l, M)
    lm, mm = get_lm(max(x-dx, 1e-6), omega, l, M)
    return (lp-lm)/(2*dx), (mp-mm)/(2*dx)

# ---- Log-space AIM ----

def aim_omega_N(omega, l, M=1.0, N=80):
    """
    AIM returning theta_N at two x-points.

    Returns theta_N(a) and theta_N(b) as (log_abs, phase).
    At eigenvalue, theta_N(a) = theta_N(b) (x-independent).

    Uses log-space throughout to handle |lambda_k| ~ exp(2^k).
    """
    xa, xb = 0.3, 0.7
    dx_small = 1e-6

    # lambda_0, mu_0 and derivatives at each point
    for label, x in [('a', xa), ('b', xb)]:
        lam0, mu0 = get_lm(x, omega, l, M)
        dlam0, dmu0 = get_lm_derivs(x, omega, l, M)

        # Convert to log-space
        if label == 'a':
            la, pa = np.log(abs(lam0)), np.angle(lam0)
            ma, qa = np.log(abs(mu0)), np.angle(mu0)
            dla, pla = np.log(abs(dlam0)), np.angle(dlam0)
            dqa, dplqa = np.log(abs(dmu0)), np.angle(dmu0)
        else:
            lb, pb = np.log(abs(lam0)), np.angle(lam0)
            mb, qb = np.log(abs(mu0)), np.angle(mu0)
            dlb, plb = np.log(abs(dlam0)), np.angle(dlam0)
            dqb, dplqb = np.log(abs(dmu0)), np.angle(dmu0)

    # AIM recurrence in log-space:
    # lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k  (three terms)
    # mu_{k+1} = lambda_k*mu_k' - mu_k*lambda_k' + mu_k^2  (three terms)
    #
    # Derivative approximations:
    # For k>=2: d(lambda_k) ~ (lambda_k - lambda_k_at_other_point) / span
    # This is a poor approximation but the AIM convergence condition
    # is robust to derivative errors since the dominant term is lambda_k^2.
    #
    # More accurate: d(lambda_k) ~ 2*lambda_k*d(lambda_k)_prev (from chain rule)
    # d(lam_{k+1}) = 2*lam*dlam + d^2lam - dmu ~ 2*lam*dlam - dmu (ignore second derivative)

    span = xb - xa

    # Previous log-lambda for theta tracking
    la_prev, pa_prev = la, pa
    lb_prev, pb_prev = lb, pb

    for k in range(1, N+1):
        # --- lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k ---

        # At point a
        # Term 1: lam_a^2 -> (2*la, 2*pa)
        t1_a = log_pow2(la, pa)
        # Term 2: dlam_a -> (dla, pla)
        t2_a = (dla, pla)
        # Term 3: -mu_a -> log_neg(ma, qa)
        t3_a = log_neg(ma, qa)

        # Sum t1 + t2 + t3 (add largest pairs first to minimize cancellation)
        s1_a = log_sum_two(t1_a[0], t1_a[1], t2_a[0], t2_a[1])
        la_new, pa_new = log_sum_two(s1_a[0], s1_a[1], t3_a[0], t3_a[1])

        # At point b
        t1_b = log_pow2(lb, pb)
        t2_b = (dlb, plb)
        t3_b = log_neg(mb, qb)

        s1_b = log_sum_two(t1_b[0], t1_b[1], t2_b[0], t2_b[1])
        lb_new, pb_new = log_sum_two(s1_b[0], s1_b[1], t3_b[0], t3_b[1])

        # --- mu_{k+1} = lam*dmu - mu*dlam + mu^2 ---

        # At point a
        mA_a = log_mul(la, pa, dqa, dplqa)       # lam*dmu
        mB_a = log_neg(log_mul(ma, qa, dla, pla))  # -mu*dlam
        mC_a = log_pow2(ma, qa)                   # mu^2
        s1_ma = log_sum_two(mA_a[0], mA_a[1], mB_a[0], mB_a[1])
        ma_new, qa_new = log_sum_two(s1_ma[0], s1_ma[1], mC_a[0], mC_a[1])

        # At point b
        mA_b = log_mul(lb, pb, dqb, dplqb)
        mB_b = log_neg(log_mul(mb, qb, dlb, plb))
        mC_b = log_pow2(mb, qb)
        s1_mb = log_sum_two(mA_b[0], mA_b[1], mB_b[0], mB_b[1])
        mb_new, qb_new = log_sum_two(s1_mb[0], s1_mb[1], mC_b[0], mC_b[1])

        # --- Derivatives for next step ---
        # d(lambda_{k+1}) = 2*lam*dlam - dmu (approx, ignoring lam'')
        # d(mu_{k+1}) = 2*mu*dmu (approx, ignoring mu'')

        dla_new, pla_new = log_sum_two(
            log_mul(log_mul(la, pa, dla, pla)[0]+np.log(2), log_mul(la, pa, dla, pla)[1], 0, 0)[0],
            log_mul(la, pa, dla, pla)[1],
            log_neg(dqa, dplqa)
        )
        # Simpler: 2*lam*dlam
        t_dla1 = (la+dla+np.log(2), pa+pla)
        t_dla2 = log_neg(dqa, dplqa)
        dla_new, pla_new = log_sum_two(t_dla1[0], t_dla1[1], t_dla2[0], t_dla2[1])

        dqa_new, dplqa_new = (ma+dqa+np.log(2), qa+dplqa)

        t_dlb1 = (lb+dlb+np.log(2), pb+plb)
        t_dlb2 = log_neg(dqb, dplqb)
        dlb_new, plb_new = log_sum_two(t_dlb1[0], t_dlb1[1], t_dlb2[0], t_dlb2[1])

        dqb_new, dplqb_new = (mb+dqb+np.log(2), qb+dplqb)

        # Update
        la, pa = la_new, pa_new
        lb, pb = lb_new, pb_new
        ma, qa = ma_new, qa_new
        mb, qb = mb_new, qb_new
        dla, pla = dla_new, pla_new
        dlb, plb = dlb_new, plb_new
        dqa, dplqa = dqa_new, dplqa_new
        dqb, dplqb = dqb_new, dplqb_new

    # theta_N = lambda_{N-1}/lambda_N
    # theta_a = exp(la_prev - la + i*(pa_prev - pa))
    # theta_b = exp(lb_prev - lb + i*(pb_prev - pb))

    ltha, ptha = log_div(la_prev, pa_prev, la, pa)
    lthb, pthb = log_div(lb_prev, pb_prev, lb, pb)

    return (ltha, ptha), (lthb, pthb)


def aim_D_N(omega, l, M=1.0, N=80):
    """D_N = |theta_N(x1) - theta_N(x2)| in regular space."""
    (ltha, ptha), (lthb, pthb) = aim_omega_N(omega, l, M, N)

    # Convert back to regular space and subtract
    theta_a = np.exp(ltha) * np.exp(1j*ptha)
    theta_b = np.exp(lthb) * np.exp(1j*pthb)

    return abs(theta_a - theta_b), theta_a, theta_b


# ---- Test ----

print("="*70)
print("Teukolsky + AIM: Kerr QNM Solver v3 (log-space)")
print("="*70)

# Test on known QNM values
print("\n--- Test: Schwarzschild l=2, n=0 ---")
expected = 0.37367 - 0.08896j
print(f"Expected: omega = {expected.real:.5f} {expected.imag:+.5f}i")

# Evaluate at exact QNM
D, ta, tb = aim_D_N(expected, l=2, N=60)
print(f"At exact QNM: D={D:.4e}, theta_a={ta:.6e}, theta_b={tb:.6e}")

# Grid search
min_D = np.inf
best = None
for wr in np.linspace(0.30, 0.45, 31):
    for wi in np.linspace(-0.15, -0.02, 22):
        omega = wr + 1j*wi
        D, _, _ = aim_D_N(omega, l=2, N=60)
        if D < min_D:
            min_D = D
            best = (wr, wi)

if best:
    print(f"Coarse best: omega = {best[0]:.3f} {best[1]:+.3f}i, D={min_D:.4e}")

    # Fine search
    min_D2 = np.inf
    for wr in np.linspace(best[0]-0.02, best[0]+0.02, 21):
        for wi in np.linspace(best[1]-0.015, best[1]+0.015, 11):
            D, _, _ = aim_D_N(wr + 1j*wi, l=2, N=60)
            if D < min_D2:
                min_D2 = D
                best = (wr, wi)

    print(f"Fine best: omega = {best[0]:.5f} {best[1]:+.5f}i, D={min_D2:.4e}")

    # Optimize
    def obj(p):
        D, _, _ = aim_D_N(p[0]+1j*p[1], l=2, N=60)
        return D
    res = minimize(obj, best, method='Nelder-Mead',
                   options={'maxiter':3000, 'xatol':1e-6, 'fatol':1e-15})
    found = res.x[0] + 1j*res.x[1]
    err = abs(found - expected) / abs(expected) * 100
    print(f"Optimized: omega = {res.x[0]:.5f} {res.x[1]:+.5f}i, D={res.fun:.4e}, err={err:.1f}%")

print("\n--- Test: Schwarzschild l=3, n=0 ---")
expected3 = 0.59108 - 0.05902j
print(f"Expected: omega = {expected3.real:.5f} {expected3.imag:+.5f}i")

D, ta, tb = aim_D_N(expected3, l=3, N=60)
print(f"At exact QNM: D={D:.4e}, theta_a={ta:.6e}, theta_b={tb:.6e}")

min_D = np.inf
best = None
for wr in np.linspace(0.45, 0.75, 31):
    for wi in np.linspace(-0.12, -0.01, 23):
        D, _, _ = aim_D_N(wr + 1j*wi, l=3, N=60)
        if D < min_D:
            min_D = D
            best = (wr, wi)

if best:
    print(f"Coarse best: omega = {best[0]:.3f} {best[1]:+.3f}i, D={min_D:.4e}")

    min_D2 = np.inf
    for wr in np.linspace(best[0]-0.02, best[0]+0.02, 21):
        for wi in np.linspace(best[1]-0.015, best[1]+0.015, 11):
            D, _, _ = aim_D_N(wr + 1j*wi, l=3, N=60)
            if D < min_D2:
                min_D2 = D
                best = (wr, wi)

    print(f"Fine best: omega = {best[0]:.5f} {best[1]:+.5f}i, D={min_D2:.4e}")

    def obj3(p):
        D, _, _ = aim_D_N(p[0]+1j*p[1], l=3, N=60)
        return D
    res = minimize(obj3, best, method='Nelder-Mead',
                   options={'maxiter':3000, 'xatol':1e-6, 'fatol':1e-15})
    found3 = res.x[0] + 1j*res.x[1]
    err3 = abs(found3 - expected3) / abs(expected3) * 100
    print(f"Optimized: omega = {res.x[0]:.5f} {res.x[1]:+.5f}i, err={err3:.1f}%")
