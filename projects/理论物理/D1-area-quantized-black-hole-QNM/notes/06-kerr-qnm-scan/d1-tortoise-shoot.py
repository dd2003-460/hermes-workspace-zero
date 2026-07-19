"""Schwarzschild QNM: Tortoise coordinate shooting method.
Integrate in r* (tortoise) coordinate to eliminate f^2 singularity at horizon.
Check against Berti values and see if my scalar eigenvalue holds.
"""
import numpy as np
from scipy.integrate import solve_ivp, odeint
import time

M = 1.0

def r_star(r):
    """Tortoise coordinate: r* = r + 2M*ln(r/2M - 1) + 3M*ln(3r/2M - 1)"""
    x = r / (2.0 * M)
    return r + 2.0 * M * np.log(x - 1.0) + 3.0 * M * np.log(3.0 * x / 2.0 - 1.0)

def r_star_array(r_arr):
    x = r_arr / (2.0 * M)
    return r_arr + 2.0 * M * np.log(x - 1.0) + 3.0 * M * np.log(3.0 * x / 2.0 - 1.0)

def dr_star_dr(r):
    """dr*/dr = 1/f(r) = r/(r-2M)"""
    return r / (r - 2.0 * M)

def pot_scalar(r, l=2):
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def pot_grav_rw(r, l=2):
    return (1.0 - 2.0 * M / r) * (l * (l + 1) - 6.0 * M / r) / r**2

# ODE in r*: d^2 psi / dr*^2 + (omega^2 - V(r)) * psi = 0
# System: y[0] = psi, y[1] = dpsi/dr*
def rhs_rt(r, y, omega, pot):
    """rhs in terms of r as independent variable (using chain rule).
    Actually, let's integrate in r* space:
    dpsi/dr* = y1
    dy1/dr* = -(omega^2 - V(r(r*))) * y0
    We need to parameterize by r: dr*/dr = 1/f, so d/dr* = f * d/dr
    dpsi/dr* = f * dpsi/dr
    d^2psi/dr*^2 = f * d/dr(f * dpsi/dr)
    So: f * d/dr(f * dpsi/dr) + (omega^2 - V) * psi = 0
    => d^2psi/dr^2 + f'/f * dpsi/dr + (omega^2 - V)/f^2 * psi = 0
    """
    r_val = r
    f = 1.0 - 2.0 * M / r_val
    f_prime = 2.0 * M / r_val**2
    V = pot(r_val)
    # dy1/dr = -(omega^2 - V)/f * y0 - f'/f * y1
    # where y1 = f * dpsi/dr = dpsi/dr*
    dy1_dr = -(omega**2 - V) / f * y[0] - f_prime / f * y[1]
    return np.array([y[1], dy1_dr])
    # y[0] = psi, y[1] = f * dpsi/dr = dpsi/dr*

def shoot_rt(omega, pot, r_match, eps=1e-8, r_inf=80.0):
    """Shooting method in tortoise coordinate.
    Horizon BC: dpsi/dr* = -i*omega * psi  (purely ingoing: psi ~ exp(-i*omega*r*))
    Infinity BC: dpsi/dr* = i*omega * psi  (purely outgoing: psi ~ exp(i*omega*r))
    """
    # Left integration: from horizon to r_match
    r0 = 2.0 * M + eps
    # BC at horizon: psi ~ exp(-i*omega*r*)
    # psi(r0) = 1, dpsi/dr* = -i*omega
    y0_L = np.array([1.0, -1j * omega])
    sol_L = solve_ivp(rhs_rt, [r0, r_match], y0_L, method='RK45', args=(omega, pot),
                      dense_output=True, max_step=1.0, atol=1e-12, rtol=1e-10)
    if not sol_L.success:
        return np.inf

    # Right integration: from r_inf to r_match
    r_inf_val = r_inf
    # BC at infinity: psi ~ exp(i*omega*r*)
    # Wait - at infinity, r* ~ r, so exp(i*omega*r) = exp(i*omega*r*)
    psi_rinf = np.exp(1j * omega * r_star(r_inf_val))
    y0_R = np.array([psi_rinf, 1j * omega * psi_rinf])
    sol_R = solve_ivp(rhs_rt, [r_inf_val, r_match], y0_R, method='RK45', args=(omega, pot),
                      dense_output=True, max_step=1.0, atol=1e-12, rtol=1e-10)
    if not sol_R.success:
        return np.inf

    pL, dL = sol_L.sol(r_match)  # dL = dpsi/dr* from left
    pR, dR = sol_R.sol(r_match)  # dR = dpsi/dr* from right

    W = dL * pR - pL * dR
    norm = abs(pL) * abs(pR)
    return W / norm if norm > 1e-30 else np.inf

def shoot_rt_check(omega, pot, r_match_points, eps=1e-8, r_inf=80.0):
    """Detailed check: print individual values at multiple r_match."""
    results = []
    for rm in r_match_points:
        # Left
        r0 = 2.0 * M + eps
        y0_L = np.array([1.0, -1j * omega])
        sol_L = solve_ivp(rhs_rt, [r0, rm], y0_L, method='RK45', args=(omega, pot),
                          dense_output=True, max_step=1.0, atol=1e-12, rtol=1e-10)
        if not sol_L.success:
            continue
        pL, dL = sol_L.sol(rm)

        # Right
        psi_rinf = np.exp(1j * omega * r_star(r_inf))
        y0_R = np.array([psi_rinf, 1j * omega * psi_rinf])
        sol_R = solve_ivp(rhs_rt, [r_inf, rm], y0_R, method='RK45', args=(omega, pot),
                          dense_output=True, max_step=1.0, atol=1e-12, rtol=1e-10)
        if not sol_R.success:
            continue
        pR, dR = sol_R.sol(rm)

        W = dL * pR - pL * dR
        ratio = dL / pL if abs(pL) > 1e-30 else complex('inf')
        ratio_r = dR / pR if abs(pR) > 1e-30 else complex('inf')

        results.append((rm, W, pL, pR, dL, dR, ratio, ratio_r))
        print(f"  r_match={rm:.1f}: W={W:.6e}, ratio(dpsi/psi)_L={ratio:.4e}, ratio_R={ratio_r:.4e}")

    return results

# ===== Test =====
print("=== Tortoise coordinate verification ===")
print()

# Test A: My scalar eigenvalue
my_scalar = complex(0.273568, -0.026196)
print(f"Test A: Scalar eigenvalue {my_scalar}")
print("-" * 50)
res_a = shoot_rt_check(my_scalar, pot_scalar, [30, 50, 80, 120, 200])
min_W = min(abs(res[1]) for res in res_a if res is not None)
print(f"  Min |W| across r_match: {min_W:.6e}")
print()

# Test B: Berti scalar
berti_scalar = complex(0.27204, -0.03150)
print(f"Test B: Berti scalar {berti_scalar}")
print("-" * 50)
res_b = shoot_rt_check(berti_scalar, pot_scalar, [30, 50, 80, 120, 200])
min_W = min(abs(res[1]) for res in res_b if res is not None)
print(f"  Min |W| across r_match: {min_W:.6e}")
print()

# Test C: Berti gravitational
berti_grav = complex(0.37367, -0.08896)
print(f"Test C: Berti gravitational {berti_grav}")
print("-" * 50)
res_c = shoot_rt_check(berti_grav, pot_grav_rw, [30, 50, 80, 120, 200])
min_W = min(abs(res[1]) for res in res_c if res is not None)
print(f"  Min |W| across r_match: {min_W:.6e}")
print()

# Test D: Scan for scalar eigenvalue (smaller region)
print("Test D: Scan for scalar eigenvalue (tight region)")
print("-" * 50)
best_W = np.inf
best_omega = None
for re in np.linspace(0.26, 0.29, 60):
    for im in np.linspace(-0.035, -0.015, 60):
        omega = complex(re, im)
        W = shoot_rt(omega, pot_scalar, 80.0)
        if np.isfinite(W) and abs(W) < best_W:
            best_W = abs(W)
            best_omega = omega
    if (re - 0.26) / 0.03 < 0.5:
        print(f"  re={re:.3f}, best |W|={best_W:.6e}")
print(f"  Best: {best_omega.real:.6f} + {best_omega.imag:.6f}i, |W|={best_W:.6e}")
print()

# Test E: Scan for gravitational eigenvalue (coarse)
print("Test E: Scan for gravitational eigenvalue (coarse)")
print("-" * 50)
t0 = time.time()
best_W = np.inf
best_omega = None
for re in np.linspace(0.2, 0.6, 40):
    for im in np.linspace(-0.15, -0.02, 40):
        omega = complex(re, im)
        W = shoot_rt(omega, pot_grav_rw, 50.0)
        if np.isfinite(W) and abs(W) < best_W:
            best_W = abs(W)
            best_omega = omega
    if (re - 0.2) / 0.4 < 0.5:
        print(f"  re={re:.3f}, best |W|={best_W:.6e}, t={time.time()-t0:.1f}s")
print(f"  Best: {best_omega.real:.6f} + {best_omega.imag:.6f}i, |W|={best_W:.6e}")
print(f"  Berti grav: 0.37367 - 0.08896i")
