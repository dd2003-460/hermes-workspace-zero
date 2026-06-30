#!/usr/bin/env python3
"""Quick convergence check for c=6, l=2 QNM with different integration settings."""
import numpy as np

M = 1.0

def r_from_rstar(rs):
    r = max(rs * 0.5 + M, 2.5)
    for _ in range(30):
        f = r + 2*M*np.log(r/(2*M) - 1) - rs
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15:
            break
        r = r - f/df
        if r <= 2.0*M:
            r = 2.0*M + 1e-10
        if abs(f) < 1e-14:
            break
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

# Test convergence for c=6, l=2
test_omegas = [
    (complex(0.37367, -0.08896), "Berti ref"),
    (complex(0.48982, -0.04314), "Cardoso ref (wrong)"),
    (complex(0.548, -0.071), "My scan minimum"),
    (complex(0.520, -0.060), "Alternative candidate"),
    (complex(0.490, -0.065), "Near Cardoso"),
]

for w, label in test_omegas:
    vals = []
    for N in [500, 1000, 2000, 5000]:
        v = WN(w, 2, 6, N)
        vals.append((N, v))
        print(f"  {label} ({w.real:.5f}+{w.imag:.5f}i), N={N:5d}: |W|/norm = {v:.6e}")

print("\n--- Also test l=3 ---")
for w, label in [
    (complex(0.59108, -0.05902), "Berti ref"),
    (complex(0.520, -0.060), "My scan minimum"),
    (complex(0.600, -0.050), "Alternative l=3"),
]:
    for N in [500, 1000, 2000, 5000]:
        v = WN(w, 3, 6, N)
        print(f"  {label}, N={N:5d}: |W|/norm = {v:.6e}")
    print()

# Test: c=2, l=2
print("--- c=2, l=2 ---")
for w, label in [
    (complex(0.37367, -0.08896), "Berti ref"),
    (complex(0.27204, -0.03150), "Scalar ref"),
]:
    for N in [500, 1000, 2000]:
        v = WN(w, 2, 2, N)
        print(f"  {label}, N={N:5d}: |W|/norm = {v:.6e}")

print("\nDone")
