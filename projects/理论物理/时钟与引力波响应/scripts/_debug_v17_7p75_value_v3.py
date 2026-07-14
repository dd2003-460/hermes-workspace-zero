#!/usr/bin/env python3
"""
Diagnostic v3: Deep investigation of v17's -7.750753e-3 source.

Hypotheses tested:
H1: CW sum + OLC TF breaks mirror symmetry -> nonzero Gamma^V (PARTIALLY CONFIRMED in v2)
H2: v17's value comes from a specific sky direction, not sky-average
H3: The normalization convention differs from what I use
H4: The actual chiral_integrand at v17's claimed direction gives -7.75e-3

Key fix from v2: Pass frequency properly to transfer function.
In v2, f=1 was hardcoded, which only gives the "shape" of the response.
"""
import numpy as np
import time

c = 299792458.0

def olc_transfer_function(f, L, cos_nu):
    """Full OLC transfer function (one-way link)."""
    beta = np.pi * f * L / c  # f > 0, abs not needed
    sinc_arg = beta * (1.0 - cos_nu)
    eps = 1e-10
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * (1.0 - cos_nu))
    prefac = 1j * 2.0 * np.pi * f * L / c
    return prefac * sinc_v * phase

def build_triangle(L, inclination_rad, z_offset=0.0):
    """Equilateral triangle with optional z-offset.
    Arms: 0->1 along x, 1->2 at 60°, 2->0 at -60°.
    Inclination rotates around x-axis.
    """
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

def cw_sum_response_at_dir(TG, PG, positions, L, f, tf_fn):
    """CW sum at a SINGLE sky direction. Returns (R_plus, R_cross)."""
    nx = np.sin(TG) * np.cos(PG)
    ny = np.sin(TG) * np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG),
                   np.cos(TG)*np.sin(PG),
                   -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), 0.0])

    cw_links = [(0, 1), (1, 2), (2, 0)]
    R_plus = 0.0
    R_cross = 0.0

    for i, j in cw_links:
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]
        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(f, L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

def chiral_R_single(R1p, R1x, R2p, R2x):
    """Compute chiral correlation for a single sky direction.
    R^V_single = Re[conj(R1p)*R2x - conj(R1x)*R2p] / sqrt(|R1p|^2+|R1x|^2) / sqrt(|R2p|^2+|R2x|^2)
    """
    denom1 = np.sqrt(np.abs(R1p)**2 + np.abs(R1x)**2)
    denom2 = np.sqrt(np.abs(R2p)**2 + np.abs(R2x)**2)
    chiral = np.real(np.conj(R1p) * R2x - np.conj(R1x) * R2p)
    if denom1 * denom2 > 1e-30:
        return chiral / (denom1 * denom2)
    return 0.0

def main():
    t0 = time.time()
    print("=" * 80)
    print("DIAGNOSTIC v3: Deep investigation of v17's -7.750753e-3")
    print("=" * 80)

    # v17 claimed direction
    v17_theta = np.radians(36.51)
    v17_phi = np.radians(82.58)

    L_lisa = 2.5e9  # ~2.5 million km
    L_taiji = 3.0e9  # ~3 million km
    au = 1.496e11

    # ============================================================
    # Part 1: Compute R^V at v17's claimed direction
    # ============================================================
    print("\n=== Part 1: R^V at v17 claimed direction (theta=36.51, phi=82.58) ===")
    for f in [0.001, 0.01, 0.1]:
        pos1 = build_triangle(L_lisa, np.radians(30.0))
        pos2 = build_triangle(L_taiji, np.radians(0.0))

        R1p, R1x = cw_sum_response_at_dir(v17_theta, v17_phi, pos1, L_lisa, f, olc_transfer_function)
        R2p, R2x = cw_sum_response_at_dir(v17_theta, v17_phi, pos2, L_taiji, f, olc_transfer_function)

        rv_single = chiral_R_single(R1p, R1x, R2p, R2x)

        # Also compute auto-correlations
        S1 = np.abs(R1p)**2 + np.abs(R1x)**2
        S2 = np.abs(R2p)**2 + np.abs(R2x)**2
        cross = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
        chir = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

        print(f"\n  f={f}:")
        print(f"    R1p = {R1p:.6e}, R1x = {R1x:.6e}")
        print(f"    R2p = {R2p:.6e}, R2x = {R2x:.6e}")
        print(f"    S1 = {S1:.6e}, S2 = {S2:.6e}")
        print(f"    cross = {cross:.6e}, chir = {chir:.6e}")
        print(f"    R^V_single = {rv_single:.6e}")
        print(f"    v17 target = -7.750753e-3")

        # Check: is the value coming from the TF amplitude or the phase?
        # Compare with pure antenna (T=1)
        R1p_noTF, R1x_noTF = cw_sum_response_at_dir(v17_theta, v17_phi, pos1, L_lisa, f,
                                                      lambda ff, LL, cn: np.ones_like(cn, dtype=np.complex128))
        R2p_noTF, R2x_noTF = cw_sum_response_at_dir(v17_theta, v17_phi, pos2, L_taiji, f,
                                                      lambda ff, LL, cn: np.ones_like(cn, dtype=np.complex128))
        rv_noTF = chiral_R_single(R1p_noTF, R1x_noTF, R2p_noTF, R2x_noTF)
        print(f"    R^V_single (no TF, T=1) = {rv_noTF:.6e}")

    # ============================================================
    # Part 2: Scan ALL sky directions, histogram R^V_single
    # ============================================================
    print("\n=== Part 2: Sky scan of R^V_single (f=0.001 Hz) ===")
    ntheta = 180
    nphi = 360
    TG = np.linspace(0, np.pi, ntheta, endpoint=False)
    PG = np.linspace(0, 2*np.pi, nphi, endpoint=False)

    pos1 = build_triangle(L_lisa, np.radians(30.0))
    pos2 = build_triangle(L_taiji, np.radians(0.0))

    rv_values = []
    rv_at_v17_dir = None

    # Strided scan for speed
    stride_t = max(1, ntheta // 90)
    stride_p = max(1, nphi // 180)

    for it in range(0, ntheta, stride_t):
        for ip in range(0, nphi, stride_p):
            th = TG[it]
            ph = PG[ip]
            R1p, R1x = cw_sum_response_at_dir(th, ph, pos1, L_lisa, 0.001, olc_transfer_function)
            R2p, R2x = cw_sum_response_at_dir(th, ph, pos2, L_taiji, 0.001, olc_transfer_function)
            rv = chiral_R_single(R1p, R1x, R2p, R2x)
            rv_values.append(rv)

            # Check if this is close to v17 direction
            dth = abs(th - v17_theta)
            dph = abs(ph - v17_phi)
            if dth < 0.02 and dph < 0.02:
                rv_at_v17_dir = rv

    rv_array = np.array(rv_values)
    print(f"  Min R^V_single = {np.min(rv_array):.6e}")
    print(f"  Max R^V_single = {np.max(rv_array):.6e}")
    print(f"  Mean R^V_single = {np.mean(rv_array):.6e}")
    print(f"  std R^V_single = {np.std(rv_array):.6e}")
    if rv_at_v17_dir is not None:
        print(f"  R^V_single near v17 dir = {rv_at_v17_dir:.6e}")

    # Find sky direction closest to -7.75e-3
    target = -7.750753e-3
    idx_closest = np.argmin(np.abs(rv_array - target))
    i_closest = idx_closest // (nphi // stride_p)
    j_closest = idx_closest % (nphi // stride_p)
    closest_th = TG[i_closest]
    closest_ph = PG[j_closest]
    print(f"\n  Closest to target -7.75e-3:")
    print(f"    theta = {np.degrees(closest_th):.2f}°, phi = {np.degrees(closest_ph):.2f}°")
    print(f"    R^V = {rv_array[idx_closest]:.6e}")

    # ============================================================
    # Part 3: What if v17 computed with ONLY the chiral correlation
    #         (no normalization)?
    # ============================================================
    print("\n=== Part 3: Unnormalized chiral correlation at v17 direction ===")
    for f in [0.001]:
        R1p, R1x = cw_sum_response_at_dir(v17_theta, v17_phi, pos1, L_lisa, f, olc_transfer_function)
        R2p, R2x = cw_sum_response_at_dir(v17_theta, v17_phi, pos2, L_taiji, f, olc_transfer_function)
        chir = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)
        cross = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
        print(f"  f={f}: unnormalized chir = {chir:.6e}")
        print(f"  v17 target = -7.750753e-3")

    # ============================================================
    # Part 4: What about single-arm (not CW sum) correlation?
    # ============================================================
    print("\n=== Part 4: Single arm (link 0->1) vs CW sum ===")
    # Single link: 0->1 only
    def single_link_response(TG, PG, positions, L, f, tf_fn, link=(0,1)):
        nx = np.sin(TG) * np.cos(PG)
        ny = np.sin(TG) * np.sin(PG)
        nz = np.cos(TG)
        th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
        ph = np.array([-np.sin(PG), np.cos(PG), 0.0])

        i, j = link
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]
        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0 * th_dot_u * ph_dot_u

        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(f, L, cos_nu)

        return F_plus * T, F_cross * T

    for f in [0.001]:
        R1p_s, R1x_s = single_link_response(v17_theta, v17_phi, pos1, L_lisa, f, olc_transfer_function)
        R2p_s, R2x_s = single_link_response(v17_theta, v17_phi, pos2, L_taiji, f, olc_transfer_function)
        rv_single_link = chiral_R_single(R1p_s, R1x_s, R2p_s, R2x_s)
        print(f"  Single-link (0->1): R^V = {rv_single_link:.6e}")

        R1p_cw, R1x_cw = cw_sum_response_at_dir(v17_theta, v17_phi, pos1, L_lisa, f, olc_transfer_function)
        R2p_cw, R2x_cw = cw_sum_response_at_dir(v17_theta, v17_phi, pos2, L_taiji, f, olc_transfer_function)
        rv_cw = chiral_R_single(R1p_cw, R1x_cw, R2p_cw, R2x_cw)
        print(f"  CW sum: R^V = {rv_cw:.6e}")
        print(f"  v17 target = -7.750753e-3")

    # ============================================================
    # Part 5: Scan inclinations more finely around the claimed value
    # ============================================================
    print("\n=== Part 5: Fine inclination scan at v17 direction ===")
    for inc1 in np.arange(20, 41, 2.5):
        pos1f = build_triangle(L_lisa, np.radians(inc1))
        R1p, R1x = cw_sum_response_at_dir(v17_theta, v17_phi, pos1f, L_lisa, 0.001, olc_transfer_function)
        R2p, R2x = cw_sum_response_at_dir(v17_theta, v17_phi, pos2, L_taiji, 0.001, olc_transfer_function)
        rv = chiral_R_single(R1p, R1x, R2p, R2x)
        match = ""
        if abs(rv + 7.75e-3) < 1e-4:
            match = " <<< CLOSE TO TARGET!"
        print(f"  LISA(i={inc1:.1f}) x Taiji(i=0): R^V = {rv:.6e}{match}")

    # ============================================================
    # Part 6: What if the "v17 value" came from a DIFFERENT pair?
    # LISA x LISA, Taiji x Taiji?
    # ============================================================
    print("\n=== Part 6: Self-correlation chiral response ===")
    for name, pos, L in [("LISA(30) x LISA(30)", build_triangle(L_lisa, np.radians(30)), L_lisa),
                          ("Taiji(0) x Taiji(0)", build_triangle(L_taiji, np.radians(0)), L_taiji)]:
        R1p, R1x = cw_sum_response_at_dir(v17_theta, v17_phi, pos, L, 0.001, olc_transfer_function)
        R2p, R2x = cw_sum_response_at_dir(v17_theta, v17_phi, pos, L, 0.001, olc_transfer_function)
        rv = chiral_R_single(R1p, R1x, R2p, R2x)
        print(f"  {name}: R^V = {rv:.6e}")

    # ============================================================
    # Part 7: Gamma^V sky-averaged at different frequencies (proper f)
    # ============================================================
    print("\n=== Part 7: Sky-averaged Gamma^V at proper frequencies ===")
    def gamma_v_sky_avg(f):
        ntheta = 90
        nphi = 180
        TG = np.linspace(0, np.pi, ntheta, endpoint=False)
        PG = np.linspace(0, 2*np.pi, nphi, endpoint=False)
        TG, PG = np.meshgrid(TG, PG, indexing='ij')

        pos1 = build_triangle(L_lisa, np.radians(30.0))
        pos2 = build_triangle(L_taiji, np.radians(0.0))

        R1p_all = np.zeros((ntheta, nphi), dtype=np.complex128)
        R1x_all = np.zeros((ntheta, nphi), dtype=np.complex128)
        R2p_all = np.zeros((ntheta, nphi), dtype=np.complex128)
        R2x_all = np.zeros((ntheta, nphi), dtype=np.complex128)

        for it in range(ntheta):
            for ip in range(nphi):
                R1p_all[it, ip], R1x_all[it, ip] = cw_sum_response_at_dir(
                    TG[it, ip], PG[it, ip], pos1, L_lisa, f, olc_transfer_function)
                R2p_all[it, ip], R2x_all[it, ip] = cw_sum_response_at_dir(
                    TG[it, ip], PG[it, ip], pos2, L_taiji, f, olc_transfer_function)

        chiral_integrand = np.real(np.conj(R1p_all) * R2x_all - np.conj(R1x_all) * R2p_all)
        dtheta = np.pi / ntheta
        dphi = 2.0 * np.pi / nphi
        dOmega = np.sin(np.linspace(0, np.pi, ntheta, endpoint=False).reshape(-1, 1)) * dtheta * dphi
        gamma_V = np.sum(chiral_integrand * dOmega) / (4.0 * np.pi)

        # Normalization
        S_A = np.sum(np.abs(R1p_all)**2 + np.abs(R1x_all)**2) / (4.0 * np.pi)
        S_B = np.sum(np.abs(R2p_all)**2 + np.abs(R2x_all)**2) / (4.0 * np.pi)
        rv = gamma_V / np.sqrt(S_A * S_B) if S_A * S_B > 1e-30 else 0.0
        return gamma_V, S_A, S_B, rv

    for f in [0.001, 0.01, 0.1]:
        gV, SA, SB, rv = gamma_v_sky_avg(f)
        print(f"  f={f}: Gamma^V={gV:.6e}, S_A={SA:.6e}, S_B={SB:.6e}, R^V={rv:.6e}")

    print(f"\n  TARGET: v17 claims R^V = -7.750753e-3")
    total_time = time.time() - t0
    print(f"\nDone. Total time: {total_time:.1f}s")

if __name__ == '__main__':
    main()
