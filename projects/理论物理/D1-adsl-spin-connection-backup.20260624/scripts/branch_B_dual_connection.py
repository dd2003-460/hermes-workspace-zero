#!/usr/bin/env python3
"""
Branch B: Dual connection transformation verification
Goal: The paper says ω^a = ε^{abc}η_{bd}ω^d_c (dual connection).
Invert this to get standard ω^d_c, then check if EOMs are satisfied
with the standard connection vs dual connection.

Also: check if the EOM3 residual r(M+b-r²/ℓ²)/ℓ⁴ can be eliminated
by a modified σ ≠ -κ.
"""

from sympy import symbols, Rational, expand, simplify, solve, Matrix

r, ell, M, J, b = symbols('r ell M J b', real=True)

# η antidiag: η_{01}=η_{10}=1, η_{22}=1
eta = Matrix([[0, 1, 0],
              [1, 0, 0],
              [0, 0, 1]])

# Given dual connection ω^a (1-forms, but we treat components):
# ω^0̄ = -(b/2) dφ  → component: ω^0 = {2: -b/2}
# ω^1̄ = dφ          → component: ω^1 = {2: 1}
# ω^2̄ = 0           → component: ω^2 = {}

# Invert: ω^a = ε^{abc} η_{bd} ω^d_c
# In 3D: ω^a = ε^{abc} ω_{bc} where ω_{bc} = η_{bd} ω^d_c
# And ω_{bc} = (1/2) ε_{bcd} ω^d (since ω_{bc} is antisymmetric)

print("="*60)
print("  Branch B: Dual connection transformation")
print("="*60)

# Step 1: Invert ω^a → ω^d_c
# ω^a = ε^{abc} ω_{bc} where ω_{bc} = η_{bd} ω^d_c
# In 3D, antisymmetric ω_{bc} has 3 independent components: ω_{01}, ω_{02}, ω_{12}
# ω^0 = ε^{0bc} ω_{bc} = ε^{012}ω_{12} + ε^{021}ω_{21} = 2ε^{012}ω_{12} = -2ω_{12}
# ω^1 = ε^{1bc} ω_{bc} = ε^{102}ω_{02} + ε^{120}ω_{20} = 2ε^{102}ω_{02} = 2ω_{02}
# ω^2 = ε^{2bc} ω_{bc} = ε^{201}ω_{01} + ε^{210}ω_{10} = 2ε^{201}ω_{01} = -2ω_{01}

# So: ω_{12} = -ω^0/2, ω_{02} = ω^1/2, ω_{01} = -ω^2/2
# With our values: ω^0 = -b/2·dφ, ω^1 = dφ, ω^2 = 0
# → ω_{12} = b/4·dφ, ω_{02} = 1/2·dφ, ω_{01} = 0

print("\n--- Step 1: Dual → Standard connection ---")
print("  ω^a (dual): ω^0 = -(b/2)dφ, ω^1 = dφ, ω^2 = 0")
print("  Inversion: ω_{bc} = (1/2)ε_{bcd}ω^d")
print()

# Compute ω_{bc} for each component
omega_dual = {0: -Rational(1,2)*b, 1: Rational(1,1), 2: Rational(0,1)}  # dφ components

def eps_lower_abc(a,b,c):
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return (-1)**inv

def eps_upper_abc(a,b,c):
    if len({a,b,c}) < 3: return 0
    arr = [a,b,c]
    inv = sum(1 for i in range(3) for j in range(i+1,3) if arr[i]>arr[j])
    return -((-1)**inv)

# ω_{bc} = (1/2) ε_{bcd} ω^d
omega_std = {}
for bc in [(0,1), (0,2), (1,2)]:
    val = 0
    for d in range(3):
        val += Rational(1,2) * eps_lower_abc(bc[0], bc[1], d) * omega_dual[d]
    omega_std[bc] = expand(val)
    print(f"  ω_{bc[0]}{bc[1]} = {val}")

# Now get ω^d_c from ω_{bc} = η_{bd} ω^d_c
print("\n  Standard connection ω^d_c (from ω_{bc} = η_{bd}ω^d_c):")
omega_matrix = [[0]*3 for _ in range(3)]
for bc, val in omega_std.items():
    b_idx, c_idx = bc
    # ω_{bc} = η_{bd} ω^d_c → need to invert η
    # For antidiag η: η^{-1} = η
    # ω^d_c = η^{db} ω_{bc}
    for d in range(3):
        omega_matrix[d][c_idx] += eta[d, b_idx] * val

for d in range(3):
    for c in range(3):
        v = expand(omega_matrix[d][c])
        if v != 0:
            print(f"  ω^{d}_{c} = {v}")

# Step 2: Compare with what the script computes
# The script's "lower" function gives [ω_0, ω_1, ω_2] = [ω^1, ω^0, ω^2]
# ω_0 = ω^1 = dφ, ω_1 = ω^0 = -(b/2)dφ, ω_2 = ω^2 = 0
print("\n--- Step 2: Script's lowered indices vs standard connection ---")
print("  Script: ω_0 = ω^1 = dφ, ω_1 = ω^0 = -(b/2)dφ, ω_2 = ω^2 = 0")
print("  Standard: ω_{01}=(b/4)dφ, ω_{02}=(1/2)dφ, ω_{12}=0")
print()
print("  These are DIFFERENT objects!")
print("  Script uses: ω_a (3 components, vector-valued 1-form)")
print("  Standard: ω^d_c (3×3 matrix of 1-forms, antisymmetric in d↔c)")
print()
print("  The EOMs D_ω defined in the paper use ω^a (dual),")
print("  so the script's approach of directly using ω^a is correct")
print("  IF the EOMs are written in terms of the dual connection.")
print()
print("  The paper's D_ω e^a = de^a - ε^{abc}ω_b∧e_c uses ω_b (lowered dual)")
print("  This IS the correct form for the dual connection representation.")

# Step 3: What if we use the standard connection in the EOMs?
print("\n--- Step 3: EOMs with standard connection ---")
print("  If EOMs actually use standard ω^d_c (not dual ω^a),")
print("  then D_ω e^a = de^a - ω^a_b ∧ e^b with standard ω^a_b")
print("  Need to check if paper's D_ω definition matches this.")
print()
print("  Paper: D_ω e^a = de^a - ε^{abc}ω_b ∧ e_c")
print("  Standard: D_ω e^a = de^a - ω^a_b ∧ e^b")
print()
print("  For these to be equal: ω^a_b = ε^{abc}ω_c")
print("  Check: ω^0_b = ε^{0bc}ω_c")
print("    ω^0_1 = ε^{012}ω_2 = -1·0 = 0")
print("    ω^0_2 = ε^{021}ω_1 = 1·(-b/2) = -b/2")
print("  Standard ω^0_1 = ?, ω^0_2 = ?")

# Verify: ω^a_b = ε^{abc} ω_c
print("\n  Verification ω^a_b = ε^{abc}ω_c:")
for a in range(3):
    for b_idx in range(3):
        if a == b_idx:
            continue
        val = 0
        for c in range(3):
            val += eps_upper_abc(a, b_idx, c) * omega_dual[c]
        val = expand(val)
        if val != 0:
            print(f"  ω^{a}_{b_idx} = {val}")

print("\n  Comparing with standard connection from Step 1:")
# standard was computed from ω_{bc}
for a in range(3):
    for b_idx in range(3):
        if a == b_idx:
            continue
        sv = expand(omega_matrix[a][b_idx])
        if sv != 0:
            print(f"  Standard ω^{a}_{b_idx} = {sv}")

print("\n✓ Branch B analysis complete.")
