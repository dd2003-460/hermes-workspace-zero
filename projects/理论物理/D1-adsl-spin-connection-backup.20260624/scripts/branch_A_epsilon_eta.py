#!/usr/bin/env python3
"""
Branch A: ε convention + non-diagonal η deep verification
Goal: Verify whether ε_{abc}σ^b∧e^c ≠ ε^{abc}σ_b∧e_c when η is antidiagonal.
Check if the script's uniform use of ε^{abc} with metric-lowered forms is correct.

Reference: JHEP 09 (2023) 185
η_{ab} = antidiag(1,1,0;1,0,0;0,0,1) → η^{ab} same form, det=-1
ε_{012} = +1, ε^{012} = -1
"""

from sympy import symbols, Rational, expand, simplify

# ── Metric: antidiagonal η ──
# η_{01}=η_{10}=1, η_{22}=1, rest 0
eta_lower = [[0, 1, 0],
             [1, 0, 0],
             [0, 0, 1]]
# η^{ab}: inverse is same matrix for antidiag(1,1,1)
eta_upper = [[0, 1, 0],
             [1, 0, 0],
             [0, 0, 1]]

def eps_contravariant(a, b, c):
    """ε^{abc} with ε^{012} = -1"""
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return -((-1)**inv)

def eps_covariant(a, b, c):
    """ε_{abc} with ε_{012} = +1, computed via η lowering"""
    # ε_{abc} = η_{ad}η_{be}η_{cf}ε^{def}
    # For antidiagonal η, this should give -ε^{abc}
    total = 0
    for d in range(3):
        for e in range(3):
            for f in range(3):
                total += eta_lower[a][d] * eta_lower[b][e] * eta_lower[c][f] * eps_contravariant(d,e,f)
    return total

def eps_covariant_direct(a, b, c):
    """ε_{abc} directly: ε_{012} = +1"""
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return (-1)**inv

print("="*60)
print("  Branch A: ε_{abc} vs ε^{abc} verification")
print("="*60)

# Step 1: Verify ε_{abc} from η-lowering matches ε_{abc} direct
print("\n--- Step 1: ε_{abc} via η-lowering vs direct ---")
match = True
for a in range(3):
    for b in range(3):
        for c in range(3):
            via_eta = eps_covariant(a,b,c)
            direct = eps_covariant_direct(a,b,c)
            contra = eps_contravariant(a,b,c)
            ok = (via_eta == direct)
            if not ok: match = False
            sign_relation = "ε_cov = ε_contra" if direct == contra else "ε_cov = -ε_contra"
            print(f"  ε_{{{a}{b}{c}}} = {direct:2d}  (η-lowered: {via_eta:2d})  ε^{{{a}{b}{c}}} = {contra:2d}  | {sign_relation} {'✅' if ok else '❌'}")

print(f"\n  η-lowering match: {'✅ ALL MATCH' if match else '❌ MISMATCH'}")

# Step 2: Check if ε_{abc} = ε^{abc} for this metric
print("\n--- Step 2: ε_{abc} vs ε^{abc} ---")
same = True
for a in range(3):
    for b in range(3):
        for c in range(3):
            cov = eps_covariant_direct(a,b,c)
            con = eps_contravariant(a,b,c)
            if cov != con:
                same = False
                print(f"  ε_{{{a}{b}{c}}}={cov} ≠ ε^{{{a}{b}{c}}}={con}")
if same:
    print("  ✅ ε_{abc} = ε^{abc} for ALL (a,b,c)")
else:
    print("  ❌ ε_{abc} ≠ ε^{abc} — they differ by sign!")

# Step 3: What does the script actually compute?
print("\n--- Step 3: Script's eps_abc function ---")
def script_eps_abc(a, b, c):
    """What sympy_verify.py uses"""
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return -((-1)**inv)

for a in range(3):
    for b in range(3):
        for c in range(3):
            se = script_eps_abc(a,b,c)
            cov = eps_covariant_direct(a,b,c)
            con = eps_contravariant(a,b,c)
            if se != cov:
                print(f"  ⚠️ script({a}{b}{c})={se} ≠ ε_{{{a}{b}{c}}}={cov}  (ε^{{{a}{b}{c}}}={con})")

print("\n  Script uses ε^{abc} (with ε^{012}=-1)")
print("  If ε_{abc} ≠ ε^{abc}, then ALL EOMs using ε_{abc} are WRONG in the script!")

# Step 4: Detailed sign analysis for EOM2 component a=0
print("\n--- Step 4: EOM2 sign analysis for a=0 ---")
print("  EOM2: T^a + ε_{abc} σ^b ∧ e^c = 0")
print("  Script computes: T^a + ε^{abc} σ_b ∧ e_c = 0")
print()
for b in range(3):
    for c in range(3):
        if b == c: continue
        cov = eps_covariant_direct(0, b, c)
        con = eps_contravariant(0, b, c)
        print(f"  a=0, (b,c)=({b},{c}): ε_{{0{b}{c}}}={cov:+d}, ε^{{0{b}{c}}}={con:+d}, {'SAME' if cov==con else 'DIFFERENT!'}")

print("\n✓ Branch A analysis complete.")
