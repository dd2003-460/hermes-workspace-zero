"""Test if removing 4M from horizon BC fixes the Berti value."""
import numpy as np
from scipy.integrate import solve_ivp

M = 1.0

def pot_scalar(r, l=2):
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def rhs_in_r(r, psi, omega, l=2):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot_scalar(r, l)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot_v1(omega, l=2, r_match=12.0, eps=1e-4, r_inf=80.0):
    """Current: psi ~ exp(-i*omega*r*/(4M)) => dpsi/dr = -i*omega/(4M*f)"""
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

def shoot_v2(omega, l=2, r_match=12.0, eps=1e-4, r_inf=80.0):
    """Change: psi ~ exp(-i*omega*r*) => dpsi/dr = -i*omega/f
    Removes the 4M factor."""
    r0 = 2.0 * M + eps
    f0 = 1.0 - 2.0 * M / r0
    y0_L = np.array([1.0, -1j * omega / f0])  # No 4M!
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

# Test: sweep eps for both versions, using Berti scalar value
print("Testing Berti scalar value (0.27204 - 0.03150i):")
print("====================================")
beta = complex(0.27204, -0.03150)

for eps in [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
    W1 = shoot_v1(beta, eps=eps)
    W2 = shoot_v2(beta, eps=eps)
    print(f"  eps={eps:.0e}: v1(4M) |W|={np.abs(W1):.6e}, v2(1) |W|={np.abs(W2):.6e}")

# Also test with my found value
print("\nTesting my found value (0.273568 - 0.026196i):")
myval = complex(0.273568, -0.026196)
for eps in [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
    W1 = shoot_v1(myval, eps=eps)
    W2 = shoot_v2(myval, eps=eps)
    print(f"  eps={eps:.0e}: v1(4M) |W|={np.abs(W1):.6e}, v2(1) |W|={np.abs(W2):.6e}")

# Now let's also test: what is the minimum for v2 (no 4M)?
print("\nQuick sweep for v2 (no 4M) around Berti scalar region:")
best_W2 = np.inf
best_omega2 = None
for re in np.linspace(0.25, 0.30, 50):
    for im in np.linspace(-0.035, -0.015, 40):
        W = shoot_v2(complex(re, im))
        if np.isfinite(W) and np.abs(W) < best_W2:
            best_W2 = np.abs(W)
            best_omega2 = complex(re, im)
print(f"  v2 best: {best_omega2.real:.5f} + {best_omega2.imag:.5f}i, |W|={best_W2:.6e}")
