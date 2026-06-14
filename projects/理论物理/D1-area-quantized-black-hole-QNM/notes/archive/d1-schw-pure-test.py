#!/usr/bin/env python3
"""
纯 Schwarzschild 测试：v22 风格 FDTD 在 a=0, l=2 的表现
================================================
对比 v20 (<1% error) vs v22/P0 (5% error) 在 Schwarzschild 下的表现
"""
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time

M = 1.0

# v20 style: Dirichlet BC, V_clip=0.0
def solve_v20_style(l, M, N_r=5000, T_total=800.0, sigma=4.0):
    rs = 2.0 * M
    r_horizon = rs * 1.0001
    r_max = 200.0 * M

    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N_r)
    r_star_grid = r_grid + rs * np.log(r_grid / rs - 1.0)

    f_grid = 1.0 - rs / r_grid
    V_grid = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)

    rstar_min = r_star_grid[0] - 10
    rstar_max = r_star_grid[-1] + 30
    N_rstar = 4000
    drstar = (rstar_max - rstar_min) / N_rstar
    rstar_u = np.linspace(rstar_min, rstar_max, N_rstar + 1)

    V_interp = interp1d(r_star_grid, V_grid, kind='cubic', fill_value='extrapolate')
    V_u = V_interp(rstar_u)
    V_u = np.maximum(V_u, 0.0)  # v20 style

    dt = drstar * 0.5
    dt2 = dt * dt
    N_t = int(T_total / dt)

    V_pos = rstar_u[np.argmax(V_u)]
    psi = np.exp(-(rstar_u - V_pos)**2 / (2 * sigma**2))
    psi_prev = psi

    for t in range(N_t):
        # Dirichlet BC: psi=0 at boundaries
        d2 = (psi[2:] - 2*psi[1:-1] + psi[:-2]) / (drstar**2)
        source = -V_u[1:-1] * psi[1:-1]
        psi_new = 2*psi[1:-1] - psi_prev[1:-1] + dt2 * (d2 + source)
        # Dirichlet BC
        psi_new = np.concatenate([[0], psi_new, [0]])

        psi_prev = psi.copy()
        psi = psi_new

    # Record near boundary for FFT
    boundary_idx = len(psi) - 100
    signal = np.zeros(N_t)
    psi_copy = psi.copy()
    for t in range(N_t):
        d2 = (psi_copy[2:] - 2*psi_copy[1:-1] + psi_copy[:-2]) / (drstar**2)
        source = -V_u[1:-1] * psi_copy[1:-1]
        psi_new = 2*psi_copy[1:-1] - psi_prev[1:-1] + dt2 * (d2 + source)
        psi_new = np.concatenate([[0], psi_new, [0]])
        signal[t] = psi_new[boundary_idx]
        psi_prev = psi_copy.copy()
        psi_copy = psi_new

    skip = int(N_t * 0.15)
    sig = signal[skip:] * np.hanning(len(signal) - skip)
    f = np.fft.rfftfreq(len(sig), dt)
    pw = np.abs(np.fft.rfft(sig))**2
    peaks, _ = find_peaks(pw, height=0.01, distance=30)
    return f[peaks[0]] if len(peaks) > 0 else f[np.argmax(pw)]

# v22 style: zero d2 at boundaries, V_clip=-0.01, sponge, record at N/4
def solve_v22_style(a, l, m, N, T, sigma=4.0):
    rs = M + np.sqrt(M**2 - a**2)
    r_horizon = rs * 1.0001
    r_max = 400.0 * M
    omega_guess = 0.374 - 0.09j

    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N)
    dr_star_dr = (r_grid**2 + a**2) / (r_grid**2 - 2*M*r_grid + a**2)
    r_star_grid = np.cumsum(np.concatenate([[0], dr_star_dr[:-1] * np.diff(r_grid)]))

    if a == 0:
        f_grid = 1.0 - 2*M/r_grid
        V_kerr = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    else:
        f_grid = 1.0 - 2*M/r_grid
        V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
        aomega = a * omega_guess
        E_lm = l*(l+1) if abs(aomega) < 0.01 else l*(l+1) - 2*m*m*(l+m+1)*(l-m+1)/(2*l+1) * aomega**2
        V_kerr = V_schw + (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2

    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N
    rstar_u = np.linspace(rstar_min, rstar_max, N + 1)

    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_u = V_interp(rstar_u)
    V_u = np.maximum(V_u, -0.01)

    dt = drstar * 0.5
    dt2 = dt * dt
    Nt = int(T / dt)

    V_pos = rstar_u[np.argmax(V_u)]
    psi = np.exp(-(rstar_u - V_pos)**2 / (2 * sigma**2))
    psi_prev = psi

    W = int(N * 0.2)
    alpha = 2.0
    spon = np.ones(N + 1)
    for i in range(N + 1):
        if i < W:
            spon[i] = np.exp(-alpha * (i / W)**2)
        elif i > N - W:
            spon[i] = np.exp(-alpha * ((N - i) / W)**2)

    signal = np.zeros(Nt)
    rec_idx = N // 4

    for t in range(Nt):
        d2 = np.zeros(N + 1)
        d2[1:-1] = (psi[2:] - 2*psi[1:-1] + psi[:-2]) / (drstar**2)
        source = -V_u * psi
        psi_new = 2*psi - psi_prev + dt2 * (d2 + source)
        psi_new = psi_new * spon
        psi_prev = psi.copy()
        psi = psi_new
        signal[t] = psi[rec_idx]

    skip = int(Nt * 0.15)
    sig = signal[skip:] * np.hanning(len(signal) - skip)
    f = np.fft.rfftfreq(len(sig), dt)
    pw = np.abs(np.fft.rfft(sig))**2
    peaks, _ = find_peaks(pw, height=0.01, distance=30)
    if len(peaks) > 0:
        closest = np.argmin(np.abs(f[peaks] - 0.3737))
        return f[peaks[closest]]
    return f[np.argmax(pw)]

lit = 0.37373

print("\n=== v20 style (Dirichlet BC, V_clip=0) ===\n")
result = solve_v20_style(2, M, N_r=5000, T_total=800.0)
error = abs(result - lit) / lit * 100
print(f"l=2, Schwarzschild: meas={result:.6f}, lit={lit:.5f}, error={error:.2f}%")

print("\n=== v22 style (zero BC, V_clip=-0.01, sponge) a=0 ===\n")
result = solve_v22_style(0, 2, 0, 4000, 800.0)
error = abs(result - lit) / lit * 100
print(f"a=0, l=2, m=0: meas={result:.6f}, error={error:.2f}%")

result = solve_v22_style(0, 2, 2, 4000, 800.0)
error = abs(result - 0.37367) / 0.37367 * 100
print(f"a=0, l=2, m=2: meas={result:.6f}, lit=0.37367, error={error:.2f}%")

result = solve_v22_style(0.5, 2, 2, 4000, 800.0)
error = abs(result - 0.37414) / 0.37414 * 100
print(f"a=0.5, l=2, m=2: meas={result:.6f}, lit=0.37414, error={error:.2f}%")

result = solve_v22_style(0.5, 2, 2, 6000, 1200.0)
error = abs(result - 0.37414) / 0.37414 * 100
print(f"a=0.5, l=2, m=2, N=6000,T=1200: meas={result:.6f}, error={error:.2f}%")

print("\nDone.")
