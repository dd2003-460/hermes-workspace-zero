#!/usr/bin/env python3
"""
Branch C: σ ≠ −κ investigation
EOM3 residual: r(M+b-r²/ℓ²)/ℓ⁴ in (0,2) component.
This suggests σ might not be exactly −κ.

Idea: Treat σ as unknown 1-forms with symbolic coefficients,
solve EOM2+3 simultaneously to find the correct σ.
Compare with −κ to identify the discrepancy.
"""

from sympy import symbols, Rational, expand, simplify, solve, Symbol, Eq

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')

# ── Form algebra (same as main script) ──
def d1(f1, coords):
    result = {}
    for i, coeff in f1.items():
        for j in range(len(coords)):
            if j == i: continue
            dc = expand(coeff.diff(coords[j]))
            if dc == 0: continue
            pair = (min(i,j), max(i,j))
            sign = 1 if j > i else -1
            result[pair] = result.get(pair, 0) + sign*dc
    return {k: expand(v) for k,v in result.items() if expand(v) != 0}

def wedge(a, b):
    result = {}
    for i, ai in a.items():
        for j, bj in b.items():
            if i == j: continue
            pair = (min(i,j), max(i,j))
            sign = 1 if j > i else -1
            result[pair] = expand(result.get(pair, 0) + sign*ai*bj)
    return {k: v for k,v in result.items() if expand(v) != 0}

def add2(*forms):
    result = {}
    for f in forms:
        for k,v in f.items():
            result[k] = result.get(k, 0) + v
    return {k: expand(v) for k,v in result.items() if expand(v) != 0}

def neg2(f): return {k: -v for k,v in f.items()}
def smul2(s, f): return {k: expand(s*v) for k,v in f.items()}

def lower(conn):
    return [conn[1], conn[0], conn[2]]

def eps_upper(a,b,c):
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return -((-1)**inv)

def eps_lower(a,b,c):
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return (-1)**inv

# ── Given fields (ingoing frame) ──
coords = [v, r, phi]
e_in = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: Rational(1), 2: -Rational(1,2)*J},
    {0: Rational(1)},
    {2: r},
]
omega_in = [
    {2: -Rational(1,2)*b},
    {2: Rational(1)},
    {},
]

# κ from paper
kappa_in = [
    {0: Rational(1,2)*J/ell**2, 2: Rational(1,2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]

print("="*60)
print("  Branch C: Solve for correct σ from EOM2+3")
print("="*60)

# Parameterize σ as generic 1-forms with unknown coefficients
# σ^a = σ^a_0 dv + σ^a_1 dr + σ^a_2 dφ
# Use symbolic unknowns
s00, s01, s02 = symbols('s00 s01 s02')  # σ^0 components
s10, s11, s12 = symbols('s10 s11 s12')  # σ^1 components
s20, s21, s22 = symbols('s20 s21 s22')  # σ^2 components

sigma_sym = [
    {0: s00, 1: s01, 2: s02},
    {0: s10, 1: s11, 2: s12},
    {0: s20, 1: s21, 2: s22},
]

# Compute EOM2: T^a + ε_{abc}σ^b∧e^c = 0
ol, el = lower(omega_in), lower(e_in)

print("\n--- Solving EOM2 + EOM3 for σ components ---")
print("  (treating σ components as symbolic unknowns)")

equations = []

# EOM2
for a in range(3):
    sl = lower(sigma_sym)
    de = d1(e_in[a], coords)
    tw = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_upper(a, bv, cv)
            if ev == 0: continue
            if ol[bv] and el[cv]:
                tw.append(smul2(ev, wedge(ol[bv], el[cv])))
    Ta = add2(de, neg2(add2(*tw))) if tw else de
    se = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_lower(a, bv, cv)
            if ev == 0: continue
            if sl[bv] and el[cv]:
                se.append(smul2(ev, wedge(sl[bv], el[cv])))
    st = add2(*se) if se else {}
    eom2 = add2(Ta, st)
    for pair, coeff in eom2.items():
        equations.append((f"EOM2[{a}]({pair})", expand(coeff)))

# EOM3
for a in range(3):
    sl = lower(sigma_sym)
    ds = d1(sigma_sym[a], coords)
    ws = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_upper(a, bv, cv)
            if ev == 0: continue
            if ol[bv] and sl[cv]:
                ws.append(smul2(ev, wedge(ol[bv], sl[cv])))
    Ds = add2(ds, neg2(add2(*ws))) if ws else ds
    ss = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_upper(a, bv, cv)
            if ev == 0 or bv == cv: continue
            if sl[bv] and sl[cv]:
                ss.append(smul2(Rational(1,2)*ev, wedge(sl[bv], sl[cv])))
    sst = add2(*ss) if ss else {}
    Fa = add2(Ds, sst)
    ee = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_lower(a, bv, cv)
            if ev == 0 or bv == cv: continue
            if el[bv] and el[cv]:
                ee.append(smul2(Rational(1,2)/ell**2*ev, wedge(el[bv], el[cv])))
    eet = add2(*ee) if ee else {}
    eom3 = add2(Fa, eet)
    for pair, coeff in eom3.items():
        equations.append((f"EOM3[{a}]({pair})", expand(coeff)))

# Extract polynomial equations in the unknowns
unknowns = [s00, s01, s02, s10, s11, s12, s20, s21, s22]
poly_eqs = []
for name, expr in equations:
    # Collect coefficients of powers of r
    poly_eqs.append((name, expr))

print(f"\n  Total equations: {len(poly_eqs)}")
print(f"  Unknowns: {len(unknowns)}")

# Try to solve
print("\n--- Attempting symbolic solve ---")
try:
    eqs_only = [eq for _, eq in poly_eqs]
    sol = solve(eqs_only, unknowns, dict=True)
    if sol:
        print(f"  Solutions found: {len(sol)}")
        for s in sol:
            print(f"\n  Solution:")
            for u in unknowns:
                if u in s:
                    print(f"    {u} = {s[u]}")
                else:
                    print(f"    {u} = FREE")
    else:
        print("  No solution found (system may be overdetermined or inconsistent)")
except Exception as e:
    print(f"  Symbolic solve failed: {e}")
    print("  Falling back to component-by-component analysis...")

# Compare with -κ
print("\n--- Comparison with σ = -κ ---")
neg_kappa = [{k: -v for k,v in f.items()} for f in kappa_in]
print("  Paper's σ = -κ:")
for a, f in enumerate(neg_kappa):
    print(f"    σ^{a} = {f}")

# Check if -κ satisfies the equations
print("\n--- Checking if σ=-κ satisfies EOM2 ---")
sl_k = lower(neg_kappa)
for a in range(3):
    de = d1(e_in[a], coords)
    tw = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_upper(a, bv, cv)
            if ev == 0: continue
            if ol[bv] and el[cv]:
                tw.append(smul2(ev, wedge(ol[bv], el[cv])))
    Ta = add2(de, neg2(add2(*tw))) if tw else de
    se = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_lower(a, bv, cv)
            if ev == 0: continue
            if sl_k[bv] and el[cv]:
                se.append(smul2(ev, wedge(sl_k[bv], el[cv])))
    st = add2(*se) if se else {}
    eom2 = add2(Ta, st)
    if eom2:
        print(f"  EOM2[{a}]: {eom2}")
    else:
        print(f"  EOM2[{a}]: ✅ 0")

print("\n✓ Branch C analysis complete.")
