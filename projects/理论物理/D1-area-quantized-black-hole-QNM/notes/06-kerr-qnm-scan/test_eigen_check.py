#!/usr/bin/env python3
"""
Different eigenvalue criterion: ratio of psi to dpsi.
Instead of Wronskian, check: does log-derivative match at rs_m?
log_der_h = dpsi_h/dpsi_h / psi_h
log_der_f = dpsi_f/dpsi_f / psi_f
At eigenvalue: log_der_h == log_der_f
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
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - c * M / r**3)

def log_deriv_match(omega, l, rs_h=-50, rs_inf=150, rs_m=80, c=6.0):
    """Return |log_der_h - log_der_f| at rs_m."""
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

    # Log derivatives
    ldh = dph / ph if abs(ph) > 1e-200 else None
    ldf = dpf / pf if abs(pf) > 1e-200 else None

    if ldh is None or ldf is None:
        return None

    diff = abs(ldh - ldf)
    return diff, ldh, ldf


def main():
    print("=" * 80)
    print("Log-Derivative Matching Criterion")
    print("=" * 80)

    for l in [2, 3]:
        ref = BERTI_REF[l]
        print(f"\nl = {l}, Berti: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        # At Berti reference
        result = log_deriv_match(ref, l, c=6.0)
        if result:
            diff, ldh, ldf = result
            print(f"  |log_der_h - log_der_f| at Berti: {diff:.6e}")
            print(f"    log_der_h = {ldh:.6e} (phase={np.angle(ldh):.4f})")
            print(f"    log_der_f = {ldf:.6e} (phase={np.angle(ldf):.4f})")

            # Also check psi ratio
            def V(r, l=l): return rw_potential(r, l, c=6.0)
            def deriv(rst, Y, om=ref):
                r = r_from_rstar(rst)
                if r <= 2.0*M+1e-14: r = 2.0*M+1e-14
                return [Y[1], -(om**2 - V(r))*Y[0]]
            s1 = solve_ivp(deriv, [-50, 80], [1, -1j*ref], rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
            s2 = solve_ivp(deriv, [150, 80], [1, +1j*ref], rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
            ph = s1.sol(80)
            pf = s2.sol(80)
            ratio = ph[0] / pf[0]
            dratio = ph[1] / pf[1]
            print(f"    psi_h/psi_f = {ratio:.6e} (ratio should be constant for eigenvalue)")
            print(f"    dpsi_h/dpsi_f = {dratio:.6e}")

        # Scan for minimum log-derivative mismatch
        print(f"  Scan (11x11 grid):")
        best = []
        for dr in np.linspace(-0.15, 0.2, 15):
            for di in np.linspace(-0.1, 0.1, 15):
                omega = ref + complex(dr, di)
                result = log_deriv_match(omega, l, rs_m=80, c=6.0)
                if result:
                    diff, _, _ = result
                    best.append((diff, omega))
        best.sort()
        for diff, omega in best[:5]:
            print(f"    {omega.real:.5f}{omega.imag:.5f}i: |Δld| = {diff:.6e}")

    # For l=2: look at log-derivative mismatch vs. wronskian
    print(f"\n" + "="*80)
    print("Cross-comparison: Wronskian vs log-derivative mismatch (l=2, c=6)")
    print("="*80)

    def wronskian_raw(omega, l=2, c=6.0):
        def deriv(rs, Y):
            r = r_from_rstar(rs)
            if r <= 2.0 * M + 1e-14:
                r = 2.0 * M + 1e-14
            V = rw_potential(r, l, c)
            return [Y[1], -(omega**2 - V) * Y[0]]
        s1 = solve_ivp(deriv, [-50, 80], [1, -1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
        s2 = solve_ivp(deriv, [150, 80], [1, +1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
        if not (s1.success and s2.success):
            return None, None
        ph, dph = s1.sol(80)
        pf, dpf = s2.sol(80)
        W = abs(ph*dpf - dph*pf)
        return W

    # Compare criteria for a few values
    omegas = [
        BERTI_REF[2],
        complex(0.574, -0.039),
        complex(0.454, -0.029),
    ]
    for w in omegas:
        W = wronskian_raw(w)
        res = log_deriv_match(w, 2, c=6.0)
        ld = res[0] if res else None
        if W is not None and ld is not None:
            print(f"  {w.real:.4f}{w.imag:.4f}i: |W|={W:.6e},  |Δld|={ld:.6e}")

    # Now scan through 1D imaginary part
    print(f"\n1D scan: vary Im(ω), fix Re(ω)=0.374")
    for re in [0.374, 0.454, 0.574]:
        print(f"  Re(ω) = {re}:")
        best_ld = []
        best_W = []
        for im in np.linspace(-0.2, 0.0, 21):
            w = complex(re, im)
            W = wronskian_raw(w)
            res = log_deriv_match(w, 2, c=6.0)
            if W is not None and res is not None:
                W, ld = W, res[0]
                best_W.append((W, im))
                best_ld.append((ld, im))
        best_ld.sort()
        best_W.sort()
        print(f"    Best |Δld| at Im={best_ld[0][1]:.4f}: {best_ld[0][0]:.6e}")
        print(f"    Best |W| at Im={best_W[0][1]:.4f}: {best_W[0][0]:.6e}")


if __name__ == "__main__":
    main()
