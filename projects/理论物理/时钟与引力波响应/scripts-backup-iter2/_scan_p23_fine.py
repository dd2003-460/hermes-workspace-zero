#!/usr/bin/env python3
"""
P2-3: High-res single-sky scan to pinpoint the (theta, phi) matching R^V = -7.750753e-3.

Refines the coarse search result: theta≈14.31°, phi≈83.76°.
Also computes sky-averaged R^V for comparison.
"""
import numpy as np
import sys

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


# ============================================================
# ORF computation (single direction)
# ============================================================

def compute_orf_single_full(R1p, R1x, R2p, R2x, chi):
    """
    Full single-sky-direction chiral ORF.
    Gamma^V = Re[chi * (conj(R1p)*R2x - conj(R1x)*R2p)]
    Gamma^I = Re[chi * (conj(R1p)*R2p + conj(R1x)*R2x)]
    """
    raw_chiral = np.conj(R1p)*R2x - np.conj(R1x)*R2p
    raw_cross = np.conj(R1p)*R2p + np.conj(R1x)*R2x

    gamma_I = np.real(chi * raw_cross)
    gamma_V = np.real(chi * raw_chiral)

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv


def spatial_phase_single(f, delta_x, theta, phi):
    """Single-direction spatial phase."""
    k_hat = np.array([np.sin(theta)*np.cos(phi),
                      np.sin(theta)*np.sin(phi),
                      np.cos(theta)])
    k_dot_delta = np.sum(k_hat * delta_x)
    omega = 2.0 * np.pi * f
    return np.exp(-1j * omega / c * k_dot_delta)


# ============================================================
# Fine high-res search around theta=14.31, phi=83.76
# ============================================================

TARGET_RV = -7.750753e-3

def fine_search():
    f = 0.001  # Hz
    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2 = build_constellation(L_taiji, np.radians(0.0))

    delta_x = np.array([1.496e11, 0.0, 0.0])

    # Refine: theta in [14.0°, 14.6°], phi in [83.5°, 84.0°] with 0.01° steps
    thetas = np.arange(14.0, 14.6, 0.01)
    phis = np.arange(83.5, 84.0, 0.01)

    print("=" * 90)
    print("FINE SEARCH: theta=[14.0°, 14.6°] (step 0.01°), phi=[83.5°, 84.0°] (step 0.01°)")
    print(f"Target R^V = {TARGET_RV:.10e}")
    print("=" * 90)

    best_dist = 1e30
    best = None
    nclose = 0
    ntotal = 0

    for td in thetas:
        theta = np.radians(td)
        for pd in phis:
            phi = np.radians(pd)
            ntotal += 1

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
            if dist < 1e-8:
                nclose += 1

    print(f"\n  Evaluated {ntotal} points")
    if best:
        td, pd, rv, dist, chi, gV, SA, SB = best
        print(f"  Best match: theta = {td:.4f}°, phi = {pd:.4f}°")
        print(f"  R^V = {rv:.10e}")
        print(f"  Target = {TARGET_RV:.10e}")
        print(f"  |delta| = {dist:.10e}")
        print(f"  Gamma^V = {gV:.10e}")
        print(f"  S_A = {SA:.10e}")
        print(f"  S_B = {SB:.10e}")
        print(f"  chi_real = {np.real(chi):.12f}, chi_imag = {np.imag(chi):.12f}")
        print(f"  |chi| = {np.abs(chi):.12f}")
    return best


# ============================================================
# Frequency sweep at the best (theta, phi)
# ============================================================

def freq_sweep():
    best_td, best_pd = 14.31, 83.76  # Use the coarse result as starting point
    theta = np.radians(best_td)
    phi = np.radians(best_pd)

    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2 = build_constellation(L_taiji, np.radians(0.0))
    delta_x = np.array([1.496e11, 0.0, 0.0])

    print(f"\n{'=' * 90}")
    print(f"FREQUENCY SWEEP at theta={best_td}°, phi={best_pd}°")
    print(f"{'=' * 90}")
    print(f"  {'f (Hz)':<12s} {'R^V':<22s} {'|R^V - target|':<20s}")
    print(f"  " + "-" * 60)

    for f in [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]:
        T = np.array([[theta]])
        P = np.array([[phi]])

        R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = antenna_cw_sum(T, P, pos2 + delta_x, L_taiji, olc_transfer_function)

        chi = spatial_phase_single(f, delta_x, theta, phi)
        gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)

        dist = abs(rv - TARGET_RV)
        print(f"  {f:<12.4f} {rv:<22.6e} {dist:<20.6e}")


# ============================================================
# Sky-averaged R^V
# ============================================================

def sky_average():
    """Compute sky-averaged R^V with OLC TF and spatial phase."""
    f = 0.001
    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2_base = build_constellation(L_taiji, np.radians(0.0))

    delta_x = np.array([1.496e11, 0.0, 0.0])
    pos2 = pos2_base + delta_x

    TG = np.linspace(0, np.pi, 256, endpoint=False)
    PG = np.linspace(0, 2*np.pi, 512, endpoint=False)
    _TG, _PG = np.meshgrid(TG, PG, indexing='ij')

    R1p, R1x = antenna_cw_sum(_TG, _PG, pos1, L_lisa, olc_transfer_function)
    R2p, R2x = antenna_cw_sum(_TG, _PG, pos2, L_taiji, olc_transfer_function)

    dtheta = np.pi / 256
    dphi = 2.0 * np.pi / 512
    sin_theta = np.sin(_TG)
    dOmega = sin_theta * dtheta * dphi
    inv4pi = 1.0 / (4.0 * np.pi)

    omega = 2.0 * np.pi * f
    k_hat_vals = np.stack([
        np.sin(_TG)*np.cos(_PG),
        np.sin(_TG)*np.sin(_PG),
        np.cos(_TG)
    ], axis=-1)  # (Ntheta, Nphi, 3)
    k_dot_delta = k_hat_vals[..., 0]*delta_x[0] + k_hat_vals[..., 1]*delta_x[1] + k_hat_vals[..., 2]*delta_x[2]
    chi_sky = np.exp(-1j * omega / c * k_dot_delta)

    raw_cross = np.conj(R1p)*R2p + np.conj(R1x)*R2x
    raw_chiral = np.conj(R1p)*R2x - np.conj(R1x)*R2p

    gamma_I = np.sum(np.real(chi_sky * raw_cross) * dOmega) * inv4pi
    gamma_V = np.sum(np.real(chi_sky * raw_chiral) * dOmega) * inv4pi

    S_A = np.sum(np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x) * dOmega) * inv4pi
    S_B = np.sum(np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x) * dOmega) * inv4pi

    rv_sky = gamma_V / np.sqrt(S_A * S_B)

    print(f"\n{'=' * 90}")
    print("SKY-AVERAGED R^V (OLC TF + Spatial Phase)")
    print(f"{'=' * 90}")
    print(f"  Gamma^I = {gamma_I:.10e}")
    print(f"  Gamma^V = {gamma_V:.10e}")
    print(f"  S_A = {S_A:.10e}")
    print(f"  S_B = {S_B:.10e}")
    print(f"  R^V (sky-avg) = {rv_sky:.10e}")
    print(f"  R^V / Target = {rv_sky / TARGET_RV:.6f}")
    print(f"\n  Note: sky-avg ({rv_sky:.2e}) differs from v17 ({TARGET_RV:.2e})")
    print(f"        by factor {rv_sky/TARGET_RV:.3f}, confirming v17 is NOT sky-averaged.")

    # Also compute without SP
    print(f"\n{'=' * 90}")
    print("SKY-AVERAGED R^V (OLC TF only, no spatial phase)")
    print(f"{'=' * 90}")
    pos2_no_sp = pos2_base  # no spatial offset
    R2p_n, R2x_n = antenna_cw_sum(_TG, _PG, pos2_no_sp, L_taiji, olc_transfer_function)
    gamma_I_n = np.sum(np.real(np.conj(R1p)*R2p_n + np.conj(R1x)*R2x_n) * dOmega) * inv4pi
    gamma_V_n = np.sum(np.real(np.conj(R1p)*R2x_n - np.conj(R1x)*R2p_n) * dOmega) * inv4pi
    S_B_n = np.sum(np.real(np.conj(R2p_n)*R2p_n + np.conj(R2x_n)*R2x_n) * dOmega) * inv4pi
    rv_sky_n = gamma_V_n / np.sqrt(S_A * S_B_n)
    print(f"  Gamma^V = {gamma_V_n:.10e}")
    print(f"  R^V (no SP) = {rv_sky_n:.10e}")
    print(f"  Confirms: no SP → near-zero (mirror symmetry preserved)")


# ============================================================
# Test different delta_x directions
# ============================================================

def delta_x_directions():
    f = 0.001
    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, np.radians(30.0))
    pos2_base = build_constellation(L_taiji, np.radians(0.0))

    theta = np.radians(14.31)
    phi = np.radians(83.76)
    T = np.array([[theta]])
    P = np.array([[phi]])

    R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)

    print(f"\n{'=' * 90}")
    print(f"R^V vs delta_x direction (single sky at theta=14.31°, phi=83.76°)")
    print(f"{'=' * 90}")
    print(f"  {'delta_x direction':<20s} {'R^V':<22s} {'|delta|':<20s}")
    print(f"  " + "-" * 65)

    dx_list = [
        ("+x", np.array([1.496e11, 0.0, 0.0])),
        ("-x", np.array([-1.496e11, 0.0, 0.0])),
        ("+y", np.array([0.0, 1.496e11, 0.0])),
        ("-y", np.array([0.0, -1.496e11, 0.0])),
        ("+z", np.array([0.0, 0.0, 1.496e11])),
        ("radial", np.array([1.496e11, 1.496e11, 1.496e11])/np.sqrt(3)),
    ]

    for dx_name, delta_x in dx_list:
        pos2 = pos2_base + delta_x
        R2p, R2x = antenna_cw_sum(T, P, pos2, L_taiji, olc_transfer_function)
        chi = spatial_phase_single(f, delta_x, theta, phi)
        gI, gV, SA, SB, rv = compute_orf_single_full(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi)
        dist = abs(rv - TARGET_RV)
        print(f"  {dx_name:<20} {rv:<22.6e} {dist:<20.6e}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    best = fine_search()
    freq_sweep()
    sky_average()
    delta_x_directions()

    # Write results to file
    if best:
        td, pd, rv, dist, chi, gV, SA, SB = best
        with open("loop/2-loop/p23-best-match.txt", "w") as f:
            f.write(f"P2-3 Best Single-Sky Match\n")
            f.write(f"========================\n")
            f.write(f"theta = {td:.4f}°\n")
            f.write(f"phi = {pd:.4f}°\n")
            f.write(f"R^V = {rv:.10e}\n")
            f.write(f"Target = {TARGET_RV:.10e}\n")
            f.write(f"|delta| = {dist:.10e}\n")
            f.write(f"Gamma^V = {gV:.10e}\n")
            f.write(f"S_A = {SA:.10e}\n")
            f.write(f"S_B = {SB:.10e}\n")
            f.write(f"chi_real = {np.real(chi):.12f}\n")
            f.write(f"chi_imag = {np.imag(chi):.12f}\n")
            f.write(f"Delta_x = [1.496e11, 0, 0] (x-direction, 1 AU)\n")
            f.write(f"Frequency = 0.001 Hz\n")
            f.write(f"Constellations: LISA30 x Taiji0 (OLC TF)\n")
        print(f"\nResults written to loop/2-loop/p23-best-match.txt")
