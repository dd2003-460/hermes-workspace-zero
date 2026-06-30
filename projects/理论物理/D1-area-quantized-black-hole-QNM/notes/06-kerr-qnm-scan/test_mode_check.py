#!/usr/bin/env python3
"""
Debug the mode decomposition at r* = infinity.
Check: for Im(omega) < 0, which mode grows and which decays?
"""

import numpy as np

omega = complex(0.37367, -0.08896)

print(f"omega = {omega.real} + {omega.imag}i")
print(f"Re(omega) = {omega.real:.5f}, Im(omega) = {omega.imag:.5f}")

# Mode solutions for d2psi/dr*2 + omega^2*psi = 0 (free wave at infinity)
# psi = A*exp(i*omega*r*) + B*exp(-i*omega*r*)

# For r* >> 0 and Im(omega) < 0:
# |exp(i*omega*r*)| = exp(-Im(omega)*r*) = exp(0.08896*150) = exp(13.34) ~ 6.2e5  -> GROWS
# |exp(-i*omega*r*)| = exp(Im(omega)*r*) = exp(-0.08896*150) = exp(-13.34) ~ 1.6e-6 -> DECAYS

print(f"\nAt r* = 150, Im(omega) = {omega.imag}:")
print(f"  Outgoing exp(i*omega*r*): |ampl| = exp(-{abs(omega.imag)}*150) = exp(0.089*150) = {np.exp(-omega.imag*150):.2e}  -> GROWS")
print(f"  Ingoing exp(-i*omega*r*): |ampl| = exp(omega.imag*150) = exp(-0.089*150) = {np.exp(omega.imag*150):.2e}  -> DECAYS")

# So at r* = infinity:
# The ingoing BC (only exp(i*omega*r*) present) gives a GROWING mode at finite r*
# The outgoing BC (only exp(-i*omega*r*) present) gives a DECAYING mode at finite r*
# But the ingoing mode has finite amplitude (A * exp(growth) ), while B mode is small

# For QNM: at r* -> +inf, we need ONLY outgoing: A*exp(i*omega*r*)
# But this GROWS at finite r* = 150. So |A| << |B| normally.
# At QNM: B -> 0 exactly, A remains finite (but large at finite r*).
# The OUTGOING mode is the A mode.

# So B/A -> 0 is correct. But we're getting ~5e-4, which is small.
# The issue might be that B at r*=150 isn't really near zero because
# the outgoing mode dominates at large r*, making B indeterminate.

# Let me check: integrate from BOTH ends and compute Wronskian.
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0
l = 2

def r_from_rstar(rs):
    t = rs / (2.0 * M) - 1.0
    y = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y)
    for _ in range(30):
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-14:
            break
        r -= dr
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
    return r

def rw_potential(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)

def solve_side(omega, l, rs_start, rs_end, dpsi0_psi0_ratio):
    """Integrate d2psi/dr*2 + (omega^2 - V)*psi = 0 with dpsi/dpsi = ratio at start."""
    def ode(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V = rw_potential(r, l)
        return [Y[1], -(omega**2 - V)*Y[0]]

    sol = solve_ivp(ode, [rs_start, rs_end], [1.0, dpsi0_psi0_ratio],
                   rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
    return sol

ref = complex(0.37367, -0.08896)

# Shoot from near-horizon (rs=-60) with ingoing BC
rs_horizon = -60
sol_h = solve_side(ref, l, rs_horizon, 50, -1j*ref)  # ingoing: dpsi/psi = -i*omega

# Shoot from far (rs=150) with outgoing BC
rs_far = 150
sol_f = solve_side(ref, l, rs_far, 50, +1j*ref)  # outgoing: dpsi/psi = +i*omega

# Evaluate at matching point rs = 50
psi_h, dpsi_h = sol_h.y[:, -1]
psi_f, dpsi_f = sol_f.y[:, -1]

print(f"\nAt matching point r* = 50:")
print(f"  psi_h = {psi_h:.6e}")
print(f"  psi_f = {psi_f:.6e}")

# Wronskian
W = psi_h * dpsi_f - dpsi_h * psi_f
print(f"  Wronskian W = {W:.6e}")
print(f"  |W| = {abs(W):.6e}")

# For a true QNM eigenvalue, W should be zero (two independent solutions are
# actually the same solution, so their Wronskian vanishes).

# Scan for minimum |W|
print(f"\nScan for minimum |W| around Berti:")
best = []
for dr in np.linspace(-0.1, 0.1, 11):
    for di in np.linspace(-0.04, 0.04, 9):
        omega = ref + complex(dr, di)
        sol1 = solve_side(omega, l, -60, 80, -1j*omega)
        sol2 = solve_side(omega, l, 150, 80, 1j*omega)
        ph, dph = sol1.y[:, -1]
        pf, dpf = sol2.y[:, -1]
        W_val = abs(ph * dpf - dph * pf)
        best.append((W_val, omega))
        # Add check for NaN/Inf
        if np.isnan(W_val) or np.isinf(W_val):
            best[-1] = (1e20, omega)

best.sort()
print("\n  Best 5:")
for w_val, w in best[:5]:
    print(f"    omega = {w.real:.5f} + {w.imag:.5f}i, |W| = {w_val:.6e}")
print(f"\n  Berti reference = {ref.real:.5f} + {ref.imag:.5f}i, |W| at ref:")

# Recalculate W at reference
sol1 = solve_side(ref, l, -60, 80, -1j*ref)
sol2 = solve_side(ref, l, 150, 80, 1j*ref)
ph, dph = sol1.y[:, -1]
pf, dpf = sol2.y[:, -1]
W_ref = abs(ph * dpf - dph * pf)
print(f"    |W| = {W_ref:.6e}")

# Also check with different matching points
print(f"\nTesting different matching points (at Berti ref):")
for rs_m in [40, 60, 80, 100]:
    sol1 = solve_side(ref, l, -60, rs_m, -1j*ref)
    sol2 = solve_side(ref, l, 150, rs_m, 1j*ref)
    ph, dph = sol1.y[:, -1]
    pf, dpf = sol2.y[:, -1]
    W_val = abs(ph * dpf - dph * pf)
    print(f"    r*={rs_m}: |W| = {W_val:.6e}")

print("\n" + "=" * 70)
