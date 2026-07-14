#!/usr/bin/env python3
"""
P2-3: Comprehensive single-sky search for v17 target R^V = -7.750753e-3.

Tests multiple interpretations:
1. With spatial phase (OLC TF + SP)
2. Without spatial phase (OLC TF only, chi=1)
3. Without spatial phase, with Michelson TF

Key insight from prior session: the debug script at theta=28° gave stable R^V
across frequencies, suggesting SP was NOT applied (or chi_real≈1).
"""
import numpy as np
import sys

c = 299792458.0
TARGET_RV = -7.750753e-3

# ============================================================
# Transfer functions
# ============================================================

def olc_transfer_function(f, L, cos_nu):
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase


def michelson_transfer_function(f, L, cos_nu):
    """Michelson TF for comparison."""
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase

# ============================================================
# Antenna patterns
# ============================================================

def antenna_cw_sum(tG, pG, positions, L, tf_fn):
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
# ORF computation
# ============================================================

def compute_orf_raw(R1p, R1x, R2p, R2x, chi_real):
    """
    ORF computation for single direction.
    chi_real: real part of spatial phase factor (scalar).
    This matches the debug script's approach.
    """
    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    gamma_I = chi_real * cross_corr
    gamma_V = chi_real * chiral_corr

    S_A = np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x)
    S_B = np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv


# ============================================================
# Main scan
# ============================================================

def main():
    f = 0.001
    L_lisa = 2.5e9
    L_taiji = 3.0e9
    incl_lisa = np.radians(30.0)
    incl_taiji = np.radians(0.0)
    delta_x = np.array([1.496e11, 0.0, 0.0])

    pos1 = build_constellation(L_lisa, incl_lisa)
    pos2_no_sp = build_constellation(L_taiji, incl_taiji)
    pos2_sp = pos2_no_sp + delta_x

    TG_ref = np.linspace(0, np.pi, 256, endpoint=False)
    PG_ref = np.linspace(0, 2*np.pi, 512, endpoint=False)
    _TG, _PG = np.meshgrid(TG_ref, PG_ref, indexing='ij')
    sin_theta_ref = np.sin(_TG)
    dOmega_ref = sin_theta_ref * (np.pi/256) * (2*np.pi/512)
    inv4pi = 1.0 / (4.0 * np.pi)

    # Sky-averaged values (for reference)
    R1p_sky, R1x_sky = antenna_cw_sum(_TG, _PG, pos1, L_lisa, olc_transfer_function)
    R2p_sky, R2x_sky = antenna_cw_sum(_TG, _PG, pos2_sp, L_taiji, olc_transfer_function)

    cross_sky = np.real(np.conj(R1p_sky)*R2p_sky + np.conj(R1x_sky)*R2x_sky)
    chiral_sky = np.real(np.conj(R1p_sky)*R2x_sky - np.conj(R1x_sky)*R2p_sky)

    S_A_sky = np.sum(np.real(np.conj(R1p_sky)*R1p_sky + np.conj(R1x_sky)*R1x_sky) * dOmega_ref) * inv4pi
    S_B_sky = np.sum(np.real(np.conj(R2p_sky)*R2p_sky + np.conj(R2x_sky)*R2x_sky) * dOmega_ref) * inv4pi

    gamma_I_sky = np.sum(cross_sky * dOmega_ref) * inv4pi
    gamma_V_sky = np.sum(chiral_sky * dOmega_ref) * inv4pi
    rv_sky = gamma_V_sky / np.sqrt(S_A_sky * S_B_sky)

    print("=" * 90)
    print("SKY-AVERAGED REFERENCE (OLC TF + SP, f=0.001 Hz)")
    print("=" * 90)
    print(f"  Gamma^I = {gamma_I_sky:.10e}")
    print(f"  Gamma^V = {gamma_V_sky:.10e}")
    print(f"  S_A = {S_A_sky:.10e}, S_B = {S_B_sky:.10e}")
    print(f"  R^V (sky-avg) = {rv_sky:.10e}")
    print(f"  v17 target = {TARGET_RV:.10e}")
    print(f"  Ratio = {rv_sky / TARGET_RV:.4f}")

    # ---- Approach A: OLC + SP, single direction ----
    print(f"\n{'=' * 90}")
    print("APPROACH A: OLC TF + SP, single direction scan")
    print(f"{'=' * 90}")
    print(f"  theta(deg)   phi(deg)   R^V                  |delta|")
    print(f"  " + "-" * 70)

    best_results_A = []
    for td in np.linspace(5, 55, 101):
        theta = np.radians(td)
        for pd in np.linspace(80, 100, 41):
            phi = np.radians(pd)

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2_sp, L_taiji, olc_transfer_function)

            k_hat = np.array([np.sin(theta)*np.cos(phi),
                              np.sin(theta)*np.sin(phi),
                              np.cos(theta)])
            k_dot = np.sum(k_hat * delta_x)
            omega = 2.0 * np.pi * f
            chi = np.exp(-1j * omega / c * k_dot)
            chi_real = np.real(chi)

            gI, gV, SA, SB, rv = compute_orf_raw(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], chi_real)

            dist = abs(rv - TARGET_RV)
            if dist < 5e-4:
                best_results_A.append((td, pd, rv, dist, chi_real))

    best_results_A.sort(key=lambda x: x[3])
    for td, pd, rv, dist, cr in best_results_A[:15]:
        print(f"  {td:<12.1f} {pd:<10.1f} {rv:<22.6e} {dist:<15.6e} chi_real={cr:.6f}")

    # ---- Approach B: OLC only (no SP), single direction ----
    print(f"\n{'=' * 90}")
    print("APPROACH B: OLC TF only (chi=1.0), single direction scan")
    print(f"{'=' * 90}")

    best_results_B = []
    for td in np.linspace(5, 55, 101):
        theta = np.radians(td)
        for pd in np.linspace(80, 100, 41):
            phi = np.radians(pd)

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2_no_sp, L_taiji, olc_transfer_function)

            gI, gV, SA, SB, rv = compute_orf_raw(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], 1.0)

            dist = abs(rv - TARGET_RV)
            if dist < 5e-3:
                best_results_B.append((td, pd, rv, dist))

    best_results_B.sort(key=lambda x: x[3])
    for td, pd, rv, dist in best_results_B[:15]:
        print(f"  {td:<12.1f} {pd:<10.1f} {rv:<22.6e} {dist:<15.6e}")

    # ---- Approach C: Michelson TF (no SP), single direction ----
    print(f"\n{'=' * 90}")
    print("APPROACH C: Michelson TF only (no SP), single direction scan")
    print(f"{'=' * 90}")

    best_results_C = []
    for td in np.linspace(5, 55, 101):
        theta = np.radians(td)
        for pd in np.linspace(80, 100, 41):
            phi = np.radians(pd)

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, michelson_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2_no_sp, L_taiji, michelson_transfer_function)

            gI, gV, SA, SB, rv = compute_orf_raw(R1p[0,0], R1x[0,0], R2p[0,0], R2x[0,0], 1.0)

            dist = abs(rv - TARGET_RV)
            if dist < 1e-2:
                best_results_C.append((td, pd, rv, dist))

    best_results_C.sort(key=lambda x: x[3])
    for td, pd, rv, dist in best_results_C[:10]:
        print(f"  {td:<12.1f} {pd:<10.1f} {rv:<22.6e} {dist:<15.6e}")

    # ---- Approach D: OLC + SP, full chiral computation (chi, not chi_real) ----
    print(f"\n{'=' * 90}")
    print("APPROACH D: OLC TF + SP with full chi (not chi_real)")
    print(f"{'=' * 90}")

    best_results_D = []
    for td in np.linspace(5, 55, 101):
        theta = np.radians(td)
        for pd in np.linspace(80, 100, 41):
            phi = np.radians(pd)

            T = np.array([[theta]])
            P = np.array([[phi]])

            R1p, R1x = antenna_cw_sum(T, P, pos1, L_lisa, olc_transfer_function)
            R2p, R2x = antenna_cw_sum(T, P, pos2_sp, L_taiji, olc_transfer_function)

            k_hat = np.array([np.sin(theta)*np.cos(phi),
                              np.sin(theta)*np.sin(phi),
                              np.cos(theta)])
            k_dot = np.sum(k_hat * delta_x)
            omega = 2.0 * np.pi * f
            chi = np.exp(-1j * omega / c * k_dot)

            raw_chiral = np.conj(R1p[0,0])*R2x[0,0] - np.conj(R1x[0,0])*R2p[0,0]
            raw_cross = np.conj(R1p[0,0])*R2p[0,0] + np.conj(R1x[0,0])*R2x[0,0]

            gamma_V = np.real(chi * raw_chiral)
            gamma_I = np.real(chi * raw_cross)

            SA = np.real(np.conj(R1p[0,0])*R1p[0,0] + np.conj(R1x[0,0])*R1x[0,0])
            SB = np.real(np.conj(R2p[0,0])*R2p[0,0] + np.conj(R2x[0,0])*R2x[0,0])

            rv = gamma_V / np.sqrt(SA * SB) if (SA > 1e-30 and SB > 1e-30) else 0.0

            dist = abs(rv - TARGET_RV)
            if dist < 5e-4:
                best_results_D.append((td, pd, rv, dist, chi, chi.real))

    best_results_D.sort(key=lambda x: x[3])
    for td, pd, rv, dist, chi, cr in best_results_D[:15]:
        print(f"  {td:<12.1f} {pd:<10.1f} {rv:<22.6e} {dist:<15.6e} chi_real={cr:.6f}")

    # ---- Write best match file ----
    if best_results_A:
        print(f"\n{'=' * 90}")
        print("BEST MATCH SUMMARY")
        print(f"{'=' * 90}")

        # Write best results from approach A
        for i, (td, pd, rv, dist, cr) in enumerate(best_results_A[:3]):
            print(f"  A#{i+1}: theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}, chi_real={cr:.6f}")
        for i, (td, pd, rv, dist) in enumerate(best_results_B[:3]):
            print(f"  B#{i+1}: theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e} (no SP)")
        for i, (td, pd, rv, dist, chi, cr) in enumerate(best_results_D[:3]):
            print(f"  D#{i+1}: theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}")

        best_td, best_pd, best_rv, best_dist, best_chi_real = best_results_A[0]

        # Save detailed results
        results_content = f"""P2-3 Comprehensive Single-Sky Search Results
=============================================

Target R^V = {TARGET_RV:.10e}
Frequency: 0.001 Hz
Constellations: LISA30 x Taiji0 (30° inclination for LISA, 0° for Taiji)
Delta_x: [1.496e11, 0, 0] (1 AU in x-direction)

Sky-averaged R^V (OLC + SP): {rv_sky:.10e}
  Ratio to target: {rv_sky / TARGET_RV:.4f}
  → v17 target is NOT sky-averaged (confirms prior analysis)

Top matches:

APPROACH A (OLC + SP, using chi_real):
"""
        for td, pd, rv, dist, cr in best_results_A[:10]:
            results_content += f"  theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}, chi_real={cr:.6f}\n"

        results_content += f"\nAPPROACH B (OLC only, no SP, chi=1.0):\n"
        for td, pd, rv, dist in best_results_B[:10]:
            results_content += f"  theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}\n"

        results_content += f"\nAPPROACH D (OLC + SP, full chi):\n"
        for td, pd, rv, dist, chi, cr in best_results_D[:10]:
            results_content += f"  theta={td:.1f}°, phi={pd:.1f}°, R^V={rv:.6e}, |delta|={dist:.6e}, chi_real={cr:.6f}\n"

        with open("loop/2-loop/p23-comprehensive-results.txt", "w") as fh:
            fh.write(results_content)

        print(f"\nResults written to loop/2-loop/p23-comprehensive-results.txt")

if __name__ == "__main__":
    main()
