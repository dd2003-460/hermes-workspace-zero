#!/usr/bin/env python3
"""Reproduce the quick-check exactly to compare."""
import numpy as np

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

def rw_potential(r, l, c):
    return (1 - 2*M/r) * (l*(l+1)/r**2 - c*M/r**3)

def integrate_bc(bc, rs_t, w, l, c, N):
    if bc == 'in':
        rs_s = -50.0
        dr = (rs_t - rs_s) / N
        psi = np.exp(-1j * w * rs_s)
        dp = -1j * w * psi
    else:
        rs_s = 70.0
        dr = (rs_t - rs_s) / N
        psi = np.exp(1j * w * rs_s)
        dp = 1j * w * psi
    for _ in range(N):
        r = r_from_rstar(rs_s)
        V = rw_potential(r, l, c)
        k1 = dp
        k2 = -(w**2 - V) * psi
        r2 = r_from_rstar(rs_s + dr/2)
        V2 = rw_potential(r2, l, c)
        k3 = dp + 0.5*dr*k2
        k4 = -(w**2 - V2) * (psi + 0.5*dr*k1)
        r3 = r_from_rstar(rs_s + dr/2)
        V3 = rw_potential(r3, l, c)
        k5 = dp + 0.5*dr*k4
        k6 = -(w**2 - V3) * (psi + 0.5*dr*k3)
        r4 = r_from_rstar(rs_s + dr)
        V4 = rw_potential(r4, l, c)
        k7 = dp + dr*k6
        k8 = -(w**2 - V4) * (psi + dr*k5)
        psi += dr/6 * (k1 + 2*k3 + 2*k5 + k7)
        dp += dr/6 * (k2 + 2*k4 + 2*k6 + k8)
        if abs(psi) > 1e28:
            psi /= abs(psi) * 1e-27
            dp /= abs(psi) * 1e-27
    return psi, dp

def WN(w, l, c, N=500):
    a1, a2 = integrate_bc('in', 0.0, w, l, c, N)
    b1, b2 = integrate_bc('out', 0.0, w, l, c, N)
    W = a2*b1 - a1*b2
    return abs(W) / (abs(a1)+abs(a2)+abs(b1)+abs(b2)+1)

# Exactly reproduce quick-check
test_vals = [
    (complex(0.37367, -0.08896), "Berti ref"),
    (complex(0.48982, -0.04314), "Cardoso ref"),
    (complex(0.548, -0.071), "My scan minimum"),
]

print("c=6, l=2:")
for w, label in test_vals:
    for N in [500, 1000, 5000]:
        v = WN(w, 2, 6, N)
        print(f"  {label}, N={N:5d}: |W| = {v:.6e}")
    print()

# Compare with my Wronskian: standard determinant definition
def W_standard(w, l, c, N=500):
    a1, a2 = integrate_bc('in', 0.0, w, l, c, N)
    b1, b2 = integrate_bc('out', 0.0, w, l, c, N)
    W = abs(a2*b1 - a1*b2)
    # Standard normalization
    return W, a1, a2, b1, b2

print("Wronskian value and individual values for WN(Berti):")
w = complex(0.37367, -0.08896)
W, a1, a2, b1, b2 = W_standard(w, 2, 6, 500)
print(f"  a1 (in->0) = {a1}")
print(f"  a2 = {a2}")
print(f"  b1 (out->0) = {b1}")
print(f"  b2 = {b2}")
print(f"  W = {W}")
print(f"  denom = {abs(a1)+abs(a2)+abs(b1)+abs(b2)+1}")
print(f"  WN = {W/(abs(a1)+abs(a2)+abs(b1)+abs(b2)+1):.6e}")

# Check that b=0 or a=0 at eigenvalue (single-sided BC)
# If one side vanishes, W = 0 trivially
print(f"\n  Check if a2=0 or b2=0 at Berti:")
print(f"  |a2|/|a1| = {abs(a2)/abs(a1):.6f}")
print(f"  |b2|/|b1| = {abs(b2)/abs(b1):.6f}")
