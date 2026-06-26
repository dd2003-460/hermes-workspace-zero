#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v5
=====================================
Correct independent normalization at each x-point.

The AIM convergence condition is theta_N = lambda_{N-1}/lambda_N becomes
x-independent at the eigenvalue.

Key insight: We can normalize lambda_k independently at each x-point
(lambda_k -> lambda_k/s_k), and the condition theta_N(xa) == theta_N(xb)
translates to a scaling-independent condition.

Deriving:
  theta_scaled(x) = theta_orig(x) * (s_N(x)/s_{N-1}(x)) * (lambda_{N-2}/lambda_{N-2}_scaled)
                  = theta_orig(x) * (s_N * lambda_{N-2} / (s_{N-1} * lambda_{N-2}_scaled))
                  = theta_orig(x) * ratio_orig/scaled * s_N/s_{N-1}

For theta_orig to be x-independent:
  theta_scaled(xa)/theta_scaled(xb) = s(xa)_{ratio}/s(xb)_{ratio}

So D_N = |theta_scaled(xa)/theta_scaled(xb) - s_ratio(xa)/s_ratio(xb)| = 0

Simpler formulation:
  W_N = lambda_{N-1}(xa) * lambda_N(xb) - lambda_N(xa) * lambda_{N-1}(xb)
  (Wronskian). This is zero when theta_N is x-independent.
  Under independent scaling:
  W_N_scaled = lambda_{N-1}_s(xa)*lambda_N_s(xb) - lambda_N_s(xa)*lambda_{N-1}_s(xb)
            = W_orig * (s_{N-1}(xa)*s_N(xb))^-1  [if same scaling applied]

  Wait, this depends on WHICH scaling was used at each point. Since we scale
  independently, W_N_scaled IS zero iff W_N is zero.

  W_N_scaled = ls_{N-1}(xa) * ls_N(xb) - ls_N(xa) * ls_{N-1}(xb)
  where ls_k(x) = lambda_k(x)/s_k(x).

  W_orig = lambda_{N-1}(xa)*lambda_N(xb) - lambda_N(xa)*lambda_{N-1}(xb)
         = ls_{N-1}(xa)*s_{N-1}(xa) * ls_N(xb)*s_N(xb)
           - ls_N(xa)*s_N(xa) * ls_{N-1}(xb)*s_{N-1}(xb)
         = s_{N-1}(xa)*s_N(xb) * ls_{N-1}(xa)*ls_N(xb)
           - s_N(xa)*s_{N-1}(xb) * ls_N(xa)*ls_{N-1}(xb)

  W_N_scaled = ls_{N-1}(xa)*ls_N(xb) - ls_N(xa)*ls_{N-1}(xb)

  W_orig = 0 iff ls_{N-1}(xa)*ls_N(xb)*s_{N-1}(xa)*s_N(xb)
            = ls_N(xa)*ls_{N-1}(xb)*s_N(xa)*s_{N-1}(xb)
  iff ls_{N-1}(xa)/ls_N(xa) * s_{N-1}(xa)/s_N(xa)^(-1) * ...

  This doesn't simplify to W_N_scaled = 0 in general with independent scaling!

Alternative: Use GLOBAL scale (same s_k for both points).
  W_N_scaled = lambda_{N-1}(xa)/s * lambda_N(xb)/s - lambda_N(xa)/s * lambda_{N-1}(xb)/s
            = W_orig / s^2
  W_N_scaled = 0 iff W_orig = 0. Correct!

So the solution is to use a global scale factor.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

def get_lm(x, omega, l):
    """lambda_0(x), mu_0(x)."""
    x = np.clip(x, 1e-10, 1-1e-10)
    r = 2*M/(1-x)
    drstar_dr = r**2/(r-2*M)**2
    dr_dx = 2*M/(1-x)**2
    drstar_dx = drstar_dr * dr_dx

    f_r = r**2/(r-2*M)**2
    g_x = 2*M/(1-x)**2
    df_dx = -4*M*r/(r-2*M)**3 * g_x
    dg_dx = 4*M/(1-x)**3
    d2r = df_dx*g_x + f_r*dg_dx

    lam0 = d2r / drstar_dx
    V = (1-2*M/r)*(l*(l+1)/r**2 - 6*M/r**3)
    mu0 = -(omega**2 - V)*drstar_dx**2
    return lam0, mu0

def aim_D_N(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM with global normalization. Returns Wronskian D_N.

    W_N = ls_{N-1}(xa)*ls_N(xb) - ls_N(xa)*ls_{N-1}(xb)
    = 0 at eigenvalue (when lambda_{N-1}/lambda_N is x-independent).
    """
    dx = 1e-6

    # Initial values at xa
    la0, ma0 = get_lm(xa, omega, l)
    lp, mp = get_lm(xa+dx, omega, l)
    lm, mm = get_lm(max(xa-dx, 1e-8), omega, l)
    dla0 = (lp-lm)/(2*dx)
    dqa0 = (mp-mm)/(2*dx)

    # Initial values at xb
    lb0, mb0 = get_lm(xb, omega, l)
    lp, mp = get_lm(xb+dx, omega, l)
    lm, mm = get_lm(xb-dx, omega, l)
    dlb0 = (lp-lm)/(2*dx)
    dqb0 = (mp-mm)/(2*dx)

    # Scaled variables (start unscaled, scale factor = 1)
    lsa, msa = la0, ma0    # at xa
    lsb, msb = lb0, mb0    # at xb
    dla, dqa = dla0, dqa0  # derivatives at xa
    dlb, dqb = dlb0, dqb0  # derivatives at xb

    MAX_S = 1e80

    # Previous scaled values
    lsa_prev, msa_prev = lsa, msa
    lsb_prev, msb_prev = lsb, msb

    for k in range(1, N+1):
        # lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
        # mu_{k+1} = lambda_k*mu_k' - mu_k*lambda_k' + mu_k^2

        lna = lsa**2 + dla - msa
        mna = lsa*dqa - msa*dla + msa**2

        ln_b = lsb**2 + dlb - msb
        mn_b = lsb*dqb - msb*dlb + msb**2

        # Global scale = max magnitude across both points and both sequences
        scale = max(abs(lna), abs(mna), abs(ln_b), abs(mn_b))
        if scale > MAX_S:
            lna /= scale; mna /= scale
            ln_b /= scale; mn_b /= scale
            dla /= scale; dqa /= scale
            dlb /= scale; dqb /= scale
            lsa_prev /= scale; msa_prev /= scale
            lsb_prev /= scale; msb_prev /= scale

        # Derivatives of new values
        # d(lambda_new) ~ 2*lam*dlam - dmu
        dla_new = 2*lsa*dla - dqa
        dqa_new = 2*msa*dqa  # approximate

        dlb_new = 2*lsb*dlb - dqb
        dqb_new = 2*msb*dqb

        # Scale derivatives if we scaled
        if scale > MAX_S:
            dla_new /= scale; dqa_new /= scale
            dlb_new /= scale; dqb_new /= scale

        # Save and update
        lsa_prev, msa_prev = lsa, msa
        lsb_prev, msb_prev = lsb, msb
        lsa, msa = lna, mna
        lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqa_new
        dlb, dqb = dlb_new, dqb_new

    # Wronskian: W = lambda_{N-1}(xa)*lambda_N(xb) - lambda_N(xa)*lambda_{N-1}(xb)
    W = lsa_prev * lsb - lsa * lsb_prev

    return abs(W)


# ---- Tests ----

print("="*70)
print("Teukolsky + AIM: Kerr QNM Solver v5 (global norm + Wronskian)")
print("="*70)

def test_qNM(label, omega_ref, l, srw, srwi, N=80):
    print(f"\n--- {label} ---")
    print(f"Expected: omega = {omega_ref.real:.5f} {omega_ref.imag:+.5f}i")

    D = aim_D_N(omega_ref, l, N)
    print(f"D at exact QNM: |W|={D:.4e}")

    min_D, best = np.inf, None
    for wr in np.linspace(*srw, 25):
        for wi in np.linspace(*srwi, 20):
            D = aim_D_N(wr+1j*wi, l, N)
            if D < min_D:
                min_D, best = D, (wr, wi)
    print(f"Coarse min: omega = {best[0]:.3f} {best[1]:+.3f}i, D = {min_D:.4e}")

    min_D2, best2 = np.inf, best
    for wr in np.linspace(best[0]-0.02, best[0]+0.02, 21):
        for wi in np.linspace(best[1]-0.02, best[1]+0.02, 15):
            D = aim_D_N(wr+1j*wi, l, N)
            if D < min_D2:
                min_D2, best2 = D, (wr, wi)
    print(f"Fine min: omega = {best2[0]:.5f} {best2[1]:+.5f}i, D = {min_D2:.4e}")

    def obj(p):
        return aim_D_N(p[0]+1j*p[1], l, N)
    res = minimize(obj, best2, method='Nelder-Mead',
                   options={'maxiter':5000, 'xatol':1e-6, 'fatol':1e-15})
    found = res.x[0] + 1j*res.x[1]
    err = abs(found - omega_ref) / abs(omega_ref) * 100
    print(f"Optimized: omega = {found.real:.5f} {found.imag:+.5f}i, err = {err:.1f}%")
    return found, err

test_qNM("Schwarzschild l=2, n=0", 0.37367-0.08896j, l=2,
         srw=(0.30, 0.45), srwi=(-0.15, -0.02))
test_qNM("Schwarzschild l=3, n=0", 0.59108-0.05902j, l=3,
         srw=(0.45, 0.75), srwi=(-0.12, -0.01))
