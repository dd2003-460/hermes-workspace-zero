#!/usr/bin/env python3
"""
Diagnostic: compare OLC vs Michelson transfer function for chiral ORF.
Also test with and without spatial phase for each.

Key questions:
1. Does Michelson give a different Gamma^V than OLC?
2. Does spatial phase affect Gamma^V at low frequency?
3. Can we reproduce v17's -7.75e-3 with any combination?
"""
import numpy as np
import time

c = 299792458.0

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
    beta = np.pi * np.abs(f) * L / c
    sinc_val = np.where(np.abs(beta) < 1e-15, 1.0, np.sin(beta) / beta)
    phase = np.exp(-1j * beta)
    return sinc_val * phase

def antenna_pattern_cw_sum(tG, pG, positions, L, trans_fn):
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
        T = trans_fn(np.ones_like(tG), L, cos_nu)

        R_plus += F_plus * T
        R_cross += F_cross * T

    return R_plus, R_cross

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
    k_hat = np.array([
        np.sin(TG)*np.cos(PG),
        np.sin(TG)*np.sin(PG),
        np.cos(TG)
    ])
    delta_x_exp = delta_x.reshape(3, 1, 1)
    k_dot_delta = np.sum(k_hat * delta_x_exp, axis=0)
    omega = 2.0 * np.pi * np.asarray(f)
    return np.exp(-1j * omega / c * k_dot_delta)

def compute_orf_positions(R1p, R1x, R2p, R2x, phase, TG, PG):
    """Compute Gamma^I and Gamma^V with proper sin(theta) measure."""
    ntheta = len(TG)
    nphi = len(TG[0])
    dtheta = np.pi / (ntheta - 1)
    dphi = 2.0 * np.pi / nphi
    dOmega = np.sin(TG) * dtheta * dphi

    cross_corr = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
    chiral_corr = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)

    gamma_I = np.sum(phase * cross_corr * dOmega) / (4.0 * np.pi)
    gamma_V = np.sum(phase * chiral_corr * dOmega) / (4.0 * np.pi)

    # Also compute auto-responses for normalization
    S_A = np.sum(np.real(np.conj(R1p)*R1p + np.conj(R1x)*R1x) * dOmega) / (4.0 * np.pi)
    S_B = np.sum(np.real(np.conj(R2p)*R2p + np.conj(R2x)*R2x) * dOmega) / (4.0 * np.pi)

    return gamma_I, gamma_V, S_A, S_B

def run_test(f, trans_fn_name, trans_fn, incl1_deg, incl2_deg,
             use_sp, delta_x, ntheta=128, nphi=256):
    """Run one configuration and return Gamma^I, Gamma^V, R^V."""
    incl1 = np.radians(incl1_deg)
    incl2 = np.radians(incl2_deg)

    pos1 = build_constellation(2.5e9, incl1)
    pos2 = build_constellation(3.0e9, incl2)

    if delta_x is not None:
        pos2 = pos2 + delta_x

    tG = np.linspace(0, np.pi, ntheta, endpoint=False)
    pG = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    TG, PG = np.meshgrid(tG, pG, indexing='ij')

    R1p, R1x = antenna_pattern_cw_sum(TG, PG, pos1, 2.5e9, trans_fn)
    R2p, R2x = antenna_pattern_cw_sum(TG, PG, pos2, 3.0e9, trans_fn)

    if use_sp and delta_x is not None:
        ph = spatial_phase(f, delta_x, TG, PG)
    else:
        ph = np.ones_like(TG)

    gamma_I, gamma_V, S_A, S_B = compute_orf_positions(R1p, R1x, R2p, R2x, ph, TG, PG)

    rv = gamma_V / np.sqrt(S_A * S_B) if S_A > 0 and S_B > 0 else 0

    return {
        'gamma_I': gamma_I,
        'gamma_V': gamma_V,
        'S_A': S_A,
        'S_B': S_B,
        'R_V': rv,
    }

def main():
    print("=" * 90)
    print("DIAGNOSTIC: OLC vs Michelson, with/without SP")
    print("=" * 90)

    f = 0.001  # 1 mHz
    au = 1.496e11
    delta_x = np.array([0, 0, au])

    configs = [
        ('LISA0 x Taiji0', 0.0, 0.0),
        ('LISA30 x Taiji0', 30.0, 0.0),
        ('LISA60 x Taiji0', 60.0, 0.0),
    ]

    trans_fns = [
        ('OLC', olc_transfer_function),
        ('Michelson', michelson_transfer_function),
    ]

    print("\nKey: (use_sp) = spatial phase, no_sp = no spatial phase")
    print(f"v17 claimed value: Gamma^V = -7.75e-3")
    print()

    for tf_name, tf_fn in trans_fns:
        print(f"\n{'=' * 90}")
        print(f"Transfer function: {tf_name}")
        print(f"{'=' * 90}")

        for cfg_name, inc1, inc2 in configs:
            print(f"\n  Config: {cfg_name} (incl1={inc1:.0f}° incl2={inc2:.0f}°)")

            for use_sp_name, use_sp in [('with_SP', True), ('without_SP', False)]:
                result = run_test(f, tf_name, tf_fn, inc1, inc2, use_sp,
                                delta_x if use_sp else None, ntheta=128, nphi=256)

                gI = result['gamma_I']
                gV = result['gamma_V']
                rv = result['R_V']

                print(f"    {use_sp_name:<12s}: Gamma^I = {gI:.6f}, Gamma^V = {gV:.8e}, R^V = {rv:.6e}")

    print("\n" + "=" * 90)
    print("FREQUENCY SCAN: OLC with SP, LISA30 x Taiji0")
    print("=" * 90)
    print(f"  {'f (Hz)':<15s} {'Gamma^I':<15s} {'Gamma^V':<15s} {'R^V':<15s}")
    print("  " + "-" * 60)
    for freq in [0.001, 0.01, 0.1]:
        result = run_test(freq, 'OLC', olc_transfer_function, 30.0, 0.0,
                         True, delta_x, ntheta=128, nphi=256)
        print(f"  {freq:<15.3f} {result['gamma_I']:<15.6f} {result['gamma_V']:<15.6e} {result['R_V']:<15.6e}")

    print("\nDone.")

if __name__ == '__main__':
    t0 = time.time()
    main()
    print(f"\nTotal time: {time.time() - t0:.1f}s")
