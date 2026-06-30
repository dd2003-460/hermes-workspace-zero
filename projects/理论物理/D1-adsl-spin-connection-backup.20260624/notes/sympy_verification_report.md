# SymPy Verification Report — AdSL BTZ Spin Connection

> Generated: 2026-04-01T01:43+08:00  
> Script: `scripts/sympy_verify.py`  
> Reference: JHEP 09 (2023) 185

## Summary

SymPy symbolic computation executed on ingoing/outgoing Eddington-Finkelstein frames.
**EOM 1 (geometric curvature) fully satisfied. EOM 2 & 3 have non-zero residuals.**

## Results

### EOM 1: R^a = 0 (Geometric Curvature)

| Frame | [0̄] | [1̄] | [2̄] | Verdict |
|-------|------|------|------|---------|
| Ingoing | ✅ 0 | ✅ 0 | ✅ 0 | **PASS** |
| Outgoing | ✅ 0 | ✅ 0 | ✅ 0 | **PASS** |

**Interpretation**: The spin connection ω is flat (R^a=0) in both frames. This confirms the connection defines a flat AdSL structure, consistent with the Chern-Simons formulation.

### EOM 2: T^a + ε_{abc}σ^b ∧ e^c = 0 (Modified Torsion)

| Frame | [0̄] | [1̄] | [2̄] | Verdict |
|-------|------|------|------|---------|
| Ingoing | ❌ {(0,1): -2r/ℓ²} | ✅ 0 | ❌ {(1,2): -2, (0,2): -b/2} | **FAIL** |
| Outgoing | ✅ 0 | ✅ 0 | ❌ {(0,2): -b/2} | **FAIL** |

**Key observations**:
- **Factor-of-2 issue**: Ingoing [0̄] has -2r/ℓ² instead of 0. The coefficient 2 suggests a convention mismatch in the T^a definition or the ε_{abc}σ∧e term.
- **b-dependence**: The (0,2) component = -b/2 appears in both frames. The paper treats b as a free gauge parameter of the spin connection. If the paper's claim is that these EOMs hold for *all* b, this residual is problematic. If b is fixed by additional conditions, this may be acceptable.
- **Outgoing partially cleaner**: Only b/2 residual, no factor-of-2 issue.

### EOM 3: F^a + (1/2ℓ²)ε_{abc}e^b ∧ e^c = 0 (σ-Curvature)

| Frame | [0̄] | [1̄] | [2̄] | Verdict |
|-------|------|------|------|---------|
| Ingoing | ❌ {(1,2): 2r/ℓ², (0,2): r(ℓ²(2M+b)-2r²)/(2ℓ⁴)} | ✅ 0 | ❌ {(0,1): 2/ℓ²} | **FAIL** |
| Outgoing | ❌ {(0,2): r(ℓ²(2M+b)-2r²)/(2ℓ⁴)} | ✅ 0 | ✅ 0 | **FAIL** |

**Key observations**:
- **Systematic 2/ℓ² factors**: Ingoing has 2r/ℓ² and 2/ℓ², suggesting the same factor-of-2 issue as EOM 2.
- **(0,2) component**: r(ℓ²(2M+b)-2r²)/(2ℓ⁴) appears in both frames. This involves both M and b, suggesting it's not a simple sign error.

## Diagnostic: Possible Sources of Discrepancy

### 1. ε convention mismatch
The script uses ε^{012} = -1 (from det(η) = -1 for antidiagonal metric). The paper may use a different sign convention for the lower-index ε_{abc} in the EOM.

### 2. F^a definition
The script defines F^a = D_ω σ^a + (1/2)ε^{abc} σ_b ∧ σ_c. If the paper's F^a = D_ω σ^a without the σ∧σ term, the residuals would change.

### 3. σ = -κ or σ = κ?
The script uses σ^a = -κ^a. If the sign is reversed, both EOM 2 and 3 would be affected.

### 4. T^a definition convention
The script defines T^a = de^a - ε^{abc} ω_b ∧ e_c. Some references use T^a = de^a + ε^{abc} ω_b ∧ e_c.

## Next Steps

1. **Verify against paper's explicit equations**: Re-read JHEP 09 (2023) 185 §2-§3 for the exact sign conventions and EOM definitions
2. **Try alternative sign conventions**: Systematically flip ε signs and σ sign
3. **Check if b is constrained**: The paper may impose additional conditions on b beyond gauge freedom
4. **Cross-reference with known AdSL results**: Compare with other papers on AdSL gravity

## Files

- Script: `projects/adsl-spin-connection/scripts/sympy_verify.py`
- This report: `projects/adsl-spin-connection/notes/sympy_verification_report.md`
- Analytical notes: `projects/adsl-spin-connection/notes/analytical_verification.md`
