#!/usr/bin/env python3
"""
收敛性测试：N_rstar 和 T_total 对 QNM 测量的影响
================================================
针对 l=2, a=0 的 5% 误差进行收敛性分析
"""
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks

print("NumPy:", np.__version__)

M = 1.0

def angle_eigenvalue_E_lm(l, m, aomega):
    if abs(aomega) < 0.01:
        return l*(l+1)
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    return l*(l+1) + c1*x**2 + c2*x**4

def kerr_eff_pot(r_grid, M, a, l, m, omega_guess):
    f_grid = 1.0 - 2*M/r_grid
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    return V_schw + delta_rot

def solve_FDTD(a, l, m, N, T, dt_factor=0.5, sigma=4.0, clip=-0.01):
    rs = M + np.sqrt(M**2 - a**2)
    r_horizon = rs * 1.0001
    r_max = 400.0 * M  # v22-style range
    omega_guess = 0.374 - 0.09j

    r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), N)
    dr_star_dr = (r_grid**2 + a**2) / (r_grid**2 - 2*M*r_grid + a**2)
    r_star_grid = np.cumsum(np.concatenate([[0], dr_star_dr[:-1] * np.diff(r_grid)]))

    V_kerr = kerr_eff_pot(r_grid, M, a, l, m, omega_guess)

    rstar_min = r_star_grid[0] - 20
    rstar_max = r_star_grid[-1] + 50
    drstar = (rstar_max - rstar_min) / N
    rstar_u = np.linspace(rstar_min, rstar_max, N + 1)
    V_interp = interp1d(r_star_grid, V_kerr, kind='cubic', bounds_error=False, fill_value=(0.0, 0.0))
    V_u = V_interp(rstar_u)
    V_u = np.maximum(V_u, clip)

    dt = drstar * dt_factor
    dt2 = dt * dt
    Nt = int(T / dt)

    V_pos = rstar_u[np.argmax(V_u)]
    psi = np.exp(-(rstar_u - V_pos)**2 / (2 * sigma**2))
    psi_prev = psi

    # Sponge
    W = int(N * 0.2)
    alpha = 2.0
    spon = np.ones(N + 1)
    for i in range(N + 1):
        if i < W:
            spon[i] = np.exp(-alpha * (i / W)**2)
        elif i > N - W:
            spon[i] = np.exp(-alpha * ((N - i) / W)**2)

    rec = np.zeros(Nt)
    rec_idx = N // 4

    for t in range(Nt):
        d2 = np.zeros(N + 1)
        d2[1:-1] = (psi[2:] - 2*psi[1:-1] + psi[:-2]) / (drstar**2)
        source = -V_u * psi
        psi_new = 2*psi - psi_prev + dt2 * (d2 + source)
        psi_new = psi_new * spon
        psi_prev = psi.copy()
        psi = psi_new
        rec[t] = psi[rec_idx]

    # FFT
    skip = int(Nt * 0.15)
    sig = rec[skip:] * np.hanning(len(rec) - skip)
    f = np.fft.rfftfreq(len(sig), dt)
    pw = np.abs(np.fft.rfft(sig))**2

    peaks, _ = find_peaks(pw, height=0.01, distance=30)
    if len(peaks) > 0:
        return f[peaks[0]]
    return f[np.argmax(pw)]

# Convergence test for l=2, a=0
print("\n=== Convergence: N_rstar (l=2, a=0, m=2, T=1200) ===\n")
for N in [4000, 6000, 8000, 10000]:
    result = solve_FDTD(0, 2, 2, N, 1200.0, dt_factor=0.5, sigma=4.0)
    error = abs(result - 0.37367) / 0.37367 * 100
    print(f"N={N}: omega={result:.6f}, error={error:.2f}%")

print("\n=== Convergence: T_total (l=2, a=0, m=2, N=4000) ===\n")
for T in [400, 600, 800, 1200, 1600, 2000]:
    result = solve_FDTD(0, 2, 2, 4000, T, dt_factor=0.5, sigma=4.0)
    error = abs(result - 0.37367) / 0.37367 * 100
    print(f"T={T}: omega={result:.6f}, error={error:.2f}%")

print("\n=== Convergence: T_total (l=3, a=0, m=3, N=4000) ===\n")
for T in [800, 1200, 1600, 2000]:
    result = solve_FDTD(0, 3, 3, 4000, T, dt_factor=0.5, sigma=4.0)
    error = abs(result - 0.59108) / 0.59108 * 100
    print(f"T={T}: omega={result:.6f}, error={error:.2f}%")

print("\nDone.")
