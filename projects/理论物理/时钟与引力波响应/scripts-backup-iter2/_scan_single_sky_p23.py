#!/usr/bin/env python3
"""
P2-3: Fine-grained single-sky-direction search for R^V = -7.750753e-3.

Uses the same OLC TF + spatial phase setup as _debug_v17_hypotheses.py.
Searches theta in [10°, 50°] and phi in [80°, 100°] with fine resolution.

Target: R^V = -7.750753e-3 (v17 claimed value, LISA30 x Taiji0, with SP)
"""
import numpy as np
import sys
import os

c = 299792458.0

# ============================================================
# Transfer functions
# ============================================================

def olc_transfer_function(f, L, cos_nu):
    """Full OLC transfer function."""
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase


def michelson_transfer_function(f, L, cos_nu):
    """Michelson transfer function (sky-independent)."""
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase


# ============================================================
# Antenna patterns
# ============================================================

def antenna_cw_sum(tG, pG, positions, L, tf_fn):
    """CW-sum antenna pattern with flexible transfer function."""
    nx = np.sin(tG) * np.cos(pG)
    ny = np.sin(tG) * np.sin(pG)
    nz = np.cos(tG)

    th = np.array([np.cos(tG)*np.cos(pG),
                   np.cos(tG)*np.sin(pG),
                   -np.sin(tG)])
    ph = np.array([-np.sin(pG), np.cos(pG), np.zeros_like(pG)])

    cw_links = [(0, 1), (1, 2), (2, 0)]
    R_plus = np.zeros_like(tG, dtype=np.complex128)
    R_cross = np.zeros_like(tG, dtype=np.complex128)

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]

        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(np.ones_like(tG), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross


# ============================================================
# Constellation builder
# ============================================================

def build_constellation(L, inclination_rad):
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    positions = np.array([r1, r2, r3])

    cos_i = np.cos(inclination_rad)
    sin_i = np.sin(inclination_rad)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    return rotated


def spatial_phase_single(f, delta_x, theta, phi):
    """Single-direction spatial phase."""
    k_hat = np.array([np.sin(theta)*np.cos(phi),
                      np.sin(theta)*np.sin(phi),
                      np.cos(theta)])
    k_dot_delta = np.sum(k_hat * delta_x)
    omega = 2.0 * np.pi * f
    return np.exp(-1j * omega / c * k_dot_delta)


# ============================================================
# ORF computation (single direction)
# ============================================================

def compute_orf_single(R1p, R1x, R2p, R2x, chi):
    """
    Single-sky-direction chiral ORF.
    R1p, R1x, R2p, R2x: complex antenna responses for that single direction.
    chi: spatial phase factor (complex scalar).
    Returns (gamma_I, gamma_V, S_A, S_B, R^V).
    """
    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    # For single direction, weight by cos(theta)*sin(theta) (sky measure)
    # but since we have just one point, we evaluate the integrand directly
    gamma_I = chi_real * cross_corr
    gamma_V = chi_real * chiral_corr

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv


def compute_orf_single_raw(R1p, R1x, R2p, R2x, chi):
    """
    Single-sky-direction chiral ORF (raw, no sky weighting).
    The key: R^V = Gamma^V / sqrt(S_A * S_B) is per-direction.
    We report the per-direction R^V value.

    chi is the complex spatial phase factor.
    """
    # The chiral correlation includes the spatial phase
    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    # Apply spatial phase to chiral term
    chi_real = np.real(chi)
    chi_imag = np.imag(chi)

    # The spatial phase affects the chiral correlation
    # Gamma^V = <chi * chiral_corr> over sky
    # For single direction: Gamma^V = Re[chi] * chiral_corr + Im[chi] * something
    # Actually, Gamma^V = Re[chi * (chiral_corr)] if chiral_corr is complex
    # But chiral_corr is real. So Gamma^V = Re[chi] * chiral_corr

    gamma_I = chi_real * cross_corr
    gamma_V = chi_real * chiral_corr

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv


def compute_orf_single_full(R1p, R1x, R2p, R2x, chi):
    """
    Full single-sky-direction chiral ORF.
    Uses proper chiral correlation: Gamma^V = Re[chi * (conj(R1p)*R2x - conj(R1x)*R2p)]

    This is the per-direction contribution to the sky-averaged Gamma^V.
    """
    # Complex chiral correlation (before taking real part)
    raw_chiral = np.conj(R1p)*R2x - np.conj(R1x)*R2p
    raw_cross = np.conj(R1p)*R2p + np.conj(R1x)*R2x

    # Apply spatial phase
    gamma_I = np.real(chi * raw_cross)
    gamma_V = np.real(chi * raw_chiral)

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv


# ============================================================
# Search
# ============================================================

TARGET_RV = -7.750753e-3
TARGET_GAMMA_V = -7.750753e-3  # v17 claims Gamma^V = -7.750753e-3

def scan_coarse():
    """Coarse scan over theta and phi to find the region with R^V ≈ target."""
    f = 0.001  # Hz

    L_lisa = 2.5e9
    L_taiji = 3.0e9

    incl1 = np.radians(30.0)
    incl2 = np.radians(0.0)

    pos1 = build_constellation(L_lisa, incl1)
    pos2 = build_constellation(L_taiji, incl2)

    # 1 AU separation
    delta_x = np.array([1.496e11, 0.0, 0.0])  # ~1 AU in x direction

    results = []

    print("=" * 80)
    print("COARSE SINGLE-SKY SCAN: theta=[10°, 50°], phi=[80°, 100°]")
    print("=" * 80)
    print(f"  Target R^V = {TARGET_RV:.6e}")
    print(f"  f = {f} Hz, LISA30 x Taiji0, OLC TF + SP")
    print(f"  {'theta(deg)':<12s} {'phi(deg)':<10s} {'R^V':<20s} {'|R^V - target|':<20s} {'dist':<15s}")
    print("  " + "-" * 80)

    for theta_deg in np.linspace(10, 50, 81):
        for phi_deg in np.linspace(80, 100, 41):
            theta = np.radians(theta_deg)
            phi = np.radians(phi_deg)

            # Single sky direction
            T = np.array([[theta]])
            P = np.array([[phi]])

            # Antenna responses
            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2 + delta_x, L_taiji, olc_transfer_function)

            # Spatial phase
            chi = spatial_phase_single(f, delta_x, theta, phi)

            # Compute ORF
            gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)

            dist = abs(rv - TARGET_RV)
            results.append((theta_deg, phi_deg, rv, dist))

            if dist < 1e-6:
                print(f"  {theta_deg:<12.1f} {phi_deg:<10.1f} {rv:<20.6e} {dist:<20.6e} *** CLOSE ***")

    results.sort(key=lambda x: x[3])

    print("\nTop 10 closest matches:")
    for i, (td, pd, rv, dist) in enumerate(results[:10]):
        print(f"  #{i+1}: theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}")

    return results


def scan_fine(theta_min, theta_max, phi_min, phi_max, ntheta, nphi):
    """Fine scan around the best region found in coarse scan."""
    f = 0.001

    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2 = build_constellation(L_taiji, np.radians(0.0))

    delta_x = np.array([1.496e11, 0.0, 0.0])

    print(f"\n{'=' * 80}")
    print(f"FINE SCAN: theta=[{theta_min:.1f}°, {theta_max:.1f}°], phi=[{phi_min:.1f}°, {phi_max:.1f}°]")
    print(f"{'=' * 80}")

    thetas = np.linspace(theta_min, theta_max, ntheta)
    phis = np.linspace(phi_min, phi_max, nphi)

    best_dist = 1e30
    best = None

    for td in thetas:
        theta = np.radians(td)
        for pd in phis:
            phi = np.radians(pd)

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2 + delta_x, L_taiji, olc_transfer_function)

            chi = spatial_phase_single(f, delta_x, theta, phi)
            gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)

            dist = abs(rv - TARGET_RV)
            if dist < best_dist:
                best_dist = dist
                best = (td, pd, rv, dist, chi, gV, SA, SB)

    if best:
        td, pd, rv, dist, chi, gV, SA, SB = best
        print(f"  Best match: theta={td:.4f}°, phi={pd:.4f}°")
        print(f"  R^V = {rv:.10e}")
        print(f"  target = {TARGET_RV:.10e}")
        print(f"  |delta| = {dist:.10e}")
        print(f"  Gamma^V = {gV:.10e}")
        print(f"  S_A = {SA:.10e}")
        print(f"  S_B = {SB:.10e}")
        print(f"  chi_real = {np.real(chi):.8f}, chi_imag = {np.imag(chi):.8f}")
        return best
    return None


def scan_fine_highres():
    """Very high resolution scan around the best fine-scan result."""
    f = 0.001

    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2 = build_constellation(L_taiji, np.radians(0.0))

    delta_x = np.array([1.496e11, 0.0, 0.0])

    # Scan around the expected region with 0.01° steps
    thetas = np.arange(27.5, 28.5, 0.01)
    phis = np.arange(88.5, 91.5, 0.01)

    print(f"\n{'=' * 80}")
    print(f"HIGH-RES SCAN: theta=[27.5°, 28.5°] (step 0.01°), phi=[88.5°, 91.5°] (step 0.01°)")
    print(f"{'=' * 80}")

    best_dist = 1e30
    best = None
    count = 0

    for td in thetas:
        theta = np.radians(td)
        for pd in phis:
            phi = np.radians(pd)
            count += 1

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2 + delta_x, L_taiji, olc_transfer_function)

            chi = spatial_phase_single(f, delta_x, theta, phi)
            gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)

            dist = abs(rv - TARGET_RV)
            if dist < best_dist:
                best_dist = dist
                best = (td, pd, rv, dist, chi, gV, SA, SB)

    print(f"  Evaluated {count} points")
    if best:
        td, pd, rv, dist, chi, gV, SA, SB = best
        print(f"  Best match: theta={td:.4f}°, phi={pd:.4f}°")
        print(f"  R^V = {rv:.10e}")
        print(f"  target = {TARGET_RV:.10e}")
        print(f"  |delta| = {dist:.10e}")
        print(f"  Gamma^V = {gV:.10e}")
        print(f"  chi_real = {np.real(chi):.10f}, chi_imag = {np.imag(chi):.10f}")
    return best


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("P2-3: Precise single-sky matching for v17 R^V = -7.750753e-3")
    print()

    # Step 1: Coarse scan
    coarse_results = scan_coarse()

    # Step 2: Fine scan around the best coarse result
    if coarse_results:
        best_td, best_pd, _, _ = coarse_results[0]
        # ±2° around best coarse result
        theta_min = max(0, best_td - 2.0)
        theta_max = min(180, best_td + 2.0)
        phi_min = max(0, best_pd - 2.0)
        phi_max = min(360, best_pd + 2.0)
        fine_result = scan_fine(theta_min, theta_max, phi_min, phi_max, 401, 401)
    else:
        fine_result = None
        print("\nNo good match in coarse scan, trying default region")
        fine_result = scan_fine(26.0, 30.0, 88.0, 91.0, 401, 301)

    # Step 3: High-res scan
    if fine_result:
        td, pd, rv, dist, _, _, _, _ = fine_result
        if dist > 1e-10:
            print("\nNote: fine scan didn't match to machine precision.")
            print("      This suggests the target may not be reachable with current setup.")
            print("      Checking if different f or different delta_x direction helps...")
    else:
        print("\nNo result from fine scan")

    # Step 4: Test without spatial phase (should be ~0)
    print(f"\n{'=' * 80}")
    print("CONTROL: Without spatial phase (should be ~0)")
    print(f"{'=' * 80}")
    f = 0.001
    pos1 = build_constellation(2.5e9, np.radians(30.0))
    pos2 = build_constellation(3.0e9, np.radians(0.0))

    theta = np.radians(28.0)
    phi = np.radians(89.0)
    T = np.array([[theta]])
    P = np.array([[phi]])

    R1p, R1x = antenna_cw_sum(T, P, pos1, 2.5e9, olc_transfer_function)
    R2p, R2x = antenna_cw_sum(T, P, pos2, 3.0e9, olc_transfer_function)

    chi = 1.0  # no spatial phase
    gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)
    print(f"  R^V (no SP) at theta=28°, phi=89°: {rv:.10e}")

    print(f"\n{'=' * 80}")
    print("Test 5: Without spatial phase (pure OLC, sky-averaged)")
    print(f"{'=' * 80}")
    f = 0.001
    pos1 = build_constellation(2.5e9, np.radians(30.0))
    pos2 = build_constellation(3.0e9, np.radians(0.0))
    TG = np.linspace(0, np.pi, 128, endpoint=False)
    PG = np.linspace(0, 2*np.pi, 256, endpoint=False)
    _TG, _PG = np.meshgrid(TG, PG, indexing='ij')
    R1p, R1x = antenna_cw_sum(_TG, _PG, pos1, 2.5e9, olc_transfer_function)
    R2p, R2x = antenna_cw_sum(_TG, _PG, pos2, 3.0e9, olc_transfer_function)

    # Manual sky average
    dtheta = np.pi / 128
    dphi = 2.0 * np.pi / 256
    sin_theta = np.sin(_TG)
    dOmega = sin_theta * dtheta * dphi

    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    gamma_I = np.sum(cross_corr * dOmega) / (4.0 * np.pi)
    gamma_V = np.sum(chiral_corr * dOmega) / (4.0 * np.pi)

    S_A = np.sum(np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x) * dOmega) / (4.0 * np.pi)
    S_B = np.sum(np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x) * dOmega) / (4.0 * np.pi)

    rv_sky = gamma_V / np.sqrt(S_A * S_B)
    print(f"  Sky-averaged R^V (no SP): {rv_sky:.10e}")

    print(f"\n{'=' * 80}")
    print("Test 6: With spatial phase (sky-averaged)")
    print(f"{'=' * 80}")
    delta_x = np.array([1.496e11, 0.0, 0.0])
    pos2_sp = pos2 + delta_x
    omega = 2.0 * np.pi * f
    k_hat = np.array([[np.sin(_TG)*np.cos(_PG),
                       np.sin(_TG)*np.sin(_PG),
                       np.cos(_TG)]]).T  # (Ntheta*Nphi, 3)
    k_dot_delta = k_hat[:, 0]*delta_x[0] + k_hat[:, 1]*delta_x[1] + k_hat[:, 2]*delta_x[2]
    k_dot_delta = k_dot_delta.reshape(_TG.shape)
    chi_sky = np.exp(-1j * omega / c * k_dot_delta)

    chiral_corr_sp = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)
    gamma_V_sp = np.sum(chi_sky * chiral_corr_sp * dOmega) / (4.0 * np.pi)
    rv_sky_sp = gamma_V_sp / np.sqrt(S_A * S_B)

    print(f"  Sky-averaged R^V (with SP): {rv_sky_sp:.10e}")
    print(f"  Gamma^V (with SP): {gamma_V_sp:.10e}")

    print(f"\n{'=' * 80}")
    print("Test 7: Testing different SP directions")
    print(f"{'=' * 80}")
    # Try delta_x in different directions
    for dx_name, dx_val in [
        ("x-dir", np.array([1.496e11, 0.0, 0.0])),
        ("y-dir", np.array([0.0, 1.496e11, 0.0])),
        ("z-dir", np.array([0.0, 0.0, 1.496e11])),
        ("radial", np.array([1.496e11/np.sqrt(3), 1.496e11/np.sqrt(3), 1.496e11/np.sqrt(3)])),
    ]:
        pos2_d = pos2 + dx_val
        R2p_d, R2x_d = antenna_cw_sum(_TG, _PG, pos2_d, 3.0e9, olc_transfer_function)
        S_B_d = np.sum(np.real(np.conj(R2p_d)*R2p_d + np.conj(R2x_d)*R2x_d) * dOmega) / (4.0 * np.pi)
        chi_d = np.exp(-1j * omega / c * k_dot_delta.reshape(_TG.shape))
        gamma_V_d = np.sum(chi_d * np.real(np.conj(R1p)*R2x_d - np.conj(R1x)*R2p_d) * dOmega) / (4.0 * np.pi)
        rv_d = gamma_V_d / np.sqrt(S_A * S_B_d)
        print(f"  delta_x = {dx_name}: R^V (sky-avg) = {rv_d:.10e}")
