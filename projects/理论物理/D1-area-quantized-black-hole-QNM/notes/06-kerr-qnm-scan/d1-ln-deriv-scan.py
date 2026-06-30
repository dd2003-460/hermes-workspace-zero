#!/usr/bin/env python3
"""Find eigenvalues via log-derivative matching with proper stability."""
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

def shoot_logderiv(w, l, c, N_side=2000, origin=-50.0, direction=+1):
    """
    Integrate d(ln phi)/dr* = -(w^2-V) - (ln phi)^2
    from origin (horizon=-50 or infinity=80) toward origin rs=0.

    CRITICAL: integrate using both psi and dpsi simultaneously,
    then recover ln phi = dpsi/psi from the integrated solution.
    """
    # Use psi, dpsi integration but only return log derivative
    # as phi'/phi at rs=0
    if direction > 0:  # horizon to test
        rs_start, rs_end = origin, 0.0
        ps = np.exp(-1j*w*rs_start)  # initial psi at horizon BC
        dps = -1j*w*ps               # initial dpsi at horizon BC
    else:  # infinity to test
        rs_start, rs_end = origin, 0.0
        ps = np.exp(1j*w*rs_start)
        dps = 1j*w*ps

    dr = (rs_end - rs_start) / N_side
    lnphi_start = dps / ps if ps != 0 else (-1j*w if direction > 0 else 1j*w)

    ps_h = ps
    dps_h = dps

    for i in range(N_side):
        rs = rs_start + i*dr

        r = r_from_rstar(rs)
        Vr = V(r, l, c)
        h = dr

        k1_y = dps_h
        k1_d = -(w**2 - Vr) * ps_h

        rm = r_from_rstar(rs + h/2); Vm = V(rm, l, c)
        k2_y = dps_h + h/2*k1_d
        k2_d = -(w**2 - Vm)*(ps_h + h/2*k1_y)

        k3_y = dps_h + h/2*k2_d
        k3_d = -(w**2 - Vm)*(ps_h + h/2*k2_y)

        re = r_from_rstar(rs + h); Ve = V(re, l, c)
        k4_y = dps_h + h*k3_d
        k4_d = -(w**2 - Ve)*(ps_h + h*k3_y)

        ps_h += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps_h += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

        # Handle potential divergence with local renorm
        mag = max(abs(ps_h), abs(dps_h), 1e-300)
        if mag > 1e100:
            ps_h /= mag
            dps_h /= mag

    if abs(ps_h) < 1e-300:
        return 1e50

    return dps_h / ps_h  # logarithmic derivative at rs=0

def find_logderiv_min(w0, l, c, N_side=1000):
    """
    Compute |ln_H - ln_I| for given w.
    This is the eigenvalue condition.
    """
    try:
        ln_h = shoot_logderiv(w0, l, c, N_side, -50.0, +1)
        ln_i = shoot_logderiv(w0, l, c, N_side, 80.0, -1)
        if abs(ln_h) > 1e30 or abs(ln_i) > 1e30:
            return 1e20, ln_h, ln_i
        mm = abs(ln_h - ln_i)
        scale = max(abs(ln_h), abs(ln_i), 1)
        return mm/scale, ln_h, ln_i
    except:
        return 1e20, 0, 0

print("=" * 60)
print("Log-derivative eigenvalue scan")
print("=" * 60)

# Test Betti value at various N
for N_test in [200, 500, 1000, 2000]:
    mm, ln_h, ln_i = find_logderiv_min(complex(0.37367, -0.08896), 2, 6, N_test)
    print(f"c=6,l=2 Betti, N={N_test:4d}: mm={mm:.6e}, lnH={ln_h:.3f}, lnI={ln_i:.3f}")

# Grid scan for c=6, l=2
print("\nGrid scan c=6, l=2 (N=1000):")
best_mm = 1e20; best_w = None
for re in np.arange(0.3, 0.7, 0.01):
    for im in np.arange(-0.12, -0.03, 0.003):
        w = complex(re, im)
        mm, _, _ = find_logderiv_min(w, 2, 6, 500)
        if mm < best_mm and mm < 10:  # only care about reasonable values
            best_mm = mm; best_w = w

if best_w and best_mm < 1e15:
    print(f"  Best found: omega = {best_w.real:.3f}+{best_w.imag:.3f}i, mm = {best_mm:.6e}")

    # Convergence
    for N_test in [500, 1000, 2000]:
        mm, ln_h, ln_i = find_logderiv_min(best_w, 2, 6, N_test)
        print(f"    N={N_test:4d}: mm={mm:.6e}, lnH={ln_h.real:.4f}+{ln_h.imag:.4f}i, lnI={ln_i.real:.4f}+{ln_i.imag:.4f}i")
else:
    print("  No good minimum found in this grid")

# Same for l=3
print("\nGrid scan c=6, l=3 (N=500):")
best_mm3 = 1e20; best_w3 = None
for re in np.arange(0.4, 0.7, 0.01):
    for im in np.arange(-0.10, -0.02, 0.003):
        w = complex(re, im)
        mm, _, _ = find_logderiv_min(w, 3, 6, 500)
        if mm < best_mm3 and mm < 10:
            best_mm3 = mm; best_w3 = w

if best_w3 and best_mm3 < 1e15:
    print(f"  Best found: omega = {best_w3.real:.3f}+{best_w3.imag:.3f}i, mm = {best_mm3:.6e}")
    for N_test in [500, 1000, 2000]:
        mm, ln_h, ln_i = find_logderiv_min(best_w3, 3, 6, N_test)
        print(f"    N={N_test:4d}: mm={mm:.6e}, lnH={ln_h.real:.4f}+{ln_h.imag:.4f}i, lnI={ln_i.real:.4f}+{ln_i.imag:.4f}i")
else:
    print("  No good minimum found in this grid")

print("\nDone")
