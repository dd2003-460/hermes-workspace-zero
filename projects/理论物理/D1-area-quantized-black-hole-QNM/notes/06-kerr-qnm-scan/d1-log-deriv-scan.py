"""Schwarzschild QNM: Logarithmic derivative matching.
W = (ratio_L - ratio_R) * pL * pR grows exponentially, so use ratio = dpsi/dr* / psi as the eigenvalue indicator.
Eigenvalue: ratio_L(r_match) == ratio_R(r_match) (complex equality, independent of r_match).
"""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0

def r_star(r):
    x = r / (2.0 * M)
    return r + 2.0 * M * np.log(x - 1.0) + 3.0 * M * np.log(3.0 * x / 2.0 - 1.0)

def pot_scalar(r, l=2):
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def pot_grav_rw(r, l=2):
    return (1.0 - 2.0 * M / r) * (l * (l + 1) - 6.0 * M / r) / r**2

def rhs_rt(r, y, omega, pot):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot(r)
    dy1_dr = -(omega**2 - V) / f * y[0] - f_prime / f * y[1]
    return np.array([y[1], dy1_dr])

def log_deriv(omega, pot, r_match, eps=1e-8, r_inf=80.0, direction='L'):
    """Compute logarithmic derivative dpsi/dr* / psi at r_match."""
    if direction == 'L':
        r0 = 2.0 * M + eps
        y0 = np.array([1.0, -1j * omega])
        sol = solve_ivp(rhs_rt, [r0, r_match], y0, method='RK45', args=(omega, pot),
                        dense_output=True, max_step=1.0, atol=1e-14, rtol=1e-11)
    else:
        psi_rinf = np.exp(1j * omega * r_star(r_inf))
        y0 = np.array([psi_rinf, 1j * omega * psi_rinf])
        sol = solve_ivp(rhs_rt, [r_inf, r_match], y0, method='RK45', args=(omega, pot),
                        dense_output=True, max_step=1.0, atol=1e-14, rtol=1e-11)

    if not sol.success:
        return None

    psi, dpsi = sol.sol(r_match)
    if abs(psi) < 1e-30:
        return None
    return dpsi / psi

def shooting_function(omega, pot, r_match=80.0, r_inf=80.0):
    """Distance between left and right logarithmic derivatives.
    Returns |ratio_L - ratio_R| / |ratio_R| — relative complex distance.
    """
    rL = log_deriv(omega, pot, r_match, direction='L', r_inf=r_inf)
    rR = log_deriv(omega, pot, r_match, direction='R', r_inf=r_inf)
    if rL is None or rR is None:
        return np.inf
    return abs(rL - rR) / (abs(rR) + 1e-30)

# ===== Test: verify the new metric =====
print("=== Verify: log-derivative matching ===")
print()

# Check at multiple r_match for each test value
test_vals = [
    ("My scalar 0.27357-0.02620i", complex(0.273568, -0.026196), pot_scalar),
    ("Berti scalar 0.27204-0.03150i", complex(0.27204, -0.03150), pot_scalar),
    ("Berti grav 0.37367-0.08896i", complex(0.37367, -0.08896), pot_grav_rw),
]

for label, omega, pot in test_vals:
    print(f"{label}:")
    for rm in [30, 50, 80, 120]:
        rd = shooting_function(omega, pot, r_match=rm)
        rL = log_deriv(omega, pot, rm, direction='L')
        rR = log_deriv(omega, pot, rm, direction='R')
        if rL is not None and rR is not None:
            print(f"  r_match={rm}: rel_dist={rd:.6e}, ratio_L={rL:.6e}, ratio_R={rR:.6e}")
    print()

# ===== Scan for scalar eigenvalue =====
print("=== Scan: scalar potential eigenvalue ===")
t0 = time.time()
best_rel = np.inf
best_omega = None
for re in np.linspace(0.25, 0.30, 100):
    for im in np.linspace(-0.04, -0.01, 100):
        omega = complex(re, im)
        rel = shooting_function(omega, pot_scalar, r_match=80.0)
        if rel < best_rel:
            best_rel = rel
            best_omega = omega
    if (re - 0.25) / 0.05 < 0.4:
        print(f"  re={re:.3f}, best rel_dist={best_rel:.6e}, t={time.time()-t0:.1f}s")
print(f"\nScalar best: {best_omega.real:.6f} + {best_omega.imag:.6f}i, rel_dist={best_rel:.6e}")
print(f"  Berti scalar: 0.27204 - 0.03150i")

# Fine scan
print("\nFine scan scalar:")
for dr, di in [(0.01, 0.003), (0.004, 0.0012), (0.0016, 0.0005)]:
    best2_rel = np.inf
    best2_omega = best_omega
    for re in np.linspace(best_omega.real - dr, best_omega.real + dr, 60):
        for im in np.linspace(best_omega.imag - di, best_omega.imag + di, 60):
            omega = complex(re, im)
            rel = shooting_function(omega, pot_scalar, r_match=80.0)
            if rel < best2_rel:
                best2_rel = rel
                best2_omega = omega
    best_omega, best_rel = best2_omega, best2_rel
    print(f"  [{dr}, {di}]: {best_omega.real:.6f} + {best_omega.imag:.6f}i, rel_dist={best_rel:.6e}")
print(f"FINAL scalar: {best_omega.real:.8f} + {best_omega.imag:.8f}i")
print()

# ===== Scan for gravitational eigenvalue =====
print("=== Scan: gravitational potential eigenvalue ===")
t0 = time.time()
best_rel = np.inf
best_omega = None
for re in np.linspace(0.2, 0.6, 80):
    for im in np.linspace(-0.15, -0.01, 80):
        omega = complex(re, im)
        rel = shooting_function(omega, pot_grav_rw, r_match=50.0)
        if rel < best_rel:
            best_rel = rel
            best_omega = omega
    if (re - 0.2) / 0.4 < 0.4:
        print(f"  re={re:.3f}, best rel_dist={best_rel:.6e}, t={time.time()-t0:.1f}s")
print(f"\nGrav best: {best_omega.real:.6f} + {best_omega.imag:.6f}i, rel_dist={best_rel:.6e}")
print(f"  Berti grav: 0.37367 - 0.08896i")

# Fine scan
print("\nFine scan grav:")
for dr, di in [(0.05, 0.015), (0.02, 0.006), (0.008, 0.0025)]:
    best2_rel = np.inf
    best2_omega = best_omega
    for re in np.linspace(best_omega.real - dr, best_omega.real + dr, 60):
        for im in np.linspace(best_omega.imag - di, best_omega.imag + di, 60):
            omega = complex(re, im)
            rel = shooting_function(omega, pot_grav_rw, r_match=50.0)
            if rel < best2_rel:
                best2_rel = rel
                best2_omega = omega
    best_omega, best_rel = best2_omega, best2_rel
    print(f"  [{dr}, {di}]: {best_omega.real:.6f} + {best_omega.imag:.6f}i, rel_dist={best_rel:.6e}")
print(f"FINAL grav: {best_omega.real:.8f} + {best_omega.imag:.8f}i")
