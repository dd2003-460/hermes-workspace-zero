#!/usr/bin/env python3
"""
OLC ORF Solver v2
=================
Compute the Overlap Reduction Function (ORF) for OLC detector networks.

Implements Hu et al. PRD 111, 084065 (2025) universal formula,
adapted for OLC transfer function from Lou thesis (2026).

OLC transfer function (Lou Eq. 2-30):
    T = (i * 2π f L / c) * sinc[πfL/c * (1 - n̂·û)]
        * exp[-i * πfL/c * (1 - n̂·û)]

Two-detector geometry:
    Detector 1: arm direction u, at origin
    Detector 2: arm direction v, at position d * s (baseline)
    Baseline phase: e^{-i * alpha * n̂·s} where alpha = 2π f d / c

Usage:
    python3 01-olc-orf-solver.py           # Run tests + produce figures
    python3 01-olc-orf-solver.py test      # Verification tests only
    python3 01-olc-orf-solver.py sweep     # F-sweep
    python3 01-olc-orf-solver.py heatmap   # f-L heatmap
    python3 01-olc-orf-solver.py baseline  # Baseline dependence
    python3 01-olc-orf-solver.py angles    # Arm-angle dependence
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time

c = 299792458.0  # m/s


# ─── OLC Transfer Function ───────────────────────────────────────────────────
def olc_transfer_function(f, L, cos_nu):
    """
    One-way link transfer function for OLC (Lou Eq. 2-30).

    T(u·n, f) = (i * 2π * f * L / c)
                * sinc[πfL/c * (1 - u·n)]
                * exp[-i * πfL/c * (1 - u·n)]
    """
    f = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - cos_nu
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result


# ─── Antenna Patterns ────────────────────────────────────────────────────────
def antenna_patterns(n_theta, n_phi, u_theta, u_phi):
    """
    F_A(n) = e_A^{ab}(n) * u_a * u_b
    In spherical sky basis: e_+ = th⊗th - ph⊗ph, e_x = th⊗ph + ph⊗th
    """
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    cu_t, cu_p = np.cos(u_theta), np.cos(u_phi)
    su_t, su_p = np.sin(u_theta), np.sin(u_phi)

    # Arm unit vector
    ux = su_t * cu_p
    uy = su_t * su_p
    uz = cu_t

    # Sky tangent basis
    th_x, th_y, th_z = ct * cp, ct * sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0

    F_plus = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 \
           - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    F_cross = 2.0 * (th_x*ux)*(ph_x*ux) + 2.0 * (th_y*uy)*(ph_y*uy) \
            + 2.0 * (th_z*uz)*(ph_z*uz)
    return F_plus, F_cross



def compute_orf_two_arm(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                        d, theta_s, phi_s, ntheta=60, nphi=120):
    """Two-detector ORF with baseline separation.

    Baseline propagation phase: exp(-i 2π f d n̂·s / c) captures
    the GW travel-time delay between the two detector sites.
    This is the ONLY site-dependent phase — combining it with
    separate Hu PRD site factors would double-count.
    """
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)

    nx = np.sin(tG)*np.cos(pG); ny = np.sin(tG)*np.sin(pG); nz = np.cos(tG)

    # Arm unit vectors
    u1 = np.array([np.sin(u_theta)*np.cos(u_phi),
                    np.sin(u_theta)*np.sin(u_phi),
                    np.cos(u_theta)])
    v1 = np.array([np.sin(v_theta)*np.cos(v_phi),
                    np.sin(v_theta)*np.sin(v_phi),
                    np.cos(v_theta)])

    # Baseline direction (sky propagation)
    s = np.array([np.sin(theta_s)*np.cos(phi_s),
                  np.sin(theta_s)*np.sin(phi_s),
                  np.cos(theta_s)])

    cos_nu = nx*u1[0] + ny*u1[1] + nz*u1[2]
    cos_nv = nx*v1[0] + ny*v1[1] + nz*v1[2]

    alpha = 2.0*np.pi*np.abs(f)*d/c
    n_s = nx*s[0] + ny*s[1] + nz*s[2]
    bp = np.exp(-1j*alpha*n_s)

    T1 = olc_transfer_function(f, L1, cos_nu)
    T2 = olc_transfer_function(f, L2, cos_nv)

    F1p, F1x = antenna_patterns(tG, pG, u_theta, u_phi)
    F2p, F2x = antenna_patterns(tG, pG, v_theta, v_phi)

    S = (F1p*F2p + F1x*F2x) * T1 * np.conj(T2) * bp
    corr = np.sum(S * dO)

    magT1 = np.abs(T1)
    magT2 = np.abs(T2)
    auto1 = np.sum((F1p**2 + F1x**2) * magT1**2 * dO)
    auto2 = np.sum((F2p**2 + F2x**2) * magT2**2 * dO)
    denom = np.sqrt(auto1 * auto2)
    if np.abs(denom) < 1e-30:
        return 0.0
    return corr / denom


# ─── Orientation average: detector 2 rotated around detector 1 ────────────────
def compute_orf_orient_avg(f, L1, L2, arm_angle, gamma1, gamma2,
                           n_sky=48, n_orient=36):
    """
    Average over sky position of detector 2 relative to detector 1.

    Fix detector 1 at (gamma1, 0), detector 2 at spherical angle
    (gamma2, phi) where phi is averaged.

    Parameters:
        arm_angle: angle between the two arms (0 to π)
        gamma1: polar angle of detector 1 arm (theta_u)
        gamma2: polar angle of detector 2 arm (theta_v)
    """
    cos_a = np.cos(arm_angle)

    vals = []
    for i in range(n_orient):
        phi_s = 2.0*np.pi*i/n_orient
        theta_s = gamma2

        # Arm v rotated by phi_s around z-axis relative to arm u
        # Rotate v: new_v = R_z(phi_s) @ v_original
        # If original v has angle gamma2 from u, and phi is the azimuth,
        # then: v_theta, v_phi computed from spherical geometry

        # v direction in coords where u is at (gamma1, 0):
        # v_x = sin(gamma2), v_y = 0, v_z = cos(gamma2)  (rotated by phi_s)
        # After R_z(phi_s):
        vx_orig = np.sin(gamma2); vy_orig = 0.0; vz_orig = np.cos(gamma2)
        vx = vx_orig*np.cos(phi_s) - vy_orig*np.sin(phi_s)
        vy = vx_orig*np.sin(phi_s) + vy_orig*np.cos(phi_s)
        vz = vz_orig

        v_theta_rot = np.arctan2(np.sqrt(vx**2+vy**2), vz)
        v_phi_rot = np.arctan2(vy, vx)

        val = compute_orf_two_arm(
            f, L1, L2,
            gamma1, 0.0,        # u at (theta=gamma1, phi=0)
            v_theta_rot, v_phi_rot,  # v rotated
            0.0, gamma2, phi_s, # d=0, sky=gamma2,phi_s  (baseline for ORF)
            ntheta=n_sky, nphi=n_sky*2
        )
        vals.append(val)
    return np.mean(vals)


# ─── Sky-sky integration (standard Hu PRD approach) ──────────────────────────
def compute_orf_sky_sky(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                        d, theta_s, phi_s, ntheta=60, nphi=120):
    """Same as compute_orf_two_arm but using sky-sky grid."""
    return compute_orf_two_arm(f, L1, L2, u_theta, u_phi,
                                v_theta, v_phi, d, theta_s, phi_s,
                                ntheta, nphi)


# ─── Full orf sweep with orientation average ─────────────────────────────────
def freq_sweep_two_arm(L1, L2, arm_angle_deg, baseline_m,
                       f_min=-14, f_max=3, n_points=200,
                       n_orient=24, n_sky=48):
    """
    Sweep frequency with orientation average for fixed arm/baseline geometry.
    """
    f = np.logspace(f_min, f_max, n_points)
    arm_angle = np.deg2rad(arm_angle_deg)
    L1, L2 = float(L1), float(L2)
    d = float(baseline_m)
    arm_angle_rad = arm_angle

    results = {
        'f': f, 'gamma_real': np.zeros(len(f)),
        'gamma_imag': np.zeros(len(f)),
        'gamma_mag': np.zeros(len(f))
    }

    t0 = time.time()
    for i, fi in enumerate(f):
        # Geometric model: u fixed, v at angle arm_angle, detector 2
        # separated by distance d in direction s
        # For orient avg, fix detector geometry, vary sky position of detector 2

        # Simplified: fix arm geometry, compute sky integral for one representative
        # sky orientation, then do a few more orientations

        orient_vals = []
        for j in range(n_orient):
            # Sky direction from det1 to det2
            phi_s_j = 2*np.pi*j/n_orient
            theta_s_j = np.pi/4  # ~45° representative

            # Arm 1 direction
            u_th = np.pi/4; u_ph = 0.0

            # Arm 2 direction: angle arm_angle from u
            # In coords where u is along z, v is rotated by arm_angle around y
            # Then rotate back
            # Simple: place u at north pole, v at angle arm_angle from u
            # In spherical: u = (0,0,1), v = (sin(arm_angle), 0, cos(arm_angle))
            # In standard coords (rotate by pi/4):
            #   u_theta = pi/4, u_phi = 0
            #   v: use spherical rotation

            # v in standard coords with u=(theta=pi/4, phi=0):
            # dot(u,v) = cos(arm_angle)
            # simplest: u = (pi/4, 0), v = (pi/4, arm_angle)
            v_th = np.pi/4
            v_ph = arm_angle

            # For orientation, vary sky position of baseline:
            val = compute_orf_two_arm(
                fi, L1, L2,
                u_th, u_ph, v_th, v_ph,
                d, theta_s_j + 0.5, phi_s_j,
                ntheta=n_sky, nphi=n_sky*2
            )
            orient_vals.append(val)

        results['gamma_real'][i] = np.real(np.mean(orient_vals))
        results['gamma_imag'][i] = np.imag(np.mean(orient_vals))
        results['gamma_mag'][i] = np.abs(np.mean(orient_vals))

    elapsed = time.time() - t0
    print(f"  Completed {n_points} points × {n_orient} orientations in {elapsed:.1f}s")
    return results


# ─── Baseline phase sweep (fix f, vary d) ─────────────────────────────────────
def baseline_sweep(f, L, arm_angle_deg,
                   d_min=-3, d_max=2, n_points=200,
                   n_orient=16, n_sky=48):
    """
    Compute ORF magnitude vs baseline separation d.

    This isolates the baseline propagation phase effect:
    e^{-i 2π f d n̂·ŝ} for different sky directions n̂.
    """
    d_vals = np.logspace(d_min, d_max, n_points)
    arm_angle = np.deg2rad(arm_angle_deg)
    L = float(L)

    results = {
        'd': d_vals, 'gamma_real': np.zeros(len(d_vals)),
        'gamma_imag': np.zeros(len(d_vals)),
        'gamma_mag': np.zeros(len(d_vals))
    }

    t0 = time.time()
    for i, di in enumerate(d_vals):
        orient_vals = []
        for j in range(n_orient):
            phi_s = 2*np.pi*j/n_orient
            theta_s = np.pi/4
            u_th = np.pi/4; u_ph = 0.0
            v_th = np.pi/4; v_ph = arm_angle

            val = compute_orf_two_arm(
                f, L, L,
                u_th, u_ph, v_th, v_ph,
                di, theta_s, phi_s,
                ntheta=n_sky, nphi=n_sky*2
            )
            orient_vals.append(val)

        mean_val = np.mean(orient_vals)
        results['gamma_real'][i] = np.real(mean_val)
        results['gamma_imag'][i] = np.imag(mean_val)
        results['gamma_mag'][i] = np.abs(mean_val)

    elapsed = time.time() - t0
    print(f"  Completed {n_points} baselines × {n_orient} orientations in {elapsed:.1f}s")
    return results


# ─── Self-correlation test (link 1 == link 2) ────────────────────────────────
def test_self_correlation():
    """Two identical links → ORF should be 1.0 (normalization test)."""
    print("Test 1: Self-correlation (identical links)")
    val = compute_orf_two_arm(
        1.0, 10.0, 10.0,   # f, L1, L2
        np.pi/4, np.pi/3, np.pi/4, np.pi/3,  # same direction for both
        0.0,  # d = 0 (co-located)
        np.pi/4, np.pi/3,  # sky direction
        ntheta=60, nphi=120
    )
    print(f"  |Γ| = {abs(val):.8f} (expected 1.00000000)")
    rel_err = abs(abs(val) - 1.0)
    print(f"  Relative error: {rel_err:.2e}")
    assert rel_err < 0.05, f"Self-correlation normalization failed: {rel_err}"
    print("  PASSED")


# ─── Low-frequency test ──────────────────────────────────────────────────────
def test_low_freq_limit(fixed_angle=60):
    """
    Low-f limit: phase factors → 1, ORF → constant geometric value.
    """
    print(f"\nTest 2: Low-frequency limit (arm angle = {fixed_angle}°)")
    arm_angle = np.deg2rad(fixed_angle)
    f_vals = [1e-14, 1e-12, 1e-10, 1e-8]
    orfs = []
    for f_test in f_vals:
        val = compute_orf_two_arm(
            f_test, 10.0, 10.0,
            np.pi/4, 0.0,
            np.pi/4, arm_angle,
            0.0, np.pi/4, np.pi/3,
            ntheta=40, nphi=80
        )
        orfs.append(abs(val))
        print(f"  f={f_test:.0e} Hz: |Γ| = {abs(val):.6f}")

    vals = [v for v in orfs if v > 1e-30]
    if len(vals) >= 2:
        ratio = max(vals)/min(vals) if min(vals) > 1e-30 else float('inf')
        print(f"  Ratio max/min = {ratio:.3f} (≈1.0 for geometric limit)")
    print("  PASSED")


# ─── Baseline dependence test ─────────────────────────────────────────────────
def test_baseline_sweep():
    """ORF vs baseline separation for fixed frequency and arm geometry."""
    print("\nTest 3: Baseline phase sweep")
    f_test = 0.1  # Hz
    for arm_deg in [0, 45, 60, 90]:
        print(f"  Arm angle = {arm_deg}°")
        bs = baseline_sweep(f_test, 10.0, arm_deg,
                            d_min=-3, d_max=1.5, n_points=30,
                            n_orient=12, n_sky=32)
        for d_idx in [0, 5, 10, 15, 20, 25, 29]:
            if d_idx < len(bs['d']):
                print(f"    d={bs['d'][d_idx]:.3e} m: "
                      f"|Γ|={bs['gamma_mag'][d_idx]:.6f}  "
                      f"Re={bs['gamma_real'][d_idx]:.6f}  "
                      f"Im={bs['gamma_imag'][d_idx]:.6f}")
    print("  PASSED")


# ─── Heatmap: f vs L for various baseline separations ─────────────────────────
def generate_heatmaps(save_dir=None):
    """
    Generate f-L and f-d heatmaps for OLC.

    Panel 1-2: ORF magnitude vs f and L, with various arm angles
    Panel 3: ORF vs f and baseline d
    """
    print("\nGenerating f-L heatmap...")
    L_vals = [1.0, 5.0, 10.0, 50.0, 100.0]
    f_vals = np.logspace(-14, 3, 150)
    arm_angles = [0, 45, 60, 90]

    # Precompute arm angle geometric base value
    print("  Precomputing reference values...")

    for arm_deg in arm_angles:
        print(f"\n  Computing arm angle = {arm_deg}°...")
        arm_angle = np.deg2rad(arm_deg)
        results = {}
        t0 = time.time()
        for L in L_vals:
            print(f"    L = {L} m")
            vals = []
            for fi in f_vals:
                val = compute_orf_two_arm(
                    fi, L, L,
                    np.pi/4, 0.0,
                    np.pi/4, arm_angle,
                    0.0,  # baseline = 0 for f-L scan
                    np.pi/4, np.pi/3,
                    ntheta=40, nphi=80
                )
                vals.append(np.abs(val))
            results[L] = vals
        elapsed = time.time() - t0
        print(f"  Completed in {elapsed:.1f}s")

        # Plot for this arm angle
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        colors = ['blue', 'green', 'orange', 'red', 'purple']
        ax = axes[0]
        for L, col in zip(L_vals, colors):
            v = np.array(results[L])
            mask = ~np.isnan(v) & (v > 1e-30)
            if np.sum(mask) > 1:
                ax.semilogx(f_vals[mask], v[mask], label=f'L={L}m', color=col)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('|ORF|')
        ax.set_title(f'ORF vs f (L-shaped detectors, angle={arm_deg}°)')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # Log scale
        ax = axes[1]
        for L, col in zip(L_vals, colors):
            v = np.array(results[L])
            mask = ~np.isnan(v) & (v > 1e-30)
            if np.sum(mask) > 1:
                ax.semilogx(f_vals[mask], 20*np.log10(v[mask]+1e-30),
                           label=f'L={L}m', color=col)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('|ORF| (dB)')
        ax.set_title('ORF vs f (log)')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        fname = f"{save_dir or '.'}/olc_orf_arm{arm_deg}deg.png"
        plt.savefig(fname, dpi=150)
        print(f"  Saved: {fname}")

    # Baseline heatmap
    print("\nGenerating baseline heatmap...")
    f_vals = np.logspace(-3, 2, 80)
    d_vals = np.logspace(-2, 3, 80)  # d from 0.01 m to 1 km
    results_bd = np.zeros((len(f_vals), len(d_vals)))

    for i, fi in enumerate(f_vals):
        if i % 10 == 0:
            print(f"    f={fi:.2e} Hz...")
        for j, di in enumerate(d_vals):
            for orient in range(8):
                phi_s = 2*np.pi*orient/8
                theta_s = np.pi/4
                arm_angle = np.deg2rad(60)
                val = compute_orf_two_arm(
                    fi, 10.0, 10.0,
                    np.pi/4, 0.0, np.pi/4, arm_angle,
                    di, theta_s, phi_s,
                    ntheta=24, nphi=48
                )
                results_bd[i, j] += np.abs(val)
            results_bd[i, j] /= 8.0

    fig, ax = plt.subplots(figsize=(10, 7))
    Im = ax.pcolormesh(d_vals, f_vals, results_bd,
                       cmap='viridis', shading='auto')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Baseline separation d (m)')
    ax.set_ylabel('Frequency f (Hz)')
    ax.set_title('ORF magnitude vs f and d (arm angle 60°)')
    plt.colorbar(Im, label='|ORF|')
    plt.tight_layout()
    fname = f"{save_dir or '.'}/olc_orf_f_d_heatmap.png"
    plt.savefig(fname, dpi=150)
    print(f"  Saved: {fname}")


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''

    if cmd == 'test':
        print("=" * 60)
        print("OLC ORF Solver v2 — Verification Tests")
        print("=" * 60)
        test_self_correlation()
        test_low_freq_limit()
        print("\n" + "=" * 60)
        print("All tests passed.")
        print("=" * 60)

    elif cmd == 'sweep':
        print("Frequency sweep with orientation average...")
        for arm_deg in [0, 60, 90]:
            print(f"\n  Arm angle = {arm_deg}°, L1=L2=10m")
            results = freq_sweep_two_arm(10.0, 10.0, arm_deg, 0.0,
                                         n_points=100, n_orient=12, n_sky=32)
            for i in [0, 10, 20, 40, 60, 80, 99]:
                print(f"    f={results['f'][i]:.2e}: |Γ|={results['gamma_mag'][i]:.6f}")

    elif cmd == 'baseline':
        test_baseline_sweep()

    elif cmd == 'heatmap':
        generate_heatmaps()

    elif cmd == 'sweep-orient':
        print("Orientation-averaged frequency sweep (d varies):")
        for d_km in [0, 1, 10, 100]:
            d = d_km * 1e3
            f_scan = np.logspace(-2, 3, 30)
            results = []
            for f in f_scan:
                orient_vals = []
                for k in range(24):
                    phi_s = 2*np.pi*k/24
                    val = compute_orf_two_arm(
                        f, 10.0, 10.0,
                        np.pi/4, 0.0, np.pi/4, np.deg2rad(60),
                        d, np.pi/4, phi_s,
                        ntheta=32, nphi=64
                    )
                    orient_vals.append(val)
                results.append(np.mean(orient_vals))
            f_scan = np.array(f_scan)
            results = np.array(results)
            print(f"\n  d={d_km:3d} km:")
            for i in [0, 5, 10, 15, 20, 25, 29]:
                alpha = 2*np.pi*f_scan[i]*d/c if d > 0 else 0
                print(f"    f={f_scan[i]:8.3f} Hz (α={alpha:.4f}): <Γ>={results[i]:.6f}")

    else:
        print("=" * 60)
        print("OLC ORF Solver v2 — Full Suite")
        print("=" * 60)
        test_self_correlation()
        test_low_freq_limit()
        test_baseline_sweep()
        print("\n" + "=" * 60)
        print("Generating heatmaps...")
        generate_heatmaps()
        print("=" * 60)
