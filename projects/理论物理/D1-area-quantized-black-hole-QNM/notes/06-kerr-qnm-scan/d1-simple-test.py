#!/usr/bin/env python3
"""Minimal diagnostic: test if Berti c=6 l=2 QNM works with different c values.
N=1000 per side, fast test.
"""
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

def V(r, l, c):
    return (1 - 2*M/r)*(l*(l+1)/r**2 - c*M/r**3)

def shoot(w, l, c, N=1000):
    rs_h = -60; rs_i = 80; rs_t = 0
    # Horizon side
    dr = (rs_t - rs_h)/N
    ph = np.exp(-1j*w*rs_h); dph = -1j*w*ph
    for i in range(N):
        rs = rs_h + i*dr
        r = r_from_rstar(rs); Vr = V(r,l,c)
        h = dr
        k1p=dph; k1d=-(w**2-Vr)*ph
        rm1=r_from_rstar(rs+h/2); Vm1=V(rm1,l,c)
        k2p=dph+h/2*k1d; k2d=-(w**2-Vm1)*(ph+h/2*k1p)
        k3p=dph+h/2*k2d; k3d=-(w**2-Vm1)*(ph+h/2*k2p)
        rm2=r_from_rstar(rs+h); Vm2=V(rm2,l,c)
        k4p=dph+h*k3d; k4d=-(w**2-Vm2)*(ph+h*k3p)
        ph += h/6*(k1p+2*k2p+2*k3p+k4p)
        dph += h/6*(k1d+2*k2d+2*k3d+k4d)
        mg = max(abs(ph),abs(dph),1e-290)
        if mg>1e100: ph/=mg; dph/=mg

    # Infinity side
    dr = (rs_i - rs_t)/N
    pi = np.exp(1j*w*rs_i); dpi = 1j*w*pi
    for i in range(N):
        rs = rs_i - i*dr
        r = r_from_rstar(rs); Vr = V(r,l,c)
        h = dr
        k1p=dpi; k1d=-(w**2-Vr)*pi
        rm1=r_from_rstar(rs-h/2); Vm1=V(rm1,l,c)
        k2p=dpi-h/2*k1d; k2d=-(w**2-Vm1)*(pi-h/2*k1p)
        k3p=dpi-h/2*k2d; k3d=-(w**2-Vm1)*(pi-h/2*k2p)
        rm2=r_from_rstar(rs-h); Vm2=V(rm2,l,c)
        k4p=dpi-h*k3d; k4d=-(w**2-Vm2)*(pi-h*k3p)
        pi -= h/6*(k1p+2*k2p+2*k3p+k4p)
        dpi -= h/6*(k1d+2*k2d+2*k3d+k4d)
        mg = max(abs(pi),abs(dpi),1e-290)
        if mg>1e100: pi/=mg; dpi/=mg

    W = abs(dph*pi - ph*dpi)/(abs(ph)+abs(dph)+abs(pi)+abs(dpi)+1)
    return W

# Just test the key points for c=6,l=2
print("c=6, l=2:")
candidates = [
    (0.37367, -0.08896, "Berti"),
    (0.548, -0.071, "PrevMin"),
    (0.54826, -0.07133, "PrevRefined"),
]
for re, im, label in candidates:
    w = complex(re, im)
    v = shoot(w, 2, 6, 5000)
    print(f"  omega={re:.5f}+{im:.5f}i ({label}): |W|/norm={v:.3e}")

# Test c=2, l=2 with scalar Berti
print("\nc=2, l=2 (scalar):")
w = complex(0.27204, -0.03150)
v = shoot(w, 2, 2, 5000)
print(f"  Berti scalar: {v:.3e}")

# Test c=0, l=2
print("\nc=0, l=2:")
w = complex(0.27204, -0.03150)
v = shoot(w, 2, 0, 5000)
print(f"  Berti scalar: {v:.3e}")

print("\nc=6, l=3:")
for re, im, label in [
    (0.59108, -0.05902, "Berti"),
    (0.523, -0.063, "PrevMin"),
]:
    w = complex(re, im)
    v = shoot(w, 3, 6, 5000)
    print(f"  omega={re:.5f}+{im:.5f}i ({label}): |W|/norm={v:.3e}")
