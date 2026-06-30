#!/usr/bin/env python3
"""
Fast formulation diagnostic.
One focused Riccati scan, lower precision, smaller grid.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def r_from_rs(rs):
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(60):
        if r <= 2 * M: r = 2 * M + 1e-14; continue
        rs_calc = r + 2 * M * np.log(r / (2 * M) - 1.0)
        drstar_dr = r ** 2 / (r - 2 * M) ** 2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-16: break
        r -= dr
        if r <= 2 * M: r = 2 * M + 1e-14
    return r


def rs_from_r(r):
    return r + 2 * M * np.log(r / (2 * M) - 1.0)


def V(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)


def riccati_mismatch(omega, l):
    def deriv(rs, f):
        r = r_from_rs(rs)
        r = max(r, 2 * M + 1e-14)
        Vv = V(r, l)
        return [-(omega ** 2 - Vv) - f[0] ** 2]
    s_h = solve_ivp(deriv, [-50, 0], [-1j*omega], rtol=1e-10, atol=1e-12, max_step=0.5)
    s_inf = solve_ivp(deriv, [200, 0], [+1j*omega], rtol=1e-10, atol=1e-12, max_step=0.5)
    if not (s_h.success and s_inf.success):
        return 1e100, None, None
    return abs(s_h.y[0,-1] - s_inf.y[0,-1]), s_h.y[0,-1], s_inf.y[0,-1]


print("=" * 70)
print("Formulation Diagnostic")
print("=" * 70)

# Potential check
print("\n1. Potential shape:")
for l in [2, 3]:
    r_vals = np.linspace(2.01, 30, 300)
    V_vals = np.array([V(r, l) for r in r_vals])
    peak_idx = np.argmax(V_vals)
    r_peak = r_vals[peak_idx]
    V_peak = V_vals[peak_idx]
    print(f"   l={l}: V_peak={V_peak:.6f} at r={r_peak:.3f}M")
    print(f"          Berti w^2={BERTI[l]**2:.6f}, Re(w^2)={np.real(BERTI[l]**2):.6f}")

# Coords check
print("\n2. Tortoise coord roundtrip:")
for r_test in [3.0, 6.0, 10.0]:
    rs = rs_from_r(r_test)
    r_back = r_from_rs(rs)
    print(f"   r={r_test}: r*={rs:.4f}, roundtrip err={abs(r_test-r_back):.2e}")

# Riccati at Berti
print("\n3. Riccati at Berti values:")
for l in [2, 3]:
    err, fh, fi = riccati_mismatch(BERTI[l], l)
    print(f"   l={l}: Berti={BERTI[l]}, |mismatch|={err:.8f}")
    if fh and fi:
        print(f"     f_h={fh:.6f}, f_inf={fi:.6f}, i*w={(1j*BERTI[l]):.6f}, -i*w={(-1j*BERTI[l]):.6f}")

# Focused scan
print("\n4. Focused scan 15x10 around Berti (l=2):")
best = None
for rr in np.linspace(0.2, 0.7, 15):
    for ri in np.linspace(-0.15, 0.0, 10):
        w = complex(rr, ri)
        err, fh, fi = riccati_mismatch(w, 2)
        if best is None or err < best[0]:
            best = (err, w, fh, fi)

if best:
    err, w, fh, fi = best
    print(f"   Best: omega={w.real:.5f}+({w.imag:.5f})i")
    print(f"   Error={err:.8e}")
    print(f"   w^2={w**2:.8f}")
    print(f"   Berti={BERTI[2]}, Berti w^2={BERTI[2]**2:.8f}")
    print(f"   Delta: dRe={w.real-BERTI[2].real:.4f}, dIm={w.imag-BERTI[2].imag:.4f}")
    print(f"   f_h={fh:.6f}, f_inf={fi:.6f}")
    print(f"   i*w={(1j*w):.6f}, -i*w={(-1j*w):.6f}")

    # Check: does a finer search find better?
    print("\n5. Fine scan around best (21x11):")
    best2 = None
    wr_center, wi_center = w.real, w.imag
    for rr in np.linspace(wr_center-0.05, wr_center+0.10, 21):
        for ri in np.linspace(wi_center-0.05, wi_center+0.02, 11):
            w2 = complex(rr, ri)
            err2, fh2, fi2 = riccati_mismatch(w2, 2)
            if best2 is None or err2 < best2[0]:
                best2 = (err2, w2, fh2, fi2)

    if best2:
        err2, w2, fh2, fi2 = best2
        print(f"   Refined: omega={w2.real:.5f}+({w2.imag:.5f})i")
        print(f"   Refined Error={err2:.8e}")
        print(f"   Final Delta from Berti: dRe={w2.real-BERTI[2].real:.5f}, dIm={w2.imag-BERTI[2].imag:.5f}")
        print(f"   f_h={fh2:.6f}, f_inf={fi2:.6f}")
        print(f"   i*w={(1j*w2):.6f}, -i*w={(-1j*w2):.6f}")
        print(f"   r²={w2**2:.8f}")

        # Convergence check: reduce tolerance at best omega
        print(f"\n6. Convergence check at best omega = {w2}:")
        for tol in [1e-6, 1e-8, 1e-10, 1e-12]:
            def deriv(rs, f):
                r = r_from_rs(rs)
                r = max(r, 2 * M + 1e-14)
                Vv = V(r, 2)
                return [-(w2**2 - Vv) - f[0]**2]
            sh = solve_ivp(deriv, [-50, 0], [-1j*w2], rtol=tol, atol=tol*1e-2, max_step=0.5)
            si = solve_ivp(deriv, [200, 0], [+1j*w2], rtol=tol, atol=tol*1e-2, max_step=0.5)
            if sh.success and si.success:
                fh = sh.y[0,-1]
                fi = si.y[0,-1]
                print(f"   tol={tol:.0e}: |fh-fi|={abs(fh-fi):.8e}, fh={fh:.6f}, fi={fi:.6f}")
            else:
                print(f"   tol={tol:.0e}: integration failed")

# Try Im(omega) negative range: look beyond Berti
print("\n7. Search wider Im range (l=2): Re=[0.2,0.7] Im=[-0.25,0.0]:")
best3 = None
for rr in np.linspace(0.2, 0.7, 15):
    for ri in np.linspace(-0.25, 0.0, 12):
        w = complex(rr, ri)
        err, _, _ = riccati_mismatch(w, 2)
        if best3 is None or err < best3[0]:
            best3 = (err, w)
if best3:
    print(f"   Best: omega={best3[1].real:.5f}+({best3[1].imag:.5f})i, err={best3[0]:.8e}")
    print(f"   Delta from Berti: dRe={best3[1].real-BERTI[2].real:.4f}, dIm={best3[1].imag-BERTI[2].imag:.4f}")


# Broader Re range (coarse only)
print("\n8. Broader Re search: Re=[0.05,1.5] Im=[-0.2,0.0] (coarse 8x6):")
best4 = None
for rr in np.linspace(0.05, 1.5, 8):
    for ri in np.linspace(-0.2, 0.0, 6):
        w = complex(rr, ri)
        err, _, _ = riccati_mismatch(w, 2)
        if best4 is None or err < best4[0]:
            best4 = (err, w)
if best4:
    print(f"   Best: omega={best4[1].real:.5f}+({best4[1].imag:.5f})i, err={best4[0]:.8e}")

# Verify Riccati at a very specific omega — try the value found in test_quick_riccati.py:
# omega ~ 0.76 - 0.05i or the best from that script
print("\n9. Test specific omega values from prior scans:")
test_vals = [
    complex(0.37367, -0.08896),  # Berti
    complex(0.749567, -0.207092),  # from test_matrix_eigen.py Riccati
    complex(0.344069, -0.019584),  # from test_matrix_eigen.py shooting
    complex(0.20, 0.0),  # from Leaver v2 with corrected BCs
    complex(0.76, -0.05),
]
for tv in test_vals:
    err, fh, fi = riccati_mismatch(tv, 2)
    print(f"   omega={tv.real:.5f}+({tv.imag:.5f})i: |mismatch|={err:.8e}")
    if fh and fi:
        print(f"     fh={fh:.6f}, fi={fi:.6f}")

# Verify at Berti with different rs_m matching points
print("\n10. Mismatch at Berti for different rs_m:")
for rs_m in [-30, -20, -10, -5, 0, 5, 10, 20, 40, 80]:
    err, _, _ = riccati_mismatch(BERTI[2], 2) if rs_m == 0 else riccati_mismatch.__code__  # dummy
    # Manually compute for each rs_m
    w = BERTI[2]
    def deriv(rs, f):
        r = r_from_rs(rs)
        r = max(r, 2*M+1e-14)
        Vv = V(r, 2)
        return [-(w**2 - Vv) - f[0]**2]
    sh = solve_ivp(deriv, [-50, rs_m], [-1j*w], rtol=1e-10, atol=1e-12, max_step=0.5)
    si = solve_ivp(deriv, [200, rs_m], [+1j*w], rtol=1e-10, atol=1e-12, max_step=0.5)
    if sh.success and si.success:
        fh = sh.y[0,-1]
        fi = si.y[0,-1]
        print(f"   rs_m={rs_m:4d}: |fh-fi|={abs(fh-fi):.8e}")
    else:
        print(f"   rs_m={rs_m:4d}: failed")


print("\n" + "=" * 70)
print("Done.")
