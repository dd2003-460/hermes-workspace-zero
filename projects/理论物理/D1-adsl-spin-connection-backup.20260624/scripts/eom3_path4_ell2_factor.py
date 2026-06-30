#!/usr/bin/env python3
"""
EOM3 Deep Dive — Path 4: ℓ² factor inspection
任务ID: adsl-eom3-deep-dive | 创建时间: 2026-04-01 | 关联项目: adsl-spin-connection

Residual: r(ℓ²(M+b) - r²)/ℓ⁴ in (0,2) component.

Question: Could there be a typo in the ℓ² factor in EOM3?
The paper gives: F^a + (1/(2ℓ²))ε_{abc}e^b∧e^c = 0.

Try variations:
- (1/ℓ²) instead of 1/(2ℓ²)
- Different placement of 2
- Check if residual matches half of something
"""

from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')

coords = [v, r, phi]

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
def simp2(f): return {k: simplify(v) for k,v in f.items() if simplify(v) != 0}

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

# ── Setup (branch_A_corrected basis, dr=-1 fix) ──

e_in = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: 1, 2: -Rational(1,2)*J},
    {0: 1},
    {2: r},
]
omega_in = [
    {2: -Rational(1,2)*b},
    {2: 1},
    {},
]
kappa_in = [
    {0: Rational(1,2)*J/ell**2, 2: Rational(1,2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma = [{k: -v for k, v in f.items()} for f in kappa_in]

print("=" * 70)
print("  Path 4: ℓ² factor typo investigation")
print("=" * 70)

# Compute F^a (using ε^{abc} definitions)
ol, el, sl = lower(omega_in), lower(e_in), lower(sigma)
coords = [v, r, phi]

F_results = []
for a in range(3):
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
    F_results.append(simp2(add2(Ds, sst)))

print("\nComputed F^a (definition side):")
for a in range(3):
    labels = ['0̄', '1̄', '2̄']
    print(f"  F^{labels[a]} = {F_results[a]}")

# Compute e∧e term with various prefactors
ee_terms = []
for bv in range(3):
    for cv in range(3):
        ev = eps_lower(0, bv, cv)
        if ev == 0 or bv == cv: continue
        if el[bv] and el[cv]:
            w = wedge(el[bv], el[cv])
            if w:
                ee_terms.append((bv, cv, ev, w))
print("\ne∧e term (ε_{0bc} e^b ∧ e^c):")
for bv, cv, ev, w in ee_terms:
    print(f"  ε_{0}{bv}{cv}={ev:+d}: e_{bv}∧e_{cv} = {w}")

# Candidate ℓ² factors to test
print("\n" + "=" * 70)
print("  Testing different ℓ² prefactors for e∧e term")
print("=" * 70)

prefactors = [
    ("1/(2ℓ²)", Rational(1,2)/ell**2),
    ("1/ℓ²", 1/ell**2),
    ("2/ℓ²", 2/ell**2),
    ("1/(ℓ²) (same as 1/ℓ²)", 1/ell**2),
]

residual_standard = None
for name, prefac in prefactors:
    print(f"\n--- Test: EOM3 with factor {name} ---")
    ee_sum = {}
    for bv, cv, ev, w in ee_terms:
        term = smul2(prefac * ev, w)
        ee_sum = add2(ee_sum, term)
    eom3_0 = simp2(add2(F_results[0], ee_sum))
    print(f"  Full EOM3[0̄] = {eom3_0}")
    if (0, 2) in eom3_0:
        expr = simplify(eom3_0[(0, 2)])
        print(f"  (0,2) component: {expr}")
        factored = simplify(expr.factor())
        print(f"  Factored: {factored}")
        if residual_standard is None:
            residual_standard = expr
        else:
            # Compare forms
            diff_with_standard = simplify(expr - residual_standard)
            if diff_with_standard != 0:
                print(f"  Diff from 1/(2ℓ²) version: {diff_with_standard}")
    else:
        print("  (0,2) component: absent")

# Analysis: what would it take to cancel (0,2)?
print("\n" + "=" * 70)
print("  Analysis: Can any standard factor cancel the (0,2) residual?")
print("=" * 70)

print("\nStandard residual from 1/(2ℓ²):")
print(f"  r*(ell**2*(M + b) - r**2)/ell**4")

# If F^0(0,2) means A*r/ell² + B*r/ell^4, and e∧e gives C*r/ell² + D*r/ell^4
# What are A, B, C, D?

print("\nDecompose F^0(0,2):")
if (0,2) in F_results[0]:
    f02 = simplify(F_results[0][(0,2)])
    print(f"  F^0_(0,2) = {f02}")
    f02_factor = simplify(f02.factor())
    print(f"  Factored: {f02_factor}")
    # Extract terms with different ell powers manually
    f02_expanded = expand(f02)
    print(f"  Expanded: {f02_expanded}")
else:
    print("  F^0_(0,2) = ∅")

print("\nCompute e∧e(0,2) for 1/(2ℓ²):")
e02 = None
for name, prefac in prefactors:
    if name == "1/(2ℓ²)":
        ee_sum = {}
        for bv, cv, ev, w in ee_terms:
            term = smul2(prefac * ev, w)
            ee_sum = add2(ee_sum, term)
        if (0,2) in ee_sum:
            e02 = simplify(ee_sum[(0,2)])
            print(f"  e∧e_(0,2) = {e02}")
            print(f"  Expanded: {expand(e02)}")

# Reconstruct what the sum should be if EOM3 passed
if e02 is not None and (0,2) in F_results[0]:
    total = simplify(F_results[0][(0,2)] + e02)
    print(f"\nF^0_(0,2) + e∧e_(0,2) = {total}")
    print("Expected if everything consistent: 0")
    print("To get 0, we would need e∧e_(0,2) = -F^0_(0,2)")
    target = simplify(-F_results[0][(0,2)])
    print(f"Required e∧e_(0,2) = {target}")

    # Check if any prefactor gives this
    print("\nCheck if any prefactor achieves cancellation:")
    for name, prefac in prefactors:
        ee_sum = {}
        for bv, cv, ev, w in ee_terms:
            term = smul2(prefac * ev, w)
            ee_sum = add2(ee_sum, term)
        if (0,2) in ee_sum:
            candidate = simplify(ee_sum[(0,2)])
            diff = simplify(candidate - target)
            if diff == 0:
                print(f"  ✅ {name} yields perfect cancellation!")
            else:
                print(f"  {name}: residual diff = {diff}")

# Check if there's a missing factor of 2 in the σ∧σ term coefficient
print("\n" + "=" * 70)
print("  Alternative: What if F^a definition uses 2·(1/2)ε^{abc}σ_b∧σ_c?")
print("=" * 70)

# Recompute F^0 with σ∧σ term doubled
ds0 = d1(sigma[0], coords)
ws0 = []
for bv in range(3):
    for cv in range(3):
        ev = eps_upper(0, bv, cv)
        if ev == 0: continue
        if ol[bv] and sl[cv]:
            ws0.append(smul2(ev, wedge(ol[bv], sl[cv])))
Dws0 = add2(ds0, neg2(add2(*ws0))) if ws0 else ds0

# σ∧σ double
ss0_terms = []
for bv in range(3):
    for cv in range(3):
        ev = eps_upper(0, bv, cv)
        if ev == 0 or bv == cv: continue
        if sl[bv] and sl[cv]:
            ss0_terms.append(smul2(Rational(1)*ev, wedge(sl[bv], sl[cv])))  # factor = 1 instead of 1/2
sst0_double = add2(*ss0_terms) if ss0_terms else {}
F0_alt = simp2(add2(Dws0, sst0_double))
print(f"\nAlternate F^0 (σ∧σ coeff = 1): {F0_alt}")
if (0,2) in F0_alt:
    f02_alt = simplify(F0_alt[(0,2)])
    print(f"  (0,2): {f02_alt}")
    total_alt = simplify(f02_alt + e02 if e02 else 0)
    print(f"  F^0_(0,2) + e∧e_(0,2) = {total_alt}")

print("\n✓ Path 4 complete.")
