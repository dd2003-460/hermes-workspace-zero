#!/usr/bin/env python3
"""Quick diagnostic: test Berti eigenvalues with various c values."""
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

def shoot(v_test, w, l, c, N=5000):
    """Shoot from both sides, return Wronskian/norm at v_test in r*."""
    # From horizon
    rs_h_start = -60.0
    dr_h = (v_test - rs_h_start) / N
    psi_h = np.exp(-1j*w*rs_h_start)
    dpsi_h = -1j*w*psi_h

    for i in range(N):
        rs = rs_h_start + i*dr_h
        r = r_from_rstar(rs)
        V = rw_potential(r, l, c)
        h = dr_h
        k1p, k1d = dpsi_h, -(w**2-V)*psi_h
        r1 = r_from_rstar(rs+h/2); V1 = rw_potential(r1, l, c)
        k2p = dpsi_h + h/2*k1d
        k2d = -(w**2-V1)*(psi_h + h/2*k1p)
        k3p = dpsi_h + h/2*k2d
        k3d = -(w**2-V1)*(psi_h + h/2*k2p)
        r2 = r_from_rstar(rs+h); V2 = rw_potential(r2, l, c)
        k4p = dpsi_h + h*k3d
        k4d = -(w**2-V2)*(psi_h + h*k3p)
        psi_h += h/6*(k1p+2*k2p+2*k3p+k4p)
        dpsi_h += h/6*(k1d+2*k2d+2*k3d+k4d)
        mg = max(abs(psi_h), abs(dpsi_h), 1e-290)
        if mg > 1e100:
            psi_h /= mg; dpsi_h /= mg

    # From infinity
    rs_i_start = 80.0
    dr_i = (rs_i_start - v_test) / N
    psi_i = np.exp(1j*w*rs_i_start)
    dpsi_i = 1j*w*psi_i

    for i in range(N):
        rs = rs_i_start - i*dr_i
        r = r_from_rstar(rs)
        V = rw_potential(r, l, c)
        h = dr_i
        k1p, k1d = dpsi_i, -(w**2-V)*psi_i
        r1 = r_from_rstar(rs-h/2); V1 = rw_potential(r1, l, c)
        k2p = dpsi_i - h/2*k1d
        k2d = -(w**2-V1)*(psi_i - h/2*k1p)
        k3p = dpsi_i - h/2*k2d
        k3d = -(w**2-V1)*(psi_i - h/2*k2p)
        r2 = r_from_rstar(rs-h); V2 = rw_potential(r2, l, c)
        k4p = dpsi_i - h*k3d
        k4d = -(w**2-V2)*(psi_i - h*k3p)
        psi_i -= h/6*(k1p+2*k2p+2*k3p+k4p)
        dpsi_i -= h/6*(k1d+2*k2d+2*k3d+k4d)
        mg = max(abs(psi_i), abs(dpsi_i), 1e-290)
        if mg > 1e100:
            psi_i /= mg; dpsi_i /= mg

    W = dpsi_h*psi_i - psi_h*dpsi_i
    return abs(W)/(abs(psi_h)+abs(dpsi_h)+abs(psi_i)+abs(dpsi_i)+1)

# Fast check at key values
print("Fast check: N=5000 per side")
for (l, c, label) in [(2,6,"c=6,l=2 GR"), (3,6,"c=6,l=3 GR"), (2,2,"c=2,l=2 scal")]:
    print(f"\n--- {label} ---")
    # Test Berti reference
    if c == 6:
        beti = (0.37367, -0.08896) if l == 2 else (0.59108, -0.05902)
    else:
        beti = (0.27204, -0.03150) if l == 2 else None
    if beti:
        w_b = complex(*beti)
        vb = shoot(0.0, w_b, l, c, 5000)
        print(f"  Berti ({beti[0]:.5f}+{beti[1]:.5f}i): {vb:.3e}")

    # Test previous minimum
    w_p = complex(0.548, -0.071) if l==2 else complex(0.523, -0.063)
    vp = shoot(0.0, w_p, l, c, 5000)
    print(f"  PrevMin({w_p.real:.3f}+{w_p.imag:.3f}i): {vp:.3e}")

# Now test if c=0 or c=2 gives Berti for l=2 (scalar case)
print("\n--- c=0, l=2 (pure 1/r^2 potential) ---")
vb0 = shoot(0.0, complex(0.27204, -0.03150), 2, 0, 5000)
print(f"  Scalar Berti: {vb0:.3e}")

print("\n--- Exploring c-values for l=2 ---")
for c_val in [0, 2, 6, 8, 12]:
    # Quick grid search for each c
    best_w = None
    best_v = 1e10
    for re in np.arange(0.15, 0.85, 0.02):
        for im in np.arange(-0.15, -0.01, 0.005):
            w = complex(re, im)
            v = shoot(0.0, w, 2, c_val, 2000)
            if v < best_v:
                best_v = v
                best_w = w
    print(f"  c={c_val:2d}: best omega = {best_w.real:.3f}+{best_w.imag:.3f}i  |W|/norm = {best_v:.3e}")
