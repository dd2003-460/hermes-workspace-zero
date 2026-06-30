#!/usr/bin/env python3
"""
Calibrate: use direct shooting to find QNM eigenvalues with B/A criterion.
This is a ground truth to compare against AIM results.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

M = 1.0

BERTI_REF = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def r_from_rstar(rs):
    """Convert r* to r using Lambert W + Newton refinement."""
    from scipy.special import lambertw
    t = rs / (2.0 * M) - 1.0
    if t > 10:
        y = t - np.log(t) + np.log(t) / t
    else:
        y = np.real(lambertw(np.exp(t), k=0))
    r = 2.0 * M * (1.0 + y)
    # Newton refinement
    for _ in range(30):
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-14:
            break
        r -= dr
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
    return r


def rw_potential(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)


def b_ratio(omega, l, rs_from, rs_to):
    """
    Integrate from rs_from to rs_to with ingoing BC.
    Decompose into outgoing and ingoing components at rs_to.
    Return B/A ratio.
    """
    def ode(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l)
        psi, dpsi = Y
        return [dpsi, -(omega**2 - V) * psi]

    sol = solve_ivp(
        ode, [rs_from, rs_to],
        [complex(1.0), complex(-1j * omega)],  # ingoing BC: psi ~ exp(-i*omega*r*)
        rtol=1e-11, atol=1e-13, max_step=0.3, dense_output=True
    )

    # At rs_to, extract (psi, dpsi)
    psi, dpsi = sol.y[:, -1]

    # Decompose:
    # Outgoing: A*exp(i*omega*rs_to) -> contribution to psi' is +i*omega*A*exp(i*omega*rs)
    # Ingoing: B*exp(-i*omega*rs_to) -> contribution to psi' is -i*omega*B*exp(-i*omega*rs)
    # psi = A*exp(iw*s) + B*exp(-iw*s)
    # psi' = iw*A*exp(iw*s) - iw*B*exp(-iw*s)
    # A*exp(iw*s) = (psi' + iw*psi) / (2iw)
    # B*exp(-iw*s) = (psi' - iw*psi) / (-2iw)
    A = (dpsi + 1j * omega * psi) / (2j * omega)
    B = (dpsi - 1j * omega * psi) / (-2j * omega)

    return abs(B / A) if abs(A) > 1e-300 else np.inf


def b_ratio_inward(omega, l, rs_from, rs_to):
    """Integrate from rs_to to rs_from with ingoing BC at infinity."""
    def ode(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l)
        psi, dpsi = Y
        return [dpsi, -(omega**2 - V) * psi]

    # Outgoing BC at far infinity: dpsi/dr* = +i*omega*psi
    sol = solve_ivp(
        ode, [rs_from, rs_to],
        [complex(1.0), complex(1j * omega)],  # outgoing BC at infinity
        rtol=1e-11, atol=1e-13, max_step=0.3, dense_output=True
    )

    psi, dpsi = sol.y[:, -1]

    # At rs_to (closer to horizon):
    # Decompose into ingoing and outgoing components
    A = (dpsi + 1j * omega * psi) / (2j * omega)
    B = (dpsi - 1j * omega * psi) / (-2j * omega)

    return abs(A / B) if abs(B) > 1e-300 else np.inf


def shooting_eigenvalue(l, rs_from, rs_to, initial_guess=None):
    """Find eigenvalue by minimizing |B/A| with respect to omega."""
    def objective(omega_params):
        omega = complex(omega_params[0], omega_params[1])
        return b_ratio(omega, l, rs_from, rs_to)

    if initial_guess is None:
        initial_guess = [0.4, -0.09]

    result = minimize(objective, initial_guess, method='Nelder-Mead',
                     xtol=1e-10, ftol=1e-12, maxiter=10000)

    return complex(result.x[0], result.x[1]), result.fun


def scan_b_ratio(l, rs_from, rs_to, re_range, im_range, re_step, im_step):
    """Scan B/A ratio over a grid."""
    best = []
    for re_w in np.arange(re_range[0], re_range[1], re_step):
        for im_w in np.arange(im_range[0], im_range[1], im_step):
            w = complex(re_w, im_w)
            br = b_ratio(w, l, rs_from, rs_to)
            if br < 10.0:
                best.append((br, w))
    best.sort()
    return best[:10]


def main():
    print("=" * 70)
    print("B/A Shooting Method - Ground Truth Calibration")
    print("=" * 70)

    for l in [2, 3]:
        print(f"\nl={l}:")
        ref = BERTI_REF[l]
        print(f"  Berti ref: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        # Test B/A at reference
        rs_start = r_from_rstar(-60)  # near horizon, r ~ 2.0005
        rs_end = 150  # far out, r ~ 250

        print(f"\n  Shooting from r*={rs_start:.1f} to r*={rs_end}")

        for Npts in [200, 500, 1000]:
            t_eval = np.linspace(rs_start, rs_end, Npts)
            if Npts == 200:
                max_step = 0.5
            elif Npts == 500:
                max_step = 0.3
            else:
                max_step = 0.2

            def ode_test(rs, Y):
                r = r_from_rstar(rs)
                if r <= 2.0 * M + 1e-14:
                    r = 2.0 * M + 1e-14
                V = rw_potential(r, l)
                psi, dpsi = Y
                return [dpsi, -(ref**2 - V) * psi]

            sol = solve_ivp(ode_test, [rs_start, rs_end],
                           [complex(1.0), complex(-1j * ref)],
                           rtol=1e-11, atol=1e-13,
                           max_step=max_step, dense_output=True)

            psi, dpsi = sol.y[:, -1]
            A = (dpsi + 1j * ref * psi) / (2j * ref)
            B = (dpsi - 1j * ref * psi) / (-2j * ref)

            ratio = abs(B / A) if abs(A) > 1e-300 else float('inf')
            print(f"    Npts={Npts}: |B/A| at r*={rs_end:.0f} = {ratio:.6e}")

        # Scan
        print(f"\n  Coarse scan near Berti:")
        best = scan_b_ratio(l, -60, 150,
                           [ref.real - 0.1, ref.real + 0.1],
                           [ref.imag - 0.04, ref.imag + 0.04],
                           0.025, 0.01)
        if best:
            for br, w in best[:5]:
                print(f"    omega = {w.real:.4f} - {abs(w.imag):.4f}i, |B/A| = {br:.6e}")
        else:
            print("    No good results in scan range.")

        # Refine near best
        if best:
            best_br, best_w = best[0]
            print(f"\n  Refinement around {best_w.real:.4f} - {abs(best_w.imag):.4f}i:")
            refined = scan_b_ratio(l, -60, 150,
                                  [best_w.real - 0.05, best_w.real + 0.05],
                                  [best_w.imag - 0.02, best_w.imag + 0.02],
                                  0.01, 0.005)
            if refined:
                for br, w in refined[:5]:
                    print(f"    omega = {w.real:.5f} - {abs(w.imag):.5f}i, |B/A| = {br:.6e}")
                print(f"    Best: omega = {refined[0][1].real:.5f} - {abs(refined[0][1].imag):.5f}i")
            else:
                print("    No refined results.")

        # Direct optimization
        print(f"\n  Direct Nelder-Mead optimization:")
        omega_opt, br_opt = shooting_eigenvalue(l, -60, 120)
        print(f"    omega = {omega_opt.real:.6f} - {abs(omega_opt.imag):.6f}i")
        print(f"    |B/A| = {br_opt:.6e}")
        rel_err = abs(omega_opt - ref) / abs(ref)
        print(f"    Rel error vs Berti: {rel_err:.2e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
