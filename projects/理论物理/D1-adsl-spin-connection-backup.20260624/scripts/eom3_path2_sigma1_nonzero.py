#!/usr/bin/env python3
"""
EOM3 Deep Dive — Path 2: σ¹ ≠ 0 test
任务ID: adsl-eom3-deep-dive | 创建时间: 2026-04-01 | 关联项目: adsl-spin-connection

Question: If σ¹ has non-zero components, can it cancel the EOM3 residual?
- Parameterize σ¹ = a·dv + c·dφ (skip dr since σ¹_r doesn't appear in wedge)
- Substitute into EOM2 + EOM3, solve simultaneously
- Check if EOM2 forces σ¹=0
"""

from sympy import symbols, simplify, expand, Rational, diff, solve

r, ell, M, b, J = symbols('r ell M b J', real=True)
v, phi = symbols('v phi')
s1_v, s1_r, s1_p = symbols('s1_v s1_r s1_p', real=True)  # σ¹ components

coords = [v, r, phi]

# ── Form algebra ──

def d1(f1, coords):
    result = {}
    for i, coeff in f1.items():
        for j in range(len(coords)):
            if j == i:
                continue
            dc = diff(coeff, coords[j])
            if dc == 0:
                continue
            pair = (min(i, j), max(i, j))
            sign = 1 if j > i else -1
            result[pair] = result.get(pair, 0) + sign * dc
    return {k: expand(v) for k, v in result.items() if expand(v) != 0}

def wedge(a, b):
    result = {}
    for i, ai in a.items():
        for j, bj in b.items():
            if i == j:
                continue
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
    if len({a, b, c}) < 3:
        return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return -((-1) ** inv)

def eps_lower(a, b, c):
    if len({a, b, c}) < 3:
        return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return (-1) ** inv

def eom3_F_ee(omega, e, sigma, ell_sym, coords):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
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
        Fa = add2(Ds, sst)
        ee = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_lower(a, bv, cv)
                if ev == 0 or bv == cv: continue
                if el[bv] and el[cv]:
                    ee.append(smul2(Rational(1,2)/ell_sym**2*ev, wedge(el[bv], el[cv])))
        eet = add2(*ee) if ee else {}
        results.append(simp2(add2(Fa, eet)))
    return results

def eom2_T_sigma(omega, e, sigma, coords):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        de = d1(e[a], coords)
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
        results.append(simp2(add2(Ta, st)))
    return results

# ── Ingoing EF frame ──

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
sigma_base = [{k: -v for k, v in f.items()} for f in kappa_in]

print("=" * 70)
print("  Path 2: σ¹ ≠ 0 test")
print("=" * 70)

# Test with σ¹ = s1_v·dv + s1_r·dr + s1_p·dφ
print("\n--- Test 2a: σ¹ = s1_v·dv + s1_r·dr + s1_p·dφ ---")
sigma_test = [dict(sigma_base[0]), {0: s1_v, 1: s1_r, 2: s1_p}, dict(sigma_base[2])]

print("Checking EOM2...")
r2 = eom2_T_sigma(omega_in, e_in, sigma_test, coords)
for a_idx in range(3):
    labels = ['0̄', '1̄', '2̄']
    print(f"  EOM2[{labels[a_idx]}]: {r2[a_idx]}")

# Collect all EOM2 constraints
eom2_constraints = []
for a_idx in range(3):
    for k, v in r2[a_idx].items():
        eom2_constraints.append(v)

print(f"\nEOM2 constraint equations ({len(eom2_constraints)}):")
for i, c in enumerate(eom2_constraints):
    print(f"  [{i}] {c} = 0")

# Try to solve for σ¹ components from EOM2
print("\nSolving EOM2 for σ¹ components...")
sol_eom2 = solve(eom2_constraints, [s1_v, s1_r, s1_p], dict=True)
print(f"  Solutions: {sol_eom2}")

if not sol_eom2:
    print("  → No solution found. Trying without s1_r...")
    sol_eom2_partial = solve(eom2_constraints, [s1_v, s1_p], dict=True)
    print(f"  Partial solutions (s1_v, s1_p): {sol_eom2_partial}")

    if not sol_eom2_partial:
        print("  → Still no solution. Individual equations force σ¹=0.")
        # Check each equation individually
        for i, c in enumerate(eom2_constraints):
            s_v = solve(c, s1_v)
            s_r = solve(c, s1_r)
            s_p = solve(c, s1_p)
            print(f"    eq[{i}]: s1_v={s_v}, s1_r={s_r}, s1_p={s_p}")

# If we got solutions, check EOM3
if sol_eom2:
    for idx, sol in enumerate(sol_eom2):
        print(f"\n--- Solution {idx}: {sol} ---")
        sigma_solved = [
            dict(sigma_base[0]),
            {0: sol.get(s1_v, 0), 1: sol.get(s1_r, 0), 2: sol.get(s1_p, 0)},
            dict(sigma_base[2]),
        ]
        r3 = eom3_F_ee(omega_in, e_in, sigma_solved, ell, coords)
        print(f"  EOM3[0̄] = {r3[0]}")
        print(f"  EOM3[1̄] = {r3[1]}")
        print(f"  EOM3[2̄] = {r3[2]}")

# Test 2b: Only σ¹_dv (simplest non-trivial case)
print("\n--- Test 2b: σ¹ = s1_v·dv only ---")
sigma_test2 = [dict(sigma_base[0]), {0: s1_v}, dict(sigma_base[2])]

r2_b = eom2_T_sigma(omega_in, e_in, sigma_test2, coords)
print("EOM2 constraints:")
for a_idx in range(3):
    print(f"  [{['0̄','1̄','2̄'][a_idx]}]: {r2_b[a_idx]}")

constraints_b = []
for a_idx in range(3):
    for k, v in r2_b[a_idx].items():
        constraints_b.append(v)
sol_b = solve(constraints_b, s1_v, dict=True)
print(f"  s1_v solutions from EOM2: {sol_b}")

if sol_b:
    for s in sol_b:
        print(f"\n  Substituting s1_v = {s[s1_v]} into EOM3...")
        sigma_sub = [dict(sigma_base[0]), {0: s[s1_v]}, dict(sigma_base[2])]
        r3_sub = eom3_F_ee(omega_in, e_in, sigma_sub, ell, coords)
        print(f"    EOM3[0̄] = {r3_sub[0]}")

# Test 2c: Only σ¹_φ
print("\n--- Test 2c: σ¹ = s1_p·dφ only ---")
sigma_test3 = [dict(sigma_base[0]), {2: s1_p}, dict(sigma_base[2])]

r2_c = eom2_T_sigma(omega_in, e_in, sigma_test3, coords)
print("EOM2 constraints:")
for a_idx in range(3):
    print(f"  [{['0̄','1̄','2̄'][a_idx]}]: {r2_c[a_idx]}")

constraints_c = []
for a_idx in range(3):
    for k, v in r2_c[a_idx].items():
        constraints_c.append(v)
sol_c = solve(constraints_c, s1_p, dict=True)
print(f"  s1_p solutions from EOM2: {sol_c}")

if sol_c:
    for s in sol_c:
        sigma_sub = [dict(sigma_base[0]), {2: s[s1_p]}, dict(sigma_base[2])]
        r3_sub = eom3_F_ee(omega_in, e_in, sigma_sub, ell, coords)
        print(f"  EOM3[0̄] with s1_p={s[s1_p]}: {r3_sub[0]}")

print("\n✓ Path 2 complete.")
