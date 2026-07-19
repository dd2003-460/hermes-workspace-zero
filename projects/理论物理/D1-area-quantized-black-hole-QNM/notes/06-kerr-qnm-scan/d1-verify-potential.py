"""Quick check: test a FEW candidate omegas to see if the Wronskian actually dips."""
import numpy as np
from scipy.integrate import solve_ivp

M = 1.0
r_plus = 2.0 * M

def potential_RW(r, l=2, s=2):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1) - 2.0 * M * s**2 / r) / r**2

def rhs_in_r(r, psi, omega):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = potential_RW(r)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot_single(omega, r_match=12.0, eps_horizon=1e-4, r_inf=80.0):
    y0_L = np.array([1.0, -1j * omega / (4.0 * M) / (1.0 - 2.0 * M / (r_plus + eps_horizon))])
    sol_L = solve_ivp(rhs_in_r, [r_plus + eps_horizon, r_match], y0_L,
                     method='RK45', args=(omega,), dense_output=True,
                     max_step=0.5, atol=1e-10, rtol=1e-9)
    if not sol_L.success:
        return np.inf

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

# Test Berti value and nearby values
berti = complex(0.37367, -0.08896)
print("Testing specific omega values:")
test_vals = [
    berti,
    complex(0.374, -0.089),
    complex(0.37, -0.09),
    complex(0.5, -0.07),
    complex(0.272, -0.0315),  # scalar l=2
    complex(0.3, -0.05),
    complex(0.4, -0.06),
    complex(0.217, -0.025),  # previously found
]

for omega in test_vals:
    W = shoot_single(omega)
    if np.isfinite(W):
        print(f"  omega = {omega.real:.5f} + {omega.imag:.5f}i => |W|/norm = {np.abs(W):.6e}")
    else:
        print(f"  omega = {omega.real:.5f} + {omega.imag:.5f}i => |W|/norm = INF (failed)")
