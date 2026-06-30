#!/usr/bin/env python3
"""
The eigenvalue condition: at the QNM frequency, both
- Solution from horizon: decay at infinity (outgoing)
- Solution from infinity: decay at horizon (ingoing)

At rs=0, if both solutions have the SAME log derivative, then Wronskian=0
(i.e., the two solutions are proportional, which is the QNM condition).

But the log derivatives don't even match for arbitrary omega. The question
is: is there ANY omega where they match?

Let me do a fine scan.
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

def integrate_to_r0(w, l, c, N, side, renorm_threshold=1e100):
    """
    Integrate psi'' + (omega^2-V)*psi = 0 from boundary to rs=0.
    side = 'in' (horizon, rs=-50) or 'out' (infinity, rs=80).
    Returns (psi, dpsi) at rs=0.
    """
    if side == 'in':
        rs_s, rs_t = -50.0, 0.0
        ps = np.exp(-1j*w*rs_s)
        dps = -1j*w*ps
    else:
        rs_s, rs_t = 80.0, 0.0
        ps = np.exp(1j*w*rs_s)
        dps = 1j*w*ps

    dr = (rs_t - rs_s) / N
    h = dr

    for i in range(N):
        rs = rs_s + i*dr
        r = r_from_rstar(rs)
        Vr = V(r, l, c)

        k1_y = dps; k1_d = -(w**2 - Vr)*ps

        rm = r_from_rstar(rs+h/2); Vm = V(rm, l, c)
        k2_y = dps+h/2*k1_d; k2_d = -(w**2-Vm)*(ps+h/2*k1_y)

        k3_y = dps+h/2*k2_d; k3_d = -(w**2-Vm)*(ps+h/2*k2_y)

        re = r_from_rstar(rs+h); Ve = V(re, l, c)
        k4_y = dps+h*k3_d; k4_d = -(w**2-Ve)*(ps+h*k3_y)

        ps += h/6*(k1_y+2*k2_y+2*k3_y+k4_y)
        dps += h/6*(k1_d+2*k2_d+2*k3_d+k4_d)

        # Periodic renormalization every 100 steps
        if (i+1) % 100 == 0:
            mag = max(abs(ps), abs(dps), 1e-300)
            if mag > renorm_threshold:
                ps /= mag
                dps /= mag

    return ps, dps

def find_QNM(l, c, re_start, re_end, im_start, im_end, re_step, im_step, N=2000):
    """Find QNM by grid search, minimizing |ln_H - ln_I|."""
    best_mm = 1e20
    best_w = None
    best_lnH = None
    best_lnI = None
    best_ratio = None

    for re in np.arange(re_start, re_end, re_step):
        for im in np.arange(im_start, im_end, im_step):
            w = complex(re, im)

            ps_h, dps_h = integrate_to_r0(w, l, c, N//2, 'in')
            ps_i, dps_i = integrate_to_r0(w, l, c, N//2, 'out')

            # Check if either is too small
            if abs(ps_h) < 1e-300 or abs(ps_i) < 1e-300:
                continue

            ln_h = dps_h / ps_h
            ln_i = dps_i / ps_i

            # Mismatch
            mm = abs(ln_h - ln_i)
            scale = abs(ln_h) + abs(ln_i) + 1

            if mm/scale < best_mm and mm < 10:
                best_mm = mm/scale
                best_w = w
                best_lnH = ln_h
                best_lnI = ln_i

                # Also compute the Wronskian for reference
                W = abs(dps_h*ps_i - ps_h*dps_i) / (abs(ps_h)+abs(dps_h)+abs(ps_i)+abs(dps_i)+1)

    return best_w, best_mm, best_lnH, best_lnI

print("=" * 60)
print("Final QNM search for Schwarzschild Regge-Wheeler")
print("Equation: psi'' + (omega^2 - V)psi = 0")
print("V = (1-2M/r)(l(l+1)/r^2 - cM/r^3)")
print("=" * 60)

# Grid search for c=6, l=2
print("\n--- c=6, l=2 grid search (N=1000 per side) ---")
best_w, best_mm, lnH, lnI = find_QNM(2, 6, 0.3, 0.8, -0.15, -0.02, 0.01, 0.003, 1000)

if best_w:
    print(f"  Grid minimum: omega = {best_w.real:.3f}+{best_w.imag:.3f}i")
    print(f"  |lnH-lnI| = {best_mm:.6e}")
    print(f"  lnH = {lnH.real:.4f}+{lnH.imag:.4f}i")
    print(f"  lnI = {lnI.real:.4f}+{lnI.imag:.4f}i")

    # Convergence test
    for N in [1000, 2000, 5000]:
        ps_h, dps_h = integrate_to_r0(best_w, 2, 6, N//2, 'in')
        ps_i, dps_i = integrate_to_r0(best_w, 2, 6, N//2, 'out')
        ln_h = dps_h / ps_h
        ln_i = dps_i / ps_i
        mm = abs(ln_h - ln_i) / (abs(ln_h) + abs(ln_i) + 1)
        W = abs(dps_h*ps_i - ps_h*dps_i) / (abs(ps_h)+abs(dps_h)+abs(ps_i)+abs(dps_i)+1)
        ratio_h = abs(dps_h)/abs(ps_h)
        ratio_i = abs(dps_i)/abs(ps_i)
        print(f"    N={N:5d}: |W|/norm={W:.6e}, mm={mm:.6e}, |ratio_H|={ratio_h:.4f}, |ratio_I|={ratio_i:.4f}")
else:
    print("  No QNM found in this range.")

# Refined search for l=2
print("\n--- c=6, l=2 refined search (N=2000 per side) ---")
ref_w, ref_mm, ref_lH, ref_lI = find_QNM(2, 6,
    best_w.real - 0.05 if best_w else 0.4,
    best_w.real + 0.05 if best_w else 0.6,
    -0.12 if best_w else -0.08,
    -0.03 if best_w else -0.01,
    0.005, 0.002, 2000)

if ref_w and ref_mm < best_mm:
    print(f"  Refined minimum: omega = {ref_w.real:.3f}+{ref_w.imag:.3f}i")
    print(f"  |lnH-lnI| = {ref_mm:.6e}")
    for N in [1000, 2000, 5000]:
        ps_h, dps_h = integrate_to_r0(ref_w, 2, 6, N//2, 'in')
        ps_i, dps_i = integrate_to_r0(ref_w, 2, 6, N//2, 'out')
        ln_h = dps_h / ps_h
        ln_i = dps_i / ps_i
        mm = abs(ln_h - ln_i) / (abs(ln_h) + abs(ln_i) + 1)
        W = abs(dps_h*ps_i - ps_h*dps_i) / (abs(ps_h)+abs(dps_h)+abs(ps_i)+abs(dps_i)+1)
        print(f"    N={N:5d}: |W|/norm={W:.6e}, mm={mm:.6e}")

# c=6, l=3
print("\n--- c=6, l=3 grid search (N=1000 per side) ---")
w3, mm3, lH3, lI3 = find_QNM(3, 6, 0.4, 0.8, -0.12, -0.02, 0.01, 0.003, 1000)
if w3:
    print(f"  Grid minimum: omega = {w3.real:.3f}+{w3.imag:.3f}i")
    print(f"  |lnH-lnI| = {mm3:.6e}")
    for N in [1000, 2000, 5000]:
        ps_h, dps_h = integrate_to_r0(w3, 3, 6, N//2, 'in')
        ps_i, dps_i = integrate_to_r0(w3, 3, 6, N//2, 'out')
        ln_h = dps_h / ps_h
        ln_i = dps_i / ps_i
        mm = abs(ln_h - ln_i) / (abs(ln_h) + abs(ln_i) + 1)
        W = abs(dps_h*ps_i - ps_h*dps_i) / (abs(ps_h)+abs(dps_h)+abs(ps_i)+abs(dps_i)+1)
        print(f"    N={N:5d}: |W|/norm={W:.6e}, mm={mm:.6e}")
        print(f"      lnH={ln_h.real:.4f}+{ln_h.imag:.4f}i, lnI={ln_i.real:.4f}+{ln_i.imag:.4f}i")

# Same for scalar c=2, l=2
print("\n--- c=2, l=2 (scalar) grid search (N=1000 per side) ---")
w2, mm2, lH2, lI2 = find_QNM(2, 2, 0.1, 0.7, -0.10, -0.01, 0.01, 0.003, 1000)
if w2:
    print(f"  Grid minimum: omega = {w2.real:.3f}+{w2.imag:.3f}i")
    print(f"  |lnH-lnI| = {mm2:.6e}")
    print(f"  Berti scalar ref: 0.27204-0.03150i")
    for N in [1000, 2000, 5000]:
        ps_h, dps_h = integrate_to_r0(w2, 2, 2, N//2, 'in')
        ps_i, dps_i = integrate_to_r0(w2, 2, 2, N//2, 'out')
        ln_h = dps_h / ps_h
        ln_i = dps_i / ps_i
        mm = abs(ln_h - ln_i) / (abs(ln_h) + abs(ln_i) + 1)
        W = abs(dps_h*ps_i - ps_h*dps_i) / (abs(ps_h)+abs(dps_h)+abs(ps_i)+abs(dps_i)+1)
        print(f"    N={N:5d}: |W|/norm={W:.6e}, mm={mm:.6e}")

print("\nDone")
