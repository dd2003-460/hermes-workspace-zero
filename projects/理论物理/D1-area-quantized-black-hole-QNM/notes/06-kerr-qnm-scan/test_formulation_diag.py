#!/usr/bin/env python3
"""Diagnostic: compare raw vs dehghan AIM formulations."""
import numpy as np

M = 1.0
OMEGA_REF = 0.37367 - 0.08896j

def get_coeffs_raw(x, omega, l=2):
    """No gauge: direct coordinate transformation."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)
    drstar_dx = r**2 / (r - 2*M)**2
    d2rstar_dx2 = 2*r/(1-x)**3 * drstar_dx/(r-2*M)
    V = (1 - 2*M/r) * (l*(l+1)/r**2 - 2*M/r**3)  # scalar perturbation
    lam = d2rstar_dx2 / drstar_dx
    mu = -drstar_dx**2 * (omega**2 - V)
    return lam, mu

def get_coeffs_dehghan(x, omega, l=2):
    """Dehghan-Safari Dehghan gauge with c=6 potential."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)
    drstar_dx = r**2 / (r - 2*M)**2
    d2rstar_dx2 = 2*r/(1-x)**3 * drstar_dx/(r-2*M)
    V = (1 - 2*M/r) * (l*(l+1)/r**2 - 6*M/r**3)  # gravitational
    dln = 1j * omega * (3/(1-x) - 1/x)
    d2ln = 1j * omega * (3/(1-x)**2 + 1/x**2)
    Q_over_P = -d2rstar_dx2 / drstar_dx
    lam = -(2*dln + Q_over_P)
    mu = -(d2ln + dln**2 + Q_over_P*dln + (omega**2 - V)*drstar_dx**2)
    return lam, mu

def aim_theta(omega, l, N, x, get_coeffs):
    """Return theta = lambda_{N-1}/lambda_N at point x."""
    la, mu = get_coeffs(x, omega, l)
    eps = 1e-7
    dla = (get_coeffs(x+eps, omega, l)[0] - get_coeffs(x-eps, omega, l)[0])/(2*eps)
    dmu = (get_coeffs(x+eps, omega, l)[1] - get_coeffs(x-eps, omega, l)[1])/(2*eps)
    for k in range(N):
        la_prev = la
        la_n = la**2 + dla - mu
        mu_n = la*dmu - mu*dla + mu**2
        dla_n = 2*la*dla - dmu
        dmu_n = 2*mu*dmu
        mx = max(abs(la_n), abs(mu_n), abs(dla_n), abs(dmu_n), 1.0)
        sc = mx / 1e80 if mx > 1e80 else 1.0
        la, mu, dla, dmu = la_n/sc, mu_n/sc, dla_n/sc, dmu_n/sc
    if abs(la) < 1e-300: return complex('inf')
    return la_prev/la

def aim_c(omega, l, N, xa, xb, get_coeffs):
    """Convergence indicator C = |theta_a/|theta_a| - theta_b/|theta_b||."""
    ta = aim_theta(omega, l, N, xa, get_coeffs)
    tb = aim_theta(omega, l, N, xb, get_coeffs)
    ta_d = ta/abs(ta) if abs(ta) > 1e-100 else 0
    tb_d = tb/abs(tb) if abs(tb) > 1e-100 else 0
    return abs(ta_d - tb_d)

def aim_W_abs(omega, l, N, xa, xb, get_coeffs):
    """Absolute Wronskian |W_N|."""
    eps = 1e-7
    def run_pts(y):
        la, mu = get_coeffs(y, omega, l)
        dla = (get_coeffs(y+eps, omega, l)[0] - get_coeffs(y-eps, omega, l)[0])/(2*eps)
        dmu = (get_coeffs(y+eps, omega, l)[1] - get_coeffs(y-eps, omega, l)[1])/(2*eps)
        lp_a, mp_a = la, mu
        lp_b, mp_b = la, mu
        for k in range(N):
            la_n = la**2 + dla - mu
            mu_n = la*dmu - mu*dla + mu**2
            dla_n = 2*la*dla - dmu
            dmu_n = 2*mu*dmu
            mx = max(abs(la_n), abs(mu_n), abs(dla_n), abs(dmu_n), 1.0)
            sc = mx / 1e80 if mx > 1e80 else 1.0
            lp_a, mp_a = la, mu
            lp_b, mp_b = la, mu
            la, mu, dla, dmu = la_n/sc, mu_n/sc, dla_n/sc, dmu_n/sc
        return lp_a, la_n, lp_b, la_n
    
    la_prev_a, la_n_a, la_prev_b, la_n_b = run_pts(0)
    # Re-run separately at each point
    def run_single(y):
        la, mu = get_coeffs(y, omega, l)
        dla = (get_coeffs(y+eps, omega, l)[0] - get_coeffs(y-eps, omega, l)[0])/(2*eps)
        dmu = (get_coeffs(y+eps, omega, l)[1] - get_coeffs(y-eps, omega, l)[1])/(2*eps)
        la_prev = la
        for k in range(N):
            la_n = la**2 + dla - mu
            mu_n = la*dmu - mu*dla + mu**2
            dla_n = 2*la*dla - dmu
            dmu_n = 2*mu*dmu
            mx = max(abs(la_n), abs(mu_n), abs(dla_n), abs(dmu_n), 1.0)
            sc = mx / 1e80 if mx > 1e80 else 1.0
            la_prev = la
            la, mu, dla, dmu = la_n/sc, mu_n/sc, dla_n/sc, dmu_n/sc
        return la_prev, la_n
    
    lap_a, lan_a = run_single(xa)
    lap_b, lan_b = run_single(xb)
    return abs(lap_a * lan_b - lan_a * lap_b)

# Compare formulations at reference
print("=" * 70)
print("REFERENCE OMEGA = 0.37367 - 0.08896j")
print("=" * 70)

for name, fn in [("RAW (c=2, scalar)", lambda x,w,l: get_coeffs_raw(x,w,2)),
                  ("DEHGHAN (c=6, grav)", lambda x,w,l: get_coeffs_dehghan(x,w,2))]:
    print(f"\n--- {name} ---")
    print(f"lambda_0 at xa=0.35: {fn(0.35, OMEGA_REF, 2)}")
    print(f"lambda_0 at xb=0.65: {fn(0.65, OMEGA_REF, 2)}")
    print(f"mu_0   at xa=0.35: {fn(0.35, OMEGA_REF, 2)[1]:.4e}")
    print(f"mu_0   at xb=0.65: {fn(0.65, OMEGA_REF, 2)[1]:.4e}")
    for N in [5, 8, 10, 15, 20]:
        C = aim_c(OMEGA_REF, 2, N, 0.35, 0.65, fn)
        W = aim_W_abs(OMEGA_REF, 2, N, 0.35, 0.65, fn)
        print(f"  N={N:2d}: C={C:.6e}, |W|={W:.6e}")

# Grid scans
print("\n" + "=" * 70)
print("GRID SCANS (30x15 points each)")
print("=" * 70)

for name, fn in [("RAW (c=2)", lambda x,w,l: get_coeffs_raw(x,w,2)),
                  ("DEHGHAN (c=6)", lambda x,w,l: get_coeffs_dehghan(x,w,2))]:
    print(f"\n--- {name}: C-indicator ---")
    best_c = 1e100
    best_w = None
    for wr in np.arange(0.25, 0.65, 0.02):
        for wi in np.arange(-0.18, 0.02, 0.01):
            w = wr + 1j*wi
            try:
                C = aim_c(w, 2, 10, 0.35, 0.65, fn)
            except:
                C = 1e100
            if C < best_c:
                best_c = C
                best_w = w
    if best_w:
        err = abs(best_w - OMEGA_REF)
        print(f"  Best C = {best_c:.6e} at omega = {best_w:.6f} (err={err:.6f})")

    print(f"\n--- {name}: |W|-indicator ---")
    best_W = 1e100
    best_w2 = None
    for wr in np.arange(0.25, 0.65, 0.02):
        for wi in np.arange(-0.18, 0.02, 0.01):
            w = wr + 1j*wi
            try:
                W = aim_W_abs(w, 2, 10, 0.35, 0.65, fn)
            except:
                W = 1e100
            if W < best_W:
                best_W = W
                best_w2 = w
    if best_w2:
        err = abs(best_w2 - OMEGA_REF)
        print(f"  Best |W| = {best_W:.6e} at omega = {best_w2:.6f} (err={err:.6f})")
