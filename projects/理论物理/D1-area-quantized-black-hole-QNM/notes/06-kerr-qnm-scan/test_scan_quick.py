#!/usr/bin/env python3
"""
Quick focused scan: check if c=2 vs c=6 fixes the Berti mismatch.
Just compute Wronskian at Berti ref for both potentials, plus a light scan.
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

def rw_potential(r, l, c):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - c * M / r**3)


def W_one(omega, l, pot_c, rs_h=-50, rs_inf=150, rs_m=80):
    """Return W/|phi_h * phi_f| at rs_m."""
    t0 = time.time()

    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l, pot_c)
        return [Y[1], -(omega**2 - V) * Y[0]]

    s1 = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
    s2 = solve_ivp(deriv, [rs_inf, rs_m], [1.0, +1j * omega],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)

    if not (s1.success and s2.success):
        return None, time.time() - t0

    ph, dph = s1.sol(rs_m)
    pf, dpf = s2.sol(rs_m)
    W = abs(ph * dpf - dph * pf) / (abs(ph) * abs(pf))
    return W, time.time() - t0


N_re = 17
N_im = 11


def main():
    t_global = time.time()

    for l in [2, 3]:
        ref = BERTI_REF[l]
        pot_names = ["Gravitational (c=6)", "Scalar (c=2)"]
        pot_cs = [6.0, 2.0]

        print(f"\nl = {l}, Berti: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")
        print(f"  {'='*60}")

        for pot_name, pot_c in zip(pot_names, pot_cs):
            print(f"\n  {pot_name}:")

            # Check at multiple matching points
            for rs_m in [40, 60, 80, 100, 120]:
                W, t = W_one(ref, l, pot_c, rs_m=rs_m)
                if W is not None:
                    print(f"    rs_m={rs_m:3d}: |W|/norm = {W:.6e}  (t={t:.2f}s)")
                else:
                    print(f"    rs_m={rs_m:3d}: FAILED (t={t:.2f}s)")

            # Test a few nearby omega values
            print(f"    Nearby omega scan (c=6):")
            for dr in [-0.1, -0.05, 0.0, 0.05, 0.10]:
                for di in [-0.02, 0.0, 0.02]:
                    omega = ref + complex(dr, di)
                    W, t = W_one(omega, l, pot_c, rs_m=80)
                    if W is not None and W < 0.5:
                        print(f"      {omega.real:.4f}{omega.imag:+.4f}i: {W:.6e}")

            # Light scan
            print(f"    Light scan ({N_re}x{N_im}):")
            t1 = time.time()
            best = []
            for dr in np.linspace(-0.2, 0.2, N_re):
                for di in np.linspace(-0.1, 0.15, N_im):
                    omega = ref + complex(dr, di)
                    W, t = W_one(omega, l, pot_c, rs_m=80)
                    if W is not None and W < 2.0:
                        best.append((W, omega))
            best.sort()
            elapsed = time.time() - t1
            print(f"      Best {len(best)} found in {elapsed:.1f}s")
            for W, omega in best[:3]:
                print(f"        omega = {omega.real:.5f} - {abs(omega.imag):.5f}i, |W| = {W:.6e}")

        total = time.time() - t_global
        print(f"\n  Total time so far: {total:.0f}s")

    print(f"\nTotal: {time.time()-t_global:.0f}s")


if __name__ == "__main__":
    main()
