#!/usr/bin/env python3
"""
精确复现 P0 FDTD 求解器，诊断 l=2, low-a 误差
================================================
严格匹配 d1-p0-kerr-qnm-scan.py 的数值方案
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time

print("NumPy:", np.__version__)
print("=" * 70)

M = 1.0

def angle_eigenvalue_E_lm(l, m, aomega):
    if abs(aomega) < 0.01:
        return l*(l+1)
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    return l*(l+1) + c1*x**2 + c2*x**4

def kerr_effective_potential(r_grid, M, a, l, m, omega_guess):
    f_grid = 1.0 - 2*M/r_grid
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    return V_schw + delta_rot

def solve_qnm_FDTD(a, l, m, N_rstar=4000, T_total=800.0, dt_factor=0.5):
    rs = M + np.sqrt(M**2 - a**2)
    r_horizon = rs * 1.0001
    r_max = 300.0 * M

    omega_guess = 0.374 - 0.09j
    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_rstar)
    dr_star_dr = (r_grid**2 + a**2) / (r_grid**2 - 2*M*r_grid + a**2)

    r_star_grid = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])

    V_kerr = kerr_effective_potential(r_grid, M, a, l, m, omega_guess)

    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_grid_u = np.linspace(rstar_min, rstar_max, N_rstar + 1)

    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_uniform = V_interp(rstar_grid_u)
    V_uniform = np.maximum(V_uniform, -0.01)

    dt = drstar * dt_factor
    dt2 = dt * dt
    N_t = int(T_total / dt)

    V_peak_pos = rstar_grid_u[np.argmax(V_uniform)]
    sigma = 4.0
    psi_0 = np.exp(-(rstar_grid_u - V_peak_pos)**2 / (2 * sigma**2))
    dpsi_0 = np.zeros_like(psi_0)

    psi_n = psi_0.copy()
    psi_n_minus_1 = psi_0 - dt * dpsi_0

    # Sponge layer (P0 方案)
    W_sponge = int(N_rstar * 0.2)
    alpha = 2.0
    sponge_factor = np.ones(N_rstar + 1)
    for i in range(N_rstar + 1):
        if i < W_sponge:
            sponge_factor[i] = np.exp(-alpha * (i / W_sponge)**2)
        elif i > N_rstar - W_sponge:
            sponge_factor[i] = np.exp(-alpha * ((N_rstar - i) / W_sponge)**2)

    # Record signal
    record_idx = N_rstar // 4
    signal_record = np.zeros(N_t)
    nan_count = 0

    for time_idx in range(N_t):
        d2_psi = np.zeros(N_rstar + 1)
        d2_psi[1:-1] = (psi_n[2:] - 2 * psi_n[1:-1] + psi_n[:-2]) / (drstar * drstar)
        source = -V_uniform * psi_n

        psi_new = 2 * psi_n - psi_n_minus_1 + dt2 * (d2_psi + source)
        psi_new = psi_new * sponge_factor

        if np.any(np.isnan(psi_new)):
            nan_count += 1
            psi_new = np.nan_to_num(psi_new, nan=0, posinf=0, neginf=0)

        signal_record[time_idx] = psi_new[record_idx]
        psi_n_minus_1 = psi_n.copy()
        psi_n = psi_new.copy()

    # FFT with hanning window (P0 方案)
    start_skip = int(N_t * 0.15)
    signal_cut = signal_record[start_skip:]
    window = np.hanning(len(signal_cut))
    signal_windowed = signal_cut * window

    fft_vals = np.fft.rfft(signal_windowed)
    freqs = np.fft.rfftfreq(len(signal_cut), dt)
    power_spectrum = np.abs(fft_vals)**2
    power_spectrum /= np.max(power_spectrum)

    peaks, props = find_peaks(power_spectrum, height=0.01, distance=30)

    if len(peaks) > 0:
        return freqs[peaks[0]], power_spectrum, freqs
    return None, power_spectrum, freqs

lit = {
    (0.0, 2, 0): 0.37373, (0.0, 2, 1): 0.37373, (0.0, 2, 2): 0.37367,
    (0.1, 2, 0): 0.37376, (0.1, 2, 1): 0.37384, (0.1, 2, 2): 0.37368,
    (0.2, 2, 0): 0.37383, (0.2, 2, 1): 0.37400, (0.2, 2, 2): 0.37373,
    (0.5, 2, 2): 0.37414,
    (0.0, 3, 3): 0.59108,
}

print("\n=== P0-style FDTD (l=2, a≤0.2) ===\n")
for a in [0.0, 0.1, 0.2]:
    for m in [0, 1, 2]:
        result, pspec, freqs = solve_qnm_FDTD(a, 2, m, N_rstar=4000, T_total=800.0, dt_factor=0.5)
        if result is not None:
            error = abs(result - lit[(a, 2, m)]) / lit[(a, 2, m)] * 100
            status = "⚠" if error >= 5 else "✓"
            print(f"{status} a={a:.1f}, l=2, m={m}: meas={result:.6f}, lit={lit[(a,2,m)]:.5f}, error={error:.2f}%")
        else:
            print(f"  a={a:.1f}, l=2, m={m}: NO PEAK FOUND")

print("\n=== v22-like (a=0.5, l=2, m=2) ===\n")
result, pspec, freqs = solve_qnm_FDTD(0.5, 2, 2, N_rstar=4000, T_total=800.0, dt_factor=0.5)
if result:
    error = abs(result - 0.37414) / 0.37414 * 100
    print(f"a=0.5, l=2, m=2: meas={result:.6f}, error={error:.2f}%")

print("\nDone.")
