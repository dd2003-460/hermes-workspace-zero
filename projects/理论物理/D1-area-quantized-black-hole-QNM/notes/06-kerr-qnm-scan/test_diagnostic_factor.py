#!/usr/bin/env python3
"""Compact diagnostic: factorized u-field method for QNM."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}

def rstar(r):
    return r + 2*M*np.log(r/(2*M)-1)

def r_from_rs(rs):
    t = rs/(2*M) - 1
    y = np.real(lambertw(np.exp(t)))
    r = 2*M*(1+y)
    for _ in range(30):
        if r <= 2*M: r = 2*M+1e-14; continue
        rc = r + 2*M*np.log(r/(2*M)-1)
        d = (rc - rs) / (r**2/(r-2*M)**2)
        if abs(d) < 1e-16: break
        r -= d
        if r <= 2*M: r = 2*M+1e-14
    return r

def rw_pot(r, l):
    f = 1-2*M/r
    return f*(l*(l+1)/r**2 - 6*M/r**3)

def raw_wronskian(omega, l, r_m, rs_h=-50, rs_inf=150):
    """Two-sided integration in r* coordinate."""
    def deriv(rs, Y):
        r = r_from_rs(rs)
        r = max(r, 2*M+1e-14)
        return [Y[1], -(omega**2 - rw_pot(r, l))*Y[0]]
    s1 = solve_ivp(lambda rs, Y: deriv(rs, Y), [rs_h, r_m], [1, -1j*omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2)
    s2 = solve_ivp(lambda rs, Y: deriv(rs, Y), [rs_inf, r_m], [1, +1j*omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2)
    if not (s1.success and s2.success):
        return None
    ph, dph = s1.y[:, -1]
    pf, dpf = s2.y[:, -1]
    return abs(ph*dpf - dph*pf) / (abs(ph)*abs(pf))

def u_field_wronskian(omega, l, r_m, rs_h=-50, rs_inf=150):
    """Factorized method: psi = exp(-i*w*r*) * u.
    u'' - 2i*w*u' - V*u = 0
    Horizon BC: u = constant => [1, 0]
    Infinity BC: u = exp(2i*w*r*) => du/dr* = 2i*w => [1, 2i*w]
    """
    def deriv(rs, Y):
        r = r_from_rs(rs)
        r = max(r, 2*M+1e-14)
        V = rw_pot(r, l)
        return [Y[1], 2j*omega*Y[1] + V*Y[0]]

    s1 = solve_ivp(lambda rs, Y: deriv(rs, Y), [rs_h, r_m], [1+0j, 0+0j],
                   rtol=1e-10, atol=1e-12, max_step=0.2)
    s2 = solve_ivp(lambda rs, Y: deriv(rs, Y), [rs_inf, r_m], [1+0j, 2j*omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2)
    if not (s1.success and s2.success):
        return None, None
    ph, dph = s1.y[:, -1]
    pf, dpf = s2.y[:, -1]
    # Now u is the quantity. Wronskian of u:
    W = abs(ph*dpf - dph*pf) / (abs(ph)*abs(pf))
    return W, (ph, pf)

def psi_logderiv(omega, l, rs):
    """Single-shot: integrate from horizon, return log-derivative dpsi/drs / psi."""
    def deriv(rs, Y):
        r = r_from_rs(rs)
        r = max(r, 2*M+1e-14)
        return [Y[1], -(omega**2 - rw_pot(r, l))*Y[0]]
    s = solve_ivp(lambda rs, Y: deriv(rs, Y), [rs, rs+1], [1, -1j*omega],
                  rtol=1e-10, atol=1e-12, max_step=0.05)
    if not s.success:
        return None
    psif = s.y[0, -1]
    dpsif = s.y[1, -1]
    return dpsif/psif

# ============================================================
print("="*70)
print("Factorized u-field vs Raw Wronskian comparison")
print("="*70)

for l in [2, 3]:
    ref = BERTI[l]
    print(f"\nl={l}, Berti: omega={ref.real:.5f}{ref.imag:.5f}i")

    # Method 1: raw Wronskian at different matching radii
    print("  Raw Wronskian (horizon->r_m, infinity->r_m):")
    for r_m in [-20, -10, 0, 10, 20, 30, 40, 50]:
        W = raw_wronskian(ref, l, r_m)
        if W is not None:
            print(f"    r_m={r_m:4d}: |W| = {W:.6e}")

    # Method 2: factorized Wronskian
    print("  Factorized u Wronskian:")
    for r_m in [-20, -10, 0, 10, 20, 30, 40, 50]:
        res = u_field_wronskian(ref, l, r_m)
        if res:
            W, (ph, pf) = res
            print(f"    r_m={r_m:4d}: |W| = {W:.6e}  |phi_h|={abs(ph):.4e}  |phi_i|={abs(pf):.4e}")

    # Method 3: u Wronskian at BERTI vs at previously found "minimum"
    if l == 2:
        candidates = [("Berti", ref), ("prev_min1", complex(0.454, -0.029)), ("prev_min2", complex(0.574, -0.039))]
    else:
        candidates = [("Berti", ref), ("prev_min", complex(0.691, -0.034))]

    print("  |u-W| at various omega, r_m=40:")
    for name, w in candidates:
        res = u_field_wronskian(w, l, 40)
        if res:
            W, (ph, pf) = res
            print(f"    {name}: |W| = {W:.6e}  ratio|ph/pf|={abs(ph)/abs(pf):.6f}")

    # Method 4: scanning with u-field Wronskian
    print(f"  Scan with u-field at r_m=30:")
    best = []
    for dr in np.linspace(-0.2, 0.3, 25):
        for di in np.linspace(-0.12, 0.02, 15):
            w = ref + complex(dr, di)
            res = u_field_wronskian(w, l, 30)
            if res:
                W, _ = res
                if W < 10:
                    best.append((W, w))
    best.sort()
    print("  Best 5:")
    for W, w in best[:5]:
        print(f"    omega={w.real:.5f}{w.imag:.5f}i: |W|={W:.6e}")

print("\n" + "="*70)
