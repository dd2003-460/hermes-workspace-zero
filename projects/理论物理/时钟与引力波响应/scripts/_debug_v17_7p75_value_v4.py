#!/usr/bin/env python3
"""
Diagnostic v4: What specific formula produces -7.750753e-3?

v3 showed:
- CW sum + OLC TF gives R^V_single = -0.141 at v17's direction (factor 18 off)
- Single-link gives R^V = 0 (chiral needs 3-link CW sum)
- Gamma^V_sky_avg ≈ 0 at f=0.001 (symmetry cancels)

Hypothesis: v17 computed the chiral correlation WITHOUT CW sum —
just the product of single-arm antenna patterns.
Or: v17 computed with only 2 links (bypass link).
Or: v17 defined R^V differently (e.g., with spatial phase factor).
"""
import numpy as np
import time

c = 299792458.0

def olc_tf(f, L, cos_nu):
    beta = np.pi * f * L / c
    sinc_arg = beta * (1.0 - cos_nu)
    eps = 1e-10
    sinc_v = np.where(np.abs(sinc_arg) < eps, 1.0, np.sin(sinc_arg) / sinc_arg)
    phase = np.exp(-1j * beta * (1.0 - cos_nu))
    prefac = 1j * 2.0 * np.pi * f * L / c
    return prefac * sinc_v * phase

def build_triangle(L, incl):
    r1 = np.array([0.0, 0.0, 0.0])
    r2 = np.array([L, 0.0, 0.0])
    r3 = np.array([L/2, L*np.sqrt(3)/2, 0.0])
    pos = np.array([r1, r2, r3])
    ci, si = np.cos(incl), np.sin(incl)
    rot = np.zeros_like(pos)
    rot[:, 0] = pos[:, 0]
    rot[:, 1] = pos[:, 1] * ci - pos[:, 2] * si
    rot[:, 2] = pos[:, 1] * si + pos[:, 2] * ci
    return rot

def antenna_patterns_single(TG, PG, positions, link_idx):
    """Compute antenna patterns for a single detector arm (not CW sum).

    link_idx: which arm of the detector (0, 1, or 2)
    Returns (F_plus, F_cross) for the arm.
    """
    nx = np.sin(TG) * np.cos(PG)
    ny = np.sin(TG) * np.sin(PG)
    nz = np.cos(TG)

    th = np.array([np.cos(TG)*np.cos(PG), np.cos(TG)*np.sin(PG), -np.sin(TG)])
    ph_vec = np.array([-np.sin(PG), np.cos(PG), 0.0])

    i, j = link_idx
    u = positions[j] - positions[i]
    u = u / np.linalg.norm(u)

    F_plus = (th[0]*u[0] + th[1]*u[1] + th[2]*u[2])**2 - \
             (ph_vec[0]*u[0] + ph_vec[1]*u[1] + ph_vec[2]*u[2])**2
    F_cross = 2.0 * (th[0]*u[0] + th[1]*u[1] + th[2]*u[2]) * \
                        (ph_vec[0]*u[0] + ph_vec[1]*u[1] + ph_vec[2]*u[2])
    return F_plus, F_cross

def cw_sum(TG, PG, positions, L, f, tf_fn):
    """Full CW sum with transfer function."""
    R_p, R_x = 0.0, 0.0
    for i, j in [(0,1), (1,2), (2,0)]:
        Fp, Fx = antenna_patterns_single(TG, PG, positions, (i,j))
        nx = np.sin(TG)*np.cos(PG)
        ny = np.sin(TG)*np.sin(PG)
        nz = np.cos(TG)
        u = positions[j] - positions[i]
        u = u / np.linalg.norm(u)
        cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
        T = tf_fn(f, L, cos_nu)
        R_p += Fp * T
        R_x += Fx * T
    return R_p, R_x

def chiral_R(R1p, R1x, R2p, R2x):
    d1 = np.sqrt(np.abs(R1p)**2 + np.abs(R1x)**2)
    d2 = np.sqrt(np.abs(R2p)**2 + np.abs(R2x)**2)
    chir = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)
    if d1*d2 > 1e-30:
        return chir / (d1*d2)
    return 0.0

def main():
    t0 = time.time()
    print("=" * 80)
    print("DIAGNOSTIC v4: Reverse-engineering -7.750753e-3")
    print("=" * 80)

    v17_th = np.radians(36.51)
    v17_ph = np.radians(82.58)
    L_lisa = 2.5e9
    L_taiji = 3.0e9
    f = 0.001

    pos1_30 = build_triangle(L_lisa, np.radians(30.0))
    pos2_0 = build_triangle(L_taiji, np.radians(0.0))

    print("\n=== A. Different response definitions ===")

    # 1. CW sum + OLC TF
    R1p, R1x = cw_sum(v17_th, v17_ph, pos1_30, L_lisa, f, olc_tf)
    R2p, R2x = cw_sum(v17_th, v17_ph, pos2_0, L_taiji, f, olc_tf)
    rv = chiral_R(R1p, R1x, R2p, R2x)
    print(f"  CW sum + OLC TF:        R^V = {rv:.6e}")

    # 2. CW sum, no TF (T=1)
    def id_tf(f, L, cn): return 1.0 + 0j
    R1p, R1x = cw_sum(v17_th, v17_ph, pos1_30, L_lisa, f, id_tf)
    R2p, R2x = cw_sum(v17_th, v17_ph, pos2_0, L_taiji, f, id_tf)
    rv = chiral_R(R1p, R1x, R2p, R2x)
    print(f"  CW sum + T=1:           R^V = {rv:.6e}")

    # 3. Single arm (link 0-1 only), with TF
    F1p, F1x = antenna_patterns_single(v17_th, v17_ph, pos1_30, (0,1))
    F2p, F2x = antenna_patterns_single(v17_th, v17_ph, pos2_0, (0,1))
    nx = np.sin(v17_th)*np.cos(v17_ph)
    ny = np.sin(v17_th)*np.sin(v17_ph)
    nz = np.cos(v17_th)
    u1 = pos1_30[1] - pos1_30[0]; u1 /= np.linalg.norm(u1)
    u2 = pos2_0[1] - pos2_0[0]; u2 /= np.linalg.norm(u2)
    T1 = olc_tf(f, L_lisa, nx*u1[0]+ny*u1[1]+nz*u1[2])
    T2 = olc_tf(f, L_taiji, nx*u2[0]+ny*u2[1]+nz*u2[2])
    rv = chiral_R(F1p*T1, F1x*T1, F2p*T2, F2x*T2)
    print(f"  Single arm + TF:        R^V = {rv:.6e}")

    # 4. Single arm, no TF
    rv = chiral_R(F1p, F1x, F2p, F2x)
    print(f"  Single arm + T=1:       R^V = {rv:.6e}")

    # 5. 2-link bypass (0-1 + 1-2), with TF
    def bypass_response(TG, PG, positions, L, f, tf_fn):
        R_p, R_x = 0.0, 0.0
        for i, j in [(0,1), (1,2)]:
            Fp, Fx = antenna_patterns_single(TG, PG, positions, (i,j))
            nx = np.sin(TG)*np.cos(PG)
            ny = np.sin(TG)*np.sin(PG)
            nz = np.cos(TG)
            u = positions[j] - positions[i]
            u = u / np.linalg.norm(u)
            cos_nu = nx*u[0] + ny*u[1] + nz*u[2]
            T = tf_fn(f, L, cos_nu)
            R_p += Fp * T
            R_x += Fx * T
        return R_p, R_x

    R1p, R1x = bypass_response(v17_th, v17_ph, pos1_30, L_lisa, f, olc_tf)
    R2p, R2x = bypass_response(v17_th, v17_ph, pos2_0, L_taiji, f, olc_tf)
    rv = chiral_R(R1p, R1x, R2p, R2x)
    print(f"  2-link bypass + TF:     R^V = {rv:.6e}")

    # 6. 2-link bypass, no TF
    R1p, R1x = bypass_response(v17_th, v17_ph, pos1_30, L_lisa, f, id_tf)
    R2p, R2x = bypass_response(v17_th, v17_ph, pos2_0, L_taiji, f, id_tf)
    rv = chiral_R(R1p, R1x, R2p, R2x)
    print(f"  2-link bypass + T=1:    R^V = {rv:.6e}")

    print("\n=== B. What if v17 used a different definition? ===")
    print("  Try: R^V = <F1p*F2x - F1x*F2p> / <F1p^2+F1x^2+F2p^2+F2x^2>")

    # Compute using only antenna patterns (no TF), over 3-link CW sum of F only
    def cw_sum_F(TG, PG, positions):
        R_p, R_x = 0.0, 0.0
        for i, j in [(0,1), (1,2), (2,0)]:
            Fp, Fx = antenna_patterns_single(TG, PG, positions, (i,j))
            R_p += Fp
            R_x += Fx
        return R_p, R_x

    R1p, R1x = cw_sum_F(v17_th, v17_ph, pos1_30)
    R2p, R2x = cw_sum_F(v17_th, v17_ph, pos2_0)
    rv = chiral_R(R1p, R1x, R2p, R2x)
    print(f"  CW sum F only:          R^V = {rv:.6e}")
    print(f"    R1p={R1p:.6e}, R1x={R1x:.6e}")
    print(f"    R2p={R2p:.6e}, R2x={R2x:.6e}")

    print("\n=== C. What if v17's value is the chiral correlation coefficient ===")
    print("  r = sum(chir_i * auto_i) / sqrt(sum(chir_i^2) * sum(auto_i^2))")

    # Let's try: the correlation coefficient of chiral vs auto across sky
    # This is essentially the Pearson correlation coefficient
    nsky = 1000
    thetas = np.random.random(nsky) * np.pi
    phis = np.random.random(nsky) * 2 * np.pi

    chirs = []
    autos = []
    for th, ph in zip(thetas, phis):
        R1p, R1x = cw_sum(th, ph, pos1_30, L_lisa, f, olc_tf)
        R2p, R2x = cw_sum(th, ph, pos2_0, L_taiji, f, olc_tf)
        chir = np.real(np.conj(R1p)*R2x - np.conj(R1x)*R2p)
        auto = np.real(np.conj(R1p)*R2p + np.conj(R1x)*R2x)
        chirs.append(chir)
        autos.append(auto)

    chirs = np.array(chirs)
    autos = np.array(autos)

    # Pearson correlation
    mean_c = np.mean(chirs)
    mean_a = np.mean(autos)
    r = np.sum((chirs - mean_c) * (autos - mean_a)) / \
        np.sqrt(np.sum((chirs - mean_c)**2) * np.sum((autos - mean_a)**2))
    print(f"  Pearson corr(chir, auto) = {r:.6e}")

    print("\n=== D. Search ALL sky directions for R^V ≈ -7.75e-3 ===")
    ngrid = 180
    TG = np.linspace(0, np.pi, ngrid, endpoint=False)
    PG = np.linspace(0, 2*np.pi, ngrid, endpoint=False)

    best_match = None
    best_dist = 1e9

    # Coarse scan first
    for it in range(0, ngrid, 3):
        for ip in range(0, ngrid, 3):
            th = TG[it]
            ph = PG[ip]
            R1p, R1x = cw_sum(th, ph, pos1_30, L_lisa, f, olc_tf)
            R2p, R2x = cw_sum(th, ph, pos2_0, L_taiji, f, olc_tf)
            rv = chiral_R(R1p, R1x, R2p, R2x)

            dist = abs(rv + 7.750753e-3)
            if dist < best_dist:
                best_dist = dist
                best_match = (th, ph, rv)

    th_best, ph_best, rv_best = best_match
    print(f"  Coarse best: theta={np.degrees(th_best):.1f}°, phi={np.degrees(ph_best):.1f}°, R^V={rv_best:.6e}")
    print(f"  Distance to target: {best_dist:.6e}")

    # Fine scan around best
    th_fine = np.linspace(max(0, np.degrees(th_best)-5), min(180, np.degrees(th_best)+5), 200) * np.pi/180
    ph_fine = np.linspace(max(0, np.degrees(ph_best)-5), min(360, np.degrees(ph_best)+5), 200) * np.pi/180
    for th in th_fine:
        for ph in ph_fine:
            R1p, R1x = cw_sum(th, ph, pos1_30, L_lisa, f, olc_tf)
            R2p, R2x = cw_sum(th, ph, pos2_0, L_taiji, f, olc_tf)
            rv = chiral_R(R1p, R1x, R2p, R2x)
            dist = abs(rv + 7.750753e-3)
            if dist < best_dist:
                best_dist = dist
                best_match = (th, ph, rv)

    th_best, ph_best, rv_best = best_match
    print(f"  Fine best:   theta={np.degrees(th_best):.2f}°, phi={np.degrees(ph_best):.2f}°, R^V={rv_best:.6e}")
    print(f"  Distance to target: {best_dist:.6e}")

    if best_dist < 1e-6:
        print(f"  >>> FOUND NEAR MATCH <<<")

    print("\n=== E. Compare with different inclination pairs ===")
    for inc1_deg in [0, 10, 20, 30, 45, 60, 90]:
        pos1_test = build_triangle(L_lisa, np.radians(inc1_deg))

        # Coarse search for best match
        best_rv_inc = None
        for th in np.linspace(0, np.pi, 60, endpoint=False):
            for ph in np.linspace(0, 2*np.pi, 120, endpoint=False):
                R1p, R1x = cw_sum(th, ph, pos1_test, L_lisa, f, olc_tf)
                R2p, R2x = cw_sum(th, ph, pos2_0, L_taiji, f, olc_tf)
                rv = chiral_R(R1p, R1x, R2p, R2x)
                if best_rv_inc is None or abs(rv + 7.750753e-3) < abs(best_rv_inc + 7.750753e-3):
                    best_rv_inc = rv

        print(f"  LISA(i={inc1_deg:2d}) x Taiji(i=0): best R^V = {best_rv_inc:.6e}")

    print(f"\n  TARGET: v17 claims R^V = -7.750753e-3 at theta=36.51, phi=82.58")
    total_time = time.time() - t0
    print(f"\nDone. Total time: {total_time:.1f}s")

if __name__ == '__main__':
    main()
