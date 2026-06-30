#!/usr/bin/env python3
"""
Wronskian calculation using proper shooting method, with per-step
renormalization. Compare c=6 eigenvalues vs Berti values.
Uses fixed-step RK4 with step size control.
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

def shoot_2side(w, l, c, N_total=10000):
    """Shoot from both sides, return the Wronskian value.
    Uses global renormalization when needed."""
    rs_hor = -60.0
    rs_inf = 80.0
    rs_test = 0.0
    N1 = N_total // 2  # horizon side
    N2 = N_total - N1  # infinity side

    # Horizon -> test
    dr1 = (rs_test - rs_hor) / N1
    ph = np.exp(-1j*w*rs_hor)
    dph = -1j*w*ph

    for i in range(N1):
        rs = rs_hor + i*dr1
        r = r_from_rstar(rs)
        Vr = V(r, l, c)

        h = dr1
        k1_y = dph; k1_d = -(w**2-Vr)*ph

        rm1 = r_from_rstar(rs+h/2); V1 = V(rm1, l, c)
        k2_y = dph + h/2*k1_d; k2_d = -(w**2-V1)*(ph+h/2*k1_y)

        k3_y = dph + h/2*k2_d; k3_d = -(w**2-V1)*(ph+h/2*k2_y)

        rm2 = r_from_rstar(rs+h); V2 = V(rm2, l, c)
        k4_y = dph + h*k3_d; k4_d = -(w**2-V2)*(ph+h*k3_y)

        ph += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dph += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

        # Global renormalization
        if abs(ph) + abs(dph) > 1e50:
            ph /= abs(ph) + abs(dph) + 1
            dph /= abs(ph) + abs(dph) + 1

    # Infinity -> test
    dr2 = (rs_inf - rs_test) / N2
    pi = np.exp(1j*w*rs_inf)
    dpi = 1j*w*pi

    for i in range(N2):
        rs = rs_inf - i*dr2
        r = r_from_rstar(rs)
        Vr = V(r, l, c)

        h = dr2
        k1_y = dpi; k1_d = -(w**2-Vr)*pi

        rm1 = r_from_rstar(rs-h/2); V1 = V(rm1, l, c)
        k2_y = dpi - h/2*k1_d; k2_d = -(w**2-V1)*(pi-h/2*k1_y)

        k3_y = dpi - h/2*k2_d; k3_d = -(w**2-V1)*(pi-h/2*k2_y)

        rm2 = r_from_rstar(rs-h); V2 = V(rm2, l, c)
        k4_y = dpi - h*k3_d; k4_d = -(w**2-V2)*(pi-h*k3_y)

        pi -= h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dpi -= h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

        if abs(pi) + abs(dpi) > 1e50:
            pi /= abs(pi) + abs(dpi) + 1
            dpi /= abs(pi) + abs(dpi) + 1

    # Compute Wronskian at rs_test
    W = abs(dph*pi - ph*dpi)
    denom = abs(ph) + abs(dph) + abs(pi) + abs(dpi)
    return W, W/(denom+1), ph, dph, pi, dpi

def test_point(w, l, c, N=10000):
    W, Wn, ph, dph, pi, dpi = shoot_2side(w, l, c, N)
    return W, Wn, ph, dph, pi, dpi

# Quick comparison at key values
for N in [1000, 5000, 10000]:
    print(f"\nN = {N}:")
    for (l, c, label) in [(2,6,"c=6,l=2"), (3,6,"c=6,l=3")]:
        beti = complex(0.37367, -0.08896) if l==2 else complex(0.59108, -0.05902)
        prev = complex(0.548, -0.071) if l==2 else complex(0.523, -0.063)

        # Berti
        Wb, Wbn, *rest = test_point(beti, l, c, N)
        print(f"  {label} Betti: W={Wb:.3e}  Wn={Wbn:.6e}")

        # Previous
        Wp, Wpn, *rest = test_point(prev, l, c, N)
        print(f"  {label} Prev:  W={Wp:.3e}  Wn={Wpn:.6e}")

# Also check: at the eigenvalue, the log derivative should match
print("\nLog-derivative check at best found (N=10000):")
for l, c in [(2,6), (3,6)]:
    best = complex(0.548, -0.071) if l==2 else complex(0.523, -0.063)
    W, Wn, ph, dph, pi, dpi = test_point(best, l, c, 10000)
    ln_h = dph / ph
    ln_i = dpi / pi
    print(f"  c={c}, l={l}:")
    print(f"    ln_H = {ln_h.real:.4f} + {ln_h.imag:.4f}i")
    print(f"    ln_I = {ln_i.real:.4f} + {ln_i.imag:.4f}i")
    print(f"    |ln_H - ln_I| = {abs(ln_h-ln_i):.6e}")
    print(f"    |W| = {W:.3e}")
    print(f"    |phi_h| = {abs(ph):.3f}, |phi_i| = {abs(pi):.3f}")
