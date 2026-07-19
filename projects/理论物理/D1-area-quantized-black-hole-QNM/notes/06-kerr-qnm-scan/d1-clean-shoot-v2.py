"""
Clean Schwarzschild QNM solver via shooting method.
Optimized: vectorized grid search with coarse-to-fine approach.

Berti et al. PRD 79, 044006 (2009), arXiv:0802.4126
Table I (M=1):
  l=2:  omega = 0.37367 - 0.08896i
  l=3:  omega = 0.59108 - 0.05902i
"""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0
r_plus = 2.0 * M

def potential_RW(r, c=2):
    f = 1.0 - 2.0 * M / r
    return f * (2.0 * r + c * M) / r**3

def rhs_in_r(r, psi, omega):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = potential_RW(r)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot_single(omega, r_match=10.0, eps_horizon=1e-4, r_inf=80.0):
    """Single shoot. Returns normalized Wronskian."""
    # Left: horizon -> r_match
    y0_L = np.array([1.0, -1j * omega / (4.0 * M) / (1.0 - 2.0 * M / (r_plus + eps_horizon))])
    sol_L = solve_ivp(rhs_in_r, [r_plus + eps_horizon, r_match], y0_L,
                     method='RK45', args=(omega,), dense_output=True,
                     max_step=0.5, atol=1e-10, rtol=1e-9)
    if not sol_L.success:
        return np.inf

    # Right: r_inf -> r_match
    psi_r0 = np.exp(1j * omega * r_inf)
    y0_R = np.array([psi_r0, 1j * omega * psi_r0])
    sol_R = solve_ivp(rhs_in_r, [r_inf, r_match], y0_R,
                     method='RK45', args=(omega,), dense_output=True,
                     max_step=0.5, atol=1e-10, rtol=1e-9)
    if not sol_R.success:
        return np.inf

    pL = sol_L.sol(r_match)[0]
    dL = sol_L.sol(r_match)[1]
    pR = sol_R.sol(r_match)[0]
    dR = sol_R.sol(r_match)[1]

    W = (dL * pR - pL * dR)
    norm = np.abs(pL) * np.abs(pR)
    return W / norm if norm > 1e-30 else np.inf

def coarse_scan():
    """Very coarse scan to find approximate location."""
    print("Coarse scan (30x30 grid)...")
    reals = np.linspace(0.1, 0.8, 30)
    imags = np.linspace(-0.15, -0.01, 30)

    best_W = np.inf
    best_omega = None

    t0 = time.time()
    for i, r in enumerate(reals):
        for j, im in enumerate(imags):
            omega = complex(r, im)
            W = shoot_single(omega)
            if np.isfinite(W) and np.abs(W) < best_W:
                best_W = np.abs(W)
                best_omega = omega
        if i % 10 == 0:
            print(f"  Progress: {i+1}/{len(reals)} rows, best |W| = {best_W:.6e}")

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Best: omega = {best_omega.real:.5f} + {best_omega.imag:.5f}i, |W| = {best_W:.6e}")
    return best_omega

def fine_scan(omega0, n=40, dr=0.01, di=0.003):
    """Fine scan around omega0."""
    print(f"\nFine scan around {omega0}:")
    r_range = np.linspace(omega0.real - dr, omega0.real + dr, n)
    i_range = np.linspace(omega0.imag - di, omega0.imag + di, n)

    best_W = np.inf
    best_omega = omega0

    t0 = time.time()
    count = 0
    for r in r_range:
        for i in i_range:
            omega = complex(r, i)
            W = shoot_single(omega)
            count += 1
            if np.isfinite(W) and np.abs(W) < best_W:
                best_W = np.abs(W)
                best_omega = omega

    elapsed = time.time() - t0
    print(f"  {count} shoots in {elapsed:.1f}s")
    print(f"  Refined: omega = {best_omega.real:.6f} + {best_omega.imag:.6f}i, |W| = {best_W:.6e}")
    return best_omega

if __name__ == "__main__":
    print("=" * 60)
    print("Clean Schwarzschild QNM - Optimized Shooting Method")
    print("Berti 2009 (M=1): l=2: 0.37367 - 0.08896i")
    print("=" * 60)

    omega0 = coarse_scan()
    omega1 = fine_scan(omega0)
    omega2 = fine_scan(omega1, dr=0.003, di=0.0008, n=30)

    print(f"\nFinal: omega = {omega2.real:.6f} + {omega2.imag:.6f}i")
    print(f"Expected: 0.37367 - 0.08896i")
