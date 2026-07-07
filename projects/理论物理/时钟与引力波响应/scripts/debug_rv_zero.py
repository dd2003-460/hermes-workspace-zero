#!/usr/bin/env python3
"""
Diagnostic: Why is R^V ≈ 0 for Michelson but non-zero for E-variable?

Tests:
  1. Michelson R^V vs relative inclination (should be ~0 for all)
  2. E-variable R^V vs relative inclination (non-zero for different inclinations)
  3. Parity analysis: does F_+/F_x have definite parity for Michelson?
  4. Transfer-function-free test (TF=1)
  5. Three-arm CW sum vs two-arm Michelson difference
  6. Rotation sweep (z-axis rotation of second detector)

Key physics:
  - R^V = <F_+1*F_x2 - F_x1*F_+2>_sky
  - For a single planar detector, there is a reflection symmetry.
  - If two planar detectors share the same reflection symmetry plane
    (or have aligned normals), the chiral integrand is odd and integrates to 0.
  - For DIFFERENT inclinations, the symmetry planes are different, so
    R^V might not vanish — UNLESS there is a deeper reason.
"""
import numpy as np
import sys
from pathlib import Path

C = 299792458.0
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# ============================================================
# UTILITY: Build triangle detector geometry
# ============================================================

def build_triangle_positions(arm_length, inclination, rotation_phi=0):
    """Equilateral triangle with inclination (x-axis rot) and z-rotation."""
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([arm_length, 0.0, 0.0])
    r3 = np.array([arm_length / 2.0, arm_length * np.sqrt(3) / 2.0, 0.0])
    positions = np.array([r1, r2, r3])

    cos_i = np.cos(inclination)
    sin_i = np.sin(inclination)
    positions[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    positions[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i

    if rotation_phi != 0.0:
        cos_p = np.cos(rotation_phi)
        sin_p = np.sin(rotation_phi)
        new = np.zeros_like(positions)
        new[:, 0] = positions[:, 0] * cos_p - positions[:, 1] * sin_p
        new[:, 1] = positions[:, 0] * sin_p + positions[:, 1] * cos_p
        new[:, 2] = positions[:, 2]
        positions = new

    return positions


def get_basis(th_gw, phi_gw):
    """Polarization basis vectors: th_hat, ph_hat."""
    st, ct = np.sin(th_gw), np.cos(th_gw)
    sp, cp = np.sin(phi_gw), np.cos(phi_gw)
    th_x = ct * cp
    th_y = ct * sp
    th_z = -st
    ph_x = -sp
    ph_y = cp
    ph_z = 0.0
    return th_x, th_y, th_z, ph_x, ph_y, ph_z


def link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z):
    """Single-arm antenna pattern: (F_plus, F_cross)."""
    td = th_x * u[0] + th_y * u[1] + th_z * u[2]
    pd = ph_x * u[0] + ph_y * u[1] + ph_z * u[2]
    return td**2 - pd**2, 2.0 * td * pd


def link_transfer_magnitude(cos_nu, f, L):
    """One-way link transfer function magnitude: |W| = |sinc(beta*(1-cos_nu))|."""
    beta = np.pi * f * L / C
    arg = beta * (1.0 - np.abs(cos_nu))
    eps = 1e-15
    return np.where(np.abs(arg) < eps, 1.0, np.abs(np.sin(arg) / arg))


# ============================================================
# APPROACH A: Two-arm Michelson
# ============================================================

def michelson_response(th_gw, phi_gw, u1, u2, f, L):
    """
    Two-arm Michelson response (TF-modulated).

    M = arm_a - arm_b
    F_M_plus = F_plus(u1)*|W1| - F_plus(u2)*|W2|
    F_M_cross = F_cross(u1)*|W1| - F_cross(u2)*|W2|
    """
    nx = np.sin(th_gw) * np.cos(phi_gw)
    ny = np.sin(th_gw) * np.sin(phi_gw)
    nz = np.cos(th_gw)

    cos_nu1 = nx * u1[0] + ny * u1[1] + nz * u1[2]
    cos_nu2 = nx * u2[0] + ny * u2[1] + nz * u2[2]

    T1 = link_transfer_magnitude(cos_nu1, f, L)
    T2 = link_transfer_magnitude(cos_nu2, f, L)

    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)

    Fp1, Fx1 = link_antenna(u1, th_x, th_y, th_z, ph_x, ph_y, ph_z)
    Fp2, Fx2 = link_antenna(u2, th_x, th_y, th_z, ph_x, ph_y, ph_z)

    y_plus = Fp1 * T1 - Fp2 * T2
    y_cross = Fx1 * T1 - Fx2 * T2
    return y_plus, y_cross


def michelson_response_no_tf(th_gw, phi_gw, u1, u2):
    """Michelson response with transfer function = 1 (no frequency dependence)."""
    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)

    Fp1, Fx1 = link_antenna(u1, th_x, th_y, th_z, ph_x, ph_y, ph_z)
    Fp2, Fx2 = link_antenna(u2, th_x, th_y, th_z, ph_x, ph_y, ph_z)

    y_plus = Fp1 - Fp2
    y_cross = Fx1 - Fx2
    return y_plus, y_cross


# ============================================================
# APPROACH B: CW link sum (E-variable style)
# ============================================================

def cw_link_sum_response(th_gw, phi_gw, positions, f, L):
    """
    Sum of CW link responses (like Orlando E-variable).

    For equilateral triangle, all one-way link lengths = L.
    E ~ sum_k F(k) * W(k)  where k = 1->2, 2->3, 3->1 (CW links)
    """
    nx = np.sin(th_gw) * np.cos(phi_gw)
    ny = np.sin(th_gw) * np.sin(phi_gw)
    nz = np.cos(th_gw)

    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)

    cw_links = [(0, 1), (1, 2), (2, 0)]

    D_plus = np.zeros_like(th_gw, dtype=np.complex128)
    D_cross = np.zeros_like(th_gw, dtype=np.complex128)

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)

        Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)

        cos_nu = nx * u[0] + ny * u[1] + nz * u[2]
        beta_link = np.pi * f * L / C
        arg = beta_link * (1.0 - np.abs(cos_nu))
        eps = 1e-15
        sinc_val = np.where(np.abs(arg) < eps, 1.0, np.sin(arg) / arg)
        phase = np.exp(-1j * beta_link)
        T = sinc_val * phase

        D_plus += Fp * T
        D_cross += Fx * T

    return D_plus, D_cross


def cw_ccw_difference(th_gw, phi_gw, positions, f, L):
    """CW link sum minus CCW link sum."""
    cw_links = [(0, 1), (1, 2), (2, 0)]
    ccw_links = [(1, 0), (2, 1), (0, 2)]

    nx = np.sin(th_gw) * np.cos(phi_gw)
    ny = np.sin(th_gw) * np.sin(phi_gw)
    nz = np.cos(th_gw)

    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)

    R_cw_plus = np.zeros_like(th_gw, dtype=np.complex128)
    R_cw_cross = np.zeros_like(th_gw, dtype=np.complex128)
    R_ccw_plus = np.zeros_like(th_gw, dtype=np.complex128)
    R_ccw_cross = np.zeros_like(th_gw, dtype=np.complex128)

    for i, j in cw_links + ccw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)

        Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)

        cos_nu = nx * u[0] + ny * u[1] + nz * u[2]
        beta_link = np.pi * f * L / C
        arg = beta_link * (1.0 - np.abs(cos_nu))
        eps = 1e-15
        sinc_val = np.where(np.abs(arg) < eps, 1.0, np.sin(arg) / arg)
        phase = np.exp(-1j * beta_link)
        T = sinc_val * phase

        if (i, j) in cw_links:
            R_cw_plus += Fp * T
            R_cw_cross += Fx * T
        else:
            R_ccw_plus += Fp * T
            R_ccw_cross += Fx * T

    R_plus = (R_cw_plus - R_ccw_plus)
    R_cross = (R_cw_cross - R_ccw_cross)
    return R_plus, R_cross


# ============================================================
# Cross-correlation computation
# ============================================================

def compute_orf_pair(FA_plus, FA_cross, FB_plus, FB_cross, dO):
    """
    Compute normalized R^I, R^V and auto-responses.
    Uses real-part cross-correlation (matching Orlando convention).
    """
    Y_I = np.real(FA_plus * np.conj(FB_plus)) + np.real(FA_cross * np.conj(FB_cross))
    Y_V = np.real(FA_plus * np.conj(FB_cross)) - np.real(FA_cross * np.conj(FB_plus))

    r_I_raw = np.sum(Y_I * dO)
    r_V_raw = np.sum(Y_V * dO)

    S_A = np.sum(np.real(FA_plus * np.conj(FA_plus) + FA_cross * np.conj(FA_cross)) * dO)
    S_B = np.sum(np.real(FB_plus * np.conj(FB_plus) + FB_cross * np.conj(FB_cross)) * dO)

    norm = np.sqrt(S_A * S_B)
    if norm < 1e-50:
        return 0.0, 0.0, r_I_raw, r_V_raw, S_A, S_B

    return r_I_raw / norm, r_V_raw / norm, r_I_raw, r_V_raw, S_A, S_B


def make_sky_grid(ntheta=64, nphi=128):
    """Create sky grid and cell areas."""
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2.0 * np.pi / ntheta) * (2.0 * np.pi / nphi)
    return tG, pG, dO


# ============================================================
# TEST 1: Michelson R^V vs relative inclination
# ============================================================
def test1_michelson_inclination_scan():
    """
    Det A: LISA fixed at 60 deg inclination.
    Det B: rotation at varying inclination (0-90 deg).
    Both use two-arm Michelson.
    """
    results = []
    print("=" * 80)
    print("TEST 1: Michelson R^V vs relative inclination")
    print("  Detector A: L = 2.5e9 m, inclination = 60 deg (fixed)")
    print("  Detector B: L = 3.0e9 m, inclination = varying")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L1 = 2.5e9
    L2 = 3.0e9
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    # Apply inclination to detector A
    cos_i = np.cos(np.radians(60.0))
    sin_i = np.sin(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i - uA2[2]*sin_i, uA2[1]*sin_i + uA2[2]*cos_i])

    print(f"\n  f = 0.01 Hz")
    print(f"  {'inc_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}  {'Raw R^I':>14s}  {'Raw R^V':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}  {'-'*14}  {'-'*14}")

    for inc_b_deg in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
        inc_b = np.radians(inc_b_deg)
        cos_i = np.cos(inc_b)
        sin_i = np.sin(inc_b)
        uB2 = np.array([0.5, np.sqrt(3)/2, 0.0])
        uB2_rot = np.array([uB2[0], uB2[1]*cos_i - uB2[2]*sin_i, uB2[1]*sin_i + uB2[2]*cos_i])

        FA_p, FA_c = michelson_response(tG, pG, uA1, uA2_rot, 0.01, L1)
        FB_p, FB_c = michelson_response(tG, pG, uA1, uB2_rot, 0.01, L2)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(FA_p, FA_c, FB_p, FB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        results.append((inc_b_deg, r_I, r_V, ratio, r_I_raw, r_V_raw))
        print(f"  {inc_b_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}  {r_I_raw:14.6e}  {r_V_raw:14.6e}")

    print(f"\n  Max |R^V| = {max(abs(r) for _, _, r, _, _, r in results):.6e}")
    return results


# ============================================================
# TEST 2: E-variable CW sum R^V vs relative inclination
# ============================================================
def test2_evar_inclination_scan():
    """
    Same setup as Test 1, but using E-variable CW link sum.
    """
    results = []
    print("\n" + "=" * 80)
    print("TEST 2: E-variable (CW link sum) R^V vs relative inclination")
    print("  Detector A: L = 2.5e9 m, inclination = 60 deg (fixed)")
    print("  Detector B: L = 3.0e9 m, inclination = varying")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L1 = 2.5e9
    L2 = 3.0e9

    pos_A = build_triangle_positions(L1, np.radians(60.0))

    print(f"\n  f = 0.01 Hz")
    print(f"  {'inc_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}  {'Raw R^I':>14s}  {'Raw R^V':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}  {'-'*14}  {'-'*14}")

    for inc_b_deg in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
        inc_b = np.radians(inc_b_deg)
        pos_B = build_triangle_positions(L2, inc_b)

        DA_p, DA_c = cw_link_sum_response(tG, pG, pos_A, 0.01, L1)
        DB_p, DB_c = cw_link_sum_response(tG, pG, pos_B, 0.01, L2)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(DA_p, DA_c, DB_p, DB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        results.append((inc_b_deg, r_I, r_V, ratio, r_I_raw, r_V_raw))
        print(f"  {inc_b_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}  {r_I_raw:14.6e}  {r_V_raw:14.6e}")

    print(f"\n  Max |R^V| = {max(abs(r) for _, _, r, _, _, r in results):.6e}")
    return results


# ============================================================
# TEST 3: Same-arm-length Michelson R^V scan (L = 2.5e9 both)
# ============================================================
def test3_same_length_michelson():
    """
    Both detectors with L = 2.5e9, to isolate inclination effect.
    """
    results = []
    print("\n" + "=" * 80)
    print("TEST 3: Michelson R^V vs inclination (equal arm lengths, L=2.5e9)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L = 2.5e9
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    cos_i60 = np.cos(np.radians(60.0))
    sin_i60 = np.sin(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i60, uA2[1]*sin_i60])

    print(f"\n  f = 0.01 Hz")
    print(f"  {'inc_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}")

    for inc_b_deg in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
        inc_b = np.radians(inc_b_deg)
        uB2 = np.array([0.5, np.sqrt(3)/2, 0.0])
        uB2_rot = np.array([uB2[0], uB2[1]*np.cos(inc_b), uB2[1]*np.sin(inc_b)])

        FA_p, FA_c = michelson_response(tG, pG, uA1, uA2_rot, 0.01, L)
        FB_p, FB_c = michelson_response(tG, pG, uA1, uB2_rot, 0.01, L)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(FA_p, FA_c, FB_p, FB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        results.append((inc_b_deg, r_I, r_V, ratio))
        print(f"  {inc_b_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")

    print(f"\n  Max |R^V| = {max(abs(r) for _, _, r, _ in results):.6e}")
    return results


# ============================================================
# TEST 4: Frequency scan for Michelson
# ============================================================
def test4_michelson_freq_scan():
    """
    Frequency scan for LISA(60) x Taiji(0) with Michelson.
    """
    print("\n" + "=" * 80)
    print("TEST 4: Michelson frequency scan (LISA 60 x Taiji 0)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L1, L2 = 2.5e9, 3.0e9
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    cos_i60 = np.cos(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i60, uA2[1]*np.sin(np.radians(60.0))])

    print(f"\n  {'f(Hz)':>8s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*8}  {'-'*12}  {'-'*16}  {'-'*14}")

    results = []
    for f in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]:
        FA_p, FA_c = michelson_response(tG, pG, uA1, uA2_rot, f, L1)
        FB_p, FB_c = michelson_response(tG, pG, uA1, uA2_rot, f, L2)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(FA_p, FA_c, FB_p, FB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        results.append((f, r_I, r_V, ratio))
        print(f"  {f:8.3f}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")

    print(f"\n  Max |R^V| = {max(abs(r) for _, _, r, _ in results):.6e}")
    return results


# ============================================================
# TEST 5: E-variable CW vs CW-CCW difference
# ============================================================
def test5_cw_vs_ccw():
    """
    Show that CW link sum is non-zero but CW-CCW is exactly zero.
    This proves the E-variable is fundamentally different from Michelson.
    """
    print("\n" + "=" * 80)
    print("TEST 5: CW sum vs CW-CCW (same detector, equilateral triangle)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L = 2.5e9
    pos = build_triangle_positions(L, np.radians(60.0))

    for f in [0.001, 0.01, 0.1, 1.0]:
        D_p, D_c = cw_link_sum_response(tG, pG, pos, f, L)
        R_p, R_c = cw_ccw_difference(tG, pG, pos, f, L)

        cw_rms = np.sqrt(np.mean(np.abs(D_p)**2 + D_c**2))
        ccw_rms = np.sqrt(np.mean(np.abs(R_p)**2 + R_c**2))

        print(f"\n  f = {f} Hz:")
        print(f"    CW sum:     |D|_rms = {cw_rms:.6f}")
        print(f"    CW-CCW:     |R|_rms = {ccw_rms:.15e}")
        print(f"    CW-CCW / CW  = {ccw_rms/cw_rms:.2e}")

    print(f"\n  CONCLUSION: CW-CCW = 0 exactly for equilateral triangle.")
    print(f"  Michelson = arm_a - arm_b (2 arms) is similar to CW-CCW.")
    print(f"  E-variable = CW sum (3 links) is fundamentally different.")


# ============================================================
# TEST 6: Rotation sweep
# ============================================================
def test6_rotation_sweep():
    """
    Z-axis rotation of Detector B relative to Detector A.
    This tests whether changing the azimuthal angle breaks the symmetry.
    """
    print("\n" + "=" * 80)
    print("TEST 6: Z-axis rotation sweep (Michelson, equal lengths)")
    print("  Detector A: inclination=60 deg, phi=0 (fixed)")
    print("  Detector B: inclination=0 deg, phi=varying")
    print("  L = 2.5e9 m both")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L = 2.5e9
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    cos_i60 = np.cos(np.radians(60.0))
    sin_i60 = np.sin(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i60, uA2[1]*sin_i60])

    print(f"\n  f = 0.01 Hz")
    print(f"  {'rot_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}")

    results = []
    for rot_deg in range(0, 360, 15):
        rot = np.radians(rot_deg)
        cos_r = np.cos(rot)
        sin_r = np.sin(rot)

        uB1_base = np.array([1.0, 0.0, 0.0])
        uB2_base = np.array([0.5, np.sqrt(3)/2, 0.0])

        # Apply z-rotation then inclination
        uB1_z = np.array([uB1_base[0]*cos_r, uB1_base[0]*sin_r, 0.0])
        uB2_z = np.array([uB2_base[0]*cos_r - uB2_base[1]*sin_r,
                           uB2_base[0]*sin_r + uB2_base[1]*cos_r, 0.0])

        # No inclination for B (0 deg)
        uB1 = uB1_z
        uB2 = uB2_z

        FA_p, FA_c = michelson_response(tG, pG, uA1, uA2_rot, 0.01, L)
        FB_p, FB_c = michelson_response(tG, pG, uB1, uB2, 0.01, L)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(FA_p, FA_c, FB_p, FB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        results.append((rot_deg, r_I, r_V, ratio))
        print(f"  {rot_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")

    print(f"\n  Max |R^V| = {max(abs(r) for _, _, r, _ in results):.6e}")
    return results


# ============================================================
# TEST 7: TF-free comparison (transfer function = 1 for all)
# ============================================================
def test7_no_tf():
    """
    Without transfer functions, the comparison is cleaner.
    Tests if R^V = 0 for Michelson even without TF modulation.
    """
    print("\n" + "=" * 80)
    print("TEST 7: TF-free (transfer function = 1)")
    print("  Michelson R^V vs inclination (no TF modulation)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    cos_i60 = np.cos(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i60, uA2[1]*np.sin(np.radians(60.0))])

    print(f"\n  Michelson (TF-free):")
    print(f"  {'inc_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}")

    for inc_b_deg in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
        inc_b = np.radians(inc_b_deg)
        uB2 = np.array([0.5, np.sqrt(3)/2, 0.0])
        uB2_rot = np.array([uB2[0], uB2[1]*np.cos(inc_b), uB2[1]*np.sin(inc_b)])

        FA_p, FA_c = michelson_response_no_tf(tG, pG, uA1, uA2_rot)
        FB_p, FB_c = michelson_response_no_tf(tG, pG, uA1, uB2_rot)

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(FA_p, FA_c, FB_p, FB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        print(f"  {inc_b_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")

    # Also test E-variable TF-free
    print(f"\n  E-variable (TF-free, CW sum):")
    print(f"  {'inc_B(deg)':>10s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*16}  {'-'*14}")

    pos_A = build_triangle_positions(2.5e9, np.radians(60.0))

    for inc_b_deg in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
        pos_B = build_triangle_positions(2.5e9, np.radians(inc_b_deg))

        # Simple CW sum without TF
        DA_p = np.zeros_like(tG)
        DA_c = np.zeros_like(tG)
        for i, j in [(0,1),(1,2),(2,0)]:
            u = pos_A[j] - pos_A[i]
            u = u / np.linalg.norm(u)
            Fp, Fx = link_antenna(u, *get_basis(tG, pG))
            DA_p += Fp
            DA_c += Fx

        DB_p = np.zeros_like(tG)
        DB_c = np.zeros_like(tG)
        for i, j in [(0,1),(1,2),(2,0)]:
            u = pos_B[j] - pos_B[i]
            u = u / np.linalg.norm(u)
            Fp, Fx = link_antenna(u, *get_basis(tG, pG))
            DB_p += Fp
            DB_c += Fx

        r_I, r_V, r_I_raw, r_V_raw, S_A, S_B = compute_orf_pair(DA_p, DA_c, DB_p, DB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        print(f"  {inc_b_deg:10d}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")


# ============================================================
# TEST 8: Pointwise integrand analysis for Michelson
# ============================================================
def test8_integrand_analysis():
    """
    Analyze the pointwise chiral integrand Y_V = F_+1*F_x2 - F_x1*F_+2
    for Michelson detectors.
    """
    print("\n" + "=" * 80)
    print("TEST 8: Pointwise integrand analysis (Michelson, f=0.01 Hz)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L1, L2 = 2.5e9, 3.0e9
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    cos_i60 = np.cos(np.radians(60.0))
    uA2_rot = np.array([uA2[0], uA2[1]*cos_i60, uA2[1]*np.sin(np.radians(60.0))])

    # Taiji at 0 deg
    uB1 = np.array([1.0, 0.0, 0.0])
    uB2 = np.array([0.5, np.sqrt(3)/2, 0.0])

    FA_p, FA_c = michelson_response(tG, pG, uA1, uA2_rot, 0.01, L1)
    FB_p, FB_c = michelson_response(tG, pG, uB1, uB2, 0.01, L2)

    Y_V = np.real(FA_p * np.conj(FB_c)) - np.real(FA_c * np.conj(FB_p))
    Y_I = np.real(FA_p * np.conj(FB_p)) + np.real(FA_c * np.conj(FB_c))

    print(f"\n  Chiral integrand Y_V:")
    print(f"    Max:   {np.max(Y_V):.8f}")
    print(f"    Min:   {np.min(Y_V):.8f}")
    print(f"    RMS:   {np.sqrt(np.mean(Y_V**2)):.8f}")
    print(f"    Mean:  {np.mean(Y_V):.8e}")
    print(f"    Sky int: {np.sum(Y_V * dO):.8e}")

    print(f"\n  Even integrand Y_I:")
    print(f"    Max:   {np.max(Y_I):.8f}")
    print(f"    Min:   {np.min(Y_I):.8f}")
    print(f"    RMS:   {np.sqrt(np.mean(Y_I**2)):.8f}")
    print(f"    Mean:  {np.mean(Y_I):.8e}")

    # Sign distribution
    npos = np.sum(Y_V > 1e-10)
    nneg = np.sum(Y_V < -1e-10)
    nzero = np.sum(np.abs(Y_V) <= 1e-10)
    print(f"\n  Sign distribution of Y_V:")
    print(f"    Positive cells: {npos} ({npos/tG.size*100:.1f}%)")
    print(f"    Negative cells: {nneg} ({nneg/tG.size*100:.1f}%)")
    print(f"    Near-zero cells: {nzero} ({nzero/tG.size*100:.1f}%)")


# ============================================================
# TEST 9: E-variable F+ and Fx parity analysis
# ============================================================
def test9_evar_parity():
    """
    Analyze the parity properties of E-variable antenna patterns.
    Check if the E-variable has definite parity under reflection.
    """
    print("\n" + "=" * 80)
    print("TEST 9: E-variable parity analysis")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L = 2.5e9
    pos = build_triangle_positions(L, np.radians(60.0))
    D_p, D_c = cw_link_sum_response(tG, pG, pos, 0.01, L)

    # Check: for a single detector, is the E-variable antenna pattern
    # symmetric or antisymmetric under some reflection?
    print(f"\n  Single detector (L=2.5e9, inc=60 deg):")
    print(f"    |D_+|_rms = {np.sqrt(np.mean(np.abs(D_p)**2)):.6f}")
    print(f"    |D_x|_rms = {np.sqrt(np.mean(np.abs(D_c)**2)):.6f}")
    print(f"    <D_+> = {np.mean(D_p):.6e}")
    print(f"    <D_x> = {np.mean(D_c):.6e}")

    # Self-correlation: should give R^V = 0 (since same detector)
    D2_p, D2_c = cw_link_sum_response(tG, pG, pos, 0.01, L)
    r_I, r_V, _, _, _, _ = compute_orf_pair(D_p, D_c, D2_p, D2_c, dO)
    print(f"\n  Self-correlation:")
    print(f"    R^I = {r_I:.8f}, R^V = {r_V:.8e}")

    # Check: does <F_+ * F_x> = 0 for a single detector?
    cross_term = np.real(D_p * np.conj(D_c))
    print(f"\n  <F_+ * F_x> (same detector) = {np.mean(cross_term):.8e}")


# ============================================================
# TEST 10: E-variable frequency scan
# ============================================================
def test10_evar_freq_scan():
    """
    E-variable frequency scan for LISA(60) x Taiji(0).
    """
    print("\n" + "=" * 80)
    print("TEST 10: E-variable frequency scan (LISA 60 x Taiji 0)")
    print("=" * 80)

    tG, pG, dO = make_sky_grid()

    L1, L2 = 2.5e9, 3.0e9
    pos_A = build_triangle_positions(L1, np.radians(60.0))
    pos_B = build_triangle_positions(L2, 0.0)

    print(f"\n  {'f(Hz)':>8s}  {'R^I':>12s}  {'R^V':>16s}  {'|R^V/R^I|':>14s}")
    print(f"  {'-'*8}  {'-'*12}  {'-'*16}  {'-'*14}")

    for f in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]:
        DA_p, DA_c = cw_link_sum_response(tG, pG, pos_A, f, L1)
        DB_p, DB_c = cw_link_sum_response(tG, pG, pos_B, f, L2)
        r_I, r_V, _, _, _, _ = compute_orf_pair(DA_p, DA_c, DB_p, DB_c, dO)
        ratio = abs(r_V) / (abs(r_I) + 1e-50)
        print(f"  {f:8.3f}  {r_I:12.6f}  {r_V:16.6e}  {ratio:14.6e}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("#" * 80)
    print("# DEBUG: Why is R^V zero for Michelson but non-zero for E-variable?")
    print("#" * 80)

    test1_michelson_inclination_scan()
    test2_evar_inclination_scan()
    test3_same_length_michelson()
    test4_michelson_freq_scan()
    test5_cw_vs_ccw()
    test6_rotation_sweep()
    test7_no_tf()
    test8_integrand_analysis()
    test9_evar_parity()
    test10_evar_freq_scan()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
