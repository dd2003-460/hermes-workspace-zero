#!/usr/bin/env python3
"""
EOM3 Deep Dive — Path 1: σ⁰ dv component correction
任务ID: adsl-eom3-deep-dive | 创建时间: 2026-04-01 | 关联项目: adsl-spin-connection

Question: If σ⁰ has an additional dv component δσ⁰_dv, can it cancel the EOM3 residual?
- Substitute σ⁰ → σ⁰ + δσ⁰_dv·dv into EOM3
- Solve for δσ⁰_dv that makes EOM3 vanish
- Check whether this correction violates EOM2
"""

from sympy import symbols, simplify, expand, Rational, diff, solve, Function

r, ell, M, b, J = symbols('r ell M b J', real=True)
v, phi = symbols('v phi')
dv_coeff = Function('dv_coeff')(r)

coords = [v, r, phi]

# ── Form algebra (same as branch_A_corrected.py) ──

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

# Fix simp2 typo
def simp2(f):
    return {k: simplify(v) for k, v in f.items() if simplify(v) != 0}

# ── EOM3 function ──

def eom3_F_ee(omega, e, sigma, ell_sym, coords):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        ds = d1(sigma[a], coords)
        ws = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_upper(a, bv, cv)
                if ev == 0:
                    continue
                if ol[bv] and sl[cv]:
                    ws.append(smul2(ev, wedge(ol[bv], sl[cv])))
        Ds = add2(ds, neg2(add2(*ws))) if ws else ds
        ss = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_upper(a, bv, cv)
                if ev == 0 or bv == cv:
                    continue
                if sl[bv] and sl[cv]:
                    ss.append(smul2(Rational(1, 2) * ev, wedge(sl[bv], sl[cv])))
        sst = add2(*ss) if ss else {}
        Fa = add2(Ds, sst)
        ee = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_lower(a, bv, cv)
                if ev == 0 or bv == cv:
                    continue
                if el[bv] and el[cv]:
                    ee.append(smul2(Rational(1, 2) / ell_sym**2 * ev, wedge(el[bv], el[cv])))
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
                if ev == 0:
                    continue
                if ol[bv] and el[cv]:
                    tw.append(smul2(ev, wedge(ol[bv], el[cv])))
        Ta = add2(de, neg2(add2(*tw))) if tw else de
        se = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_lower(a, bv, cv)
                if ev == 0:
                    continue
                if sl[bv] and el[cv]:
                    se.append(smul2(ev, wedge(sl[bv], el[cv])))
        st = add2(*se) if se else {}
        results.append(simp2(add2(Ta, st)))
    return results

# ── Ingoing EF frame ──

e_in = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: 1, 2: -Rational(1, 2)*J},
    {0: 1},
    {2: r},
]
omega_in = [
    {2: -Rational(1, 2)*b},
    {2: 1},
    {},
]
kappa_in = [
    {0: Rational(1, 2)*J/ell**2, 2: Rational(1, 2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma_base = [{k: -v for k, v in f.items()} for f in kappa_in]

print("=" * 70)
print("  Path 1: σ⁰ dv component correction")
print("=" * 70)

# First, compute the EOM3 residual with unmodified σ
r3_orig = eom3_F_ee(omega_in, e_in, sigma_base, ell, coords)
print("\nOriginal EOM3 [0̄] residual:")
print(f"  {r3_orig[0]}")

# Now modify σ⁰ to include δσ⁰_dv (component 0 = dv)
sigma_mod = [dict(sigma_base[0]), dict(sigma_base[1]), dict(sigma_base[2])]
sigma_mod[0][0] = sigma_mod[0].get(0, 0) + dv_coeff  # add δσ⁰_dv·dv

print(f"\nModified σ⁰ = {sigma_mod[0]}")

r3_mod = eom3_F_ee(omega_in, e_in, sigma_mod, ell, coords)

print("\nModified EOM3 [0̄]:")
print(f"  {r3_mod[0]}")

# Extract (dv,dr) = (0,1) component
if (0, 1) in r3_mod[0]:
    expr = r3_mod[0][(0, 1)]
    print(f"\n(0,1) component: {expr}")
    sol = solve(expr, dv_coeff)
    print(f"  Solution for δσ⁰_dv: {sol}")
else:
    print("\n(0,1) component: absent (coefficient = 0)")
    print("  → σ⁰ dv correction has NO effect on EOM3 (0,1)!")
    sol = []

# Check EOM2 with the correction
print("\n" + "-" * 70)
print("  Checking EOM2 with corrected σ⁰...")
print("-" * 70)

r2_mod = eom2_T_sigma(omega_in, e_in, sigma_mod, coords)
print("\nModified EOM2 [0̄]:")
print(f"  {r2_mod[0]}")
print("Modified EOM2 [1̄]:")
print(f"  {r2_mod[1]}")
print("Modified EOM2 [2̄]:")
print(f"  {r2_mod[2]}")

e2_ok = all(len(r) == 0 for r in r2_mod)
print(f"\nEOM2 still satisfied? {'✅ YES' if e2_ok else '❌ NO'}")

if sol:
    print("\n" + "-" * 70)
    print("  Substituting solution back into EOM2...")
    print("-" * 70)
    for s in sol:
        print(f"\n  If δσ⁰_dv = {s}:")
        r2_sub = [dict(r) for r in r2_mod]
        for a_idx in range(3):
            for k in list(r2_sub[a_idx].keys()):
                val = simplify(r2_sub[a_idx][k].subs(dv_coeff, s))
                if val == 0:
                    del r2_sub[a_idx][k]
                else:
                    r2_sub[a_idx][k] = val
        e2_ok_sub = all(len(r) == 0 for r in r2_sub)
        print(f"    EOM2 satisfied? {'✅ YES' if e2_ok_sub else '❌ NO'}")
        if not e2_ok_sub:
            for a_idx in range(3):
                if r2_sub[a_idx]:
                    print(f"    EOM2[{a_idx}] residual: {r2_sub[a_idx]}")

# Also check what σ⁰_dv correction does to EOM3 other components
print("\n" + "-" * 70)
print("  Full EOM3 with σ⁰ dv correction:")
print("-" * 70)
for a_idx in range(3):
    labels = ['0̄', '1̄', '2̄']
    ok = len(r3_mod[a_idx]) == 0
    print(f"  [{labels[a_idx]}] {'✅ 0' if ok else f'❌ {r3_mod[a_idx]}'}")

print("\n✓ Path 1 complete.")
