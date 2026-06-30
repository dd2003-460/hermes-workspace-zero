#!/usr/bin/env python3
"""
Derive the ODE in y = 1-2M/r and get the EXPLICIT coefficients.
y=0: HORIZON, y=1: INFINITY
"""

import numpy as np
import sympy as sp

M_val = 1.0
l_val = 2

M_s = sp.Symbol('M', positive=True)
w_s = sp.Symbol('w')
l_s = sp.Symbol('l')
y_s = sp.Symbol('y')

# ODE in y:
# f(y) = y^2*(1-y)^2
# P(y) = f'(y)/f(y) = 2(2y-1)/(y(y-1))
# Q(y) = 4M^2(w^2 - V)/f^2
# V = y*(1-y)^2/(4M^2) * [l(l+1) - 3(1-y)]

P = 2 * (2*y_s - 1) / (y_s * (y_s - 1))
V = y_s * (1 - y_s)**2 / (4 * M_s**2) * (l_s * (l_s + 1) - 3 * (1 - y_s))
Q = (4 * M_s**2 * w_s**2 - y_s * (1 - y_s)**2 * (l_s*(l_s+1) - 3*(1-y_s))) / (y_s**4 * (1 - y_s)**4)

print("=== ODE in y = 1-2M/r ===")
print("y=0: HORIZON, y=1: INFINITY")
print(f"P(y) = {sp.simplify(P)}")
print(f"Q(y) = {sp.simplify(Q)}")
print()

# Singularity analysis
# At y=0 (horizon): look at Q ~ 4M^2*w^2 / y^4
# This is an irregular singular point of rank 1.
# For rank 1, the asymptotic behavior is psi ~ exp(c/y + ...).
# substitute psi = exp(integral(A/y^2 + B/y + ...) dy) = exp(-A/y + B*ln(y) + ...)
# = y^B * exp(-A/y)
#
# Substitute into psi'' + P*psi' + Q*psi = 0
# Q ~ 4M^2*w^2 / y^4 at leading order
# We need A^2 = -4M^2*w^2 (from leading term of Q)
# => A = ±2iMw
#
# For sub-leading B: solve from next order in Q expansion

print("=== Asymptotic analysis at y=0 (horizon) ===")
# Q near y=0:
Q_y0 = sp.series(Q, y_s, 0, 5)
print(f"Q near y=0: {Q_y0}")

print("\n=== Asymptotic analysis at y=1 (infinity) ===")
# Q near y=1:
Q_y1 = sp.series(Q, y_s, 1, 5)
print(f"Q near y=1: {Q_y1}")

# Now, the power series expansion should be done around a regular point.
# For Leaver's method, we expand around ONE of the singular points.
# Convention: expand around y=0 (horizon).
#
# The solution with ingoing BC at horizon:
# psi ~ y^(rho_0) * exp(...) where rho_0 comes from the regular singular part
#
# But y=0 is an IRREGULAR singular point!
# For irregular singular point of rank 1:
# psi = exp(sigma(1/y)) * y^r * phi(y), where phi is analytic at y=0.
#
# sigma(1/y) = A/y + B*ln(y) + C + D*y + ...
# We found A = ±2iMw (from A^2 = -Q_40 where Q ~ Q_40/y^4)
# Q_40 = 4M^2*w^2, so A = ±2iMw

# For ingoing waves at horizon: psi ~ exp(-2iMw/y) (matching exp(-i*w*r*))
# For outgoing waves at horizon: psi ~ exp(2iMw/y)

# But wait - we need the ingoing OUT at the horizon (which is what QNMs need).
# Actually for black holes, QNMs require:
# - INGOING at horizon: psi ~ exp(-i*omega*r*) ~ exp(-2i*M*w/y) as y->0
# - OUTGOING at infinity: psi ~ exp(+i*omega*r*) ~ exp(+2i*M*w/(1-y)) as y->1
#   Wait, r* near y=1...

# Let me check r* near y=1:
# r* = r + 2M*ln(r/2M - 1) = 2M/(1-y) + 2M*ln(2M/(1-y) - 1)
# For y near 1 (r near infinity):
# r* ~ 2M/(1-y) + 2M*ln(2M/(1-y))  [for small 1-y, since r/2M >> 1]
# ~ 2M/(1-y) - 2M*ln(1-y) + 2M*ln(2M)

print("\n=== r* expansion ===")
r_star_horizon = sp.series(2*M_s/(1-y_s) + 2*M_s*sp.log(2*M_s/(1-y_s) - 1), y_s, 0, 3)
r_star_inf = sp.series(2*M_s/(1-y_s) + 2*M_s*sp.log(2*M_s/(1-y_s) - 1), y_s, 1, 3)
print(f"r* near y=0 (horizon): {r_star_horizon}")
print(f"r* near y=1 (infinity): {r_star_inf}")

# At horizon y->0: r* ~ -2M/y + ...  (actually from log term too?)
# Wait, as y->0: r = 2M/(1-y) ~ 2M, so r/2M-1 ~ 0
# r* ~ 2M + 2M*ln(r/2M-1) = 2M + 2M*ln(2M/(1-y) - 2M) = 2M + 2M*ln(2M*y/(1-y))
# r* ~ 2M + 2M*ln(2M) + 2M*ln(y) - 2M*ln(1-y) ~ const + 2M*ln(y) (since ln(1-y) ~ 0)
#
# So: exp(-i*w*r*) ~ exp(-i*w*2M*ln(y)) = y^(-2iMw) near y=0

# At infinity y->1: r* ~ 2M/(1-y) + 2M*ln(2M/(1-y))
# = 2M/(1-y) - 2M*ln(1-y) + const
# exp(+i*w*r*) ~ exp(i*w*2M/(1-y)) * (1-y)^(-2iMw) near y=1

print("\n=== Asymptotic behavior ===")
print("Near horizon (y=0):")
print("  r* ~ 2M*ln(y) + const")
print("  Ingoing: psi ~ y^(-2iMw)")
print("  Outgoing: psi ~ y^(+2iMw)")
print("Near infinity (y=1):")
print("  r* ~ 2M/(1-y) - 2M*ln(1-y) + const")
print("  Outgoing: psi ~ (1-y)^(-2iMw) * exp(2iMw/(1-y))")
print("  Ingoing: psi ~ (1-y)^(+2iMw) * exp(-2iMw/(1-y))")

# For QNM BCs:
# - Horizon (y=0): INGOING => psi ~ y^(-2iMw) = y^{rho_0}
# - Infinity (y=1): OUTGOING => psi ~ (1-y)^(-2iMw) * exp(2iMw/(1-y))

# The factorization is:
# psi(y) = y^{rho_0} * (1-y)^{rho_1} * exp(alpha/(1-y)) * phi(y)
# where:
# rho_0 = -2iMw  (ing at horizon)
# rho_1 = -2iMw  (out at infinity)  -- wait, the power factor
# alpha = 2iMw   (from exp(2iMw/(1-y)))

# Hmm, but we also have the polynomial exp factor at infinity.
# Actually: exp(+i*w*r*) ~ exp(2iMw/(1-y)) * (1-y)^{+2iMw}
# So the outgoing factor at infinity is (1-y)^{-2iMw} * exp(2iMw/(1-y))? No...
#
# r* = 2M/(1-y) - 2M*ln(1-y) + const (near y=1)
# exp(+iwr*) = exp(2iMw/(1-y)) * exp(-2iMw*ln(1-y))
#            = exp(2iMw/(1-y)) * (1-y)^{-2iMw}

# So: at infinity (outgoing): psi ~ exp(2iMw/(1-y)) * (1-y)^{-2iMw}

# And: at horizon (ingoing): psi ~ y^{-2iMw}
# Note: r* ~ 2M*ln(y) near y=0, so exp(-iwr*) ~ y^{-2iMw}

# Now, for Leaver's method:
# We expand phi as a power series in y around y=0 (horizon).
# psi(y) = y^{-2iMw} * (1-y)^{-2iMw} * exp(2iMw/(1-y)) * phi(y)
#
# phi(y) is analytic at y=0, so phi(y) = sum_{n=0}^{inf} a_n * y^n
# The QNM condition requires the continued fraction to converge.

# But this is very complicated due to the exp factor.
# Alternative: use variable z = 1-y (z=1 at horizon, z=0 at infinity)
# Actually, Leaver usually expands in a coordinate where the series
# has singular points at both boundaries.

# Let me try a different approach: use the series expansion in the full
# space. The idea of Leaver's method is:
# 1. The ODE has 2 physical singularities and (optionally) 1 auxiliary
# 2. Factor out both boundary behaviors
# 3. The remaining function satisfies a 3-term recurrence
# 4. Convergence condition gives the eigenvalue

# For the REGGE-WHEELER equation, the singularity at y=0 is irregular (rank 1).
# So we can't directly use Frobenius expansion at y=0.

# However, we CAN use the asymptotic iteration method or
# a slightly different series expansion.

# Alternative: change variable to tau = y * (1-y) or similar.
# Or use the transformation: x = y/(y-1) which maps:
# y=0 -> x=0, y=1 -> x=-1

# Actually, for the practical implementation, let me just try the
# asymptotic iteration method (AIM), which has a clean algorithm.

print("\n=== AIM Implementation ===")
print("For the ODE: psi'' + lambda_1(y)*psi' + lambda_0(y)*psi = 0")
print("AIM iteration: psi^{(n+1)}(y) = alpha_n(y) * psi'(y)")
print("alpha_{n+1} = alpha_n' + lambda_0*psi + lambda_1*alpha_n")
print("Condition: delta_n(y) = alpha_n' - alpha_n*lambda_1 = 0")
print("For QNM: delta_n must have a y-independent solution.")
