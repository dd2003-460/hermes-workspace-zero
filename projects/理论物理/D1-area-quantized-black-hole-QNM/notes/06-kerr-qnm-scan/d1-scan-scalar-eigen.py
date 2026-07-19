"""Search for true eigenvalue under scalar potential V = f * l(l+1)/r^2."""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0

def pot_scalar(r, l=2):
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def rhs_in_r(r, psi, omega, l=2):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot_scalar(r, l)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot(omega, l=2, r_match=12.0, eps=1e-4, r_inf=80.0):
    r0 = 2.0 * M + eps
    f0 = 1.0 - 2.0 * M / r0
    y0_L = np.array([1.0, -1j * omega / (4.0 * M) / f0])
    sol_L = solve_ivp(rhs_in_r, [r0, r_match], y0_L, method='RK45',
                     args=(omega, l), dense_output=True, max_step=0.5,
                     atol=1e-10, rtol=1e-9)
    if not sol_L.success:
        return np.inf
    psi_r0 = np.exp(1j * omega * r_inf)
    y0_R = np.array([psi_r0, 1j * omega * psi_r0])
    sol_R = solve_ivp(rhs_in_r, [r_inf, r_match], y0_R, method='RK45',
                     args=(omega, l), dense_output=True, max_step=0.5,
                     atol=1e-10, rtol=1e-9)
    if not sol_R.success:
        return np.inf
    pL, dL = sol_L.sol(r_match)
    pR, dR = sol_R.sol(r_match)
    W = dL * pR - pL * dR
    norm = np.abs(pL) * np.abs(pR)
    return W / norm if norm > 1e-30 else np.inf

# Fine grid around the minimum we found
print("Fine grid search for scalar potential eigenvalue (l=2):")
print("Region: re [0.15, 0.40], im [-0.05, -0.01]")
t0 = time.time()

reals = np.linspace(0.15, 0.40, 100)
imags = np.linspace(-0.05, -0.01, 100)

best_W = np.inf
best_omega = None

for r in reals:
    for i in imags:
        omega = complex(r, i)
        W = shoot(omega)
        if np.isfinite(W) and np.abs(W) < best_W:
            best_W = np.abs(W)
            best_omega = omega
    if (r - 0.15) / 0.25 < 0.3:
        print(f"  ... {r:.3f}, best |W| = {best_W:.6e}")

elapsed = time.time() - t0
print(f"Done in {elapsed:.1f}s")
print(f"Best: omega = {best_omega.real:.6f} + {best_omega.imag:.6f}i, |W| = {best_W:.6e}")

# Also check: is |W| going to zero anywhere? The minimum should be near 0 for true eigenvalue.
# Search in a tighter region
print("\nVery fine search around best:")
dr = 0.01
di = 0.002
reals2 = np.linspace(best_omega.real - dr, best_omega.real + dr, 60)
imags2 = np.linspace(best_omega.imag - di, best_omega.imag + di, 60)
t0 = time.time()
best2_W = np.inf
best2_omega = best_omega
for r in reals2:
    for i in imags2:
        omega = complex(r, i)
        W = shoot(omega)
        if np.isfinite(W) and np.abs(W) < best2_W:
            best2_W = np.abs(W)
            best2_omega = omega
elapsed = time.time() - t0
print(f"Done in {elapsed:.1f}s")
print(f"Refined: omega = {best2_omega.real:.6f} + {best2_omega.imag:.6f}i, |W| = {best2_W:.6e}")
