#!/usr/bin/env python3
"""
Convention Sweep — AdSL BTZ EOM Verification
Systematically test sign conventions to find the combination that passes all 3 EOMs.

Parameters swept:
  eps_sign: ±1 — overall sign of ε^{abc} (default: -1)
  sigma_sign: ±1 — σ = sigma_sign * κ (default: -1)
  Ta_sign: ±1 — T^a = de^a + Ta_sign * ε^{abc} ω_b ∧ e_c (default: -1, i.e. minus)
  Fa_half: bool — whether F^a includes (1/2)ε^{abc}σ_b∧σ_c term (default: True)

Total: 2^4 = 16 combinations × 2 frames = 32 checks
"""

from sympy import symbols, simplify, expand, Rational, diff
from itertools import product

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')
u, phi_hat = symbols('u phi_hat')

COORD_LABELS = ['0̄', '1̄', '2̄']

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

def eom1_R(omega, coords):
    ol = lower(omega)
    results = []
    for a in range(3):
        dw = d1(omega[a], coords)
        terms = []
        for bv in range(3):
            for cv in range(3):
                e = eps_abc(a, bv, cv, sign=1)  # EOM1 doesn't depend on eps_sign
                if e == 0 or bv == cv: continue
                if ol[bv] and ol[cv]:
                    terms.append(smul2(Rational(1, 2) * e, wedge(ol[bv], ol[cv])))
        eps_part = add2(*terms) if terms else {}
        R = simp2(add2(dw, neg2(eps_part)))
        results.append(R)
    return results

def eom2_T_sigma(omega, e, sigma, coords, eps_sign, Ta_sign):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        de = d1(e[a], coords)
        tw = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if ol[bv] and el[cv]:
                    tw.append(smul2(Ta_sign * ev, wedge(ol[bv], el[cv])))
        Ta = add2(de, neg2(add2(*tw))) if tw else de
        se = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if sl[bv] and el[cv]:
                    se.append(smul2(ev, wedge(sl[bv], el[cv])))
        st = add2(*se) if se else {}
        results.append(simp2(add2(Ta, st)))
    return results

def eom3_F_ee(omega, e, sigma, ell_sym, coords, eps_sign, Ta_sign, Fa_half):
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        ds = d1(sigma[a], coords)
        ws = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0: continue
                if ol[bv] and sl[cv]:
                    ws.append(smul2(Ta_sign * ev, wedge(ol[bv], sl[cv])))
        Ds = add2(ds, neg2(add2(*ws))) if ws else ds
        ss = []
        if Fa_half:
            for bv in range(3):
                for cv in range(3):
                    ev = eps_abc(a, bv, cv, sign=eps_sign)
                    if ev == 0 or bv == cv: continue
                    if sl[bv] and sl[cv]:
                        ss.append(smul2(Rational(1, 2) * ev, wedge(sl[bv], sl[cv])))
        sst = add2(*ss) if ss else {}
        Fa = add2(Ds, sst)
        ee = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv, sign=eps_sign)
                if ev == 0 or bv == cv: continue
                if el[bv] and el[cv]:
                    ee.append(smul2(Rational(1, 2) / ell_sym**2 * ev, wedge(el[bv], el[cv])))
        eet = add2(*ee) if ee else {}
        results.append(simp2(add2(Fa, eet)))
    return results

def check_all_zero(results):
    return all(len(R) == 0 for R in results)

# ── Frame definitions ──
coords_in = [v, r, phi]
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

coords_out = [u, r, phi_hat]
e_out = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: -1, 2: -Rational(1, 2)*J},
    {0: 1},
    {2: r},
]

# ── Sweep ──
print("=" * 80)
print("CONVENTION SWEEP — AdSL BTZ EOM Verification")
print("=" * 80)
print(f"{'eps':>4} {'sig':>4} {'Ta':>4} {'Fa½':>4} | {'EOM1-in':>8} {'EOM2-in':>8} {'EOM3-in':>8} | {'EOM1-out':>8} {'EOM2-out':>8} {'EOM3-out':>8} | ALL?")
print("-" * 110)

winners = []

for eps_s, sigma_s, Ta_s, Fa_h in product([1, -1], [1, -1], [1, -1], [True, False]):
    sigma_in = [{k: sigma_s * v for k, v in f.items()} for f in kappa_in]
    sigma_out = sigma_in
    omega_out = omega_in

    r1i = eom1_R(omega_in, coords_in)
    r2i = eom2_T_sigma(omega_in, e_in, sigma_in, coords_in, eps_s, Ta_s)
    r3i = eom3_F_ee(omega_in, e_in, sigma_in, ell, coords_in, eps_s, Ta_s, Fa_h)

    r1o = eom1_R(omega_out, coords_out)
    r2o = eom2_T_sigma(omega_out, e_out, sigma_out, coords_out, eps_s, Ta_s)
    r3o = eom3_F_ee(omega_out, e_out, sigma_out, ell, coords_out, eps_s, Ta_s, Fa_h)

    c1i = check_all_zero(r1i)
    c2i = check_all_zero(r2i)
    c3i = check_all_zero(r3i)
    c1o = check_all_zero(r1o)
    c2o = check_all_zero(r2o)
    c3o = check_all_zero(r3o)

    all_pass = c1i and c2i and c3i and c1o and c2o and c3o

    def tag(ok): return "✅" if ok else "❌"

    print(f"{eps_s:+4d} {sigma_s:+4d} {Ta_s:+4d} {'Y' if Fa_h else 'N':>4} | "
          f"{tag(c1i):>8} {tag(c2i):>8} {tag(c3i):>8} | "
          f"{tag(c1o):>8} {tag(c2o):>8} {tag(c3o):>8} | "
          f"{'✅ ALL' if all_pass else '❌'}")

    if all_pass:
        winners.append((eps_s, sigma_s, Ta_s, Fa_h))
    elif c1i and c1o and (c2i or c3i):  # partial: EOM1 pass + at least one more
        # Record partial matches for analysis
        score = sum([c1i, c2i, c3i, c1o, c2o, c3o])
        if score >= 4:
            winners.append((eps_s, sigma_s, Ta_s, Fa_h, f"PARTIAL({score}/6)"))
            # Print residuals for partial matches
            if not c2i:
                print(f"       EOM2-in residuals: {r2i}")
            if not c3i:
                print(f"       EOM3-in residuals: {r3i}")
            if not c2o:
                print(f"       EOM2-out residuals: {r2o}")
            if not c3o:
                print(f"       EOM3-out residuals: {r3o}")

print("\n" + "=" * 80)
if winners:
    print(f"WINNERS ({len(winners)}):")
    for w in winners:
        if len(w) == 4:
            print(f"  eps={w[0]:+d}, σ={w[1]:+d}, T^a={w[2]:+d}, Fa_half={w[3]}")
        else:
            print(f"  eps={w[0]:+d}, σ={w[1]:+d}, T^a={w[2]:+d}, Fa_half={w[3]} — {w[4]}")
else:
    print("NO WINNER: No convention combination passes all 6 checks.")
    print("This suggests the issue may be in:")
    print("  - The connection (ω, σ, e) values themselves")
    print("  - A missing term in the EOM definitions")
    print("  - The index lowering scheme for antidiagonal η")

print("\n✓ Sweep complete.")
