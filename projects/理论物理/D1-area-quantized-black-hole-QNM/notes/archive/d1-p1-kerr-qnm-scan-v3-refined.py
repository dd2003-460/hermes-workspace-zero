#!/usr/bin/env python3
"""
P1-v3-refined: Kerr QNM 边界扫描 (带三次多项式精确参考值)
===========================================================
改进点:
1. 文献值使用三次多项式拟合 (4个已知点精确插值) 替代线性外推
2. 扩展到 a=0.95
"""

import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time, os

print("=" * 70)
print("P1-v3-refined: Kerr QNM 边界扫描 (三次多项式参考值)")
print("=" * 70)

M = 1.0
a_vals = np.array([0.75, 0.80, 0.85, 0.90, 0.95])
n = 0
l_vals = [2, 3]

# Berti et al. 2009 exact data at a = 0, 0.5, 0.6, 0.7
a_exact = np.array([0.0, 0.5, 0.6, 0.7])
data_wR = {
    (2,2,0): [0.37367, 0.37414, 0.37439, 0.37471],
    (2,1,0): [0.37373, 0.37478, 0.37514, 0.37555],
    (2,0,0): [0.37373, 0.37428, 0.37451, 0.37479],
    (3,3,0): [0.59108, 0.59163, 0.59192, 0.59229],
    (3,2,0): [0.59146, 0.59230, 0.59269, 0.59319],
    (3,1,0): [0.59187, 0.59288, 0.59331, 0.59384],
    (3,0,0): [0.59231, 0.59343, 0.59390, 0.59447],
}
data_wI = {
    (2,2,0): [0.08896, 0.09332, 0.09535, 0.09784],
    (2,1,0): [0.08896, 0.09420, 0.09624, 0.09867],
    (2,0,0): [0.08896, 0.09079, 0.09157, 0.09254],
    (3,3,0): [0.05902, 0.06245, 0.06379, 0.06536],
    (3,2,0): [0.05916, 0.06261, 0.06395, 0.06553],
    (3,1,0): [0.05933, 0.06278, 0.06413, 0.06572],
    (3,0,0): [0.05952, 0.06297, 0.06433, 0.06593],
}

# Precompute cubic fits
fits = {}
for key in data_wR:
    pR = Polynomial.fit(a_exact, data_wR[key], 3)
    pI = Polynomial.fit(a_exact, data_wI[key], 3)
    fits[key] = (pR, pI)

def get_literature(l, m, n, a):
    pR, pI = fits.get((l,m,n), (None, None))
    if pR is None:
        return None, None
    return float(pR(a)), float(pI(a))

def angle_eigenvalue_E_lm(l, m, aomega):
    if abs(aomega) < 0.01:
        return l * (l + 1)
    x = aomega
    c1 = -2 * m**2 * (l + m + 1) * (l - m + 1) / (2 * l + 1)
    c2 = m**2 * (l + m + 1)**2 * (l - m + 1)**2 / ((2 * l + 1) * (2 * l + 3) * (2 * l - 1))
    return l * (l + 1) + c1 * x**2 + c2 * x**4

def kerr_potential(r, M, a, l, m, omega):
    f = 1.0 - 2 * M / r
    V_schw = f * (l * (l + 1) / r**2 - 6 * M / r**3)
    E_lm = angle_eigenvalue_E_lm(l, m, a * omega)
    delta = (a**2 / r**2) * (E_lm - l * (l + 1)) - 2 * a * m * omega / r**2
    return V_schw + delta

def solve_qnm(a, l, m):
    lit_R, lit_I = get_literature(l, m, n, a)
    if lit_R is None:
        return None

    rs = M + np.sqrt(M**2 - a**2)
    r_h = rs * 1.0001
    r_max = 300.0
    r_grid = np.logspace(np.log10(r_h), np.log10(r_max), 5000)
    delta_r = r_grid**2 - 2 * M * r_grid + a**2
    drstar_dr = (r_grid**2 + a**2) / delta_r

    rstar = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        rstar[i] = rstar[i - 1] + drstar_dr[i - 1] * (r_grid[i] - r_grid[i - 1])

    V = kerr_potential(r_grid, M, a, l, m, lit_R)
    V_peak = V.max()

    if V_peak <= -0.001:
        return {'status': 'FAIL_barrier', 'V_peak': V_peak,
                'a': a, 'l': l, 'm': m, 'n': n, 'lit_R': lit_R, 'lit_I': lit_I}

    V_peak_rstar = rstar[np.argmax(V)]
    rstar_min, rstar_max = rstar[0] - 20, rstar[-1] + 50
    N = 5000
    dr = (rstar_max - rstar_min) / N
    rstar_u = np.linspace(rstar_min, rstar_max, N + 1)
    V_interp = interp1d(rstar, V, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_u = np.maximum(V_interp(rstar_u), -0.01)
    dt = dr * 0.5
    dt2 = dt * dt
    T = 1000.0
    Nt = int(T / dt)
    psi = np.exp(-(rstar_u - V_peak_rstar)**2 / 32.0)
    psi_old = psi.copy()
    sig = np.zeros(Nt)
    sponge = np.ones(N + 1)
    W = int(N * 0.2)
    for i in range(N + 1):
        if i < W:
            sponge[i] = np.exp(-2.0 * (i / W) ** 2)
        elif i > N - W:
            sponge[i] = np.exp(-2.0 * ((N - i) / W) ** 2)
    rec = N // 4

    for ti in range(Nt):
        d2 = np.zeros(N + 1)
        d2[1:-1] = (psi[2:] - 2 * psi[1:-1] + psi[:-2]) / (dr * dr)
        psi_new = 2 * psi - psi_old + dt2 * (d2 - V_u * psi)
        psi_new *= sponge
        if np.any(np.isnan(psi_new)):
            psi_new = np.nan_to_num(psi_new, nan=0)
        sig[ti] = psi_new[rec]
        psi_old, psi = psi, psi_new
        if np.sum(psi[1:-1]**2) < 1e-30:
            sig[ti:] = 0
            break

    skip = int(Nt * 0.15)
    sc = sig[skip:] * np.hanning(len(sig[skip:]))
    if len(sc) < 100:
        return {'status': 'FAIL_short', 'a': a, 'l': l, 'm': m, 'n': n}
    fft_result = np.fft.rfft(sc)
    freqs = np.fft.rfftfreq(len(sc), dt)
    power = np.abs(fft_result) ** 2
    peaks, props = find_peaks(power, height=0.01 * np.max(power), distance=30)
    if len(peaks) == 0:
        return {'status': 'FAIL_no_peak', 'a': a, 'l': l, 'm': m, 'n': n}
    ci = np.argmin(np.abs(freqs[peaks] - lit_R))
    omega_R = freqs[peaks[ci]]
    err_R = abs(omega_R - lit_R) / lit_R * 100
    status = 'PASS' if err_R < 5 else 'WARN'
    return {'status': status, 'omega_R': omega_R, 'lit_R': lit_R, 'lit_I': lit_I,
            'err_R': err_R, 'a': a, 'l': l, 'm': m, 'n': n, 'V_peak': V_peak}

# Run scan
print(f"\n扫描范围: a = {a_vals}, l = {l_vals}, n = {n}")
total = len(a_vals) * sum(l + 1 for l in l_vals)
print(f"总组合数: {total}")
print("=" * 70)

results = []
t_start = time.time()

for a in a_vals:
    for l in l_vals:
        for m in range(l + 1):
            r = solve_qnm(a, l, m)
            if r is None:
                print(f"[{a:.2f}, l={l}, m={m}]: SKIP")
                continue
            if r['status'].startswith('FAIL'):
                vp = r.get('V_peak', 'N/A')
                if isinstance(vp, float):
                    print(f"[{a:.2f}, l={l}, m={m}]: {r['status']} (V_peak={vp:.6f})")
                else:
                    print(f"[{a:.2f}, l={l}, m={m}]: {r['status']}")
            else:
                print(f"[{a:.2f}, l={l}, m={m}]: {r['status']}: omega_R={r['omega_R']:.6f} vs {r['lit_R']:.6f}, err={r['err_R']:.2f}%, V_peak={r['V_peak']:.6f}")
            results.append(r)

elapsed = time.time() - t_start

print(f"\n{'=' * 70}")
print(f"完成 — 耗时 {elapsed:.1f}s")
passed = sum(1 for r in results if r.get('status') == 'PASS')
warned = sum(1 for r in results if r.get('status') == 'WARN')
failed = sum(1 for r in results if r.get('status', '').startswith('FAIL'))
print(f"PASS: {passed}, WARN: {warned}, FAIL: {failed}")

print("\n--- V_peak 趋势 (关键: l=2,m=2 和 l=3,m=3) ---")
for a in a_vals:
    for l, m in [(2,2), (3,3)]:
        r = [x for x in results if x.get('a')==a and x.get('l')==l and x.get('m')==m]
        if r:
            r = r[0]
            if r['status'].startswith('FAIL'):
                print(f"  a={a:.2f}, l={l},m={m}: FAIL (V_peak={r.get('V_peak','?')})")
            else:
                print(f"  a={a:.2f}, l={l},m={m}: omega_R={r['omega_R']:.6f}, err={r['err_R']:.2f}%, V_peak={r['V_peak']:.6f}")

# Compare with v3 linear extrapolation
print("\n--- 对比: v3(线性) vs refined(三次多项式) 参考值 ---")
print(f"  {'a':>5} {'模式':>10} {'wR_cubic':>10} {'wR_linear':>11} {'差异':>8}")
linear_ref = {
    (2,2,0,0.9): 0.375350, (3,3,0,0.9): 0.593030,
    (2,2,0,0.95): 0.375510, (3,3,0,0.95): 0.593215,
}
for a in [0.9, 0.95]:
    for l, m in [(2,2), (3,3)]:
        pR, _ = fits[(l,m,n)]
        wR_cubic = float(pR(a))
        wR_lin = linear_ref.get((l,m,n,a), None)
        if wR_lin:
            diff = abs(wR_cubic - wR_lin) / wR_lin * 100
            print(f"  {a:5.2f} {(l,m):>10} {wR_cubic:10.6f} {wR_lin:11.6f} {diff:7.4f}%")

# Save results
outdir = "/Users/a1-6/Desktop/workspace/projects/理论物理/D1-area-quantized-black-hole-QNM/notes/06-kerr-qnm-scan"
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "p1-v3-refined-results.txt"), "w") as f:
    f.write("P1-v3 refined Kerr QNM 边界扫描 (三次多项式参考值)\n")
    f.write(f"耗时: {elapsed:.1f}s\n")
    f.write(f"PASS: {passed}, WARN: {warned}, FAIL: {failed}\n")
    f.write("=" * 70 + "\n")
    for r in results:
        st = r.get('status', 'SKIP')
        a_val = r.get('a', 0)
        l_val = r.get('l', '?')
        m_val = r.get('m', '?')
        n_val = r.get('n', 0)
        if isinstance(a_val, float):
            f.write(f"a={a_val:.2f}, l={l_val}, m={m_val}, n={n_val}:\n")
        else:
            f.write(f"a={a_val}, l={l_val}, m={m_val}:\n")
        if st.startswith('FAIL'):
            vp = r.get('V_peak', 'N/A')
            if isinstance(vp, (int, float)):
                f.write(f"  V_peak = {vp:.6f}\n")
            f.write(f"  status: {st}\n\n")
            continue
        f.write(f"  measured: ω_R = {r.get('omega_R', 'N/A'):.6f}\n")
        f.write(f"  literature (cubic fit): ω_R = {r.get('lit_R', 'N/A'):.6f}, ω_I = {r.get('lit_I', 'N/A'):.6f}\n")
        f.write(f"  error_R = {r.get('err_R', 'N/A'):.2f}%\n")
        f.write(f"  V_peak = {r.get('V_peak', 'N/A'):.6f}\n")
        f.write(f"  status: {r.get('status', 'N/A')}\n\n")
print(f"\n结果已保存: {outdir}/p1-v3-refined-results.txt")
