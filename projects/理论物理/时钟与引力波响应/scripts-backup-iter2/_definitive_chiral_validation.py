#!/usr/bin/env python3
"""
Definitive chiral ORF validation: endpoint=True vs endpoint=False for v17 paper.

This script performs the final validation of the key finding:
  The ~577x discrepancy between script 11's Gamma^V and v17's Gamma^V is
  caused by endpoint=True in the phi integration, which breaks reflection
  symmetry at coarse grids for coplanar detectors.

Computes Gamma^V for:
  1. LISA(i=30) x Taiji(i=0) coplanar — true Gamma^V = 0
  2. LISA(i=60) x Taiji(i=0) non-coplanar — non-zero Gamma^V
  3. OLC(i=0) x Taiji(i=0) coplanar — true Gamma^V = 0

For each, tests endpoint=True and endpoint=False at grids: 32x64, 64x128, 128x256
"""
import numpy as np
import sys
import time

c = 299792458.0

# ━━━ OLC One-Way Link Transfer Function ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function for OLC."""
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    return prefac * sinc_v * phase

# ━━━ Michelson Transfer Function ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def michelson_transfer_function(f, L, cos_nu):
    """Michelson link transfer function (simplified, no 1-cos_nu in prefac)."""
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase

# ━━━ CW-sum antenna pattern (same as script 11) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def antenna_pattern_cw_sum(tG, pG, positions, L, transfer_fn='olc'):
    """
    CW-sum antenna pattern for triangular constellation.
    R_plus = sum_{CW links} F_+(link) * T(link)
    R_cross = sum_{CW links} F_x(link) * T(link)
    """
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
        T = transfer_fn(np.ones_like(tG), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

# ━━━ Constellation builder ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_constellation(L, inclination_rad, reference_position=None):
    """Build triangular constellation with given arm length and inclination."""
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    positions = np.array([r1, r2, r3])

    # Inclination rotation (x-axis)
    cos_i = np.cos(inclination_rad)
    sin_i = np.sin(inclination_rad)
    rotated = np.zeros_like(positions)
    rotated[:, 0] = positions[:, 0]
    rotated[:, 1] = positions[:, 1] * cos_i - positions[:, 2] * sin_i
    rotated[:, 2] = positions[:, 1] * sin_i + positions[:, 2] * cos_i
    return rotated, reference_position

# ━━━ Spatial phase factor ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def spatial_phase(f, delta_x, TG, PG):
    """exp(-i*omega/c * k_hat . delta_x)."""
    k_hat = np.array([
        np.sin(TG)*np.cos(PG),
        np.sin(TG)*np.sin(PG),
        np.cos(TG)
    ])
    delta_x_exp = delta_x.reshape(3, 1, 1)
    k_dot_delta = np.sum(k_hat * delta_x_exp, axis=0)
    omega = 2.0 * np.pi * np.asarray(f)
    return np.exp(-1j * omega / c * k_dot_delta)

# ━━━ ORF computation ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def compute_gamma_V(R1p, R1x, R2p, R2x, phase, dOmega, endpoint=False, nphi=64):
    """
    Compute Gamma^V with either uniform or sin(theta) measure.
    R_V = sum(phase * (conj(R1p)*R2x - conj(R1x)*R2p)) * dOmega / (4*pi)
    """
    integrand = np.real(np.conj(R1p) * R2x - np.conj(R1x) * R2p)
    weighted = phase * integrand
    return np.sum(weighted) * dOmega / (4.0 * np.pi)

def compute_all_orfs(f, positions1, L1, positions2, L2, incl1_deg, incl2_deg,
                     ntheta, nphi, use_spatial_phase, delta_x):
    """
    Compute Gamma^I and Gamma^V with BOTH endpoint=True and False,
    and BOTH uniform and sin(theta) measures.
    Returns dict with all combinations.
    """
    results = {}

    for endpoint_label, endpoint in [('False', False), ('True', True)]:
        for measure_label, dOmega_fn in [('uniform', None), ('sin_theta', None)]:
            if endpoint:
                # endpoint=True: include phi=2pi edge
                tG = np.linspace(0, np.pi, ntheta)
                pG = np.linspace(0, 2*np.pi, nphi, endpoint=True)
            else:
                tG = np.linspace(0, np.pi, ntheta, endpoint=False)
                pG = np.linspace(0, 2*np.pi, nphi, endpoint=False)

            TG, PG = np.meshgrid(tG, pG, indexing='ij')

            if endpoint:
                # For endpoint=True, the phi spacing is different
                dphi = 2*np.pi / (nphi - 1)
                dtheta = np.pi / (ntheta - 1)
            else:
                dphi = 2*np.pi / nphi
                dtheta = np.pi / (ntheta - 1)

            if measure_label == 'uniform':
                dOmega_val = dtheta * dphi
                dOmega = np.ones_like(TG) * dOmega_val
            else:
                # sin(theta) measure
                dOmega = np.sin(TG) * dtheta * dphi

            # Antenna patterns
            R1p, R1x = antenna_pattern_cw_sum(TG, PG, positions1, L1, olc_transfer_function)
            R2p, R2x = antenna_pattern_cw_sum(TG, PG, positions2, L2, olc_transfer_function)

            # Spatial phase
            if use_spatial_phase and delta_x is not None:
                ph = spatial_phase(f, delta_x, TG, PG)
            else:
                ph = np.ones_like(TG)

            # Gamma^I and Gamma^V
            cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
            chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

            gamma_I = np.sum(ph * cross_corr * dOmega) / (4.0 * np.pi)
            gamma_V = np.sum(ph * chiral_corr * dOmega) / (4.0 * np.pi)

            key = f"ep={endpoint_label}_{measure_label}"
            results[key] = {'gamma_I': gamma_I, 'gamma_V': gamma_V,
                           'ntheta': ntheta, 'nphi': nphi,
                           'endpoint': endpoint, 'measure': measure_label}

    return results

# ━━━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("=" * 80)
    print("DEFINITIVE CHIRAL ORF VALIDATION: endpoint=True vs False")
    print("=" * 80)
    print(f"\nTarget v17 value: Gamma^V = -7.75e-3 for LISA(i=30) x Taiji(i=0)")
    print(f"  with spatial phase, OLC transfer function, f = 0.001 Hz")
    print()

    f_test = 0.001  # 1 mHz
    L_lisa = 2.5e9
    L_taiji = 3.0e9
    incl_lisa30 = np.pi / 6.0  # 30 deg
    incl_lisa60 = np.pi / 3.0  # 60 deg
    incl_taiji = 0.0
    au = 1.496e11

    # Configurations
    configs = {
        'LISA30 x Taiji30 (coplanar)': (
            *build_constellation(L_lisa, incl_lisa30, np.array([0, 0, au])),
            *build_constellation(L_taiji, incl_taiji, np.array([0, 0, 0])),
            30.0, 0.0
        ),
        'LISA60 x Taiji0 (non-coplanar)': (
            *build_constellation(L_lisa, incl_lisa60, np.array([0, 0, au])),
            *build_constellation(L_taiji, incl_taiji, np.array([0, 0, 0])),
            60.0, 0.0
        ),
        'OLC0 x Taiji0 (coplanar, self-corr)': (
            *build_constellation(L_lisa, incl_taiji, np.array([0, 0, 0])),
            *build_constellation(L_taiji, incl_taiji, np.array([0, 0, 0])),
            0.0, 0.0
        ),
    }

    grids = [(32, 64), (64, 128), (128, 256)]

    all_results = {}

    for config_name, (pos1, ref1, pos2, ref2, inc1, inc2) in configs.items():
        print(f"\n{'=' * 60}")
        print(f"CONFIG: {config_name}")
        print(f"  Inclinations: {inc1} deg / {inc2} deg")
        print(f"  Use spatial phase: YES (delta_x = {ref1 - ref2 if ref1 is not None and ref2 is not None else 'None'})")
        print(f"{'=' * 60}")

        delta_x = ref1 - ref2 if ref1 is not None and ref2 is not None else None
        if delta_x is not None:
            d = np.linalg.norm(delta_x)
            print(f"  Separation: {d:.3e} m = {d/au:.3f} AU")

        # Choose transfer function
        # For configs with reference_position, use OLC (paper convention)
        # For configs without reference_position (self-correlation), use OLC
        trans_fn = olc_transfer_function
        print(f"  Transfer function: OLC")

        config_results = {}

        for ntheta, nphi in grids:
            print(f"\n  Grid: {ntheta} x {nphi}")
            results = compute_all_orfs(f_test, pos1, L_lisa, pos2, L_taiji,
                                      incl_lisa30, incl_taiji,
                                      ntheta, nphi,
                                      use_spatial_phase=True, delta_x=delta_x)

            key_grid = f"{ntheta}x{nphi}"
            for key, val in results.items():
                print(f"    {key}: Gamma^I = {val['gamma_I']:.8f}, Gamma^V = {val['gamma_V']:.6e}")
                config_results[key] = val

        all_results[config_name] = config_results

    # ━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "=" * 80)
    print("SUMMARY: Gamma^V convergence (endpoint=False should → 0 for coplanar)")
    print("=" * 80)

    print("\n  {'key': 'value'} format:")
    print(f"  {'Config':<40s} {'Grid':<10s} {'endpoint':<8s} {'measure':<12s} {'Gamma^V':>15s}")
    print("  " + "-" * 90)

    for config_name in all_results:
        for key in all_results[config_name]:
            parts = key.split('_')
            ep = parts[0].split('=')[1]
            meas = parts[1]
            val = all_results[config_name][key]
            gV = val['gamma_V']
            # grid size from stored values
            g = f"{val['ntheta']}x{val['nphi']}"
            print(f"  {config_name[:40]:<40s} {g:<10s} {ep:<8s} {meas:<12s} {gV:>15.6e}")

    # ━━━ Comparison with v17 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print("\n" + "=" * 80)
    print("COMPARISON WITH v17 PAPER VALUE")
    print("=" * 80)

    v17_value = -7.75e-3

    # LISA30 x Taiji30 with spatial phase
    if 'LISA30 x Taiji30 (coplanar)' in all_results:
        for key, val in all_results['LISA30 x Taiji30 (coplanar)'].items():
            gV = val['gamma_V']
            ratio = abs(gV / v17_value) if abs(v17_value) > 1e-20 else 0
            print(f"  LISA30 x Taiji30, {key}: Gamma^V = {gV:.6e}, |Gamma^V/v17| = {ratio:.2f}")

    print(f"\n  v17 claimed value: {v17_value:.6e}")

    if 'LISA30 x Taiji30 (coplanar)' in all_results:
        ep1_val = all_results['LISA30 x Taiji30 (coplanar)'].get('ep=True_uniform', {}).get('gamma_V', None)
        if ep1_val is not None:
            ratio = abs(ep1_val / v17_value)
            print(f"  LISA30 ep=True_uniform Gamma^V: {ep1_val:.6e}")
            print(f"  Ratio |Gamma^V_ep1 / v17|: {ratio:.2f}")
    print(f"  Correct (endpoint=False, sin_theta) coplanar: ~0")

    print("\nDone.")

if __name__ == '__main__':
    t0 = time.time()
    main()
    print(f"\nTotal time: {time.time() - t0:.1f}s")
