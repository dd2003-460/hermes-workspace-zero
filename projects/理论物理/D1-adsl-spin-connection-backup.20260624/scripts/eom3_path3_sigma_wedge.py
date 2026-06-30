#!/usr/bin/env python3
"""
EOM3 Deep Dive — Path 3: σ∧σ contribution audit
任务ID: adsl-eom3-deep-dive | 创建时间: 2026-04-01 | 关联项目: adsl-spin-connection

Question: Is the (1/2)ε^{{abc}}σ_b ∧ σ_c term in F^a being computed correctly?
- Re-compute this term explicitly for each a
- Check ε^{{0bc}}σ_b∧σ_c contributions to (dv,dr) component
- Verify we're using the right σ (κ vs -κ, lower vs upper)
"""

from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, b, J = symbols('r ell M b J', real=True)
v, phi = symbols('v phi')

coords = [v, r, phi]

# ── Form algebra ──

def d1(f1, coords):
    result = {}
    for i, coeff in f1.items():
        for j in range(len(coords)):
            if j == i: continue
            dc = diff(coeff, coords[j])
            if dc == 0: continue
            pair = (min(i, j), max(i, j))
            sign = 1 if j > i else -1
            result[pair] = result.get(pair, 0) + sign * dc
    return {k: expand(v) for k, v in result.items() if expand(v) != 0}

def wedge(a, b):
    result = {}
    for i, ai in a.items():
        for j, bj in b.items():
            if i == j: continue
            pair = (min(i, j), max(i, j))
            sign = 1 if j > i else -1
            result[pair] = expand(result.get(pair, 0) + sign * ai * bj)
    return {k: v for k, v in result.items() if expand(v) != 0}

def add2(*forms):
    result = {}
    for f in forms:
        for k, v in f.items():
            result[k] = result.get(k, 0) + v
    return {k: expand(v) for k, v in result.items() if expand(v) != 0}

def neg2(f):
    return {k: -v for k, v in f.items()}

def smul2(s, f):
    return {k: expand(s * v) for k, v in f.items()}

def simp2(f):
    return {k: simplify(v) for k, v in f.items() if simplify(v) != 0}

def lower(conn):
    return [conn[1], conn[0], conn[2]]

def eps_upper(a, b, c):
    if len({a, b, c}) < 3: return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return -((-1) ** inv)

def eps_lower(a, b, c):
    if len({a, b, c}) < 3: return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return (-1) ** inv

# ── Setup ──

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

sl = lower(sigma)
ol = lower(omega_in)

print("=" * 70)
print("  Path 3: σ∧σ contribution audit")
print("=" * 70)

print("\nσ^a (upper, paper definition):")
for a in range(3):
    print(f"  σ^{a} = {sigma[a]}")

print("\nσ_a (lowered):")
for a in range(3):
    print(f"  σ_{a} = {sl[a]}")

# ── Compute (1/2)ε^{{abc}}σ_b ∧ σ_c for each a ──

print("\n" + "-" * 70)
print("  Computing (1/2)ε^{{abc}}σ_b ∧ σ_c for each a")
print("-" * 70)

for a in range(3):
    labels = ['0̄', '1̄', '2̄']
    print(f"\n  a = {a} ({labels[a]}):")
    ss_terms = []
    for bv in range(3):
        for cv in range(3):
            ev = eps_upper(a, bv, cv)
            if ev == 0 or bv == cv:
                continue
            w = wedge(sl[bv], sl[cv])
            if w:
                term = smul2(Rational(1, 2) * ev, w)
                print(f"    ε^{a}{bv}{cv}={ev:+d}: (1/2)·{ev}·(σ_{bv}∧σ_{cv}) = {term}")
                ss_terms.append(term)
            else:
                print(f"    ε^{a}{bv}{cv}={ev:+d}: σ_{bv}∧σ_{cv} = ∅ (zero)")
    total = add2(*ss_terms) if ss_terms else {}
    print(f"    TOTAL (1/2)ε^{{abc}}σ_b∧σ_c = {total}")

# ── Focus on (dv,dr) = (0,1) component of ε^{{0bc}}σ_b∧σ_c ──

print("\n" + "-" * 70)
print("  Focus: (0,1) component of (1/2)ε^{{0bc}}σ_b∧σ_c")
print("-" * 70)

# For a=0: ε^{012}σ_1∧σ_2 + ε^{021}σ_2∧σ_1
# ε^{012} = -1, ε^{021} = +1
# σ_1∧σ_2: wedge of σ_1 (index 1) with σ_2 (index 2)
# σ_2∧σ_1 = -σ_1∧σ_2
# So: (1/2)[-1·σ_1∧σ_2 + 1·(-σ_1∧σ_2)] = (1/2)[-2σ_1∧σ_2] = -σ_1∧σ_2

w12 = wedge(sl[1], sl[2])
print(f"  σ_1∧σ_2 = {w12}")
w21 = wedge(sl[2], sl[1])
print(f"  σ_2∧σ_1 = {w21}")

print(f"\n  (1/2)[ε^{{012}}σ_1∧σ_2 + ε^{{021}}σ_2∧σ_1]")
print(f"       = (1/2)[-1·σ_1∧σ_2 + 1·σ_2∧σ_1]")
print(f"       = (1/2)[-σ_1∧σ_2 - σ_1∧σ_2] = -σ_1∧σ_2")

if (0, 1) in w12:
    print(f"\n  (0,1) component of -σ_1∧σ_2 = {expand(-w12[(0,1)])}")
else:
    print(f"\n  σ_1∧σ_2 has no (0,1) component")

# ── Compute D_ω σ⁰ separately ──

print("\n" + "-" * 70)
print("  D_ω σ⁰ decomposition")
print("-" * 70)

ds0 = d1(sigma[0], coords)
print(f"  dσ⁰ = {ds0}")

ws0 = []
for bv in range(3):
    for cv in range(3):
        ev = eps_upper(0, bv, cv)
        if ev == 0: continue
        if ol[bv] and sl[cv]:
            w = wedge(ol[bv], sl[cv])
            if w:
                term = smul2(ev, w)
                print(f"  ε^{{0{bv}{cv}}}={ev:+d}: ω_{bv}∧σ_{cv} → {term}")
                ws0.append(term)
Dws0 = add2(ds0, neg2(add2(*ws0))) if ws0 else ds0
print(f"  D_ω σ⁰ = dσ⁰ - Σ εω∧σ = {Dws0}")

# Extract (0,1) from D_ω σ⁰
if (0, 1) in Dws0:
    print(f"\n  (0,1) component of D_ω σ⁰ = {Dws0[(0,1)]}")
    print(f"  Simplified: {simplify(Dws0[(0,1)])}")

# ── Now compute F⁰ fully and separately ──

ss0_terms = []
for bv in range(3):
    for cv in range(3):
        ev = eps_upper(0, bv, cv)
        if ev == 0 or bv == cv: continue
        if sl[bv] and sl[cv]:
            w = wedge(sl[bv], sl[cv])
            if w:
                ss0_terms.append(smul2(Rational(1,2)*ev, w))
sst0 = add2(*ss0_terms) if ss0_terms else {}
print(f"\n  (1/2)ε^{{0bc}}σ_b∧σ_c = {sst0}")

F0 = add2(Dws0, sst0)
print(f"  F⁰ = D_ω σ⁰ + (1/2)εσ∧σ = {F0}")

# ── Compute (1/2ℓ²)ε_{0bc}e^b∧e^c ──

print("\n" + "-" * 70)
print("  (1/2ℓ²)ε_{0bc}e^b∧e^c")
print("-" * 70)

el = lower(e_in)
ee0_terms = []
for bv in range(3):
    for cv in range(3):
        ev = eps_lower(0, bv, cv)
        if ev == 0 or bv == cv: continue
        if el[bv] and el[cv]:
            w = wedge(el[bv], el[cv])
            if w:
                term = smul2(Rational(1,2)/ell**2*ev, w)
                print(f"  ε_{{0{bv}{cv}}}={ev:+d}: (1/2ℓ²)·{ev}·(e_{bv}∧e_{cv}) = {term}")
                ee0_terms.append(term)
eet0 = add2(*ee0_terms) if ee0_terms else {}
print(f"  Total = {eet0}")

# EOM3 residual
eom3_0 = simp2(add2(F0, eet0))
print(f"\n  EOM3[0̄] = F⁰ + (1/2ℓ²)εe∧e = {eom3_0}")

if (0, 1) in eom3_0:
    print(f"\n  (0,1) residual = {simplify(eom3_0[(0,1)])}")
    print(f"  Factored: {simplify(eom3_0[(0,1)]).factor()}")

print("\n✓ Path 3 complete.")
