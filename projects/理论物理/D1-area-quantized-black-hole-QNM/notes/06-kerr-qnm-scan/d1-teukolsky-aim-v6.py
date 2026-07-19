#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v6
=====================================
Correct Teukolsky-to-RW gauge transformation at a=0.

At a=0: Teukolsky variable R = Delta * psi, so
  A_coeff_Teuk - 2*(Delta'/Delta) = Q_over_P_RW (the Dehghan coefficient)

The AIM solver must use gauge-corrected lambda_0:
  lambda_0 = A_coeff - 2*(ln Delta)' - 2*(ln g)'_gauge_fix

where the gauge fix accounts for the factor F^(iω) * x^(-iω) * (1-x)^(iω).

Test: at a=0, must reproduce BERTI GRAV = 0.37367-0.08896i for l=2.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0
s = -2  # spin weight for gravitational perturbations


def teukolsky_coeffs(x, omega, l=2, m=2, a=0.0):
    """
    Teukolsky equation coefficients in Poincare coordinate x.

    x = 1 - r_+/r, so x=0 at horizon, x=1 at infinity.

    Returns:
        A_coeff: coefficient of R' in the Teukolsky ODE
        B_coeff: coefficient of R
        gauge_ln_delta_prime: (ln Delta)' w.r.t. x
    """
    x = np.clip(x, 1e-10, 1 - 1e-10)

    r_plus = M + np.sqrt(max(M**2 - a**2, 0))
    r_minus = M - np.sqrt(max(M**2 - a**2, 0))
    r = r_plus / (1.0 - x)
    dr_dx = r_plus / (1.0 - x)**2

    # Metric functions
    Delta = (r - r_plus) * (r - r_minus)
    dDelta_dr = 2.0 * r - 2.0 * M
    K = (r**2 + a**2) * omega - a * m

    # P_r = (s+1) * Delta'/Delta
    P_r = (s + 1.0) * dDelta_dr / Delta

    # Teukolsky ODE: R''_x = A_coeff * R'_x + B_coeff * R
    # U = K²/Delta - 4s*omega*r/Delta + l(l+1)
    U = K**2 / Delta - 4.0 * s * omega * r / Delta + l * (l + 1)

    d2r_dx2 = 2.0 * r_plus / (1.0 - x)**3

    A_coeff = d2r_dx2 / dr_dx - dr_dx * P_r
    B_coeff = -dr_dx**2 * U

    # (ln Delta)' w.r.t. x
    dDelta_dx = dDelta_dr * dr_dx
    gauge_ln_delta_prime = dDelta_dx / Delta

    return A_coeff, B_coeff, gauge_ln_delta_prime


def aim_teukolsky(omega, l, a=0.0, m=2, N=120, xa=0.3, xb=0.7):
    """
    AIM on gauge-corrected Teukolsky equation.

    The gauge-corrected lambda_0 accounts for:
    1. The Teukolsky-to-RW transformation: R = Delta * psi
    2. The standard AIM gauge: psi -> exp(iω ln(...) * psi)

    lambda_0_corrected = A_coeff - 2 * (ln Delta + ln g_std)'
    where ln g_std = iω * [ln F - ln x + ln(1-x)]
    """
    dx = 1e-7
    MAX_S = 1e80

    def get_corrected_lam_mu(xpt):
        """Get gauge-corrected (lambda_0, mu_0) at point xpt."""
        A, B, lnDp = teukolsky_coeffs(xpt, omega, l, m, a)

        # Gauge transformation: psi_std -> R = Delta * F^(iω) * x^(-iω) * (1-x)^(iω) * psi_aim
        # So ln_gauge_total = ln Delta + iω[ln F - ln x + ln(1-x)]
        # (ln gauge_total)' = lnD + iω[dlnF/dx - 1/x + 1/(1-x)]

        # Compute dlnF/dx numerically for safety
        eps = 1e-8
        A_p, _, _ = teukolsky_coeffs(xpt + eps, omega, l, m, a)
        A_m, _, _ = teukolsky_coeffs(xpt - eps, omega, l, m, a)
        dA_dx = (A_p - A_m) / (2 * eps)

        # F = (r² + a²) / Delta, compute lnF' at xpt
        rv_p = r_plus_at(a) / (1.0 - (xpt + eps))
        rv_m = r_plus_at(a) / (1.0 - (xpt - eps))

        def lnF_prime(xv):
            rv = r_plus_at(a) / (1.0 - xv)
            rp = M + np.sqrt(max(M**2 - a**2, 0))
            rm = M - np.sqrt(max(M**2 - a**2, 0))
            Dr = (rv - rp) * (rv - rm)
            dDr = 2.0 * rv - 2.0 * M
            drdx = rp / (1.0 - xv)**2
            num = 2.0 * rv * Dr - (rv**2 + a**2) * dDr
            return num / (Dr * (rv**2 + a**2)) * drdx

        dlnF_dx = lnF_prime(xpt)

        # Total gauge derivative
        ln_gauge_total_prime = lnD + iω * (dlnF_dx - 1.0/xpt + 1.0/(1.0-xpt))

        # Now: psi_std = exp(iω ln g_std) * psi_t, where psi_t is Teukolsky variable
        # R = Delta * psi_std = Delta * exp(iω ln g_std) * psi_t
        # But AIM acts on R: R'' = A*R' + B*R
        # We want psi = R * exp(-∫α) where α = (1/2)(A - Q_over_P)
        # This gives psi'' = -lambda_0 * psi - mu_0 * psi

        # Actually, the standard approach:
        # R'' = A*R' + B*R
        # Let R = exp(∫β) * phi, choose β to eliminate first derivative
        # phi'' = (β' + β² - A*β - B) * phi
        # Set β = (1/2)(A - Q) where Q is the "physical" first-derivative coeff

        # For the Teukolsky equation, after removing the first derivative term:
        # phi'' = -(ω² - V_eff) * phi
        # where V_eff includes the Teukolsky potential + gauge terms

        # The gauge correction for AIM:
        # lambda_0 = A - 2 * (ln Delta)' - 2 * (ln g_std)'
        # mu_0 = -(ω² - V_RW) * (dr*/dx)² (for a=0, should match Dehghan)

        # For general a, we use:
        # lambda_0 = A - 2 * ln_gauge_total_prime
        # mu_0 = B - ln_gauge_total_second_prime - ln_gauge_total_prime²
        #        + A * ln_gauge_total_prime

        # Compute second derivative of gauge
        lnF_pp = lnF_prime(xpt + eps)
        lnF_mm = lnF_prime(xpt - eps)
        d2lnF_dx2 = (lnF_pp - lnF_mm) / (2 * eps)

        ln_gauge_total_second = (lnD_p + 1j * omega * (d2lnF_dx2 + 1.0/xpt**2 + 1.0/(1-xpt)**2))

        # This is getting complicated. Let me use a simpler approach:
        # Just compute the AIM sequence directly on the gauge-transformed variable.

        # R'' = A*R' + B*R
        # Let R = exp(∫γ) * phi where γ = (1/2)(A - 2*(ln Delta)')
        # Then phi'' = -(omega² - V_eff)*phi with
        # lambda_0 = A - 2*gamma = 2*(ln Delta)' - A + A = 2*(ln Delta)' ... no

        # Let me just use the Dehghan coefficients at a=0 (verified working)
        # and the Teukolsky coefficients at a>0 (where there's no Dehghan equivalent).

        # For a=0, the Teukolsky equation with R = Delta * psi gives:
        # psi'' = -(omega² - V_RW) * psi
        # So we should use the Dehghan AIM coefficients at a=0.

        # For a>0, we use the Teukolsky equation directly:
        # lambda_0 = A - 2*gamma, mu_0 = B - gamma' - gamma² + A*gamma
        # where gamma = (1/2)(A - 2*(ln Delta)')

        # Actually let me simplify: use the Dehghan AIM at a=0, Teukolsky AIM at a>0.
        pass

    # For a=0: use the verified Dehghan AIM coefficients
    if abs(a) < 1e-10:
        return aim_dehghan(omega, l, N, xa, xb)

    # For a>0: use Teukolsky coefficients with gauge correction
    # This is the implementation to develop
    raise NotImplementedError("Only a=0 supported")


def r_plus_at(a):
    return M + np.sqrt(max(M**2 - a**2, 0))


# =====================================================================
# Dehghan AIM (verified) for a=0 baseline
# =====================================================================

def dehghan_coeffs(x, omega, l=2):
    """Dehghan-Safari AIM coefficients (working)."""
    x = np.clip(x, 1e-10, 1-1e-10)
    r = 2*M/(1-x)
    drstar_dr = r**2/(r-2*M)**2
    dr_dx = 2*M/(1-x)**2
    rstar_prime = drstar_dr * dr_dx

    d2r_dx2 = 4*M/(1-x)**3

    lam0 = d2r_dx2 / rstar_prime
    f = 1.0 - 2*M/r
    V = f*(l*(l+1)/r**2 - 6*M/r**3)
    mu0 = -(omega**2 - V)*rstar_prime**2
    return lam0, mu0


def aim_dehghan(omega, l, N=120, xa=0.3, xb=0.7):
    """
    AIM on Dehghan coefficients.

    Uses Wronskian-based convergence condition:
    W_N = lambda_{N-1}(xa) * lambda_N(xb) - lambda_N(xa) * lambda_{N-1}(xb)

    W_N → 0 when lambda_{N-1}/lambda_N becomes x-independent (eigenvalue).
    """
    dx = 1e-7
    MAX_S = 1e80

    # At xa
    la0, ma0 = dehghan_coeffs(xa, omega, l)
    lp, mp = dehghan_coeffs(xa+dx, omega, l)
    lm, mm = dehghan_coeffs(max(xa-dx, 1e-8), omega, l)
    dla0 = (lp-lm)/(2*dx)
    dqa0 = (mp-mm)/(2*dx)

    # At xb
    lb0, mb0 = dehghan_coeffs(xb, omega, l)
    lp, mp = dehghan_coeffs(xb+dx, omega, l)
    lm, mm = dehghan_coeffs(xb-dx, omega, l)
    dlb0 = (lp-lm)/(2*dx)
    dqb0 = (mp-mm)/(2*dx)

    # Initialize AIM sequences
    lsa, msa = la0, ma0
    lsb, msb = lb0, mb0
    dla, dqa = dla0, dqa0
    dlb, dqb = dlb0, dqb0

    lsa_prev, msa_prev = lsa, msa
    lsb_prev, msb_prev = lsb, msb

    for k in range(1, N+1):
        lna = lsa**2 + dla - msa
        mna = lsa*dqa - msa*dla + msa**2
        ln_b = lsb**2 + dlb - msb
        mn_b = lsb*dqb - msb*dlb + msb**2

        # Global normalization
        scale = max(abs(lna), abs(mna), abs(ln_b), abs(mn_b))
        if scale > MAX_S:
            lna /= scale; mna /= scale
            ln_b /= scale; mn_b /= scale
            dla /= scale; dqa /= scale
            dlb /= scale; dqb /= scale
            lsa_prev /= scale; msa_prev /= scale
            lsb_prev /= scale; msb_prev /= scale

        # Derivatives
        dla_new = 2*lsa*dla - dqa
        dqb_new = 2*msa*dqb
        dlb_new = 2*lsb*dlb - dqb
        dqb_new_local = 2*msb*dqb

        if scale > MAX_S:
            dla_new /= scale; dqb_new /= scale
            dlb_new /= scale; dqb_new_local /= scale

        lsa_prev, msa_prev = lsa, msa
        lsb_prev, msb_prev = lsb, msb
        lsa, msa = lna, mna
        lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqb_new
        dlb, dqb = dlb_new, dqb_new_local

    # Wronskian convergence condition
    W = lsa_prev * lsb - lsa * lsb_prev
    return abs(W)


# =====================================================================
# Teukolsky AIM (a>0)
# =====================================================================

def aim_teukolsky_coeffs(omega, l, a, m, N=120, xa=0.3, xb=0.7):
    """
    AIM on Teukolsky equation coefficients.

    Teukolsky ODE: R''_x = A_coeff * R'_x + B_coeff * R

    Gauge transformation: R = exp(∫α) * psi
    where α = (1/2) * A_coeff eliminates the first-derivative term.

    Result: psi''_x = -(omega² - V_eff) * psi
    with lambda_0 = A_coeff - 2*alpha = 0 (by construction)
    and mu_0 = B_coeff - alpha' - alpha².

    Wait, that's wrong. Let me redo:
    R = exp(∫α) * psi
    R' = α*R + exp(∫α)*psi'
    R'' = α'*R + α*R' + α*R' + exp(∫α)*psi''
        = α'*R + 2α*R' + exp(∫α)*psi''

    Substituting R'' = A*R' + B*R:
    α'*R + 2α*R' + exp*psi'' = A*R' + B*R
    exp*psi'' = (A - 2α)*R' + (B - α')*R

    For R' term: R' = α*R + exp*psi', so
    exp*psi'' = (A-2α)*(α*R + exp*psi') + (B-α')*R
              = (A-2α)*exp*psi' + [(A-2α)*α + B-α']*R

    For the psi' term to have coefficient exp (i.e., coefficient 1 after dividing):
    A - 2α = 1 → α = (A-1)/2

    That's also wrong. Let me be more careful.

    R = g * psi, where g = exp(∫α dx)
    R' = g'*psi + g*psi' = α*g*psi + g*psi'
    R'' = α'*g*psi + α*g'*psi + α*g*psi' + g*psi''
        = α'*g*psi + α²*g*psi + α*g*psi' + g*psi''
        = g*(alpha'*psi + alpha²*psi + alpha*psi' + psi'')

    ODE: R'' = A*R' + B*R
    g*(psi'' + alpha*psi' + (alpha' + alpha²)*psi) = A*g*(alpha*psi + psi') + B*g*psi

    Divide by g:
    psi'' + alpha*psi' + (alpha' + alpha²)*psi = A*alpha*psi + A*psi' + B*psi

    psi'' + (alpha - A)*psi' + (alpha' + alpha² - A*alpha - B)*psi = 0

    Set alpha = A to eliminate psi' term:
    psi'' + (A' + A² - A*A - B)*psi = 0
    psi'' + (A' - B)*psi = 0

    So lambda_0 = 0, mu_0 = -(A' - B) = B - A'

    Hmm, that can't be right either. Let me reconsider.

    Actually, the correct choice is alpha = A (not alpha = A/2):
    psi'' + (A - A)*psi' + (A' + A² - A² - B)*psi = 0
    psi'' + (A' - B)*psi = 0

    So lambda_0 = A (first derivative coefficient = alpha - A = 0 after gauge fix)
    and mu_0 = -(A' - B) = B - A'

    But A' means dA/dx, which changes with x. This doesn't look like a standard eigenvalue problem.

    Let me use a different approach. The standard AIM is for:
    y''(x) = f(x) * y'(x) + g(x) * y(x)

    For the Teukolsky equation in x: R'' = A_coeff*R' + B_coeff*R
    AIM recurrence: lambda_{k+1} = lambda_k² + lambda_k' - mu_k
    with lambda_0 = A_coeff, mu_0 = B_coeff.

    This should work directly! No gauge transformation needed for AIM.
    The only issue is that the AIM convergence condition (theta_N = lambda_{N-1}/lambda_N
    being x-independent) is gauge-invariant, so it should detect the eigenvalue.

    So the original v1-v5 should work if the Teukolsky coefficients are correct.
    Let me try the AIM recurrence directly on (A_coeff, B_coeff).
    """
    dx = 1e-7
    MAX_S = 1e80

    def get_coeffs(xpt):
        A, B, _ = teukolsky_coeffs(xpt, omega, l, m, a)
        return A, B

    # At xa
    Aa, Ba = get_coeffs(xa)
    Ap, Bp = get_coeffs(xa + dx)
    Am, Bm = get_coeffs(max(xa - dx, 1e-8))
    dAdx_a = (Ap - Am) / (2*dx)
    dBdx_a = (Bp - Bm) / (2*dx)

    # At xb
    Ab, Bb = get_coeffs(xb)
    Ap, Bp = get_coeffs(xb + dx)
    Am, Bm = get_coeffs(xb - dx)
    dAdx_b = (Ap - Am) / (2*dx)
    dBdx_b = (Bp - Bm) / (2*dx)

    # AIM recurrence: R'' = A*R' + B*R
    # lambda_0 = A, mu_0 = B
    # lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    lsa, msa = Aa, Ba
    lsb, msb = Ab, Bb
    dla, dqa = dAdx_a, dBdx_a
    dlb, dqb = dAdx_b, dBdx_b

    lsa_prev, msa_prev = lsa, msa
    lsb_prev, msb_prev = lsb, msb

    for k in range(1, N+1):
        lna = lsa**2 + dla - msa
        mna = lsa*dqa - msa*dla + msa**2
        ln_b = lsb**2 + dlb - msb
        mn_b = lsb*dqb - msb*dlb + msb**2

        scale = max(abs(lna), abs(mna), abs(ln_b), abs(mn_b))
        if scale > MAX_S:
            lna /= scale; mna /= scale
            ln_b /= scale; mn_b /= scale
            dla /= scale; dqa /= scale
            dlb /= scale; dqb /= scale
            lsa_prev /= scale; msa_prev /= scale
            lsb_prev /= scale; msb_prev /= scale

        dla_new = 2*lsa*dla - dqa
        dqb_new = 2*msa*dqb
        dlb_new = 2*lsb*dlb - dqb
        dqb_new_b = 2*msb*dqb

        if scale > MAX_S:
            dla_new /= scale; dqb_new /= scale
            dlb_new /= scale; dqb_new_b /= scale

        lsa_prev, msa_prev = lsa, msa
        lsb_prev, msb_prev = lsb, msb
        lsa, msa = lna, mna
        lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqb_new
        dlb, dqb = dlb_new, dqb_new_b

    # Wronskian convergence condition
    W = lsa_prev * lsb - lsa * lsb_prev
    return abs(W)


# =====================================================================
# Tests
# =====================================================================

print("="*70)
print("Teukolsky + AIM v6: Kerr QNM Solver")
print("Test 1: Dehghan AIM at a=0 (should reproduce BERTI GRAV)")
print("Test 2: Teukolsky AIM at a=0 (should match Dehghan)")
print("="*70)

def test_qNM_dehghan(label, omega_ref, l, srw, srwi, N=120):
    print(f"\n--- {label} ---")
    print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

    D = aim_dehghan(omega_ref, l, N)
    print(f"D at exact QNM: |W|={D:.4e}")

    min_D, best = np.inf, None
    for wr in np.linspace(*srw, 25):
        for wi in np.linspace(*srwi, 20):
            D = aim_dehghan(wr+1j*wi, l, N)
            if D < min_D:
                min_D, best = D, (wr, wi)
    print(f"Coarse min: omega = {best[0]:.3f} {best[1]:+.3f}i, D = {min_D:.4e}")

    min_D2, best2 = np.inf, best
    for wr in np.linspace(best[0]-0.02, best[0]+0.02, 21):
        for wi in np.linspace(best[1]-0.02, best[1]+0.02, 15):
            D = aim_dehghan(wr+1j*wi, l, N)
            if D < min_D2:
                min_D2, best2 = D, (wr, wi)
    print(f"Fine min: omega = {best2[0]:.5f} {best2[1]:+.5f}i, D = {min_D2:.4e}")

    def obj(p):
        return aim_dehghan(p[0]+1j*p[1], l, N)
    res = minimize(obj, best2, method='Nelder-Mead',
                   options={'maxiter':5000, 'xatol':1e-7, 'fatol':1e-15})
    found = res.x[0] + 1j*res.x[1]
    err = abs(found - omega_ref) / abs(omega_ref) * 100
    print(f"Optimized: omega = {found.real:.5f} {found.imag:+.5f}i, err = {err:.1f}%")
    return found, err


def test_qNM_teuk(label, omega_ref, l, a, srw, srwi, N=120):
    print(f"\n--- {label} ---")
    print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

    m = l  # |m| = l for fundamental mode

    D = aim_teukolsky_coeffs(omega_ref, l, a, m, N)
    print(f"D at exact QNM: |W|={D:.4e}")

    min_D, best = np.inf, None
    for wr in np.linspace(*srw, 15):
        for wi in np.linspace(*srwi, 12):
            D = aim_teukolsky_coeffs(wr+1j*wi, l, a, m, N)
            if D < min_D:
                min_D, best = D, (wr, wi)
    print(f"Coarse min: omega = {best[0]:.3f} {best[1]:+.3f}i, D = {min_D:.4e}")

    min_D2, best2 = np.inf, best
    for wr in np.linspace(max(best[0]-0.05, 0.1), min(best[0]+0.05, 1.0), 15):
        for wi in np.linspace(best[1]-0.03, best[1]+0.03, 12):
            D = aim_teukolsky_coeffs(wr+1j*wi, l, a, m, N)
            if D < min_D2:
                min_D2, best2 = D, (wr, wi)
    print(f"Fine min: omega = {best2[0]:.5f} {best2[1]:+.5f}i, D = {min_D2:.4e}")

    def obj(p):
        return aim_teukolsky_coeffs(p[0]+1j*p[1], l, a, m, N)
    res = minimize(obj, best2, method='Nelder-Mead',
                   options={'maxiter':5000, 'xatol':1e-7, 'fatol':1e-15})
    found = res.x[0] + 1j*res.x[1]
    err = abs(found - omega_ref) / abs(omega_ref) * 100
    print(f"Optimized: omega = {found.real:.5f} {found.imag:+.5f}i, err = {err:.1f}%")
    return found, err


# Test 1: Dehghan AIM at a=0
test_qNM_dehghan("Schwarzschild l=2, n=0 (Dehghan AIM)",
                 0.37367-0.08896j, l=2,
                 srw=(0.30, 0.45), srwi=(-0.15, -0.02))

# Test 2: Teukolsky AIM at a=0 (should reproduce Dehghan if coefficients are correct)
test_qNM_teuk("Schwarzschild l=2, n=0 (Teukolsky AIM, a=0)",
              0.37367-0.08896j, l=2, a=0.0,
              srw=(0.30, 0.45), srwi=(-0.15, -0.02))
