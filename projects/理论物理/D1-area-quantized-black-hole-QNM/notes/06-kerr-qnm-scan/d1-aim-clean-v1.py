#!/usr/bin/env python3
"""
Clean AIM solver with per-step normalization.

The AIM recurrence lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k grows as
|lambda_k| ~ |lambda_0|^(2^k). For N=100 this is exp(2^100) - impossible to store.

Solution: normalize at each step. Define:
  lambda_k = s_k * L_k,  |L_k| ~ O(1)
where s_k is a cumulative scale factor.

Substituting:
  s_{k+1} * L_{k+1} = s_k^2 * L_k^2 + (s_k*L_k)' - s_k*M_k

If we choose s_{k+1} = s_k^2 (so s_k = s_0^(2^k)):
  s_k^2 * L_{k+1} = s_k^2 * L_k^2 + s_k*L_k' + s_k'*L_k - s_k*M_k
  L_{k+1} = L_k^2 + L_k'/s_k + s_k'/(s_k^2)*L_k - M_k/s_k

For large k, the correction terms L_k'/s_k ~ 0 since s_k ~ 2^(2^k).
So L_{k+1} ~ L_k^2, meaning |L_k| ~ |L_0|^(2^k)/s_k.

But this doesn't help because L_k still grows exponentially.

Better approach: choose s_{k+1} = |lambda_{k+1}| so L_{k+1} = lambda_{k+1}/|lambda_{k+1}|.
Then |L_k| = 1 always. The recurrence:
  lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
  L_{k+1} = lambda_{k+1} / |lambda_{k+1}|  (phase only)

But we need lambda_k' for the recurrence, and the phase doesn't give the derivative.

Alternative (used in Dehghan's actual implementation):
  At each step, compute the UN-normalized recurrence. When |lambda| > 1e80:
  divide BOTH lambda and mu (and their derivatives) by |lambda|/1e80.
  This keeps values in float range.

The convergence criterion theta_N = lambda_{N-1}/lambda_N is RATIO-based,
so dividing both lambda_{N-1} and lambda_N by the same cumulative scale
at each x-point gives the correct ratio.

BUG in previous versions: when scaling lsa_prev/lsb_prev, both were divided
by the SAME scale factor computed from BOTH points. But the lambda sequences
at points a and b diverge, and the "global" scale distorts their relationship.

FIX: Track theta components independently at each x-point using the
per-step normalized recurrence:

  lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k

Choose scale_k = max(|lambda_k|, |mu_k|, |lambda_k'|, |mu_k'|).
If scale_k > MAX_S:
  lambda_k /= scale_k, mu_k /= scale_k, lambda_k' /= scale_k, mu_k' /= scale_k

After normalization, theta_N = lambda_{N-1}/lambda_N.
Since we normalized BOTH lsa and lsb by the SAME factor at EACH step,
the RATIO at each x-point is preserved within that point.

But theta across points is NOT preserved because the two points see different
max values and different scaling.

HOWEVER: the convergence condition is theta_a = theta_b. Under independent
scaling:
  theta_a_scaled = theta_a_orig * (s_N^a / s_{N-1}^a)
  theta_b_scaled = theta_b_orig * (s_N^b / s_{N-1}^b)

theta_a = theta_b does NOT imply theta_a_scaled = theta_b_scaled!

Solution: track the scale ratio (s_N/s_{N-1}) at each point separately.
  theta_a_corr = theta_a_scaled * (s_{N-1}^a / s_N^a)
              = lambda_{N-1}^a / lambda_N^a  (UN-normalized)

But we DON'T know the un-normalized values!

Real solution from Dehghan 2011 (Sec. III.B):
  Use theta_N(x) ~ A/(x-B) for large N, fit A and B from 3 x-values.
  The eigenvalue is the real part of B.

This avoids the cross-point comparison entirely.

Simpler: use the Wronskian-like criterion:
  D = |lambda_{N-1}(xa)*lambda_N(xb) - lambda_N(xa)*lambda_{N-1}(xb)|

With independent normalization:
  D_scaled = D_orig * (1/(s_{N-1}^a * s_N^b))

D_scaled = 0 iff D_orig = 0. So the Wronskian IS zero-crossing invariant
under scaling, as long as we use the ORIGINAL (unscaled) values.

But the values overflow! So we need to track them in log-space.

Let me use a different approach: track (ln|lambda|, phase) at each point.

For the recurrence:
  lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k

In log-space, lambda_k = exp(l_k + i*p_k):
  lambda_k^2 = exp(2*l_k + i*2*p_k)
  lambda_k' ~ 2*lambda_k * lambda_k'/lambda_k
            ~ 2*lambda_k * ln_lambda_k'  (derivative of ln|lambda| + i*phase)

Actually, let me just track the ratio theta_k = lambda_{k-1}/lambda_k directly.
From the recurrence:
  lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
  lambda_k = lambda_{k-1}^2 + lambda_{k-1}' - mu_{k-1}

Dividing:
  lambda_{k+1}/lambda_k = lambda_k + (lambda_k' - mu_k)/lambda_k
                        = lambda_k + (lambda_k' - mu_k)*theta_k

Hmm, this isn't a clean recurrence for theta.

OK, let me try the simplest approach that actually works:
1. Run AIM at two x-points simultaneously
2. At each step, scale BOTH points by the SAME factor = max of both points
3. This preserves the Wronskian (since W/s^2 = 0 iff W = 0)
4. Use per-step scaling to avoid overflow

The bug in v5 was that cumulative scaling of lsa_prev corrupted the values.
The fix: don't scale lsa_prev. Instead, save lsa/lsb before updating, and
only scale when needed (with the SAME scale for both points).

Let me carefully implement this:
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

def get_lm(x, omega, l):
    """Compute lambda_0(x), mu_0(x), and their derivatives."""
    x = np.clip(x, 1e-10, 1 - 1e-10)
    r = 2 * M / (1 - x)

    # dr*/dx and d^2r*/dx^2
    dr_dx = 2 * M / (1 - x) ** 2
    drstar_dr = r ** 2 / (r - 2 * M) ** 2
    rstar_prime = drstar_dr * dr_dx

    # d^2r*/dx^2 = d/drstar_dr/dx * dr_dx + drstar_dr * d^2r/dx^2
    # But actually it's d/dr(drstar_dr) * dr/dx + drstar_dr * d2r/dx2
    # Wait, d2r* = d(r*')/dx = d/dr(dr*/dr) * dr/dx (chain rule on first factor)
    #                  + dr*/dr * d^2r/dx^2
    # No! r*' = dr*/dr * dr/dx.
    # d2r* = d/dx[dr*/dr * dr/dx]
    #      = d/dr[dr*/dr] * dr/dx * dr/dx + dr*/dr * d^2r/dx^2
    #      = d2rstar_dr2 * (dr/dx)^2 + drstar_dr * d2r_dx2

    # d/dr(dr*/dr) = d/dr(1/f) where f = (r-2M)/r
    # = d/dr(r^2/(r-2M)^2)
    df_dr = -4 * M * r / (r - 2 * M) ** 3
    # But this is dF/dr for F = r^2/(r-2M)^2... no
    # dr*/dr = r^2/(r-2M)^2
    # d/dr(r^2/(r-2M)^2) = [2r*(r-2M)^2 - r^2*2*(r-2M)]/(r-2M)^4
    #                     = 2r(r-2M)[(r-2M) - r]/(r-2M)^4
    #                     = 2r(-2M)/(r-2M)^3
    #                     = -4Mr/(r-2M)^3
    d2rstar_dr2 = -4 * M * r / (r - 2 * M) ** 3

    d2r_dx2 = 2 * dr_dx * (-1) * (-2 * M) / (1 - x) ** 3  # wrong
    # r = 2M/(1-x), dr/dx = 2M/(1-x)^2, d2r/dx2 = 4M/(1-x)^3
    d2r_dx2 = 4 * M / (1 - x) ** 3

    rstar_double_prime = d2rstar_dr2 * dr_dx ** 2 + drstar_dr * d2r_dx2

    # ODE coefficients
    lam0 = rstar_double_prime / (rstar_prime ** 2)
    V = (1 - 2 * M / r) * (l * (l + 1) / r ** 2 - 6 * M / r ** 3)
    mu0 = -(omega ** 2 - V) / (rstar_prime ** 2) * rstar_prime ** 2
    mu0 = -(omega ** 2 - V) * (1 / rstar_prime ** 2) / (1 / rstar_prime ** 2)
    # Wait: the ODE is:
    # d2y/dx2 + (r*''/r*'^2)*y' + (w^2-V)/r*'^2 * y = 0
    # In form y'' = lambda*y' + mu*y:
    # lambda_0 = -(r*''/r*'^2)  [sign flip because moving to RHS]
    # NO: y'' + a*y' + b*y = 0 -> y'' = -a*y' - b*y
    # So lambda_0 = -r*''/r*'^2 and mu_0 = -(w^2-V)/r*'^2

    lam0 = -rstar_double_prime / (rstar_prime ** 2)
    mu0 = -(omega ** 2 - V) / (rstar_prime ** 2)

    return lam0, mu0


def get_lm_derivs(x, omega, l):
    """Numerical derivatives of lambda_0, mu_0."""
    dx = 1e-6
    lp, mp = get_lm(min(x + dx, 0.9999), omega, l)
    lm, mm = get_lm(max(x - dx, 1e-8), omega, l)
    return (lp - lm) / (2 * dx), (mp - mm) / (2 * dx)


def aim_theta(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM with independent normalization at each x-point.

    Track normalized lambda: L_k = lambda_k / scale_k.
    The theta ratio at each point: theta = L_{N-1} / L_N.
    This equals lambda_{N-1}/lambda_N since scale cancels within one point.

    Cross-point comparison: D = |theta_a - theta_b|.
    But under independent scaling:
      theta_a * (scale_N^a/scale_{N-1}^a) = theta_a_orig
      theta_b * (scale_N^b/scale_{N-1}^b) = theta_b_orig

    We need theta_a_orig = theta_b_orig, which means:
      theta_a/scale_ratio_a = theta_b/scale_ratio_b

    We track scale_ratio = scale_N/scale_{N-1} at each point.

    Convergence function:
      D = |theta_a*scale_ratio_b - theta_b*scale_ratio_a|
    """
    # Initialize at point a
    la0, ma0 = get_lm(xa, omega, l)
    dla0, dqa0 = get_lm_derivs(xa, omega, l)

    # Initialize at point b
    lb0, mb0 = get_lm(xb, omega, l)
    dlb0, dqb0 = get_lm_derivs(xb, omega, l)

    MAX_S = 1e80

    lsa, msa, dla, dqa = la0, ma0, dla0, dqa0
    lsb, msb, dlb, dqb = lb0, mb0, dlb0, dqb0

    # Track scale ratios at each point
    ratio_a = 1.0  # scale_N^a / scale_{N-1}^a (cumulative from last unscaled step)
    ratio_b = 1.0

    # Save prev for theta computation (within same point)
    la_prev, lb_prev = lsa, lsb
    # Track cumulative scaling separately for cross-point correction
    cum_scale_a = 1.0  # actual lambda / normalized L (product of scales for this point)
    cum_scale_b = 1.0

    for k in range(1, N + 1):
        # Recurrence at both points
        lna = lsa ** 2 + dla - msa
        ln_b = lsb ** 2 + dlb - msb
        mna = lsa * dqa - msa * dla + msa ** 2
        mn_b = lsb * dqb - msb * dlb + msb ** 2

        # Scale factor = max across both points
        scale = max(abs(lna), abs(ln_b), abs(mna), abs(mn_b))

        if scale > MAX_S:
            # Scale prev lambdas at each point
            la_prev /= scale
            lb_prev /= scale

            # Scale derivatives at each point
            dla_old = dla; dqa_old = dqa
            dlb_old = dlb; dqb_old = dqb

            # Compute new derivatives BEFORE scaling lambda/mu
            dla_new = 2 * lsa * dla - dqa
            dlb_new = 2 * lsb * dlb - dqb

            # Scale everything
            lna /= scale; ln_b /= scale
            mna /= scale; mn_b /= scale
            dla_new /= scale; dqb_new /= scale
            dla /= scale; dqa /= scale
            dlb /= scale; dqb /= scale

            # Update
            lsa, msa = lna, mna
            lsb, msb = ln_b, mn_b
            dla, dqa = dla_new, dqa / scale
            dlb, dqb = dlb_new, dqb / scale
            cum_scale_a *= scale
            cum_scale_b *= scale
            continue

        # Compute new derivatives
        dla_new = 2 * lsa * dla - dqa
        dlb_new = 2 * lsb * dlb - dqb
        dqa_new = 2 * msa * dqa
        dqb_new = 2 * msb * dqb

        la_prev = lsa
        lb_prev = lsb

        lsa, msa = lna, mna
        lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqa_new
        dlb, dqb = dlb_new, dqb_new

    # theta at each point
    theta_a = la_prev / lsa
    theta_b = lb_prev / lsb

    # Cross-point difference (with cumulative scale correction)
    # Original theta_a = theta_a_normalized * (cum_scale_a / cum_scale_a) = theta_a_normalized
    # Original theta_b = theta_b_normalized * (cum_scale_b / cum_scale_b) = theta_b_normalized
    # Wait, the normalization at each step divides ALL variables at BOTH points
    # by the SAME scale. So cum_scale_a = cum_scale_b! The global scale IS shared.

    # So the issue is simpler: under GLOBAL scaling:
    # theta_a = la_prev_scaled / lsa_scaled = (la_prev/s) / (lsa/s) = la_prev/lsa
    # Same for b. So theta_a and theta_b are CORRECT under global scaling.

    # Then why is D always 0? Let me check by printing values.

    D = abs(theta_a - theta_b)

    return D, theta_a, theta_b


def aim_single_scale(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM tracking the ODE coefficients at two x-points with global per-step scaling.

    Key insight: when scale > MAX_S, ALL variables (both points) are divided by the
    same factor. So lambda_a/lambda_b ratios within each step are preserved.
    And theta_a = lambda_{N-1}(a)/lambda_N(a) is also preserved.

    The D should NOT be identically zero unless the AIM implementation is wrong.

    Let me add diagnostics to understand why D=0.
    """
    dx = 1e-6

    # Get coefficients and derivatives
    la0, ma0 = get_lm(xa, omega, l)
    lb0, mb0 = get_lm(xb, omega, l)
    dla0, dqa0 = get_lm_derivs(xa, omega, l)
    dlb0, dqb0 = get_lm_derivs(xb, omega, l)

    lsa, msa, dla, dqa = la0, ma0, dla0, dqa0
    lsb, msb, dlb, dqb = lb0, mb0, dlb0, dqb0
    la_prev, lb_prev = lsa, lsb

    MAX_S = 1e80
    total_scale = 1.0  # track total cumulative scaling

    for k in range(1, N + 1):
        lna = lsa ** 2 + dla - msa
        ln_b = lsb ** 2 + dlb - msb
        mna = lsa * dqa - msa * dla + msa ** 2
        mn_b = lsb * dqb - msb * dlb + msb ** 2

        scale = max(abs(lna), abs(ln_b), abs(mna), abs(mn_b))

        if scale > MAX_S:
            total_scale *= scale
            la_prev /= scale
            lb_prev /= scale

            # Derivatives BEFORE update
            dla_new = 2 * lsa * dla - dqa
            dlb_new = 2 * lsb * dlb - dqb

            lna /= scale; ln_b /= scale; mna /= scale; mn_b /= scale
            dla /= scale; dqa /= scale; dlb /= scale; dqb /= scale
            dla_new /= scale; dlb_new /= scale

            lsa, msa = lna, mna; lsb, msb = ln_b, mn_b
            dla, dqa = dla_new, dqa  # dqa already scaled above
            dlb, dqb = dlb_new, dqb  # dqb already scaled above
        else:
            dla_new = 2 * lsa * dla - dqa
            dlb_new = 2 * lsb * dlb - dqb
            dqa_new = 2 * msa * dqa
            dqb_new = 2 * msb * dqb

            la_prev = lsa; lb_prev = lsb
            lsa, msa = lna, mna; lsb, msb = ln_b, mn_b
            dla, dqa = dla_new, dqa_new; dlb, dqb = dlb_new, dqb_new

    # Check: do the scaled lambda values give a meaningful theta?
    theta_a = la_prev / lsa
    theta_b = lb_prev / lsb

    # Debug: check magnitudes
    return abs(theta_a - theta_b), theta_a, theta_b, abs(lsa), abs(lsb), total_scale


# ---- Diagnostic run ----
print("=" * 70)
print("Clean AIM v1 - Diagnostic Run")
print("=" * 70)

omega_test = 0.37367 - 0.08896j
l = 2

print(f"\nODE coefficients at omega={omega_test:.4f}:")
xa, xb = 0.3, 0.7
for label, x in [("xa", xa), ("xb", xb)]:
    lam, mu = get_lm(x, omega_test, l)
    dlam, dmu = get_lm_derivs(x, omega_test, l)
    print(f"  {label}={x}: lam0={lam:.4e}, mu0={mu:.4e}, dlam0={dlam:.4e}, dmu0={dmu:.4e}")

print(f"\nStep-by-step AIM (first 5 steps, no scaling):")
for label, x in [("xa", xa), ("xb", xb)]:
    la0, ma0 = get_lm(x, omega_test, l)
    dla0, dqa0 = get_lm_derivs(x, omega_test, l)

    lsa, msa = la0, ma0
    dla, dqa = dla0, dqa0

    for k in range(1, 6):
        lna = lsa ** 2 + dla - msa
        mna = lsa * dqa - msa * dla + msa ** 2

        dla_new = 2 * lsa * dla - dqa
        dqa_new = 2 * msa * dqa

        print(f"  {label} k={k}: |lambda|={abs(lna):.4e}, |mu|={abs(mna):.4e}, "
              f"|dlambda|={abs(dla_new):.4e}")

        lsa, msa = lna, mna
        dla, dqa = dla_new, dqa_new

# Run with different N to see convergence behavior
print(f"\nAIM convergence (N vs theta at exact QNM):")
for N in [5, 10, 15, 20, 30]:
    D, ta, tb, la_abs, lb_abs, sc = aim_single_scale(omega_test, l, N=N)
    print(f"  N={N:2d}: D={D:.6e}, |theta_a|={abs(ta):.6e}, |theta_b|={abs(tb):.6e}, "
          f"|lambda_a|={la_abs:.6e}, |lambda_b|={lb_abs:.6e}, scale={sc:.6e}")
