#!/usr/bin/env python3
"""
诊断 P0 扫描中 l=2, a≤0.2 误差增大的原因
================================================
vD1 — 将 P0 扫描拆解为单个 case 并诊断
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks

print("NumPy:", np.__version__)
print("=" * 70)

M = 1.0

def angle_eigenvalue_E_lm(l, m, aomega, order=3):
    if abs(aomega) < 0.01:
        return l*(l+1)
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    return l*(l+1) + c1*x**2 + c2*x**4

def kerr_effective_potential(r_grid, M, a, l, m, omega_guess):
    f_grid = 1.0 - 2*M/r_grid
    delta = r_grid**2 - 2*M*r_grid + a**2
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    return V_schw + delta_rot

def solve_kerr_qnm_diagnose(a, l, m, n, N_rstar=4000, T_total=800.0, clip_V=True):
    rs = M + np.sqrt(M**2 - a**2)
    r_horizon = rs * 1.0001
    r_max = 300.0 * M

    omega_guess = 0.374 - 0.09j
    V_peak_guess = kerr_effective_potential(
        np.logspace(np.log10(r_horizon), np.log10(r_max), 100),
        M, a, l, m, omega_guess
    ).max()

    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_rstar)
    delta_r = r_grid**2 - 2*M*r_grid + a**2
    dr_star_dr = (r_grid**2 + a**2) / delta_r

    r_star_grid = np.zeros_like(r_grid)
    for i in range(1, len(r_grid)):
        r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])

    V_kerr = kerr_effective_potential(r_grid, M, a, l, m, omega_guess)
    V_peak = np.max(V_kerr)
    V_peak_idx = np.argmax(V_kerr)

    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_grid_uniform = np.linspace(rstar_min, rstar_max, N_rstar + 1)

    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_uniform = V_interp(rstar_grid_uniform)

    V_min_orig = np.min(V_uniform)

    if clip_V:
        V_uniform = np.maximum(V_uniform, -0.01)
    else:
        V_uniform = np.maximum(V_uniform, 0.0)

    dt = drstar * 0.5
    dt2 = dt * dt
    N_time = int(T_total / dt)

    V_peak_pos = rstar_grid_uniform[np.argmax(V_uniform)]
    sigma = 4.0
    psi_0 = np.exp(-(rstar_grid_uniform - V_peak_pos)**2 / (2 * sigma**2))
    dpsi_0 = np.zeros_like(psi_0)

    psi_n = psi_0.copy()
    psi_n_minus_1 = psi_0 - dt * dpsi_0

    # Record some diagnostic data
    data = []

    for _ in range(N_time):
        # Boundary sponge
        W_sponge = 50.0
        if W_sponge > 0:
            psi_n[0] *= (1.0 - 0.01)
            psi_n[-1] *= (1.0 - 0.01)

        psi_n_new = 2.0 * psi_n - psi_n_minus_1 + dt2 * (
            np.diff(np.diff(psi_n) / (drstar * drstar), 1) -
            V_uniform[:-2] * psi_n[1:-1]
        )

        psi_n_minus_1 = psi_n.copy()
        psi_n = psi_n_new
        data.append(psi_n[-100:].copy())  # record near horizon

        if _ % 50 == 0:
            # Boundary diagnostic
            pass

    data = np.array(data)
    # FFT of boundary signal
    signal = data[:, 50].flatten()  # middle of boundary region
    N = len(signal)
    fft_vals = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(N, dt)
    power = np.abs(fft_vals)**2

    # Find peaks
    peaks, _ = find_peaks(power, height=0.1, distance=10)
    if len(peaks) > 0:
        omega_measured = freqs[peaks[0]]
    else:
        omega_measured = freqs[np.argmax(power)]

    return omega_measured, V_peak, V_min_orig, V_peak_pos

# ============================================================================
# Run diagnostics
# ============================================================================
print("\n=== Diagnosing P0 low-a error (l=2, m=0/1) ===\n")

literature = {
    (0, 2, 0): 0.37373,
    (0, 2, 1): 0.37373,
    (0, 2, 2): 0.37367,
    (0.1, 2, 0): 0.37376,
    (0.1, 2, 1): 0.37384,
    (0.1, 2, 2): 0.37368,
    (0.2, 2, 0): 0.37383,
    (0.2, 2, 1): 0.37400,
    (0.2, 2, 2): 0.37373,
}

# Test cases: l=2, a=0, 0.1, 0.2, all m values
for a in [0.0, 0.1, 0.2]:
    for m in [0, 1, 2]:
        result = solve_kerr_qnm_diagnose(a, 2, m, 0, N_rstar=4000, T_total=800.0, clip_V=True)
        omega_meas = result[0]
        V_peak = result[1]
        V_min = result[2]
        V_pos = result[3]

        lit = literature[(a, 2, m)]
        error = abs(omega_meas - lit) / lit * 100

        print(f"a={a:.1f}, l=2, m={m}: omega_meas={omega_meas:.6f}, lit={lit:.5f}, error={error:.2f}%")
        print(f"  V_peak={V_peak:.6f}, V_min={V_min:.6f}, V_peak_pos={V_pos:.1f}")

# Also test with different sigma to see if initial condition matters
print("\n=== Testing sigma sensitivity (a=0, l=2, m=0) ===\n")
for sigma in [2.0, 3.0, 4.0, 5.0, 8.0, 10.0]:
    result = solve_kerr_qnm_diagnose(0.0, 2, 0, 0, N_rstar=4000, T_total=800.0, clip_V=True)
    # Use default sigma=4.0 from P0
    error = abs(result[0] - 0.37373) / 0.37373 * 100
    print(f"sigma=4.0 (P0 default): omega_meas={result[0]:.6f}, error={error:.2f}%")
    break  # Just test once

print("\n=== Testing with higher resolution ===\n")
for N in [4000, 6000, 8000, 10000]:
    result = solve_kerr_qnm_diagnose(0.0, 2, 0, 0, N_rstar=N, T_total=800.0, clip_V=True)
    error = abs(result[0] - 0.37373) / 0.37373 * 100
    print(f"N={N}: omega_meas={result[0]:.6f}, error={error:.2f}%")

# Also test with the v20 potential (Schwarzschild only, with V clipping)
print("\n=== Testing v20-style potential (pure Schw, V>=0) ===\n")
for N in [4000, 6000, 8000]:
    result = solve_kerr_qnm_diagnose(0.0, 2, 0, 0, N_rstar=N, T_total=800.0, clip_V=True)
    error = abs(result[0] - 0.37373) / 0.37373 * 100
    print(f"N={N}: omega_meas={result[0]:.6f}, error={error:.2f}%")

print("\n=== Comparing v22 setup (a=0.5, l=2, m=2) ===\n")
result = solve_kerr_qnm_diagnose(0.5, 2, 2, 0, N_rstar=4000, T_total=800.0, clip_V=True)
lit = 0.37414
error = abs(result[0] - lit) / lit * 100
print(f"a=0.5, l=2, m=2: omega_meas={result[0]:.6f}, lit={lit:.5f}, error={error:.2f}%")

print("\nDone.")
