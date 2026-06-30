#!/usr/bin/env python3
"""
Boundary condition check for QNM equation.
Core question: does our formulation correctly enforce ingoing/h outgoing BCs?
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw

M = 1.0

def rstar(r):
    return r + 2*M*np.log(r/(2*M)-1)

def r_from_rs(rs):
    t = rs/(2*M) - 1
    y = np.real(lambertw(np.exp(t)))
    r = 2*M*(1+y)
    for _ in range(30):
        if r <= 2*M: r = 2*M+1e-14; continue
        rc = r + 2*M*np.log(r/(2*M)-1)
        d = (rc - rs) / (r**2/(r-2*M)**2)
        if abs(d) < 1e-16: break
        r -= d
        if r <= 2*M: r = 2*M+1e-14
    return r

def V(r, l):
    f = 1-2*M/r
    return f*(l*(l+1)/r**2 - 6*M/r**3)

omega = 0.37367 - 0.08896j  # Berti l=2
l = 2

# Q: What does ingoing at horizon look like in different formulations?
# ingoing: psi ~ exp(-i*omega*r*)
# factorized: psi = exp(-i*omega*r*) * u, u = const => [1, 0]

# TEST 1: Direct integration, compare ingoing BC [1, -i*omega] vs correct asymptotic
print("="*70)
print("TEST 1: Boundary condition verification")
print("="*70)

def deriv_raw(rs, Y):
    r = r_from_rs(rs)
    r = max(r, 2*M+1e-14)
    return [Y[1], -(omega**2 - V(r, l))*Y[0]]

# Horizon side with ingoing BC
# Case A: [1, -i*omega] -- pure outgoing of form exp(-i*omega*r*) at r_h
s1a = solve_ivp(deriv_raw, [-50, -20], [1, -1j*omega], rtol=1e-12, atol=1e-14, max_step=0.1, dense_output=True)
# Case B: [1, 0] in factorized -> converts to [1, -i*omega] in raw!
# Because dpsi/dr* = d/dr*(exp(-i*w*r*)*1) = -i*w*psi = -i*w*1

# Let me check: integrate the FACTORIZED equation directly
def deriv_factored(rs, Y):
    r = r_from_rs(rs)
    r = max(r, 2*M+1e-14)
    return [Y[1], 2j*omega*Y[1] + V(r, l)*Y[0]]

s2 = solve_ivp(deriv_factored, [-50, -20], [1+0j, 0+0j], rtol=1e-12, atol=1e-14, max_step=0.1, dense_output=True)
u_val = s2.y[0, -1]
du_val = s2.y[1, -1]
# Reconstruct: psi_factored = exp(-i*w*(-20)) * u(-20)
exp_term = np.exp(-1j*omega*(-20))
psi_from_factored = exp_term * u_val
dpsi_from_factored = exp_term * (-1j*omega*u_val + du_val)

psi_raw = s1a.y[0, -1]
dpsi_raw = s1a.y[1, -1]

print(f"  Direct ingoing [1, -iw] at r*=-20:")
print(f"    psi = {psi_raw:.10f}  dpsi = {dpsi_raw:.10f}")
print(f"  Factorized [1, 0] => reconstructed at r*=-20:")
print(f"    exp(-iw*r*) = {exp_term:.10f}")
print(f"    psi = {psi_from_factored:.10f}  dpsi = {dpsi_from_factored:.10f}")
print(f"  Difference in psi: {abs(psi_raw - psi_from_factored):.2e}")
print(f"  Ratio: {psi_raw/psi_from_factored:.10f}")

# TEST 2: What about the WRONG boundary condition?
# What if we accidentally use [1, +i*omega] (ingoing/outgoing mix-up)?
s_wrong = solve_ivp(deriv_raw, [-50, -20], [1, +1j*omega], rtol=1e-12, atol=1e-14, max_step=0.1, dense_output=True)
print(f"\n  Wrong BC [1, +iw] at r*=-20:")
print(f"    psi = {s_wrong.y[0,-1]:.10f}")

# TEST 3: V check
print("\nTEST 2: Potential values at key points")
r_check = [r_from_rs(r) for r in [-50, -20, 0, 20, 40, 80, 150]]
for r_ in r_check:
    rs_ = rstar(r_)
    v_ = V(r_, l)
    print(f"  r*={rs_:7.1f}, r={r_:.4f}, V={v_:.8f}")

# TEST 4: Analytical test - integrate V=0 exactly
print("\nTEST 3: V=0 free equation test")
# With V=0, the ODE is psi'' + omega^2 psi = 0
# Exact solution: psi(r*) = C1*exp(i*omega*r*) + C2*exp(-i*omega*r*)
# [psi, dpsi] = [1, -i*omega] at r*=-50 means C1=C2=0.5 (ingoing + outgoing = 1, derivative gives -i*omega)
# Wait: C1*e^{i*omega*r*} + C2*e^{-i*omega*r*} with C1=C2=0.5 gives
# psi = 0.5*(e^{i*omega*r*} + e^{-i*omega*r*}) = cos(omega*r*)
# dpsi = 0.5*i*omega*(e^{i*omega*r*} - e^{-i*omega*r*}) = -i*omega*sin(omega*r*)
# At r*=-50: cos(omega*(-50)) should not equal 1 in general.
# Hmm, so [1, -i*omega] does NOT mean C1=1, C2=0.

# Let me solve: psi(0) = C1+C2 = psi_0, psi'(0) = i*omega*(C1-C2) = dp_0
# C1 = (psi_0 + dp_0/(i*omega))/2, C2 = (psi_0 - dp_0/(i*omega))/2

# For [1, -i*omega]: C1 = (1 + (-i*omega)/(i*omega))/2 = (1+(-1))/2 = 0
#                        C2 = (1 - (-i*omega)/(i*omega))/2 = (1-(-1))/2 = 1
# So [1, -i*omega] => C1=0, C2=1 => psi = exp(-i*omega*r*)

# Now with our BC: psi=-50, dpsi=-i*omega
# At r*=-50: C1 = (1+1)/2=1, C2=(1-1)/2=0? Let me be careful.

# Actually [1, -i*omega] at r*=-50 means:
# psi(-50) = 1, dpsi/dr*|_{-50} = -i*omega
# C1 = (psi + dpsi/(i*omega))/2 = (1 + (-i*omega)/(i*omega))/2 = (1 + (-1))/2 = 0
# C2 = (psi - dpsi/(i*omega))/2 = (1 - (-i*omega)/(i*omega))/2 = (1-(-1))/2 = 1

print(f"  [1, -iw] at any r* gives C1=0, C2=1 for V=0")
print(f"  (pure ingoing, which is correct)")

# TEST 4: Verify with numerical integration (V=0)
def deriv_zero(rs, Y):
    return [Y[1], -omega**2 * Y[0]]

s_zero = solve_ivp(deriv_zero, [-50, 50], [1+0j, -1j*omega], rtol=1e-14, atol=1e-14, max_step=0.1, dense_output=True)
for rs_t in [-50, -20, 0, 20, 50]:
    psi_exact = np.exp(-1j*omega*rs_t)
    psi_num = s_zero.sol(rs_t)[0]
    rel = abs(psi_num - psi_exact)/abs(psi_exact)
    print(f"  V=0 at r*={rs_t:5d}: psi_num={psi_num:.8f}, psi_exact={psi_exact:.8f}, rel_err={rel:.2e}")

# TEST 5: The crucial check - log-derivative of u
# At horizon, for true ingoing: u = const, du/dr* = 0
# But with finite integration (r* = -50), is u truly constant?

print("\nTEST 4: Checking u evolution from horizon")
# Integrate factorized equation outward
s_u = solve_ivp(deriv_factored, [-50, 50], [1+0j, 0+0j], rtol=1e-12, atol=1e-14, max_step=0.1, dense_output=True)
# Plot u and du/dr*
for rs_t in [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40]:
    u_t = s_u.sol(rs_t)[0]
    du_t = s_u.sol(rs_t)[1]
    # Also check log-derivative
    log_der = du_t / u_t if abs(u_t) > 1e-10 else None
    if log_der is not None:
        print(f"  r*={rs_t:4d}: |u|={abs(u_t):.6e}, |du/dr*|={abs(du_t):.6e}, log_der={log_der:.6f}")

# At infinity (r* large positive):
# For ingoing: psi = exp(-i*omega*r*) => u = constant
# For QNM: we need outgoing at infinity, which means u should behave like exp(2*i*omega*r*)
# At infinity V->0, so u''-2*i*omega*u'=0 => u = C + D*exp(2*i*omega*r*)

print("\nTEST 5: Infinity behavior for ingoing initial condition")
print("  (checking what component D grows at infinity)")
for rs_t in [80, 100, 120, 150]:
    u_t = s_u.sol(rs_t)[0]
    du_t = s_u.sol(rs_t)[1]
    log_der = du_t / u_t if abs(u_t) > 1e-10 else None
    # u ~ C + D*exp(2*i*omega*r*)
    # 2*i*omega = 2*i*(0.37367-0.08896j) = 0.17792 + 0.74734j
    # exp(2*i*omega*r*) for r*>0: |exp(0.178*r*)| grows! and |exp(i*0.747*r*)|=1
    if log_der is not None:
        print(f"  r*={rs_t:4d}: |u|={abs(u_t):.6e}, |du/dr*|={abs(du_t):.6e}, log_der={log_der.real:.6f}+{log_der.imag:.6f}j")
print("  NOTE: 2*i*omega = %.4f + %.4fj, real part=%.4f > 0 => EXP(2*i*w*r*) GROWS at infinity" % (2*omega.real, -2*omega.imag, 2*omega.real))

# KEY INSIGHT: For ingoing initial condition at horizon:
# u starts constant. As r* increases, V becomes nonzero and drives u.
# At large r* (where V~0), u has a constant component PLUS a growing exp(2i*omega*r*) component.
# The ingoing solution has BOTH components at infinity!
# For QNM, we need ONLY outgoing at infinity.

# Let's check: what does the actual QNM u look like?
print("\nTEST 6: Two-sided matching - does horizon U contribute at infinity?")
# If our ansatz is correct, the QNM should satisfy:
# 1) ingoing at horizon (u~constant)
# 2) outgoing at infinity (u~exp(2*i*omega*r*))
# For pure ingoing: horizon BC = [1, 0]
# For outgoing at infinity: we need u_infinity = exp(2*i*omega*r*)
# which means u=1, du/dr*=2*i*omega at large r*

print("  The question: for ingoing BC [1, 0] at r*=-50, does the solution")
print("  have u ~ const or u ~ exp(2iw r*) at infinity?")

# Integrate over full range
s_full = solve_ivp(deriv_factored, [-50, 150], [1+0j, 0+0j], rtol=1e-12, atol=1e-14, max_step=0.1, dense_output=True)
u_at_inf = s_full.sol(150)[0]
du_at_inf = s_full.sol(150)[1]

# At r*=150, u = C + D*exp(2*i*omega*150)
# The growing component dominates: |exp(2*i*omega*150)| = exp(2*|Im(omega)|*150) = exp(2*0.089*150) = exp(26.68) = 3.5e11
# If |u| is O(1), then C dominates. If |u| is huge, D dominates.
print(f"  |u(150)| = {abs(u_at_inf):.2e}")
print(f"  Growth factor for ingoing: exp(|Im(w)|*200) = exp(0.089*200) = exp(17.8)")
exp_growth = np.exp(0.08896*200)
print(f"  (raw exp growth would be exp(|Im(w)|*200) = {exp_growth:.2e})")
print(f"  |u(150)| >> 1? => horizon wave dominates (wrong for QNM)")
