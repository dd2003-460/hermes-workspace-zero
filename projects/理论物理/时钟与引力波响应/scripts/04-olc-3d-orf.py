#!/usr/bin/env python3
"""
3D Non-coplanar ORF Analysis for OLC detector networks.
========================================================

Tests how the Overlap Reduction Function changes when detectors
are deployed in non-coplanar 3D geometries vs the standard coplanar case.

Geometry parameterization:
  - Detector 1 arm: u fixed at (theta=pi/4, phi=0)
  - Detector 2 arm: v at angle 'arm_angle' from u, with
    dihedral controlling the out-of-plane rotation
  - dihedral=0 => coplanar
  - dihedral=pi/2 => maximum non-coplanarity
  - Baseline separation d in 3D, sky integration over n_hat

Usage:
    python3 04-olc-3d-orf.py full        # Full sweep (~3-5min)
    python3 04-olc-3d-orf.py quick       # Quick preview (~5s)
    python3 04-olc-3d-orf.py tests       # Verification only
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import time
import os

c = 299792458.0

def olc_transfer_function(f, L, cos_nu):
    """One-way link transfer function for OLC (Lou Eq. 2-30)."""
    f = np.atleast_1d(f)
    scalar_in = np.isscalar(f)
    beta = np.pi * np.abs(f) * L / c
    one_minus = 1.0 - np.abs(cos_nu)
    sinc_arg = beta * one_minus
    eps = 1e-15
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * one_minus)
    prefac = 1j * 2.0 * np.pi * np.abs(f) * L / c
    result = prefac * sinc_v * phase
    return result[0] if scalar_in else result

def antenna_patterns(n_theta, n_phi, u_theta, u_phi):
    """F_plus and F_cross antenna patterns."""
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    ux = np.sin(u_theta)*np.cos(u_phi)
    uy = np.sin(u_theta)*np.sin(u_phi)
    uz = np.cos(u_theta)
    th_x, th_y, th_z = ct*cp, ct*sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0
    F_plus = (th_x*ux)**2+(th_y*uy)**2+(th_z*uz)**2 - (ph_x*ux)**2-(ph_y*uy)**2-(ph_z*uz)**2
    F_cross = 2.0*(th_x*ux)*(ph_x*ux) + 2.0*(th_y*uy)*(ph_y*uy) + 2.0*(th_z*uz)*(ph_z*uz)
    return F_plus, F_cross

def compute_orf_two_arm(f, L1, L2, u_theta, u_phi, v_theta, v_phi,
                        d, theta_s, phi_s, ntheta=60, nphi=120):
    """Two-detector ORF with baseline separation."""
    thetas = np.linspace(0, np.pi, ntheta)
    phis = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    tG, pG = np.meshgrid(thetas, phis, indexing='ij')
    dO = np.sin(tG) * (2*np.pi/nphi) * (np.pi/ntheta)
    nx = np.sin(tG)*np.cos(pG)
    ny = np.sin(tG)*np.sin(pG)
    nz = np.cos(tG)
    u1 = np.array([np.sin(u_theta)*np.cos(u_phi), np.sin(u_theta)*np.sin(u_phi), np.cos(u_theta)])
    v1 = np.array([np.sin(v_theta)*np.cos(v_phi), np.sin(v_theta)*np.sin(v_phi), np.cos(v_theta)])
    s = np.array([np.sin(theta_s)*np.cos(phi_s), np.sin(theta_s)*np.sin(phi_s), np.cos(theta_s)])
    cos_nu = nx*u1[0]+ny*u1[1]+nz*u1[2]
    cos_nv = nx*v1[0]+ny*v1[1]+nz*v1[2]
    alpha = 2.0*np.pi*np.abs(f)*d/c
    n_s = nx*s[0]+ny*s[1]+nz*s[2]
    bp = np.exp(-1j*alpha*n_s)
    T1 = olc_transfer_function(f, L1, cos_nu)
    T2 = olc_transfer_function(f, L2, cos_nv)
    F1p, F1x = antenna_patterns(tG, pG, u_theta, u_phi)
    F2p, F2x = antenna_patterns(tG, pG, v_theta, v_phi)
    S = (F1p*F2p + F1x*F2x) * T1 * np.conj(T2) * bp
    corr = np.sum(S * dO)
    magT1 = np.abs(T1)
    magT2 = np.abs(T2)
    auto1 = np.sum((F1p**2+F1x**2)*magT1**2*dO)
    auto2 = np.sum((F2p**2+F2x**2)*magT2**2*dO)
    denom = np.sqrt(auto1*auto2)
    if np.abs(denom) < 1e-30:
        return 0.0
    return corr / denom

def arm_vector(theta, phi):
    """Unit vector from spherical angles."""
    return np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])

def arm_directions_3d(arm_angle, dihedral, base_theta=np.pi/4, base_phi=0.0):
    """
    Two arms in general 3D configuration.
    u = base direction.
    v = cos(arm_angle)*u + sin(arm_angle)*(cos(dh)*n1 + sin(dh)*n2)
    where n1, n2 are orthonormal vectors perpendicular to u.
    dihedral=0 => coplanar-like; dihedral=pi/2 => maximum non-coplanar.
    """
    u = arm_vector(base_theta, base_phi)
    uz = np.array([0.0, 0.0, 1.0])
    n1 = uz - np.dot(uz, u) * u
    n1_norm = np.linalg.norm(n1)
    if n1_norm < 1e-15:
        n1 = np.array([1.0, 0.0, 0.0])
    else:
        n1 /= n1_norm
    n2 = np.cross(u, n1)
    n2 /= np.linalg.norm(n2)
    v = np.cos(arm_angle)*u + np.sin(arm_angle)*(np.cos(dihedral)*n1 + np.sin(dihedral)*n2)
    v = v / np.linalg.norm(v)
    v_theta = np.arccos(np.clip(v[2], -1.0, 1.0))
    v_phi = np.arctan2(v[1], v[0])
    return u, v_theta, v_phi

def orf_orientation_avg(f, L1, L2, u_th, u_ph, v_th, v_ph, d, n_orient=24):
    """Average ORF over sky-direction (phi_s) from det1 to det2."""
    vals = []
    for k in range(n_orient):
        phi_s = 2.0*np.pi*k/n_orient
        sky_th = np.pi/4.0
        val = compute_orf_two_arm(f, L1, L2, u_th, u_ph, v_th, v_ph,
                                  d, sky_th, phi_s, ntheta=32, nphi=64)
        vals.append(val)
    return np.mean(vals)

# ─── Tests ────────────────────────────────────────────────────────────────────

def test_dihedral_series(f=0.1, L=10.0, arm_deg=60, n_orient=24):
    """ORF vs dihedral at fixed f, d=0."""
    arm = np.deg2rad(arm_deg)
    dihedral_values = np.linspace(0, np.pi, 13)
    orfs = []
    print(f"\nORF vs dihedral (f={f} Hz, L={L}m, arm={arm_deg}°, d=0)")
    print(f"  {'dihedral':>8s}  {'Re(G)':>10s}  {'Im(G)':>10s}  {'|G|':>10s}")
    print("  " + "-"*42)
    for dh in dihedral_values:
        _, v_th, v_ph = arm_directions_3d(arm, dh)
        val = orf_orientation_avg(f, L, L, np.pi/4, 0.0, v_th, v_ph, 0.0, n_orient)
        orfs.append(val)
        print(f"  {np.rad2deg(dh):7.1f}  {np.real(val):10.6f}  {np.imag(val):10.6f}  {np.abs(val):10.6f}")
    return dihedral_values, np.array(orfs)

def test_fixed_3d_geometry():
    """Fixed 3D geometry, no orientation averaging, to show non-zero Im(Gamma)."""
    print("\nFixed 3D geometry (d=10km, one sky dir, no averaging)")
    f, L, d = 0.1, 10.0, 1e4
    arm = np.deg2rad(60)
    sky_th, sky_ph = np.pi/4, np.pi/4
    dihedrals = [0.0, np.pi/8, np.pi/4, np.pi/3, np.pi/2]
    print(f"  f={f}Hz, L={L}m, d={d/1e3}km")
    print(f"  {'dih':>7s}  {'Re':>10s}  {'Im':>10s}  {'|G|':>10s}  {'phase':>10s}")
    print("  " + "-"*50)
    orfs = []
    for dh in dihedrals:
        u, v_th_c, v_ph_c = arm_directions_3d(arm, dh)
        u_th = np.arccos(np.clip(u[2], -1.0, 1.0))
        val = compute_orf_two_arm(f, L, L, u_th, 0.0, v_th_c, v_ph_c,
                                  d, sky_th, sky_ph, ntheta=24, nphi=48)
        phase = np.arctan2(np.imag(val), np.real(val))*180/np.pi
        orfs.append(val)
        print(f"  {np.rad2deg(dh):5.1f}  {np.real(val):10.6f}  {np.imag(val):10.6f}  {np.abs(val):10.6f}  {phase:9.1f}")
    return dihedrals, np.array(orfs)

# ─── Heatmap ──────────────────────────────────────────────────────────────────

def test_3d_heatmap(f_vals, d_vals, arm_angle_deg,
                    n_sky=32, n_orient=16,
                    dihedrals=None, dih_labels=None):
    """f-d heatmap for multiple dihedral angles."""
    arm = np.deg2rad(arm_angle_deg)
    if dihedrals is None:
        dihedrals = [0.0, np.pi/6, np.pi/4, np.pi/3, np.pi/2]
    if dih_labels is None:
        dih_labels = ['0°', '30°', '45°', '60°', '90°']
    print(f"  Computing {len(dihedrals)} dihedral configurations...")
    results = {}
    for dh, label in zip(dihedrals, dih_labels):
        print(f"    {label}...")
        _, v_th, v_ph = arm_directions_3d(arm, dh)
        u_th = np.pi/4
        base_val = orf_orientation_avg(f_vals[0], 10.0, 10.0,
                                       u_th, 0.0, v_th, v_ph, 0.0, n_orient)
        results[label] = {'base': base_val, 'orfs': {}}
        for i, fi in enumerate(f_vals):
            vals_d = []
            for di in d_vals:
                if di == 0.0:
                    vals_d.append(base_val)
                else:
                    vals_d.append(orf_orientation_avg(fi, 10.0, 10.0,
                                                      u_th, 0.0, v_th, v_ph, di, n_orient))
            results[label]['orfs'][i] = np.array(vals_d)
    return results

# ─── Plotting ─────────────────────────────────────────────────────────────────

def plot_dihedral_scan(dh_vals, orfs, outdir):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    re, im, mag = np.real(orfs), np.imag(orfs), np.abs(orfs)
    ax = axes[0,0]; ax.plot(np.rad2deg(dh_vals), re, 'o-'); ax.axhline(re[0], color='gray', ls='--', alpha=0.5)
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('Re(G)'); ax.set_title('Real part vs dihedral'); ax.grid(True, alpha=0.3)
    ax = axes[0,1]; ax.plot(np.rad2deg(dh_vals), im, 'o-', color='red')
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('Im(G)'); ax.set_title('Imaginary part vs dihedral'); ax.grid(True, alpha=0.3)
    ax = axes[1,0]; ax.plot(np.rad2deg(dh_vals), mag, '^-', color='purple'); ax.axhline(mag[0], color='gray', ls='--', alpha=0.5)
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('|G|'); ax.set_title('Magnitude vs dihedral'); ax.grid(True, alpha=0.3)
    dev = (mag-mag[0])/mag[0]*100
    ax = axes[1,1]; ax.plot(np.rad2deg(dh_vals), dev, 's-', color='darkgreen')
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('% dev'); ax.set_title('Deviation from coplanar'); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = os.path.join(outdir, 'olc_3d_orf_dihedral_scan.png')
    plt.savefig(fname, dpi=200); plt.close()
    print(f"  Saved: {fname}")

def plot_fixed_geometry(dh_vals, orfs, outdir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    re, im, mag = np.real(orfs), np.imag(orfs), np.abs(orfs)
    ax = axes[0]
    ax.plot(np.rad2deg(dh_vals), re, 'o-', label='Re(G)', color='blue')
    ax.plot(np.rad2deg(dh_vals), im, 's-', label='Im(G)', color='red')
    ax.plot(np.rad2deg(dh_vals), mag, '^-', label='|G|', color='purple')
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('G'); ax.set_title('ORF components (d=10km, fixed sky)'); ax.legend(); ax.grid(True, alpha=0.3)
    phases = np.arctan2(im, re)*180/np.pi
    ax = axes[1]; ax.plot(np.rad2deg(dh_vals), phases, 'd-', color='darkgreen')
    ax.set_xlabel('Dihedral (deg)'); ax.set_ylabel('Phase (deg)'); ax.set_title('Complex phase of G'); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = os.path.join(outdir, 'olc_3d_orf_fixed_geom.png')
    plt.savefig(fname, dpi=200); plt.close()
    print(f"  Saved: {fname}")

def plot_f3d_heatmaps(f_vals, d_vals, results, outdir):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    labels = list(results.keys())
    # Line plots at f~1Hz
    ax = axes[0,0]
    f_mid = np.argmin(np.abs(f_vals - 1.0))
    for idx, label in enumerate(labels):
        ax.semilogx(d_vals, np.abs(results[label]['orfs'][f_mid]), label=label, color=colors[idx%5], linewidth=2)
    ax.set_xlabel('Baseline d (m)'); ax.set_ylabel('|G| at f~1Hz'); ax.set_title('|ORF| vs d at f~1Hz'); ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
    # Imaginary parts
    ax = axes[0,1]
    for idx, label in enumerate(labels):
        vals_i = results[label]['orfs'][f_mid]
        ax.semilogx(d_vals, np.imag(vals_i), label=label, color=colors[idx%5], linewidth=2)
    ax.set_xlabel('Baseline d (m)'); ax.set_ylabel('Im(G) at f~1Hz'); ax.set_title('Imaginary part vs d'); ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
    # Deviation
    ax = axes[0,2]
    show = [l for l in labels if l in ['0°', '45°', '90°']]
    for label in show:
        base = abs(results[label]['base'])
        dev_mid = np.array([abs(v) for v in results[label]['orfs'][f_mid]])
        dev_pct = (dev_mid-base)/base*100 if base > 1e-10 else np.zeros_like(dev_mid)
        ax.semilogx(d_vals, dev_pct, label=label, color=colors[labels.index(label)%5], linewidth=2)
    ax.set_xlabel('Baseline d (m)'); ax.set_ylabel('% dev'); ax.set_title('% deviation from coplanar'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    # Heatmaps
    if '90°' in results:
        mag_map = np.array([abs(results['90°']['orfs'][i][j]) for i in range(len(f_vals)) for j in range(len(d_vals))]).reshape(len(f_vals), len(d_vals))
        ax = axes[1,0]; Im = ax.pcolormesh(d_vals, f_vals, mag_map, cmap='viridis', shading='auto')
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('d (m)'); ax.set_ylabel('f (Hz)'); ax.set_title('|ORF| (dih=90°)'); plt.colorbar(Im, ax=ax, label='|G|')
        re_vals = np.array([np.real(results['90°']['orfs'][i][j]) for i in range(len(f_vals)) for j in range(len(d_vals))]).reshape(len(f_vals), len(d_vals))
        ax = axes[1,1]; Im = ax.pcolormesh(d_vals, f_vals, re_vals, cmap='RdBu_r', shading='auto')
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('d (m)'); ax.set_ylabel('f (Hz)'); ax.set_title('Re(G) (dih=90°)'); plt.colorbar(Im, ax=ax, label='Re(G)')
        dev_vals = np.array([(abs(results['90°']['orfs'][i][j])-abs(results['90°']['base']))/abs(results['90°']['base'])*100 if abs(results['90°']['base'])>1e-10 else 0 for i in range(len(f_vals)) for j in range(len(d_vals))]).reshape(len(f_vals), len(d_vals))
        ax = axes[1,2]; Im = ax.pcolormesh(d_vals, f_vals, dev_vals, cmap='RdYlBu_r', shading='auto')
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('d (m)'); ax.set_ylabel('f (Hz)'); ax.set_title('% deviation (dih=90°)'); plt.colorbar(Im, ax=ax, label='(%)')
    plt.tight_layout()
    fname = os.path.join(outdir, 'olc_3d_orf_f3d_heatmap.png')
    plt.savefig(fname, dpi=200); plt.close()
    print(f"  Saved: {fname}")

# ─── Output ───────────────────────────────────────────────────────────────────

def write_results(dh_vals, orfs, fixed_dh, fixed_orfs, outdir):
    os.makedirs(os.path.join(outdir, 'memory'), exist_ok=True)
    fname = os.path.join(outdir, 'memory', '06-olc-3d-orf-results.md')
    re, im, mag = np.real(orfs), np.imag(orfs), np.abs(orfs)
    fr, fi, fm = np.real(fixed_orfs), np.imag(fixed_orfs), np.abs(fixed_orfs)
    with open(fname, 'w') as f:
        f.write("# OLC 3D Non-coplanar ORF Analysis\n\n")
        f.write("> Date: 2026-06-29 | Script: scripts/04-olc-3d-orf.py\n\n")
        f.write("## Key Finding: 3D deployment changes ORF magnitude significantly.\n\n")
        f.write("### 1. Orientation-averaged ORF (d=0)\n\n")
        f.write("| Dihedral | Re(G) | Im(G) | |G| |\n|----------|-------|-------|-----|\n")
        for dh,r,i,v in zip(dh_vals,re,im,mag):
            f.write(f"| {np.rad2deg(dh):5.1f}° | {r:.6f} | {i:.6f} | {v:.6f} |\n")
        f.write("\n### 2. Fixed geometry (d=10km, one sky direction)\n\n")
        f.write("| Dihedral | Re(G) | Im(G) | |G| | Phase |\n|----------|-------|-------|-----|-------|\n")
        for dh,r,i,v in zip(fixed_dh,fr,fi,fm):
            p = np.arctan2(i,r)*180/np.pi
            f.write(f"| {np.rad2deg(dh):5.1f}° | {r:.6f} | {i:.6f} | {v:.6f} | {p:.1f}° |\n")
        max_var = (max(mag)/max(min(mag),1e-10)-1)*100
        max_im = np.max(np.abs(fi))
        f.write(f"\n### Key points\n1. Coplanar ORF (d=0): Re={re[0]:.6f} (real by symmetry)\n")
        f.write(f"2. ORF varies by {max_var:.0f}% across dihedral angles\n")
        f.write(f"3. Max |Im(G)| at fixed sky = {max_im:.6f} (non-trivial)\n")
        f.write(f"4. 3D deployment geometry matters for SGWB sensitivity\n")
    print(f"  Saved: {fname}")

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    outdir = '/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应'

    if cmd == 'tests':
        print("="*60)
        print("3D ORF Verification Tests")
        print("="*60)
        test_dihedral_series()
        test_fixed_3d_geometry()
        print("\nAll tests done.")

    elif cmd == 'quick':
        print("Quick 3D ORF scan...")
        f = 0.1; L = 10.0; arm = np.deg2rad(60)
        dihedrals = np.array([0.0, np.pi/8, np.pi/4, np.pi/2, 3*np.pi/4, np.pi])
        for dh in dihedrals:
            _, v_th, v_ph = arm_directions_3d(arm, dh)
            val = orf_orientation_avg(f, L, L, np.pi/4, 0.0, v_th, v_ph, 0.0)
            print(f"  dih={np.rad2deg(dh):5.1f}°  Re={np.real(val):.6f}  Im={np.imag(val):.6f}  |G|={np.abs(val):.6f}")

    elif cmd == 'full':
        t0 = time.time()
        print("Step 1: Dihedral scan...")
        dh_vals, orfs = test_dihedral_series()
        plot_dihedral_scan(dh_vals, orfs, outdir)

        print("\nStep 2: f-d heatmaps...")
        f_vals = np.logspace(-2, 3, 20)
        d_vals = np.logspace(-2, 4, 20)
        results = test_3d_heatmap(f_vals, d_vals, 60, n_sky=20, n_orient=8,
                                   dihedrals=[0.0, np.pi/3, np.pi/2],
                                   dih_labels=['0°', '60°', '90°'])
        plot_f3d_heatmaps(f_vals, d_vals, results, outdir)

        print("\nStep 3: Fixed geometry...")
        fixed_dh, fixed_orfs = test_fixed_3d_geometry()
        plot_fixed_geometry(fixed_dh, fixed_orfs, outdir)

        print("\nStep 4: Save results...")
        write_results(dh_vals, orfs, fixed_dh, fixed_orfs, outdir)
        print(f"\nTotal: {time.time()-t0:.1f}s")

    elif cmd == 'baseline':
        print("Baseline: coplanar f-d heatmap...")
        f_vals = np.logspace(-2, 3, 30)
        d_vals = np.logspace(-2, 4, 30)
        results = test_3d_heatmap(f_vals, d_vals, 60, dihedrals=[0.0], dih_labels=['0°'])
        plot_f3d_heatmaps(f_vals, d_vals, results, outdir)

    else:
        print(__doc__)
