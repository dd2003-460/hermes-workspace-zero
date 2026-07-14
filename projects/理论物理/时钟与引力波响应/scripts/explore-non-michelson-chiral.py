#!/usr/bin/env python3
"""
Explore non-Michelson linear combinations for chiral ORF in triangular OLC.

Computes Gamma^V (chiral ORF) for mixed combinations of:
  - Standard Michelsons: M_X, M_Y, M_Z (each = sum of opposite links)
  - E-like: M_E = M_X - M_Y
  - T-like: M_T = M_X + M_Y + M_Z

Tests cross-correlation pairs to find non-zero chiral signals.
"""
import numpy as np

c = 299792458.0


def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function (Lou Eq. 2-30)."""
    f_arr = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f_arr) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f_arr) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


def olc_link_response_grid(f, tG, pG, arm_theta, arm_phi, L):
    """GW response for a single OLC link over sky grid."""
    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)
    cos_nu = (nx*np.sin(arm_theta)*np.cos(arm_phi)
             + ny*np.sin(arm_theta)*np.sin(arm_phi)
             + nz*np.cos(arm_theta))
    T = olc_transfer_function(np.ones_like(tG), L, cos_nu)

    ct, st = np.cos(tG), np.sin(tG)
    cp, sp = np.cos(pG), np.sin(pG)
    th = np.stack([ct*cp, ct*sp, -st])
    ph = np.stack([-sp, cp, np.zeros_like(sp)])

    ux = np.sin(arm_theta)*np.cos(arm_phi)
    uy = np.sin(arm_theta)*np.sin(arm_phi)
    uz = np.cos(arm_theta)

    R_plus = (th[0]*ux)**2 + (th[1]*uy)**2 + (th[2]*uz)**2 \
           - (ph[0]*ux)**2 - (ph[1]*uy)**2 - (ph[2]*uz)**2
    R_cross = 2.0*(th[0]*ux)*(ph[0]*ux) + 2.0*(th[1]*uy)*(ph[1]*uy) \
            + 2.0*(th[2]*uz)*(ph[2]*uz)
    return R_plus * T, R_cross * T


def link_direction(r_from, r_to):
    """Link direction unit vector. Returns (theta, phi, L)."""
    d = r_to - r_from
    d_norm = np.linalg.norm(d)
    ux, uy, uz = d[0]/d_norm, d[1]/d_norm, d[2]/d_norm
    theta = np.arccos(np.clip(uz, -1.0, 1.0))
    phi = np.arctan2(uy, ux)
    return theta, phi, d_norm


def compute_variable_on_sky(f, wdict, links_dict, tG, pG, L):
    """Compute response of any variable (linear combo of links) over sky grid."""
    Rp = np.zeros_like(tG, dtype=complex)
    Rx = np.zeros_like(tG, dtype=complex)
    for (i, j), w in wdict.items():
        theta_link, phi_link, ll = links_dict[(i, j)]
        Rp_p, Rx_x = olc_link_response_grid(f, tG, pG, theta_link, phi_link, L)
        Rp += w * Rp_p
        Rx += w * Rx_x
    return Rp, Rx


def run_exploration():
    """Compute chiral and standard ORF for non-Michelson combinations."""
    f = 0.030  # 30 mHz
    L = 2.5e9  # 2.5 Gm

    print("=" * 65)
    print("Non-Michelson Chiral ORF Exploration for Triangular OLC")
    print("=" * 65)
    print(f"  f = {f*1e3:.0f} mHz, L = {L/1e9:.1f} Gm")

    # Satellite positions (equilateral triangle in xy-plane)
    tri = np.array([
        [0.0, 0.0, 0.0],
        [L, 0.0, 0.0],
        [L/2, L*np.sqrt(3)/2, 0.0]
    ])

    # Link directions
    links = {}
    for (i, j) in [(0,1),(1,0),(1,2),(2,1),(2,0),(0,2)]:
        links[(i,j)] = link_direction(tri[i], tri[j])

    # ━━━ Define variables via link-weight dictionaries ━━━━━━━━━━━━━━━━━━━━━
    variables = {
        'M_X': {(0,1): 1.0, (1,0): 1.0},
        'M_Y': {(1,2): 1.0, (2,1): 1.0},
        'M_Z': {(2,0): 1.0, (0,2): 1.0},
        'M_E': {(0,1): 1.0, (1,0): 1.0, (1,2): -1.0, (2,1): -1.0},  # M_X - M_Y
        'M_T': {(0,1): 1.0, (1,0): 1.0, (1,2): 1.0, (2,1): 1.0,
                (2,0): 1.0, (0,2): 1.0},  # M_X + M_Y + M_Z
    }

    # ━━━ Sky-averaged standard ORF (auto) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print()
    print("Sky-averaged standard ORF (auto-correlation, |R_+|^2 + |R_x|^2):")

    thetas = np.linspace(0, np.pi, 16)
    phis = np.linspace(0, 2*np.pi, 32, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/32) * (np.pi/16)

    auto_orf = {}
    for name, wdict in variables.items():
        Rp, Rx = compute_variable_on_sky(f, wdict, links, tG, pG, L)
        auto_orf[name] = np.real(np.sum((np.abs(Rp)**2 + np.abs(Rx)**2) * dO))
        print(f"    {name:6s}: {auto_orf[name]:.4f}")

    print()

    # ━━━ Standard ORF (cross-correlation) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pair_names = [
        ('M_X', 'M_Y'), ('M_E', 'M_X'), ('M_T', 'M_E'),
        ('M_X', 'M_T'), ('M_E', 'M_Y'), ('M_X', 'M_Z'),
        ('M_T', 'M_X'), ('M_E', 'M_T'),
    ]

    print("Standard ORF (cross-correlation, sky-averaged):")
    print(f"    {'Pair':<20s}  {'<Gamma^I>':>12s}")
    print(f"    {'-'*20}  {'-'*12}")

    std_orf = {}
    for name1, name2 in pair_names:
        Rp1, Rx1 = compute_variable_on_sky(f, variables[name1], links, tG, pG, L)
        Rp2, Rx2 = compute_variable_on_sky(f, variables[name2], links, tG, pG, L)

        corr = np.sum(np.real(Rp1 * np.conj(Rp2) + Rx1 * np.conj(Rx2)) * dO)
        norm = np.sqrt(
            np.abs(np.sum((np.abs(Rp1)**2 + np.abs(Rx1)**2) * dO))
            * np.abs(np.sum((np.abs(Rp2)**2 + np.abs(Rx2)**2) * dO)))
        gamma_I = corr / norm if norm > 1e-30 else 0.0
        std_orf[(name1, name2)] = gamma_I
        print(f"    <{name1}, {name2}>{'':<7s}  {gamma_I:.6f}")

    print()

    # ━━━ Chiral ORF (cross-correlation) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("Chiral ORF (cross-correlation, sky-averaged):")
    print(f"    {'Pair':<20s}  {'<Gamma^V>':>14s}  {'|Gamma^V|':>12s}")
    print(f"    {'-'*20}  {'-'*14}  {'-'*12}")

    chiral_orf = {}
    for name1, name2 in pair_names:
        Rp1, Rx1 = compute_variable_on_sky(f, variables[name1], links, tG, pG, L)
        Rp2, Rx2 = compute_variable_on_sky(f, variables[name2], links, tG, pG, L)

        # Chiral factor: Re(Rp1 * conj(Rx2) - Rx1 * conj(Rp2))
        chiral_factor = np.real(Rp1 * np.conj(Rx2) - Rx1 * np.conj(Rp2))
        corr = np.sum(chiral_factor * dO)

        auto1 = np.sum((np.abs(Rp1)**2 + np.abs(Rx1)**2) * dO)
        auto2 = np.sum((np.abs(Rp2)**2 + np.abs(Rx2)**2) * dO)
        norm = np.sqrt(np.abs(auto1) * np.abs(auto2))

        gamma_V = corr / norm if norm > 1e-30 else 0.0
        chiral_orf[(name1, name2)] = gamma_V
        print(f"    <{name1}, {name2}>{'':<7s}  {gamma_V:14.6e}  {np.abs(gamma_V):12.6e}")

    print()

    # ━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("=" * 65)
    print("SUMMARY: Nonzero Gamma^V pairs (|Gamma^V| > 1e-6):")
    nonzero_pairs = [(k, v) for k, v in chiral_orf.items() if np.abs(v) > 1e-6]
    if nonzero_pairs:
        for (n1, n2), gv in nonzero_pairs:
            sig_str = "SIGNIFICANT" if np.abs(gv) > 1e-3 else "marginal"
            print(f"  <{n1}, {n2}>: {gv:.6e}  [{sig_str}]")
    else:
        print("  None found (all Gamma^V consistent with zero)")

    print(f"\n  Key finding:")
    if chiral_orf:
        max_abs_item = max(chiral_orf.items(), key=lambda x: np.abs(x[1]))
        print(f"  Maximum |Gamma^V| = {max_abs_item[1]:.6e} for pair {max_abs_item[0]}")
    print("=" * 65)

    # ━━━ Check symmetry: Gamma^V(a,b) == -Gamma^V(b,a) ━━━━━━━━━━━━━━━━━━
    print("\nSymmetry check (Gamma^V(a,b) vs -Gamma^V(b,a)):")
    for name1, name2 in pair_names:
        gv_12 = chiral_orf.get((name1, name2), 0)
        gv_21 = chiral_orf.get((name2, name1), 0)
        ratio = gv_12/gv_21 if gv_21 != 0 else float('nan')
        print(f"  <{name1}, {name2}> = {gv_12:.6e},  <{name2}, {name1}> = {gv_21:.6e}, "
              f"ratio = {ratio:.4f}")


if __name__ == '__main__':
    run_exploration()
