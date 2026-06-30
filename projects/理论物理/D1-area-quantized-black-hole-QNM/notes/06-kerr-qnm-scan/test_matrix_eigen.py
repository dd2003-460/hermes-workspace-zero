#!/usr/bin/env python3
"""
Quick eigenvalue diagnostic: shooting method with compact grid search.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
from scipy.optimize import minimize

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def r_from_rs(rs):
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(40):
        if r <= 2 * M:
            r = 2 * M + 1e-14
            continue
        rs_calc = r + 2 * M * np.log(r / (2 * M) - 1.0)
        drstar_dr = r ** 2 / (r - 2 * M) ** 2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-16:
            break
        r -= dr
        if r <= 2 * M:
            r = 2 * M + 1e-14
    return r


def V(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)


def ode(rs, Y, omega, l):
    r = r_from_rs(rs)
    r = max(r, 2 * M + 1e-14)
    Vv = V(r, l)
    return [Y[1], -(omega ** 2 - Vv) * Y[0]]


def shooting_W(omega, l, rs_m):
    """Wronskian at matching point. |W| = 0 at eigenvalue."""
    try:
        s1 = solve_ivp(lambda rs, Y: ode(rs, Y, omega, l),
                       [-70, rs_m], [1.0, -1j*omega],
                       rtol=1e-10, atol=1e-12, max_step=1.0)
        s2 = solve_ivp(lambda rs, Y: ode(rs, Y, omega, l),
                       [200, rs_m], [1.0, +1j*omega],
                       rtol=1e-10, atol=1e-12, max_step=1.0)
        if not (s1.success and s2.success):
            return 1e100
        ph, dph = s1.y[:, -1]
        pf, dpf = s2.y[:, -1]
        if abs(ph) < 1e-100 or abs(pf) < 1e-100:
            return 1e100
        return abs(ph * dpf - dph * pf) / (abs(ph) * abs(pf))
    except:
        return 1e100


def riccati_W(omega, l, rs_m):
    """Riccati log-derivative mismatch."""
    def deriv(rs, f):
        r = r_from_rs(rs)
        r = max(r, 2 * M + 1e-14)
        Vv = V(r, l)
        return [-(omega ** 2 - Vv) - f[0] ** 2]
    try:
        s1 = solve_ivp(deriv, [-50, rs_m], [-1j*omega],
                      rtol=1e-12, atol=1e-14, max_step=0.5)
        s2 = solve_ivp(deriv, [200, rs_m], [+1j*omega],
                      rtol=1e-12, atol=1e-14, max_step=0.5)
        if not (s1.success and s2.success):
            return 1e100, None, None
        fh = s1.y[0, -1]
        fi = s2.y[0, -1]
        return abs(fh - fi), fh, fi
    except:
        return 1e100, None, None


def main():
    for l in [2, 3]:
        ref = BERTI[l]
        print(f"\nl={l}: Berti = {ref.real:.5f}{ref.imag:.5f}i")

        # ----- Test at BERTI value -----
        print(f"  At Berti (rs_m=80):")
        Wb = shooting_W(ref, l, 80)
        errb, _, _ = riccati_W(ref, l, 80)
        print(f"    Shooting |W| = {Wb:.6e}")
        print(f"    Riccati |diff| = {errb:.6e}")

        # Quick check: does V(omega^2 - V) = 0 anywhere near?
        for r_test in [2.5, 3.0, 4.0, 5.0, 6.0]:
            r = max(r_test, 2*M+0.01)
            Vv = V(r, l)
            print(f"    r={r:.2f}: V={Vv:.6f}, omega^2={ref**2:.6f}")

        # ----- Narrow grid search (11x11) around Berti -----
        print(f"  Grid search (11x11, rs_m=80):")
        best = []
        for rr in np.linspace(ref.real-0.15, ref.real+0.15, 11):
            for ri in np.linspace(ref.imag-0.1, ref.imag+0.1, 11):
                w = complex(rr, ri)
                W = shooting_W(w, l, 80)
                best.append((W, w))
        best.sort()
        print(f"    Best: {best[0][1].real:.5f}{best[0][1].imag:.5f}i, |W|={best[0][0]:.6e}")
        print(f"    2nd:  {best[1][1].real:.5f}{best[1][1].imag:.5f}i, |W|={best[1][0]:.6e}")
        print(f"    3rd:  {best[2][1].real:.5f}{best[2][1].imag:.5f}i, |W|={best[2][0]:.6e}")

        # Same for Riccati
        print(f"  Riccati search (11x11):")
        best_r = []
        for rr in np.linspace(ref.real-0.15, ref.real+0.15, 11):
            for ri in np.linspace(ref.imag-0.1, ref.imag+0.1, 11):
                w = complex(rr, ri)
                err, fh, fi = riccati_W(w, l, 80)
                best_r.append((err, w, fh, fi))
        best_r.sort()
        for i in range(3):
            print(f"    {i+1}: {best_r[i][1].real:.5f}{best_r[i][1].imag:.5f}i, err={best_r[i][0]:.6e}, fh={best_r[i][2]:.6f}, fi={best_r[i][3]:.6f}")

        # ----- Wider grid search (21x21) -----
        print(f"  Wider grid (21x21, rs_m=80):")
        best_wide = []
        for rr in np.linspace(ref.real-0.25, ref.real+0.30, 21):
            for ri in np.linspace(ref.imag-0.15, ref.imag+0.15, 21):
                w = complex(rr, ri)
                W = shooting_W(w, l, 80)
                best_wide.append((W, w))
        best_wide.sort()
        for i in range(3):
            print(f"    {i+1}: {best_wide[i][1].real:.5f}{best_wide[i][1].imag:.5f}i, |W|={best_wide[i][0]:.6e}")
            rel = abs((best_wide[i][1] - ref) / ref)
            print(f"        rel_err = {rel:.2e}")


if __name__ == "__main__":
    main()
