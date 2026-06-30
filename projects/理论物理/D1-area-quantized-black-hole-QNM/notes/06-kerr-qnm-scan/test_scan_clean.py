#!/usr/bin/env python3
"""
Clean frequency scan: locate QNM eigenvalues using r* Wronskian method.
Test BOTH scalar (2M/r³) and gravitational (6M/r³) Regge-Wheeler potentials
to identify the source of Berti reference mismatch.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

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
    """c=6 for gravitational, c=2 for scalar perturbations."""
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - c * M / r**3)


def wronskian_rstar(omega, l, rs_h=-50, rs_inf=150, rs_m=80, pot_c=6.0):
    """Two-sided Wronskian at matching point rs_m."""
    def V(r):
        return rw_potential(r, l, c=pot_c)

    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        return [Y[1], -(omega**2 - V(r)) * Y[0]]

    # Horizon side: ingoing BC
    s1 = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
    # Infinity side: outgoing BC
    s2 = solve_ivp(deriv, [rs_inf, rs_m], [1.0, +1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)

    if not (s1.success and s2.success):
        return None

    ph, dph = s1.sol(rs_m)
    pf, dpf = s2.sol(rs_m)
    W = abs(ph * dpf - dph * pf)
    # Normalize by product of norms to get relative measure
    norm = abs(ph) * abs(pf)
    if norm < 1e-300:
        return None
    return W / norm


def scan_potential(l, pot_c, ref, N_re=30, N_im=20):
    """Scan with given potential coefficient c."""
    re_range = np.linspace(ref.real - 0.3, ref.real + 0.3, N_re)
    im_range = np.linspace(ref.imag - 0.15, ref.imag + 0.10, N_im)

    results = []
    for re_w in re_range:
        for im_w in im_range:
            omega = complex(re_w, im_w)
            w_val = wronskian_rstar(omega, l, pot_c=pot_c)
            if w_val is not None and w_val < 5.0:
                results.append((w_val, omega))

    results.sort()
    return results[:15]


def main():
    print("=" * 80)
    print("QNM Frequency Scan: Gravitational (6M/r³) vs Scalar (2M/r³)")
    print("=" * 80)

    for l in [2, 3]:
        ref = BERTI_REF[l]
        print(f"\nl = {l}")
        print(f"  Berti ref:  omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        for pot_name, pot_c in [("Gravitational (c=6)", 6.0), ("Scalar (c=2)", 2.0)]:
            print(f"\n  {pot_name}:")

            # Check at Berti reference
            W_ref = wronskian_rstar(ref, l, pot_c=pot_c)
            print(f"    |W|/norm at Berti: {W_ref:.6e}")

            # Also check at r*=40, 60, 100
            for rs_m in [40, 80, 120]:
                def V2(r, l=l, c=pot_c):
                    return rw_potential(r, l, c=c)
                def deriv2(rs, Y, om=ref):
                    r = r_from_rstar(rs)
                    if r <= 2.0 * M + 1e-14:
                        r = 2.0 * M + 1e-14
                    return [Y[1], -(om**2 - V2(r))*Y[0]]
                s1 = solve_ivp(deriv2, [-50, rs_m], [1.0, -1j*ref],
                             rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
                s2 = solve_ivp(deriv2, [150, rs_m], [1.0, +1j*ref],
                             rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
                if s1.success and s2.success:
                    ph, dph = s1.sol(rs_m)
                    pf, dpf = s2.sol(rs_m)
                    W = abs(ph*dpf - dph*pf) / (abs(ph)*abs(pf))
                    print(f"    |W|/norm at r*={rs_m}: {W:.6e}")

            # Scan
            print(f"    Scan results (best 5):")
            best = scan_potential(l, pot_c, ref, N_re=25, N_im=15)
            if best:
                for w_val, omega in best[:5]:
                    rel_err = abs(omega - ref) / abs(ref)
                    print(f"      omega = {omega.real:.5f} - {abs(omega.imag):.5f}i, |W|/norm = {w_val:.6e}, rel_err = {rel_err:.4f}")
            else:
                print("      No low-W values found in scan range.")

    # High-precision refinement near best minimum for c=6
    print(f"\n{'='*80}")
    print("Refinement near c=6 minimum for l=2")
    print("=" * 80)

    # First, refine the c=6, l=2 result with dense grid
    ref_l2 = BERTI_REF[2]
    best_c6 = scan_potential(2, 6.0, ref_l2, N_re=50, N_im=30)
    if best_c6:
        omega_best = best_c6[0][1]
        print(f"\nBest (c=6, l=2): omega = {omega_best.real:.6f} - {abs(omega_best.imag):.6f}i")
        print(f"  |W|/norm = {best_c6[0][0]:.6e}")
        print(f"  Berti ref:  omega = {ref_l2.real:.5f} - {abs(ref_l2.imag):.5f}i")
        print(f"  Δ Re = {omega_best.real - ref_l2.real:.6f}")
        print(f"  Δ Im = {omega_best.imag + abs(ref_l2.imag):.6f}")
        rel_err = abs(omega_best - ref_l2) / abs(ref_l2)
        print(f"  Relative error: {rel_err:.4f} ({rel_err*100:.1f}%)")

        # Refined scan around the best
        print(f"\n  Refined scan around minimum:")
        best2 = scan_potential(2, 6.0, omega_best, N_re=30, N_im=20)
        if best2:
            omega2 = best2[0][1]
            print(f"    omega = {omega2.real:.6f} - {abs(omega2.imag):.6f}i")
            print(f"    |W|/norm = {best2[0][0]:.6e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
