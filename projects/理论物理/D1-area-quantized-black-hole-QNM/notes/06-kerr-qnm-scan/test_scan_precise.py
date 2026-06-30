#!/usr/bin/env python3
"""
Precise Wronskian scan for QNM eigenvalues.
Fine-grained scan around the previously found minimum.
Also test the matching point to verify consistency.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
import time

M = 1.0
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}

def r_from_rstar(rs):
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(40):
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-14:
            break
        r -= dr
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
    return r

def rw_potential(r, l, c=6.0):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - c * M / r**3)

def wronskian_raw(omega, l, rs_h=-50, rs_inf=150, rs_m=80, c=6.0):
    """Return W = psi_h * dpsi_f/dps - dpsi_h/dps * psi_f (no normalization)."""
    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l, c)
        return [Y[1], -(omega**2 - V) * Y[0]]

    s1 = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
    s2 = solve_ivp(deriv, [rs_inf, rs_m], [1.0, +1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)

    if not (s1.success and s2.success):
        return None

    ph, dph = s1.sol(rs_m)
    pf, dpf = s2.sol(rs_m)
    W = ph * dpf - dph * pf
    # Return complex W
    return W, ph, pf

def W_complex_vals(omega, l, rs_m=80, c=6.0):
    """Return the complex Wronskian (phase matters)."""
    W, ph, pf = wronskian_raw(omega, l, rs_m=rs_m, c=c)
    if W is None:
        return None
    return W

def find_min_wronskian(omega, l, rs_m):
    """Refine by scanning in omega plane around omega_guess."""
    # We look for the absolute minimum of |W|
    re_best = omega.real
    im_best = omega.imag
    w_min = np.inf
    # Scan 50x50 grid
    re_c = np.linspace(omega.real - 0.1, omega.real + 0.1, 41)
    im_c = np.linspace(omega.imag - 0.05, omega.imag + 0.05, 21)
    for re_w in re_c:
        for im_w in im_c:
            w = complex(re_w, im_w)
            res = W_complex_vals(w, l, rs_m)
            if res is not None:
                mag = abs(res)
                if mag < w_min:
                    w_min = mag
                    re_best = re_w
                    im_best = im_w
    return complex(re_best, im_best), w_min

def main():
    print("=" * 80)
    print("Precise QNM Wronskian Scan")
    print("=" * 80)

    t0 = time.time()

    for l in [2, 3]:
        ref = BERTI_REF[l]

        print(f"\nl = {l}, Berti: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")
        print(f"  {'='*65}")

        # Test at Berti reference
        for rs_m in [30, 50, 70, 90, 110]:
            res = W_complex_vals(ref, l, rs_m=rs_m, c=6.0)
            if res is not None:
                print(f"    rs_m={rs_m:3d}: |W| = {abs(res):.6e}, phase = {np.angle(res):.4f} rad")
            else:
                print(f"    rs_m={rs_m:3d}: FAILED")

        # Scan around Berti (11x11 grid)
        print(f"\n    Scan around Berti (c=6):")
        best = []
        for dr in np.linspace(-0.1, 0.1, 11):
            for di in np.linspace(-0.06, 0.06, 8):
                omega = ref + complex(dr, di)
                res = W_complex_vals(omega, l, rs_m=80, c=6.0)
                if res is not None:
                    best.append((abs(res), omega))
        best.sort()
        for mag, omega in best[:5]:
            rel_err = abs(omega - ref) / abs(ref)
            print(f"      {omega.real:.5f}{omega.imag:.5f}i: |W|={mag:.6e}  rel_err={rel_err:.3f}")

        # Compare Berti vs previously-found minimum
        if l == 2:
            omega_min = complex(0.574, -0.039)
        else:
            omega_min = complex(0.691, -0.034)

        res_berti = W_complex_vals(ref, l, rs_m=80, c=6.0)
        res_min = W_complex_vals(omega_min, l, rs_m=80, c=6.0)
        res_berti2 = W_complex_vals(ref, l, rs_m=80, c=2.0)
        res_min2 = W_complex_vals(omega_min, l, rs_m=80, c=2.0)

        if res_berti is not None:
            print(f"\n    |W| at Berti (c=6): {abs(res_berti):.6e}")
            print(f"  |W| at Berti (c=2): {abs(res_berti2):.6e}")
        if res_min is not None:
            print(f"  |W| at min (c=6): {abs(res_min):.6e}")
            print(f"  |W| at min (c=2): {abs(res_min2):.6e}")
            print(f"  Ratio c=6: {abs(res_berti)/abs(res_min):.2f}x (BERTI higher by that factor)")

        total = time.time() - t0
        print(f"  Elapsed: {total:.0f}s")

    # Refined minimization for l=2
    print(f"\n{'='*80}")
    print("Refined Minimization (l=2)")
    print("=" * 80)

    # Start from the coarse minimum
    omega_start = complex(0.57, -0.04)
    for rs_m in [40, 60, 80]:
        print(f"\nrs_m = {rs_m}:")
        best = []
        for re_w in np.linspace(0.40, 0.70, 31):
            for im_w in np.linspace(-0.12, 0.04, 17):
                omega = complex(re_w, im_w)
                res = W_complex_vals(omega, 2, rs_m=rs_m, c=6.0)
                if res is not None:
                    best.append((abs(res), omega))
        best.sort()
        print(f"  Best 3:")
        for mag, omega in best[:3]:
            rel_err = abs(omega - BERTI_REF[2]) / abs(BERTI_REF[2])
            print(f"    {omega.real:.5f}{omega.imag:.5f}i: |W| = {mag:.6e}  rel_err={rel_err:.3f}")

    print(f"\nTotal: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
