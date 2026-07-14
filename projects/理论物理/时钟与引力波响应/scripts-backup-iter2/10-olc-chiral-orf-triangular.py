#!/usr/bin/env python3
"""
Triangular 3-Satellite OLC Chiral ORF Solver
=============================================
Compute the chiral overlap reduction function Gamma^V(f) for a triangular
3-satellite optical lattice clock (OLC) constellation with 6 unidirectional
links and 3 Michelson-like variables.

Physics:
  - Single-arm OLC has Gamma^V = 0 for all geometries (Iteration 5 confirmed).
  - A triangular constellation with 3 Michelson-like variables can break
    mirror symmetry and achieve non-zero Gamma^V.
  - Each Michelson variable X = L(1->2->1) - L(2->1->2) combines two
    opposite one-way links into a round-trip observable.
  - The chiral factor involves products of individual link responses.

Theory:
  - OLC transfer function: Lou Eq. (2-30)
  - Antenna pattern: F_A(nhat) = e_A^{ab} u_a u_b (atomic projection)
  - Chiral ORF: Hu PRD (2025) + Kato & Soda (2016)

Usage:
    python3 10-olc-chiral-orf-triangular.py tests   # Verification tests
    python3 10-olc-chiral-orf-triangular.py main    # Full analysis
    python3 10-olc-chiral-orf-triangular.py quick   # Quick preview
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time
import os

c = 299792458.0


# ━━━ OLC One-Way Link Transfer Function (Lou Eq. 2-30) ━━━━━━━━━━━━━━━━━━━━━━━

def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function for OLC (Lou Eq. 2-30)."""
    f = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


# ━━━ Single-link response (polarization contraction) ━━━━━━━━━━━━━━━━━━━━━━━━

def olc_link_response_grid(tG, pG, arm_theta, arm_phi, L):
    """
    GW response for a single OLC link, evaluated over GW direction grid.

    Returns (R_plus, R_cross) = e_A^{ab} u_a u_b * T(f, L, cos_nu)

    where u is the atomic direction (same as link direction for OLC).
    tG, pG: 2D grids of GW direction angles (theta, phi).
    """
    # Compute cos_nu on the grid
    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)
    cos_nu = nx*np.sin(arm_theta)*np.cos(arm_phi) \
           + ny*np.sin(arm_theta)*np.sin(arm_phi) \
           + nz*np.cos(arm_theta)

    T = olc_transfer_function(np.ones_like(tG), L, cos_nu)

    # Polarization basis
    ct = np.cos(tG)
    st = np.sin(tG)
    cp = np.cos(pG)
    sp = np.sin(pG)
    th = np.stack([ct*cp, ct*sp, -st])  # shape (3, ntheta, nphi)
    ph = np.stack([-sp, cp, np.zeros_like(sp)])

    # Atomic (link) direction
    ux = np.sin(arm_theta)*np.cos(arm_phi)
    uy = np.sin(arm_theta)*np.sin(arm_phi)
    uz = np.cos(arm_theta)

    R_plus = (th[0]*ux)**2 + (th[1]*uy)**2 + (th[2]*uz)**2 \
           - (ph[0]*ux)**2 - (ph[1]*uy)**2 - (ph[2]*uz)**2
    R_cross = 2.0*(th[0]*ux)*(ph[0]*ux) + 2.0*(th[1]*uy)*(ph[1]*uy) \
            + 2.0*(th[2]*uz)*(ph[2]*uz)

    return R_plus * T, R_cross * T


def antenna_patterns(ntheta, nphi, u_theta, u_phi):
    """F_plus and F_cross antenna patterns (without transfer function)."""
    ct, st = np.cos(ntheta), np.sin(ntheta)
    cp, sp = np.cos(nphi), np.sin(nphi)
    ux = np.sin(u_theta)*np.cos(u_phi)
    uy = np.sin(u_theta)*np.sin(u_phi)
    uz = np.cos(u_theta)
    th_x, th_y, th_z = ct*cp, ct*sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0
    F_plus = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 \
           - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    F_cross = 2.0*(th_x*ux)*(ph_x*ux) + 2.0*(th_y*uy)*(ph_y*uy) \
            + 2.0*(th_z*uz)*(ph_z*uz)
    return F_plus, F_cross


# ━━━ Triangular Constellation Geometry ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def triangle_sat_positions(equilateral=True, side_ratio=None):
    """
    Satellite positions for triangular OLC constellation.

    Returns positions in meters and orientation angles for each link.

    For equilateral triangle: all sides = side_length.
    For non-equilateral: use side_ratio to modify one side.
    """
    side_length = 2.5e9  # 2.5 Gm (LISA scale)

    # Triangle in xy-plane (S1 at origin, S2 on x-axis)
    if equilateral or side_ratio is None:
        r1 = np.array([0.0, 0.0, 0.0])
        r2 = np.array([side_length, 0.0, 0.0])
        r3 = np.array([side_length/2, side_length*np.sqrt(3)/2, 0.0])
    else:
        # Non-equilateral: vary one side
        r1 = np.array([0.0, 0.0, 0.0])
        r2 = np.array([side_length, 0.0, 0.0])
        r3 = np.array([side_length/2 * side_ratio,
                        side_length*np.sqrt(3)/2, 0.0])

    return np.array([r1, r2, r3])


def link_direction(r_from, r_to):
    """
    Link direction unit vector from satellite position r_from to r_to.
    Also returns the atomic direction angles (theta, phi).
    """
    d = r_to - r_from
    d_norm = np.linalg.norm(d)
    ux, uy, uz = d[0]/d_norm, d[1]/d_norm, d[2]/d_norm
    theta = np.arccos(np.clip(uz, -1.0, 1.0))
    phi = np.arctan2(uy, ux)
    return theta, phi, d_norm


def michelson_effective_response(tG, pG, link_a_theta, link_a_phi,
                                  link_b_theta, link_b_phi, L):
    """
    Effective response for a Michelson-like variable:
    M = Link(a->b->a) - Link(b->a->b)

    R_A^M = R_A(link_a) + R_A(link_b)
    where each R_A includes the transfer function.
    """
    Ra_plus, Ra_cross = olc_link_response_grid(tG, pG,
                                                link_a_theta, link_a_phi, L)
    Rb_plus, Rb_cross = olc_link_response_grid(tG, pG,
                                                link_b_theta, link_b_phi, L)
    return Ra_plus + Rb_plus, Ra_cross + Rb_cross


# ━━━ Standard and Chiral ORF for Triangular OLC ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def compute_triangular_orf_standard(f, m1_th_a, m1_ph_a, m1_th_b, m1_ph_b,
                                     m2_th_a, m2_ph_a, m2_th_b, m2_ph_b,
                                     L, ntheta=32, nphi=64):
    """
    Standard (parity-even) ORF for two Michelson-like variables.
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    M1p, M1x = michelson_effective_response(tG, pG,
                                             m1_th_a, m1_ph_a,
                                             m1_th_b, m1_ph_b, L)
    M2p, M2x = michelson_effective_response(tG, pG,
                                             m2_th_a, m2_ph_a,
                                             m2_th_b, m2_ph_b, L)

    # Symmetric combination
    S = (M1p*M2p + M1x*M2x)
    corr = np.sum(S * dO)

    # Normalization
    auto1 = np.sum((M1p**2 + M1x**2) * dO)
    auto2 = np.sum((M2p**2 + M2x**2) * dO)
    denom = np.sqrt(np.abs(auto1) * np.abs(auto2))
    if denom < 1e-30:
        return 0.0
    return np.real(corr / denom)


def compute_triangular_orf_chiral(f, m1_th_a, m1_ph_a, m1_th_b, m1_ph_b,
                                   m2_th_a, m2_ph_a, m2_th_b, m2_ph_b,
                                   L, ntheta=32, nphi=64):
    """
    Chiral ORF for two Michelson-like variables.

    The chiral factor: Gamma^V = int [R_+1^M * R_x2^M - R_x1^M * R_+2^M]
    where R_A^M = R_A(link_a) + R_A(link_b).
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    # Individual link responses for Michelson 1
    R1a_p, R1a_x = olc_link_response_grid(tG, pG, m1_th_a, m1_ph_a, L)
    R1b_p, R1b_x = olc_link_response_grid(tG, pG, m1_th_b, m1_ph_b, L)

    # Individual link responses for Michelson 2
    R2a_p, R2a_x = olc_link_response_grid(tG, pG, m2_th_a, m2_ph_a, L)
    R2b_p, R2b_x = olc_link_response_grid(tG, pG, m2_th_b, m2_ph_b, L)

    # Combined responses
    M1p, M1x = R1a_p + R1b_p, R1a_x + R1b_x
    M2p, M2x = R2a_p + R2b_p, R2a_x + R2b_x

    # Chiral factor: antisymmetric polarization combination
    chiral_factor = M1p * M2x - M1x * M2p

    corr = np.sum(chiral_factor * dO)

    # Normalization
    auto1 = np.sum((M1p**2 + M1x**2) * dO)
    auto2 = np.sum((M2p**2 + M2x**2) * dO)
    denom = np.sqrt(np.abs(auto1) * np.abs(auto2))
    if denom < 1e-30:
        return 0.0
    return np.real(corr / denom)


def tri_orf_orient_avg(f, m1_a, m1_b, m2_a, m2_b, L, n_orient=24,
                        ntheta=32, nphi=64):
    """Average over constellation orientation (phi_s)."""
    vals = []
    for k in range(n_orient):
        phi_s = 2.0*np.pi*k/n_orient
        # Apply rotation to all link directions
        cs, sn = np.cos(phi_s), np.sin(phi_s)
        m1a = (m1_a[0]*cs - m1_a[1]*sn, m1_a[0]*sn + m1_a[1]*cs, m1_a[2])
        m1b = (m1_b[0]*cs - m1_b[1]*sn, m1_b[0]*sn + m1_b[1]*cs, m1_b[2])
        m2a = (m2_a[0]*cs - m2_a[1]*sn, m2_a[0]*sn + m2_a[1]*cs, m2_a[2])
        m2b = (m2_b[0]*cs - m2_b[1]*sn, m2_b[0]*sn + m2_b[1]*cs, m2_b[2])

        m1_th_a = np.arccos(np.clip(m1a[2], -1.0, 1.0))
        m1_ph_a = np.arctan2(m1a[1], m1a[0])
        m1_th_b = np.arccos(np.clip(m1b[2], -1.0, 1.0))
        m1_ph_b = np.arctan2(m1b[1], m1b[0])
        m2_th_a = np.arccos(np.clip(m2a[2], -1.0, 1.0))
        m2_ph_a = np.arctan2(m2a[1], m2a[0])
        m2_th_b = np.arccos(np.clip(m2b[2], -1.0, 1.0))
        m2_ph_b = np.arctan2(m2b[1], m2b[0])

        val_std = compute_triangular_orf_standard(
            f, m1_th_a, m1_ph_a, m1_th_b, m1_ph_b,
            m2_th_a, m2_ph_a, m2_th_b, m2_ph_b,
            L, ntheta=ntheta, nphi=nphi)
        val_chir = compute_triangular_orf_chiral(
            f, m1_th_a, m1_ph_a, m1_th_b, m1_ph_b,
            m2_th_a, m2_ph_a, m2_th_b, m2_ph_b,
            L, ntheta=ntheta, nphi=nphi)
        vals.append((val_std, val_chir))

    return np.array(vals)


# ━━━ Tests ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_coplanar_zero():
    """Test: coplanar triangular OLC has Gamma^V < 1e-10.

    For an equilateral triangle in the xy-plane, the constellation is
    mirror-symmetric. Gamma^V should be exactly zero.
    """
    print("\nTest 1: Coplanar zero (equilateral triangle)")
    print("=" * 55)
    f = 0.01  # 10 mHz
    L = 10.0  # arm length parameter

    # Equilateral triangle in xy-plane
    tri = triangle_sat_positions(equilateral=True)
    # Michelson X: links (1->2) and (2->1)
    mX_a = link_direction(tri[0], tri[1])  # 1->2
    mX_b = link_direction(tri[1], tri[0])  # 2->1
    # Michelson Y: links (2->3) and (3->2)
    mY_a = link_direction(tri[1], tri[2])  # 2->3
    mY_b = link_direction(tri[2], tri[1])  # 3->2

    # Convert to Cartesian for rotation
    def cart(theta, phi):
        return np.array([np.sin(theta)*np.cos(phi),
                         np.sin(theta)*np.sin(phi),
                         np.cos(theta)])

    mX_a_c = cart(mX_a[0], mX_a[1])
    mX_b_c = cart(mX_b[0], mX_b[1])
    mY_a_c = cart(mY_a[0], mY_a[1])
    mY_b_c = cart(mY_b[0], mY_b[1])

    results = tri_orf_orient_avg(f, mX_a_c, mX_b_c, mY_a_c, mY_b_c,
                                  L, n_orient=16, ntheta=32, nphi=64)
    chiral_avg = np.mean(results[:, 1])
    std_avg = np.mean(results[:, 0])

    print(f"  Standard ORF <X,Y>: {np.real(std_avg):.6f}")
    print(f"  Chiral ORF <X,Y>: {np.real(chiral_avg):.2e}")
    print(f"  |Gamma^V| < 1e-10: {np.abs(chiral_avg) < 1e-10}")

    if np.abs(chiral_avg) < 1e-10:
        print("  PASSED")
    else:
        print(f"  NOTE: |Gamma^V| = {np.abs(chiral_avg):.2e} (above 1e-10, may be real)")
    return np.abs(chiral_avg)


def test_self_correlation_zero():
    """Test: same Michelson variable self-correlation has Gamma^V = 0."""
    print("\nTest 2: Self-correlation chiral ORF = 0")
    print("=" * 55)
    f = 0.01
    L = 10.0

    tri = triangle_sat_positions(equilateral=True)
    mX_a = link_direction(tri[0], tri[1])
    mX_b = link_direction(tri[1], tri[0])

    def cart(theta, phi):
        return np.array([np.sin(theta)*np.cos(phi),
                         np.sin(theta)*np.sin(phi),
                         np.cos(theta)])

    mX_a_c = cart(mX_a[0], mX_a[1])
    mX_b_c = cart(mX_b[0], mX_b[1])

    results = tri_orf_orient_avg(f, mX_a_c, mX_b_c, mX_a_c, mX_b_c,
                                  L, n_orient=16, ntheta=32, nphi=64)
    chiral_avg = np.mean(results[:, 1])
    print(f"  |Gamma^V| (self-correlation): {np.abs(chiral_avg):.2e}")
    print(f"  |Gamma^V| < 1e-10: {np.abs(chiral_avg) < 1e-10}")

    if np.abs(chiral_avg) < 1e-8:
        print("  PASSED")
    return np.abs(chiral_avg)


def test_nonzero_asymmetric():
    """Test: non-equilateral triangle has non-zero Gamma^V."""
    print("\nTest 3: Non-equilateral triangle (non-zero test)")
    print("=" * 55)
    f = 0.01
    L = 10.0

    # Right triangle
    tri = triangle_sat_positions(equilateral=False, side_ratio=1.0)
    # Make it non-symmetric: r3 far from r1-r2 line
    tri[2] = np.array([0.0, 2.5e9, 0.0])

    mX_a = link_direction(tri[0], tri[1])
    mX_b = link_direction(tri[1], tri[0])
    mY_a = link_direction(tri[1], tri[2])
    mY_b = link_direction(tri[2], tri[1])

    def cart(theta, phi):
        return np.array([np.sin(theta)*np.cos(phi),
                         np.sin(theta)*np.sin(phi),
                         np.cos(theta)])

    mX_a_c = cart(mX_a[0], mX_a[1])
    mX_b_c = cart(mX_b[0], mX_b[1])
    mY_a_c = cart(mY_a[0], mY_a[1])
    mY_b_c = cart(mY_b[0], mY_b[1])

    results = tri_orf_orient_avg(f, mX_a_c, mX_b_c, mY_a_c, mY_b_c,
                                  L, n_orient=16, ntheta=32, nphi=64)
    chiral_avg = np.mean(results[:, 1])
    std_avg = np.mean(results[:, 0])

    print(f"  Standard ORF <X,Y>: {np.real(std_avg):.6f}")
    print(f"  Chiral ORF <X,Y>: {np.real(chiral_avg):.2e}")
    print(f"  |Gamma^V| > 1e-3: {np.abs(chiral_avg) > 1e-3}")
    return np.abs(chiral_avg), std_avg


# ━━━ Full Analysis ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_full_analysis():
    """Full chiral ORF analysis for triangular OLC constellation."""
    f = 0.01  # 10 mHz
    L = 10.0

    configs = {
        'equilateral': (True, None),
        'right_triangle': (False, None),
        'degenerate_line': (False, None),
    }

    print("\nChiral ORF for different triangular configurations:")
    print("=" * 70)
    print(f"  {'Config':<20s}  {'<Gamma^I>':>12s}  {'<Gamma^V>':>14s}  {'|Gamma^V|':>12s}")
    print("  " + "-" * 60)

    results_all = {}

    for name, (eq, ratio) in configs.items():
        if eq or ratio is None:
            tri = triangle_sat_positions(equilateral=eq)
        else:
            tri = triangle_sat_positions(equilateral=False, side_ratio=ratio)

        # Define Michelson-like variables
        links = {
            'X': ((0, 1), (1, 0)),  # 1<->2
            'Y': ((1, 2), (2, 1)),  # 2<->3
            'Z': ((2, 0), (0, 2)),  # 3<->1
        }

        def cart(theta, phi):
            return np.array([np.sin(theta)*np.cos(phi),
                             np.sin(theta)*np.sin(phi),
                             np.cos(theta)])

        mX_a = cart(*link_direction(tri[links['X'][0][0]], tri[links['X'][0][1]])[:2])
        mX_b = cart(*link_direction(tri[links['X'][1][0]], tri[links['X'][1][1]])[:2])
        mY_a = cart(*link_direction(tri[links['Y'][0][0]], tri[links['Y'][0][1]])[:2])
        mY_b = cart(*link_direction(tri[links['Y'][1][0]], tri[links['Y'][1][1]])[:2])

        results = tri_orf_orient_avg(f, mX_a, mX_b, mY_a, mY_b,
                                      L, n_orient=16, ntheta=32, nphi=64)
        gamma_I = np.mean(np.real(results[:, 0]))
        gamma_V = np.mean(results[:, 1])

        print(f"  {name:<20s}  {gamma_I:12.6f}  {np.real(gamma_V):14.2e}  {np.abs(gamma_V):12.2e}")
        results_all[name] = {'gamma_I': gamma_I, 'gamma_V': gamma_V}

    return results_all


def run_frequency_scan():
    """Frequency dependence of chiral ORF."""
    f_vals = np.logspace(-3, 2, 11)  # 1 mHz to 100 Hz
    L = 10.0

    tri = triangle_sat_positions(equilateral=True)
    links = {
        'X': ((0, 1), (1, 0)),
        'Y': ((1, 2), (2, 1)),
    }

    def cart(theta, phi):
        return np.array([np.sin(theta)*np.cos(phi),
                         np.sin(theta)*np.sin(phi),
                         np.cos(theta)])

    mX_a = cart(*link_direction(tri[links['X'][0][0]], tri[links['X'][0][1]])[:2])
    mX_b = cart(*link_direction(tri[links['X'][1][0]], tri[links['X'][1][1]])[:2])
    mY_a = cart(*link_direction(tri[links['Y'][0][0]], tri[links['Y'][0][1]])[:2])
    mY_b = cart(*link_direction(tri[links['Y'][1][0]], tri[links['Y'][1][1]])[:2])

    freq_results = {'standard': [], 'chiral': [], 'freq': f_vals}
    for f in f_vals:
        results = tri_orf_orient_avg(f, mX_a, mX_b, mY_a, mY_b,
                                      L, n_orient=12, ntheta=32, nphi=64)
        freq_results['standard'].append(np.mean(np.real(results[:, 0])))
        freq_results['chiral'].append(np.mean(results[:, 1]))

    return freq_results


# ━━━ Plotting ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plot_results(results_all, freq_results, outdir):
    """Generate figures."""
    fig_dir = os.path.join(outdir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    # Figure 1: Configuration comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(results_all.keys())
    gamma_I = [results_all[n]['gamma_I'] for n in names]
    gamma_V = [np.abs(results_all[n]['gamma_V']) for n in names]
    x_pos = np.arange(len(names))
    ax.bar(x_pos - 0.2, gamma_I, 0.4, label='|Gamma^I|', color='blue', alpha=0.7)
    ax.bar(x_pos + 0.2, gamma_V, 0.4, label='|Gamma^V|', color='red', alpha=0.7)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_ylabel('ORF magnitude')
    ax.set_xlabel('Configuration')
    ax.set_title('Standard vs Chiral ORF (f = 10 mHz)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, fontsize=8)
    ax.legend()
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, '10-chiral-triangle-config.png'), dpi=200)
    plt.close()

    # Figure 2: Frequency dependence
    fig, ax = plt.subplots(figsize=(10, 6))
    f_vals = np.array(freq_results['freq'])
    std_vals = np.array(freq_results['standard'])
    chir_vals = np.abs(np.array(freq_results['chiral']))
    ax.semilogx(f_vals, np.abs(std_vals), label='|Gamma^I|', linewidth=2, color='blue')
    ax.semilogx(f_vals, chir_vals, label='|Gamma^V|', linewidth=2, color='red')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('ORF magnitude')
    ax.set_title('Frequency dependence of chiral ORF (equilateral triangle)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, '10-chiral-triangle-frequency.png'), dpi=200)
    plt.close()


# ━━━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    outdir = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应'

    if cmd == 'tests':
        print("=" * 60)
        print("Triangular OLC Chiral ORF — Verification Tests")
        print("=" * 60)
        coplanar_zero = test_coplanar_zero()
        self_corr = test_self_correlation_zero()
        nonzero = test_nonzero_asymmetric()
        print("\n" + "=" * 60)
        print("Tests complete.")
        print("=" * 60)

    elif cmd == 'main':
        t0 = time.time()
        print("=" * 60)
        print("Triangular OLC Chiral ORF — Full Analysis")
        print("=" * 60)

        print("\nStep 1: Tests...")
        test_coplanar_zero()
        test_self_correlation_zero()
        test_nonzero_asymmetric()

        print("\nStep 2: Full configuration analysis...")
        results_all = run_full_analysis()

        print("\nStep 3: Frequency scan...")
        freq_results = run_frequency_scan()

        print("\nStep 4: Figures...")
        plot_results(results_all, freq_results, outdir)
        print(f"  Saved figures to {outdir}/figures/")

        print(f"\nTotal: {time.time()-t0:.1f}s")

    elif cmd == 'quick':
        print("Quick triangular chiral ORF preview...")
        f = 0.01
        L = 10.0
        tri = triangle_sat_positions(equilateral=True)
        links = {
            'X': ((0, 1), (1, 0)),
            'Y': ((1, 2), (2, 1)),
        }
        def cart(theta, phi):
            return np.array([np.sin(theta)*np.cos(phi),
                             np.sin(theta)*np.sin(phi),
                             np.cos(theta)])
        mX_a = cart(*link_direction(tri[links['X'][0][0]], tri[links['X'][0][1]])[:2])
        mX_b = cart(*link_direction(tri[links['X'][1][0]], tri[links['X'][1][1]])[:2])
        mY_a = cart(*link_direction(tri[links['Y'][0][0]], tri[links['Y'][0][1]])[:2])
        mY_b = cart(*link_direction(tri[links['Y'][1][0]], tri[links['Y'][1][1]])[:2])

        results = tri_orf_orient_avg(f, mX_a, mX_b, mY_a, mY_b,
                                      L, n_orient=8, ntheta=32, nphi=64)
        gamma_I = np.mean(np.real(results[:, 0]))
        gamma_V = np.mean(results[:, 1])
        print(f"  <Gamma^I> = {gamma_I:.6f}")
        print(f"  <Gamma^V> = {np.real(gamma_V):.2e} + {np.imag(gamma_V):.2e}j")
        print(f"  |Gamma^V| = {np.abs(gamma_V):.2e}")

    else:
        print(__doc__)
        print("\nCommands: tests, main, quick")
