#!/usr/bin/env python3
"""
Simple shooting test with fine scanning to understand what's happening.
Track the exact solution structure at various r* values.
"""
import numpy as np
from scipy.integrate import solve_ivp

M = 1.0

def rstar_of(r):
    return r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)

def r_from_rstar(rs):
    from scipy.special import lambertw
    t = rs / (2.0 * M) - 1.0
    if t > 10:
        y = t - np.log(t) + np.log(t) / t
    else:
        y = lambertw(np.exp(t), k=0).real
    r = 2.0 * M * (1.0 + y)
    for _ in range(30):
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
            continue
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        delta = (rs_calc - rs) / drstar_dr
        if abs(delta) < 1e-16 * max(abs(r), 1e-14):
            break
        r -= delta
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
    return r

def rw_potential(r, l):
    return (1.0 - 2.0 * M / r) * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)

def integrate_shoot(omega, l, rs_start, rs_end, psi0, dpsi0):
    """Integrate d2psi/dr*2 + (w^2 - V)*psi = 0"""
    def ode(rs, Y):
        r = r_from_rstar(rs)
        V = rw_potential(r, l)
        psi, dpsi = Y
        return [dpsi, -(omega**2 - V) * psi]

    sol = solve_ivp(
        lambda rs, Y: ode(rs, Y),
        [rs_start, rs_end],
        [complex(psi0), complex(dpsi0)],
        max_step=0.2,
        rtol=1e-12,
        atol=1e-14,
        dense_output=True
    )
    return sol

# Berti reference
omega_ref = complex(0.37367, -0.08896)
l = 2

# Shoot from horizon with ingoing BC
r_start = 2.02
rs_start = rstar_of(r_start)
r_end = 6.0
rs_end_40 = rstar_of(r_end)  # r* ≈ 40
r_end2 = 10.0
rs_end2_60 = rstar_of(r_end2)

print(f"r_start = {r_start}, r*_start = {rs_start:.6f}")
print(f"r_end  = {r_end}, r*_end_40 = {rs_end_40:.6f}")
print(f"r_end2 = {r_end2}, r*_end2_60 = {rs_end2_60:.6f}")
print()

# Integrate with ingoing BC
sol = integrate_shoot(omega_ref, l, rs_start, rs_end_40, 1.0, -1j * omega_ref)

# Get solution at rs ≈ 40 (r ≈ 6)
psi_end, dpsi_end = sol.y[:, -1]

print(f"At rs ≈ 40 (r = {r_end}):")
print(f"  psi = {psi_end:.6e}")
print(f"  dpsi = {dpsi_end:.6e}")

# Decompose: d2psi/ds*2 + (w^2 - V)*psi = 0
# Near infinity: V ~ 0, so d2psi/ds*2 + w^2*psi = 0
# Solution: psi = A*exp(iws*) + B*exp(-iws*)
# psi' = iωA*exp(iωs*) - iωB*exp(-iωs*)
# At a finite rs: we can decompose
omega = omega_ref

# A and B from:
# psi = A*exp(iωrs) + B*exp(-iωrs)
# psi' = iωA*exp(iωrs) - iωB*exp(-iωrs)
# => A*exp(iωrs) = (psi' + iωψ) / (2iω)
# => B*exp(-iωrs) = (psi' - iωψ) / (-2iω)

Aexp = (dpsi_end + 1j * omega * psi_end) / (2.0 * 1j * omega)
Bexp = (dpsi_end - 1j * omega * psi_end) / (-2.0 * 1j * omega)

print(f"\nDecomposition at rs={rs_end_40:.1f}:")
print(f"  A*exp(iωr*) = {Aexp:.6e}")
print(f"  B*exp(-iωr*) = {Bexp:.6e}")
print(f"  |A| = {abs(Aexp):.6e}")
print(f"  |B| = {abs(Bexp):.6e}")
print(f"  |B/A| = {abs(Bexp / Aexp):.6e}")

# Now check the behavior of each mode as we approach infinity
# The A mode (outgoing) should GROW with r*
# The B mode (ingoing) should DECAY with r* (for Im(ω)<0)

# Actually for Im(ω) < 0:
# exp(iωrs) with rs large: Im(ω)<0 means exp(i*(Re+i*Im)*rs) = exp(i*Re*rs)*exp(-Im*rs)
# Since Im < 0: exp(-Im*rs) = exp(|Im|*rs) -> GROWS
# exp(-iωrs) with Im(ω)<0: exp(-i*(Re+i*Im)*rs) = exp(-i*Re*rs)*exp(+Im*rs)
# Since Im < 0: exp(Im*rs) = exp(-|Im|*rs) -> DECAYS

print(f"\nFor Im(ω) = {omega.imag:.5f} < 0:")
print(f"  Outgoing exp(iωr*) GROWS as exp(|ω_i| * r*) ~ exp({abs(omega.imag):.5f} * {rs_end_40:.1f}) = {np.exp(abs(omega.imag)*rs_end_40):.2e}")
print(f"  Ingoing exp(-iωr*) DECAYS as exp(-|ω_i| * r*) ~ exp(-{abs(omega.imag):.5f} * {rs_end_40:.1f}) = {np.exp(-abs(omega.imag)*rs_end_40):.2e}")

# Now shoot from far infinity INWARD
r_far = 50.0
rs_far = rstar_of(r_far)
print(f"\nr_far = {r_far}, r*_far = {rs_far:.1f}")

# Outgoing BC at far infinity
sol_in = integrate_shoot(omega_ref, l, rs_far, rs_end_40, 1.0, +1j * omega_ref)

psi_in_end, dpsi_in_end = sol_in.y[:, -1]
Aexp_in, Bexp_in = (dpsi_in_end + 1j*omega*psi_in_end)/(2j*omega), (dpsi_in_end - 1j*omega*psi_in_end)/(-2j*omega)

print(f"\nIntegrating INWARD from r* = {rs_far:.1f}:")
print(f"  psi_in = {psi_in_end:.6e}")
print(f"  |A_in| = {abs(Aexp_in):.6e}")
print(f"  |B_in| = {abs(Bexp_in):.6e}")

# Wronskian at matching point
W = psi_end * dpsi_in_end - dpsi_end * psi_in_end
W_norm = abs(W) / max(abs(psi_end) * abs(psi_in_end), 1e-100)
print(f"\nWronskian |W|/(|ψ1||ψ2|) = {W_norm:.6e}")
print(f"  psi1 = {psi_end:.6e}, psi2 = {psi_in_end:.6e}")
print(f"  dpsi1 = {dpsi_end:.6e}, dpsi2 = {dpsi_in_end:.6e}")
