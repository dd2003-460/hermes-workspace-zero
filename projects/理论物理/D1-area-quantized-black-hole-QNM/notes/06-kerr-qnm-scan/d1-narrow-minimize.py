#!/usr/bin/env python3
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

def integrate_side(w, l, c, rs_start, rs_end, N):
    dr = (rs_end - rs_start) / N
    bc = -1j*w if rs_start < 0 else 1j*w
    ps = np.exp(bc*rs_start)
    dps = bc * ps
    for i in range(N):
        rs = rs_start + i*dr
        r = r_from_rstar(rs); Vr = V(r, l, c); h = dr
        k1y, k1d = dps, -(w**2-Vr)*ps
        rm = r_from_rstar(rs+h/2); Vm = V(rm, l, c)
        k2y = dps+h/2*k1d; k2d = -(w**2-Vm)*(ps+h/2*k1y)
        k3y = dps+h/2*k2d; k3d = -(w**2-Vm)*(ps+h/2*k2y)
        re = r_from_rstar(rs+h); Ve = V(re, l, c)
        k4y = dps+h*k3d; k4d = -(w**2-Ve)*(ps+h*k3y)
        ps += h/6*(k1y+2*k2y+2*k3y+k4y)
        dps += h/6*(k1d+2*k2d+2*k3d+k4d)
    return ps, dps

def W(w, l, c, N):
    ps_h, dph = integrate_side(w, l, c, -50.0, 0.0, N)
    ps_i, dpi = integrate_side(w, l, c, 80.0, 0.0, N)
    return abs(dph*ps_i - ps_h*dpi)

def Wn(w, l, c, N):
    ps_h, dph = integrate_side(w, l, c, -50.0, 0.0, N)
    ps_i, dpi = integrate_side(w, l, c, 80.0, 0.0, N)
    W = abs(dph*ps_i - ps_h*dpi)
    return W / (abs(ps_h)+abs(dph)+abs(ps_i)+abs(dpi)+1)

def mm(w, l, c, N):
    ps_h, dph = integrate_side(w, l, c, -50.0, 0.0, N)
    ps_i, dpi = integrate_side(w, l, c, 80.0, 0.0, N)
    ln_h = dph/ps_h; ln_i = dpi/ps_i
    return abs(ln_h - ln_i) / (abs(ln_h)+abs(ln_i)+1)

print("="*60)
print("Wronskian minimization (Nelder-Mead)")
print("="*60)

for (l, c, name, w0) in [
    (2, 6, "c=6, l=2", [0.374, -0.089]),
    (2, 2, "c=2, l=2", [0.264, -0.024]),
    (3, 6, "c=6, l=3", [0.591, -0.059]),
]:
    res = minimize(lambda x, l=l, c=c: W(complex(x[0], x[1]), l, c, 2000),
                   x0=w0, method='Nelder-Mead',
                   options={'xatol':1e-8, 'fatol':1e-14, 'maxiter':3000, 'adaptive':True})
    wm = complex(res.x[0], res.x[1])
    print(f"\n{name}:")
    print(f"  omega = {wm.real:.8f} + ({wm.imag:.8f})i")
    print(f"  |W| = {res.fun:.3e}, |W|/norm = {Wn(wm, l, c, 2000):.6e}")

print("\n\nCombined criterion minimization (W + log-derivative mismatch)")
for (l, c, name, w0) in [
    (2, 6, "c=6, l=2 from Berti", [0.374, -0.089]),
    (2, 6, "c=6, l=2 from prev W", [0.548, -0.071]),
    (2, 6, "c=6, l=2 from prev logd", [0.665, -0.070]),
]:
    res = minimize(lambda x, l=l, c=c: W(complex(x[0], x[1]), l, c, 2000) + 100*mm(complex(x[0], x[1]), l, c, 2000),
                   x0=w0, method='Nelder-Mead',
                   options={'xatol':1e-8, 'fatol':1e-14, 'maxiter':3000, 'adaptive':True})
    wm = complex(res.x[0], res.x[1])
    print(f"\n{name}:")
    print(f"  omega = {wm.real:.8f} + ({wm.imag:.8f})i")
    print(f"  |W| = {W(wm, l, c, 2000):.3e}, |W|/norm = {Wn(wm, l, c, 2000):.6e}, mm = {mm(wm, l, c, 2000):.6e}")

print("\n\n=== Direct verification at candidate eigenvalues ===")
candidates = {
    "Berti l=2": (0.373673, -0.088962),
    "Found min W": (0.548261, -0.071329),
    "Found min mm": (0.665, -0.070),
}
for name, (re_w, im_w) in candidates.items():
    w = complex(re_w, im_w)
    ps_h, dph = integrate_side(w, 2, 6, -50.0, 0.0, 5000)
    ps_i, dpi = integrate_side(w, 2, 6, 80.0, 0.0, 5000)
    ln_h = dph/ps_h; ln_i = dpi/ps_i
    Wval = abs(dph*ps_i - ps_h*dpi)
    Wnval = Wval/(abs(ps_h)+abs(dph)+abs(ps_i)+abs(dpi)+1)
    print(f"\n{name}: omega = {re_w:.6f}+{im_w:.6f}i")
    print(f"  |W| = {Wval:.6e}, |W|/norm = {Wnval:.6e}")
    print(f"  lnH = {ln_h.real:.6f}+{ln_h.imag:.6f}i")
    print(f"  lnI = {ln_i.real:.6f}+{ln_i.imag:.6f}i")
    print(f"  |lnH-lnI| = {abs(ln_h-ln_i):.6e}")
    print(f"  |ps_h|={abs(ps_h):.3e}, |ps_i|={abs(ps_i):.3e}")

print("\nDone")
