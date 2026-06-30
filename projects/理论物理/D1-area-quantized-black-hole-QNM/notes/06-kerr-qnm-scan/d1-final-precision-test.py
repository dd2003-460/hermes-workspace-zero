#!/usr/bin/env python3
"""
Final precision test:
1. Use log-derivative matching to find eigenvalues (more stable than Wronskian)
2. Test with very high N for precise eigenvalue determination
3. Compare with Betti values
"""
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
    """Integrate d(ln psi)/dr* = psi'/psi, starting from BC.
    side='in': horizon -> rs=0, start with dpsi/psi = -iw
    side='out': infinity -> rs=0, start with dpsi/psi = +iw
    Returns the logarithmic derivative at rs=0.
    """
    if side == 'in':
        rs_start = -60.0
        rs_end = 0.0
        lnpsi_start = -1j*w  # psi ~ exp(-iwrs) => dlnpsi/dr* = -iw
    else:
        rs_start = 80.0
        rs_end = 0.0
        lnpsi_start = 1j*w   # psi ~ exp(+iwrs) => dlnpsi/dr* = +iw

    # Convert lnpsi_start: psi'/psi = lnpsi => psi''/psi = d(lnpsi)/dr* + (lnpsi)^2
    # d^2psi/dr*2 + (w^2 - V)psi = 0 => d(lnpsi)/dr* = (psi'' - (psi')^2/psi)/psi
    # = -(w^2 - V) - (lnpsi)^2
    # So: d(lnpsi)/dr* = -(w^2 - V) - (lnpsi)^2

    dr = (rs_end - rs_start) / N
    lnpsi = lnpsi_start
    for i in range(N):
        rs = rs_start + i*dr
        r = r_from_rstar(rs)
        V_r = V(r, l, c)

        # d(lnpsi)/dr* = -(w^2 - V) - (lnpsi)^2
        k1 = -(w**2 - V_r) - lnpsi**2

        rs_mid = rs + dr/2
        r_mid = r_from_rstar(rs_mid)
        V_mid = V(r_mid, l, c)
        k2 = -(w**2 - V_mid) - (lnpsi + dr/2*k1)**2

        k3 = -(w**2 - V_mid) - (lnpsi + dr/2*k2)**2

        rs_end_i = rs + dr
        r_end = r_from_rstar(rs_end_i)
        V_end = V(r_end, l, c)
        k4 = -(w**2 - V_end) - (lnpsi + dr*k3)**2

        lnpsi += dr/6*(k1 + 2*k2 + 2*k3 + k4)

        # Remedy instability: if lnpsi grows too large,
        # we need to avoid divergence. But this can happen for sub-eigenvalues.
        if abs(lnpsi) > 1e50:
            break

    return lnpsi

def logderiv_mismatch(w, l, c, N):
    """At eigenvalue, logderiv from both sides should match."""
    ln_h = integrate_logderiv('in', w, l, c, N)
    ln_i = integrate_logderiv('out', w, l, c, N)

    # The mismatch:
    if abs(ln_h) > 1e40 or abs(ln_i) > 1e40:
        return 1e20

    mismatch = abs(ln_h - ln_i)
    # Scale by typical amplitude to avoid scale issues
    scale = abs(ln_h) + abs(ln_i) + 1
    return mismatch / scale

def full_wronskian(w, l, c, N=10000):
    """Standard Wronskian with proper scaling."""
    return logderiv_mismatch(w, l, c, N)

print("=" * 60)
print("Log-derivative matching for QNM eigenvalues")
print("=" * 60)

# Test at Betti reference for c=6, l=2
w_b = complex(0.37367, -0.08896)
w_m = complex(0.548, -0.071)

print(f"\nc=6, l=2:")
print(f"  Betti:     {w_b}")
print(f"  Previous:  {w_m}")
for N_test in [500, 1000, 2000, 5000, 10000]:
    m_b = logderiv_mismatch(w_b, 2, 6, N_test)
    m_m = logderiv_mismatch(w_m, 2, 6, N_test)
    print(f"  N={N_test:5d}:  mismatch(Betti)     = {m_b:.6e}")
    print(f"                 mismatch(Previous)  = {m_m:.6e}")

# Scan around the found value with finer resolution
print("\nFine scan around c=6, l=2 minimum:")
best = None
for re in np.arange(0.45, 0.65, 0.01):
    for im in np.arange(-0.10, -0.03, 0.005):
        w = complex(re, im)
        m = logderiv_mismatch(w, 2, 6, 1000)
        if m < 0.1:
            if best is None or m < best[1]:
                best = (w, m)

if best:
    print(f"  Best: omega = {best[0].real:.3f}+{best[0].imag:.3f}i  mismatch = {best[1]:.6e}")

# Same for l=3
print(f"\nc=6, l=3:")
w_b3 = complex(0.59108, -0.05902)
w_m3 = complex(0.523, -0.063)
for N_test in [500, 1000, 2000, 5000]:
    m_b3 = logderiv_mismatch(w_b3, 3, 6, N_test)
    m_m3 = logderiv_mismatch(w_m3, 3, 6, N_test)
    print(f"  N={N_test:5d}:  mismatch(Betti)     = {m_b3:.6e}")
    print(f"                 mismatch(Previous)  = {m_m3:.6e}")

# Nelder-Mead refinement for c=6, l=2
print("\nNelder-Mead refinement (c=6, l=2):")
obj = lambda x: full_wronskian(complex(x[0], x[1]), 2, 6, 5000)
r = minimize(obj, [0.548, -0.071], method='Nelder-Mead',
             options={'xatol': 1e-10, 'fatol': 1e-15, 'maxiter': 10000})
w_found = complex(r.x[0], r.x[1])
print(f"  omega = {w_found.real:.10f} + {w_found.imag:.10f}i")
print(f"  mismatch = {r.fun:.3e}")
print(f"  Berti:      0.37367 - 0.08896i")
print(f"  diff:       {w_found.real - 0.37367:.6f} + {w_found.imag + 0.08896:.6f}i")

# Same for l=3
print("\nNelder-Mead refinement (c=6, l=3):")
obj3 = lambda x: full_wronskian(complex(x[0], x[1]), 3, 6, 5000)
r3 = minimize(obj3, [0.523, -0.063], method='Nelder-Mead',
              options={'xatol': 1e-10, 'fatol': 1e-15, 'maxiter': 10000})
w_found3 = complex(r3.x[0], r3.x[1])
print(f"  omega = {w_found3.real:.10f} + {w_found3.imag:.10f}i")
print(f"  mismatch = {r3.fun:.3e}")
print(f"  Berti:      0.59108 - 0.05902i")
print(f"  diff:       {w_found3.real - 0.59108:.6f} + {w_found3.imag + 0.05902:.6f}i")

print("\nDone")
