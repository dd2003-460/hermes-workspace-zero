#!/usr/bin/env python3
"""Debug EOM2 [2̄] computation step by step."""
from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')

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

def eps_abc(a, b, c):
    if len({a, b, c}) < 3: return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return -((-1) ** inv)

def lower(conn):
    return [conn[1], conn[0], conn[2]]

coords = [v, r, phi]

e = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: 1, 2: -Rational(1, 2)*J},
    {0: 1},
    {2: r},
]
omega = [
    {2: -Rational(1, 2)*b},
    {2: 1},
    {},
]
kappa = [
    {0: Rational(1, 2)*J/ell**2, 2: Rational(1, 2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma = [{k: -v for k, v in f.items()} for f in kappa]

ol = lower(omega)
el = lower(e)
sl = lower(sigma)

print("=== Step by step for a=2 (2̄) ===\n")

a = 2
# de^a
de = d1(e[a], coords)
print(f"de^2 = {de}")

# T^a = de^a - ε^{abc} ω_b ∧ e_c
tw = []
for bv in range(3):
    for cv in range(3):
        ev = eps_abc(a, bv, cv)
        if ev == 0: continue
        w = wedge(ol[bv], el[cv]) if ol[bv] and el[cv] else {}
        print(f"  ε^{a}{bv}{cv} = {ev}, ω_{bv}∧e_{cv} = {w}")
        if w:
            tw.append({k: expand(ev * v) for k, v in w.items()})

print(f"\nSum of -εω∧e terms: {[{k: -v for k, v in t.items()} for t in tw]}")

# Manual T^{2̄}
# de^{2̄} = d(r dφ) = dr∧dφ = {(1,2): 1}
# ε^{201}=-1: ω_0∧e_1 = dφ∧dv = -dv∧dφ = {(0,2): -1}
# ε^{210}=+1: ω_1∧e_0 = (-b/2 dφ)∧e_0 → (1,2): -b/2
# -[(-1)(-1) + (1)(-b/2)] = -[1 - b/2] = -1 + b/2
# T^{2̄} = {(1,2): 1-1+b/2, (0,2): b/2 - b/2} = {(1,2): b/2}

# ε_{2bc} σ^b ∧ e^c (ε_{abc}=ε^{abc} for antidiagonal)
se = []
for bv in range(3):
    for cv in range(3):
        ev = eps_abc(a, bv, cv)
        if ev == 0: continue
        w = wedge(sl[bv], el[cv]) if sl[bv] and el[cv] else {}
        print(f"  ε_{a}{bv}{cv} = {ev}, σ_{bv}∧e_{cv} = {w}")
        if w:
            se.append({k: expand(ev * v) for k, v in w.items()})

# Compute total
print(f"\nεσ∧e terms: {se}")
total_tw = {}
for t in tw:
    for k, v in t.items():
        total_tw[k] = total_tw.get(k, 0) - v  # -εω∧e
total_se = {}
for t in se:
    for k, v in t.items():
        total_se[k] = total_se.get(k, 0) + v  # +εσ∧e

print(f"\nT^2 (de - εω∧e): {de}")
print(f"  minus εω∧e: {total_tw}")
Ta = {}
for k, v in de.items():
    Ta[k] = Ta.get(k, 0) + v
for k, v in total_tw.items():
    Ta[k] = Ta.get(k, 0) + v
Ta = {k: expand(v) for k, v in Ta.items()}
print(f"  T^2 = {Ta}")

print(f"\nεσ∧e = {total_se}")
result = {}
for k, v in Ta.items():
    result[k] = result.get(k, 0) + v
for k, v in total_se.items():
    result[k] = result.get(k, 0) + v
result = {k: simplify(v) for k, v in result.items() if simplify(v) != 0}
print(f"\nT^2 + εσ∧e = {result}")
