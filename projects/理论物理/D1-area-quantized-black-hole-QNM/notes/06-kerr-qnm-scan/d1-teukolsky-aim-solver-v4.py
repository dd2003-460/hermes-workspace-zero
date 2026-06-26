#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v4
=====================================
Log-space AIM. Correct derivative handling.

ODE: y'' = lambda_0(x)*y' + mu_0(x)*y
AIM: lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
     mu_{k+1} = lambda_k*mu_k' - mu_k*lambda_k' + mu_k^2
Convergence: theta_N = lambda_{N-1}/lambda_N becomes x-independent at eigenvalue.

D_N = |theta_N(xa) - theta_N(xb)| ~ 0 at QNM.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

# ---- Complex log-space arithmetic ----
# Each complex number represented as (ln|z|, arg(z))

def ln_abs(z):
    return np.log(np.abs(z) + 1e-300)

def cplx(l, p):
    """Reconstruct complex from (ln|z|, phase)."""
    return np.exp(l) * np.exp(1j*p)

def add(l1, p1, l2, p2):
    """z1 + z2."""
    if l1 > l2 + 400: return l1, p1
    if l2 > l1 + 400: return l2, p2
    m = max(l1, l2)
    a = np.exp(l1-m)*np.cos(p1) + np.exp(l2-m)*np.cos(p2)
    b = np.exp(l1-m)*np.sin(p1) + np.exp(l2-m)*np.sin(p2)
    return m + np.log(np.sqrt(a*a + b*b) + 1e-300), np.arctan2(b, a)

def sub(l1, p1, l2, p2):
    """z1 - z2."""
    return add(l1, p1, l2, p2 + np.pi)

def mul(l1, p1, l2, p2):
    """z1 * z2."""
    return l1 + l2, p1 + p2

def sq(l, p):
    """z^2."""
    return 2*l, 2*p

# ---- ODE coefficients ----

def get_lm(x, omega, l):
    """lambda_0(x), mu_0(x) from RW equation mapped to x in (0,1)."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2*M/(1-x)

    dr_dx = 2*M/(1-x)**2
    drstar_dr = r**2/(r - 2*M)**2
    drstar_dx = drstar_dr * dr_dx

    f_r = r**2/(r-2*M)**2
    g_x = 2*M/(1-x)**2
    df_dx = -4*M*r/(r-2*M)**3 * g_x
    dg_dx = 4*M/(1-x)**3
    d2r = df_dx*g_x + f_r*dg_dx

    lam0 = d2r / drstar_dx
    V = (1-2*M/r)*(l*(l+1)/r**2 - 6*M/r**3)
    mu0 = -(omega**2 - V)*drstar_dx**2
    return lam0, mu0

# ---- Log-space AIM ----

def aim_D_N(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM convergence function using log-space arithmetic.

    Returns (D_N, theta_a, theta_b) where D_N = |theta_a - theta_b|.
    """
    dx = 1e-6

    # Initialize at point a
    la0, ma0 = get_lm(xa, omega, l)
    lp, mp = get_lm(xa+dx, omega, l)
    lm, mm = get_lm(max(xa-dx, 1e-8), omega, l)

    la, pa = ln_abs(la0), np.angle(la0)
    ma, qa = ln_abs(ma0), np.angle(ma0)
    dla, pla = ln_abs((lp-lm)/(2*dx)), np.angle((lp-lm)/(2*dx))
    dqa, dplqa = ln_abs((mp-mm)/(2*dx)), np.angle((mp-mm)/(2*dx))

    # Initialize at point b
    lb0, mb0 = get_lm(xb, omega, l)
    lp, mp = get_lm(xb+dx, omega, l)
    lm, mm = get_lm(xb-dx, omega, l)

    lb, pb = ln_abs(lb0), np.angle(lb0)
    mb, qb = ln_abs(mb0), np.angle(mb0)
    dlb, plb = ln_abs((lp-lm)/(2*dx)), np.angle((lp-lm)/(2*dx))
    dqb, dplqb = ln_abs((mp-mm)/(2*dx)), np.angle((mp-mm)/(2*dx))

    # Save lambda_{N-1} for theta computation
    la_prev, pa_prev = la, pa
    lb_prev, pb_prev = lb, pb

    for k in range(1, N+1):
        # ---- lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k ----

        # At point a
        t1 = sq(la, pa)           # lambda^2
        t2 = (dla, pla)           # dlambda
        t3 = (ma, qa + np.pi)     # -mu
        s1 = add(t1[0], t1[1], t2[0], t2[1])
        la_new, pa_new = add(s1[0], s1[1], t3[0], t3[1])

        # At point b
        t1 = sq(lb, pb)
        t2 = (dlb, plb)
        t3 = (mb, qb + np.pi)
        s1 = add(t1[0], t1[1], t2[0], t2[1])
        lb_new, pb_new = add(s1[0], s1[1], t3[0], t3[1])

        # ---- mu_{k+1} = lambda*mu' - mu*lambda' + mu^2 ----

        # At point a
        mA = mul(la, pa, dqa, dplqa)          # lambda*mu'
        mB_mul = mul(ma, qa, dla, pla)        # mu*lambda'
        mB = (mB_mul[0], mB_mul[1] + np.pi)   # -mu*lambda'
        mC = sq(ma, qa)                        # mu^2
        s1 = add(mA[0], mA[1], mB[0], mB[1])
        ma_new, qa_new = add(s1[0], s1[1], mC[0], mC[1])

        # At point b
        mA = mul(lb, pb, dqb, dplqb)
        mB_mul = mul(mb, qb, dlb, plb)
        mB = (mB_mul[0], mB_mul[1] + np.pi)
        mC = sq(mb, qb)
        s1 = add(mA[0], mA[1], mB[0], mB[1])
        mb_new, qb_new = add(s1[0], s1[1], mC[0], mC[1])

        # ---- Derivatives for next step ----
        # d(lambda_{k+1}) = 2*lambda*lambda' - mu'  (ignore lambda'')
        # d(mu_{k+1}) = 2*mu*mu'  (ignore mu'')

        # At point a: 2*la*dla
        t_plus = (la+dla+np.log(2), pa+pla)
        t_minus = (dqa, dplqa + np.pi)
        dla_new, pla_new = add(t_plus[0], t_plus[1], t_minus[0], t_minus[1])
        dqa_new, dplqa_new = (ma+dqa+np.log(2), qa+dplqa)

        # At point b
        t_plus = (lb+dlb+np.log(2), pb+plb)
        t_minus = (dqb, dplqb + np.pi)
        dlb_new, plb_new = add(t_plus[0], t_plus[1], t_minus[0], t_minus[1])
        dqb_new, dplqb_new = (mb+dqb+np.log(2), qb+dplqb)

        # Update
        la_prev, pa_prev = la, pa
        lb_prev, pb_prev = lb, pb
        la, pa = la_new, pa_new
        lb, pb = lb_new, pb_new
        ma, qa = ma_new, qa_new
        mb, qb = mb_new, qb_new
        dla, pla = dla_new, pla_new
        dlb, plb = dlb_new, plb_new
        dqa, dplqa = dqa_new, dplqa_new
        dqb, dplqb = dqb_new, dplqb_new

    # theta_N = lambda_{N-1}/lambda_N = exp(la_prev-la + i*(pa_prev-pa))
    theta_a = cplx(la_prev - la, pa_prev - pa)
    theta_b = cplx(lb_prev - lb, pb_prev - pb)

    return abs(theta_a - theta_b), theta_a, theta_b


# ---- Tests ----

print("="*70)
print("Teukolsky + AIM: Kerr QNM Solver v4 (log-space)")
print("="*70)

def test_qNM(label, omega_ref, l, search_range_wr, search_range_wi):
    print(f"\n--- {label} ---")
    print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

    # Check D at exact QNM
    D, ta, tb = aim_D_N(omega_ref, l, N=80)
    print(f"D at exact QNM: {D:.4e}  (theta_a={ta:.6g}, theta_b={tb:.6g})")

    # Coarse grid search
    min_D, best = np.inf, None
    for wr in np.linspace(*search_range_wr, 25):
        for wi in np.linspace(*search_range_wi, 20):
            D, _, _ = aim_D_N(wr+1j*wi, l, N=80)
            if D < min_D:
                min_D, best = D, (wr, wi)
    print(f"Coarse min: omega = {best[0]:.3f} {best[1]:+.3f}i, D = {min_D:.4e}")

    # Fine search
    min_D2, best2 = np.inf, best
    for wr in np.linspace(best[0]-0.02, best[0]+0.02, 21):
        for wi in np.linspace(best[1]-0.02, best[1]+0.02, 15):
            D, _, _ = aim_D_N(wr+1j*wi, l, N=80)
            if D < min_D2:
                min_D2, best2 = D, (wr, wi)
    print(f"Fine min: omega = {best2[0]:.5f} {best2[1]:+.5f}i, D = {min_D2:.4e}")

    # Nelder-Mead
    def obj(p):
        return aim_D_N(p[0]+1j*p[1], l, N=80)[0]
    res = minimize(obj, best2, method='Nelder-Mead',
                   options={'maxiter':5000, 'xatol':1e-6, 'fatol':1e-15})
    found = res.x[0] + 1j*res.x[1]
    err = abs(found - omega_ref) / abs(omega_ref) * 100
    print(f"Optimized: omega = {found.real:.5f} {found.imag:+.5f}i")
    print(f"  D = {res.fun:.4e}, error = {err:.1f}%")
    return found, err

test_qNM("Schwarzschild l=2, n=0", 0.37367-0.08896j, l=2,
         search_range_wr=(0.30, 0.45), search_range_wi=(-0.15, -0.02))
test_qNM("Schwarzschild l=3, n=0", 0.59108-0.05902j, l=3,
         search_range_wr=(0.45, 0.75), search_range_wi=(-0.12, -0.01))

# Test with different x-points to check robustness
print("\n--- Robustness: Different x-point pairs ---")
omega_test = 0.37367-0.08896j
for xa, xb in [(0.2, 0.8), (0.3, 0.7), (0.1, 0.9), (0.25, 0.75)]:
    D, ta, tb = aim_D_N(omega_test, l=2, N=80, xa=xa, xb=xb)
    print(f"x=({xa},{xb}): D={D:.4e}, theta_a={ta:.6g}, theta_b={tb:.6g}")

# Test with different N
print("\n--- Robustness: Different N ---")
for N in [30, 50, 80, 100, 150]:
    D, ta, tb = aim_D_N(omega_test, l=2, N=N)
    print(f"N={N:3d}: D={D:.4e}")
