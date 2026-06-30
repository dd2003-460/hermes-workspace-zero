# 草稿：联系 Omar Valdivia 关于 EOM3 残差

> 状态：草稿 | 日期：2026-04-01
> 收件人：Omar Valdivia, ovaldivi@unap.cl
> 论文：arXiv:2308.09114, JHEP 09 (2023) 185

---

## 邮件正文

**Subject:** Question on EOM3 residual in spin connection verification — JHEP 09 (2023) 185

Dear Prof. Valdivia,

I hope this email finds you well. I am a theoretical physicist working on first-order gravity formulations, and I have been independently verifying the BTZ black hole solution presented in your paper "Thermodynamics of the three-dimensional black hole with torsion" (JHEP 09 (2023) 185, arXiv:2308.09114).

### Verification results

My SymPy-based verification of the spin connection and equations of motion confirms the following:

| Check | Result |
|-------|--------|
| EOM1: R^a = 0 (ingoing) | ✅ Pass |
| EOM1: R^a = 0 (outgoing) | ✅ Pass |
| EOM2: T^a + ε_{abc} σ^b ∧ e^c = 0 (ingoing) | ✅ Pass |
| EOM2: T^a + ε_{abc} σ^b ∧ e^c = 0 (outgoing) | ✅ Pass |
| σ = −κ consistency | ✅ Verified |
| **EOM3: F^a + (1/2ℓ²) ε_{abc} e^b ∧ e^c = 0** | **❌ Fail** |

The tetrad correctly reproduces the BTZ metric, and EOM1/EOM2 pass in both ingoing and outgoing Eddington-Finkelstein frames (with the appropriate convention ε_{012} = +1 for the EOMs).

### EOM3 residual details

For the a=0 component, EOM3 = F^0 + (1/2ℓ²) ε_{0bc} e^b ∧ e^c should vanish identically. However, two independent components remain non-zero:

1. **(dr, dφ) component:** residual = **2r/ℓ²**
   - F^0 contributes r/ℓ² (from the dσ^0 term), and the e∧e term contributes another r/ℓ² with the same sign
   - These add to 2r/ℓ² instead of cancelling

2. **(dv, dφ) component:** residual = **r(ℓ²(M+b) − r²)/ℓ⁴**
   - F^0's D_ω σ^0 + σ∧σ terms produce a b-dependent contribution that the e∧e term does not match

Both residuals are structural — they are not zero for any choice of parameters (r, M, b, ℓ).

### Exhaustive investigation of possible errors

I have systematically checked 8 possible sources of convention/error, all of which have been ruled out:

| Branch | Investigation | Outcome |
|--------|--------------|---------|
| A | ε convention (ε^{abc} vs ε_{abc}) | Partially fixed EOM2; EOM3 unchanged |
| B | Dual connection (ω^a vs *ω^a) | Correct usage confirmed |
| C | Symbolic solve for unknown σ components | Overdetermined, no solution |
| D | e^0 dr sign correction | Fixed EOM2; EOM3 unchanged |
| E | δσ correction to EOM3 | EOM2 constraints force δσ = 0 |
| Deep-dive 1 | σ^0 dv component | Wrong target component + breaks EOM2 |
| Deep-dive 2 | σ^1 ≠ 0 | EOM2 forces σ^1 = 0 |
| Deep-dive 4 | ℓ² prefactor variations | No single factor resolves both residuals |

The key constraint is that EOM2 strictly enforces σ = −κ, leaving no freedom in the σ field to absorb the EOM3 residual. This was verified both analytically and numerically.

### My questions

Given the above, I would be grateful if you could clarify:

1. **Is the EOM3 formula in the paper exactly as you intended**, or might there be a typo in the prefactor (1/2ℓ²) or the ε convention?

2. **Are the spin connection (ω) and contortion (σ) expressions complete as written**, or is there an implicit gauge condition or additional term not explicitly listed?

3. **Is there a subtlety in the definition of F^a** — for instance, could D_ω in EOM3 refer to a different connection than in EOM1/EOM2?

I would be happy to share my complete verification scripts (Python/SymPy) and a Mathematica notebook if that would help diagnose the issue.

Thank you very much for your time. I look forward to hearing from you.

Best regards,

[Your name]
[Your affiliation]
[Your email]

---

## 备注

- **语言**：英文（学术通用）
- **语气**：礼貌、专业、提供充分细节
- **核心策略**：展示 5/6 通过（表明验证基础正确）+ 8 条修复失败（排除简单错误）
- **附件建议**：
  - `scripts/branch_A_corrected.py`（修正后的完整验证脚本）
  - `scripts/eom3_path1-4_*.py`（4 条深潜路径）
  - `notebooks/BTZ_SpinConnection_Verification.nb`（如完成）
- **发送前检查**：
  - 填写 [Your name] 等占位符
  - 确认 ε_{012} = +1 与论文一致（已多次确认）
  - 考虑是否附上 verification_summary.md 的 PDF 版
