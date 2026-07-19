"""
Corrected Schwarzschild QNM solver.
Fixed potential: V = f * (l*(l+1) - 2*M*s^2/r) / r^2

Where s = spin weight: s=0 for scalar, s=2 for gravitational.
For l=2, s=2: V = f * (6 - 6M/r) / r^2 = (1-2M/r) * 6*(r-M) / r^3

Berti 2009 (M=1):
  l=2, s=0/2: omega = 0.37367 - 0.08896i
  l=3, s=0/2: omega = 0.59108 - 0.05902i
  l=4, s=0/2: omega = 0.75946 - 0.04535i
"""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0
r_plus = 2.0 * M

def potential_RW(r, l=2, s=2):
    """Correct Regge-Wheeler potential."""
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1) - 2.0 * M * s**2 / r) / r**2

def rhs_in_r(r, psi, omega):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = potential_RW(r)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot_single(omega, r_match=12.0, eps_horizon=1e-4, r_inf=80.0):
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

def coarse_scan(l=2, s=2):
    reals = np.linspace(0.1, 1.0, 45)
    imags = np.linspace(-0.15, -0.01, 45)

    best_W = np.inf
    best_omega = None

    print(f"  l={l}, s={s} coarse scan ({len(reals)}x{len(imags)})")
    t0 = time.time()
    for i, r in enumerate(reals):
        for j, im in enumerate(imags):
            omega = complex(r, im)
            W = shoot_single(omega)
            if np.isfinite(W) and np.abs(W) < best_W:
                best_W = np.abs(W)
                best_omega = omega
        if i % 15 == 0:
            print(f"    Row {i+1}/{len(reals)}, best |W| = {best_W:.6e}")

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s. Best: {best_omega.real:.4f} + {best_omega.imag:.4f}i")
    return best_omega

def fine_scan(omega0, l=2, s=2, dr=0.015, di=0.004, n=40):
    r_range = np.linspace(omega0.real - dr, omega0.real + dr, n)
    i_range = np.linspace(omega0.imag - di, omega0.imag + di, n)

    best_W = np.inf
    best_omega = omega0
    count = 0

    t0 = time.time()
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
    print(f"  Refined: {best_omega.real:.6f} + {best_omega.imag:.6f}i, |W| = {best_W:.6e}")
    return best_omega

if __name__ == "__main__":
    print("=" * 65)
    print("Corrected Schwarzschild QNM - Shooting Method")
    print("V = f * (l*(l+1) - 2Ms^2/r) / r^2")
    print("=" * 65)

    # l=2, s=2 (gravitational)
    print("\n--- l=2, s=2 (gravitational) ---")
    print("Berti ref: 0.37367 - 0.08896i")
    o0 = coarse_scan(l=2, s=2)
    o1 = fine_scan(o0, l=2, s=2, dr=0.02, di=0.005, n=40)
    o2 = fine_scan(o1, l=2, s=2, dr=0.005, di=0.0012, n=30)
    print(f"\n  FINAL: {o2.real:.6f} + {o2.imag:.6f}i")

    # l=3, s=2 (gravitational)
    print("\n--- l=3, s=2 (gravitational) ---")
    print("Berti ref: 0.59108 - 0.05902i")
    o0 = coarse_scan(l=3, s=2)
    o1 = fine_scan(o0, l=3, s=2, dr=0.02, di=0.005, n=40)
    o2 = fine_scan(o1, l=3, s=2, dr=0.005, di=0.0012, n=30)
    print(f"\n  FINAL: {o2.real:.6f} + {o2.imag:.6f}i")

    # l=2, s=0 (scalar)
    print("\n--- l=2, s=0 (scalar) ---")
    print("Berti ref: 0.27204 - 0.03150i")
    o0 = coarse_scan(l=2, s=0)
    o1 = fine_scan(o0, l=2, s=0, dr=0.015, di=0.004, n=40)
    o2 = fine_scan(o1, l=2, s=0, dr=0.005, di=0.0012, n=30)
    print(f"\n  FINAL: {o2.real:.6f} + {o2.imag:.6f}i")
