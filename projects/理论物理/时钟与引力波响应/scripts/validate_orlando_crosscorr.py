#!/usr/bin/env python3
"""
Validate Orlando's R^I / R^V response functions for LISA-Taiji cross-correlation.

Follows Orlando et al. arXiv:2011.07059 formalism:
  - Chiral polarization basis e^{R/L} (right/left circular polarization)
  - Chiral antenna patterns R^lambda_i for each Michelson channel
  - Cross-correlation response:
      R^I_mn = (1/4pi) int (R^R_mn + R^L_mn)/2 dOmega   (parity-even)
      R^V_mn = (1/4pi) int (R^R_mn - R^L_mn)/2 dOmega   (parity-odd)

Key physics:
  - Single planar detector: R^V_self = 0  (mirror symmetry about detector plane)
  - Two coplanar detectors:  R^V_cross = 0  (same mirror plane)
  - Two tilted detectors (different mirror planes): R^V_cross can be nonzero
    BUT: if both mirror planes share an axis of rotation, combined symmetries
    may still force R^V = 0.
"""

import numpy as np
import csv
import sys
import os

# ==============================================================================
# Configuration
# ==============================================================================

NTHETA = 128
NPHI = 256
FREQ_HZ = 0.0

# ==============================================================================
# Helper functions
# ==============================================================================

def rotation_matrix_x(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1,  0,  0], [0,  c, -s], [0,  s,  c]])

def rotation_matrix_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[ c, 0, s], [0, 1, 0], [-s, 0, c]])

def rotation_matrix_xy(tilt_x, tilt_y):
    return rotation_matrix_y(tilt_y) @ rotation_matrix_x(tilt_x)

def polarization_basis(khat):
    theta = np.arccos(np.clip(khat[2], -1.0, 1.0))
    phi = np.arctan2(khat[1], khat[0])
    u = np.array([np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), -np.sin(theta)])
    v = np.array([-np.sin(phi), np.cos(phi), 0.0])
    return u, v

def chiral_antenna_response(arm_unit, khat):
    u, v = polarization_basis(khat)
    au, av = np.dot(arm_unit, u), np.dot(arm_unit, v)
    GR = (au + 1j * av)**2 / 4.0
    GL = (au - 1j * av)**2 / 4.0
    return GR, GL

def michelson_chiral_response(arm1, arm2, khat):
    GR1, GL1 = chiral_antenna_response(arm1, khat)
    GR2, GL2 = chiral_antenna_response(arm2, khat)
    return GR1 - GR2, GL1 - GL2

def rotate_to_aet(RX, RY, RZ):
    A = (RZ - RX) / np.sqrt(2.0)
    E = (RX - 2.0*RY + RZ) / np.sqrt(6.0)
    T = (RX + RY + RZ) / np.sqrt(3.0)
    return np.array([A, E, T])

def sky_grid(Ntheta, Nphi):
    theta = np.linspace(0, np.pi, Ntheta)
    phi = np.linspace(0, 2*np.pi, Nphi, endpoint=False)
    th, ph = np.meshgrid(theta, phi, indexing='ij')
    x = np.sin(th)*np.cos(ph)
    y = np.sin(th)*np.sin(ph)
    z = np.cos(th)
    khat = np.stack([x.ravel(), y.ravel(), z.ravel()], axis=-1)
    return khat, th.ravel(), ph.ravel()

def sky_domega(Ntheta, Nphi):
    theta = np.linspace(0, np.pi, Ntheta)
    phi = np.linspace(0, 2*np.pi, Nphi, endpoint=False)
    dtheta = theta[1]-theta[0] if len(theta) > 1 else np.pi/Ntheta
    dphi = 2*np.pi/Nphi
    return np.sin(theta) * dtheta * dphi

def compute_chiral(detector_arms, khat_grid):
    N_ch = len(detector_arms)
    N_sky = len(khat_grid)
    R_L = np.zeros((N_ch, N_sky), dtype=complex)
    R_R = np.zeros((N_ch, N_sky), dtype=complex)
    for ch in range(N_ch):
        for s in range(N_sky):
            RR, RL = michelson_chiral_response(detector_arms[ch][0], detector_arms[ch][1], khat_grid[s])
            R_R[ch, s] = RR
            R_L[ch, s] = RL
    return R_L, R_R

# ==============================================================================
# Detector definitions
# ==============================================================================

def define_coplanar():
    L = 2.5e9
    arms = [
        (np.array([L, 0.0, 0.0]), np.array([L/2.0, L*np.sqrt(3)/2.0, 0.0])),
        (np.array([-L/2.0, L*np.sqrt(3)/2.0, 0.0]), np.array([0.0, 0.0, 0.0])),
        (np.array([-L/2.0, -L*np.sqrt(3)/2.0, 0.0]), np.array([L, 0.0, 0.0])),
    ]
    return arms

def define_tilted_x(tilt_deg):
    L = 2.5e9
    base = [
        (np.array([L, 0.0, 0.0]), np.array([L/2.0, L*np.sqrt(3)/2.0, 0.0])),
        (np.array([-L/2.0, L*np.sqrt(3)/2.0, 0.0]), np.array([0.0, 0.0, 0.0])),
        (np.array([-L/2.0, -L*np.sqrt(3)/2.0, 0.0]), np.array([L, 0.0, 0.0])),
    ]
    T = rotation_matrix_x(np.radians(tilt_deg))
    return [(T@a[0], T@a[1]) for a in base]

def define_tilted_y(tilt_deg):
    L = 2.5e9
    base = [
        (np.array([L, 0.0, 0.0]), np.array([L/2.0, L*np.sqrt(3)/2.0, 0.0])),
        (np.array([-L/2.0, L*np.sqrt(3)/2.0, 0.0]), np.array([0.0, 0.0, 0.0])),
        (np.array([-L/2.0, -L*np.sqrt(3)/2.0, 0.0]), np.array([L, 0.0, 0.0])),
    ]
    T = rotation_matrix_y(np.radians(tilt_deg))
    return [(T@a[0], T@a[1]) for a in base]

def define_tilted_taiji(tilt_x, tilt_y):
    """Taiji with different tilt around x and y axes from LISA."""
    L = 2.5e9
    base = [
        (np.array([L, 0.0, 0.0]), np.array([L/2.0, L*np.sqrt(3)/2.0, 0.0])),
        (np.array([-L/2.0, L*np.sqrt(3)/2.0, 0.0]), np.array([0.0, 0.0, 0.0])),
        (np.array([-L/2.0, -L*np.sqrt(3)/2.0, 0.0]), np.array([L, 0.0, 0.0])),
    ]
    T = rotation_matrix_xy(np.radians(tilt_x), np.radians(tilt_y))
    return [(T@a[0], T@a[1]) for a in base]

# ==============================================================================
# Diagnostic: chiral response at specific sky directions
# ==============================================================================

def diagnostic_chiral(arms_det1, arms_det2, labels, khat, verbose=True):
    """Print chiral responses for specific sky directions."""
    names = labels[0].split('\n')

    # Compute chiral responses at this sky direction
    RL1, RR1 = [], []
    RL2, RR2 = [], []
    for ch in range(3):
        rr, rl = michelson_chiral_response(arms_det1[ch][0], arms_det1[ch][1], khat)
        RL1.append(rl); RR1.append(rr)
        rr2, rl2 = michelson_chiral_response(arms_det2[ch][0], arms_det2[ch][1], khat)
        RL2.append(rl2); RR2.append(rr2)

    AET1_L = rotate_to_aet(RL1[0], RL1[1], RL1[2])
    AET1_R = rotate_to_aet(RR1[0], RR1[1], RR1[2])
    AET2_L = rotate_to_aet(RL2[0], RL2[1], RL2[2])
    AET2_R = rotate_to_aet(RR2[0], RR2[1], RR2[2])

    print(f"\n  --- Diagnostic at khat = ({khat[0]:.3f}, {khat[1]:.3f}, {khat[2]:.3f}) ---")
    print(f"  {labels[0]}")
    print(f"  {labels[1]}")
    print()

    for i, n1 in enumerate(['A','E','T']):
        for j, n2 in enumerate(['C','D','S']):
            rr_mn = AET1_R[i] * np.conj(AET2_R[j])
            rl_mn = AET1_L[i] * np.conj(AET2_L[j])
            rI = (rr_mn + rl_mn) / 2
            rV = (rr_mn - rl_mn) / 2
            print(f"  ({n1},{n2}): R^R = {rr_mn: .3e}, R^L = {rl_mn: .3e}, R^I = {rI: .3e}, R^V = {rV: .3e}")

    # Also compute mirror reflection of these directions
    # Mirror about tilted plane for detector 2
    tilt = np.arctan2(arms_det2[0][0][1], arms_det2[0][0][2]) if abs(arms_det2[0][0][2]) > 1e-15 else 0
    print(f"\n  Mirror-plane angle of detector 2: {np.degrees(tilt):.1f} deg")
    print(f"  Mirror-plane angle of detector 1: 0.0 deg (coplanar)")


# ==============================================================================
# Cross-correlation computation
# ==============================================================================

def compute_cross_response(RL1, RR1, RL2, RR2):
    """Compute sky-integrated R^I and R^V for all channel pairs."""
    N_ch1 = RL1.shape[0]
    N_ch2 = RL2.shape[0]
    domega = sky_domega(NTHETA, NPHI).reshape(-1, 1)
    norm = 4.0 * np.pi

    R_I = np.zeros((N_ch1, N_ch2), dtype=float)
    R_V = np.zeros((N_ch1, N_ch2), dtype=float)

    for m in range(N_ch1):
        for n in range(N_ch2):
            RR_mn = RR1[m, :] * np.conj(RR2[n, :])
            integral = np.sum(RR_mn * domega) / norm
            R_I[m, n] = np.real(integral)
            R_V[m, n] = np.imag(integral)

    return R_I, R_V

def run_test(name, arms1, arms2, l1, l2):
    print(f"\n{'='*70}")
    print(f"  TEST: {name}")
    print(f"{'='*70}")

    khat, thetas, phis = sky_grid(NTHETA, NPHI)
    N_sky = len(khat)
    print(f"  Sky grid: {NTHETA} x {NPHI} = {N_sky}")

    # Diagnostics at a few sky directions
    diag_dirs = [
        np.array([0.0, 0.0, 1.0]),   # z-direction
        np.array([1.0, 0.0, 0.0]),   # x-direction
        np.array([0.0, 1.0, 0.0]),   # y-direction
        np.array([1.0, 1.0, 0.0])/np.sqrt(2),
    ]

    for d in diag_dirs:
        diagnostic_chiral(arms1, arms2, [l1, l2], d)

    # Compute chiral responses
    print("\n  Computing R^L and R^R for all sky directions...")
    RL1, RR1 = compute_chiral(arms1, khat)
    RL2, RR2 = compute_chiral(arms2, khat)

    # AET rotation
    AET1_R = rotate_to_aet(RR1[0], RR1[1], RR1[2])
    AET1_L = rotate_to_aet(RL1[0], RL1[1], RL1[2])
    AET2_R = rotate_to_aet(RR2[0], RR2[1], RR2[2])
    AET2_L = rotate_to_aet(RL2[0], RL2[1], RL2[2])

    # Compute R^I and R^V
    R_I, R_V = compute_cross_response(AET1_L, AET1_R, AET2_L, AET2_R)

    print(f"\n  {l1.split(chr(10))[0]} \\ {l2.split(chr(10))[0]}   |   A       E       T    ")
    print(f"  {'-'*55}")
    for i, n1 in enumerate(['A','E','T']):
        row = f"  {n1}       |"
        for j, n2 in enumerate(['C','D','S']):
            row += f"  ({R_I[i,j]:8.4e}, {R_V[i,j]:8.4e}) "
        print(row)

    avg_I = np.mean(R_I)
    avg_V = np.mean(R_V)
    max_V = np.max(np.abs(R_V))

    print(f"\n  Average R^I: {avg_I:.4e}")
    print(f"  Average R^V: {avg_V:.4e}")
    print(f"  Max |R^V|:   {max_V:.4e}")
    if abs(avg_I) > 1e-20:
        print(f"  R^V / R^I:   {avg_V/avg_I:.4e}")

    return {'test_name': name, 'R_I': R_I, 'R_V': R_V, 'avg_I': avg_I, 'avg_V': avg_V, 'max_V': max_V}


# ==============================================================================
# Mirror symmetry diagnostic
# ==============================================================================

def mirror_symmetry_test(arms_det, labels):
    """Test mirror symmetry: check if R^R(k_mirror) = R^L(k) for specific directions."""
    khat, _, _ = sky_grid(NTHETA, NPHI)
    N_sky = len(khat)

    # Compute mirror reflection about the detector's plane
    # For the tilted detector, the mirror plane is defined by the normal n = R_x(alpha) * (0,0,1)
    arm_ref = arms_det[0][0] - arms_det[0][1]
    n = np.cross(arms_det[1][0] - arms_det[1][1], arms_det[2][0] - arms_det[2][1])
    n = n / np.linalg.norm(n)

    print(f"\n  Detector plane normal: ({n[0]:.4f}, {n[1]:.4f}, {n[2]:.4f})")

    # Check mirror symmetry for a few sky directions
    print(f"\n  Mirror symmetry test: R^R(k_mirror) vs R^L(k)")
    print(f"  Mirror reflection k -> k - 2(k.n)n")
    test_dirs = [
        np.array([0, 0, 1]),
        np.array([1, 0, 0]),
        np.array([0, 1, 0]),
        np.array([1, 1, 0])/np.sqrt(2),
        np.array([1, 0, 1])/np.sqrt(2),
        np.array([0, 1, 1])/np.sqrt(2),
    ]

    for k in test_dirs:
        # Mirror reflection
        km = k - 2*np.dot(k, n)*n
        km = km / np.linalg.norm(km)

        # R^R(k) and R^L(k)
        RL, RR = [], []
        for ch in range(3):
            rr, rl = michelson_chiral_response(arms_det[ch][0], arms_det[ch][1], k)
            RL.append(rl); RR.append(rr)
        AET_L = rotate_to_aet(RL[0], RL[1], RL[2])
        AET_R = rotate_to_aet(RR[0], RR[1], RR[2])

        # R^R(k_mirror)
        RLm, RRm = [], []
        for ch in range(3):
            rr, rl = michelson_chiral_response(arms_det[ch][0], arms_det[ch][1], km)
            RLm.append(rl); RRm.append(rr)
        AETm_L = rotate_to_aet(RLm[0], RLm[1], RLm[2])
        AETm_R = rotate_to_aet(RRm[0], RRm[1], RRm[2])

        print(f"\n  k = ({k[0]:.3f}, {k[1]:.3f}, {k[2]:.3f}), k_mirror = ({km[0]:.3f}, {km[1]:.3f}, {km[2]:.3f})")
        for i, n1 in enumerate(['A','E','T']):
            rr_mm = AETm_R[i]  # R^R at mirror direction
            rl_k = AET_L[i]    # R^L at original direction
            rr_k = AET_R[i]    # R^R at original direction
            diff_R = np.abs(rr_mm - rl_k)
            diff_RR = np.abs(rr_mm - rr_k)
            print(f"  {n1}: |R^R(k_mirror) - R^L(k)| = {diff_R:.2e}, |R^R(k_mirror) - R^R(k)| = {diff_RR:.2e}")


# ==============================================================================
# Main
# ==============================================================================

def main():
    print("="*70)
    print("  Orlando arXiv:2011.07059 R^I / R^V Validation")
    print("  LISA-Taiji Cross-Correlation Response Functions")
    print("="*70)

    results = []

    # Self-correlations
    arms_L = define_coplanar()
    results.append(run_test("LISA(A,E,T) self-correlation", arms_L, arms_L,
                            "LISA(A,E,T)\n(xy-plane)", "LISA(A,E,T)\n(xy-plane)"))
    arms_L_t = define_tilted_x(60)
    results.append(run_test("Tilted Taiji(C,D,S) self-correlation (60 deg)",
                            arms_L_t, arms_L_t,
                            "Taiji tilted 60 deg", "Taiji tilted 60 deg"))

    # Cross-correlations
    arms_T = define_coplanar()  # Taiji geometry same as LISA (for cross-corr test)
    arms_T_60 = define_tilted_x(60)

    results.append(run_test("Coplanar LISA(Taiji) x Coplanar Taiji(LISA)",
                            arms_L, arms_T,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\n(xy-plane)"))
    results.append(run_test("Coplanar LISA x Tilted Taiji (5 deg)",
                            arms_L, arms_T_60,  # will redefine below
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\ntilted 5 deg"))

    # Rerun with correct tilted Taiji
    arms_T_5 = define_tilted_x(5)
    results.append(run_test("Coplanar LISA x Tilted Taiji (5 deg)",
                            arms_L, arms_T_5,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\ntilted 5 deg"))
    arms_T_10 = define_tilted_x(10)
    results.append(run_test("Coplanar LISA x Tilted Taiji (10 deg)",
                            arms_L, arms_T_10,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\ntilted 10 deg"))
    arms_T_30 = define_tilted_x(30)
    results.append(run_test("Coplanar LISA x Tilted Taiji (30 deg)",
                            arms_L, arms_T_30,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\ntilted 30 deg"))
    results.append(run_test("Coplanar LISA x Tilted Taiji (60 deg)",
                            arms_L, arms_T_60,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\ntilted 60 deg"))

    # ===== Genuinely non-parallel mirror planes =====
    # Different rotation axes => no shared symmetry axis

    # Taiji tilted around y-axis (not x-axis)
    arms_T_y5  = define_tilted_y(5)
    arms_T_y10 = define_tilted_y(10)
    arms_T_y30 = define_tilted_y(30)
    arms_T_y60 = define_tilted_y(60)

    results.append(run_test("LISA(xy) × Taiji(y-tilt 5 deg)  [orthogonal axes]",
                            arms_L, arms_T_y5,
                            "LISA(A,E,T)\n(xy-plane, n=z)", "Taiji(C,D,S)\ny-tilted 5 deg, n~(0,-sin5,cos5)"))
    results.append(run_test("LISA(xy) × Taiji(y-tilt 10 deg)",
                            arms_L, arms_T_y10,
                            "LISA(A,E,T)\n(xy-plane, n=z)", "Taiji(C,D,S)\ny-tilted 10 deg"))
    results.append(run_test("LISA(xy) × Taiji(y-tilt 30 deg)",
                            arms_L, arms_T_y30,
                            "LISA(A,E,T)\n(xy-plane, n=z)", "Taiji(C,D,S)\ny-tilted 30 deg"))
    results.append(run_test("LISA(xy) × Taiji(y-tilt 60 deg)",
                            arms_L, arms_T_y60,
                            "LISA(A,E,T)\n(xy-plane, n=z)", "Taiji(C,D,S)\ny-tilted 60 deg"))

    # Taiji tilted by different angles around BOTH x and y axes
    arms_T_xy30x30 = define_tilted_taiji(30, 30)
    arms_T_xy60x30 = define_tilted_taiji(60, 30)
    arms_T_xy30x60 = define_tilted_taiji(30, 60)
    arms_T_xy60x60 = define_tilted_taiji(60, 60)

    results.append(run_test("LISA(xy) × Taiji(x-tilt30, y-tilt30)",
                            arms_L, arms_T_xy30x30,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\nx-tilt30 + y-tilt30"))
    results.append(run_test("LISA(xy) × Taiji(x-tilt60, y-tilt30)",
                            arms_L, arms_T_xy60x30,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\nx-tilt60 + y-tilt30"))
    results.append(run_test("LISA(xy) × Taiji(x-tilt30, y-tilt60)",
                            arms_L, arms_T_xy30x60,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\nx-tilt30 + y-tilt60"))
    results.append(run_test("LISA(xy) × Taiji(x-tilt60, y-tilt60)",
                            arms_L, arms_T_xy60x60,
                            "LISA(A,E,T)\n(xy-plane)", "Taiji(C,D,S)\nx-tilt60 + y-tilt60"))

    # Mirror plane normal vectors for reference
    print("\n\n" + "="*70)
    print("  MIRROR PLANE NORMAL VECTORS (reference)")
    print("="*70)
    for name, arms in [("LISA coplanar", arms_L),
                       ("Taiji x-tilt 60", arms_T_60),
                       ("Taiji y-tilt 60", arms_T_y60),
                       ("Taiji x30y30", arms_T_xy30x30),
                       ("Taiji x60y30", arms_T_xy60x30)]:
        n = np.cross(arms[1][0]-arms[1][1], arms[2][0]-arms[2][1])
        n = n / np.linalg.norm(n)
        print(f"  {name}: normal = ({n[0]:.6f}, {n[1]:.6f}, {n[2]:.6f})")

    # Mirror symmetry tests
    print("\n\n" + "="*70)
    print("  MIRROR SYMMETRY DIAGNOSTICS")
    print("="*70)
    mirror_symmetry_test(arms_L, ["LISA coplanar"])
    mirror_symmetry_test(arms_T_60, ["Taiji 60 deg"])

    # Summary
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Test':60s}  {'<R^I>':>15s}  {'<R^V>':>15s}  R^V/<R^I>:")

    for r in results:
        test_short = r['test_name'][:50]
        ratio = r['avg_V']/r['avg_I'] if abs(r['avg_I']) > 1e-20 else 0
        print(f"  {test_short:50s}  {r['avg_I']:15.3e}  {r['avg_V']:15.3e}  {ratio:.2e}")

    # CSV output
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "validate_orlando_crosscorr_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Test', 'Avg_R_I', 'Avg_R_V', 'Max_R_V',
                         'R_I_A_C','R_V_A_C','R_I_A_D','R_V_A_D','R_I_A_S','R_V_A_S',
                         'R_I_E_C','R_V_E_C','R_I_E_D','R_V_E_D','R_I_E_S','R_V_E_S',
                         'R_I_T_C','R_V_T_C','R_I_T_D','R_V_T_D','R_I_T_S','R_V_T_S'])
        for r in results:
            row = [r['test_name'], r['avg_I'], r['avg_V'], r['max_V']]
            for i in range(3):
                for j in range(3):
                    row.extend([r['R_I'][i,j], r['R_V'][i,j]])
            writer.writerow(row)

    print(f"\n  Results saved to: {csv_path}")

    # Key conclusions
    print("\n" + "="*70)
    print("  KEY CONCLUSIONS")
    print("="*70)

    # Check coplanar self-correlation
    print(f"\n  1. Self-correlation R^V check:")
    for r in results[:2]:
        if 'self' in r['test_name'].lower() or 'self' in r['test_name'].lower():
            rrat = abs(r['avg_V']/r['avg_I']) if abs(r['avg_I']) > 1e-20 else 0
            status = "PASS (R^V ~ 0)" if rrat < 1e-10 else "FAIL"
            print(f"     {r['test_name'][:50]}: R^V/<R^I> = {rrat:.2e}  {status}")

    # Check tilted cross-correlation (same axis)
    print(f"\n  2. Same-axis tilt (all around x): R^V vs tilt angle:")
    same_axis = [r for r in results if 'x-tilt' not in r['test_name'] and 'y-tilt' not in r['test_name']
                 and 'x-tilt' not in r['test_name'] and 'tilted' in r['test_name'].lower()
                 and 'orthogonal' not in r['test_name']]
    for r in same_axis:
        rrat = abs(r['avg_V']/r['avg_I']) if abs(r['avg_I']) > 1e-20 else 0
        print(f"     {r['test_name'][:55]}: R^V/<R^I> = {rrat:.2e}")

    # Check tilted cross-correlation (different axis)
    print(f"\n  3. Different-axis tilt (orthogonal planes): R^V vs tilt:")
    diff_axis = [r for r in results if 'y-tilt' in r['test_name'] or 'orthogonal' in r['test_name']]
    for r in diff_axis:
        rrat = abs(r['avg_V']/r['avg_I']) if abs(r['avg_I']) > 1e-20 else 0
        print(f"     {r['test_name'][:55]}: R^V/<R^I> = {rrat:.2e}")

    # Check tilted cross-correlation (both x and y)
    print(f"\n  4. Dual-axis tilt (different mirror planes): R^V vs config:")
    dual_axis = [r for r in results if 'x-tilt' in r['test_name'] and 'y-tilt' in r['test_name']]
    for r in dual_axis:
        rrat = abs(r['avg_V']/r['avg_I']) if abs(r['avg_I']) > 1e-20 else 0
        print(f"     {r['test_name'][:55]}: R^V/<R^I> = {rrat:.2e}")

    print("\n  3. Mirror symmetry of R^R:")
    print("     - If R^R(k_mirror) = R^L(k) for all k, then R^V = 0")
    print("     - If R^R(k_mirror) = R^R(k) for all k, then R^R is even under mirror")
    print("     - The combination of both gives R^R = R^L pointwise => R^V = 0")


if __name__ == "__main__":
    main()
