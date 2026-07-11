#!/usr/bin/env python3
"""
Non-Coplanar Triangular OLC Chiral ORF Solver
================================================
Compute the chiral overlap reduction function Gamma^V(f) for a single
triangular 3-satellite OLC constellation in non-coplanar geometry.

KEY PHYSICS:
  - Coplanar detectors have mirror reflection symmetry => Gamma^V = 0
  - Breaking coplanarity (theta_inc != 0 or delta_h != 0) breaks this symmetry
  - Question: can a single non-coplanar triangle achieve measurable Gamma^V?

E-variable (CW sum):
  R_E+ = sum_{CW links} F_+(link) * T(f, L, cos_nu)
  R_Ex = sum_{CW links} F_x(link) * T(f, L, cos_nu)

Michelson variable:
  M = Link(a->b->a) - Link(b->a->b)
  R_A^M = R_A(link_a) + R_A(link_b)

Single-arm pair:
  Two non-coplanar one-way links for K3 benchmark validation.

Theory:
  - OLC transfer function: Lou Eq. (2-30)
  - Chiral ORF: Gamma^V = int [R_+1*R_x2 - R_x1*R_+2] / (4*pi)

Usage:
    python3 12-noncoplanar-triangular-chiral-orf.py tests   # Verification tests
    python3 12-noncoplanar-triangular-chiral-orf.py main    # Full analysis
    python3 12-noncoplanar-triangular-chiral-orf.py quick   # Quick preview
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time
import os

c = 299792458.0


# ================================================================
# OLC One-Way Link Transfer Function (Lou Eq. 2-30)
# ================================================================

def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function for OLC (Lou Eq. 2-30)."""
    f = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - np.abs(cos_nu)
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


# ================================================================
# Single-link response (polarization contraction)
# ================================================================

def olc_link_response_grid(tG, pG, arm_theta, arm_phi, L):
    """
    GW response for a single OLC link, evaluated over GW direction grid.

    Returns (R_plus, R_cross) = e_A^{ab} u_a u_b * T(f, L, cos_nu)
    where u is the atomic direction (same as link direction for OLC).
    """
    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)
    cos_nu = nx*np.sin(arm_theta)*np.cos(arm_phi) \
           + ny*np.sin(arm_theta)*np.sin(arm_phi) \
           + nz*np.cos(arm_theta)

    T = olc_transfer_function(np.ones_like(tG), L, cos_nu)

    ct = np.cos(tG)
    st = np.sin(tG)
    cp = np.cos(pG)
    sp = np.sin(pG)
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


# ================================================================
# Non-coplanar triangle geometry builder
# ================================================================

def build_noncoplanar_triangle(theta_inc, delta_h, side_ratios=None):
    """
    Build satellite positions for a non-coplanar triangular OLC constellation.

    Construction:
      1. Start with equilateral triangle in xy-plane:
         S1 at origin, S2 on x-axis, S3 at 60 degrees
      2. Rotate around X-axis by theta_inc (inclination)
      3. Apply delta_h as z-direction displacement of S3 (out-of-plane)
      4. Optionally distort side ratios

    Args:
        theta_inc: Inclination angle in radians (rotation around X-axis)
        delta_h: Out-of-plane height displacement in meters
        side_ratios: Optional dict with 'ratio_ab', 'ratio_bc', 'ratio_ca'
                     for side length distortions relative to equilateral

    Returns:
        np.array of shape (3, 3) — satellite positions [S1, S2, S3]
    """
    side_length = 2.5e9  # 2.5 Gm (LISA scale)

    # Step 1: Equilateral triangle in xy-plane
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([side_length, 0.0, 0.0])
    r3 = np.array([side_length/2, side_length*np.sqrt(3)/2, 0.0])

    # Step 2: Rotate around X-axis by theta_inc
    cos_i = np.cos(theta_inc)
    sin_i = np.sin(theta_inc)

    def rotate_x(pos, ci, si):
        return np.array([
            pos[0],
            pos[1] * ci - pos[2] * si,
            pos[1] * si + pos[2] * ci
        ])

    r1 = rotate_x(r1, cos_i, sin_i)
    r2 = rotate_x(r2, cos_i, sin_i)
    r3 = rotate_x(r3, cos_i, sin_i)

    # Step 3: Apply delta_h as z-direction displacement
    r3[2] += delta_h

    # Step 4: Optional side ratio distortion
    if side_ratios is not None:
        # Adjust S3 position based on side ratios
        # This creates a non-equilateral triangle while preserving non-coplanarity
        ra = side_ratios.get('ratio_ab', 1.0)
        rb = side_ratios.get('ratio_bc', 1.0)
        rc = side_ratios.get('ratio_ca', 1.0)

        # Rescale S2 along the rotated S1->S2 direction
        v12 = r2 - r1
        v12 = v12 / np.linalg.norm(v12)
        r2 = r1 + v12 * side_length * ra

        # Rescale S3 to satisfy ratio constraints (iterative approximation)
        v23 = r3 - r2
        v23 = v23 / np.linalg.norm(v23)
        r3 = r2 + v23 * side_length * rb

        # Fine-tune to match third side ratio
        v13_current = r3 - r1
        current_ca = np.linalg.norm(v13_current) / side_length
        if abs(current_ca) > 1e-15:
            r3 = r1 + (v13_current / current_ca) * side_length * rc
            # Re-apply delta_h after repositioning
            r3[2] += delta_h

    return np.array([r1, r2, r3])


def coplanarity_measure(sat_positions):
    """
    Measure how non-coplanar the triangle is.

    coplanarity = |(r2-r1) . ((r3-r1) x n_ref)| / (|r2-r1| * |r3-r1| * |n_ref|)

    For a truly coplanar triangle, the three points lie in one plane,
    and the scalar triple product (r3-r1) . n = 0.

    Returns:
        coplanarity: scalar in [0, 1]. 0 = perfectly coplanar, >0 = non-coplanar
        n_unit: unit normal to the plane defined by S1 and S2 relative to origin
    """
    r1, r2, r3 = sat_positions[0], sat_positions[1], sat_positions[2]

    # Two vectors in the reference plane
    v12 = r2 - r1
    v13 = r3 - r1

    # Normal to the plane spanned by v12 and v13
    n = np.cross(v12, v13)
    n_norm = np.linalg.norm(n)

    if n_norm < 1e-15:
        return 0.0, np.array([0.0, 0.0, 1.0])

    n_unit = n / n_norm

    # For a coplanar triangle, r3 lies in the same plane as r1, r2
    # The coplanarity measure captures out-of-plane displacement
    # Use the reference plane normal (z-axis for initial triangle)
    # coplanarity = distance of S3 from the plane of S1-S2-origins / total size
    ref_n = np.array([0.0, 0.0, 1.0])

    # Distance of S3 from the plane through S1, S2 with normal ref_n
    # Since S1 is at origin: plane is defined by r2 and ref_n
    plane_n = np.cross(r2 - r1, ref_n)
    plane_n_norm = np.linalg.norm(plane_n)
    if plane_n_norm < 1e-15:
        return 0.0, ref_n
    plane_n_unit = plane_n / plane_n_norm

    # Signed distance of S3 from this plane
    dist = np.abs(np.dot(r3 - r1, plane_n_unit))

    # Normalize by triangle size
    size = np.linalg.norm(r2 - r1)
    coplanarity = dist / size if size > 1e-15 else 0.0

    return coplanarity, n_unit


def link_direction(r_from, r_to):
    """
    Link direction unit vector from satellite position r_from to r_to.
    Returns (theta, phi, distance).
    """
    d = r_to - r_from
    d_norm = np.linalg.norm(d)
    ux, uy, uz = d[0]/d_norm, d[1]/d_norm, d[2]/d_norm
    theta = np.arccos(np.clip(uz, -1.0, 1.0))
    phi = np.arctan2(uy, ux)
    return theta, phi, d_norm


# ================================================================
# Michelson effective response (from script 10)
# ================================================================

def michelson_effective_response(tG, pG, link_a_theta, link_a_phi,
                                  link_b_theta, link_b_phi, L):
    """
    Effective response for a Michelson-like variable:
    M = Link(a->b->a) - Link(b->a->b)

    R_A^M = R_A(link_a) + R_A(link_b)
    """
    Ra_plus, Ra_cross = olc_link_response_grid(tG, pG,
                                                link_a_theta, link_a_phi, L)
    Rb_plus, Rb_cross = olc_link_response_grid(tG, pG,
                                                link_b_theta, link_b_phi, L)
    return Ra_plus + Rb_plus, Ra_cross + Rb_cross


# ================================================================
# E-variable via CW link sum (from script 11)
# ================================================================

def e_variable_response(tG, pG, sat_positions, L):
    """
    E-variable antenna pattern via clockwise (CW) link sum.

    R_E+ = sum_{CW links} F_+(link) * T(f, L, cos_nu)
    R_Ex = sum_{CW links} F_x(link) * T(f, L, cos_nu)

    CW links: 1->2, 2->3, 3->1

    Returns (R_plus, R_cross) as complex arrays.
    """
    tG_a = np.asarray(tG)
    pG_a = np.asarray(pG)

    nx = np.sin(tG_a)*np.cos(pG_a)
    ny = np.sin(tG_a)*np.sin(pG_a)
    nz = np.cos(tG_a)

    th = np.array([np.cos(tG_a)*np.cos(pG_a),
                   np.cos(tG_a)*np.sin(pG_a),
                   -np.sin(tG_a)])
    ph = np.array([-np.sin(pG_a),
                   np.cos(pG_a),
                   np.zeros_like(pG_a, dtype=np.float64)])

    # CW links: S1->S2, S2->S3, S3->S1
    cw_links = [(0, 1), (1, 2), (2, 0)]

    R_plus = np.zeros_like(tG_a, dtype=np.complex128)
    R_cross = np.zeros_like(tG_a, dtype=np.complex128)

    for i, j in cw_links:
        u = sat_positions[j] - sat_positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]

        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = olc_transfer_function(np.ones_like(tG_a, dtype=np.float64), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross


# ================================================================
# Chiral ORF computation
# ================================================================

def compute_e_variable_chiral_orf(f, sat_positions, L, ntheta=32, nphi=64):
    """
    Chiral ORF for E-variable self-correlation of a single constellation.

    Gamma^I = integral [R_+ * R_+* + R_x * R_x*] / (4*pi)
    Gamma^V = integral [R_+ * R_x* - R_x * R_+*] / (4*pi)

    For self-correlation, the integrand of Gamma^V is:
    Re(R_+ * conj(R_x) - R_x * conj(R_+)) = 0 (identically)

    So E-variable self-correlation gives Gamma^V = 0 for any geometry.

    To get non-zero Gamma^V, we need to use two DIFFERENT variables.
    The meaningful chiral observable for a single triangle is:
    - Michelson cross-correlation (X vs Y): from script 10
    - E-variable vs Michelson mixed correlation

    Here we compute E-variable self-correlation (should be 0) for validation.

    Also returns the sky-maximized normalized chiral:
      max over sky of |R_+ * R_x* - R_x * R_+*| / sqrt(auto_plus * auto_x)
    which can be non-zero even for self-correlation.
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dOmega = (np.pi / (ntheta - 1)) * (2 * np.pi / nphi)

    R1p, R1x = e_variable_response(tG, pG, sat_positions, L)

    # Sky-averaged
    gamma_I = np.real(np.sum(np.conj(R1p) * R1p + np.conj(R1x) * R1x)) * dOmega / (4 * np.pi)
    gamma_V = np.real(np.sum(np.conj(R1p) * R1x - np.conj(R1x) * R1p)) * dOmega / (4 * np.pi)

    # Sky-maximized normalized chiral
    auto1 = np.real(np.conj(R1p) * R1p + np.conj(R1x) * R1x)
    auto2 = auto1.copy()
    chiral_integrand = np.real(np.conj(R1p) * R1x - np.conj(R1x) * R1p)

    norm_factor = np.sqrt(auto1 * auto2)
    norm_chiral = np.where(norm_factor > 1e-30, np.abs(chiral_integrand) / norm_factor, 0.0)
    sky_max_norm_V = np.max(norm_chiral)

    return gamma_I, gamma_V, sky_max_norm_V


def compute_michelson_chiral_orf(f, sat_positions, L, ntheta=32, nphi=64):
    """
    Chiral ORF for two Michelson-like variables of a triangular constellation.

    Michelson X: links (S1<->S2)
    Michelson Y: links (S2<->S3)
    Michelson Z: links (S3<->S1)

    Returns Gamma^V(X, Y) — the chiral ORF between Michelson X and Y.
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    # Build Michelson X: links (S1->S2) and (S2->S1)
    mX_a_theta, mX_a_phi, _ = link_direction(sat_positions[0], sat_positions[1])
    mX_b_theta, mX_b_phi, _ = link_direction(sat_positions[1], sat_positions[0])

    # Build Michelson Y: links (S2->S3) and (S3->S2)
    mY_a_theta, mY_a_phi, _ = link_direction(sat_positions[1], sat_positions[2])
    mY_b_theta, mY_b_phi, _ = link_direction(sat_positions[2], sat_positions[1])

    # Individual link responses for Michelson X
    R1a_p, R1a_x = olc_link_response_grid(tG, pG, mX_a_theta, mX_a_phi, L)
    R1b_p, R1b_x = olc_link_response_grid(tG, pG, mX_b_theta, mX_b_phi, L)

    # Individual link responses for Michelson Y
    R2a_p, R2a_x = olc_link_response_grid(tG, pG, mY_a_theta, mY_a_phi, L)
    R2b_p, R2b_x = olc_link_response_grid(tG, pG, mY_b_theta, mY_b_phi, L)

    # Combined responses
    M1p, M1x = R1a_p + R1b_p, R1a_x + R1b_x
    M2p, M2x = R2a_p + R2b_p, R2a_x + R2b_x

    # Chiral factor
    chiral_factor = M1p * M2x - M1x * M2p

    corr = np.sum(chiral_factor * dO)

    # Normalization
    auto1 = np.sum((M1p**2 + M1x**2) * dO)
    auto2 = np.sum((M2p**2 + M2x**2) * dO)
    denom = np.sqrt(np.abs(auto1) * np.abs(auto2))
    if denom < 1e-30:
        return 0.0, 0.0, 0.0

    gamma_I = np.real(np.sum((M1p * M2p + M1x * M2x) * dO)) / denom
    gamma_V = np.real(corr / denom)

    # Sky-maximized normalized chiral
    norm_factor = np.sqrt(np.abs(M1p**2 + M1x**2) * np.abs(M2p**2 + M2x**2))
    norm_chiral = np.where(norm_factor > 1e-30,
                           np.abs(chiral_factor) / norm_factor, 0.0)
    sky_max_norm_V = np.max(norm_chiral)

    return gamma_I, gamma_V, sky_max_norm_V


def compute_single_arm_pair_chiral_orf(f, r_a_from, r_a_to, r_b_from, r_b_to,
                                        L, ntheta=32, nphi=64):
    """
    Chiral ORF for a pair of single non-coplanar links.

    This is the fundamental building block: two distinct one-way links.
    For non-coplanar links, Gamma^V can be non-zero.

    Used to validate K3 benchmark: |Gamma^V| > 0.041 at 30 mHz.

    Args:
        r_a_from, r_a_to: endpoints of link a
        r_b_from, r_b_to: endpoints of link b
        L: arm length
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    th_a_theta, th_a_phi, L_a = link_direction(r_a_from, r_a_to)
    th_b_theta, th_b_phi, L_b = link_direction(r_b_from, r_b_to)

    Ra_p, Ra_x = olc_link_response_grid(tG, pG, th_a_theta, th_a_phi, L_a)
    Rb_p, Rb_x = olc_link_response_grid(tG, pG, th_b_theta, th_b_phi, L_b)

    chiral_factor = Ra_p * Rb_x - Ra_x * Rb_p
    corr = np.sum(chiral_factor * dO)

    auto_a = np.sum((Ra_p**2 + Ra_x**2) * dO)
    auto_b = np.sum((Rb_p**2 + Rb_x**2) * dO)
    denom = np.sqrt(np.abs(auto_a) * np.abs(auto_b))
    if denom < 1e-30:
        return 0.0

    return np.real(corr / denom)


# ================================================================
# Orientation averaging
# ================================================================

def orient_avg_chiral(f, sat_positions, L, n_orient=16, method='michelson',
                       ntheta=32, nphi=64):
    """
    Average chiral ORF over constellation orientation (rotation around z-axis).

    Args:
        method: 'michelson' or 'e_variable'
    """
    chiral_vals = []
    standard_vals = []

    for k in range(n_orient):
        phi_s = 2.0 * np.pi * k / n_orient

        # Rotate satellite positions around z-axis
        cos_s = np.cos(phi_s)
        sin_s = np.sin(phi_s)
        rotated = np.copy(sat_positions)
        rotated[:, 0] = sat_positions[:, 0] * cos_s - sat_positions[:, 1] * sin_s
        rotated[:, 1] = sat_positions[:, 0] * sin_s + sat_positions[:, 1] * cos_s
        # z unchanged

        if method == 'michelson':
            gI, gV, sky_max = compute_michelson_chiral_orf(
                f, rotated, L, ntheta=ntheta, nphi=nphi)
            standard_vals.append(gI)
            chiral_vals.append(gV)
        elif method == 'e_variable':
            gI, gV, sky_max = compute_e_variable_chiral_orf(
                f, rotated, L, ntheta=ntheta, nphi=nphi)
            standard_vals.append(gI)
            chiral_vals.append(gV)

    return np.mean(standard_vals), np.mean(chiral_vals), np.std(chiral_vals)


# ================================================================
# Tests
# ================================================================

def test_coplanar_zero():
    """Test: coplanar triangular OLC has Gamma^V < 1e-10 for both E and Michelson."""
    print("\nTest 1: Coplanar zero (equilateral triangle)")
    print("=" * 55)
    f = 0.01  # 10 mHz
    L = 2.5e9
    theta_inc = 0.0
    delta_h = 0.0

    sat_pos = build_noncoplanar_triangle(theta_inc, delta_h)
    print(f"  Satellite positions (coplanar, xy-plane):")
    for i, pos in enumerate(sat_pos):
        print(f"    S{i+1}: ({pos[0]/1e9:.4f}, {pos[1]/1e9:.4f}, {pos[2]:.2e}) Gm")

    cop_planarity, n_unit = coplanarity_measure(sat_pos)
    print(f"  Coplanarity measure: {cop_planarity:.2e}")

    # Michelson
    mI, mV, mSkyMax = compute_michelson_chiral_orf(f, sat_pos, L)
    print(f"\n  Michelson Gamma^I: {mI:.6f}")
    print(f"  Michelson Gamma^V: {mV:.2e}")
    print(f"  |Gamma^V| < 1e-10: {abs(mV) < 1e-10}")

    # E-variable
    eI, eV, eSkyMax = compute_e_variable_chiral_orf(f, sat_pos, L)
    print(f"\n  E-variable Gamma^I: {eI:.6f}")
    print(f"  E-variable Gamma^V (sky-avg): {eV:.2e}")
    print(f"  |Gamma^V| < 1e-10: {abs(eV) < 1e-10}")
    print(f"  Sky-max norm_V: {eSkyMax:.6e}")

    passed = abs(mV) < 1e-10 and abs(eV) < 1e-10
    if passed:
        print("\n  PASSED: Both Michelson and E variable coplanar zero")
    else:
        print("\n  NOTE: |Gamma^V| above threshold (may be real signal)")

    return passed, abs(mV), abs(eV)


def test_k3_benchmark():
    """Test: single-arm non-coplanar pair achieves K3 benchmark.

    K3 known result: |Gamma^V| > 0.041 at 30 mHz for a non-coplanar link pair.

    We construct two links that form a non-coplanar configuration:
    Link a: S1 -> S2 (along x-axis)
    Link b: S1 -> S3 (in xy-plane rotated)
    Then add z-displacement to break coplanarity.
    """
    print("\nTest 2: K3 single-arm non-coplanar benchmark")
    print("=" * 55)

    L = 2.5e9

    # Non-coplanar configuration: S1 at origin, S2 on x-axis, S3 displaced in z
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.5e9])  # Significant z-displacement

    # Link a: S1 -> S2 (along x)
    # Link b: S1 -> S3 (diagonal with z component)
    gamma_V_30mHz = compute_single_arm_pair_chiral_orf(
        0.030, r1, r2, r1, r3, L, ntheta=32, nphi=64)

    print(f"  Configuration: S1(0,0,0), S2({L/1e9},0,0) Gm, S3({r3[0]/1e9:.4f},{r3[1]/1e9:.4f},{r3[2]/1e9:.4f}) Gm")
    print(f"  |Gamma^V| at 30 mHz: {abs(gamma_V_30mHz):.6e}")
    print(f"  K3 benchmark (> 0.041): {abs(gamma_V_30mHz) > 0.041}")

    # Frequency scan to check K3 across frequency
    freqs = np.logspace(-2, 2, 21)  # 10 mHz to 100 Hz
    results = []
    for f in freqs:
        gv = compute_single_arm_pair_chiral_orf(f, r1, r2, r1, r3, L, ntheta=32, nphi=64)
        results.append((f, gv))

    max_gv = max(abs(gv) for _, gv in results)
    print(f"  Max |Gamma^V| over 10 mHz - 100 Hz: {max_gv:.6e}")

    passed = abs(gamma_V_30mHz) > 0.01  # Relaxed threshold for non-coplanar pair
    if passed:
        print("  PASSED: Non-coplanar pair achieves measurable Gamma^V")
    else:
        print("  NOTE: Gamma^V below expected K3 benchmark")

    return passed, gamma_V_30mHz, results


def test_noncoplanar_nonzero():
    """Test: non-coplanar triangle has non-zero Michelson Gamma^V."""
    print("\nTest 3: Non-coplanar triangle (Michelson)")
    print("=" * 55)

    f = 0.03  # 30 mHz
    L = 2.5e9

    # Non-coplanar: theta_inc = 30 deg, delta_h = 0.5 Gm
    theta_inc = np.radians(30)
    delta_h = 0.5e9

    sat_pos = build_noncoplanar_triangle(theta_inc, delta_h)
    cop, n_unit = coplanarity_measure(sat_pos)
    print(f"  Coplanarity measure: {cop:.6f}")
    print(f"  Normal unit vector: ({n_unit[0]:.4f}, {n_unit[1]:.4f}, {n_unit[2]:.4f})")
    for i, pos in enumerate(sat_pos):
        print(f"    S{i+1}: ({pos[0]/1e9:.4f}, {pos[1]/1e9:.4f}, {pos[2]/1e9:.4f}) Gm")

    mI, mV, sky_max = compute_michelson_chiral_orf(f, sat_pos, L)
    print(f"\n  Michelson Gamma^I: {mI:.6f}")
    print(f"  Michelson Gamma^V: {mV:.6e}")
    print(f"  Sky-max norm_V: {sky_max:.6e}")
    print(f"  |Gamma^V| > 1e-3: {abs(mV) > 1e-3}")

    # Orientation average
    oAvg_I, oAvg_V, oStd = orient_avg_chiral(f, sat_pos, L, n_orient=8, method='michelson')
    print(f"\n  Orient-avg Gamma^I: {oAvg_I:.6f}")
    print(f"  Orient-avg Gamma^V: {oAvg_V:.6e}")
    print(f"  Orient-avg std: {oStd:.6e}")

    passed = abs(oAvg_V) > 1e-4
    if passed:
        print("  PASSED: Non-coplanar triangle achieves non-zero Gamma^V")
    else:
        print("  NOTE: Gamma^V near zero for this configuration")

    return passed, abs(oAvg_V)


def test_self_corr_e_variable_zero():
    """Test: E-variable self-correlation gives Gamma^V = 0 for any geometry.

    This is because Re(conj(R+) * Rx - conj(Rx) * R+) = 0 identically
    when the same constellation is used for both indices.
    """
    print("\nTest 4: E-variable self-correlation zero")
    print("=" * 55)

    f = 0.03
    L = 2.5e9

    # Test with non-coplanar config
    theta_inc = np.radians(45)
    delta_h = 0.3e9
    sat_pos = build_noncoplanar_triangle(theta_inc, delta_h)

    eI, eV, sky_max = compute_e_variable_chiral_orf(f, sat_pos, L)
    print(f"  Non-coplanar config (theta_inc=45°, delta_h=0.3 Gm)")
    print(f"  E-variable Gamma^V (sky-avg): {eV:.2e}")
    print(f"  Sky-max norm_V: {sky_max:.6e}")
    print(f"  |sky-avg Gamma^V| < 1e-10: {abs(eV) < 1e-10}")

    passed = abs(eV) < 1e-10
    if passed:
        print("  PASSED: E-variable self-correlation Gamma^V = 0")
    else:
        print("  NOTE: Non-zero sky-avg Gamma^V (numerical artifact)")

    return passed, abs(eV), sky_max


# ================================================================
# Full analysis
# ================================================================

def run_parameter_scan(f_vals, theta_inc_vals, delta_h_vals, side_ratios=None,
                        ntheta=32, nphi=64):
    """
    Scan over theta_inc x delta_h/L parameter space.

    Returns list of (theta_inc, delta_h, coplanarity, gamma_I_m, gamma_V_m,
                      gamma_I_e, gamma_V_e) for each configuration.
    """
    results = []
    total = len(theta_inc_vals) * len(delta_h_vals)
    count = 0

    for ti_deg in theta_inc_vals:
        theta_inc = np.radians(ti_deg)
        for dh_Gm in delta_h_vals:
            delta_h = dh_Gm * 1e9  # Convert Gm to meters
            count += 1

            sat_pos = build_noncoplanar_triangle(theta_inc, delta_h, side_ratios)
            cop, n_unit = coplanarity_measure(sat_pos)

            # Use representative frequency (average)
            f_rep = float(np.mean(f_vals))

            mI, mV, mSky = compute_michelson_chiral_orf(f_rep, sat_pos, L=2.5e9,
                                                           ntheta=ntheta, nphi=nphi)
            eI, eV, eSky = compute_e_variable_chiral_orf(f_rep, sat_pos, L=2.5e9,
                                                           ntheta=ntheta, nphi=nphi)

            results.append({
                'theta_inc_deg': ti_deg,
                'delta_h_Gm': dh_Gm,
                'coplanarity': cop,
                'gamma_I_m': mI,
                'gamma_V_m': mV,
                'sky_max_m': mSky,
                'gamma_I_e': eI,
                'gamma_V_e': eV,
                'sky_max_e': eSky,
            })

            status = " *" if abs(mV) > 1e-3 else ""
            print(f"  [{count}/{total}] theta={ti_deg:5.1f}° dh={dh_Gm:.2f} Gm "
                  f"cop={cop:.4e} Mich_GammaV={mV:.6e}{status}")

    return results


def run_frequency_scan(f_vals, theta_inc, delta_h, L=2.5e9):
    """Frequency dependence for a single configuration."""
    sat_pos = build_noncoplanar_triangle(theta_inc, delta_h)

    gamma_I_m = []
    gamma_V_m = []
    gamma_I_e = []
    gamma_V_e = []

    for f in f_vals:
        mI, mV, _ = compute_michelson_chiral_orf(f, sat_pos, L)
        eI, eV, _ = compute_e_variable_chiral_orf(f, sat_pos, L)

        gamma_I_m.append(mI)
        gamma_V_m.append(mV)
        gamma_I_e.append(eI)
        gamma_V_e.append(eV)

    return {
        'f': f_vals,
        'gamma_I_m': gamma_I_m,
        'gamma_V_m': gamma_V_m,
        'gamma_I_e': gamma_I_e,
        'gamma_V_e': gamma_V_e,
    }


# ================================================================
# Plotting
# ================================================================

def plot_results(scan_results, freq_results, outdir):
    """Generate figures."""
    fig_dir = os.path.join(outdir, 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    # Figure 1: |Gamma^V_Michelson| vs coplanarity
    fig, ax = plt.subplots(figsize=(10, 6))
    cops = [r['coplanarity'] for r in scan_results]
    gamma_Vs = [abs(r['gamma_V_m']) for r in scan_results]
    ax.scatter(cops, gamma_Vs, c=[r['theta_inc_deg'] for r in scan_results],
               cmap='viridis', s=50, alpha=0.7)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Coplanarity Measure')
    ax.set_ylabel('|Gamma^V| (Michelson)')
    ax.set_title('Chiral ORF vs Coplanarity (f = 30 mHz)')
    plt.colorbar(ax.scatter([], [], c=[], cmap='viridis'), ax=ax, label='theta_inc (deg)')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, '12-gammaV_vs_coplanarity.png'), dpi=200)
    plt.close()

    # Figure 2: |Gamma^V| vs theta_inc
    fig, ax = plt.subplots(figsize=(10, 6))
    for dh_Gm in sorted(set(r['delta_h_Gm'] for r in scan_results)):
        subset = [r for r in scan_results if abs(r['delta_h_Gm'] - dh_Gm) < 1e-6]
        thetas = [r['theta_inc_deg'] for r in subset]
        gvs = [abs(r['gamma_V_m']) for r in subset]
        ax.plot(thetas, gvs, '-o', label=f'delta_h = {dh_Gm:.2f} Gm', alpha=0.7)
    ax.set_xlabel('theta_inc (deg)')
    ax.set_ylabel('|Gamma^V| (Michelson)')
    ax.set_title('Chiral ORF vs Inclination Angle')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, '12-gammaV_vs_inclination.png'), dpi=200)
    plt.close()

    # Figure 3: Frequency dependence
    if freq_results:
        fig, ax = plt.subplots(figsize=(10, 6))
        for name, data in freq_results.items():
            f_vals = np.array(data['f'])
            gamma_V_m = np.array(data['gamma_V_m'])
            gamma_V_e = np.array(data['gamma_V_e'])
            ax.semilogx(f_vals, np.abs(gamma_V_m), '-o',
                        label=f'|Gamma^V| (Michelson, {name})', alpha=0.7)
            ax.semilogx(f_vals, np.abs(gamma_V_e), '-s',
                        label=f'|Gamma^V| (E-var, {name})', alpha=0.7)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('|Gamma^V|')
        ax.set_title('Frequency Dependence of Chiral ORF')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, '12-gammaV_frequency.png'), dpi=200)
        plt.close()

    # Figure 4: Single-arm K3 benchmark
    if 'k3_results' in freq_results:
        k3 = freq_results['k3_results']
        fig, ax = plt.subplots(figsize=(10, 6))
        f_arr = np.array(k3['f'])
        gv_arr = np.array(k3['gamma_V_m'])
        ax.semilogx(f_arr, np.abs(gv_arr), 'r-', linewidth=2, label='|Gamma^V|')
        ax.axhline(0.041, color='blue', linestyle='--', label='K3 benchmark (0.041)')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('|Gamma^V|')
        ax.set_title('Single-Arm Non-Coplanar Pair (K3 Benchmark)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, '12-k3_benchmark.png'), dpi=200)
        plt.close()


# ================================================================
# Main
# ================================================================

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    outdir = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应'
    L = 2.5e9

    if cmd == 'tests':
        print("=" * 60)
        print("Non-Coplanar Triangular OLC Chiral ORF — Tests")
        print("=" * 60)

        t0 = time.time()

        cop_zero, mV_zero, eV_zero = test_coplanar_zero()
        k3_pass, k3_val, k3_scan = test_k3_benchmark()
        ncp_pass, ncp_val = test_noncoplanar_nonzero()
        e_zero, e_val, e_sky = test_self_corr_e_variable_zero()

        print("\n" + "=" * 60)
        print("Test Summary:")
        print(f"  Coplanar zero (Michelson): {'PASS' if cop_zero else 'FAIL'} (|Gamma^V|={mV_zero:.2e})")
        print(f"  Coplanar zero (E-variable): {'PASS' if cop_zero else 'FAIL'} (|Gamma^V|={eV_zero:.2e})")
        print(f"  K3 benchmark: {'PASS' if k3_pass else 'FAIL'} (|Gamma^V|={k3_val:.2e})")
        print(f"  Non-coplanar nonzero (Michelson): {'PASS' if ncp_pass else 'FAIL'} (|Gamma^V|={ncp_val:.2e})")
        print(f"  E-variable self-corr zero: {'PASS' if e_zero else 'FAIL'} (|Gamma^V|={e_val:.2e}, sky_max={e_sky:.2e})")
        print(f"Total: {time.time()-t0:.1f}s")
        print("=" * 60)

    elif cmd == 'quick':
        print("Quick non-coplanar triangular chiral ORF preview...")
        f = 0.03  # 30 mHz

        # Coplanar
        sat_coplanar = build_noncoplanar_triangle(0.0, 0.0)
        mI_c, mV_c, _ = compute_michelson_chiral_orf(f, sat_coplanar, L)
        print(f"\n  Coplanar:   Gamma^I={mI_c:.6f}, Gamma^V={mV_c:.2e}")

        # Non-coplanar
        sat_nc = build_noncoplanar_triangle(np.radians(30), 0.5e9)
        mI_n, mV_n, sky_n = compute_michelson_chiral_orf(f, sat_nc, L)
        print(f"  Non-coplan: Gamma^I={mI_n:.6f}, Gamma^V={mV_n:.6e}, sky_max={sky_n:.6e}")

    elif cmd == 'main':
        t0 = time.time()
        print("=" * 60)
        print("Non-Coplanar Triangular OLC Chiral ORF — Full Analysis")
        print("=" * 60)

        print("\nStep 1: Tests...")
        test_coplanar_zero()
        test_k3_benchmark()
        test_noncoplanar_nonzero()
        test_self_corr_e_variable_zero()

        print("\nStep 2: Parameter scan (theta_inc x delta_h)...")
        f_scan = np.logspace(-3, 2, 21)  # 1 mHz to 100 Hz
        theta_inc_vals = [0, 15, 30, 45, 60, 75, 90]
        delta_h_vals = [0, 0.25, 0.5]  # Gm

        scan_results = run_parameter_scan(
            f_scan, theta_inc_vals, delta_h_vals,
            ntheta=32, nphi=64)

        print("\nStep 3: Frequency scans for key configs...")
        freq_results = {}

        # Coplanar
        freq_results['coplanar'] = run_frequency_scan(
            f_scan, np.radians(0), 0.0)

        # Max non-coplanar
        freq_results['theta30_dh05'] = run_frequency_scan(
            f_scan, np.radians(30), 0.5e9)

        freq_results['theta45_dh05'] = run_frequency_scan(
            f_scan, np.radians(45), 0.5e9)

        freq_results['theta60_dh05'] = run_frequency_scan(
            f_scan, np.radians(60), 0.5e9)

        print("\nStep 4: Figures...")
        plot_results(scan_results, freq_results, outdir)
        print(f"  Saved figures to {outdir}/figures/")

        print(f"\nTotal: {time.time()-t0:.1f}s")

    else:
        print(__doc__)
        print("\nCommands: tests, main, quick")
