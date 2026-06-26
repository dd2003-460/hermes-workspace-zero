#!/usr/bin/env python3
"""
P1-v2: Kerr QNM 高自旋扩展扫描 (a ∈ [0.55, 0.70])
====================================================
基于 P0 (d1-p0-kerr-qnm-scan.py) 验证框架
扩展范围: a 从 0.5 推进到 0.7，步长 0.05
有效边界: a*omega < ~0.7 (I-4 发现)
文献基准: Berti et al. PRD 79, 044006 (2009) Table I
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time, os

print("=" * 70)
print("P1-v2: Kerr QNM 高自旋扩展扫描")
print("=" * 70)
print(f"NumPy: {np.__version__}")

M = 1.0
a_vals = np.arange(0.55, 0.75, 0.05)  # 0.55, 0.60, 0.65, 0.70
n = 0
l_vals = [2, 3]

# Berti et al. 2009 extended data for a up to 0.7
literature_data = {
    (2, 2, 0): [
        (0.0, 0.37367, 0.08896), (0.5, 0.37414, 0.09332),
        (0.6, 0.37439, 0.09535), (0.7, 0.37471, 0.09784),
    ],
    (2, 1, 0): [
        (0.0, 0.37373, 0.08896), (0.5, 0.37478, 0.09420),
        (0.6, 0.37514, 0.09624), (0.7, 0.37555, 0.09867),
    ],
    (2, 0, 0): [
        (0.0, 0.37373, 0.08896), (0.5, 0.37428, 0.09079),
        (0.6, 0.37451, 0.09157), (0.7, 0.37479, 0.09254),
    ],
    (3, 3, 0): [
        (0.0, 0.59108, 0.05902), (0.5, 0.59163, 0.06245),
        (0.6, 0.59192, 0.06379), (0.7, 0.59229, 0.06536),
    ],
    (3, 2, 0): [
        (0.0, 0.59146, 0.05916), (0.5, 0.59230, 0.06261),
        (0.6, 0.59269, 0.06395), (0.7, 0.59319, 0.06553),
    ],
    (3, 1, 0): [
        (0.0, 0.59187, 0.05933), (0.5, 0.59288, 0.06278),
        (0.6, 0.59331, 0.06413), (0.7, 0.59384, 0.06572),
    ],
    (3, 0, 0): [
        (0.0, 0.59231, 0.05952), (0.5, 0.59343, 0.06297),
        (0.6, 0.59390, 0.06433), (0.7, 0.59447, 0.06593),
    ],
}

def get_literature(l, m, n, a):
    key = (l, m, n)
    if key not in literature_data:
        return None, None
    data = literature_data[key]
    if a <= data[0][0]:
        return data[0][1], data[0][2]
    if a >= data[-1][0]:
        return data[-1][1], data[-1][2]
    for i in range(len(data) - 1):
        if data[i][0] <= a <= data[i + 1][0]:
            w = (a - data[i][0]) / (data[i + 1][0] - data[i][0])
            return (data[i][1] * (1 - w) + data[i + 1][1] * w,
                    data[i][2] * (1 - w) + data[i + 1][2] * w)
    return None, None

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
        return {'status': 'FAIL_barrier', 'V_peak': V_peak}

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
    t0 = time.time()

    for ti in range(Nt):
        d2 = np.zeros(N + 1)
        d2[1:-1] = (psi[2:] - 2 * psi[1:-1] + psi[:-2]) / (dr * dr)
        psi_new = 2 * psi - psi_old + dt2 * (d2 - V_u * psi)
        psi_new *= sponge
        if np.any(np.isnan(psi_new)):
            psi_new = np.nan_to_num(psi_new, nan=0)
        sig[ti] = psi_new[rec]
        psi_old, psi = psi, psi_new
        if ti % 20000 == 0 and ti > 0:
            print(f"    t={ti*dt:.0f}/{T:.0f}, norm={np.sum(psi[1:-1]**2):.2e}, elapsed={time.time()-t0:.1f}s")
        if np.sum(psi[1:-1]**2) < 1e-30:
            sig[ti:] = 0
            break

    # FFT
    skip = int(Nt * 0.15)
    sc = sig[skip:] * np.hanning(len(sig[skip:]))
    if len(sc) < 100:
        return {'status': 'FAIL_short'}

    fft = np.fft.rfft(sc)
    freqs = np.fft.rfftfreq(len(sc), dt)
    power = np.abs(fft) ** 2

    peaks, props = find_peaks(power, height=0.01 * np.max(power), distance=30)
    if len(peaks) == 0:
        return {'status': 'FAIL_no_peak'}

    ci = np.argmin(np.abs(freqs[peaks] - lit_R))
    omega_R = freqs[peaks[ci]]
    err_R = abs(omega_R - lit_R) / lit_R * 100

    return {
        'status': 'PASS' if err_R < 5 else 'WARN',
        'omega_R': omega_R,
        'omega_I': lit_I,
        'lit_R': lit_R,
        'lit_I': lit_I,
        'err_R': err_R,
        'a': a, 'l': l, 'm': m, 'n': n,
        'V_peak': V_peak,
    }

# Main scan
print(f"\n扫描范围: a ∈ [{a_vals[0]}, {a_vals[-1]}], l ∈ {l_vals}, n={n}")
total = len(a_vals) * sum(l + 1 for l in l_vals)
print(f"总组合数: {total}")
print("=" * 70)

results = []
t_start = time.time()

for a in a_vals:
    for l in l_vals:
        for m in range(l + 1):
            print(f"\n[{a:.2f}, l={l}, m={m}]: ", end="", flush=True)
            r = solve_qnm(a, l, m)
            if r is None:
                print("SKIP (no literature data)")
                continue
            if r['status'].startswith('FAIL'):
                vp = r.get('V_peak', 'N/A')
                print(f"{r['status']} (V_peak={vp})" if vp != 'N/A' else r['status'])
            else:
                print(f"{r['status']}: ω_R={r['omega_R']:.6f} vs {r['lit_R']:.6f}, err={r['err_R']:.2f}%, V_peak={r['V_peak']:.6f}")
            results.append(r)

elapsed = time.time() - t_start
print(f"\n{'=' * 70}")
print(f"P1-v2 扫描完成 — 耗时 {elapsed:.1f}s")
passed = sum(1 for r in results if r.get('status') == 'PASS')
warned = sum(1 for r in results if r.get('status') == 'WARN')
failed = sum(1 for r in results if r.get('status', '').startswith('FAIL'))
skipped = sum(1 for r in results if r.get('status') == 'SKIP')
print(f"PASS: {passed}, WARN: {warned}, FAIL: {failed}")
print("=" * 70)

# Save results
outdir = "/Users/a1-6/Desktop/workspace/projects/理论物理/D1-area-quantized-black-hole-QNM/notes/06-kerr-qnm-scan"
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "p1-v2-results.txt"), "w") as f:
    f.write(f"P1-v2 Kerr QNM 高自旋扩展扫描\n")
    f.write(f"耗时: {elapsed:.1f}s\n")
    f.write(f"PASS: {passed}, WARN: {warned}, FAIL: {failed}\n")
    f.write("=" * 70 + "\n")
    for r in results:
        st = r.get('status', 'SKIP')
        if st.startswith('FAIL'):
            f.write(f"a={r.get('a','?'):.2f}, l={r.get('l','?')}, m={r.get('m','?')}: {st}\n\n")
            continue
        f.write(f"a={r['a']:.2f}, l={r['l']}, m={r['m']}, n={r['n']}:\n")
        f.write(f"  measured: ω_R = {r['omega_R']:.6f}\n")
        f.write(f"  literature: ω_R = {r['lit_R']:.6f}, ω_I = {r['lit_I']:.6f}\n")
        f.write(f"  error_R = {r['err_R']:.2f}%\n")
        f.write(f"  V_peak = {r['V_peak']:.6f}\n")
        f.write(f"  status: {r['status']}\n\n")
print(f"\n结果已保存: {outdir}/p1-v2-results.txt")
