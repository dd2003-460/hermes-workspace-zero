#!/usr/bin/env python3
"""Quick Riccati diagnostic at Berti value - single test."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0
l = 2
omega = complex(0.37367, -0.08896)  # Berti

def r_from_rs(rs):
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(40):
        if r <= 2 * M: r = 2 * M + 1e-14; continue
        rs_calc = r + 2 * M * np.log(r / (2 * M) - 1.0)
        drstar_dr = r ** 2 / (r - 2 * M) ** 2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-16: break
        r -= dr
        if r <= 2 * M: r = 2 * M + 1e-14
    return r

def V(r):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)

print("=" * 60)
print("Riccati diagnostic for l=2 at Berti (0.37367-0.08896i)")
print("=" * 60)

# Potential and fixed point structure at key points
print("\nPotential and fixed points:")
for rs_t in [-50, -30, -20, -10, 0, 10, 20, 40, 80]:
    r = r_from_rs(rs_t)
    Vv = V(r)
    delta = Vv - omega ** 2
    try:
        sqrt_fp = np.sqrt(delta)
    except:
        sqrt_fp = np.sqrt(complex(Vv.real - (omega**2).real, Vv.imag - (omega**2).imag))
    print(f"  rs*={rs_t:4d}: r={r:8.4f}, V={Vv.real:8.4f}+{Vv.imag:.4f}j, delta=V-w²={delta.real:8.4f}+{delta.imag:.4f}j, sqrt={sqrt_fp.real:8.4f}+{sqrt_fp.imag:.4f}j")

# Integrate Riccati from horizon (ingoing: f(-50) = -i*omega)
print(f"\nRiccati f_h from horizon f(-50)=-i*w = {-1j*omega}")
def riccati_rhs(rs, f):
    r = r_from_rs(rs)
    r = max(r, 2*M + 1e-14)
    Vv = V(r)
    delta = Vv - omega ** 2
    return [-(omega ** 2 - Vv) - f[0] ** 2]

# Integrate in small steps
rs_h = -50.0
rs_inf = 200.0

# Integrate from horizon outward
s_h = solve_ivp(riccati_rhs, [rs_h, 0.0], [-1j*omega],
               rtol=1e-14, atol=1e-16, max_step=0.2)
fh_0 = s_h.y[0, -1]
print(f"  f_h(0) = {fh_0}")

# Integrate from infinity backward (outgoing: f(200) = +i*omega)
s_ipos = solve_ivp(riccati_rhs, [0.0, rs_inf], [+1j*omega],
                  rtol=1e-14, atol=1e-16, max_step=0.2)
fi_pos = s_ipos.y[0, 0]  # value at rs=0
print(f"  f_i(0) [BC=+i*w] = {fi_pos}")
print(f"  |f_h - f_i| = {abs(fh_0 - fi_pos)}")

# Also with BC = -i*omega
s_ineg = solve_ivp(riccati_rhs, [0.0, rs_inf], [-1j*omega],
                  rtol=1e-14, atol=1e-16, max_step=0.2)
fi_neg = s_ineg.y[0, 0]  # value at rs=0
print(f"  f_i(0) [BC=-i*w] = {fi_neg}")
print(f"  |f_h - f_i| = {abs(fh_0 - fi_neg)}")

# Check: what does f_h look like along the way?
print(f"\nf_h evolution (horizon -> rs*=0):")
for rs_t in [-50, -40, -30, -20, -10, 0]:
    val = s_h.sol(rs_t)[0]
    r_t = r_from_rs(rs_t)
    Vv = V(r_t)
    print(f"  rs*={rs_t:4d}: f_h={val.real:12.8f}+{val.imag:12.8f}j, V={Vv.real:8.4f}+{Vv.imag:.6f}j")

# Check: what does f_i (from infinity with +i*omega) look like along the way?
print(f"\nf_i evolution from infinity [BC=+i*w]:")
# integrate backward means: rs goes from 200 down to 0
# solve_ivp handles this automatically
s_ipos2 = solve_ivp(riccati_rhs, [rs_inf, -30], [+1j*omega],
                   rtol=1e-14, atol=1e-16, max_step=0.2)
for rs_t in [200, 150, 100, 80, 60, 40, 20, 0]:
    val = s_ipos2.sol(rs_t)[0]
    r_t = r_from_rs(rs_t)
    Vv = V(r_t)
    print(f"  rs*={rs_t:4d}: f_i={val.real:12.8f}+{val.imag:12.8f}j, V={Vv.real:8.4f}+{Vv.imag:.6f}j")

# Now the crucial test: try DIFFERENT omega values and see where they match
print(f"\nSearching for minimum |f_h(0) - f_i(0)| at different omega:")
errs = []
for dr in np.linspace(-0.15, 0.15, 13):
    for di in np.linspace(-0.05, 0.05, 13):
        w = complex(0.37367 + dr, -0.08896 + di)
        # Horizon
        sh = solve_ivp(lambda rs, f: [-(w**2 - V(r_from_rs(rs)))- f[0]**2],
                      [-50, 0], [-1j*w], rtol=1e-12, atol=1e-14, max_step=0.2)
        # Infinity (outgoing: f(200) = +i*w)
        si = solve_ivp(lambda rs, f: [-(w**2 - V(r_from_rs(rs))) - f[0]**2],
                      [0, 200], [+1j*w], rtol=1e-12, atol=1e-14, max_step=0.2)
        if sh.success and si.success:
            err = abs(sh.y[0,-1] - si.y[0,0])
            errs.append((err, w))
errs.sort()
print(f"  Best: w={errs[0][1].real:.5f}{errs[0][1].imag:.5f}i, err={errs[0][0]:.6e}")
for i in range(1, 5):
    if i < len(errs):
        print(f"    {i+1}. w={errs[i][1].real:.5f}{errs[i][1].imag:.5f}i, err={errs[i][0]:.6e}")

print("\nDone.")
