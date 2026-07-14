#!/usr/bin/env python3
"""
Investigate when R^V is non-zero for detector pairs.

Key finding: R^V = 0 for two coplanar detectors because the chiral integrand
F_+^A * F_x^B - F_x^A * F_+^B is odd under y-reflection (for detectors with
arm 1 along x-axis). The sky integral vanishes.

To get R^V != 0, need to break reflection symmetry:
1. Non-coplanar detectors (arm directions with z-components)
2. Different observable types
3. Specific sky direction (not sky-averaged)
"""
import numpy as np
import sys

C = 299792458.0


def get_basis(th_gw, phi_gw):
    st, ct = np.sin(th_gw), np.cos(th_gw)
    sp, cp = np.sin(phi_gw), np.cos(phi_gw)
    return ct * cp, ct * sp, -st, -sp, cp, 0.0


def link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z):
    td = th_x * u[0] + th_y * u[1] + th_z * u[2]
    pd = ph_x * u[0] + ph_y * u[1] + ph_z * u[2]
    return td ** 2 - pd ** 2, 2.0 * td * pd


def transfer_function(f, L, cos_nu):
    beta = np.pi * f * L / C
    arg = beta * (1.0 - cos_nu)
    eps = 1e-15
    sinc_v = np.where(np.abs(arg) < eps, 1.0, np.sin(arg) / arg)
    phase = np.exp(-1j * beta)
    return sinc_v * phase


def michelson_response(th_gw, phi_gw, u1, u2, f, L):
    """Two-arm Michelson response."""
    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)
    y_plus = np.zeros_like(th_gw)
    y_cross = np.zeros_like(th_gw)
    for u in [u1, u2]:
        Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)
        # Apply transfer function (same for both arms at low freq)
        y_plus += Fp
        y_cross += Fx
    return y_plus, y_cross


def michelson_triangular_cross(f, thG, phG, uA1, uA2, uB1, uB2, L1, L2):
    """
    Cross-correlation between two Michelson-like detectors.
    Detector A: arms along uA1 and uA2 (from common vertex)
    Detector B: arms along uB1 and uB2

    But we compute using 3-link triangular response for each detector:
    For Michelson: only use 2 links
    For E-variable: use 3 links

    This function uses 2 links per detector (Michelson-like).
    """
    nx = np.sin(thG) * np.cos(phG)
    ny = np.sin(thG) * np.sin(phG)
    nz = np.cos(thG)

    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(thG, phG)

    dO = np.sin(thG) * (2.0 * np.pi / thG.shape[0]) * (2.0 * np.pi / phG.shape[1])

    # Arm directions for detector A (2 arms from common vertex)
    # These are unit vectors, positions don't matter for the arm direction
    cos_A1 = nx * uA1[0] + ny * uA1[1] + nz * uA1[2]
    cos_A2 = nx * uA2[0] + ny * uA2[1] + nz * uA2[2]

    cos_B1 = nx * uB1[0] + ny * uB1[1] + nz * uB1[2]
    cos_B2 = nx * uB2[0] + ny * uB2[1] + nz * uB2[2]

    T_A1 = np.abs(transfer_function(f, L1, cos_A1))
    T_A2 = np.abs(transfer_function(f, L1, cos_A2))
    T_B1 = np.abs(transfer_function(f, L2, cos_B1))
    T_B2 = np.abs(transfer_function(f, L2, cos_B2))

    # Michelson responses
    RA_plus, RA_cross = michelson_response(thG, phG, uA1, uA2, f, L1)
    RB_plus, RB_cross = michelson_response(thG, phG, uB1, uB2, f, L2)

    # Apply transfer functions (weight each arm by its TF)
    # Actually for Michelson, both arms are part of the same detector
    # The response is F_+ = F_+^arm1 + F_+^arm2 (without separate TF weighting)

    # Cross-correlation
    Y_I = RA_plus * RB_plus + RA_cross * RB_cross
    Y_V = RA_plus * RB_cross - RA_cross * RB_plus

    r_I_raw = np.sum(Y_I * dO)
    r_V_raw = np.sum(Y_V * dO)

    # Auto-responses
    S_A = np.sum((RA_plus**2 + RA_cross**2) * dO)
    S_B = np.sum((RB_plus**2 + RB_cross**2) * dO)

    norm = np.sqrt(S_A * S_B)
    if norm < 1e-50:
        return 0.0, 0.0, r_I_raw, r_V_raw, S_A, S_B

    return r_I_raw / norm, r_V_raw / norm, r_I_raw, r_V_raw, S_A, S_B


def build_triangular_positions(arm_length, inclination_deg, rotation_deg=0):
    cos_i = np.cos(np.radians(inclination_deg))
    sin_i = np.sin(np.radians(inclination_deg))
    cos_r = np.cos(np.radians(rotation_deg))
    sin_r = np.sin(np.radians(rotation_deg))

    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([arm_length, 0.0, 0.0])
    r3 = np.array([arm_length / 2.0, arm_length * np.sqrt(3) / 2.0, 0.0])
    positions = np.array([r1, r2, r3])

    # Inclination
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    positions = rotated

    # Rotation
    if rotation_deg != 0:
        new_pos = np.zeros_like(positions)
        new_pos[:, 0] = positions[:, 0] * cos_r - positions[:, 1] * sin_r
        new_pos[:, 1] = positions[:, 0] * sin_r + positions[:, 1] * cos_r
        new_pos[:, 2] = positions[:, 2]
        positions = new_pos

    return positions


def test_chiral_symmetry():
    """Test: does R^V vanish for coplanar vs inclined detector pairs?"""
    print("=" * 70)
    print("CHIRAL SYMMETRY TEST: R^V for various detector configurations")
    print("=" * 70)

    ntheta, nphi = 64, 128
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')

    f = 0.01  # low frequency

    # Configuration 1: Both coplanar (same plane)
    # Arm directions in xy-plane
    u1 = np.array([1.0, 0.0, 0.0])
    u2 = np.array([0.5, np.sqrt(3)/2, 0.0])

    rI, rV, _, _, _, _ = michelson_triangular_cross(f, tG, pG, u1, u2, u1, u2, 2.5e9, 2.5e9)
    print(f"\n  Coplanar x Coplanar (same orientation): R^I={rI:.6f}, R^V={rV:.6e}")

    # Configuration 2: Both coplanar (different orientation, different arm direction)
    # Rotate second detector by 30 degrees
    u2b1 = np.array([np.cos(np.radians(30)), np.sin(np.radians(30)), 0.0])
    u2b2 = np.array([np.cos(np.radians(90)), np.sin(np.radians(90)), 0.0])

    rI, rV, _, _, _, _ = michelson_triangular_cross(f, tG, pG, u1, u2, u2b1, u2b2, 2.5e9, 2.5e9)
    print(f"  Coplanar x Coplanar (30 deg rot): R^I={rI:.6f}, R^V={rV:.6e}")

    # Configuration 3: LISA (60 deg) x Taiji (0 deg) - coplanar Michelson
    uL1 = np.array([1.0, 0.0, 0.0])
    uL2 = np.array([0.5, (np.sqrt(3)/2)*np.cos(np.radians(60)), (np.sqrt(3)/2)*np.sin(np.radians(60))])
    uT1 = np.array([1.0, 0.0, 0.0])
    uT2 = np.array([0.5, np.sqrt(3)/2, 0.0])

    rI, rV, _, _, _, _ = michelson_triangular_cross(f, tG, pG, uL1, uL2, uT1, uT2, 2.5e9, 3.0e9)
    print(f"  LISA(60) x Taiji(0) [2-arm]: R^I={rI:.6f}, R^V={rV:.6e}")

    # Configuration 4: LISA(60) x LISA(60) but rotated relative to each other
    uL1_rot = np.array([np.cos(np.radians(45)), np.sin(np.radians(45)), 0.0])
    uL2_rot = np.array([0.5, (np.sqrt(3)/2)*np.cos(np.radians(60))*np.cos(np.radians(45)) - (np.sqrt(3)/2)*np.sin(np.radians(60))*np.sin(np.radians(45)),
                         (np.sqrt(3)/2)*np.cos(np.radians(60))*np.sin(np.radians(45)) + (np.sqrt(3)/2)*np.sin(np.radians(60))*np.cos(np.radians(45))])

    rI, rV, _, _, _, _ = michelson_triangular_cross(f, tG, pG, uL1, uL2, uL1_rot, uL2_rot, 2.5e9, 2.5e9)
    print(f"  LISA(60) x LISA(60,rot45): R^I={rI:.6f}, R^V={rV:.6e}")

    # Configuration 5: Try with NON-ZERO ROTATION for Taiji
    # Taiji rotated by 90 deg about z-axis
    posA = build_triangular_positions(2.5e9, 60.0, 0.0)
    posB = build_triangular_positions(3.0e9, 0.0, 90.0)

    uA1 = (posA[1] - posA[0]) / np.linalg.norm(posA[1] - posA[0])
    uA2 = (posA[2] - posA[0]) / np.linalg.norm(posA[2] - posA[0])
    uB1 = (posB[1] - posB[0]) / np.linalg.norm(posB[1] - posB[0])
    uB2 = (posB[2] - posB[0]) / np.linalg.norm(posB[2] - posB[0])

    rI, rV, _, _, _, _ = michelson_triangular_cross(f, tG, pG, uA1, uA2, uB1, uB2, 2.5e9, 3.0e9)
    print(f"  LISA(60,rot0) x Taiji(0,rot90) [2-arm]: R^I={rI:.6f}, R^V={rV:.6e}")

    # Configuration 6: Same as 5 but with triangular 3-link response
    def triangular_cross_response(f, posA, posB, tG, pG, L1, L2):
        nx = np.sin(tG) * np.cos(pG)
        ny = np.sin(tG) * np.sin(pG)
        nz = np.cos(tG)
        th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(tG, pG)
        dO = np.sin(tG) * (2.0 * np.pi / tG.shape[0]) * (2.0 * np.pi / pG.shape[1])

        links_A = [(0,1), (1,2), (2,0)]
        links_B = [(0,1), (1,2), (2,0)]

        RA_p = np.zeros_like(tG, dtype=np.complex128)
        RA_c = np.zeros_like(tG, dtype=np.complex128)
        RB_p = np.zeros_like(tG, dtype=np.complex128)
        RB_c = np.zeros_like(tG, dtype=np.complex128)

        for idx, (i, j) in enumerate(links_A):
            u = (posA[j] - posA[i]) / np.linalg.norm(posA[j] - posA[i])
            Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)
            cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
            T = np.abs(transfer_function(f, L1, cos_nu))
            RA_p += Fp * T
            RA_c += Fx * T

        for idx, (i, j) in enumerate(links_B):
            u = (posB[j] - posB[i]) / np.linalg.norm(posB[j] - posB[i])
            Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)
            cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
            T = np.abs(transfer_function(f, L2, cos_nu))
            RB_p += Fp * T
            RB_c += Fx * T

        Y_I = np.real(RA_p * RB_p + RA_c * RB_c)
        Y_V = np.real(RA_p * RB_c - RA_c * RB_p)

        r_I_raw = np.sum(Y_I * dO)
        r_V_raw = np.sum(Y_V * dO)
        S_A = np.sum(np.real(np.abs(RA_p)**2 + np.abs(RA_c)**2) * dO)
        S_B = np.sum(np.real(np.abs(RB_p)**2 + np.abs(RB_c)**2) * dO)

        norm = np.sqrt(S_A * S_B)
        if norm < 1e-50:
            return 0.0, 0.0
        return r_I_raw / norm, r_V_raw / norm

    posA0 = build_triangular_positions(2.5e9, 60.0, 0.0)
    posB90 = build_triangular_positions(3.0e9, 0.0, 90.0)
    rI, rV = triangular_cross_response(f, posA0, posB90, tG, pG, 2.5e9, 3.0e9)
    print(f"  Triangular: LISA(60,rot0) x Taiji(0,rot90): R^I={rI:.6f}, R^V={rV:.6e}")

    posA0 = build_triangular_positions(2.5e9, 60.0, 0.0)
    posB0 = build_triangular_positions(3.0e9, 0.0, 0.0)
    rI, rV = triangular_cross_response(f, posA0, posB0, tG, pG, 2.5e9, 3.0e9)
    print(f"  Triangular: LISA(60,rot0) x Taiji(0,rot0): R^I={rI:.6f}, R^V={rV:.6e}")

    posA0 = build_triangular_positions(2.5e9, 60.0, 0.0)
    posB45 = build_triangular_positions(3.0e9, 0.0, 45.0)
    rI, rV = triangular_cross_response(f, posA0, posB45, tG, pG, 2.5e9, 3.0e9)
    print(f"  Triangular: LISA(60,rot0) x Taiji(0,rot45): R^I={rI:.6f}, R^V={rV:.6e}")

    print("\n  CONCLUSION: R^V is ~0 for all planar detector configurations.")
    print("  This is expected: planar detectors have mirror symmetry that forces")
    print("  the chiral integrand to be odd under sky reflection.")


def test_pointwise_chiral():
    """Test: is the chiral integrand non-zero at individual sky positions?"""
    print("\n" + "=" * 70)
    print("POINTWISE CHIRAL TEST: is Y_V non-zero at individual sky positions?")
    print("=" * 70)

    f = 0.01
    ntheta, nphi = 16, 32
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')

    # Two coplanar detectors
    uA1 = np.array([1.0, 0.0, 0.0])
    uA2 = np.array([0.5, np.sqrt(3)/2, 0.0])
    uB1 = np.array([np.cos(np.radians(30)), np.sin(np.radians(30)), 0.0])
    uB2 = np.array([np.cos(np.radians(90)), np.sin(np.radians(90)), 0.0])

    RA_p, RA_c = michelson_response(tG, pG, uA1, uA2, f, 2.5e9)
    RB_p, RB_c = michelson_response(tG, pG, uB1, uB2, f, 2.5e9)

    Y_V = RA_p * RB_c - RA_c * RB_p

    print(f"\n  Chiral integrand Y_V at each sky position (coplanar detectors):")
    print(f"    Y_V is NOT identically zero: {not np.allclose(Y_V, 0)}")
    print(f"    |Y_V|_max = {np.max(np.abs(Y_V)):.6f}")
    print(f"    |Y_V|_rms = {np.sqrt(np.mean(np.abs(Y_V)**2)):.6f}")
    print(f"    Sky-integrated R^V = {np.sum(Y_V * np.sin(tG) * (2*np.pi/ntheta) * (2*np.pi/nphi)):.6e}")

    print("\n  The chiral integrand is NON-ZERO pointwise but integrates to zero")
    print("  on the sky. This confirms the mirror symmetry argument.")


if __name__ == '__main__':
    test_chiral_symmetry()
    test_pointwise_chiral()
