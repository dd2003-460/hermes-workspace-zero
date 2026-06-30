#!/usr/bin/env python3
"""
AdSL Gravity BTZ — EOM Verification (CORRECTED ε convention)
Fix: use ε_{abc} (with ε_{012}=+1) in EOMs, matching JHEP 09 (2023) 185.

The original script used ε^{abc} (ε^{012}=-1) everywhere.
For antidiagonal η = antidiag(1,1,0;1,0,0;0,0,1): ε_{abc} = -ε^{abc}.
This sign flip affects ALL EOM2 and EOM3 terms.

Definitions (paper §2) use ε^{abc} (standard connection).
EOMs (paper §2) use ε_{abc} (lowered, matching covariant derivative).
"""

from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, J, b = symbols('r ell M J b', real=True)
v, phi = symbols('v phi')
u, phi_hat = symbols('u phi_hat')

COORD_LABELS = ['0̄', '1̄', '2̄']

# ── Differential form algebra ──

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
    """Lower indices: ω_0 = ω^1, ω_1 = ω^0, ω_2 = ω^2 (antidiagonal η)"""
    return [conn[1], conn[0], conn[2]]

def eps_upper(a, b, c):
    """ε^{abc} with ε^{012} = -1 (for definitions R^a, T^a, F^a)"""
    if len({a, b, c}) < 3:
        return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return -((-1) ** inv)

def eps_lower(a, b, c):
    """ε_{abc} with ε_{012} = +1 (for EOMs)"""
    if len({a, b, c}) < 3:
        return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return (-1) ** inv

# ── EOM functions (CORRECTED) ──

def eom1_R(omega, coords):
    """R^a = dω^a - (1/2)ε^{abc}ω_b ∧ ω_c
    Note: definitions use ε^{abc}."""
    ol = lower(omega)
    results = []
    for a in range(3):
        dw = d1(omega[a], coords)
        terms = []
        for b in range(3):
            for c in range(3):
                e = eps_upper(a, b, c)
                if e == 0 or b == c:
                    continue
                if ol[b] and ol[c]:
                    terms.append(smul2(Rational(1, 2) * e, wedge(ol[b], ol[c])))
        eps_part = add2(*terms) if terms else {}
        R = simp2(add2(dw, neg2(eps_part)))
        results.append(R)
    return results

def eom2_T_sigma(omega, e, sigma, coords):
    """T^a + ε_{abc}σ^b ∧ e^c = 0  (CORRECTED: ε_{abc} not ε^{abc})
    T^a = de^a - ε^{abc}ω_b ∧ e_c  (definition uses ε^{abc})
    """
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        de = d1(e[a], coords)
        # T^a = de^a - ε^{abc} ω_b ∧ e_c  (definition: ε^{abc})
        tw = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_upper(a, bv, cv)
                if ev == 0:
                    continue
                if ol[bv] and el[cv]:
                    tw.append(smul2(ev, wedge(ol[bv], el[cv])))
        Ta = add2(de, neg2(add2(*tw))) if tw else de
        # ε_{abc} σ^b ∧ e^c  (EOM: ε_{abc}, NOT ε^{abc})
        se = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_lower(a, bv, cv)  # CHANGED: eps_lower
                if ev == 0:
                    continue
                if sl[bv] and el[cv]:
                    se.append(smul2(ev, wedge(sl[bv], el[cv])))
        st = add2(*se) if se else {}
        results.append(simp2(add2(Ta, st)))
    return results

def eom3_F_ee(omega, e, sigma, ell_sym, coords):
    """F^a + (1/2ℓ²)ε_{abc}e^b ∧ e^c = 0  (CORRECTED: ε_{abc})
    F^a = D_ω σ^a + (1/2)ε^{abc}σ_b ∧ σ_c  (definition uses ε^{abc})
    D_ω σ^a = dσ^a - ε^{abc}ω_b ∧ σ_c  (definition uses ε^{abc})
    """
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    results = []
    for a in range(3):
        ds = d1(sigma[a], coords)
        # D_ω σ^a = dσ^a - ε^{abc} ω_b ∧ σ_c  (definition: ε^{abc})
        ws = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_upper(a, bv, cv)
                if ev == 0:
                    continue
                if ol[bv] and sl[cv]:
                    ws.append(smul2(ev, wedge(ol[bv], sl[cv])))
        Ds = add2(ds, neg2(add2(*ws))) if ws else ds
        # (1/2) ε^{abc} σ_b ∧ σ_c  (definition: ε^{abc})
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
        # (1/2ℓ²) ε_{abc} e_b ∧ e_c  (EOM: ε_{abc}, NOT ε^{abc})
        ee = []
        for bv in range(3):
            for cv in range(3):
                ev = eps_lower(a, bv, cv)  # CHANGED: eps_lower
                if ev == 0 or bv == cv:
                    continue
                if el[bv] and el[cv]:
                    ee.append(smul2(Rational(1, 2) / ell_sym**2 * ev, wedge(el[bv], el[cv])))
        eet = add2(*ee) if ee else {}
        results.append(simp2(add2(Fa, eet)))
    return results


def print_results(title, results):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    all_ok = True
    for a, R in enumerate(results):
        ok = len(R) == 0
        all_ok = all_ok and ok
        tag = '✅ 0' if ok else f'❌ {R}'
        print(f"  [{COORD_LABELS[a]}] {tag}")
    print(f"  → {'✅ ALL PASS' if all_ok else '❌ SOME NON-ZERO'}")
    return all_ok


# ═══════════════════════════════════════
# INGOING EF: (v=0, r=1, phi=2)
# ═══════════════════════════════════════
print("INGOING EF FRAME — BTZ Black Hole (CORRECTED ε)")
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
sigma_in = [{k: -v for k, v in f.items()} for f in kappa_in]

r1_in = eom1_R(omega_in, coords_in)
print_results("EOM 1: R^a = 0 (Ingoing)", r1_in)

r2_in = eom2_T_sigma(omega_in, e_in, sigma_in, coords_in)
print_results("EOM 2: T^a + ε_{abc}σ^b∧e^c = 0 (Ingoing)", r2_in)

r3_in = eom3_F_ee(omega_in, e_in, sigma_in, ell, coords_in)
print_results("EOM 3: F^a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0 (Ingoing)", r3_in)


# ═══════════════════════════════════════
# OUTGOING EF: (u=0, r=1, phi_hat=2)
# ═══════════════════════════════════════
print("\n\nOUTGOING EF FRAME — BTZ Black Hole (CORRECTED ε)")
coords_out = [u, r, phi_hat]

e_out = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: -1, 2: -Rational(1, 2)*J},
    {0: 1},
    {2: r},
]
omega_out = [
    {2: -Rational(1, 2)*b},
    {2: 1},
    {},
]
kappa_out = [
    {0: Rational(1, 2)*J/ell**2, 2: Rational(1, 2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma_out = [{k: -v for k, v in f.items()} for f in kappa_out]

r1_out = eom1_R(omega_out, coords_out)
print_results("EOM 1: R^a = 0 (Outgoing)", r1_out)

r2_out = eom2_T_sigma(omega_out, e_out, sigma_out, coords_out)
print_results("EOM 2: T^a + ε_{abc}σ^b∧e^c = 0 (Outgoing)", r2_out)

r3_out = eom3_F_ee(omega_out, e_out, sigma_out, ell, coords_out)
print_results("EOM 3: F^a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0 (Outgoing)", r3_out)


# ── Summary ──
print(f"\n{'='*60}")
print("  SUMMARY (Corrected ε_{abc} convention)")
print(f"{'='*60}")
all_results = [
    ("EOM1 Ingoing", r1_in), ("EOM1 Outgoing", r1_out),
    ("EOM2 Ingoing", r2_in), ("EOM2 Outgoing", r2_out),
    ("EOM3 Ingoing", r3_in), ("EOM3 Outgoing", r3_out),
]
for name, res in all_results:
    ok = all(len(r) == 0 for r in res)
    print(f"  {name:20s}: {'✅ PASS' if ok else '❌ FAIL'}")

print("\n✓ Corrected verification complete.")
