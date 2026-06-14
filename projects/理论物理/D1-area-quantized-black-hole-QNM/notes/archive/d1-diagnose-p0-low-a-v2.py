#!/usr/bin/env python3
"""
诊断 P0 扫描中 l=2, a≤0.2 误差增大的原因
================================================
vD1 — 简化解法，直接运行完整的 P0 扫描对比
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
    V_u = V_interp(rstar_grid_u)
    V_u = np.maximum(V_u, -0.01)

    dt = drstar * dt_factor
    dt2 = dt * dt
    N_t = int(T_total / dt)

    V_peak_pos = rstar_grid_u[np.argmax(V_u)]
    sigma = 4.0
    psi = np.exp(-(rstar_grid_u - V_peak_pos)**2 / (2 * sigma**2))
    psi_prev = psi  # dpsi/dt = 0

    # Record boundary signal for FFT
    boundary_signal = np.zeros(N_t)
    boundary_idx = len(rstar_grid_u) - 100

    for t in range(N_t):
        # FDTD update: interior points only
        d2psi_dr2 = (psi[2:] - 2*psi[1:-1] + psi[:-2]) / (drstar**2)
        Vpsi = V_u[1:-1] * psi[1:-1]

        psi_interior = 2*psi[1:-1] - psi_prev[1:-1] + dt2 * (d2psi_dr2 - Vpsi)

        # Boundary: Dirichlet (ψ=0 at both ends, outgoing waves)
        psi_new = np.zeros_like(psi)
        psi_new[0] = 0.0  # sponge/horizon
        psi_new[1:-1] = psi_interior
        psi_new[-1] = 0.0  # sponge/infinity

        psi_prev = psi.copy()
        psi = psi_new
        boundary_signal[t] = psi[boundary_idx] if boundary_idx < len(psi) else psi[-1]

    # FFT
    signal = boundary_signal
    N = len(signal)
    fft_vals = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(N, dt)
    power = np.abs(fft_vals)**2

    peaks, _ = find_peaks(power, height=0.1 * power.max(), distance=10)
    if len(peaks) > 0:
        return freqs[peaks[0]]
    return freqs[np.argmax(power)]

# Literature reference values
lit = {
    (0.0, 2, 0): 0.37373, (0.0, 2, 1): 0.37373, (0.0, 2, 2): 0.37367,
    (0.1, 2, 0): 0.37376, (0.1, 2, 1): 0.37384, (0.1, 2, 2): 0.37368,
    (0.2, 2, 0): 0.37383, (0.2, 2, 1): 0.37400, (0.2, 2, 2): 0.37373,
    (0.5, 2, 2): 0.37414,
    (0.0, 3, 3): 0.59108,
}

print("\n=== P0-like FDTD scan (l=2, a≤0.2) ===\n")
for a in [0.0, 0.1, 0.2]:
    for m in [0, 1, 2]:
        result = solve_qnm_FDTD(a, 2, m, N_rstar=4000, T_total=800.0, dt_factor=0.5)
        key = (a, 2, m)
        error = abs(result - lit[key]) / lit[key] * 100
        status = "⚠" if error >= 5 else "✓"
        print(f"{status} a={a:.1f}, l=2, m={m}: meas={result:.6f}, lit={lit[key]:.5f}, error={error:.2f}%")

print("\n=== v22-like (a=0.5, l=2, m=2) ===\n")
result = solve_qnm_FDTD(0.5, 2, 2, N_rstar=4000, T_total=800.0, dt_factor=0.5)
error = abs(result - 0.37414) / 0.37414 * 100
print(f"a=0.5, l=2, m=2: meas={result:.6f}, lit=0.37414, error={error:.2f}%")

print("\n=== Testing different T_total (a=0, l=2, m=0) ===\n")
for T in [200, 400, 600, 800, 1200, 1600]:
    result = solve_qnm_FDTD(0.0, 2, 0, N_rstar=4000, T_total=T, dt_factor=0.5)
    error = abs(result - 0.37373) / 0.37373 * 100
    print(f"T_total={T}: meas={result:.6f}, error={error:.2f}%")

print("\nDone.")
