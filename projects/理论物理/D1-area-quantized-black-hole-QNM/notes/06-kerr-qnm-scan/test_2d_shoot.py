#!/usr/bin/env python3
"""
2D grid shoot-and-match: integrate from horizon and check how much
of the outgoing component grows at large r*. Minimize B/A directly.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0
BERTI_REF = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


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


def b_over_a_ratio(omega, l, rs_h=-50, rs_inf=150, rs_m=100, c=6.0):
    """
    Integrate from horizon to rs_m.
    At rs_m, decompose into A (outgoing exp(iωr*)) and B (ingoing exp(-iωr*)).
    B/A is the unwanted component. QNM requires B→0.

    Returns (|B/A|, log_der_h, psiph, psiphh) at rs_m
    """
    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l, c)
        return [Y[1], -(omega**2 - V) * Y[0]]

    s = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j * omega],
                  rtol=1e-11, atol=1e-13, max_step=0.2, dense_output=True)

    if not s.success:
        return None

    psiph, psiphh = s.y[:, -1]  # psi and dpsi/dra* at rs_m

    # Decompose into outgoing/incoming at rs_m
    # psi = A*exp(iωr*) + B*exp(-iωr*)
    # dpsi/dr* = iω*A*exp(iωr*) - iω*B*exp(-iωr*)
    # A*exp(iωr*) = (dpsi/dr* + iω*psi)/(2iω)
    # B*exp(-iωr*) = (dpsi/dr* - iω*psi)/(-2iω)
    exp_iwrs = np.exp(1j * omega * rs_m)
    exp_miwrs = np.exp(-1j * omega * rs_m)
    A = (psiphh + 1j * omega * psiph) / (2j * omega)
    B = (psiphh - 1j * omega * psiph) / (-2j * omega)

    ba_ratio = abs(B / A) if abs(A) > 1e-200 else float('inf')
    return ba_ratio, (psiphh/psiph if abs(psiph) > 1e-200 else None), psiph, psiphh


def match_angular(omega, l, rs_from_h, rs_from_i, rs_m, c=6.0):
    """
    Shoot from BOTH sides to rs_m.
    Return |Wronskian| and |B/A from horizon|.
    """
    res_h = b_over_a_ratio(omega, l, rs_h=rs_from_h, rs_m=rs_m, c=c)
    if res_h is None:
        return None, None

    ba_h, ld_h, ph, dph = res_h

    # From infinity
    def deriv(rs, Y, om=omega):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l, c=c)
        return [Y[1], -(om**2 - V) * Y[0]]

    s = solve_ivp(deriv, [rs_from_i, rs_m], [1.0, +1j * omega],
                  rtol=1e-11, atol=1e-13, max_step=0.2, dense_output=True)
    if not s.success:
        return None, None

    pf, dpf = s.y[:, -1]
    W = abs(ph * dpf - dph * pf)

    return W, ba_h


def main():
    print("=" * 80)
    print("B/A + Wronskian Scan (horizon -> rs_m, infinity -> rs_m)")
    print("=" * 80)

    for l in [2, 3]:
        ref = BERTI_REF[l]
        print(f"\nl = {l}, Berti: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        # Check at Berti
        result = b_over_a_ratio(ref, l, rs_m=100, c=6.0)
        if result:
            ba, ld, ph, dph = result
            print(f"  At Berti, rs_m=100: |B/A| = {ba:.6e}, log_der_h = {ph and ld}")

        # Test various matching radii
        print(f"  rs_m = rs_m vs |W| and |B/A| at Berti:")
        for rs_m in [40, 60, 80, 100, 120]:
            result = match_angular(ref, l, -50, 150, rs_m, c=6.0)
            if result:
                w, ba = result
                if ba is not None:
                    print(f"    rs_m={rs_m}: |W|={w:.6e}, |B/A|={ba:.6e}")
                else:
                    print(f"    rs_m={rs_m}: |W|={w:.6e}")

        # Grid scan
        print(f"  Scan (17x11 grid):")
        best = []
        for dr in np.linspace(-0.15, 0.25, 17):
            for di in np.linspace(-0.12, 0.1, 11):
                omega = ref + complex(dr, di)
                ba, ld, ph, dph = b_over_a_ratio(omega, l, rs_m=80, c=6.0)
                if ba is not None:
                    best.append((ba, omega))
        best.sort()
        for ba, omega in best[:5]:
            print(f"    {omega.real:.5f}{omega.imag:.5f}i: |B/A| = {ba:.6e}")

    # Focused scan for l=2
    print(f"\n{'='*80}")
    print("Focused l=2 scan: |B/A| as function of ω")
    print("="*80)

    re_range = np.linspace(0.35, 0.65, 31)
    im_range = np.linspace(-0.12, 0.00, 25)

    for rs_m in [80, 120]:
        print(f"\n  rs_m = {rs_m}, c=6:")
        for re in re_range[::5]:  # every 5th Re value
            row = []
            for im in im_range[::5]:  # every 5th Im value
                ba, ld, ph, dph = b_over_a_ratio(
                    complex(re, im), 2, rs_m=rs_m, c=6.0)
                row.append(ba if ba is not None else np.inf)
            row = np.array(row)
            if np.any(row < 1e30):
                idx = np.argmin(row)
                best_idx = idx * 5
                print(f"    Re={re:.3f}: min |B/A| = {row[idx]:.6e} at Im = {im_range[best_idx]:.4f}")

    # The key test: at various ω, what's the B/A ratio at infinity?
    print(f"\n{'='*80}")
    print("B/A vs A/B at infinity (pure test)")
    print("="*80)

    # For pure outgoing wave at infinity: A≠0, B=0
    # B/A = 0 is the condition
    test_vals = [
        ("Berti l=2", complex(0.37367, -0.08896)),
        ("Min found", complex(0.574, -0.039)),
        ("Min 2 found", complex(0.454, -0.029)),
    ]
    for name, w in test_vals:
        ba100, _, _, _ = b_over_a_ratio(w, 2, rs_m=100, c=6.0)
        ba150, _, _, _ = b_over_a_ratio(w, 2, rs_m=150, c=6.0)
        ba80, _, _, _ = b_over_a_ratio(w, 2, rs_m=80, c=6.0)
        print(f"  {name} ({w.real:.4f}{w.imag:.4f}i): |B/A| at r*=80={ba80:.6e}, r*=100={ba100:.6e}, r*=150={ba150:.6e}")

    # Cross-check: what ω gives B/A = 0? Let me do a very fine scan
    print(f"\nFine 1D scan around |B/A| minimum for l=2:")
    print(f"  Scanning Im(ω) with Re(ω) fixed at minimum:")
    best_2d = []
    for re in np.linspace(0.45, 0.60, 16):
        for im in np.linspace(-0.12, 0.0, 25):
            ba, _, _, _ = b_over_a_ratio(complex(re, im), 2, rs_m=80, c=6.0)
            if ba is not None:
                best_2d.append((ba, complex(re, im)))
    best_2d.sort()
    for ba, omega in best_2d[:8]:
        rel_err = abs(omega - BERTI_REF[2]) / abs(BERTI_REF[2])
        print(f"    {omega.real:.5f}{omega.imag:.5f}i: |B/A|={ba:.6e}  rel_err_vs_berti={rel_err:.3f}")

    print(f"\n" + "="*80)
    print("B/A vs. Wronskian for same 12 candidates")
    print("="*80)
    # Show table
    candidates = best_2d[:12]
    print(f"  {'Re':>8s} {'Im':>8s} | {'B/A':>12s} | {'|W| at Berti':>12s} | | {'W at cand':>12s} |")
    print(f"  {'─'*8} {'─'*8}   {'─'*12}   {'─'*12}   {'─'*12}")
    for ba, omega in candidates:
        W_at_berti, ba_berti = match_angular(BERTI_REF[2], 2, -50, 150, 80, c=6.0)
        W_at_cand, _ = match_angular(omega, 2, -50, 150, 80, c=6.0)
        print(f"  {omega.real:>7.4f} {omega.imag:>7.4f} | {ba:>11.4e} | {W_at_berti:>11.4e} | | {W_at_cand:>11.4e} |")


if __name__ == "__main__":
    main()
