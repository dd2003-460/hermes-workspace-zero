#!/usr/bin/env python3
"""
Deep dive: outgoing frame analysis for the two partial-winning conventions.
Why does ingoing pass but outgoing fail with the same ω, σ?
"""

from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')
u, phi_hat = symbols('u phi_hat')

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
    return {k: v for k, v in result.items() if v != 0}

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

def eps_abc(a, b, c, sign=1):
    if len({a, b, c}) < 3: return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return sign * (-((-1) ** inv))

# ── Frame definitions ──
# Ingoing: e[0] has {0: f(r), 1: +1, 2: -J/2}
# Outgoing: e[0] has {0: f(r), 1: -1, 2: -J/2}  ← only the dr coefficient differs

f_r = Rational(1, 2)/ell**2 * (ell**2*M - r**2)

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

# Best convention: eps=+1, sigma=-1 (σ = -κ), Ta=-1, Fa_half=True
eps_sign = 1
sigma = [{k: -v for k, v in f.items()} for f in kappa]
Ta_sign = -1

print("=" * 70)
print("ANALYSIS: Why outgoing fails with eps=+1, σ=-1, T^a sign=-1")
print("=" * 70)

# ── Compute T^a for both frames ──
for frame_name, e_form, coords in [
    ("INGOING", [
        {0: f_r, 1: 1, 2: -Rational(1, 2)*J},
        {0: 1},
        {2: r},
    ], [v, r, phi]),
    ("OUTGOING", [
        {0: f_r, 1: -1, 2: -Rational(1, 2)*J},
        {0: 1},
        {2: r},
    ], [u, r, phi_hat]),
]:
    ol, el, sl = lower(omega), lower(e_form), lower(sigma)
    print(f"\n{'─'*70}")
    print(f"  {frame_name} FRAME")
    print(f"{'─'*70}")

    print(f"\n  e forms: {e_form}")
    print(f"  ω forms: {omega}")
    print(f"  σ forms: {sigma}")

    # EOM2: T^a + εσe = 0
    print(f"\n  EOM2 Breakdown (T^a + εσe):")
    for a in range(3):
        de = d1(e_form[a], coords)
        print(f"\n    a={a}: de^a = {de}")

        # T^a = de^a + Ta_sign * ε ω∧e
        tw = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if ol[bv] and el[cv]:
                    w = wedge(ol[bv], el[cv])
                    term = smul2(Ta_sign * ev, w)
                    print(f"      ω∧e: Ta_sign*ε^{a}{bv}{cv} * ω_{bv}∧e_{cv} = {Ta_sign}*{ev} * {w} = {term}")
                    tw.append(term)
        Ta = add2(de, neg2(add2(*tw))) if tw else de
        print(f"    T^a = {simp2(Ta)}")

        # εσe
        se = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if sl[bv] and el[cv]:
                    w = wedge(sl[bv], el[cv])
                    term = smul2(ev, w)
                    print(f"      σ∧e: ε^{a}{bv}{cv} * σ_{bv}∧e_{cv} = {ev} * {w} = {term}")
                    se.append(term)
        st = add2(*se) if se else {}
        print(f"    εσe = {simp2(st)}")

        total = simp2(add2(Ta, st))
        print(f"    T^a + εσe = {total} {'✅' if len(total)==0 else '❌'}")

    # EOM3: F^a + (1/2ℓ²)εee = 0
    print(f"\n  EOM3 Breakdown (F^a + (1/2ℓ²)εee):")
    for a in range(3):
        ds = d1(sigma[a], coords)
        print(f"\n    a={a}: dσ^a = {ds}")

        ws = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if ol[bv] and sl[cv]:
                    w = wedge(ol[bv], sl[cv])
                    term = smul2(Ta_sign * ev, w)
                    print(f"      ω∧σ: Ta_sign*ε^{a}{bv}{cv} * ω_{bv}∧σ_{cv} = {Ta_sign}*{ev} * {w} = {term}")
                    ws.append(term)
        Ds = add2(ds, neg2(add2(*ws))) if ws else ds
        print(f"    D_ω σ^a = {simp2(Ds)}")

        ss = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0 or bv == cv: continue
                if sl[bv] and sl[cv]:
                    w = wedge(sl[bv], sl[cv])
                    term = smul2(Rational(1, 2) * ev, w)
                    print(f"      σ∧σ: (1/2)ε^{a}{bv}{cv} * σ_{bv}∧σ_{cv} = (1/2)*{ev} * {w} = {term}")
                    ss.append(term)
        sst = add2(*ss) if ss else {}
        print(f"    (1/2)εσσ = {simp2(sst)}")

        Fa = add2(Ds, sst)
        print(f"    F^a = {simp2(Fa)}")

        ee = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0 or bv == cv: continue
                if el[bv] and el[cv]:
                    w = wedge(el[bv], el[cv])
                    term = smul2(Rational(1, 2) / ell**2 * ev, w)
                    print(f"      e∧e: (1/2ℓ²)ε^{a}{bv}{cv} * e_{bv}∧e_{cv} = (1/2ℓ²)*{ev} * {w} = {term}")
                    ee.append(term)
        eet = add2(*ee) if ee else {}
        print(f"    (1/2ℓ²)εee = {simp2(eet)}")

        total = simp2(add2(Fa, eet))
        print(f"    F^a + (1/2ℓ²)εee = {total} {'✅' if len(total)==0 else '❌'}")

print(f"\n{'='*70}")
print("CONCLUSION")
print("="*70)
print("""
The outgoing frame e[0] has dr coefficient = -1 vs +1 for ingoing.
This changes de^a (same), but changes ω_b ∧ e_c and σ_b ∧ e_c wedges.

Key difference: In outgoing, e[0][1]=-1 means:
  - e_1 (lowered) = e[0] = {0: f(r), 1: -1, 2: -J/2} (instead of +1)
  - Wedges involving e_1 pick up opposite signs

If the connection ω is truly frame-independent (same ω^a in both frames),
then the EOMs can only be satisfied in both frames if ω^a transforms
appropriately between frames. The paper may define ω^a differently for
ingoing vs outgoing coordinates.

CHECK: Does the paper define ω^a in a frame-dependent way?
""")
