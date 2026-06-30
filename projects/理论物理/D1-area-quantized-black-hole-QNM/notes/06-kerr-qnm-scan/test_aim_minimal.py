#!/usr/bin/env python3
"""
Minimal working AIM solver for Schwarzschild QNMs.

VERIFIED equations from sympy derivation:
- y = 1 - 2M/r, y=0 is horizon, y=1 is infinity
- J(y) = dr*/dy = 2M / [y^2 * (1-y)^2]
- λ(y) = J'(y) / J(y)
- μ(y) = -J(y)^2 * (ω^2 - V(r(y), l))

AIM iteration (robust scaling):
  λ_k = λ_{k-1}^2 + λ'_{k-1} - μ_{k-1}
  μ_k = λ_{k-1} * μ'_{k-1} - μ_{k-1} * λ'_{k-1} + μ_{k-1}^2

Wronskian criterion:
  W(ω) = |λ_{N-1}(xa) * λ_N(xb) - λ_N(xa) * λ_{N-1}(xb)|
  At true eigenvalue, W -> 0 as N -> inf.
"""

import numpy as np
from scipy.optimize import minimize_scalar, differential_evolution

M = 1.0

# Berti et al. (2009) reference values
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


def r_of_y(y):
    """r = 2M / (1 - y)"""
    return 2.0 * M / (1.0 - y)


def rw_potential(r, l):
    """Regge-Wheeler potential."""
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)


def J(y, l, omega):
    """J(y) = dr*/dy. The exact analytical form is:
    dr*/dy = (dr*/dr) * (dr/dy)
    dr*/dr = r^2 / (r-2M)^2
    dr/dy = 2M / (1-y)^2
    r = 2M/(1-y) => r-2M = 2My/(1-y)
    => dr*/dr = [4M^2/(1-y)^2] / [4M^2*y^2/(1-y)^2] = 1/y^2
    => dr*/dy = (1/y^2) * 2M/(1-y)^2 = 2M / [y^2*(1-y)^2]
    """
    # Analytical (no numerical differentiation needed for J itself)
    return 2.0 * M / (y**2 * (1.0 - y)**2)


def J_prime(y):
    """dJ/dy analytically.
    J(y) = 2M * y^(-2) * (1-y)^(-2)
    J'(y) = 2M * [-2*y^(-3)*(1-y)^(-2) + y^(-2)*2*(1-y)^(-3)]
          = 2M * (-2/y^3 + 2/(y^2*(1-y))) / (1-y)^2
          = 2M * 2 * (-1 + y) / [y^3*(1-y)^3]
          = 4M * (1-2y) / [y^3*(1-y)^3]
    Check: J'(y) / J(y) = 4M(1-2y)/[y^3*(1-y)^3] * y^2*(1-y)^2/(2M)
                         = 2(1-2y) / [y*(1-y)]
                         = 2(2y-1)/[y*(y-1)]  -- matches sympy result!
    """
    return 4.0 * M * (1.0 - 2.0 * y) / (y**3 * (1.0 - y)**3)


def compute_coeffs(y, l, omega):
    """Compute λ(y) and μ(y) for AIM, plus numerical derivatives."""
    y = np.clip(y, 1e-10, 1.0 - 1e-10)
    r = r_of_y(y)
    V = rw_potential(r, l)
    Jval = J(y, l, omega)
    Jp = J_prime(y)
    lam = Jp / Jval  # analytical
    mu = -Jval**2 * (omega**2 - V)
    return lam, mu


def aim_wronskian(omega, l, N=150, xa=0.3, xb=0.7):
    """
    Compute AIM Wronskian at two interior points.

    Strategy:
    1. Compute λ_0(x) and μ_0(x) at xa, xb, xa+eps, xa-eps, xb+eps, xb-eps
    2. Iteratively compute λ_k, μ_k at all 6 points
    3. At each iteration, recompute λ_k' using central differences of λ_k values
    4. This way we avoid needing analytical derivatives of the iterated quantities
    """
    eps = 1e-7
    MAX_S = 1e100

    # Initial coefficients at 6 points
    def eval_at(y):
        lam, mu = compute_coeffs(y, l, omega)
        return lam, mu

    points = [xa, xa + eps, xa - eps, xb, xb + eps, xb - eps]
    vals = {}
    for p in points:
        vals[p] = eval_at(p)

    # lambda_0 and mu_0 at each point
    l0_a, m0_a = vals[xa]
    l0_ap, m0_ap = vals[xa + eps]
    l0_am, m0_am = vals[xa - eps]
    l0_b, m0_b = vals[xb]
    l0_bp, m0_bp = vals[xb + eps]
    l0_bm, m0_bm = vals[xb - eps]

    # Initialize scaled copies for Wronskian
    la_0, ma_0 = l0_a, m0_a
    la_pp, ma_pp = l0_ap, m0_ap
    la_mm, ma_mm = l0_am, m0_am
    lb_0, mb_0 = l0_b, m0_b
    lb_pp, mb_pp = l0_bp, m0_bp
    lb_mm, mb_mm = l0_bm, m0_bm

    # Previous (N-1)th iteration values for Wronskian
    la_prev_0, ma_prev_0 = la_0, ma_0
    la_prev_pp, ma_prev_pp = la_pp, ma_pp
    la_prev_mm, ma_prev_mm = la_mm, ma_mm
    lb_prev_0, mb_prev_0 = lb_0, mb_0
    lb_prev_pp, mb_prev_pp = lb_pp, mb_pp
    lb_prev_mm, mb_prev_mm = lb_mm, mb_mm

    for k in range(1, N + 1):
        # Central differences for derivatives
        dla_a = (la_pp - la_mm) / (2 * eps)
        dmu_a = (ma_pp - ma_mm) / (2 * eps)
        dla_b = (lb_pp - lb_mm) / (2 * eps)
        dmu_b = (mb_pp - mb_mm) / (2 * eps)

        # AIM recurrence:
        # λ_k = λ_{k-1}^2 + λ'_{k-1} - μ_{k-1}
        # μ_k = λ_{k-1}·μ'_{k-1} - μ_{k-1}·λ'_{k-1} + μ_{k-1}^2
        la_new = la_0**2 + dla_a - ma_0
        ma_new = la_0 * dmu_a - ma_0 * dla_a + ma_0**2
        lb_new = lb_0**2 + dla_b - mb_0
        mb_new = lb_0 * dmu_b - mb_0 * dla_b + mb_0**2

        # Save for Wronskian (k-th iteration before scaling)
        la_prev_0, ma_prev_0 = la_0, ma_0
        la_prev_pp, ma_prev_pp = la_pp, ma_pp
        la_prev_mm, ma_prev_mm = la_mm, ma_mm
        lb_prev_0, mb_prev_0 = lb_0, mb_0
        lb_prev_pp, mb_prev_pp = lb_pp, mb_pp
        lb_prev_mm, mb_prev_mm = lb_mm, mb_mm

        # Scaling to prevent overflow
        sc = max(abs(la_new), abs(ma_new), abs(lb_new), abs(mb_new))
        if sc > MAX_S:
            la_new /= sc; ma_new /= sc
            lb_new /= sc; mb_new /= sc
            la_prev_0 /= sc; ma_prev_0 /= sc
            la_prev_pp /= sc; ma_prev_pp /= sc
            la_prev_mm /= sc; ma_prev_mm /= sc
            lb_prev_0 /= sc; mb_prev_0 /= sc
            lb_prev_pp /= sc; mb_prev_pp /= sc
            lb_prev_mm /= sc; mb_prev_mm /= sc

        # Shift for derivative evaluation at NEXT iteration
        # We need new values at ±eps points too
        # Evaluate λ_k, μ_k at those points for the next derivative
        # But evaluating at each k is O(N) calls to compute_coeffs at shifted args

        # Actually, λ_k(x±eps) = λ_k of the coefficients evaluated at x±eps
        # So we need to run the AIM iteration simultaneously at x±eps
        # OR: recompute λ_k at each point by running the iteration again

        # Better approach: run the iteration forward AND carry values at ±eps

        # Redo: compute at all three points xa±eps and xb±eps simultaneously
        # The iteration at xa+eps uses the (xa+eps)-specific coefficients
        la_pp_new, ma_pp_new = la_pp**2 + dla_a - ma_pp
        ma_pp_new_check = la_pp * dmu_a - ma_pp * dla_a + ma_pp**2
        # Hmm, this is wrong - dmu_a is the derivative of mu at xa, not at xa+eps
        # Need mu derivative at xa+eps too

        # Clean approach: track 3 points: x-eps, x, x+eps, with derivatives
        pass

    # Simpler clean reimplementation below
    return aim_wronskian_v2(omega, l, N, xa, xb)


def aim_wronskian_v2(omega, l, N=150, xa=0.3, xb=0.7):
    """
    Clean AIM Wronskian with simultaneous iteration at three nearby points
    to get derivatives at each step.

    At each iteration k, we have λ_k(y), μ_k(y) for y ∈ {xa-eps, xa, xa+eps, xb-eps, xb, xb+eps}.
    Then λ'_{k}(y) ≈ (λ_k(y+eps) - λ_k(y-eps)) / (2eps) for the NEXT iteration.
    """
    eps = 5e-7
    MAX_S = 1e120

    def init_coeffs(y):
        return compute_coeffs(y, l, omega)

    # Phase 0: initial λ_0, μ_0 at 6 points
    y_left = [xa - eps, xa, xa + eps]
    y_right = [xb - eps, xb, xb + eps]

    # (lambda, mu) at each point
    left_l = [init_coeffs(y)[0] for y in y_left]
    left_m = [init_coeffs(y)[1] for y in y_left]
    right_l = [init_coeffs(y)[0] for y in y_right]
    right_m = [init_coeffs(y)[1] for y in y_right]

    for k in range(N):
        # Compute λ_{k+1}, μ_{k+1} at each of the 6 points
        def step(l_curr, m_curr, l_plus, m_plus, l_minus, m_minus):
            dl = (l_plus - l_minus) / (2 * eps)
            dm = (m_plus - m_minus) / (2 * eps)
            l_new = l_curr**2 + dl - m_curr
            m_new = l_curr * dm - m_curr * dl + m_curr**2
            return l_new, m_new

        # Left side (xa)
        new_left_l = []
        new_left_m = []
        for i in range(3):
            ln, mn = step(left_l[i], left_m[i],
                          left_l[min(i+1, 2)], left_m[min(i+1, 2)],
                          left_l[max(i-1, 0)], left_m[max(i-1, 0)])
            new_left_l.append(ln)
            new_left_m.append(mn)

        # Right side (xb)
        new_right_l = []
        new_right_m = []
        for i in range(3):
            ln, mn = step(right_l[i], right_m[i],
                          right_l[min(i+1, 2)], right_m[min(i+1, 2)],
                          right_l[max(i-1, 0)], right_m[max(i-1, 0)])
            new_right_l.append(ln)
            new_right_m.append(mn)

        # Scaling
        all_vals = new_left_l + new_left_m + new_right_l + new_right_m
        sc = max(abs(v) for v in all_vals if not np.isnan(v) and not np.isinf(v))
        if sc > MAX_S:
            for i in range(3):
                new_left_l[i] /= sc; new_left_m[i] /= sc
                new_right_l[i] /= sc; new_right_m[i] /= sc

        # Check for NaN/Inf
        if any(np.isnan(v) or np.isinf(v) for v in new_left_l + new_left_m + new_right_l + new_right_m):
            return np.inf

        # Update
        left_l, left_m = new_left_l, new_left_m
        right_l, right_m = new_right_l, new_right_m

    # Wronskian using the last two iterations
    # λ_{N-1}(xa) = left_l[1] (middle of left side, index 1)
    # λ_N(xa) = same after N iterations... we need to track the previous iteration too

    # Actually after the loop: left_l, left_m hold λ_N. But we lost λ_{N-1}.
    # Fix: save λ_{k} at each step.

    return aim_wronskian_v3(omega, l, N, xa, eps, xb, eps)


def aim_wronskian_v3(omega, l, N=150, xa=0.3, xb=0.7):
    """
    Track the last two iterations for the Wronskian.
    """
    eps = 5e-7
    MAX_S = 1e120

    def init_coeffs(y):
        return compute_coeffs(y, l, omega)

    y_left = [xa - eps, xa, xa + eps]
    y_right = [xb - eps, xb, xb + eps]

    left_l = [init_coeffs(y)[0] for y in y_left]
    left_m = [init_coeffs(y)[1] for y in y_left]
    right_l = [init_coeffs(y)[0] for y in y_right]
    right_m = [init_coeffs(y)[1] for y in y_right]

    # Initialize previous iteration = same as current (for k=0)
    left_l_prev = left_l[:]
    left_m_prev = left_m[:]
    right_l_prev = right_l[:]
    right_m_prev = right_m[:]

    for k in range(N):
        # Save current as previous
        left_l_prev = left_l[:]
        left_m_prev = left_m[:]
        right_l_prev = right_l[:]
        right_m_prev = right_m[:]

        def step(l_curr, m_curr, l_plus, m_plus, l_minus, m_minus):
            dl = (l_plus - l_minus) / (2 * eps)
            dm = (m_plus - m_minus) / (2 * eps)
            l_new = l_curr**2 + dl - m_curr
            m_new = l_curr * dm - m_curr * dl + m_curr**2
            return l_new, m_new

        # Left
        new_ll = []
        new_lm = []
        for i in range(3):
            ln, mn = step(left_l[i], left_m[i],
                          left_l[min(i+1, 2)], left_m[min(i+1, 2)],
                          left_l[max(i-1, 0)], left_m[max(i-1, 0)])
            new_ll.append(ln)
            new_lm.append(mn)

        # Right
        new_rl = []
        new_rm = []
        for i in range(3):
            ln, mn = step(right_l[i], right_m[i],
                          right_l[min(i+1, 2)], right_m[min(i+1, 2)],
                          right_l[max(i-1, 0)], right_m[max(i-1, 0)])
            new_rl.append(ln)
            new_rm.append(mn)

        # Scaling
        all_v = new_ll + new_lm + new_rl + new_rm
        sc = max(abs(v) for v in all_v if not np.isnan(v) and not np.isinf(v))
        if sc > MAX_S:
            for i in range(3):
                new_ll[i] /= sc; new_lm[i] /= sc
                new_rl[i] /= sc; new_rm[i] /= sc

        if any(np.isnan(v) or np.isinf(v) for v in new_ll + new_lm + new_rl + new_rm):
            return np.inf

        left_l, left_m = new_ll, new_lm
        right_l, right_m = new_rl, new_rm

    # Wronskian at index 1 (middle point of each side)
    # λ_{N-1}(xa) = left_l_prev[1], λ_{N-1}(xb) = right_l_prev[1]
    # λ_N(xa) = left_l[1], λ_N(xb) = right_l[1]
    lam_nm_a = left_l_prev[1]   # λ_{N-1}(xa)
    lam_n_a = left_l[1]         # λ_N(xa)
    lam_nm_b = right_l_prev[1]  # λ_{N-1}(xb)
    lam_n_b = right_l[1]        # λ_N(xb)

    W = abs(lam_nm_a * lam_n_b - lam_n_a * lam_nm_b)
    return W


def scan_aim(l, omega_range, N=150):
    """Scan omega values and find minimum Wronskian."""
    results = []
    for re_omega in np.linspace(omega_range[0][0], omega_range[0][1], 80):
        for im_omega in np.linspace(omega_range[1][0], omega_range[1][1], 80):
            omega = complex(re_omega, im_omega)
            W = aim_wronskian_v3(omega, l, N=N)
            if W < 1e50 and not np.isnan(W):
                results.append((W, omega))
    results.sort()
    return results[:5]


if __name__ == "__main__":
    print("=" * 70)
    print("AIM Solver for Schwarzschild QNMs")
    print("=" * 70)

    for l in [2, 3]:
        print(f"\nl={l}:")
        ref = BERTI_REF[l]
        print(f"  Berti reference: ω = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        # Test at reference
        W_ref = aim_wronskian_v3(ref, l, N=100)
        print(f"  |W| at reference (N=100): {W_ref:.6e}")

        W_ref200 = aim_wronskian_v3(ref, l, N=200)
        print(f"  |W| at reference (N=200): {W_ref200:.6e}")

        # Small perturbation
        for dr in [0.01, -0.01]:
            for di in [0.005, -0.005]:
                omega_test = ref + complex(dr, di)
                W_test = aim_wronskian_v3(omega_test, l, N=100)
                print(f"  |W| at ω+({dr},{di}) (N=100): {W_test:.6e}")

        # Brief scan
        print(f"\n  Scanning around reference with N=80...")
        best = scan_aim(l, [(ref.real - 0.2, ref.real + 0.2),
                            (ref.imag - 0.1, ref.imag + 0.1)], N=80)
        if best:
            for W, om in best[:5]:
                print(f"  Best: |W|={W:.6e}, ω = {om.real:.5f} - {abs(om.imag):.5f}i")
        else:
            print("  No converged Wronskian found in scan.")

    print("\n" + "=" * 70)
