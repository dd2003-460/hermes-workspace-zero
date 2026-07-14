#!/usr/bin/env python3
"""
Diagnostic: Why is v17's claimed -7.75e-3 unreproducible?

v17 claims: LISA(i=30deg) x Taiji(i=0deg), Gamma^V = -7.750753e-3 (without SP)
             and Gamma^V = -7.750761e-3 (with SP) — <0.02% difference

Test 5 hypotheses:
  H1: Full OLC formula (with SP) — our best implementation
  H2: Full OLC formula (without SP) — should be ~0 due to mirror symmetry
  H3: Pure antenna (T=1 for all links) — tests geometric factor only
  H4: OLC transfer function WITHOUT 1j prefactor (T = sinc * exp) — tests prefactor role
  H5: Transfer function evaluated ONLY at each sky direction (per-link T) — tests T factorization

Also test:
  H6: Normalized R^V vs unnormalized Gamma^V — what does v17 report?
  H7: Different normalization — divided by 4pi, or by antenna pattern product?

Goal: reproduce -7.75e-3 and understand all three anomalies:
  (A) frequency independence
  (B) <0.02% spatial phase effect
  (C) specific value -7.75e-3
"""
import numpy as np
import time

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

def olc_transfer_function_no_1j(f, L, cos_nu):
    """OLC transfer function WITHOUT the 1j prefactor."""
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    # No prefac = 1
    return sinc_v * phase

def michelson_transfer_function(f, L, cos_nu):
    """Michelson transfer function (sky-independent)."""
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase

# ============================================================
# Antenna patterns with various transfer functions
# ============================================================

def antenna_pattern_cw_sum_flexible(tG, pG, positions, L, tf_fn, include_1j=True):
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

        if not include_1j and 'olc' in tf_fn.__name__:
            pass  # already handled in tf_fn
        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

# ============================================================
# Constellation builder
# ============================================================

def build_constellation(L, inclination_rad, pos_offset=None):
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

    if pos_offset is not None:
        rotated += pos_offset
    return rotated

def spatial_phase(f, delta_x, TG, PG):
    k_hat = np.array([np.sin(TG)*np.cos(PG), np.sin(TG)*np.sin(PG), np.cos(TG)])
    delta_x_exp = delta_x.reshape(3, 1, 1)
    k_dot_delta = np.sum(k_hat * delta_x_exp, axis=0)
    omega = 2.0 * np.pi * np.asarray(f)
    return np.exp(-1j * omega / c * k_dot_delta)

# ============================================================
# ORF computation
# ============================================================

def compute_gamma(f, R1p, R1x, R2p, R2x, phase, use_gamma_I=True):
    """Compute Gamma^I (auto) and Gamma^V (chiral) and R^V (normalized)."""
    ntheta, nphi = len(f), len(f[0])
    dtheta = np.pi / ntheta
    dphi = 2.0 * np.pi / nphi
    dOmega = np.sin(f) * dtheta * dphi

    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    gamma_I = np.sum(phase * cross_corr * dOmega) / (4.0 * np.pi)
    gamma_V = np.sum(phase * chiral_corr * dOmega) / (4.0 * np.pi)

    S_A = np.sum(np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x) * dOmega) / (4.0 * np.pi)
    S_B = np.sum(np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x) * dOmega) / (4.0 * np.pi)

    rv = gamma_V / np.sqrt(S_A * S_B) if (S_A > 1e-30 and S_B > 1e-30) else 0.0

    return gamma_I, gamma_V, S_A, S_B, rv

# ============================================================
# Main
# ============================================================

def run_hypothesis_test(f_test, hyp_name, hyp_fn, incl1_deg, incl2_deg,
                       use_sp, delta_x, ntheta=128, nphi=256):
    """Run one hypothesis and return results."""
    incl1 = np.radians(incl1_deg)
    incl2 = np.radians(incl2_deg)

    L_lisa = 2.5e9
    L_taiji = 3.0e9

    pos1 = build_constellation(L_lisa, incl1)
    pos2 = build_constellation(L_taiji, incl2)

    if use_sp and delta_x is not None:
        pos2 = pos2 + delta_x

    tG = np.linspace(0, np.pi, ntheta, endpoint=False)
    pG = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')

    R1p, R1x = hyp_fn(TG, PG, pos1, L_lisa, TG, PG, use_sp, delta_x)
    R2p, R2x = hyp_fn(TG, PG, pos2, L_taiji, TG, PG, use_sp, delta_x)

    if use_sp and delta_x is not None:
        ph = spatial_phase(f_test, delta_x, TG, PG)
    else:
        ph = np.ones_like(TG)

    gamma_I, gamma_V, S_A, S_B, rv = compute_gamma(f_test, R1p, R1x, R2p, R2x, ph, TG, PG)

    return gamma_I, gamma_V, rv, S_A, S_B

def hyp_full_olc(TG, PG, pos, L, _TG, _PG, use_sp, delta_x):
    """H1/H2: Full OLC formula."""
    cos_nu_grid = np.sin(TG)*np.cos(PG)*pos[:,0:1] + np.sin(TG)*np.sin(PG)*pos[:,1:2] + np.cos(TG)*pos[:,2:3]
    cos_nu_grid = np.broadcast_to(cos_nu_grid, (3, TG.shape[0], TG.shape[1]))
    R_plus = np.zeros_like(TG, dtype=np.complex128)
    R_cross = np.zeros_like(TG, dtype=np.complex128)

    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)
    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    cw_links = [(0, 1), (1, 2), (2, 0)]
    for i, j in cw_links:
        u = pos[j] - pos[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]
        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0*th_dot_u*ph_dot_u
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = olc_transfer_function(1.0, L, cos_nu)  # T at f=1 to get shape
        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

def hyp_pure_antenna(TG, PG, pos, L, _TG, _PG, use_sp, delta_x):
    """H3: Pure antenna (T=1)."""
    nx = np.sin(TG)*np.cos(PG)
    ny = np.sin(TG)*np.sin(PG)
    nz = np.cos(TG)
    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph = np.array([-np.sin(PG), np.cos(PG), np.zeros_like(PG)])

    R_plus = np.zeros_like(TG, dtype=np.complex128)
    R_cross = np.zeros_like(TG, dtype=np.complex128)

    cw_links = [(0, 1), (1, 2), (2, 0)]
    for i, j in cw_links:
        u = pos[j] - pos[i]
        u = u / np.linalg.norm(u)
        th_dot_u = th[0]*u[0] + th[1]*u[1] + th[2]*u[2]
        ph_dot_u = ph[0]*u[0] + ph[1]*u[1] + ph[2]*u[2]
        F_plus = th_dot_u**2 - ph_dot_u**2
        F_cross = 2.0*th_dot_u*ph_dot_u
        R_plus += F_plus  # T=1
        R_cross += F_cross

    return R_plus, R_cross

# ============================================================
# MAIN: test all 5+ hypotheses
# ============================================================

def main():
    print("=" * 90)
    print("DIAGNOSTIC: Hypotheses for v17's -7.75e-3 value")
    print("=" * 90)

    f_test = 0.001
    incl1 = 30.0  # LISA inclination
    incl2 = 0.0   # Taiji inclination
    au = 1.496e11
    delta_x = np.array([0.0, 0.0, au])

    print(f"\nf = {f_test} Hz")
    print(f"LISA incl = {incl1}°, Taiji incl = {incl2}°")
    print(f"delta_x = [0, 0, {au:.3e}] m = {au/au:.1f} AU")
    print(f"v17 claimed: Gamma^V = -7.750753e-3 (without SP)")
    print()

    # Define all hypotheses
    # Hypothesis 1: Full OLC with SP
    def hyp1(TG, PG, pos, L, *_):
        return antenna_pattern_cw_sum_flexible(TG, PG, pos, L, olc_transfer_function, include_1j=True)
    # Hypothesis 2: Full OLC without SP
    def hyp2(TG, PG, pos, L, *_):
        return antenna_pattern_cw_sum_flexible(TG, PG, pos, L, olc_transfer_function, include_1j=True)
    # Hypothesis 3: Pure antenna (T=1) without SP
    def hyp3(TG, PG, pos, L, *_):
        return hyp_pure_antenna(TG, PG, pos, L, TG, PG, False, None)
    # Hypothesis 4: OLC without 1j prefactor, without SP
    def hyp4(TG, PG, pos, L, *_):
        return antenna_pattern_cw_sum_flexible(TG, PG, pos, L, olc_transfer_function_no_1j, include_1j=False)
    # Hypothesis 5: Michelson transfer function (sky-independent), without SP
    def hyp5(TG, PG, pos, L, *_):
        return antenna_pattern_cw_sum_flexible(TG, PG, pos, L, michelson_transfer_function, include_1j=True)

    hyps = [
        ("H1: Full OLC + SP", {"use_sp": True}),
        ("H2: Full OLC no SP", {"use_sp": False}),
        ("H3: Pure antenna (T=1) no SP", {"use_sp": False}),
        ("H4: OLC no 1j prefactor no SP", {"use_sp": False}),
        ("H5: Michelson no SP", {"use_sp": False}),
    ]

    hyp_fns = [hyp1, hyp2, hyp3, hyp4, hyp5]

    results = []

    for hyp_name, extra in hyps:
        use_sp = extra.get("use_sp", False)
        # Build positions
        pos1 = build_constellation(2.5e9, np.radians(incl1))
        pos2 = build_constellation(3.0e9, np.radians(incl2))
        if use_sp and delta_x is not None:
            pos2 = pos2 + delta_x

        tG = np.linspace(0, np.pi, 128, endpoint=False)
        pG = np.linspace(0, 2*np.pi, 256, endpoint=False)
        TG, PG = np.meshgrid(tG, pG, indexing='ij')

        R1p, R1x = hyp_fns[hyps.index((hyp_name, extra))](TG, PG, pos1, 2.5e9, TG, PG, use_sp, delta_x)
        R2p, R2x = hyp_fns[hyps.index((hyp_name, extra))](TG, PG, pos2, 3.0e9, TG, PG, use_sp, delta_x)

        if use_sp and delta_x is not None:
            ph = spatial_phase(f_test, delta_x, TG, PG)
        else:
            ph = np.ones_like(TG)

        gamma_I, gamma_V, S_A, S_B, rv = compute_gamma(f_test, R1p, R1x, R2p, R2x, ph, TG, PG)
        results.append((hyp_name, gamma_I, gamma_V, rv, S_A, S_B, use_sp))

    # Print results
    print(f"  {'Hypothesis':<45s} {'use_SP':<8s} {'Gamma^I':<15s} {'Gamma^V':<15s} {'R^V':<15s}")
    print("  " + "-" * 105)
    for hyp_name, gI, gV, rv, SA, SB, use_sp in results:
        print(f"  {hyp_name:<45s} {'YES' if use_sp else 'NO':<8s} {gI:<15.8f} {gV:<15.6e} {rv:<15.6e}")

    # Frequency sweep for H1 and H2
    print("\n" + "=" * 90)
    print("FREQUENCY SWEEP: H1 (Full OLC + SP) and H2 (Full OLC no SP)")
    print("=" * 90)
    print(f"  {'f (Hz)':<10s} {'Gamma^V_H1':<18s} {'Gamma^V_H2':<18s} {'R^V_H1':<18s}")
    print("  " + "-" * 68)

    for f in [0.001, 0.005, 0.01, 0.05, 0.1]:
        results_freq = []
        for hyp_fn, hyp_use_sp in [(hyp1, True), (hyp2, False)]:
            pos1 = build_constellation(2.5e9, np.radians(incl1))
            pos2 = build_constellation(3.0e9, np.radians(incl2))
            if hyp_use_sp and delta_x is not None:
                pos2 = pos2 + delta_x

            tG = np.linspace(0, np.pi, 128, endpoint=False)
            pG = np.linspace(0, 2*np.pi, 256, endpoint=False)
            TG, PG = np.meshgrid(tG, pG, indexing='ij')

            R1p, R1x = hyp_fn(TG, PG, pos1, 2.5e9, TG, PG, hyp_use_sp, delta_x)
            R2p, R2x = hyp_fn(TG, PG, pos2, 3.0e9, TG, PG, hyp_use_sp, delta_x)

            if hyp_use_sp and delta_x is not None:
                ph = spatial_phase(f, delta_x, TG, PG)
            else:
                ph = np.ones_like(TG)

            gamma_I, gamma_V, SA, SB, rv = compute_gamma(f, R1p, R1x, R2p, R2x, ph, TG, PG)
            results_freq.append((hyp_fn.__name__, hyp_use_sp, gamma_V, rv))

        hv1 = results_freq[0][2]
        hv2 = results_freq[1][2]
        rv1 = results_freq[0][3]
        print(f"  {f:<10.3f} {hv1:<18.6e} {hv2:<18.6e} {rv1:<18.6e}")

    # Test pure antenna at multiple inclinations
    print("\n" + "=" * 90)
    print("PURE ANTENNA H3: Inclination scan (f=0.001 Hz, no SP)")
    print("=" * 90)
    print(f"  {'LISA incl':<12s} {'Taiji incl':<12s} {'Gamma^V_H3':<18s} {'R^V_H3':<18s}")
    print("  " + "-" * 64)

    for inc1 in [0, 10, 20, 30, 45, 60, 80, 90]:
        pos1 = build_constellation(2.5e9, np.radians(inc1))
        pos2 = build_constellation(3.0e9, np.radians(incl2))
        tG = np.linspace(0, np.pi, 128, endpoint=False)
        pG = np.linspace(0, 2*np.pi, 256, endpoint=False)
        TG, PG = np.meshgrid(tG, pG, indexing='ij')

        R1p, R1x = hyp_pure_antenna(TG, PG, pos1, 2.5e9, TG, PG, False, None)
        R2p, R2x = hyp_pure_antenna(TG, PG, pos2, 3.0e9, TG, PG, False, None)

        ph = np.ones_like(TG)
        gamma_I, gamma_V, SA, SB, rv = compute_gamma(f_test, R1p, R1x, R2p, R2x, ph, TG, PG)
        print(f"  {inc1:<12d} {incl2:<12.0f} {gamma_V:<18.6e} {rv:<18.6e}")

    # Test: what if we use per-link T inside the integral?
    print("\n" + "=" * 90)
    print("H7: OLC transfer function WITHOUT spatial phase, f=0.1 Hz (should show freq dep)")
    print("=" * 90)
    for f in [0.001, 0.01, 0.1]:
        pos1 = build_constellation(2.5e9, np.radians(30))
        pos2 = build_constellation(3.0e9, np.radians(0))
        tG = np.linspace(0, np.pi, 128, endpoint=False)
        pG = np.linspace(0, 2*np.pi, 256, endpoint=False)
        TG, PG = np.meshgrid(tG, pG, indexing='ij')

        R1p, R1x = antenna_pattern_cw_sum_flexible(TG, PG, pos1, 2.5e9, olc_transfer_function, True)
        R2p, R2x = antenna_pattern_cw_sum_flexible(TG, PG, pos2, 3.0e9, olc_transfer_function, True)
        ph = np.ones_like(TG)

        gamma_I, gamma_V, SA, SB, rv = compute_gamma(f, R1p, R1x, R2p, R2x, ph, TG, PG)
        print(f"  f={f:.3f}: Gamma^V = {gamma_V:.6e}, R^V = {rv:.6e}, S_A = {SA:.8f}, S_B = {SB:.8f}")

    print("\nDone.")

if __name__ == '__main__':
    t0 = time.time()
    main()
    print(f"\nTotal time: {time.time() - t0:.1f}s")
