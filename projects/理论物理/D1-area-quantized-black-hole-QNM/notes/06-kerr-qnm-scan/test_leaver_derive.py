#!/usr/bin/env python3
"""
Derive Leaver's recurrence coefficients from the explicit ODE in y = 1 - 2M/r.

Steps:
1. Transform d2psi/dr*2 + (w^2 - V)psi = 0 to y coordinate
2. Factor out asymptotic behavior: psi = (1-y)^rho0 * y^rho1 * phi(y)
3. Derive the ODE for phi
4. Apply power series phi = sum a_n y^n
5. Extract 3-term recurrence from the ODE
6. Set up continued fraction condition

Everything is derived symbolically first to avoid algebra errors.
"""

import numpy as np
import sympy as sp

M_sym = sp.Symbol('M', positive=True)
w_sym = sp.Symbol('w')  # omega (symbolic for derivation)
l_sym = sp.Symbol('l')
y_sym = sp.Symbol('y')

# Coordinate transformation
# y = 1 - 2M/r, so r = 2M/(1-y)
# dr/dy = 2M/(1-y)^2

# dr*/dr = r^2/(r-2M)^2
# r = 2M/(1-y): r - 2M = 2M/(1-y) - 2M = 2M*y/(1-y)
# (r-2M)^2 = 4M^2*y^2/(1-y)^2
# r^2 = 4M^2/(1-y)^2
# dr*/dr = [4M^2/(1-y)^2] / [4M^2*y^2/(1-y)^2] = 1/y^2
# So dr/d(r*) = y^2
# dr*/dy = dr*/dr * dr/dy = (1/y^2) * (2M/(1-y)^2) = 2M / [y^2 * (1-y)^2]

# d/d(r*) = dy/d(r*) * d/dy = y^2 * d/dy  ... wait, dr*/dr = 1/y^2
# No. dr*/dy = (dr*/dr)*(dr/dy)

# Actually let me recompute carefully:
# dr/dy = 2M/(1-y)^2
# dr*/dr = r^2/(r-2M)^2 = 1/y^2  (after substitution)
# dr*/dy = (1/y^2) * 2M/(1-y)^2 = 2M/[y^2*(1-y)^2]

# So d/dy = dr*/dy * d/d(r*) = 2M/[y^2*(1-y)^2] * d/d(r*)
# Hence d/d(r*) = y^2*(1-y)^2/(2M) * d/dy

# For second derivative:
# d2/d(r*)2 = y^2*(1-y)^2/(2M) * d/dy [ y^2*(1-y)^2/(2M) * d/dy ]
#           = y^2*(1-y)^2/(2M) * [ d(y^2*(1-y)^2/(2M))/dy * d/dy + y^2*(1-y)^2/(2M) * d2/dy2 ]

# Compute: y^2*(1-y)^2 = y^2*(1 - 2y + y^2) = y^2 - 2y^3 + y^4
# d/dy [y^2 - 2y^3 + y^4] = 2y - 6y^2 + 4y^3 = 2y(1 - 3y + 2y^2) = 2y(1-y)(1-2y)

f = y_sym**2 * (1 - y_sym)**2
df = sp.diff(f, y_sym)
print(f"f(y) = y^2*(1-y)^2 = {f}")
print(f"f'(y) = {df}")

# d2/d(r*)2 = f/(2M) * [ f'/(2M) * d/dy + f/(2M) * d2/dy2 ]
#           = f^2/(4M^2) * d2/dy2 + f*f'/(4M^2) * d/dy

# The Regge-Wheeler equation becomes:
# f^2/(4M^2) * psi'' + f*f'/(4M^2) * psi' + (w^2 - V) * psi = 0

# Divide by f^2/(4M^2):
# psi'' + [f'/f] * psi' + [4M^2*(w^2 - V)/f^2] * psi = 0

# P(y) = f'/f
# Q(y) = 4M^2*(w^2 - V)/f^2

# f/f = f'/(4M) = y(1-y)(1-2y) ... wait
# P(y) = f'/f = [2y(1-y)(1-2y)] / [y^2(1-y)^2] = 2(1-2y)/[y(1-y)]
P = df / f
P_simplified = sp.simplify(P)
print(f"\nP(y) = f'/f = {P_simplified}")

# V(y) = (1 - 2M/r) * [l(l+1)/r^2 - 6M/r^3]
# = y * [l(l+1) * (1-y)^2/(4M^2) - 6M * (1-y)^3/(8M^3)]
# = y * [l(l+1)(1-y)^2 - 6M(1-y)^3/(2M)] / (4M^2) ... wait
# r = 2M/(1-y), so 1/r = (1-y)/(2M)
# 1/r^2 = (1-y)^2/(4M^2)
# 1/r^3 = (1-y)^3/(8M^3)

# V = y * [l(l+1)*(1-y)^2/(4M^2) - 6M*(1-y)^3/(8M^3)]
# V = y * [(1-y)^2 * l(l+1)/(4M^2) - 3(1-y)^3/(4M^2)]
# V = y*(1-y)^2/(4M^2) * [l(l+1) - 3(1-y)]
# V = y*(1-y)^2/(4M^2) * [l(l+1) - 3 + 3y]

V = y_sym * (1 - y_sym)**2 / (4 * M_sym**2) * (l_sym * (l_sym + 1) - 3 * (1 - y_sym))
V = sp.simplify(V)
print(f"V(y) = {V}")

# Q(y) = 4M^2*(w^2 - V)/f^2
# But we divide by f^2/(4M^2), so the term is [4M^2 * (w^2-V)] / [f^2/(4M^2)] * 1/[f^2/(4M^2)] ...
# No wait. After dividing by f^2/(4M^2):
# Q = (4M^2/w^2 - V) / [f^2/(4M^2)]
#
# Hmm let me be more careful. The equation is:
# f^2/(4M^2) psi'' + f*f'/(4M^2) psi' + (w^2 - V) psi = 0
#
# Divide through by f^2/(4M^2):
# psi'' + [f'/f] psi' + [4M^2*(w^2 - V)/f^2] psi = 0
#
# So Q = 4M^2*(w^2 - V) / f^2

Q_num = 4 * M_sym**2 * (w_sym**2 - V)
Q_den = f**2
Q = sp.simplify(Q_num / Q_den)
print(f"\nQ(y) = 4M^2(w^2-V)/f^2 = {Q}")

# Q at y->0: f ~ y^2, so Q ~ 4M^2*w^2/y^4 + O(1/y^3) ...
# This has a 1/y^4 singularity (rank 1 irregular singular point)
# And 4M^2*w^2/y^4 means the leading exponential factor is exp(w/something * 1/y)

# Let me see: near y=0, Q ~ w^2/(M^2*y^2) + ...
# The WKB analysis: psi ~ exp(integrate(sqrt(-Q)) dy)
# sqrt(-Q) ~ w/(M*y) for y->0
# integrate(w/(M*y) dy) = (w/M) * ln(y) = ln(y^(w/M))
# So psi ~ y^(w/M) ... but this gives w/M not 2iwM

# Hmm, let me recalculate. Q ~ 4M^2*w^2 / (y^2 * y^2) / [y^4/(4M^2)] ...
# Q = 4M^2*w^2 / (y^4 * (1-y)^4) = 4M^2*w^2/(y^4) * [1 + O(y)]

# No. f = y^2*(1-y)^2. f^2 = y^4*(1-y)^4.
# Q = 4M^2*w^2 / [y^4*(1-y)^4] = 4M^2*w^2 / y^4 * (1 + 4y + ...) for y -> 0

# For the asymptotic behavior: near y=0, the dominant term is ~4M^2*w^2/y^4
# The equation is psi'' + [w^2*4M^2/y^4] * psi ~ 0
# This has irregular singular point of rank 1 at y=0
# Leading behavior: psi ~ exp(integrate sqrt(-Q) dy)
# sqrt(-Q) ~ 2i*M*w/y^2
# integrate: -2i*M*w/y
# So psi ~ exp(-2i*M*w/y) ~ exp(-i*w*r*) near y=0 (infinity)
# But there are two branches: +/- 2iMw

# Let me verify: r* ~ 2M/y as y->0 (since y = 1/r approximately near infinity)
# No: y = 1-2M/r ~ 1-0 = 1 near infinity... wait no.
# At infinity, r->infinity, y = 1-2M/r -> 1
# At horizon, r = 2M, y = 0
# I got the coordinates backwards!

print("\n\n*** Coordinate check ***")
print("y = 1 - 2M/r")
print("At horizon (r = 2M): y = 1 - 1 = 0")
print("At infinity (r -> inf): y = 1 - 0 = 1")
print("So y=0 is HORIZON, y=1 is INFINITY")
