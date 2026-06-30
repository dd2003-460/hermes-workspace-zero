#!/usr/bin/env python3
"""
Test different formulations of the AIM method and find one that works.

Standard AIM (Dehghan et al.):
  ODE: y'' = lambda(x) y' + mu(x) y
  Iteration:
    alpha_0 = mu, alpha_1 = mu' + lambda*mu
    alpha_{n+1} = alpha_n' + lambda*alpha_n
  Eigenvalue condition: delta_n = alpha_n' - alpha_n*lambda = 0

The key issue is the double-exponential growth. Standard remedy:
  Normalize at each step: beta_n = alpha_n / |alpha_n|
  But this loses magnitude information needed for delta_n.

Alternative approach: use ratio test.
  Define r_n = alpha_n / alpha_{n-1} (at each point)
  For large n, r_n -> lambda (the AIM limit)
  Eigenvalue condition: r_N(xa) = r_N(xb) for large N

But the ratio test requires comparing at specific points.

Let me try a completely different strategy: avoid numerical derivatives entirely.
Compute alpha_n values analytically by tracking the iteration at more points.

Or even simpler: let me just implement the delta_n criterion WITHOUT numerical
derivative of alpha_n. Instead, compute alpha_n' analytically by carrying
extra info.

Actually, the most standard approach (see papers):
  The eigenvalue condition is: del_{n}(x) = alpha_n'(x) - alpha_n(x)*lambda_1(x) = 0
  But we only need del_{n}(x_a) ≈ del_{n}(x_b) (they should be equal at eigenvalue)

  The derivative is computed numerically at each iteration.

Key trick from literature:
  Instead of normalizing alpha_n, compute the LOG of alpha_n:
  log_alpha_n = log(alpha_n)
  Then alpha_n' can be computed via central difference of exp(log_alpha_n)

Let me try the approach from papers more carefully.

Paper approach (G. Bonnor et al., M. Dehghan):
1. Convert to AIM form y'' = lambda * y' + mu * y
2. Iterate:
   lambda_0 = mu, mu_0 = mu'
   lambda_n = lambda_{n-1}^2 + lambda_{n-1}' - mu_{n-1}
   mu_n = lambda_{n-1}*mu_{n-1}' - mu_{n-1}*lambda_{n-1}' + mu_{n-1}^2

Wait, the standard convention uses lambda_n, mu_n instead of alpha_n.
lambda_n corresponds to the log-derivative of y at iteration n.

Let me implement THIS version.
"""

import numpy as np
import warnings

M = 1.0

BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


def r_of_y(y):
    return 2.0 * M / (1.0 - y)


def rw_potential(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)


def get_lam1_mu0(y, l, omega):
    """λ_1(y) and λ_0(y): d²ψ/dy² + λ_1(y)·dψ/dy + λ_0(y)·ψ = 0
    λ_1 = J'(y)/J(y), λ_0 = -J²(y)(ω² - V(r))
    """
    y = np.clip(y, 1e-10, 1.0 - 1e-10)
    r = r_of_y(y)
    V = rw_potential(r, l)
    J_val = 2.0 * M / (y**2 * (1.0 - y)**2)
    J_prime = 4.0 * M * (1.0 - 2.0 * y) / (y**3 * (1.0 - y)**3)
    lam1 = J_prime / J_val
    lam0 = -J_val**2 * (omega**2 - V)
    return lam1, lam0


def aim_lambda_mu_iteration(omega, l, N=80, xa=0.3, xb=0.7, eps=5e-7):
    """
    AIM using the lambda_n, mu_n recurrence:
    lambda_0(x) = mu(x), mu_0(x) = mu'(x)
    lambda_n = lambda_{n-1}^2 + lambda_{n-1}' - mu_{n-1}
    mu_n = lambda_{n-1}*mu_{n-1}' - mu_{n-1}*lambda_{n-1}' + mu_{n-1}^2

    Eigenvalue condition: lambda_{n-1}/lambda_n should be x-independent
    Or: D_n = lambda_{n-1}(xa)*lambda_n(xb) - lambda_n(xa)*lambda_{n-1}(xb) -> 0

    Or the delta_n criterion: delta_n(x) = lambda_n'(x) - lambda_n(x)*lambda_1(x) = 0

    We need lambda_n and its derivative at each iteration.
    We maintain values at xa±eps and xb±eps for numerical derivatives.
    """
    y_a = [xa - eps, xa, xa + eps]
    y_b = [xb - eps, xb, xb + eps]

    # Initial values
    lam_a = np.array([get_lam1_mu0(y, l, omega)[1] for y in y_a], dtype=complex)  # lambda_0 = mu_0
    mu_a = np.array([get_lam1_mu0(y, l, omega)[0],
                      get_lam1_mu0(y, l, omega)[0],  # placeholder
                      get_lam1_mu0(y, l, omega)[0]], dtype=complex)

    # Correctly compute mu_0 = mu'(x) for each point
    def get_mu0(y):
        h = 1e-8
        o = complex(0, 0)
        l1p, mup = get_lam1_mu0(y + h, l, omega)
        l1m, mum = get_lam1_mu0(y - h, l, omega)
        return (mup - mum) / (2 * h)

    mu_a = np.array([get_mu0(y) for y in y_a], dtype=complex)
    mu_b = np.array([get_mu0(y) for y in y_b], dtype=complex)
    lam_b = np.array([get_lam1_mu0(y, l, omega)[1] for y in y_b], dtype=complex)

    # Also get lambda_1 for derivative computation
    lam1_a = np.array([get_lam1_mu0(y, l, omega)[0] for y in y_a], dtype=complex)
    lam1_b = np.array([get_lam1_mu0(y, l, omega)[0] for y in y_b], dtype=complex)

    MAX_S = 1e100

    for k in range(1, N + 1):
        # Save previous for Wronskian
        lam_a_prev = lam_a.copy()
        mu_a_prev = mu_a.copy()
        lam_b_prev = lam_b.copy()
        mu_b_prev = mu_b.copy()

        # Derivatives of lambda and mu at current values
        dlam_a = np.array([
            (lam_a[min(i+1, 2)] - lam_a[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])
        dmu_a = np.array([
            (mu_a[min(i+1, 2)] - mu_a[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])
        dlam_b = np.array([
            (lam_b[min(i+1, 2)] - lam_b[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])
        dmu_b = np.array([
            (mu_b[min(i+1, 2)] - mu_b[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])

        # AIM iteration (center points)
        lam_a_new = lam_a**2 + dlam_a - mu_a  # (center point)
        mu_a_new = lam_a * dmu_a - mu_a * dlam_a + mu_a**2

        lam_b_new = lam_b**2 + dlam_b - mu_b
        mu_b_new = lam_b * dmu_b - mu_b * dlam_b + mu_b**2

        # Need values at ±eps too
        lam_ap_new, lam_am_new = lam_a_new, lam_a_new  # WRONG - need actual computation
        # Hmm, can't compute just from center. Need simultaneous iteration.

        # Actually for derivative of lambda_{k} at center point x:
        # lambda_k'(x) ≈ (lambda_k(x+eps) - lambda_k(x-eps)) / (2eps)
        # We need lambda_k at x±eps to compute derivative at x for the NEXT step.
        # But lambda_k(x±eps) requires running the iteration at those points.
        # This means we need to iterate at ALL points simultaneously.

        # Let me redo this properly with all points.
        break  # Break out and redo properly

    return aim_lambda_mu_v2(omega, l, N, xa, xb, eps, lam_a, mu_a, lam_b, mu_b, lam1_a, lam1_b)


def aim_lambda_mu_v2(omega, l, N=80, xa=0.3, xb=0.7):
    """
    Clean AIM iteration at 3 points per location for full derivative tracking.
    Points: [center - eps, center, center + eps] for each of xa and xb.
    """
    eps = 5e-7

    # All 3 points
    pts_a = [xa - eps, xa, xa + eps]
    pts_b = [xb - eps, xb, xb + eps]

    # Initial: lambda_0 = mu (the mu in y'' = lam1*y' + mu*y)
    # Actually re-reading the AIM paper more carefully:

    # For y'' + p(x)y' + q(x)y = 0:
    # lambda(x) = p(x), mu(x) = q(x)  [these are lambda_1 and lambda_0 above]
    #
    # AIM iteration:
    # alpha_0 = mu, (alpha_k in Dehghan notation, this is the same as lambda_k in some papers)
    # We compute alpha_n' using central differences
    # alpha_1 = alpha_0' + lambda*alpha_0 (this replaces the role of lambda_1 in the "lambda_n" notation)
    #
    # The eigenvalue condition involves the "delta_n":
    # delta_n = alpha_n' - alpha_n * lambda
    # At eigenvalue, delta_n should converge to 0.
    #
    # OR equivalently, define:
    # lambda_n = alpha_n, mu_n = alpha_n'/lambda_n (if lambda_n != 0)
    # Then the recurrence for lambda_n is the same as the original.

    # Let me use the most direct formulation:
    # Working with the ODE: psi'' = lambda_1(y) * psi' + lambda_0(y) * psi
    # where lambda_1 = -J'/J (note sign change!) and lambda_0 = J^2*(omega^2 - V)
    #
    # Wait, the standard AIM form is:
    # y'' = lambda(x) y' + mu(x) y
    # which means: y'' - lambda(x)y' - mu(x)y = 0
    #
    # My ODE: y'' + lambda_1(y)y' + lambda_0(y)y = 0
    # So: y'' = -lambda_1(y)y' - lambda_0(y)y
    # Hence: AIM-lambda = -lambda_1, AIM-mu = -lambda_0

    # But from derivation: d^2/d(r*)^2 = (1/J^2) d^2/dy^2 - (J'/J^3) d/dy
    # So: (1/J^2)psi'' - (J'/J^3)psi' + (omega^2 - V)psi = 0
    # Multiply by J^2: psi'' - (J'/J)psi' + J^2(omega^2 - V)psi = 0
    # AIM form: psi'' = (J'/J)psi' + [-J^2(omega^2 - V)]psi
    # So AIM-lambda = J'/J, AIM-mu = -J^2(omega^2 - V)

    # This matches what I have as lam1, lam0 in get_lam1_mu0.

    def init_all(y_list):
        """Initialize lambda_0 and mu_0 at all points."""
        lam0 = np.zeros(len(y_list), dtype=complex)
        for i, y in enumerate(y_list):
            _, m0 = get_lam1_mu0(y, l, omega)
            lam0[i] = m0  # lambda_0 = mu = the mu in the ODE
        return lam0

    # Initial lambda_n = mu_n (both are same notation in some conventions)
    lam_a = init_all(pts_a)
    mu_a = init_all(pts_a)

    # Wait, I'm confusing myself. Let me use clear notation.
    # In the AIM paper:
    #   Starting point: psi'' = f(x) psi' + g(x) psi
    #   Then: alpha_0(x) = g(x), and the iteration gives alpha_1, alpha_2, ...
    #   The eigenvalue condition: del_n = alpha_n' - alpha_n*f(x) = 0

    # So:
    # f(x) = lambda_1 (the coefficient of psi')
    # g(x) = lambda_0 (the coefficient of psi)

    # Let me just be super explicit:
    f = [get_lam1_mu0(y, l, omega)[0] for y in pts_a]  # lambda_1 (coefficient of psi')
    g = [get_lam1_mu0(y, l, omega)[1] for y in pts_a]  # lambda_0 (coefficient of psi)

    lam1_vals = np.array(f, dtype=complex)
    g_vals = np.array(g, dtype=complex)

    # Delta criterion (DEHGAN):
    # alpha_0 = g(x)
    # alpha_{n} = alpha_{n-1}' + f(x)*alpha_{n-1}
    # delta_n = alpha_n' - f(x)*alpha_n
    # Eigenvalue: delta_N(xa) ≈ delta_N(xb)

    alpha_a = g_vals[:]
    alpha_b = g_vals[:]

    # Precompute g at pts_b
    g_b = [get_lam1_mu0(y, l, omega)[1] for y in pts_b]
    lam1_b = np.array([get_f(y, l, omega) for y in pts_b], dtype=complex)
    g_vals_b = np.array(g_b, dtype=complex)

    MAX_S = 1e100

    for k in range(N):
        # Derivatives
        def central_diff(arr):
            return np.array([(arr[min(i+1, 2)] - arr[max(i-1, 0)]) / (2 * eps)
                            for i in range(3)], dtype=complex)

        dalpha_a = central_diff(alpha_a)
        dalpha_b = central_diff(alpha_b)

        # alpha_{k+1} = alpha_k' + f * alpha_k
        alpha_a_new = dalpha_a + lam1_vals * alpha_a
        alpha_b_new = dalpha_b + lam1_b * alpha_b

        # Scaling to prevent overflow
        sc_a = max(abs(v) for v in alpha_a_new)
        sc_b = max(abs(v) for v in alpha_b_new)

        if sc_a > MAX_S:
            alpha_a_new /= sc_a
        if sc_b > MAX_S:
            alpha_b_new /= sc_b

        if any(np.isnan(v) for v in alpha_a_new) or any(np.isnan(v) for v in alpha_b_new):
            return None, None

        alpha_a = alpha_a_new
        alpha_b = alpha_b_new

    # delta_N = alpha_N' - f * alpha_N (at center point)
    dalpha_a_center = (alpha_a[2] - alpha_a[0]) / (2 * eps)
    dalpha_b_center = (alpha_b[2] - alpha_b[0]) / (2 * eps)

    # But we scaled alpha_a and alpha_b, so delta_a is scaled too!
    # The scaling factor is NOT the same as original, so delta_a_scaled ≠ delta_a_original.
    # We need the UNSCALED delta to compare xa and xb.

    # KEY INSIGHT: The delta_n criterion is ONLY valid if alpha_n is NOT scaled.
    # But alpha_n grows so fast that it MUST be scaled.

    # The correct approach: DON'T scale. Instead, track the log-magnitude
    # and use it to rescale delta at the END.

    # Alternative: use the "ratio" eigenvalue condition.
    # At large N, lambda_n converges (up to scale).
    # The ratio alpha_n / alpha_{n-1} should be independent of x.
    # Let's try this.

    # Actually, let me just go back to basics and implement the iteration
    # WITHOUT scaling and with fewer N to see the convergence pattern.

    return dalpha_a_center - lam1_vals[1] * alpha_a[1], \
           dalpha_b_center - lam1_b[1] * alpha_b[1]


def get_f(y, l, omega):
    """f(x) = lambda_1 = J'(y)/J(y) = coefficient of psi'."""
    return get_lam1_mu0(y, l, omega)[0]


def aim_convergence_rate(omega, l, N=80, xa=0.3, xb=0.7):
    """
    Track the convergence of delta_n without any scaling.
    Report convergence rate and values at each step.
    """
    eps = 1e-7
    pts = [xa - eps, xa, xa + eps]

    def init(y):
        return get_lam1_mu0(y, l, omega)[1]  # alpha_0 = g

    alpha = np.array([init(y) for y in pts], dtype=complex)
    lam1 = np.array([get_lam1_mu0(y, l, omega)[0] for y in pts], dtype=complex)

    print(f"  k=0: alpha[1] = {alpha[1]:.6e}")

    # Track both magnitude and phase
    for k in range(1, N + 1):
        dalpha = (alpha[2:] - alpha[:-2]) / (2 * eps)  # central diff for middle only
        alpha_new = dalpha + lam1 * alpha

        info = f"  k={k:3d}: alpha_mid = {alpha_new[1]:.6e}"
        if k % 10 == 0:
            print(info)

        if any(np.isnan(v) for v in alpha_new):
            print(f"  NaN at k={k}")
            return None

        alpha = alpha_new

    # Compute delta at end
    dalpha_mid = (alpha[2] - alpha[0]) / (2 * eps)
    delta_mid = dalpha_mid - lam1[1] * alpha[1]
    print(f"  delta_mid = {delta_mid:.6e}")
    return delta_mid


def main():
    print("=" * 70)
    print("AIM Delta_n Convergence Test")
    print("=" * 70)

    l = 2
    ref = BERTI_REF[l]
    print(f"\nl={l}, reference: ω = {ref.real:.5f} - {abs(ref.imag):.5f}i")

    # Small N test to see convergence
    print("\n=== Convergence tracking at reference (unscaled) ===")
    aim_convergence_rate(ref, l, N=50, xa=0.3, xb=0.7)

    print("\n=== Testing with scaled version ===")
    for N in [40, 60, 80]:
        print(f"\nN={N}:")
        for dr in [0, 0.05, -0.05]:
            for di in [0, 0.02, -0.02]:
                w = ref + complex(dr, di)
                da, db = aim_lambda_mu_v2(w, l, N=N, xa=0.3, xb=0.7)
                if da is not None and not np.isnan(da):
                    diff = abs(da - db)
                    print(f"    ω={w.real:.4f}-{abs(w.imag):.4f}i: |δ_a - δ_b| = {diff:.6e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
