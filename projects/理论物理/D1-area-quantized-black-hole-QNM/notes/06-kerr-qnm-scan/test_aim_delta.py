#!/usr/bin/env python3
"""
AIM solver using delta_n convergence criterion.

For the ODE: psi'' + lambda_1(y) * psi' + lambda_0(y) * psi = 0
AIM iteration:
  alpha_0 = lambda_0
  alpha_{n+1} = alpha_n' + lambda_1 * alpha_n
  delta_n = alpha_n' - alpha_n * lambda_1

The eigenvalue condition is: delta_N(y) is y-independent (or delta_N -> 0).
We compute delta_N at two points and look for W = |delta_N(xa) - delta_N(xb)| ~ 0.
"""

import numpy as np
from scipy.optimize import minimize

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


def J(y):
    """dr*/dy = 2M / [y^2 * (1-y)^2]"""
    return 2.0 * M / (y**2 * (1.0 - y)**2)


def J_prime(y):
    """dJ/dy = 4M(1-2y) / [y^3 * (1-y)^3]"""
    return 4.0 * M * (1.0 - 2.0 * y) / (y**3 * (1.0 - y)**3)


def compute_lambda1_mu(y, l, omega):
    """λ_1(y) and λ_0(y) for AIM: psi'' + λ_1(y)*psi' + λ_0(y)*psi = 0
    λ_1 = J'/J, λ_0 = -J^2(ω^2 - V)
    """
    y = np.clip(y, 1e-10, 1.0 - 1e-10)
    r = r_of_y(y)
    V = rw_potential(r, l)
    lam1 = J_prime(y) / J(y)
    lam0 = -J(y)**2 * (omega**2 - V)
    return lam1, lam0


def aim_delta_criterion(omega, l, N=120, xa=0.3, xb=0.7):
    """
    Compute delta_N at xa and xb.
    delta_N(y) = alpha_N'(y) - alpha_N(y)*lambda_1(y)
    where alpha_0 = lambda_0, alpha_{n+1} = alpha_n' + lambda_1 * alpha_n

    We compute alpha_n at y ± eps simultaneously for numerical derivatives.
    """
    eps = 1e-7

    def init_at(y):
        l1, l0 = compute_lambda1_mu(y, l, omega)
        return l0  # alpha_0 = lambda_0

    # Three points at each location
    y_pts_a = [xa - eps, xa, xa + eps]
    y_pts_b = [xb - eps, xb, xb + eps]

    alpha_a = np.array([init_at(y) for y in y_pts_a], dtype=complex)
    alpha_b = np.array([init_at(y) for y in y_pts_b], dtype=complex)
    l1_vals_a = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_a], dtype=complex)
    l1_vals_b = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_b], dtype=complex)

    MAX_S = 1e100

    for k in range(N):
        # Save previous alpha for delta computation at the END
        if k == N - 1:
            alpha_a_prev = alpha_a.copy()
            alpha_b_prev = alpha_b.copy()

        # Derivatives via central difference
        dalpha_a = np.array([
            (alpha_a[min(i+1, 2)] - alpha_a[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])
        dalpha_b = np.array([
            (alpha_b[min(i+1, 2)] - alpha_b[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])

        # alpha_{n+1} = alpha_n' + lambda_1 * alpha_n
        alpha_a_new = dalpha_a + l1_vals_a * alpha_a
        alpha_b_new = dalpha_b + l1_vals_b * alpha_b

        # Scaling
        sc_a = max(abs(v) for v in alpha_a_new)
        sc_b = max(abs(v) for v in alpha_b_new)
        if sc_a > MAX_S:
            alpha_a_new /= sc_a
        if sc_b > MAX_S:
            alpha_b_new /= sc_b

        # Check for NaN
        if any(np.isnan(v) or np.isinf(v) for v in alpha_a_new):
            return np.inf, np.inf
        if any(np.isnan(v) or np.isinf(v) for v in alpha_b_new):
            return np.inf, np.inf

        alpha_a = alpha_a_new
        alpha_b = alpha_b_new

    # delta_N = alpha_N' - alpha_N * lambda_1
    dalpha_a_mid = (alpha_a[2] - alpha_a[0]) / (2 * eps)
    dalpha_b_mid = (alpha_b[2] - alpha_b[0]) / (2 * eps)

    # alpha_N_prev is NOT scaled alpha_N at previous step -- it was scaled too!
    # Hmm, this is the problem. Let me think about this more carefully.

    # Actually, the issue is: we can't keep track of the unscaled values.
    # The scaled delta_N won't equal the unscaled delta_N.

    # Let me try without scaling first, see how far we get.

    delta_a = dalpha_a_mid - alpha_a[1] * l1_vals_a[1]
    delta_b = dalpha_b_mid - alpha_b[1] * l1_vals_b[1]

    return delta_a, delta_b


def aim_delta_unscaled(omega, l, N=120, xa=0.3, xb=0.7):
    """Same as above but WITHOUT scaling, to diagnose divergence."""
    eps = 1e-7

    def init_at(y):
        l1, l0 = compute_lambda1_mu(y, l, omega)
        return l0

    y_pts_a = [xa - eps, xa, xa + eps]
    y_pts_b = [xb - eps, xb, xb + eps]

    alpha_a = np.array([init_at(y) for y in y_pts_a], dtype=complex)
    alpha_b = np.array([init_at(y) for y in y_pts_b], dtype=complex)
    l1_vals_a = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_a], dtype=complex)
    l1_vals_b = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_b], dtype=complex)

    max_norm_a = abs(alpha_a[1])
    max_norm_b = abs(alpha_b[1])

    for k in range(N):
        dalpha_a = np.array([
            (alpha_a[min(i+1, 2)] - alpha_a[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])
        dalpha_b = np.array([
            (alpha_b[min(i+1, 2)] - alpha_b[max(i-1, 0)]) / (2 * eps)
            for i in range(3)
        ])

        alpha_a = dalpha_a + l1_vals_a * alpha_a
        alpha_b = dalpha_b + l1_vals_b * alpha_b

        max_norm_a = max(max_norm_a, max(abs(v) for v in alpha_a))
        max_norm_b = max(max_norm_b, max(abs(v) for v in alpha_b))

        if k % 20 == 0:
            print(f"    k={k}: |alpha_a| = {abs(alpha_a[1]):.6e}, |alpha_b| = {abs(alpha_b[1]):.6e}, max = {max_norm_a:.6e}")

        if any(np.isnan(v) for v in alpha_a) or any(np.isnan(v) for v in alpha_b):
            return np.nan, np.nan, k

    dalpha_a_mid = (alpha_a[2] - alpha_a[0]) / (2 * eps)
    dalpha_b_mid = (alpha_b[2] - alpha_b[0]) / (2 * eps)

    delta_a = dalpha_a_mid - alpha_a[1] * l1_vals_a[1]
    delta_b = dalpha_b_mid - alpha_b[1] * l1_vals_b[1]

    return delta_a, delta_b, max_norm_a


def main():
    print("=" * 70)
    print("AIM Solver - Delta_n Convergence Criterion")
    print("=" * 70)

    l = 2
    ref = BERTI_REF[l]
    print(f"\nl={l}, Berti reference: ω = {ref.real:.5f} - {abs(ref.imag):.5f}i\n")

    # Test at reference (unscaled, track divergence)
    print(f"Testing at BERTI reference (N=100) - UNSCALED:")
    result = aim_delta_unscaled(ref, l, N=100, xa=0.3, xb=0.7)
    if len(result) == 3:
        da, db, maxnorm = result
        if np.isnan(da):
            print(f"  NaN reached at iteration {maxnorm}")
        else:
            print(f"  delta_a = {da:.6e}")
            print(f"  delta_b = {db:.6e}")
            print(f"  |delta_a - delta_b| = {abs(da - db):.6e}")
    print()

    # Small test: N=20
    print(f"Testing at reference (N=30) - UNSCALED:")
    result = aim_delta_unscaled(ref, l, N=30, xa=0.3, xb=0.7)
    if len(result) == 3 and not np.isnan(result[0]):
        da, db, _ = result
        print(f"  delta_a = {da:.6e}")
        print(f"  delta_b = {db:.6e}")
        print(f"  |delta_a - delta_b| = {abs(da - db):.6e}")
    print()

    # Test perturbed values
    for dr in [0.05, -0.05]:
        for di in [0.02, -0.02]:
            omega_test = ref + complex(dr, di)
            result = aim_delta_unscaled(omega_test, l, N=30, xa=0.3, xb=0.7)
            if len(result) == 3 and not np.isnan(result[0]):
                da, db, _ = result
                diff = abs(da - db)
                print(f"  ω = {omega_test.real:.4f} - {abs(omega_test.imag):.4f}i: |Δ| = {diff:.6e}")

    # Now try scaled version at reference
    print(f"\n=== SAIM version ===")
    eps = 1e-7

    def saim_step(omega, l, N, xa, xb):
        def init_at(y):
            l1, l0 = compute_lambda1_mu(y, l, omega)
            return l0

        y_pts_a = [xa - eps, xa, xa + eps]
        y_pts_b = [xb - eps, xb, xb + eps]

        alpha_a = np.array([init_at(y) for y in y_pts_a], dtype=complex)
        alpha_b = np.array([init_at(y) for y in y_pts_b], dtype=complex)
        l1_vals_a = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_a], dtype=complex)
        l1_vals_b = np.array([compute_lambda1_mu(y, l, omega)[0] for y in y_pts_b], dtype=complex)

        MAX_S = 1e50
        log_info = []

        for k in range(N):
            if k == N - 1:
                alpha_a_prev = alpha_a.copy()
                alpha_b_prev = alpha_b.copy()

            dalpha_a = np.array([
                (alpha_a[min(i+1, 2)] - alpha_a[max(i-1, 0)]) / (2 * eps)
                for i in range(3)
            ])
            dalpha_b = np.array([
                (alpha_b[min(i+1, 2)] - alpha_b[max(i-1, 0)]) / (2 * eps)
                for i in range(3)
            ])

            alpha_a_new = dalpha_a + l1_vals_a * alpha_a
            alpha_b_new = dalpha_b + l1_vals_b * alpha_b

            sc_a = max(abs(v) for v in alpha_a_new) if all(not np.isnan(v) for v in alpha_a_new) else 1.0
            sc_b = max(abs(v) for v in alpha_b_new) if all(not np.isnan(v) for v in alpha_b_new) else 1.0

            info_a = f"|alpha|~{sc_a:.2e}"
            if sc_a > MAX_S:
                alpha_a_new /= sc_a
                info_a += " [scaled]"
            if sc_b > MAX_S:
                alpha_b_new /= sc_b
                info_a += f" |alpha|~{sc_b:.2e}"

            log_info.append(info_a)

            if any(np.isnan(v) or np.isinf(v) for v in alpha_a_new):
                return np.inf, np.inf, log_info
            if any(np.isnan(v) or np.isinf(v) for v in alpha_b_new):
                return np.inf, np.inf, log_info

            alpha_a = alpha_a_new
            alpha_b = alpha_b_new

        # Print last few entries
        for entry in log_info[-5:]:
            print(f"  {entry}")

        dalpha_a_mid = (alpha_a[2] - alpha_a[0]) / (2 * eps)
        dalpha_b_mid = (alpha_b[2] - alpha_b[0]) / (2 * eps)
        da = dalpha_a_mid - alpha_a[1] * l1_vals_a[1]
        db = dalpha_b_mid - alpha_b[1] * l1_vals_b[1]
        return da, db, log_info

    # Test at reference
    print(f"SAIM at reference:")
    da, db, _ = saim_step(ref, l, N=50, xa=0.3, xb=0.7)
    print(f"  delta_a = {da:.6e}")
    print(f"  delta_b = {db:.6e}")
    print(f"  |delta_a - delta_b| = {abs(da - db):.6e}")

    # Perturbed
    print(f"\nSAIM at perturbed values:")
    for dr in [0.05, -0.05]:
        for di in [0.02, -0.02]:
            omega_test = ref + complex(dr, di)
            da, db, _ = saim_step(omega_test, l, N=50, xa=0.3, xb=0.7)
            diff = abs(da - db)
            print(f"  ω = {omega_test.real:.4f} - {abs(omega_test.imag):.4f}i: |Δ| = {diff:.6e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
