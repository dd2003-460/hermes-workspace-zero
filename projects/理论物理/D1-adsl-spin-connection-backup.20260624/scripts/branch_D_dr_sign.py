#!/usr/bin/env python3
"""
Branch D: Ingoing dr sign investigation
Outgoing EOM2 passes ✅ but ingoing EOM2 fails ❌.
Key difference: e⁰ dr coefficient is +1 (ingoing) vs -1 (outgoing).
ω is identical in both frames (same formula, different coord names).

Hypothesis: If we flip the dr sign in e⁰ for ingoing frame,
does EOM2 also pass? This would suggest the paper's ω for ingoing
is actually for a frame with -dr (or outgoing ω is used for ingoing).
"""

from sympy import symbols, Rational, expand, simplify

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

def compute_eoms(omega, e, sigma, ell_sym, coords, label):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    # EOM1
    all_ok1 = True
    for a in range(3):
        dw = d1(omega[a], coords)
        terms = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_upper(a, bv, cv)
                if ev == 0 or bv == cv: continue
                if ol[bv] and ol[cv]:
                    terms.append(smul2(Rational(1,2)*ev, wedge(ol[bv], ol[cv])))
        R = simp2(add2(dw, neg2(add2(*terms)))) if terms else simp2(dw)
        ok = len(R) == 0
        all_ok1 = all_ok1 and ok
        print(f"  EOM1[{a}]: {'✅' if ok else '❌ ' + str(R)}")
    print(f"  EOM1: {'✅ ALL PASS' if all_ok1 else '❌ SOME FAIL'}")

    # EOM2
    all_ok2 = True
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
        res = simp2(add2(Ta, st))
        ok = len(res) == 0
        all_ok2 = all_ok2 and ok
        print(f"  EOM2[{a}]: {'✅' if ok else '❌ ' + str(res)}")
    print(f"  EOM2: {'✅ ALL PASS' if all_ok2 else '❌ SOME FAIL'}")

    # EOM3
    all_ok3 = True
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
        res = simp2(add2(Fa, eet))
        ok = len(res) == 0
        all_ok3 = all_ok3 and ok
        print(f"  EOM3[{a}]: {'✅' if ok else '❌ ' + str(res)}")
    print(f"  EOM3: {'✅ ALL PASS' if all_ok3 else '❌ SOME FAIL'}")

coords = [v, r, phi]
omega_std = [{2: -Rational(1,2)*b}, {2: Rational(1)}, {}]
kappa = [
    {0: Rational(1,2)*J/ell**2, 2: Rational(1,2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma = [{k: -vv for k,vv in f.items()} for f in kappa]

# Test 1: Standard ingoing (e⁰ dr = +1)
e_std = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: Rational(1), 2: -Rational(1,2)*J},
    {0: Rational(1)},
    {2: r},
]
compute_eoms(omega_std, e_std, sigma, ell, coords, "Test 1: Ingoing standard (dr=+1)")

# Test 2: Flipped dr in e⁰ (e⁰ dr = -1)
e_flip = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: -Rational(1), 2: -Rational(1,2)*J},
    {0: Rational(1)},
    {2: r},
]
compute_eoms(omega_std, e_flip, sigma, ell, coords, "Test 2: Ingoing with e⁰ dr=-1 (outgoing e⁰)")

# Test 3: Outgoing standard (e⁰ dr = -1, using u instead of v)
u_coord = symbols('u')
coords_out = [u_coord, r, phi]
e_out = [
    {0: Rational(1,2)/ell**2*(ell**2*M - r**2), 1: -Rational(1), 2: -Rational(1,2)*J},
    {0: Rational(1)},
    {2: r},
]
omega_out = [{2: -Rational(1,2)*b}, {2: Rational(1)}, {}]
kappa_out = [
    {0: Rational(1,2)*J/ell**2, 2: Rational(1,2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma_out = [{k: -vv for k,vv in f.items()} for f in kappa_out]
compute_eoms(omega_out, e_out, sigma_out, ell, coords_out, "Test 3: Outgoing standard (dr=-1)")

# Test 4: What if we use outgoing ω with ingoing e? (ω has dφ→dφ̂ but same form)
# Use ingoing coords but with outgoing e⁰ (dr=-1)
compute_eoms(omega_std, e_flip, sigma, ell, coords, "Test 4: Ingoing coords + outgoing e⁰ + ingoing ω")

print("\n✓ Branch D complete.")
