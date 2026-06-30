#!/usr/bin/env python3
"""
Deep debug: compute EOM2 and EOM3 term-by-term for outgoing frame.
Compare with ingoing frame to identify exactly where sign flips should happen.
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

def lower(conn):
    """η = antidiag(1,1,1): ω_0=ω^1, ω_1=ω^0, ω_2=ω^2"""
    return [conn[1], conn[0], conn[2]]

def eps_abc(a, b, c):
    if len({a, b, c}) < 3: return 0
    arr = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if arr[i] > arr[j])
    return -((-1) ** inv)

CO2 = {(0,1): 'dv∧dr', (0,2): 'dv∧dφ', (1,2): 'dr∧dφ'}
CO2_OUT = {(0,1): 'du∧dr', (0,2): 'du∧dφ̂', (1,2): 'dr∧dφ̂'}

def pf(f, labels=None):
    """Pretty-print a 2-form dict."""
    if not f: return "0"
    parts = []
    for k in sorted(f.keys()):
        lab = (labels or CO2).get(k, str(k))
        parts.append(f"({expand(f[k])}){lab}")
    return " + ".join(parts)

# ═══════════════════════════════════════
# INGOING FRAME
# ═══════════════════════════════════════
coords_in = [v, r, phi]
e_in = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: 1, 2: -Rational(1, 2)*J},  # e^0̄
    {0: 1},   # e^1̄
    {2: r},   # e^2̄
]
omega_in = [
    {2: -Rational(1, 2)*b},  # ω^0̄
    {2: 1},                   # ω^1̄
    {},                       # ω^2̄
]
kappa_in = [
    {0: Rational(1, 2)*J/ell**2, 2: Rational(1, 2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma_in = [{k: -v for k, v in f.items()} for f in kappa_in]

# ═══════════════════════════════════════
# OUTGOING FRAME
# ═══════════════════════════════════════
coords_out = [u, r, phi_hat]
e_out = [
    {0: Rational(1, 2)/ell**2 * (ell**2*M - r**2), 1: -1, 2: -Rational(1, 2)*J},  # ê^0̄: dr coefficient is -1!
    {0: 1},   # ê^1̄
    {2: r},   # ê^2̄
]
# Paper says: ω̂^0̄ = -(b/2)dφ̂, ω̂^1̄ = dφ̂, ω̂^2̄ = 0
omega_out = [
    {2: -Rational(1, 2)*b},
    {2: 1},
    {},
]
# Paper says: κ̂^0̄ = J/(2ℓ²)du + (1/2)(r²/ℓ²-M-b)dφ̂, κ̂^1̄ = 0, κ̂^2̄ = -(r/ℓ²)du
kappa_out = [
    {0: Rational(1, 2)*J/ell**2, 2: Rational(1, 2)*(r**2/ell**2 - M - b)},
    {},
    {0: -r/ell**2},
]
sigma_out = [{k: -v for k, v in f.items()} for f in kappa_out]

print("=" * 80)
print("DETAILED EOM ANALYSIS — INGOING vs OUTGOING")
print("=" * 80)

# ── EOM2 term-by-term ──
# T^a = de^a - ε^{abc} ω_b ∧ e_c   (script convention)
# + ε^{abc} σ_b ∧ e^c               (EOM2 addition)
for frame_name, e, omega, sigma, coords, labels in [
    ("INGOING", e_in, omega_in, sigma_in, coords_in, CO2),
    ("OUTGOING", e_out, omega_out, sigma_out, coords_out, CO2_OUT),
]:
    print(f"\n{'─'*80}")
    print(f"  EOM2 — {frame_name} FRAME")
    print(f"{'─'*80}")
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    
    for a in range(3):
        print(f"\n  Component [{['0̄','1̄','2̄'][a]}]:")
        
        # de^a
        de = d1(e[a], coords)
        print(f"    de^a = {pf(de, labels)}")
        
        # -ε^{abc} ω_b ∧ e_c  for each (b,c) pair
        ta_terms = {}
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv)
                if ev == 0: continue
                w = wedge(ol[bv], el[cv]) if ol[bv] and el[cv] else {}
                if w:
                    coeff = -ev
                    print(f"    -ε^{{{a}{bv}{cv}}} ω_{bv} ∧ e_{cv} = ({coeff}) × {pf(w, labels)}")
                    for k, v in w.items():
                        ta_terms[k] = ta_terms.get(k, 0) + coeff * v
        
        Ta = {k: expand(v) for k, v in {**de, **{k: de.get(k,0)+ta_terms.get(k,0) for k in set(de)|set(ta_terms)}}.items() if expand(ta_terms.get(k,0) + de.get(k,0)) != 0}
        # Recompute Ta properly
        Ta = {}
        for k in set(list(de.keys()) + list(ta_terms.keys())):
            val = expand(de.get(k, 0) + ta_terms.get(k, 0))
            if val != 0:
                Ta[k] = val
        print(f"    → T^a = {pf(Ta, labels)}")
        
        # ε^{abc} σ_b ∧ e^c
        se_terms = {}
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv)
                if ev == 0: continue
                w = wedge(sl[bv], el[cv]) if sl[bv] and el[cv] else {}
                if w:
                    print(f"    +ε^{{{a}{bv}{cv}}} σ_{bv} ∧ e_{cv} = ({ev}) × {pf(w, labels)}")
                    for k, v in w.items():
                        se_terms[k] = se_terms.get(k, 0) + ev * v
        
        se_sum = {k: expand(v) for k, v in se_terms.items() if expand(v) != 0}
        print(f"    → εσe = {pf(se_sum, labels)}")
        
        # Total EOM2
        total = {}
        for k in set(list(Ta.keys()) + list(se_sum.keys())):
            val = expand(Ta.get(k, 0) + se_sum.get(k, 0))
            if val != 0:
                total[k] = val
        status = "✅" if not total else "❌"
        print(f"    → T^a + εσe = {pf(total, labels)}  {status}")

# ── EOM3 term-by-term ──
for frame_name, e, omega, sigma, coords, labels in [
    ("INGOING", e_in, omega_in, sigma_in, coords_in, CO2),
    ("OUTGOING", e_out, omega_out, sigma_out, coords_out, CO2_OUT),
]:
    print(f"\n{'─'*80}")
    print(f"  EOM3 — {frame_name} FRAME")
    print(f"{'─'*80}")
    ol, el, sl = lower(omega), lower(e), lower(sigma)
    
    for a in range(3):
        print(f"\n  Component [{['0̄','1̄','2̄'][a]}]:")
        
        # dσ^a
        ds = d1(sigma[a], coords)
        print(f"    dσ^a = {pf(ds, labels)}")
        
        # -ε^{abc} ω_b ∧ σ_c
        ws_terms = {}
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv)
                if ev == 0: continue
                w = wedge(ol[bv], sl[cv]) if ol[bv] and sl[cv] else {}
                if w:
                    coeff = -ev
                    print(f"    -ε^{{{a}{bv}{cv}}} ω_{bv} ∧ σ_{cv} = ({coeff}) × {pf(w, labels)}")
                    for k, v in w.items():
                        ws_terms[k] = ws_terms.get(k, 0) + coeff * v
        
        # (1/2)ε^{abc} σ_b ∧ σ_c
        ss_terms = {}
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv)
                if ev == 0 or bv == cv: continue
                w = wedge(sl[bv], sl[cv]) if sl[bv] and sl[cv] else {}
                if w:
                    coeff = Rational(1, 2) * ev
                    print(f"    (1/2)ε^{{{a}{bv}{cv}}} σ_{bv} ∧ σ_{cv} = ({coeff}) × {pf(w, labels)}")
                    for k, v in w.items():
                        ss_terms[k] = ss_terms.get(k, 0) + coeff * v
        
        Fa = {}
        for k in set(list(ds.keys()) + list(ws_terms.keys()) + list(ss_terms.keys())):
            val = expand(ds.get(k, 0) + ws_terms.get(k, 0) + ss_terms.get(k, 0))
            if val != 0:
                Fa[k] = val
        print(f"    → F^a = {pf(Fa, labels)}")
        
        # (1/2ℓ²)ε^{abc} e_b ∧ e_c
        ee_terms = {}
        for bv in range(3):
            for cv in range(3):
                ev = eps_abc(a, bv, cv)
                if ev == 0 or bv == cv: continue
                w = wedge(el[bv], el[cv]) if el[bv] and el[cv] else {}
                if w:
                    coeff = Rational(1, 2) / ell**2 * ev
                    print(f"    (1/2ℓ²)ε^{{{a}{bv}{cv}}} e_{bv} ∧ e_{cv} = ({coeff/ Rational(1,2)/ell**2}) × (1/2ℓ²) × {pf(w, labels)}")
                    for k, v in w.items():
                        ee_terms[k] = ee_terms.get(k, 0) + coeff * v
        
        ee_sum = {k: expand(v) for k, v in ee_terms.items() if expand(v) != 0}
        print(f"    → (1/2ℓ²)εee = {pf(ee_sum, labels)}")
        
        # Total EOM3
        total = {}
        for k in set(list(Fa.keys()) + list(ee_sum.keys())):
            val = expand(Fa.get(k, 0) + ee_sum.get(k, 0))
            if val != 0:
                total[k] = val
        status = "✅" if not total else "❌"
        print(f"    → F^a + (1/2ℓ²)εee = {pf(total, labels)}  {status}")

# ── Key comparison: e^0̄ ∧ e^1̄ difference ──
print(f"\n{'='*80}")
print("KEY DIFFERENCE: e^0̄ ∧ e^2̄")
print(f"{'='*80}")

print("\nIngoing:")
w_in = wedge(e_in[0], e_in[2])
print(f"  e^0̄ ∧ e^2̄ = {pf(w_in)}")

print("\nOutgoing:")
w_out = wedge(e_out[0], e_out[2])
print(f"  e^0̄ ∧ e^2̄ = {pf(w_out, CO2_OUT)}")

print("\nIngoing:")
w_in_01 = wedge(e_in[0], e_in[1])
print(f"  e^0̄ ∧ e^1̄ = {pf(w_in_01)}")

print("\nOutgoing:")
w_out_01 = wedge(e_out[0], e_out[1])
print(f"  e^0̄ ∧ e^1̄ = {pf(w_out_01, CO2_OUT)}")

print("\n✓ Debug complete.")
