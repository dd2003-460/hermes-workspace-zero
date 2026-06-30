#!/usr/bin/env python3
"""
Direct comparison: potential landscape vs Riccati fixed points.
Focus on what omega the Riccati method ACTUALLY finds.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
from scipy.optimize import minimize_scalar

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


def test_riccati_path(omega, l, rs_start, bc_sign):
    """Integrate Riccati from rs_start with given BC sign."""
    def deriv(rs, f):
        r = r_from_rs(rs)
        r = max(r, 2 * M + 1e-14)
        Vv = V(r, l)
        return [-(omega ** 2 - Vv) - f[0] ** 2]

    bc = bc_sign * (-1j) * omega  # -i*omega for ingoing, +i*omega for outgoing

    s = solve_ivp(deriv, [rs_start, 0.0], [bc],
                 rtol=1e-12, atol=1e-14, max_step=0.3)
    return s


def scan_1d_riccati(l, omref):
    """1D scan over Re(omega), fix Im(omega)."""
    results = []
    for rr in np.linspace(omref.real - 0.2, omref.real + 0.3, 40):
        w = complex(rr, omref.imag)
        # Riccati mismatch at rs=0
        s1 = test_riccati_path(w, l, -50.0, +1)  # horizon: f(-50) = -i*omega
        s2_pos = test_riccati_path(w, l, 200.0, +1)  # infinity: f(200) = +i*omega
        s2_neg = test_riccati_path(w, l, 200.0, -1)  # infinity: f(200) = -i*omega

        fh = s1.y[0, -1]
        fp = s2_pos.y[0, -1]
        fn = s2_neg.y[0, -1]

        err_pos = abs(fh - fp)
        err_neg = abs(fh - fn)

        # What is V - omega^2 at rs=0?
        r0 = r_from_rs(0.0)
        V0 = V(r0, l)
        Vomega2 = complex(np.real(V0 - w**2), 0)  # wrong, this is real

        results.append((err_pos, w, fh, fp, fn))
    results.sort()
    return results[:5]


def scan_riccati_over_FH(omega, l):
    """Track f_h(r*) along the path from horizon to infinity."""
    def deriv(rs, f):
        r = r_from_rs(rs)
        r = max(r, 2 * M + 1e-14)
        Vv = V(r, l)
        return [-(omega ** 2 - Vv) - f[0] ** 2]

    s = solve_ivp(deriv, [-50, 50], [-1j*omega],
                 rtol=1e-12, atol=1e-14, max_step=0.2, dense_output=True)

    # Evaluate at specific points using the dense output
    sol_fn = s.sol
    rs_grid = np.linspace(-50, 50, 41)
    fvals = []
    for rs_t in rs_grid:
        f_r = sol_fn(rs_t)[0]
        r_r = r_from_rs(rs_t)
        V_r = V(r_r, l)
        fvals.append((rs_t, f_r, r_r, V_r))

    return fvals


def main():
    print("=" * 70)
    print("Riccati path tracing")
    print("=" * 70)

    for l in [2, 3]:
        ref = BERTI[l]
        print(f"\nl={l}, Berti: {ref.real:.5f}{ref.imag:.5f} i")

        # Scan along f_h path
        print(f"  Riccati path for f_h from horizon (omega = Berti):")
        fvals = scan_riccati_over_FH(ref, l)
        print(f"  {'rs*':>6s} {'r':>8s} {'V':>12s} {'f_h':>20s} {'+i*omega':>20s}")
        for rs_t, f_r, r_r, V_r in fvals:
            fiw = 1j * ref
            print(f"  {rs_t:6.1f} {r_r:8.4f} {V_r:12.6f} {f_r:>20.12f} {fiw:>20.12f}")

        # Also track f_h at the "found" eigenvalue (from previous scans)
        print(f"\n  Finding minimum Riccati mismatch...")

        best_omega = None
        best_err = 1e100

        for rr in np.linspace(ref.real - 0.25, ref.real + 0.30, 50):
            w = complex(rr, ref.imag)
            s1 = test_riccati_path(w, l, -50.0, +1)
            s2_pos = test_riccati_path(w, l, 200.0, +1)
            fh = s1.y[0, -1]
            fp = s2_pos.y[0, -1]
            err = abs(fh - fp)
            if err < best_err:
                best_err = err
                best_omega = w

        print(f"  Best at fixed Im = {ref.imag}: omega = {best_omega.real:.5f}{best_omega.imag:.5f} i")
        print(f"  err = {best_err:.6e}")

        # Now scan over both Re and Im
        print(f"\n  2D grid scan (30x30):")
        best2d = 1e100
        best2d_w = None
        for rr in np.linspace(ref.real - 0.2, ref.real + 0.3, 30):
            for ri in np.linspace(ref.imag - 0.1, ref.imag + 0.1, 30):
                w = complex(rr, ri)
                s1 = test_riccati_path(w, l, -50.0, +1)
                s2_pos = test_riccati_path(w, l, 200.0, +1)
                fh = s1.y[0, -1]
                fp = s2_pos.y[0, -1]
                err = abs(fh - fp)
                if err < best2d:
                    best2d = err
                    best2d_w = w

        print(f"  Best: {best2d_w.real:.5f}{best2d_w.imag:.5f} i, err = {best2d:.6e}")
        rel = abs((best2d_w - ref) / ref)
        print(f"  rel_err from Berti = {rel:.2e}")

        # V and fixed-point analysis at rs=0 for best omega
        r0 = r_from_rs(0.0)
        V0 = V(r0, best2d_w)
        Vomega = V0 - best2d_w ** 2
        print(f"  At rs=0 for best omega:")
        print(f"    V = {V0:.6f}")
        print(f"    omega^2 = {best2d_w**2:.6f}")
        print(f"    V - omega^2 = {Vomega:.6f}")
        print(f"    -omega^2 = {(-best2d_w**2):.6f}")
        print(f"    +i*omega = {1j*best2d_w:.6f}")
        print(f"    -i*omega = {-1j*best2d_w:.6f}")

        # Check: what are the Riccati FP?
        # f^2 = V - omega^2 (when f' = 0, meaning f is constant)
        # So fixed points are f = +/- sqrt(V - omega^2)
        try:
            sqrt_fp = np.sqrt(Vomega)
            print(f"    +/- sqrt(V - omega^2) = +/-{sqrt_fp:.6f}")
        except:
            print(f"    V - omega^2 = real, no complex sqrt needed")

    print("\n" + "=" * 70)
    print("Wronskian scan")
    print("=" * 70)

    for l in [2]:
        ref = BERTI[l]
        print(f"\nl={l}, Berti: {ref.real:.5f}{ref.imag:.5f} i")

        # Wronskian scan at rs_m=80
        print(f"  Wronskian at rs_m=80:")
        best_W = 1e100
        best_w = None
        for rr in np.linspace(ref.real - 0.2, ref.real + 0.3, 30):
            for ri in np.linspace(ref.imag - 0.1, ref.imag + 0.1, 30):
                w = complex(rr, ri)
                try:
                    s1 = solve_ivp(lambda rs, Y: [Y[1], -(w**2 - V(r_from_rs(rs), l))*Y[0]],
                                  [-70, 80], [1.0, -1j*w], rtol=1e-10, atol=1e-12, max_step=1.0)
                    s2 = solve_ivp(lambda rs, Y: [Y[1], -(w**2 - V(r_from_rs(rs), l))*Y[0]],
                                  [200, 80], [1.0, +1j*w], rtol=1e-10, atol=1e-12, max_step=1.0)
                    if s1.success and s2.success:
                        ph, dph = s1.y[:, -1]
                        pf, dpf = s2.y[:, -1]
                        if abs(ph) > 1e-100 and abs(pf) > 1e-100:
                            W = abs(ph*dpf - dph*pf) / (abs(ph)*abs(pf))
                            if W < best_W:
                                best_W = W
                                best_w = w
                except:
                    pass

        if best_w:
            print(f"  Best: {best_w.real:.5f}{best_w.imag:.5f} i, |W| = {best_W:.6e}")
            rel = abs((best_w - ref) / ref)
            print(f"  rel_err from Berti = {rel:.2e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
