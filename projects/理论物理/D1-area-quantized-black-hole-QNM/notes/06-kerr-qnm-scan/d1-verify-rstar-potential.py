#!/usr/bin/env python3
"""
Investigate the R-W potential and tortoise coordinate for the known QNM values.
Key question: does V = (1-2M/r)[l(l+1)/r^2 - 6M/r^3] with r* = r + 2M ln(r/2M-1)
give the Berti values 0.37367-0.08896i for l=2, n=0?

Known QNM values from Berti:
  l=2, n=0: omega = 0.37367 - 0.08896i   [Table I, Eq. (4)]
  l=3, n=0: omega = 0.59108 - 0.05902i

Known from Cardoso 2000 (Table 1):
  For s=2, l=2, n=0: omega M = 0.37367 - 0.08896i (same as Berti)
"""

import numpy as np

M = 1.0

print("Known gravitational QNMs (s=2, l>=2):")
print("  l=2, n=0: 0.37367 - 0.08896i  (Berti 2006, Eq. (4))")
print("  l=3, n=0: 0.59108 - 0.05902i")
print("  l=4, n=0: 0.73596 - 0.05221i")
print("  l=5, n=0: 0.86425 - 0.04728i")
print()

# From Berti et al. 2009 (Living Rev.) Eq. (105):
# The Regge-Wheeler equation is:
#   d²Q_lm/dr*² + [ω² - V_lm]Q_lm = 0
# with V_lm = (1-2M/r) * [l(l+1)/r² - 6M/r³]  (for s=2 gravitational)
#
# And r* = r + 2M ln(r/2M - 1)
#
# These are UNDISPUTED standard values. Any QNM solver should reproduce them.
# My solver giving 0.548-0.071i means there's a bug.

# Let me test: what happens if we use V = f(r)[l(l+1)/r^2 + 2M/r^3]
# This is a DIFFERENT sign convention that some authors use.

print("Testing different potential coefficients:")
for l in [2, 3]:
    for c in [6, 2, 12, 0, -6]:
        print(f"\n  l={l}, c={c}")
        for r in [3.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 50.0]:
            f = 1 - 2*M/r
            V_c = f * (l*(l+1)/r**2 - c*M/r**3)
            print(f"    r={r:.1f}: V={V_c:.6f}")

print("\n\nNow testing: does a different potential give Berti values?")
print("Trying V = (1-2M/r)[l(l+1)/r^2 + A/r^3] for various A")

# The Berti 2006 Table I gives:
# s=2 (gravitational):
#   l=2,n=0: omega = 0.37367-0.08896i
# s=0 (scalar):
#   l=2,n=0: omega = 0.27204-0.03150i
#   l=3,n=0: omega = 0.45053-0.01547i

# Note: for scalar s=0, V = (1-2M/r)[l(l+1)/r^2]
# i.e., no r^3 term (c=0)

# For gravitational s=2, V = (1-2M/r)[l(l+1)/r^2 - 6M/r^3] (c=6)
# Some formulations include an extra term: V' = V + (2M/r^3)*something

print("\nV_s = scalar (no r^3 term), V_g = gravitational (c=6)")
print()

# Key insight: the "effective potential" for gravitational QNMs is NOT
# simply V_RW = (1-2M/r)[l(l+1)/r² - 6M/r³]. There's often a subtle
# factor. Let me look at the exact derivation from Chlebowicz & Papapetrou.

# Actually, I think I may have been confusing two different potential forms:
# 1. Regge-Wheeler potential: V_RW = f(r)[l(l+1)/r² - 2M/r³] (for odd parity)
# 2. Zerilli potential: V_Z = (2f(r)/r³) * [(l+1)μ² + 3Mμ/r + 6M²/r²]/[μ²+l²-1+... ]
#    where μ = l(l+1)
# 3. Spherically symmetric scalar: V_S = f(r)[l(l+1)/r² + (1-s²)2M/r³]

# The "2M/r^3" term in RW has coefficient -2M/r^3 not -6M/r^3!
# But some papers multiply by 3 to get the effective gravitational coupling.

# Let me try with c=2 (the scalar coefficient):
print("\nTrying c=2 (V = f[r^2 + l(l+1)]/r^2 - 2M/r^3):")
for l in [2, 3]:
    for r in [6.0, 10.0, 20.0]:
        f = 1 - 2*M/r
        V = f * (l*(l+1)/r**2 - 2*M/r**3)
        print(f"  l={l}, r={r}: V={V:.6f}")

# The confusion: different papers use different notations:
# - Berti eq. (105): V_s^2 = f[r^2 + (1-s^2)2M/r^3] with M = l(l+1)
# - Some authors define V = f[M/r^2 + c'] with c' = -6/r (standard GR)
# - Regge-Wheeler original: V = f[M/r^2 - 2/r^3] where the 2 comes from s=2

# For s=2:
# V = (1-2M/r)[l(l+1)/r^2 + (1-4)2M/r^3]
#   = (1-2M/r)[l(l+1)/r^2 - 6M/r^3]
# This IS the correct form with c=6.

# So the discrepancy with my solver must be in the r* or ODE integration.
# Let me verify r* step by step.

print("\n\nVerifying r* coordinate:")
r_vals = [2.01, 2.5, 3.0, 4.0, 5.0, 6.0, 10.0, 20.0]
for r in r_vals:
    rstar = r + 2*M*np.log(r/(2*M) - 1)
    dr_star_dr = r**2 / (r - 2*M)**2
    # The tortoise coordinate transformation:
    # dr*/dr = (1-2M/r)^{-1} = r^2/(r-2M)^2
    # r* = r + 2M ln(r/2M - 1)
    print(f"  r={r:.2f}M: r*={rstar:.4f}, dr*/dr={dr_star_dr:.4f}")

# Wait - I should double-check dr*/dr
# dr*/dr = d/dr[r + 2M ln(r/2M - 1)]
#        = 1 + 2M * [1/(r/2M - 1)] * [1/2M]
#        = 1 + 2M/(r-2M)
#        = (r-2M+2M)/(r-2M)
#        = r/(r-2M)
#        = (1-2M/r)^{-1} ✓

# But dr*/dr = r^2/(r-2M)^2 = (1-2M/r)^{-1} × [r/(r-2M)] / [r/(r-2M)]
# Actually: r^2/(r-2M)^2 = [r/(r-2M)]^2

# This is NOT r/(r-2M)! It's [r/(r-2M)]^2.

# Standard relation:
# dr*/dr = 1/f = r/(r-2M) for Schwarzschild
# So r* = integral dr/(1-2M/r) = r + 2M ln(r/2M-1)

# The code I used earlier: dr_star_dr = r^2/(r-2M)^2
# This equals (r/(r-2M))^2 = (1+2M/(r-2M))^2
# NOT r/(r-2M)!
# dr*/dr = (1-2M/r)^(-1) = r/(r-2M)

# But wait - what does the code in d1-schw-qnm-shoot-fast.py actually compute?
# It uses r_from_rstar which implements r + 2M ln(r/2M-1), which is CORRECT.
# The dr_star_dr I mentioned was from the AIM code, not the shooting code.

# So the r* IS correct. The issue must be in the ODE integration itself.

# Let me check: is my dpsi/dr* integration correct?
# The ODE is: d²psi/dr*² + (ω² - V) psi = 0
# which is a first-order system:
#   dψ/dr* = π
#   dπ/dr* = -(ω² - V) ψ

# In my RK4, I compute dr/d(rs) using Newton's method, then compute V from r.
# But what about the RK4 steps? Let me trace through the integration.

# The RK4 advances in r* steps, not r steps. At each step, I compute:
# 1. r = r_from_rstar(rs_start)
# 2. V = rw_potential(r, l, c_coeff)
# 3. k1_y = dpsi (this is dψ/drs = π)
# 4. k1_d = -(omega^2 - V) * psi

# This is correct! The system is integrated in r* space.

# Let me check another thing: could the problem be with numerical precision?
# 5000 steps over 120 r* units means step size 0.024. For an oscillatory
# problem, this might be insufficient. The frequency in r* is roughly
# ω near the potential barrier and approaches ω near infinity.
# With ω ~ 0.37, the wavelength is ~2π/|ω| ≈ 16.8 in r* units.
# 5000 steps gives ~237 steps per wavelength. Should be fine.

# Wait - the integration region is:
# Horizon side: from r*=-50 to r*=10 (rs_m) -> 60 units
# Infinity side: from r*=70 to r*=10 -> 60 units
# Total ~120 units of r* integration.

# The step size is (rs_target - rs_start) / N = (10 - (-50)) / 5000 = 60/5000 = 0.012
# 16.8/0.012 ≈ 1400 steps per wavelength -> should be OK.

# But wait, there might be an issue near the horizon.
# The potential V vanishes at r=2M (horizon) but oscillates near the horizon.
# With 5000 steps from r*=-50 to r*=10, we have ~0.012 per step.
# The potential at r=2.01 is V ≈ 0 (it's negligible near the horizon).
# The solution near the horizon is ~exp(-iωr*) = exp(iω|rs|).
# With ω=0.37, this oscillates with period 2π/0.37 ≈ 17.

# 5000 steps over 60 units -> ok.

# Let me try checking if there's a different issue.
# What if the issue is with the boun
