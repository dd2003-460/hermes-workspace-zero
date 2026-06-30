#!/usr/bin/env python3
"""Log-derivative matching test + coarse optimization."""
import numpy as np
from scipy.optimize import minimize

M = 1.0

def r_from_rstar(rs):
    r = max(rs * 0.5 + M, 2.5)
    for _ in range(30):
        f = r + 2*M*np.log(r/(2*M) - 1) - rs
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15: break
        r = r - f/df
        if r <= 2.0*M: r = 2.0*M + 1e-10
        if abs(f) < 1e-14: break
    return max(r, 2.0001)

def V(r, l, c):
    return (1 - 2*M/r)*(l*(l+1)/r**2 - c*M/r**3)

def integrate_logderiv(side, w, l, c, N):
    if side == 'in':
        rs_start, rs_end = -60.0, 0.0
        lnpsi_start = -1j*w
    else:
        rs_start, rs_end = 80.0, 0.0
        lnpsi_start = 1j*w

    dr = (rs_end - rs_start) / N
    lnpsi = lnpsi_start
    for i in range(N):
        rs = rs_start + i*dr
        r = r_from_rstar(rs)
        V_r = V(r, l, c)

        k1 = -(w**2 - V_r) - lnpsi**2
        rs_m = rs + dr/2; r_m = r_from_rstar(rs_m); V_m = V(r_m, l, c)
        k2 = -(w**2 - V_m) - (lnpsi + dr/2*k1)**2
        k3 = k2
        r_e = r_from_rstar(rs + dr); V_e = V(r_e, l, c)
        k4 = -(w**2 - V_e) - (lnpsi + dr*k3)**2

        lnpsi += dr/6*(k1 + 2*k2 + 2*k3 + k4)
        if abs(lnpsi) > 1e40:
            return 1e50

    return lnpsi

def mismatch(w, l, c, N):
    ln_h = integrate_logderiv('in', w, l, c, N)
    ln_i = integrate_logderiv('out', w, l, c, N)
    if abs(ln_h) > 1e40 or abs(ln_i) > 1e40:
        return 1e20
    mm = abs(ln_h - ln_i)
    return mm / (abs(ln_h) + abs(ln_i) + 1)

# Test: scan for c=6, l=2 at N=1000
print("c=6, l=2 scan (N=1000):")
best_mm = 1e20; best_w = None
for re in np.arange(0.2, 0.8, 0.01):
    for im in np.arange(-0.15, -0.01, 0.002):
        w = complex(re, im)
        mm = mismatch(w, 2, 6, 1000)
        if mm < best_mm:
            best_mm = mm; best_w = w
print(f"  Best: omega = {best_w.real:.3f}+{best_w.imag:.3f}i  mm = {best_mm:.6e}")
print(f"  Betti:     0.37367 - 0.08896i  mm = {mismatch(complex(0.37367,-0.08896),2,6,1000):.6e}")

# Convergence at best found
for N_test in [1000, 2000, 5000, 10000]:
    mm = mismatch(best_w, 2, 6, N_test)
    mm_b = mismatch(complex(0.37367, -0.08896), 2, 6, N_test)
    print(f"  N={N_test:5d}:  best={mm:.6e}  Betti={mm_b:.6e}")

# Same for c=6, l=3
print("\nc=6, l=3 scan (N=1000):")
best_mm3 = 1e20; best_w3 = None
for re in np.arange(0.35, 0.8, 0.01):
    for im in np.arange(-0.12, -0.01, 0.002):
        w = complex(re, im)
        mm = mismatch(w, 3, 6, 1000)
        if mm < best_mm3:
            best_mm3 = mm; best_w3 = w
print(f"  Best: omega = {best_w3.real:.3f}+{best_w3.imag:.3f}i  mm = {best_mm3:.6e}")
print(f"  Betti:     0.59108 - 0.05902i  mm = {mismatch(complex(0.59108,-0.05902),3,6,1000):.6e}")

# Convergence at best found
for N_test in [1000, 2000, 5000]:
    mm = mismatch(best_w3, 3, 6, N_test)
    mm_b = mismatch(complex(0.59108, -0.05902), 3, 6, N_test)
    print(f"  N={N_test:5d}:  best={mm:.6e}  Betti={mm_b:.6e}")

print("\nDone")
