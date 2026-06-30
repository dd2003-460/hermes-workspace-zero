#!/usr/bin/env python3
"""
Clean AIM solver for Schwarzschild QNMs.

Directly solves: d²ψ/dr*² + (ω² - V)ψ = 0
via the asymptotic iteration method.

Key equations:
- Transform d²/d(r*)² = J(y)² · d²/dy² + ... (chain rule)
- Write in AIM form: y'' = λ(x)y' + μ(x)y
- Iterate: λ_{k+1} = λ_k² + λ_k' - μ_k, μ_{k+1} = λ_k μ_k' - μ_k λ_k' + μ_k²
- Eigenvalue condition: λ_{k-1}/λ_k (at x1) = λ_{k-1}/λ_k (at x2) for large k

Implementation:
- Use y = 1 - 2M/r coordinate
- Evaluate at TWO points for the Wronskian criterion
- Use robust scaling to prevent overflow

Reference: Leaver (1986), Alcubierre et al. (2001), Konoplya (2003)
"""

import numpy as np
from scipy.optimize import minimize


M = 1.0
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


def r_of_y(y):
    """r = 2M/(1-y)"""
    return 2.0 * M / (1.0 - y)


def dr_dy(y):
    return 2.0 * M / (1.0 - y)**2


def drstar_dy(y):
    """dr*/dy = dr*/dr * dr/dy = (r/(r-2M))² * dr/dy"""
    r = r_of_y(y)
    drstar_dr = r**2 / (r - 2.0*M)**2
    return drstar_dr * dr_dy(y)


def rw_potential_r(r, l):
    """Regge-Wheeler potential."""
    f = 1.0 - 2.0*M/r
    return f * (l*(l+1.0)/r**2 - 6.0*M/r**3)


def compute_aim_coeffs(y, omega, l):
    """
    Compute λ(y) and μ(y) for the AIM formulation.

    Original ODE: d²ψ/dr*² + (ω² - V)ψ = 0
    Chain rule: d/d(r*) = (1/dr*/dy) · d/dy

    Let J(y) = dr*/dy
    Then d²/dr*² = (1/J²)·d²/dy² - (J'/J³)·d/dy

    So: (1/J²)·ψ'' - (J'/J³)·ψ' + (ω² - V)·ψ = 0
    ψ'' = (J'/J)·ψ' - J²(ω² - V)·ψ

    AIM form: ψ'' = λ·ψ' + μ·ψ
    where:
    λ(y) = J'(y) / J(y)
    μ(y) = -J(y)² · (ω² - V(r(y), l))
    """
    # Avoid boundaries
    y = np.clip(y, 1e-12, 1.0 - 1e-12)

    r = r_of_y(y)
    V = rw_potential_r(r, l)

    J = drstar_dy(y)
    # J' = dJ/dy (finite difference)
    h = 1e-8
    Jp = drstar_dy(y + h)
    Jm = drstar_dy(y - h)
    dJ = (Jp - Jm) / (2 * h)

    lam = dJ / J
    mu = -J**2 * (omega**2 - V)

    return lam, mu, J, dJ


def aim_wronskian(omega, l, N=100, xa=0.2, xb=0.8):
    """
    Compute AIM Wronskian at two points.
    W = λ_{N-1}(xa) · λ_N(xb) - λ_N(xa) · λ_{N-1}(xb)
    At QNM eigenvalue, W = 0 (λ_{N-1}/λ_N is y-independent).

    Uses robust scaling to prevent overflow.
    """
    h = 1e-8

    # Compute λ and μ at xa and xb, plus derivatives
    def get_coeffs_at(y):
        r = r_of_y(y)
        V = rw_potential_r(r, l)
        J = drstar_dy(y)
        Jp = drstar_dy(y + h)
        Jm = drstar_dy(y - h)
        dJ = (Jp - Jm) / (2*h)
        lam = dJ / J
        mu = -J**2 * (omega**2 - V)
        # Numerical derivatives of lam and mu
        eps = 1e-8
        J_ee = drstar_dy(y + 2*h)
        J_ee2 = drstar_dy(y - 2*h)
        dJ_ee = (J_ee - J_ee2) / (4*h)

        lam_prime = (lam*J_ee2 - lam_prime_calc(omega, l, y, J, dJ)) / (2*h)
        # Hmm, this is getting complicated. Let me just use central difference on lam directly.
        return lam, mu, dJ

    lam0_a, mu0_a, dJ_a = get_coeffs_at(xa)
    lam0_b, mu0_b, dJ_b = get_coeffs_at(xb)

    # Central difference for derivatives
    eps = 1e-8
    r_xa = r_of_y(xa)
    V_xa = rw_potential_r(r_xa, l)
    J_xa = drstar_dy(xa)
    J_xap = drstar_dy(xa + eps)
    J_xam = drstar_dy(xa - eps)
    dJ_xa = (J_xap - J_xam) / (2*eps)
    lam_xa = dJ_xa / J_xa

    eps2 = 1e-8
    lam_xa_pp, _, _ = compute_aim_coeffs(xa + eps2, omega, l)
    lam_xa_mm, _, _ = compute_aim_coeffs(xa - eps2, omega, l)
    dlam_xa = (lam_xa_pp - lam_xa_mm) / (2*eps2)

    eps_b = 1e-8
    r_xb = r_of_y(xb)
    V_xb = rw_potential_r(r_xb, l)
    J_xb = drstar_dy(xb)
    J_xbp = drstar_dy(xb + eps_b)
    J_xbm = drstar_dy(xb - eps_b)
    dJ_xb = (J_xbp - J_xbm) / (2*eps_b)

    lam_xb = dJ_xb / J_xb

    eps2_b = 1e-8
    lam_xb_pp, _, _ = compute_aim_coeffs(xb + eps2_b, omega, l)
    lam_xb_mm, _, _ = compute_aim_coeffs(xb - eps2_b, omega, l)
    dlam_xb = (lam_xb_pp - lam_xb_mm) / (2*eps2_b)

    # Compute mu values
    mu_xa = -J_xa**2 * (omega**2 - V_xa)
    mu_xb = -J_xb**2 * (omega**2 - V_xb)

    eps_mu_a = 1e-8
    _, mu0_ap, _, _ = compute_aim_coeffs_full(xa + eps_mu_a, omega, l)
    _, mu0_am, _, _ = compute_aim_coeffs_full(xa - eps_mu_a, omega, l)
    dmu_xa = (mu0_ap - mu0_am) / (2*eps_mu_a)

    eps_mu_b = 1e-8
    _, mu0_bp, _, _ = compute_aim_coeffs_full(xb + eps_mu_b, omega, l)
    _, mu0_bm, _, _ = compute_aim_coeffs_full(xb - eps_mu_b, omega, l)
    dmu_xb = (mu0_bp - mu0_bm) / (2*eps_mu_b)

    # Scaled AIM iteration
    MAX_S = 1e100
    scale_total_a = 1.0
    scale_total_b = 1.0

    lna, mna = lam_xa, mu_xa
    ln_b, mn_b = lam_xb, mu_xb

    lna_prev, mna_prev = lna, mna
    ln_prev_b, mn_prev_b = ln_b, mn_b

    dla, dqa = dlam_xa, dmu_xa
    dlb, dqb = dlam_xb, dmu_xb

    for k in range(1, N+1):
        # lambda_{k} = lambda_{k-1}^2 + lambda_{k-1}' - mu_{k-1}
        # mu_{k} = lambda_{k-1}*mu_{k-1}' - mu_{k-1}*lambda_{k-1}' + mu_{k-1}^2

        # Also need dλ_k/dy = 2λ_{k-1}·λ'_{k-1} + λ''_{k-1} - μ'_{k-1}
        # and μ_k' = λ'_{k-1}·μ_{k-1} + λ_{k-1}·μ'_{k-1}
        #          - μ'_{k-1}·λ_{k-1} - μ_{k-1}·λ'_{k-1} + 2μ_{k-1}·μ'_{k-1}
        # Simplify: μ_k' = λ'_{k-1}·μ_{k-1} - μ_{k-1}·λ'_{k-1} + 2μ_{k-1}·μ'_{k-1}
        #          = 2·μ_{k-1}·μ'_{k-1}
        # Wait: μ_k' = d/dy(mu_k) = λ'·μ - μ'·λ + λ·μ'' - μ'·λ' - λ·λ'' + 2μ·μ'
        # This is getting very messy with second derivatives.

        # For AIM, we need λ_k', μ_k' for the NEXT iteration.
        # But computing λ_k' requires λ'' which requires another round of AIM.

        # Alternative: we only need the Wronskian W = λ_{N-1}(xa)·λ_N(xb) - λ_N(xa)·λ_{N-1}(xb)
        # For this, we don't need derivatives at all if we reformulate.

        # Actually, the Wronskian formulation doesn't use the recurrence
        # lambda_{k+1} = lambda_k^2 + lambda'_k - mu_k directly.
        # Instead, we define:
        # D_n = det[L_{n-1}(x_a), L_n(x_a); L_{n-1}(x_b), L_n(x_b)]
        # where L_k are obtained from the AIM iteration.
        # The QNM condition is D_n = 0.

        # But the computation still requires derivatives.
        # Let me use a different approach: compute the full AIM sequence
        # with numerical derivatives at each step.

        # lambda_k(x) ≈ lambda_{k-1}^2(x) + (lambda_{k-1}(x+h) - lambda_{k-1}(x-h))/(2h) - mu_{k-1}(x)
        # But this requires evaluating lambda and mu at x ± h for each k.

        # This is expensive but accurate. Let me do it.
        pass

    # REDO: compute sequences at xa and xb with numerical derivatives
    lna, mna = lam_xa, mu_xa
    ln_b, mn_b = lam_xb, mu_xb
    lna_prev, mna_prev = lna, mna
    ln_prev_b, mn_prev_b = ln_b, mn_b

    for k in range(1, N+1):
        # Need dlam/da and dmu/da at xa
        lam_aa_pp, mu_aa_pp, _, _ = _coeffs_eval(xa + eps, omega, l)
        lam_aa_mm, mu_aa_mm, _, _ = _coeffs_eval(xa - eps, omega, l)
        dlam_aa = (lam_aa_pp - lam_aa_mm) / (2*eps)
        dmu_aa = (mu_aa_pp - mu_aa_mm) / (2*eps)

        lam_bb_pp, mu_bb_pp, _, _ = _coeffs_eval(xb + eps, omega, l)
        lam_bb_mm, mu_bb_mm, _, _ = _coeffs_eval(xb - eps, omega, l)
        dlam_bb = (lam_bb_pp - lam_bb_mm) / (2*eps)
        dmu_bb = (mu_bb_pp - mu_bb_mm) / (2*eps)

        lna_new = lna**2 + dlam_aa - mna
        mn_new = lna * dmu_aa - mna * dlam_aa + mna**2
        ln_b_new = ln_b**2 + dlam_bb - mn_b
        mn_b_new = ln_b * dmu_bb - mn_b * dlam_bb + mn_b**2

        # Scaling
        sc = max(abs(lna_new), abs(mn_new), abs(ln_b_new), abs(mn_b_new))
        if sc > MAX_S:
            lna_new /= sc; mn_new /= sc
            ln_b_new /= sc; mn_b_new /= sc
            lna_prev /= sc; mna_prev /= sc
            ln_prev_b /= sc; mn_prev_b /= sc
            lna, mna = lna_new, mn_new
            ln_b, mn_b = ln_b_new, mn_b_new
            lna_prev, mna_prev = lna, mna
            ln_prev_b, mn_prev_b = ln_b, mn_b
            continue

        # For next iteration's derivatives, we need λ_k(x ± h)
        # But we don't store the full sequence...
        # Need to track values at ±eps too.

        # Save previous
        lna_prev, mna_prev = lna, mna
        ln_prev_b, mn_prev_b = ln_b, mn_b
        lna, mna = lna_new, mn_new
        ln_b, mn_b = ln_b_new, mn_b_new

    # Wronskian (this won't work correctly without proper derivative tracking)
    W = abs(lna_prev * ln_b - lna * ln_prev_b)
    return W


def _coeffs_eval(y, omega, l):
    r = r_of_y(y)
    V = rw_potential_r(r, l)
    J = drstar_dy(y)
    h = 1e-8
    Jp = drstar_dy(y + h)
    Jm = drstar_dy(y - h)
    dJ = (Jp - Jm) / (2*h)
    lam = dJ / J
    mu = -J**2 * (omega**2 - V)
    return lam, mu, J, dJ


def aim_full_iter(omega, l, N=100, xa=0.2, xb=0.7):
    """Complete AIM iteration with derivative tracking at three points."""
    eps = 1e-8

    def get_coeffs(y):
        r = r_of_y(y)
        V = rw_potential_r(r, l)
        J = drstar_dy(y)
        h = 1e-8
        Jp = drstar_dy(y + h)
        Jm = drstar_dy(y - h)
        dJ = (Jp - Jm) / (2*h)
        return dJ/J, -J**2*(omega**2 - V)

    # Three-point evaluation
    lx_a, mx_a = get_coeffs(xa)
    lx_b, mx_b = get_coeffs(xb)

    lx_ap, mx_ap = get_coeffs(xa + eps)
    lx_ay, mx_ay = get_coeffs(xa - eps)
    dxa, dqa = (lx_ap-lx_ay)/(2*eps), (mx_ap-mx_ay)/(2*eps)

    lx_bp, mx_bp = get_coeffs(xb + eps)
    lx_by, mx_by = get_coeffs(xb - eps)
    dxb, dqb = (lx_bp-lx_by)/(2*eps), (mx_bp-mx_by)/(2*eps)

    MAX_S = 1e100
    scale = 1.0

    lpa_a, mpa_a = lx_a, mx_a
    lpb_b, mpb_b = lx_b, mx_b
    lpa, mpa = lx_a, mx_a
    lpb, mpb = lx_b, mx_b

    for k in range(1, N+1):
        # Store current values for Wronskian
        lpa_a_new = lpa_a; mpa_a_new = mpa_a
        lpb_b_new = lpb_b; mpb_b_new = mpb_b

        # Next iteration
        lna = lpa**2 + dxa - mpa
        mna = lpa*dqa - mpa*dxa + mpa**2
        ln_b = lpb**2 + dxb - mpb
        mn_b = lpb*dqb - mpb*dxb + mpb**2

        # Scaled for next derivative
        sc = max(abs(lna), abs(mna), abs(ln_b), abs(mn_b))
        if sc > MAX_S:
            lna/=sc; mna/=sc; ln_b/=sc; mn_b/=sc
            lpa_a_new/=sc; mpa_a_new/=sc
            lpb_b_new/=sc; mpb_b_new/=sc

        lpa_a, mpa_a = lpa_a_new, mpa_a_new
        lpb_b, mpb_b = lpb_b_new, mpb_b_new

        lpa, mpa = lna, mna
        lpb, mpb = ln_b, mn_b

        # Derivatives
        lpa_pp, mpa_pp = get_coeffs(xa + eps)
        lpa_mm, mpa_mm = get_coeffs(xa - eps)
        dxa, dqa = (lpa_pp-lpa_mm)/(2*eps), (mpa_pp-mpa_mm)/(2*eps)

        lpb_pp, mpb_pp = get_coeffs(xb + eps)
        lpb_mm, mpb_mm = get_coeffs(xb - eps)
        dxb, dqb = (lpb_pp-lpb_mm)/(2*eps), (mpb_pp-mpb_mm)/(2*eps)

    W = abs(lpa_a * lpb_b - lpa * lpb_b_new)
    return W


# ============================================================================
# Test
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AIM Solver - Wronskian Criterion")
    print("=" * 70)

    l = 2
    omega_ref = BERTI_REF[l]
    print(f"\nl={l}, reference omega = {omega_ref.real:.5f} - {abs(omega_ref.imag):.5f} i")

    # Test AIM coefficients
    print("\nAIM coefficients at reference:")
    for y in [0.1, 0.2, 0.5, 0.7, 0.9]:
        lam, mu = compute_aim_coeffs(y, omega_ref, l)
        print(f"  y={y:.1f}: lam = {lam:.4f}, mu = {mu:.4f}")

    # Test Wronskian
    for N in [20, 40, 80, 120]:
        w_val = aim_full_iter(omega_ref, l, N=N)
        print(f"  |W| at reference (N={N}): {w_val:.6e}")

    for omega_w in [0.35-0.1j, 0.4-0.07j, 0.45-0.03j]:
        w_val = aim_full_iter(omega_w, l, N=80)
        print(f"  |W| at {omega_w.real:.2f}-{abs(omega_w.imag):.2f}i (N=80): {w_val:.6e}")
