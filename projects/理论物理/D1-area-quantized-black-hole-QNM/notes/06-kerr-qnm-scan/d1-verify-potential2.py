"""Test BOTH the scalar potential and gravitational potential."""
import numpy as np
from scipy.integrate import solve_ivp

M = 1.0
r_plus = 2.0 * M

def pot_scalar(r):
    f = 1.0 - 2.0 * M / r
    return f * 6.0 / r**2

def pot_grav_rw(r):
    f = 1.0 - 2.0 * M / r
    return f * (6.0 - 6.0 * M / r) / r**2

def pot_grav_v2(r):
    f = 1.0 - 2.0 * M / r
    return f * (6.0 - 8.0 * M / r) / r**2

def rhs_in_r(r, psi, omega, pot_fn):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot_fn(r)
    d2psi_dr2 = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)
    return np.array([psi[1], d2psi_dr2])

def shoot_single(omega, pot_fn, r_match=12.0, eps_horizon=1e-4, r_inf=80.0):
    y0_L = np.array([1.0, -1j * omega / (4.0 * M) / (1.0 - 2.0 * M / (r_plus + eps_horizon))])
    sol_L = solve_ivp(rhs_in_r, [r_plus + eps_horizon, r_match], y0_L,
                     method='RK45', args=(omega, pot_fn), dense_output=True,
                     max_step=0.5, atol=1e-10, rtol=1e-9)
    if not sol_L.success:
        return np.inf
    psi_r0 = np.exp(1j * omega * r_inf)
    y0_R = np.array([psi_r0, 1j * omega * psi_r0])
    sol_R = solve_ivp(rhs_in_r, [r_inf, r_match], y0_R,
                     method='RK45', args=(omega, pot_fn), dense_output=True,
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

print("=== Scalar potential V = f * 6/r^2 ===")
print("Berti ref: 0.27204 - 0.03150i")
for o_re, o_im in [(0.27204, -0.03150), (0.270, -0.030), (0.300, -0.040), (0.250, -0.020)]:
    W = shoot_single(complex(o_re, o_im), pot_scalar)
    print(f"  {o_re:.5f}+{o_im:.5f}i => |W|={np.abs(W):.6e}")

print("\n=== Gravitational V = f*(6 - 6/r)/r^2 ===")
print("Berti ref: 0.37367 - 0.08896i")
for o_re, o_im in [(0.37367, -0.08896), (0.4, -0.07), (0.35, -0.09), (0.5, -0.07)]:
    W = shoot_single(complex(o_re, o_im), pot_grav_rw)
    print(f"  {o_re:.5f}+{o_im:.5f}i => |W|={np.abs(W):.6e}")

print("\n=== Gravitational V = f*(6 - 8/r)/r^2 ===")
print("Berti ref: 0.37367 - 0.08896i")
for o_re, o_im in [(0.37367, -0.08896), (0.4, -0.07), (0.35, -0.09), (0.5, -0.07)]:
    W = shoot_single(complex(o_re, o_im), pot_grav_v2)
    print(f"  {o_re:.5f}+{o_im:.5f}i => |W|={np.abs(W):.6e}")
