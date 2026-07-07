#!/usr/bin/env python3
"""
Test non-Michelson combinations on a non-symmetric (non-equilateral) triangle.
Determines whether the zero Gamma^V is a consequence of mirror symmetry
or a fundamental property of the OLC transfer function.
"""
import numpy as np

c = 299792458.0


def olc_transfer_function(f, L, cos_nu):
    f_arr = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f_arr) * L / c
    one_minus = 1.0 - np.abs(cos_nu)
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f_arr) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


def olc_link_response_grid(f, tG, pG, arm_theta, arm_phi, L):
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
    d = r_to - r_from
    d_norm = np.linalg.norm(d)
    ux, uy, uz = d[0]/d_norm, d[1]/d_norm, d[2]/d_norm
    theta = np.arccos(np.clip(uz, -1.0, 1.0))
    phi = np.arctan2(uy, ux)
    return theta, phi, d_norm


def compute_variable_on_sky(f, wdict, links_dict, tG, pG, L):
    Rp = np.zeros_like(tG, dtype=complex)
    Rx = np.zeros_like(tG, dtype=complex)
    for (i, j), w in wdict.items():
        theta_link, phi_link, ll = links_dict[(i, j)]
        Rp_p, Rx_x = olc_link_response_grid(f, tG, pG, theta_link, phi_link, L)
        Rp += w * Rp_p
        Rx += w * Rx_x
    return Rp, Rx


def test_configuration(tri_name, tri_positions, freq, L):
    """Test all pairs of variables on a given triangle configuration."""
    print(f"\n{'='*60}")
    print(f"Configuration: {tri_name}")
    print(f"{'='*60}")

    # Link directions
    links = {}
    for (i, j) in [(0,1),(1,0),(1,2),(2,1),(2,0),(0,2)]:
        links[(i,j)] = link_direction(tri_positions[i], tri_positions[j])

    variables = {
        'M_X': {(0,1): 1.0, (1,0): 1.0},
        'M_Y': {(1,2): 1.0, (2,1): 1.0},
        'M_Z': {(2,0): 1.0, (0,2): 1.0},
        'M_E': {(0,1): 1.0, (1,0): 1.0, (1,2): -1.0, (2,1): -1.0},
        'M_T': {(0,1): 1.0, (1,0): 1.0, (1,2): 1.0, (2,1): 1.0,
                (2,0): 1.0, (0,2): 1.0},
    }

    # Sky grid
    thetas = np.linspace(0, np.pi, 16)
    phis = np.linspace(0, 2*np.pi, 32, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/32) * (np.pi/16)

    # Compute all variable responses
    var_resps = {}
    for name, wdict in variables.items():
        var_resps[name] = compute_variable_on_sky(freq, wdict, links, tG, pG, L)

    print(f"\n  Auto-ORF (|R_+|^2 + |R_x|^2):")
    for name, (Rp, Rx) in var_resps.items():
        auto = np.real(np.sum((np.abs(Rp)**2 + np.abs(Rx)**2) * dO))
        print(f"    {name}: {auto:.4f}")

    pairs = [('M_X', 'M_Y'), ('M_X', 'M_Z'), ('M_Y', 'M_Z'),
             ('M_E', 'M_X'), ('M_E', 'M_Y'), ('M_T', 'M_E'),
             ('M_T', 'M_X'), ('M_E', 'M_T'),
             ('M_X', 'M_T'), ('M_Y', 'M_T')]

    print(f"\n  Chiral ORF (cross-correlation):")
    print(f"    {'Pair':<20s}  {'<Gamma^V>':>14s}  {'|Gamma^V|':>12s}  Result")
    print(f"    {'-'*20}  {'-'*14}  {'-'*12}  {'-'*12}")

    chiral_results = {}
    nonzero = []
    for name1, name2 in pairs:
        Rp1, Rx1 = var_resps[name1]
        Rp2, Rx2 = var_resps[name2]

        chiral_factor = np.real(Rp1 * np.conj(Rx2) - Rx1 * np.conj(Rp2))
        corr = np.sum(chiral_factor * dO)

        auto1 = np.sum((np.abs(Rp1)**2 + np.abs(Rx1)**2) * dO)
        auto2 = np.sum((np.abs(Rp2)**2 + np.abs(Rx2)**2) * dO)
        norm = np.sqrt(np.abs(auto1) * np.abs(auto2))

        gamma_V = corr / norm if norm > 1e-30 else 0.0
        chiral_results[(name1, name2)] = gamma_V

        result = "SIGNIFICANT" if np.abs(gamma_V) > 1e-3 else "zero"
        if np.abs(gamma_V) > 1e-6:
            nonzero.append((name1, name2, gamma_V))

        print(f"    <{name1}, {name2}>{'':<7s}  {gamma_V:14.6e}  {np.abs(gamma_V):12.6e}  {result}")

    print(f"\n  Non-zero findings ({len(nonzero)} pairs):")
    if nonzero:
        for n1, n2, gv in nonzero:
            print(f"    <{n1}, {n2}> = {gv:.6e}")
    else:
        print("    None - all Gamma^V consistent with zero")


if __name__ == '__main__':
    f = 0.030  # 30 mHz
    L_scale = 2.5e9

    print("=" * 60)
    print("Non-Michelson Chiral ORF: Symmetry vs Geometry")
    print("=" * 60)
    print(f"  f = {f*1e3:.0f} mHz")

    # Config 1: Equilateral triangle in xy-plane (has mirror symmetry about x-axis)
    tri_eq = np.array([
        [0.0, 0.0, 0.0],
        [L_scale, 0.0, 0.0],
        [L_scale/2, L_scale*np.sqrt(3)/2, 0.0]
    ])

    # Config 2: Right triangle (no mirror symmetry)
    tri_right = np.array([
        [0.0, 0.0, 0.0],
        [L_scale, 0.0, 0.0],
        [0.0, L_scale, 0.0]
    ])

    # Config 3: Skewed triangle (very asymmetric)
    tri_skew = np.array([
        [0.0, 0.0, 0.0],
        [L_scale, 0.0, 0.0],
        [0.3*L_scale, 0.7*L_scale, 0.0]
    ])

    test_configuration("Equilateral (xy-plane, mirror symmetric)", tri_eq, f, L_scale)
    test_configuration("Right triangle (no mirror symmetry)", tri_right, f, L_scale)
    test_configuration("Skewed triangle (highly asymmetric)", tri_skew, f, L_scale)

    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("=" * 60)
    print("If all configurations give Gamma^V ~ 0, then the OLC")
    print("transfer function inherently produces zero chiral ORF.")
    print("If any non-Michelson combination gives nonzero Gamma^V,")
    print("it breaks the symmetry that suppresses chiral detection.")
    print("=" * 60)
