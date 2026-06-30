#!/usr/bin/env python3
"""
Fine-grained scan near Berti's values to check if the eigenvalue
actually exists near Berti, or if it's far away in the complex plane.
"""
import numpy as np
import json

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

def shoot_logderiv(w, l, c, N_side, origin, direction):
    if direction > 0:
        rs_start, rs_end = origin, 0.0
        ps = np.exp(-1j*w*rs_start)
        dps = -1j*w*ps
    else:
        rs_start, rs_end = origin, 0.0
        ps = np.exp(1j*w*rs_start)
        dps = 1j*w*ps
    
    dr = (rs_end - rs_start) / N_side
    ps_h, dps_h = ps, dps
    
    for i in range(N_side):
        rs = rs_start + i*dr
        r = r_from_rstar(rs)
        Vr = V(r, l, c)
        h = dr
        
        k1_y, k1_d = dps_h, -(w**2 - Vr)*ps_h
        rm = r_from_rstar(rs+h/2); Vm = V(rm, l, c)
        k2_y = dps_h + h/2*k1_d; k2_d = -(w**2 - Vm)*(ps_h + h/2*k1_y)
        k3_y = dps_h + h/2*k2_d; k3_d = -(w**2 - Vm)*(ps_h + h/2*k2_y)
        re = r_from_rstar(rs+h); Ve = V(re, l, c)
        k4_y = dps_h + h*k3_d; k4_d = -(w**2 - Ve)*(ps_h + h*k3_y)
        
        ps_h += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps_h += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)
        
        mag = max(abs(ps_h), abs(dps_h), 1e-300)
        if mag > 1e100:
            ps_h /= mag; dps_h /= mag
    
    return dps_h / ps_h if abs(ps_h) > 1e-300 else 1e50

def logderiv_mismatch(w, l, c, N_side=1000):
    try:
        ln_h = shoot_logderiv(w, l, c, N_side, -50.0, +1)
        ln_i = shoot_logderiv(w, l, c, N_side, 80.0, -1)
        if abs(ln_h) > 1e30 or abs(ln_i) > 1e30:
            return 1e20, None, None
        mm = abs(ln_h - ln_i) / (abs(ln_h) + abs(ln_i) + 1)
        return mm, ln_h, ln_i
    except:
        return 1e20, None, None

print("="*70)
print("Fine scan near Berti values with log-derivative matching")
print("="*70)

# Try multiple candidate values from prior work
candidates = {
    "Berti l=2": (0.37367, -0.08896),
    "Berti l=3": (0.59108, -0.05902),
    "Berti scalar": (0.27204, -0.03150),
    "My prev (Wronskian)": (0.548, -0.071),
    "My prev (log-deriv)": (0.665, -0.070),
}

N_test = 2000
for name, (re_w, im_w) in candidates.items():
    w = complex(re_w, im_w)
    mm, lnH, lnI = logderiv_mismatch(w, 2, 6, N_test)
    lnH0, lnI0 = lnH or 0, lnI or 0
    print(f"\n{name}: omega={re_w:.5f}+{im_w:.5f}i (c=6,l=2)")
    print(f"  |lnH-lnI|_norm = {mm:.6e}")
    if lnH and lnI:
        print(f"  lnH = {lnH.real:.6f}+{lnH.imag:.6f}i, lnI = {lnI.real:.6f}+{lnI.imag:.6f}i")
        print(f"  delta_real = {(lnH-lnI).real:.6f}, delta_imag = {(lnH-lnI).imag:.6f}")

# Fine 2D scan around both Berti and "my" values
print("\n\n=== Fine 2D scan c=6, l=2 around Berti (real 0.30-0.50, imag -0.12 to -0.02) ===")
best = (1e20, None)
for re in np.arange(0.28, 0.55, 0.005):
    for im in np.arange(-0.13, -0.01, 0.002):
        w = complex(re, im)
        mm, _, _ = logderiv_mismatch(w, 2, 6, N_test)
        if mm < best[0]:
            best = (mm, w)
print(f"  Best: omega = {best[1].real:.3f}+{best[1].imag:.3f}i, mm = {best[0]:.6e}")

# Fine scan around "my" value  
print("\n=== Fine 2D scan c=6, l=2 around 'my value' (real 0.60-0.80, imag -0.10 to -0.04) ===")
best2 = (1e20, None)
for re in np.arange(0.58, 0.85, 0.005):
    for im in np.arange(-0.12, -0.02, 0.002):
        w = complex(re, im)
        mm, _, _ = logderiv_mismatch(w, 2, 6, N_test)
        if mm < best2[0]:
            best2 = (mm, w)
print(f"  Best: omega = {best2[1].real:.3f}+{best2[1].imag:.3f}i, mm = {best2[0]:.6e}")

# Same for scalar case
print("\n=== Fine 2D scan c=2, l=2 (real 0.20-0.50, imag -0.10 to -0.01) ===")
best3 = (1e20, None)
for re in np.arange(0.18, 0.55, 0.005):
    for im in np.arange(-0.12, -0.005, 0.002):
        w = complex(re, im)
        mm, _, _ = logderiv_mismatch(w, 2, 2, N_test)
        if mm < best3[0]:
            best3 = (mm, w)
print(f"  Best: omega = {best3[1].real:.3f}+{best3[1].imag:.3f}i, mm = {best3[0]:.6e}")

print("\nDone")
