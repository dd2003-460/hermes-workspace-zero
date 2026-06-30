#!/usr/bin/env python3
"""
Branch E: EOM3 (0,2) residual fix
Residual: r(ℓ²(M+b) - r²)/ℓ⁴ in F⁰ + (1/2ℓ²)ε_{0bc}e^b∧e^c = 0

Approach: Parameterize σ as -κ + δσ and solve for δσ that kills EOM3
while keeping EOM2 satisfied.
"""

from sympy import symbols, Rational, expand, simplify, solve

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')

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
def lower(conn): return [conn[1], conn[0], conn[2]]

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

coords = [v, r, phi]

# Use e with dr=-1 (the fix from Branch D)
e_in = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: -Rational(1), 2: -Rational(1,2)*J},
    {0: Rational(1)},
    {2: r},
]
omega_in = [{2: -Rational(1,2)*b}, {2: Rational(1)}, {}]

kappa = [
    {0: Rational(1,2)*J/ell**2, 2: Rational(1,2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]

# σ = -κ + δσ, parameterize δσ minimally
# The residual is in (0,2) of EOM3, proportional to (M+b-r²/ℓ²)
# Try: δσ⁰ has dφ component that cancels
# Try: δσ¹ has dv component

d00, d02, d10, d20 = symbols('d00 d02 d10 d20')  # δσ corrections

sigma = [
    {0: -kappa[0].get(0, 0) + d00, 2: -kappa[0].get(2, 0) + d02},
    {0: d10},
    {0: -kappa[2].get(0, 0) + d20},
]

print("="*60)
print("  Branch E: EOM3 residual fix via δσ")
print("="*60)

ol, el, sl = lower(omega_in), lower(e_in), lower(sigma)

# Compute EOM3[0] — the one with residual
a = 0
ds = d1(sigma[a], coords)
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
eom3_0 = add2(Fa, eet)

print(f"\n  EOM3[0] with δσ: {eom3_0}")

# Extract equations from each 2-form component
eqs = []
for pair, coeff in eom3_0.items():
    eqs.append(coeff)
    print(f"  Equation ({pair}): {coeff} = 0")

# Also check EOM2 is still satisfied
print("\n--- EOM2 check with δσ ---")
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
            if sl[bv] and el[cv]:
                se.append(smul2(ev, wedge(sl[bv], el[cv])))
    st = add2(*se) if se else {}
    res = add2(Ta, st)
    print(f"  EOM2[{a}]: {res if res else '✅ 0'}")

# Solve
print("\n--- Solving ---")
unknowns = [d00, d02, d10, d20]
try:
    sol = solve(eqs, unknowns, dict=True)
    if sol:
        for s in sol:
            print(f"  Solution: {s}")
    else:
        print("  No solution")
except Exception as e:
    print(f"  Error: {e}")

# Try specific fix: what if σ⁰_dφ = (M+b-r²/ℓ²)/2 instead of -(r²/ℓ²-M-b)/2?
# i.e., σ⁰_φ should be NEGATIVE of what -κ gives
print("\n--- Direct test: flip σ⁰_φ sign ---")
neg_kappa = [{k: -v for k,v in f.items()} for f in kappa]
# σ⁰_φ from -κ: (r²/ℓ² - M - b)/2 ... wait let me compute
# κ⁰_φ = (r²/ℓ² - M - b)/2
# -κ⁰_φ = -(r²/ℓ² - M - b)/2 = (M + b - r²/ℓ²)/2
# EOM3 residual: r(M+b-r²/ℓ²)/ℓ⁴ = (2r/ℓ²) × σ⁰_φ
# So if σ⁰_φ = 0, residual = 0. But that would break EOM2.
print(f"  σ⁰_φ (-κ): {(M+b-r**2/ell**2)/2}")
print(f"  EOM3 residual: r*(M+b-r²/ℓ²)/ℓ⁴ = (2r/ℓ²) × σ⁰_φ")
print(f"  If we set σ⁰_φ = 0 → EOM3 fixed but EOM2 broken")
print(f"  Need σ⁰_φ correction that kills EOM3[0] without affecting EOM2")

print("\n✓ Branch E analysis complete.")
