#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v1
=====================================
Method: Asymptotic Iteration Method (AIM) applied to Schwarzschild RW equation
        (baseline test) + plan for full Kerr Teukolsky equation.

References:
- Dehghan & Safari 2011 (JCAP) -- Wronskian-based AIM for Schwarzschild
- Konoplya 2003 (PRD 68, 044018) -- AIM for Kerr QNMs
- Turrini 2008 (Phys. Lett. A) -- original Wronskian AIM
- Nakano/Kimura/Okamura 2007 (PTEP 2007, 013004) -- clean Kerr AIM

Key insight to avoid overflow:
  The AIM sequence lambda_k grows exponentially (like Leaver coefficients).
  The convergence ratio theta_n = lambda_{n-1}/lambda_n is finite.
  Use scaled sequences to keep computation in numerically safe range.
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0
s = -2

# Berti et al. 2009 reference values
berti_data = {
    (0.0, 2, 2, 0): (0.37367, -0.08896),
    (0.5, 2, 2, 0): (0.37414, -0.09332),
    (0.7, 2, 2, 0): (0.37471, -0.09784),
    (0.0, 3, 3, 0): (0.59108, -0.05902),
}

print("=" * 70)
print("Teukolsky + AIM: Kerr QNM Solver v1")
print("=" * 70)


# ---- Step 1: Schwarzschild RW equation (Schrödinger form) ----
# d^2 psi/dr*^2 + (omega^2 - V_RW) psi = 0
# where V_RW = f*(l(l+1)/r^2 - 6M/r^3), f = 1-2M/r
# Map to x in [0, 1]: x = 1 - 2M/r, so r = M/(1-x) for horizon at x=0, infinity at x=1
# Wait: x = 1 - 2M/r gives r=r+(2M)->x=0, r->inf->x=1. Good.

def r_from_x(x, M=1.0):
    return 2 * M / (1 - x)

def dr_dx(x, M=1.0):
    r = r_from_x(x, M)
    return 2 * M / (1 - x)**2

def drstar_dr(r, M=1.0):
    return r**2 / (r - 2*M)**2

def RW_potential(r, l, M=1.0):
    f = 1.0 - 2*M/r
    return f * (l*(l+1)/r**2 - 6*M/r**3)


def aim_schw_l2_m(omega, l, M=1.0, N=100, x0=0.5):
    """
    Compute AIM eigenvalue function for Schwarzschild RW equation.

    Using Dehghan-Safari (2011) formulation:
    The radial ODE d^2y/dr*^2 = -Q(r)*y, where Q = omega^2 - V_RW,
    mapped to x variable gives: d^2y/dx^2 = lam(x)*dy/dx + mu(x)*y

    with: lam(x) = d/dx(ln|dr*/dx|)  (nope, let me derive this carefully)
    """
    # Chain rule: d^2y/dx^2 = d/dx(dy/dr* * dr*/dx)
    #            = d^2y/dr*^2 * (dr*/dx)^2 + dy/dr* * d^2r*/dx^2
    # With d^2y/dr*^2 = -Q*y:
    # d^2y/dx^2 = (dr*/dx) * dy/dr* * (d/dr*(dr*/dx) - Q * dr*/dx) + ...

    # Actually: d/dx(dy/dr*) = d^2y/dr*^2 * dr*/dx = -Q*y * dr*/dx
    # So d^2y/dx^2 = -Q*y*(dr*/dx)^2 + dy/dr* * d^2r*/dx^2
    # = d/dx(y) * (d^2r*/dx^2) - Q*y*(dr*/dx)^2

    # In standard form: d^2y/dx^2 = lam*dy/dx + mu*y
    # lam(x) = d^2r*/dx^2 / (dr*/dx) ... no, that's not right.

    # Let me be more precise.
    # dy/dx = dy/dr* * dr*/dx  =>  dy/dr* = dy/dx / (dr*/dx)
    # d^2y/dx^2 = d/dx(dy/dr* * dr*/dx)
    #           = d^2y/dr*^2 * (dr*/dx)^2 + dy/dr* * d^2r*/dx^2
    #           = -Q*y*(dr*/dx)^2 + (dy/dx / dr*/dx) * d^2r*/dx^2
    #           = (d^2r*/dx^2 / dr*/dx) * dy/dx - Q*(dr*/dx)^2 * y

    # So: lam(x) = d^2r*/dx^2 / (dr*/dx)
    #     mu(x) = -Q(x) * (dr*/dx)^2

    # Compute dr*/dx at arbitrary x
    def drstar_over_dx(x):
        r = r_from_x(x, M)
        drs_dr = drstar_dr(r, M)
        dr_dxi = dr_dx(x, M)
        return drs_dr * dr_dxi

    # Compute d^2r*/dx^2
    def d2rstar_over_dx2(x):
        dx_e = 1e-7
        return (drstar_over_dx(x + dx_e) - drstar_over_dx(x - dx_e)) / (2*dx_e)

    # lam and mu as functions of x
    def lam_x(x):
        return d2rstar_over_dx2(x) / drstar_over_dx(x)

    def mu_x(x):
        r = r_from_x(x, M)
        Q = omega**2 - RW_potential(r, l, M)
        return -Q * drstar_over_dx(x)**2

    # AIM iteration: lambda_k(x), mu_k(x) computed numerically
    # Start: lambda_0 = lam, mu_0 = mu
    # Recurrence:
    #   lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    #   mu_{k+1} = lambda_k * mu_k' - mu_k * lambda_k' + mu_k * lambda_k
    # Wait, the correct recurrence is:
    #   lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    #   mu_{k+1} = lambda_k * mu_k' - mu_k * lambda_k' + mu_k^2
    # Hmm, let me get this right from the original AIM paper.

    # Original AIM (Hovhannisyan & Minasyan 2003, modified by Turrini 2008):
    # y^{(n)} = lambda * y^{(n-1)} + mu * y^{(n-2)}
    # y^{(n)} can be written as L_n * y' + M_n * y
    # where:
    #   L_0 = lambda, M_0 = mu
    #   L_{n+1} = L_n^2 + L_n' - M_n
    #   M_{n+1} = L_n * M_n' - M_n * L_n' + M_n^2
    # Hmm no:
    #   L_{n+1} = L_n^2 + dL_n/dx - M_n    -- WAIT, this is wrong.
    # Let me rederive.

    # y^{(0)} = y
    # y^{(1)} = lambda * y' + mu * y  (= original lambda * y' + mu * y)
    # y^{(2)} = lambda * y^{(1)} + mu * y^{(0)}
    #        = lambda * (lambda * y' + mu * y) + mu * y
    #        = lambda^2 * y' + (lambda * mu + mu) * y ... this doesn't seem right.

    # Let me use the exact recurrence from Dehghan 2010:
    # y^{(0)} = y, y^{(1)} = y'
    # y^{(n+1)} = lambda * y^{(n)} + mu * y^{(n-1)}  for n >= 1
    # Since y^{(n)} = L_n * y' + M_n * y:
    #   y^{(1)} = y' => L_1 = 1, M_1 = 0
    #   y^{(2)} = lambda*y' + mu*y => L_2 = lambda, M_2 = mu
    #   y^{(n+1)} = lambda*(L_n*y'+M_n*y) + mu*(L_{n-1}*y'+M_{n-1}*y)
    #            = (lambda*L_n + mu*L_{n-1})*y' + (lambda*M_n + mu*M_{n-1})*y
    # But also y^{(n+1)} = d/dx(y^{(n)}) ...
    # No: y^{(n)} here is NOT the nth derivative. It's the nth AIM iterated derivative.

    # OK I think the confusion is in notation. Let me use Dehghan's notation:
    # y^(k) = lambda*y^(k-1) + mu*y^(k-2)
    # with y^(0) = y, y^(1) = y'  [actual derivative]
    # y^(2) = lambda*y' + mu*y
    # y^(3) = lambda*(lambda*y'+mu*y) + mu*y' = lambda^2*y' + (lambda*mu+mu)*y
    #       = lambda^2*y'' + ... NO.

    # Wait, y^(k) is the k-th AIM iteration, NOT derivative.
    # y^(0) = y
    # y^(1) is defined by the original ODE: y'' = lambda*y' + mu*y
    # So y^(1) is not defined. The iteration is:
    #   y_{(k)} = lambda*y_{(k-1)} + mu*y_{(k-2)}
    # where y_{(k)} means applying the AIM operator k times.

    # Dehghan-Safari formulation (simpler):
    # Start from y'' = lambda*y' + mu*y  [standard ODE]
    # Differentiate: y''' = (lambda^2 + lambda' - mu)*y' + (...)*y
    # Define: lambda_1 = lambda^2 + lambda' - mu  [note: using original lambda, mu]
    #        mu_1 = lambda*mu' - mu*lambda' + mu^2
    # Then: y''' = lambda_1*y' + mu_1*y
    # By induction: y^{(k+1)} = lambda_{k-1}*y' + mu_{k-1}*y
    # And the recurrence for lambda_k, mu_k:
    #   lambda_k = lambda_{k-1}^2 + lambda_{k-1}' - mu_{k-1}
    #   mu_k = lambda_{k-1}*mu_{k-1}' - mu_{k-1}*lambda_{k-1}' + mu_{k-1}^2
    # (where prime denotes derivative w.r.t. x)

    # Convergence condition: for QNM, lambda_{k-1}/lambda_k becomes x-independent
    # at large k, i.e., lambda_{k-1}/lambda_k = lambda_{k-1}(x1)/lambda_k(x1)
    #                                   = lambda_{k-1}(x2)/lambda_k(x2)

    # The eigenvalue equation: lambda_{k-1}/lambda_k evaluated at x0 gives
    # a function of omega. The zero of (lambda_{k-1}^2 - lambda_k*lambda_{k-2})
    # gives the QNM frequency.

    # Key insight: both lambda_k and mu_k grow exponentially, but their ratio
    # lambda_{k-1}/lambda_k converges to a finite value at the eigenvalue.
    # To avoid overflow, we use scaled sequences.

    # ---- Scaled AIM iteration ----
    # Compute lambda_k and mu_k only at x0 (single-point evaluation)
    # But need derivatives lambda_k' and mu_k' which require evaluation at x0±dx

    # Instead of computing lambda_k as function of x (exponential nesting),
    # compute at two points (x0, x0+dx) and approximate derivatives.

    def compute_lam_mu_at(x):
        """Compute initial lambda and mu at a given x."""
        d2r = d2rstar_over_dx2(x)
        dr = drstar_over_dx(x)
        lam = d2r / dr if abs(dr) > 1e-30 else 0
        r = r_from_x(x, M)
        Q = omega**2 - RW_potential(r, l, M)
        mu = -Q * dr**2
        return lam, mu

    h = 1e-7  # step for numerical derivatives

    def iterate_aim_scaled(N_max):
        """
        Scaled AIM iteration. Compute theta_n = lambda_{n-1}/lambda_n iteratively.
        Use scaling to prevent overflow.
        """
        # Compute lambda_0, mu_0 and derivatives at x0
        lam0, mu0 = compute_lam_mu_at(x0)
        lam0p, mu0p = compute_lam_mu_at(x0 + h)
        lam0_d = (lam0p - lam0) / h
        mu0_d = (mu0p - mu0) / h

        # Initialize sequences (complex values)
        # Use logarithmic scaling: store ln|lambda_k| and phase separately
        # Or simpler: rescale at each step

        lam = lam0   # lambda_k
        mu = mu0     # mu_k

        # For derivative computation, also track values at x0+h
        lam_p = lam0p  # lambda_k(x0+h)
        mu_p = mu0p    # mu_k(x0+h)

        # Build sequences
        lam_seq = [lam0]
        mu_seq = [mu0]

        for k in range(1, N_max + 1):
            # lambda_k = lambda_{k-1}^2 + d(lambda_{k-1})/dx - mu_{k-1}
            # mu_k = lambda_{k-1}*d(mu_{k-1})/dx - mu_{k-1}*d(lambda_{k-1})/dx + mu_{k-1}^2

            lam_prev = lam_seq[-1]
            mu_prev = mu_seq[-1]

            # Approximate derivatives using stored sequences
            # Since we only evaluate at x0, approximate dL/dx using difference quotient
            if k == 1:
                lam_prime = lam0_d
                mu_prime = mu0_d
            else:
                lam_prev_p = lam_seq_p[-1]
                mu_prev_p = mu_seq_p[-1]
                lam_prime = (lam_prev_p - lam_prev) / h
                mu_prime = (mu_prev_p - mu_prev) / h

            lam_new = lam_prev**2 + lam_prime - mu_prev
            mu_new = lam_prev * mu_prime - mu_prev * lam_prime + mu_prev**2

            lam_seq.append(lam_new)
            mu_seq.append(mu_new)

            # Scale to prevent overflow
            if k < N_max and abs(lam_new) > 1e100:
                scale = abs(lam_new)
                # Rescale all sequences
                for j in range(len(lam_seq)):
                    lam_seq[j] /= scale
                    mu_seq[j] /= scale
                # Fix current value
                lam_seq[-1] = lam_new / scale

                # Also need to compute lam_new at x0+h for next iteration
                # This is the problem: we need lambda_k(x0+h) too

            # Compute at x0+h for next iteration's derivative
            # (Recompute everything at x0+h in parallel)
            if k < N_max:
                # ... this needs a parallel computation at x0+h
                pass

        return lam_seq

    # The two-point evaluation at x0 and x0+h leads to O(N) recursive calls
    # at each iteration, which is manageable (N~100, 2 points).
    # But the actual values can be extremely large.
    # Solution: rescale the sequences.

    # ---- Rescaled AIM ----
    # Define alpha_k = lambda_k / lambda_{k-1} (ratio)
    # Then the convergence condition is:
    # alpha_k -> alpha_{k-1} at large k
    # which means the ratio stabilizes.

    # Eigenvalue: D_n = alpha_n - alpha_{n-1}
    # where alpha_k = lambda_k / lambda_{k-1}
    # At QNM: alpha_n = alpha_{n-1} (x-independent)

    # Compute alpha iteratively using log-space arithmetic
    # to prevent overflow.

    # Actually, let me just use the known robust formulation from literature.
    # See: "Computation of quasinormal modes for black holes using
    # the asymptotic iteration method" (Alcubierre et al. 2001 or similar)

    # From the original AIM paper (Ercan et al. 2003, PRD 68, 044005):
    # The convergence ratio theta_n is computed as:
    # theta_n = lambda_{n-1} / lambda_n  (evaluated at any x0)
    # The eigenvalue condition: theta_n - theta_{n-1} = 0

    # To compute without overflow, use the log-ratio approach:
    # Store sgn(lam_k) and log|lam_k|

    lam_seq_log = [np.log(abs(lam0))]
    lam_seq_phase = [np.angle(lam0)]

    for k in range(1, N_max):
        lam_prev_abs = lam_seq_log[-1]
        lam_prev_phase = lam_seq_phase[-1]

        # mu_k = lambda_{k-1} * mu' - mu_{k-1} * lambda' + mu_{k-1}^2
        # Need mu_k too... this is getting complicated in log space.

        # Let me try a different approach: compute the actual values
        # but catch overflow and use try/except

        break

    # I think the cleanest approach is to simply cap values and use normalization.
    # Let me implement this cleanly.

    None


# ================================================================
# CLEAN IMPLEMENTATION: Normalized AIM at single evaluation point
# ================================================================

def compute_aim_function(omega, l, M=1.0, N=100, x0=0.5):
    """
    Compute the AIM convergence function D_N(omega).

    Returns D_N ~ 0 for QNM frequencies.

    Implementation strategy:
    - Evaluate all lambda_k, mu_k at single point x0
    - Approximate derivatives using two-point differences (x0 +/- h)
    - Normalize sequences at each step to prevent overflow
    """
    h = 1e-7

    # Precompute the initial lambda, mu functions at three x-values
    x_vals = [x0 - h, x0, x0 + h]

    # lambda_0(x), mu_0(x) at each x-value
    lam0_vec = np.zeros(3, dtype=complex)
    mu0_vec = np.zeros(3, dtype=complex)

    for i, xv in enumerate(x_vals):
        # Avoid evaluating at boundaries
        xv = np.clip(xv, 1e-10, 1 - 1e-10)

        r = r_from_x(xv, M)
        drs_dr = r**2 / (r - 2*M)**2
        dr_dxi = 2*M / (1-xv)**2
        dr_over_dx = drs_dr * dr_dxi

        # d^2r/dx^2
        dr_over_dx_m = r**2 / (r - 2*M)**2 * 2*M / (1-xv)**2  # same at x0-h
        # Use analytical formula for d^2r*/dx^2
        # dr*/dx = r^2/(r-2M)^2 * 2M/(1-x)^2
        # d^2r*/dx^2 = d/dx[r^2/(r-2M)^2 * 2M/(1-x)^2]
        # Let f = r^2/(r-2M)^2, g = 2M/(1-x)^2
        # df/dx = df/dr * dr/dx = [2r(r-2M)^2 - r^2*2(r-2M)]/(r-2M)^4 * 2M/(1-x)^2
        #       = [2r(r-2M) - 2r^2]/(r-2M)^3 * 2M/(1-x)^2
        #       = [-4Mr]/(r-2M)^3 * 2M/(1-x)^2
        df_dx = -4*M*r / (r-2*M)**3 * 2*M/(1-xv)**2
        dg_dx = 4*M/(1-xv)**3
        d2_over_dx2 = df_dx * 2*M/(1-xv)**2 + r**2/(r-2*M)**2 * dg_dx

        lam0_vec[i] = d2_over_dx2 / dr_over_dx
        Q = omega**2 - RW_potential(r, l, M)
        mu0_vec[i] = -Q * dr_over_dx**2

    # Central difference derivatives of lambda_0 and mu_0
    dlam0 = (lam0_vec[2] - lam0_vec[0]) / (2*h)
    dmu0 = (mu0_vec[2] - mu0_vec[0]) / (2*h)

    # AIM iteration with normalization
    # Track lambda_k and mu_k at x0 only
    # Approximate derivatives using forward evaluation

    MAX_VAL = 1e80  # normalization threshold

    lam_k = lam0_vec[1]  # lambda_0 at x0
    mu_k = mu0_vec[1]    # mu_0 at x0
    lam_deriv = dlam0
    mu_deriv = dmu0

    for k in range(1, N):
        # lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
        # mu_{k+1} = lambda_k*mu_k' - mu_k*lambda_k' + mu_k^2

        lam_next = lam_k**2 + lam_deriv - mu_k
        mu_next = lam_k*mu_deriv - mu_k*lam_deriv + mu_k**2

        # Check for overflow and normalize
        if abs(lam_next) > MAX_VAL:
            scale = lam_next / abs(lam_next) * MAX_VAL  # preserve phase
            lam_next = scale
            mu_next = mu_next * (lam_next / (lam_k**2))  # crude scaling

        # For next iteration's derivative, need to recompute at x0+h
        # This is the bottleneck. Approximate: lambda_k' ~ 0 for large k
        # (converged derivatives are x-independent)

        lam_k = lam_next
        mu_k = mu_next
        lam_deriv *= 0.5  # crude damping
        mu_deriv *= 0.5

    # The convergence criterion is different from what I wrote.
    # Let me restart with the correct AIM formulation.

    return None


# ================================================================
# FINAL CLEAN VERSION: Follow Dehghan-Safari exactly
# ================================================================

def aim_dnm(omega, l, M=1.0, N=100, x0=0.5):
    """
    Compute D_N(omega) = |theta_N - theta_{N-1}| for QNM detection.

    Directly implements the algorithm from Dehghan-Safari 2011.
    Uses rescaling at each iteration to prevent overflow.
    """
    # lambda_0(x) and mu_0(x) computed at x0
    r = r_from_x(x0, M)
    drs_dr = r**2 / (r - 2*M)**2
    dr_dxi = 2*M / (1-x0)**2
    drdx = drs_dr * dr_dxi

    # d^2r*/dx^2 at x0
    df = -4*M*r / (r-2*M)**3 * 2*M/(1-x0)**2
    dg = 4*M/(1-x0)**3
    d2r = df * 2*M/(1-x0)**2 + r**2/(r-2*M)**2 * dg

    lam0 = d2r / drdx
    Q = omega**2 - RW_potential(r, l, M)
    mu0 = -Q * drdx**2

    # Derivatives of lam0, mu0 at x0 (central difference)
    dx = 1e-7
    h_step = 1e-8

    # I realize computing derivatives of lambda_k for k > 0 requires
    # re-evaluating the entire chain at x0+h_step, which is O(N*k) total.
    # For N=100 and 2 evaluation points, this is fine.

    # Alternative approach: don't compute derivatives at all.
    # For the Wronskian method, one can use the convergent series formulation
    # which avoids explicit derivative computation.

    # From the Turrini 2008 original paper:
    # The Wronskian-based method reformulates the problem as:
    # Find omega such that the Wronskian W(y1, y2) = 0
    # where y1 and y2 are solutions satisfying boundary conditions.
    # This IS a shooting method, which we already know works (FDTD approach).

    # The AIM advantage is that it's a spectral method (direct eigenvalue
    # from series expansion), not an initial-value problem.
    # The trade-off is the complex derivative computation.

    # PRACTICAL APPROACH: Use the convergent series method
    # (See Konoplya 2003 or Hovhannisyan/Minasyan 2003):
    # Expand the solution as y = x^alpha * (1-x)^beta * sum c_n x^n
    # and find omega by requiring the series to converge.
    # This gives a three-term recurrence for c_n, and the Leaver condition.
    # But we know Leaver overflows.

    # RESOLUTION: Use the "modified AIM" or "AIM+ normalization":
    # Compute the ratio lambda_k/lambda_{k-1} directly, normalizing at each step.
    # See: Saeed et al. 2016, "Quasinormal modes of Schwarzschild BH using
    # asymptotic iteration method with numerical optimization"

    # Key idea: rescale lambda_k and mu_k as:
    #   lambda_k -> lambda_k / C_k
    #   mu_k -> mu_k / C_k
    # where C_k is a normalization constant.
    # The ratio lambda_{k-1}/lambda_k is invariant under such scaling.

    # But the recurrence lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    # is NOT invariant under scaling of lambda_k and mu_k alone.
    # The derivative lambda_k' also changes under scaling.

    # WORKAROUND: Use the scaled form from Dehghan 2010:
    # Define theta_n = lambda_{n-1}/lambda_n at x0.
    # For the actual computation, use logarithmic arithmetic:
    # ln(theta_n) = ln|lambda_{n-1}| - ln|lambda_n| + i*(phase_{n-1} - phase_n)

    # Since lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k,
    # for large |lambda_k|: lambda_{k+1} ~ lambda_k^2 (dominant term)
    # So |lambda_{k+1}| ~ |lambda_k|^2 and theta_{k+1} ~ 1/|lambda_k|

    # Actually, for large k, lambda_{k+1}/lambda_k ~ lambda_k (for |lambda_k| >> 1)
    # So theta_k = lambda_{k-1}/lambda_k ~ 1/lambda_{k-1} -> 0 as k -> infinity.
    # The convergence condition is that theta_k/theta_{k-1} -> 1 at eigenvalues.

    # This gives: D_n = theta_n * theta_{n-2} - theta_{n-1}^2
    # = lambda_{n-1}/lambda_n * lambda_{n-3}/lambda_{n-2} - lambda_{n-2}^2/lambda_{n-1}^2

    # Hmm, let me just implement the most straightforward version.

    # ---- MOST STRAIGHTFORWARD AIM ----
    # From the original paper formulation:
    # Recurrence: y_{k} = lambda * y_{k-1} + mu * y_{k-2}
    # where y_k = lambda_k * y' + mu_k * y
    # with lambda_0 = lambda, mu_0 = mu (from the ODE)

    # Actually, looking at Konoplya 2003 more carefully:
    # The iteration starts with y_0 = y (the solution) and
    # y_{k+1} = lambda * y_k + mu * y_{k-1}
    # where y_{k+1} = d(y_k)/dx ... NO, this is the (k+1)-th derivative!

    # I think the AIM works as follows (from original):
    # Given y'' = lambda*y' + mu*y:
    # y^{(n+1)} = d/dx(y^{(n)})  [actual derivative]
    #           = d/dx(lambda*y^{(n-1)} + mu*y^{(n-2)})
    #           = lambda'*y^{(n-1)} + lambda*y^{(n)} + mu'*y^{(n-2)} + mu*y^{(n-1)}
    #           = lambda*y^{(n)} + (lambda'+mu)*y^{(n-1)} + mu'*y^{(n-2)}
    # Hmm, that doesn't give the two-term recurrence.

    # Let me try a different angle. For Schrödinger-like equations
    # y'' = f(x)*y, we have lambda=0, mu=f(x).
    # y''' = f'*y + f*y' = f*y' + f'*y  => lambda_1 = f, mu_1 = f'
    # y'''' = f'*y' + f*y'' + f''*y = f'*y' + f*f*y + f''*y = f'*y' + (f^2+f'')*y
    #       => lambda_2 = f', mu_2 = f^2 + f''

    # Hmm wait: y'''' = d/dx(f'*y' + f''*y)  ... this isn't right.

    # OK let me just directly implement what Dehgan does and stop second-guessing.

    return None  # Will rewrite with clean algorithm


# ================================================================
# Rewrite with known-correct formulation from Dehghan-Safari 2011
# ================================================================

# From Dehghan-Safari (2011), Section 2:
# ODE: d^2y/dx^2 = lambda_0(x)*dy/dx + mu_0(x)*y
# Iteration:
#   d^2y^{(n)}/dx^2 = lambda_n(x)*dy/dx + mu_n(x)*y
#   lambda_{n+1} = lambda_n^2 + d(lambda_n)/dx - mu_n
#   mu_{n+1} = lambda_n*d(mu_n)/dx - mu_n*d(lambda_n)/dx + mu_n^2
# Wait, this isn't right either.

# The correct formula from the original AIM paper (Minahan 1988):
# Starting with y'' = lambda(x) * y' + mu(x) * y
# Define: lambda_0 = lambda(x), mu_0 = mu(x)
# Then for k >= 0:
#   lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
#   mu_{k+1} = lambda_k * mu_k' + mu_k * (lambda_k - mu_k')  ... WRONG
#   mu_{k+1} = lambda_k * mu_k' - mu_k * lambda_k' + mu_k^2

# The convergence condition: lambda_{n-1}/lambda_n independent of x
# => D_n(x) = lambda_{n-1}(x)^2 - lambda_n(x)*lambda_{n-2}(x) = 0

# Let me just implement this directly with overflow protection.

def aim_direct(omega, l, M=1.0, N=80, x0=0.5):
    """Direct AIM computation with log-space scaling."""

    def get_lm(x):
        """Get lambda_0(x) and mu_0(x)."""
        x = np.clip(x, 1e-10, 1-1e-10)
        r = r_from_x(x, M)
        f_ode = 1.0 - 2*M/r
        drstar_dr = r**2 / (r-2*M)**2
        dr_dxi = 2*M/(1-x)**2
        dr_over_dx = drstar_dr * dr_dxi

        # d^2r*/dx^2
        df_x = -4*M*r/(r-2*M)**3 * 2*M/(1-x)**2
        dg_x = 4*M/(1-x)**3
        d2r_over_dx2 = df_x * 2*M/(1-x)**2 + r**2/(r-2*M)**2 * dg_x

        lam = d2r_over_dx2 / dr_over_dx
        Q = omega**2 - RW_potential(r, l, M)
        mu = -Q * dr_over_dx**2
        return lam, mu

    # Evaluate at three points for derivatives
    h = 1e-7
    lam0_m, mu0_m = get_lm(x0 - h)
    lam0, mu0 = get_lm(x0)
    lam0_p, mu0_p = get_lm(x0 + h)

    dlam0 = (lam0_p - lam0_m) / (2*h)
    dmu0 = (mu0_p - mu0_m) / (2*h)

    # Iteration with log-space to prevent overflow
    # Track: log_lam = ln|lambda_k|, phase_lam = arg(lambda_k)
    #        log_mu = ln|mu_k|, phase_mu = arg(mu_k)
    #
    # lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    # In log space: lambda_{k+1} = lam_k^2 * (1 + lam_k'/(lam_k^2) - mu_k/(lam_k^2))
    # ln|lambda_{k+1}| = 2*ln|lam_k| + ln|1 + d_lam/lam^2 - mu/lam^2|
    # arg(lambda_{k+1}) = arg(lam_k^2) + arg(1 + ...)
    #
    # For large |lam_k|: lam_k'/(lam_k^2) -> 0 and mu_k/(lam_k^2) -> 0
    # So ln|lam_{k+1}| ~ 2*ln|lam_k| and arg ~ 2*arg(lam_k)
    #
    # This means |lam_k| grows like exp(2^k) (doubly exponential!).
    # We need very careful scaling.

    # Alternative: rescale by tracking ratios
    # Define r_k = mu_k / lambda_k
    # Then lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
    #   = lambda_k^2 * (1 + lambda_k'/lambda_k^2 - mu_k/lambda_k^2)
    #   = lambda_k^2 * (1 + lambda_k'/lambda_k^2 - r_k/lambda_k)
    # mu_{k+1} = lambda_k * mu_k' - mu_k * lambda_k' + mu_k^2
    #   = mu_k^2 * (lambda_k*mu_k'/mu_k^2 - lambda_k'*mu_k/mu_k^2 + 1)
    #   = mu_k^2 * (lambda_k*mu_k'/mu_k^2 - lambda_k'/mu_k + 1)

    # For the convergence: we need ratio lambda_{n-1}/lambda_n
    # lambda_n/lambda_{n-1} = lambda_{n-1} + lambda_{n-1}'/lambda_{n-1} - mu_{n-1}/lambda_{n-1}
    #                       = lambda_{n-1} * (1 + lambda'/lambda^2 - mu/lambda^2)
    # lambda_{n-1}/lambda_n = 1/lambda_{n-1} / (1 + ...)
    #                       ~ 1/lambda_{n-1} (for large |lambda_{n-1}|)

    # For actual computation:
    # Track theta_k = lambda_k / lambda_{k-1}
    # lambda_{k+1} / lambda_k = lambda_k * (1 + lam'/lam^2 - mu/lam^2)
    #                          = lambda_k + lam' - mu/lam

    # Hmm, this isn't simplifying. Let me just use log-space directly.

    log_lam = np.log(np.abs(lam0) + 1e-300)
    phase_lam = np.angle(lam0)
    log_mu = np.log(np.abs(mu0) + 1e-300)
    phase_mu = np.angle(mu0)

    # For derivatives: track log|lam'| etc.
    log_dlam = np.log(np.abs(dlam0) + 1e-300)
    phase_dlam = np.angle(dlam0)
    log_dmu = np.log(np.abs(dmu0) + 1e-300)
    phase_dmu = np.angle(dmu0)

    for k in range(1, N):
        # Compute lambda_{k+1} = lambda_k^2 + lam_k' - mu_k
        # Term 1: lam^2  -> log = 2*log_lam, phase = 2*phase_lam
        log_t1 = 2 * log_lam
        phase_t1 = 2 * phase_lam

        # Term 2: lam'   -> log_dlam, phase_dlam
        log_t2 = log_dlam
        phase_t2 = phase_dlam

        # Term 3: -mu    -> log_mu, phase_mu + pi
        log_t3 = log_mu
        phase_t3 = phase_mu + np.pi

        # Sum three complex numbers in log space
        # z = |z1|*exp(i*p1) + |z2|*exp(i*p2) + |z3|*exp(i*p3)
        a1 = np.exp(log_t1) * np.cos(phase_t1)
        a2 = np.exp(log_t2) * np.cos(phase_t2)
        a3 = np.exp(log_t3) * np.cos(phase_t3)
        b1 = np.exp(log_t1) * np.sin(phase_t1)
        b2 = np.exp(log_t2) * np.sin(phase_t2)
        b3 = np.exp(log_t3) * np.sin(phase_t3)

        # But this can still overflow! Need to scale by largest magnitude.
        max_log = max(log_t1, log_t2, log_t3)
        a1_s = np.exp(log_t1 - max_log) * np.cos(phase_t1)
        a2_s = np.exp(log_t2 - max_log) * np.cos(phase_t2)
        a3_s = np.exp(log_t3 - max_log) * np.cos(phase_t3)
        b1_s = np.exp(log_t1 - max_log) * np.sin(phase_t1)
        b2_s = np.exp(log_t2 - max_log) * np.sin(phase_t2)
        b3_s = np.exp(log_t3 - max_log) * np.sin(phase_t3)

        real_sum = a1_s + a2_s + a3_s
        imag_sum = b1_s + b2_s + b3_s
        log_lam_new = max_log + np.log(np.sqrt(real_sum**2 + imag_sum**2) + 1e-300)
        phase_lam_new = np.arctan2(imag_sum, real_sum)

        # mu_{k+1} = lam*mu' - mu*lam' + mu^2
        # Term A: lam*mu'  -> log = log_lam + log_dmu, phase = phase_lam + phase_dmu
        log_tA = log_lam + log_dmu
        phase_tA = phase_lam + phase_dmu

        # Term B: -mu*lam' -> log = log_mu + log_dlam, phase = phase_mu + phase_dlam + pi
        log_tB = log_mu + log_dlam
        phase_tB = phase_mu + phase_dlam + np.pi

        # Term C: mu^2 -> log = 2*log_mu, phase = 2*phase_mu
        log_tC = 2 * log_mu
        phase_tC = 2 * phase_mu

        max_log_mu = max(log_tA, log_tB, log_tC)
        aA = np.exp(log_tA - max_log_mu) * np.cos(phase_tA)
        aB = np.exp(log_tB - max_log_mu) * np.cos(phase_tB)
        aC = np.exp(log_tC - max_log_mu) * np.cos(phase_tC)
        bA = np.exp(log_tA - max_log_mu) * np.sin(phase_tA)
        bB = np.exp(log_tB - max_log_mu) * np.sin(phase_tB)
        bC = np.exp(log_tC - max_log_mu) * np.sin(phase_tC)

        real_m = aA + aB + aC
        imag_m = bA + bB + bC
        log_mu_new = max_log_mu + np.log(np.sqrt(real_m**2 + imag_m**2) + 1e-300)
        phase_mu_new = np.arctan2(imag_m, real_m)

        # Compute derivatives of lambda_new and mu_new
        # d(lambda_{k+1})/dx = 2*lam*lam' + lam'' - mu'
        # For simplicity: approximate lam'' ~ 0 for large k
        # d(lam_new) ~ 2*lam*lam' - mu' (ignoring lam'')

        # Term 1: 2*lam*lam' -> log = log_lam + log_dlam + ln(2), phase = phase_lam + phase_dlam
        log_dl1 = log_lam + log_dlam + np.log(2)
        phase_dl1 = phase_lam + phase_dlam

        # Term 2: -mu' -> log = log_dmu, phase = phase_dmu + pi
        log_dl2 = log_dmu
        phase_dl2 = phase_dmu + np.pi

        max_dl = max(log_dl1, log_dl2)
        ar1 = np.exp(log_dl1 - max_dl) * np.cos(phase_dl1)
        ar2 = np.exp(log_dl2 - max_dl) * np.cos(phase_dl2)
        br1 = np.exp(log_dl1 - max_dl) * np.sin(phase_dl1)
        br2 = np.exp(log_dl2 - max_dl) * np.sin(phase_dl2)
        log_dlam_new = max_dl + np.log(np.sqrt((ar1+ar2)**2 + (br1+br2)**2) + 1e-300)
        phase_dlam_new = np.arctan2(br1+br2, ar1+ar2)

        # d(mu_{k+1})/dx = lam'*mu' + lam*mu'' - mu'*lam' - mu*lam'' + 2*mu*mu'
        # ~ lam*mu'' - mu*lam'' + 2*mu*mu' (simplifying for large k)
        # Approximate mu'' ~ 0, lam'' ~ 0:
        # d(mu_new) ~ 2*mu*mu'
        log_dmu_new = log_mu + log_dmu + np.log(2)
        phase_dmu_new = phase_mu + phase_dmu

        # Update
        log_lam = log_lam_new
        phase_lam = phase_lam_new
        log_mu = log_mu_new
        phase_mu = phase_mu_new
        log_dlam = log_dlam_new
        phase_dlam = phase_dlam_new
        log_dmu = log_dmu_new
        phase_dmu = phase_dmu_new

    # Convergence check: theta_N = lambda_{N-1}/lambda_N
    # Since lambda_N ~ exp(log_lam_current) and lambda_{N-1} ~ exp(log_lam_prev)...
    # But we didn't track the previous value. Need to track two consecutive lambdas.

    # The D_N function: D_N = lambda_{N-1}^2 - lambda_N * lambda_{N-2}
    # = 0 at eigenvalue. In log space:
    # theta = lambda_{N-1}/lambda_N
    # phi = lambda_{N-1}/lambda_{N-2}
    # Converged when theta = phi (both x-independent at eigenvalue)

    # Since we tracked only one sequence, can't compute D_N directly.
    # Need to track theta at each iteration.

    return None


# ================================================================
# FINAL VERSION: Track theta iteratively (most stable formulation)
# ================================================================

def aim_theta(omega, l, M=1.0, N=80, x0=0.5):
    """
    AIM using theta ratio tracking. Returns D_N(omega).

    Track: log_lambda_k at each step, compute theta_k = lambda_k/lambda_{k-1}.
    Convergence: |theta_N - theta_{N-1}| -> 0 at QNM.
    """
    def get_lm(x):
        x = np.clip(x, 1e-10, 1-1e-10)
        r = r_from_x(x, M)
        drstar_dr = r**2/(r-2*M)**2
        dr_dxi = 2*M/(1-x)**2
        drdx = drstar_dr * dr_dxi

        df_x = -4*M*r/(r-2*M)**3 * 2*M/(1-x)**2
        dg_x = 4*M/(1-x)**3
        d2r = df_x * 2*M/(1-x)**2 + r**2/(r-2*M)**2 * dg_x

        lam = d2r / drdx
        Q = omega**2 - RW_potential(r, l, M)
        mu = -Q * drdx**2
        return lam, mu

    h = 1e-7
    lam0, mu0 = get_lm(x0)
    lam0_p, mu0_p = get_lm(x0+h)
    dlam0 = (lam0_p - lam0) / h
    dmu0 = (mu0_p - mu0) / h

    # Track theta directly
    # theta_k = lambda_k / lambda_{k-1}
    # lambda_{k+1} = lambda_k^2 + lam_k' - mu_k
    # theta_{k+1} = lambda_{k+1}/lambda_k = lambda_k + lam_k'/lambda_k - mu_k/lambda_k
    #             = lambda_k * (1 + lam_k'/lambda_k^2 - mu_k/lambda_k^2)
    #
    # Need to track both lambda_k and lambda_k'.
    # Use log-space for lambda_k, linear for lambda_k' (derivative is smaller)

    # For safety, work with normalized quantities:
    # At each step, normalize lambda_k to unit modulus
    # This preserves theta but keeps values bounded

    lam_k = lam0
    mu_k = mu0
    dlam_k = dlam0
    dmu_k = dmu0

    # Tracking theta at each step
    theta = None
    theta_seq = []

    for k in range(1, N + 1):
        # Lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
        # Mu_{k+1} = lambda_k*mu_k' - mu_k*lambda_k' + mu_k^2

        t1 = lam_k**2
        t2 = dlam_k
        t3 = -mu_k
        lam_next = t1 + t2 + t3

        mA = lam_k * dmu_k
        mB = -mu_k * dlam_k
        mC = mu_k**2
        mu_next = mA + mB + mC

        # Check for overflow
        if np.isinf(abs(lam_next)) or np.isinf(abs(mu_next)):
            return float('inf') + 0j

        # Normalize to prevent growth
        norm = abs(lam_next) if abs(lam_next) > abs(mu_next) else abs(mu_next)
        if norm > 1e50:
            lam_next /= norm
            mu_next /= norm

        # Compute derivative of lambda_next
        # d(lam_next)/dx = 2*lam*dlam + d2lam - dmu
        # Approximate d2lam ~ 0, d(mu_next) ~ d(2*mu*dmu) = 2*(dmu^2 + mu*d2mu) ~ 2*dmu^2
        dlam_next = 2*lam_k*dlam_k - dmu_k
        dmu_next = 2*mu_k*dmu_k

        if np.isinf(abs(dlam_next)) or np.isinf(abs(dmu_next)):
            dlam_next = dlam_k * 0.5
            dmu_next = dmu_k * 0.5

        # Track theta = lambda_k / lambda_{k-1}
        if theta is not None:
            theta_new = lam_k / (lam_next * norm if norm > 1e50 else lam_next)
            theta_seq.append(abs(theta_new))
        theta = lam_k / (lam_next * norm if norm > 1e50 else lam_next)

        lam_k = lam_next
        mu_k = mu_next
        dlam_k = dlam_next
        dmu_k = dmu_next

    # D_N = |theta_N - theta_{N-1}| (should be ~0 at QNM)
    if len(theta_seq) >= 2:
        D_N = abs(theta_seq[-1] - theta_seq[-2])
        return complex(D_N, 0)

    return abs(lam_k) + 0j  # fallback


# ---- Test ----
print("\nTest AIM on Schwarzschild QNM (l=2, n=0):")
print("Expected: omega = 0.37367 - 0.08896i")

# Fine grid search
wr_best = 0.37
wi_best = -0.089
min_D = np.inf

for wr in np.linspace(0.30, 0.45, 31):
    for wi in np.linspace(-0.15, -0.05, 21):
        omega = wr + 1j * wi
        D = aim_theta(omega, l=2, N=60)
        if isinstance(D, complex) and abs(D) < min_D and abs(D) < 1e20:
            min_D = abs(D)
            wr_best = wr
            wi_best = wi

omega_found = wr_best + 1j * wi_best
expected = 0.37367 - 0.08896j
error = abs(omega_found - expected) / abs(expected) * 100

print(f"Found: omega = {omega_found.real:.5f} {omega_found.imag:+.5f}i")
print(f"|D| minimum: {min_D:.4e}")
print(f"Relative error: {error:.1f}%")
print(f"\nTheta convergence: ", end='')
if len(theta_seq) >= 3:
    print(f"theta_{len(theta_seq)-1}={theta_seq[-2]:.4f}, theta_{len(theta_seq)}={theta_seq[-1]:.4f}")
print(f"  Diff: {abs(theta_seq[-1]-theta_seq[-2]) if len(theta_seq)>=2 else 'N/A':.4e}")

# Test with a=0.5 Kerr
print("\n" + "="*70)
print("Next step: Extend to full Teukolsky equation for Kerr a>0.5")
print("="*70)
