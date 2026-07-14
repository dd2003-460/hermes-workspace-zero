#!/usr/bin/env python3
"""
Diagnostic v2: Can CW sum + OLC transfer function reproduce v17's -7.75e-3?

v17 claims: LISA(i=30deg) x Taiji(i=0deg), R^V = -7.750753e-3 (without SP)
           The value is frequency independent.

Hypothesis: The value comes from CW sum with OLC transfer function,
           where each link has a different T due to different cos_nu.

Key: OLC TF = i*2*pi*f*L/c * sinc(beta*(1-cos_nu)) * exp(-i*beta*(1-cos_nu))
     This is the ONE-WAY LINK transfer function in Orlando's formulation.
     For CW sum, each link has different cos_nu -> different T -> breaks mirror symmetry.
"""
import numpy as np
import time

c = 299792458.0

def olc_transfer_function(f, L, cos_nu):
    """Full OLC transfer function (one-way link)."""
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-10
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase

def michelson_tf(f, L, cos_nu):
    """Michelson TF (sky-independent)."""
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-10, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase

def pure_antenna(f, L, cos_nu):
    """Pure antenna, T=1."""
    return np.ones_like(cos_nu, dtype=np.complex128)

def cw_sum_response(TG, PG, positions, L, tf_fn):
    """CW sum with flexible TF. Returns (R_plus, R_cross) as 2D arrays."""
    nx = np.sin(TG) * np.cos(PG)
    ny = np.sin(TG) * np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG),
                   np.cos(TG)*np.sin(PG),
                   -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    cw_links = [(0, 1), (1, 2), (2, 0)]
    R_plus = np.zeros_like(TG, dtype=np.complex128)
    R_cross = np.zeros_like(TG, dtype=np.complex128)

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]
        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(1.0, L, cos_nu)  # f=1 for shape only

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

def build_triangle(L, inclination_rad, z_offset=0.0):
    """Equilateral triangle with optional z-offset for non-coplanar."""
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

    if z_offset != 0.0:
        rotated[:, 2] += z_offset
    return rotated

def compute_chiral_R(R1p, R1x, R2p, R2x):
    """Compute unnormalized chiral correlation and normalized R^V.

    R^V = Re[sum conj(R1) * R2_chiral] / sqrt(normalization)
    where R_chiral = R_plus * R2_cross_conj - R_cross * R2_plus_conj (cross-correlation)
    """
    # Normalization factors
    S_A = np.sum(np.abs(R1p)**2 + np.abs(R1x)**2) / (4.0 * np.pi)
    S_B = np.sum(np.abs(R2p)**2 + np.abs(R2x)**2) / (4.0 * np.pi)

    # Chiral cross-correlation (parity-odd)
    chiral_integrand = np.real(np.conj(R1p) * R2x - np.conj(R1x) * R2p)

    # Sky integration
    dtheta = np.pi / R1p.shape[0]
    dphi = 2.0 * np.pi / R1p.shape[1]
    dOmega = np.sin(np.linspace(0, np.pi, R1p.shape[0]).reshape(-1, 1)) * dtheta * dphi

    gamma_V = np.sum(chiral_integrand * dOmega) / (4.0 * np.pi)
    gamma_I = np.sum(np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x) * dOmega) / (4.0 * np.pi)

    return gamma_I, gamma_V, S_A, S_B, gamma_V / np.sqrt(S_A * S_B) if S_A * S_B > 1e-30 else 0.0

def sky_maximize(R1p, R1x, R2p, R2x, ntheta=128, nphi=256):
    """Find the sky direction that maximizes |R^V| for a SINGLE direction."""
    # For a single sky direction, compute R^V directly
    dOmega_val = np.pi / ntheta * 2 * np.pi / nphi
    for it in range(ntheta):
        for ip in range(nphi):
            pass  # placeholder - we'll do vectorized version
    # Vectorized: scan grid, find max
    chiral_integrand = np.real(np.conj(R1p) * R2x - np.conj(R1x) * R2p)
    idx = np.argmax(np.abs(chiral_integrand))
    i, j = np.unravel_index(idx, chiral_integrand.shape)
    theta = np.pi * i / ntheta
    phi = 2 * np.pi * j / nphi
    rv_single = chiral_integrand[i, j] / np.sqrt(
        (np.abs(R1p[i,j])**2 + np.abs(R1x[i,j])**2) *
        (np.abs(R2p[i,j])**2 + np.abs(R2x[i,j])**2)
    )
    return theta, phi, rv_single

def main():
    t0 = time.time()
    print("=" * 80)
    print("DIAGNOSTIC v2: Source of v17's -7.75e-3")
    print("=" * 80)

    f = 0.001  # Hz
    L_lisa = 2.5e9
    L_taiji = 3.0e9

    incl1_deg = 30.0
    incl2_deg = 0.0
    au = 1.496e11  # 1 AU in meters

    TG = np.linspace(0, np.pi, 128, endpoint=False)
    PG = np.linspace(0, 2*np.pi, 256, endpoint=False)
    TG, PG = np.meshgrid(TG, PG, indexing='ij')

    results = []

    # ===== Test different TF configurations =====
    tf_configs = [
        ("OLC TF, coplanar", lambda pos, L: cw_sum_response(TG, PG, pos, L, olc_transfer_function)),
        ("Michelson TF, coplanar", lambda pos, L: cw_sum_response(TG, PG, pos, L, michelson_tf)),
        ("Pure antenna, coplanar", lambda pos, L: cw_sum_response(TG, PG, pos, L, pure_antenna)),
    ]

    for name, resp_fn in tf_configs:
        pos1 = build_triangle(L_lisa, np.radians(incl1_deg))
        pos2 = build_triangle(L_taiji, np.radians(incl2_deg))

        R1p, R1x = resp_fn(pos1, L_lisa)
        R2p, R2x = resp_fn(pos2, L_taiji)

        gI, gV, SA, SB, rv = compute_chiral_R(R1p, R1x, R2p, R2x)

        # Sky-maximized single-direction
        th, ph, rv_single = sky_maximize(R1p, R1x, R2p, R2x)
        results.append((name, gI, gV, rv, th, ph, rv_single))
        print(f"  {name:<35s} Gamma^I={gI:.6f}  Gamma^V={gV:.6e}  R^V={rv:.6e}  |R^V|_sky_max={np.abs(rv_single):.6e}  (theta={np.degrees(th):.1f}, phi={np.degrees(ph):.1f})")

    # ===== Non-coplanar =====
    print("\n  Non-coplanar configurations:")
    for z_off_name, z_off in [("z=0 (coplanar)", 0.0),
                               ("z=1 AU", au),
                               ("z=0.01 AU", 0.01*au)]:
        pos1 = build_triangle(L_lisa, np.radians(incl1_deg), z_offset=z_off)
        pos2 = build_triangle(L_taiji, np.radians(incl2_deg), z_offset=0.0)

        R1p, R1x = cw_sum_response(TG, PG, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = cw_sum_response(TG, PG, pos2, L_taiji, olc_transfer_function)

        gI, gV, SA, SB, rv = compute_chiral_R(R1p, R1x, R2p, R2x)
        th, ph, rv_single = sky_maximize(R1p, R1x, R2p, R2x)
        print(f"  {z_off_name:<20s} Gamma^V={gV:.6e}  R^V={rv:.6e}  |R^V|_sky_max={np.abs(rv_single):.6e}")

    # ===== Frequency sweep =====
    print("\n  Frequency sweep (OLC TF, coplanar):")
    for f in [0.0001, 0.001, 0.005, 0.01, 0.05, 0.1]:
        pos1 = build_triangle(L_lisa, np.radians(incl1_deg))
        pos2 = build_triangle(L_taiji, np.radians(incl2_deg))

        R1p, R1x = cw_sum_response(TG, PG, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = cw_sum_response(TG, PG, pos2, L_taiji, olc_transfer_function)

        gI, gV, SA, SB, rv = compute_chiral_R(R1p, R1x, R2p, R2x)
        th, ph, rv_single = sky_maximize(R1p, R1x, R2p, R2x)
        print(f"  f={f:.4f}: Gamma^I={gI:.6f}  Gamma^V={gV:.6e}  R^V={rv:.6e}  |R^V|_max={np.abs(rv_single):.6e}")

    # ===== Direct comparison with different inclination pairs =====
    print("\n  Inclination scan: R^V (OLC TF, coplanar):")
    for inc1 in [0, 10, 20, 30, 45, 60, 80, 90]:
        pos1 = build_triangle(L_lisa, np.radians(inc1))
        pos2 = build_triangle(L_taiji, np.radians(0))

        R1p, R1x = cw_sum_response(TG, PG, pos1, L_lisa, olc_transfer_function)
        R2p, R2x = cw_sum_response(TG, PG, pos2, L_taiji, olc_transfer_function)

        gI, gV, SA, SB, rv = compute_chiral_R(R1p, R1x, R2p, R2x)
        th, ph, rv_single = sky_maximize(R1p, R1x, R2p, R2x)
        print(f"  LISA(i={inc1:2d}) x Taiji(i=0):  Gamma^V={gV:.6e}  R^V={rv:.6e}  |R^V|_max={np.abs(rv_single):.6e}")

    # ===== Cross-check: self-correlation =====
    print("\n  Self-correlation (should be Gamma^V=0):")
    pos = build_triangle(L_lisa, np.radians(incl1_deg))
    R1p, R1x = cw_sum_response(TG, PG, pos, L_lisa, olc_transfer_function)
    R2p, R2x = cw_sum_response(TG, PG, pos, L_lisa, olc_transfer_function)
    gI, gV, SA, SB, rv = compute_chiral_R(R1p, R1x, R2p, R2x)
    print(f"    LISA(30) x LISA(30):  Gamma^V={gV:.6e}")

    print(f"\n  TARGET: v17 claims R^V = -7.750753e-3")
    print(f"  Looking for: matches within 0.1% of -7.750753e-3")

    total_time = time.time() - t0
    print(f"\nDone. Total time: {total_time:.1f}s")

if __name__ == '__main__':
    main()
