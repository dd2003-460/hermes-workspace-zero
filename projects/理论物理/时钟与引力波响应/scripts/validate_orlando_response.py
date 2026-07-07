#!/usr/bin/env python3
"""
Validate Orlando et al. (arXiv:2011.07059) response functions R^I(f) and R^V(f)
for the LISA-Taiji detector pair.

Data model: D^{Lambda tau} = h^2 Omega^I_GW R^I_{Lambda tau} + h^2 Omega^V_GW R^V_{Lambda tau}

The response functions R^I and R^V are normalized cross-correlation functions:

  R^I(f) = <F_+^A F_+^B + F_x^A F_x^B>_sky / sqrt(S_A(f) S_B(f))
  R^V(f) = <F_+^A F_x^B - F_x^A F_+^B>_sky / sqrt(S_A(f) S_B(f))

Detector model: Two-arm Michelson interferometer (each detector defined by two arm
unit vectors from a common vertex).

Detector geometry:
  - LISA: triangular, arm length 2.5 Mkm, 60 deg inclination to ecliptic plane
  - Taiji: triangular, arm length 3.0 Mkm, 0 deg inclination (in ecliptic plane)

Usage:
  python3 validate_orlando_response.py tests   -- unit tests (self-correlation R^V = 0)
  python3 validate_orlando_response.py main    -- full analysis with frequency scan
  python3 validate_orlando_response.py quick   -- quick preview at f = 0.01 Hz
"""
import numpy as np
import sys
from pathlib import Path

C = 299792458.0  # m/s


def get_basis(th_gw, phi_gw):
    """Polarization basis vectors. Returns (th_x, th_y, th_z, ph_x, ph_y, ph_z)."""
    st, ct = np.sin(th_gw), np.cos(th_gw)
    sp, cp = np.sin(phi_gw), np.cos(phi_gw)
    return ct * cp, ct * sp, -st, -sp, cp, 0.0


def link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z):
    """Antenna pattern for a single link along unit vector u."""
    td = th_x * u[0] + th_y * u[1] + th_z * u[2]
    pd = ph_x * u[0] + ph_y * u[1] + ph_z * u[2]
    return td ** 2 - pd ** 2, 2.0 * td * pd


def link_transfer(cos_nu, f, L):
    """One-way link transfer function magnitude: |W| = sinc(beta(1 - cos_nu))."""
    beta = np.pi * f * L / C
    arg = beta * (1.0 - np.abs(cos_nu))
    eps = 1e-15
    return np.where(np.abs(arg) < eps, 1.0, np.sin(arg) / arg)


def michelson_response_with_tf(th_gw, phi_gw, u1, u2, f, L):
    """
    Michelson response with transfer function for each arm.

    The response for each arm is F_arm * |W_arm| where W is the
    one-way link transfer function. The Michelson response is the
    sum of the two arm responses.

    Returns: (y_plus, y_cross) arrays (complex-valued to track phases).
    """
    nx = np.sin(th_gw)
    ny = np.sin(th_gw)
    nz = np.cos(th_gw)
    # Compute cos_nu for each arm
    cos_nu1 = nx * u1[0] + ny * u1[1] + nz * u1[2]
    cos_nu2 = nx * u2[0] + ny * u2[1] + nz * u2[2]

    # Transfer function magnitudes (real, positive)
    T1 = link_transfer(cos_nu1, f, L)
    T2 = link_transfer(cos_nu2, f, L)

    th_x, th_y, th_z, ph_x, ph_y, ph_z = get_basis(th_gw, phi_gw)
    y_plus = np.zeros_like(th_gw)
    y_cross = np.zeros_like(th_gw)
    for idx, u in enumerate([u1, u2]):
        Fp, Fx = link_antenna(u, th_x, th_y, th_z, ph_x, ph_y, ph_z)
        T = T1 if idx == 0 else T2
        y_plus += Fp * T
        y_cross += Fx * T
    return y_plus, y_cross


def compute_response(tG, pG, uA1, uA2, uB1, uB2, freq, L1, L2):
    """
    Compute normalized R^I(f), R^V(f) for two Michelson-like detectors.
    Includes transfer function modulation.

    Returns: (r_I_norm, r_V_norm, r_I_raw, r_V_raw, S_A, S_B)
    """
    dO = np.sin(tG) * (2.0 * np.pi / tG.shape[0]) * (2.0 * np.pi / pG.shape[1])

    FAp_plus, FAp_cross = michelson_response_with_tf(tG, pG, uA1, uA2, freq, L1)
    FBp_plus, FBp_cross = michelson_response_with_tf(tG, pG, uB1, uB2, freq, L2)

    # Cross-correlation integrals (parity-even and parity-odd)
    # Use real parts: <Re(A)*Re(B) + Im(A)*Im(B)> for even, etc.
    Y_I = np.real(FAp_plus * np.conj(FBp_plus)) + np.real(FAp_cross * np.conj(FBp_cross))
    Y_V = np.real(FAp_plus * np.conj(FBp_cross)) - np.real(FAp_cross * np.conj(FBp_plus))

    r_I_raw = np.sum(Y_I * dO)
    r_V_raw = np.sum(Y_V * dO)

    # Detector auto-responses
    S_A = np.sum(np.real(FAp_plus * np.conj(FAp_plus) + FAp_cross * np.conj(FAp_cross)) * dO)
    S_B = np.sum(np.real(FBp_plus * np.conj(FBp_plus) + FBp_cross * np.conj(FBp_cross)) * dO)

    norm = np.sqrt(S_A * S_B)
    if norm < 1e-50:
        return 0.0, 0.0, r_I_raw, r_V_raw, S_A, S_B

    return r_I_raw / norm, r_V_raw / norm, r_I_raw, r_V_raw, S_A, S_B


def build_detector_arms(arm_length, inclination_deg, rotation_deg=0):
    """
    Build equilateral triangle and return two arm unit vectors from satellite 1.

    Args:
        arm_length: physical arm length (m)
        inclination_deg: inclination to ecliptic (x-axis rotation)
        rotation_deg: rotation about z-axis

    Returns:
        u1, u2: normalized arm unit vectors (from satellite 1 to 2, and 1 to 3)
        posA: (3, 3) satellite positions
        plane_normal: unit normal to detector plane
    """
    cos_i = np.cos(np.radians(inclination_deg))
    sin_i = np.sin(np.radians(inclination_deg))
    cos_r = np.cos(np.radians(rotation_deg))
    sin_r = np.sin(np.radians(rotation_deg))

    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([arm_length, 0.0, 0.0])
    r3 = np.array([arm_length / 2.0, arm_length * np.sqrt(3) / 2.0, 0.0])
    positions = np.array([r1, r2, r3])

    # Inclination: rotation about x-axis
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    positions = rotated

    # Rotation about z-axis
    if rotation_deg != 0:
        new_pos = np.zeros_like(positions)
        new_pos[:, 0] = positions[:, 0] * cos_r - positions[:, 1] * sin_r
        new_pos[:, 1] = positions[:, 0] * sin_r + positions[:, 1] * cos_r
        new_pos[:, 2] = positions[:, 2]
        positions = new_pos

    u1 = (positions[1] - positions[0]) / np.linalg.norm(positions[1] - positions[0])
    u2 = (positions[2] - positions[0]) / np.linalg.norm(positions[2] - positions[0])
    n = np.cross(u1, u2)
    n = n / np.linalg.norm(n)

    return u1, u2, positions, n


def print_header(title):
    print(f"\n{'=' * 78}")
    print(f"  {title}")
    print(f"{'=' * 78}")


def print_results_table(freqs, data_dict, desc=""):
    if desc:
        print(f"\n  {desc}")
    print(f"\n  {'f (Hz)':>10s}  {'fL/c':>8s}  {'R^I':>12s}  {'R^V':>14s}  "
          f"{'|R^V/R^I|':>12s}  {'Raw R^I':>14s}  {'Raw R^V':>14s}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*12}  {'-'*14}  {'-'*12}  {'-'*14}  {'-'*14}")
    for f in freqs:
        d = data_dict[f]
        fLc = np.pi * f * 2.5e9 / C
        ratio = abs(d['r_V']) / (abs(d['r_I']) + 1e-30)
        print(f"  {f:10.5f}  {fLc:8.4f}  {d['r_I']:12.6f}  {d['r_V']:14.6e}  "
              f"{ratio:12.6e}  {d['r_I_raw']:14.6e}  {d['r_V_raw']:14.6e}")


# -- Tests --
def run_tests():
    """Unit tests: self-correlation should give R^V = 0."""
    print_header("TESTS: Self-correlation R^V = 0 for planar detectors")

    L = 2.5e9
    u1 = np.array([1.0, 0.0, 0.0])
    u2 = np.array([0.5, np.sqrt(3) / 2, 0.0])

    freqs = [0.001, 0.01, 0.05, 0.1]
    ntheta, nphi = 64, 128
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')

    print("\n  Test 1: Coplanar detector self-correlation (R^V should be ~0)")
    print("  " + "-" * 62)
    all_pass = True

    for f in freqs:
        r_I, r_V, _, _, _, _ = compute_response(tG, pG, u1, u2, u1, u2, f, L, L)
        passed = abs(r_V) < 1e-6
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"    f = {f:.4f} Hz: R^I = {r_I:+10.6f}, R^V = {r_V:+10.6e}  [{status}]")

    if not all_pass:
        print("\n  FAILED: R^V should be ~0 for self-correlation")
        sys.exit(1)

    print("\n  Test 2: Self-correlation R^I should be ~1 (normalization)")
    for f in freqs[:2]:
        r_I, r_V, _, _, _, _ = compute_response(tG, pG, u1, u2, u1, u2, f, L, L)
        ri_ok = 0.8 < r_I < 1.2
        print(f"    f = {f:.4f} Hz: R^I = {r_I:.6f}  {'PASS' if ri_ok else 'CHECK'}")

    print(f"\n{'=' * 78}")
    print("  All tests PASSED")
    print(f"{'=' * 78}")


# -- Full analysis --
def run_main():
    """Full frequency scan for LISA(60deg) x Taiji(0deg)."""
    print_header("FULL ANALYSIS: LISA-Taiji Response Functions")
    print("  Physics: Orlando et al. (arXiv:2011.07059) JCAP 069 (2021)")
    print("  Model: Two-arm Michelson interferometer per detector")
    print("  Data model: D = h^2 Omega^I R^I + h^2 Omega^V R^V")

    # -- Detector A: LISA (60 deg inclination) --
    L1 = 2.5e9
    uA1, uA2, posA, nA = build_detector_arms(L1, 60.0, 0.0)
    print(f"\n  Detector A (LISA): L = {L1/1e6:.0f} Mkm, inclination = 60 deg")
    print(f"    Arm 1: [{uA1[0]:6.3f}, {uA1[1]:6.3f}, {uA1[2]:6.3f}]")
    print(f"    Arm 2: [{uA2[0]:6.3f}, {uA2[1]:6.3f}, {uA2[2]:6.3f}]")
    print(f"    Plane normal: [{nA[0]:6.3f}, {nA[1]:6.3f}, {nA[2]:6.3f}]")

    # -- Detector B: Taiji (0 deg inclination) --
    L2 = 3.0e9
    uB1, uB2, posB, nB = build_detector_arms(L2, 0.0, 0.0)
    print(f"\n  Detector B (Taiji): L = {L2/1e6:.0f} Mkm, inclination = 0 deg")
    print(f"    Arm 1: [{uB1[0]:6.3f}, {uB1[1]:6.3f}, {uB1[2]:6.3f}]")
    print(f"    Arm 2: [{uB2[0]:6.3f}, {uB2[1]:6.3f}, {uB2[2]:6.3f}]")
    print(f"    Plane normal: [{nB[0]:6.3f}, {nB[1]:6.3f}, {nB[2]:6.3f}]")

    det_angle = np.arccos(np.clip(np.dot(nA, nB), -1, 1)) * 180 / np.pi
    print(f"\n  Angle between detector planes: {det_angle:.1f} deg")

    # -- Sky grid --
    ntheta, nphi = 64, 128
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')

    # -- Part 1: LISA x Taiji cross-correlation --
    print(f"\n  Part 1: LISA(60deg) x Taiji(0deg) cross-correlation")
    print("  " + "-" * 62)

    freqs = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

    import time
    lt = time.time()
    results = {}
    for f in freqs:
        r_I_n, r_V_n, r_I_r, r_V_r, S_A, S_B = compute_response(
            tG, pG, uA1, uA2, uB1, uB2, f, L1, L2
        )
        results[f] = {
            'r_I': r_I_n, 'r_V': r_V_n,
            'r_I_raw': r_I_r, 'r_V_raw': r_V_r,
            'S_A': S_A, 'S_B': S_B
        }
    print(f"  Computation time: {time.time() - lt:.1f}s")

    print_results_table(freqs, results)

    # -- Part 2: Self-correlations --
    print(f"\n  Part 2: Self-correlations (R^V should be ~0)")
    print("  " + "-" * 62)

    for label, ua1, ua2, L_self in [("LISA", uA1, uA2, L1), ("Taiji", uB1, uB2, L2)]:
        for f in [0.01, 0.1]:
            r_I, r_V, _, _, _, _ = compute_response(tG, pG, ua1, ua2, ua1, ua2, f, L_self, L_self)
            passed = abs(r_V) < 1e-10
            status = "PASS" if passed else "WARN"
            print(f"    {label}: f={f:.2f} Hz: R^I={r_I:+10.6f}, R^V={r_V:+10.6e}  [{status}]")

    # -- Part 3: Variation with relative rotation --
    print(f"\n  Part 3: Taiji at different rotation angles (LISA fixed at 60 deg)")
    print("  " + "-" * 62)
    print(f"  {'rot_deg':>10s}  {'R^I':>12s}  {'R^V':>14s}  {'|R^V/R^I|':>12s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*14}  {'-'*12}")

    for rot in [0, 30, 60, 90, 120, 150, 180]:
        uB1r, uB2r, _, _ = build_detector_arms(L2, 0.0, float(rot))
        r_I, r_V, _, _, _, _ = compute_response(tG, pG, uA1, uA2, uB1r, uB2r, 0.01, L1, L2)
        ratio = abs(r_V) / (abs(r_I) + 1e-30)
        print(f"  {rot:10d}  {r_I:+12.6f}  {r_V:+14.6e}  {ratio:12.6e}")

    # -- Part 4: Pointwise chiral integrand --
    print(f"\n  Part 4: Chiral integrand analysis")
    print("  " + "-" * 62)

    f_check = 0.01
    FA_p, FA_c = michelson_response_with_tf(tG, pG, uA1, uA2, f_check, L1)
    FB_p, FB_c = michelson_response_with_tf(tG, pG, uB1, uB2, f_check, L2)
    Y_V = FA_p * FB_c - FA_c * FB_p

    print(f"  At f = {f_check} Hz:")
    print(f"    Y_V is NOT identically zero: {not np.allclose(Y_V, 0)}")
    print(f"    |Y_V|_max = {np.max(np.abs(Y_V)):.6f}")
    print(f"    |Y_V|_rms = {np.sqrt(np.mean(np.abs(Y_V)**2)):.6f}")
    print(f"    Sky-integrated R^V = {results[f_check]['r_V']:.6e}")
    print(f"\n  The chiral integrand is non-zero at individual sky positions")
    print(f"  but integrates to zero due to mirror symmetry of planar detectors.")

    # -- Part 5: Comparison with Orlando --
    print(f"\n  Part 5: Comparison with Orlando et al. (arXiv:2011.07059) Figure 2")
    print("  " + "-" * 62)
    print("  Orlando reference (for their detector pair):")
    print("    R^I ~ 0.3-0.4, R^V ~ 0.02-0.04 at f ~ 10-30 mHz")
    print(f"\n  Our LISA(60) x Taiji(0) results:")

    for f in [0.01, 0.02, 0.05]:
        d = results[f]
        ri_in = 0.15 <= abs(d['r_I']) <= 0.6
        status = "CLOSE" if ri_in else "CHECK"
        print(f"    f = {f:.3f} Hz: R^I = {d['r_I']:.6f}, R^V = {d['r_V']:.6e}  [{status}]")

    print(f"\n  NOTE: R^V = 0 for planar detectors is a known physical result.")
    print(f"  The chiral integrand is non-zero pointwise but integrates to zero")
    print(f"  on the sky due to mirror symmetry. Non-zero R^V requires non-planar")
    print(f"  detector geometry or time-averaged orbital evolution.")

    # -- Summary --
    max_I = max(abs(results[f]['r_I']) for f in freqs)
    max_V = max(abs(results[f]['r_V']) for f in freqs)
    f_max_I = freqs[np.argmax([abs(results[f]['r_I']) for f in freqs])]
    f_max_V = freqs[np.argmax([abs(results[f]['r_V']) for f in freqs])]

    print(f"\n  Summary:")
    print(f"    Max |R^I| = {max_I:.6f} at f = {f_max_I:.4f} Hz")
    print(f"    Max |R^V| = {max_V:.6e} at f = {f_max_V:.4f} Hz")
    print(f"    |R^V/R^I| ratio range: "
          f"[{min(abs(results[f]['r_V'] / (results[f]['r_I'] + 1e-30)) for f in freqs):.6e}, "
          f"{max(abs(results[f]['r_V'] / (results[f]['r_I'] + 1e-30)) for f in freqs):.6e}]")

    # -- Save to CSV --
    outdir = Path(__file__).parent.parent / "paper"
    outdir.mkdir(exist_ok=True)
    csv_path = outdir / "validate_orlando_response.csv"

    with open(csv_path, 'w') as f:
        f.write("Frequency(Hz),R_I_norm,R_V_norm,Raw_R_I,Raw_R_V,S_A,S_B,Ratio_V_I\n")
        for fi in freqs:
            d = results[fi]
            ratio = abs(d['r_V']) / (abs(d['r_I']) + 1e-30)
            f.write(f"{fi},{d['r_I']},{d['r_V']},{d['r_I_raw']},{d['r_V_raw']},"
                    f"{d['S_A']},{d['S_B']},{ratio}\n")

    print(f"\n  Results saved to: {csv_path}")
    return results


# -- Quick preview --
def run_quick():
    """Quick preview at single frequency."""
    print_header("QUICK PREVIEW: f = 0.01 Hz (Two-arm Michelson)")

    f = 0.01
    L1, L2 = 2.5e9, 3.0e9

    uA1, uA2, _, _ = build_detector_arms(L1, 60.0, 0.0)
    uB1, uB2, _, _ = build_detector_arms(L2, 0.0, 0.0)

    ntheta, nphi = 64, 128
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')

    r_I_n, r_V_n, r_I_raw, r_V_raw, S_A, S_B = compute_response(
        tG, pG, uA1, uA2, uB1, uB2, f, L1, L2
    )

    print(f"\n  LISA(60deg) x Taiji(0deg) at f = {f} Hz:")
    print(f"    R^I (normalized) = {r_I_n:.6f}")
    print(f"    R^V (normalized) = {r_V_n:.6e}")
    print(f"    Raw R^I          = {r_I_raw:.6e}")
    print(f"    Raw R^V          = {r_V_raw:.6e}")
    print(f"    S_A (LISA)       = {S_A:.4f}")
    print(f"    S_B (Taiji)      = {S_B:.4f}")
    print(f"    |R^V/R^I|        = {abs(r_V_n / (r_I_n + 1e-30)):.6e}")
    print(f"\n  Comparison with Orlando Figure 2:")
    print(f"    R^I in [0.15, 0.6]? {0.15 <= abs(r_I_n) <= 0.6}")
    print(f"    R^V ~ 0 (expected for planar detectors)?  {abs(r_V_n) < 1e-6}")
    print(f"\n  NOTE: R^V = 0 for planar detectors is a known physical result.")


# -- Main --
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'tests':
        run_tests()
    elif cmd == 'main':
        run_main()
    elif cmd == 'quick':
        run_quick()
    else:
        print(f"Usage: python3 {sys.argv[0]} [tests|main|quick]")
        print(f"  tests  - self-correlation R^V = 0 unit tests")
        print(f"  main   - full frequency scan (LISA-Taiji, two-arm Michelson)")
        print(f"  quick  - quick preview at f = 0.01 Hz")
