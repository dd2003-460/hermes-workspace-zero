#!/usr/bin/env python3
"""
AIM solver with log-domain arithmetic to prevent overflow.

Core idea:
  alpha_{n+1}(y) = alpha_n'(y) + f(y) * alpha_n(y)
  = alpha_n(y) * [ (log_alpha)'(y) + f(y) ]

Track: mu = log|alpha|, theta = arg(alpha)
  dmu/dy at center = (mu[y+eps] - mu[y-eps]) / (2*eps)
  dtheta/dy similarly

  multiplier = (dmu/dy + i*dtheta/dy + f) at each point
  new_mu = mu + log|multiplier|
  new_theta = theta + arg(multiplier)

  Normalize per iteration: subtract center values to keep mu center = 0.
  But record the log-ratio before normalization:
    R_n = (mu_a[center] - mu_b[center]) + i*(theta_a[center] - theta_b[center])
  where a = xa-side, b = xb-side.

  At eigenvalue: R_n converges (|R_n - R_{n-1}| -> 0)
  Off eigenvalue: |R_n - R_{n-1}| grows exponentially.
"""

import numpy as np
import sys

M = 1.0
BERTI_REF = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def r_of_y(y):
    return 2.0 * M / (1.0 - y)


def rw_potential(r, l):
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)


def get_fg(y, l, omega):
    y = np.clip(y, 1e-12, 1.0 - 1e-12)
    r = r_of_y(y)
    V = rw_potential(r, l)
    J_val = 2.0 * M / (y**2 * (1.0 - y)**2)
    J_p = 4.0 * M * (1.0 - 2.0 * y) / (y**3 * (1.0 - y)**3)
    f = J_p / J_val
    g = -J_val**2 * (omega**2 - V)
    return f, g


def run_aim_ratio(omega, l, N, xa, xb, eps=5e-7):
    """Run AIM iteration, return log-ratio history and convergence criterion."""
    pts_a = np.array([xa - eps, xa, xa + eps])
    pts_b = np.array([xb - eps, xb, xb + eps])

    def init_side(pts):
        g_vals = np.array([get_fg(y, l, omega)[1] for y in pts], dtype=complex)
        mu = np.log(np.abs(g_vals))
        theta = np.angle(g_vals)
        f_vals = np.array([get_fg(y, l, omega)[0] for y in pts], dtype=complex)
        return mu, theta, f_vals

    mu_a, theta_a, f_a = init_side(pts_a)
    mu_b, theta_b, f_b = init_side(pts_b)

    ratio_history = []

    for k in range(N):
        # Forward/central/backward derivatives
        def deriv(arr):
            d = np.zeros(3)
            d[0] = (arr[1] - arr[0]) / eps
            d[1] = (arr[2] - arr[0]) / (2 * eps)
            d[2] = (arr[2] - arr[1]) / eps
            return d

        dmu_a = deriv(mu_a)
        dth_a = deriv(theta_a)
        dmu_b = deriv(mu_b)
        dth_b = deriv(theta_b)

        # Multiplier: z(y) = dmu/dy + i*dtheta/dy + f(y)
        # (note: f is complex in general because omega is complex)
        za = dmu_a + 1j * dth_a + f_a
        zb = dmu_b + 1j * dth_b + f_b

        # log|multiplier| and arg(multiplier)
        mag_a = np.maximum(np.abs(za), 1e-300)
        mag_b = np.maximum(np.abs(zb), 1e-300)
        arg_a = np.angle(za)
        arg_b = np.angle(zb)

        new_mu_a = mu_a + np.log(mag_a)
        new_theta_a = theta_a + arg_a
        new_mu_b = mu_b + np.log(mag_b)
        new_theta_b = theta_b + arg_b

        # Record log ratio BEFORE normalization
        r = (new_mu_a[1] - new_mu_b[1]) + 1j * (new_theta_a[1] - new_theta_b[1])
        ratio_history.append(r)

        # Normalize: set center to 0 for both mu and theta
        new_mu_a -= new_mu_a[1]
        new_theta_a -= new_theta_a[1]
        new_mu_b -= new_mu_b[1]
        new_theta_b -= new_theta_b[1]

        mu_a, theta_a = new_mu_a, new_theta_a
        mu_b, theta_b = new_mu_b, new_theta_b

    return ratio_history


def search_eigenvalue(l, N, N_search):
    """Search for eigenvalue by finding where convergence criterion is minimized."""
    ref = BERTI_REF[l]

    # Scan around reference
    re_range = np.linspace(ref.real - 0.3, ref.real + 0.3, N_search)
    im_range = np.linspace(ref.imag - 0.05, ref.imag + 0.05, N_search)

    best = []
    for re_w in re_range:
        for im_w in im_range:
            w = complex(re_w, im_w)
            hist = run_aim_ratio(w, l, N, 0.2, 0.8)
            if len(hist) >= 2:
                diff = abs(hist[-1] - hist[-2])
                if diff < 1e15 and not np.isnan(diff):
                    best.append((diff, w))

    best.sort()
    return best


def refine_eigenvalue(l, N, candidates):
    """Refine eigenvalues using bisection on log-ratio difference."""
    ref = BERTI_REF[l]
    eps = 5e-7

    # For 1D search: fix imaginary part, scan real part
    # Look for sign change in the convergence criterion
    # The criterion should go from small (at eigenvalue) to large (off eigenvalue)

    # Better: find where the AIM gives consistent limit at xa and xb
    # i.e., |R_N - R_{N-1}| is minimum

    # For each candidate, do a 1D refinement
    refined = []
    for guess_w in candidates[:10]:
        # Scan real part around guess
        re_best = guess_w
        re_best_diff = np.inf
        for dr in np.linspace(-0.05, 0.05, 21):
            w = complex(guess_w.real + dr, guess_w.imag)
            hist = run_aim_ratio(w, l, N, 0.2, 0.8)
            if len(hist) >= 2:
                diff = abs(hist[-1] - hist[-2])
                if diff < re_best_diff:
                    re_best = w
                    re_best_diff = diff
        refined.append((re_best_diff, re_best))

    refined.sort()
    return refined


def main():
    print("=" * 70)
    print("AIM Solver: Log-Ratio Convergence")
    print("=" * 70)

    l = 2
    ref = BERTI_REF[l]
    print(f"\nl={l}, Berti ref: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

    # Small test: verify at reference
    N = 100
    print(f"\nTest at Berti reference (N={N}):")
    hist = run_aim_ratio(ref, l, N, 0.25, 0.75)
    print(f"  First 3 ratio values: {hist[0]:.4e}, {hist[1]:.4e}, {hist[2]:.4e}")
    diffs = [abs(hist[i] - hist[i-1]) for i in range(1, len(hist))]
    print(f"  Last 3 |Rn-Rn-1|: {diffs[-3]:.4e}, {diffs[-2]:.4e}, {diffs[-1]:.4e}")
    print(f"  Mid 3 |Rn-Rn-1|: {diffs[N//4]:.4e}, {diffs[N//2]:.4e}, {diffs[3*N//4]:.4e}")

    # Different N
    for N in [50, 80, 120]:
        hist = run_aim_ratio(ref, l, N, 0.25, 0.75)
        diffs = [abs(hist[i] - hist[i-1]) for i in range(1, len(hist))]
        print(f"  N={N}: last_diff = {diffs[-1]:.4e}, midpoint_diff = {diffs[N//2]:.4e}")

    # Scan
    print(f"\n  Coarse scan (N=60):")
    best = search_eigenvalue(l, 60, 7)
    if best:
        for d, w in best[:5]:
            print(f"    omega = {w.real:.4f} - {abs(w.imag):.4f}i, |diff| = {d:.6e}")
    else:
        print("    No good results.")

    # Refine best candidate
    if best:
        ref_candidates = [w for _, w in best[:3]]
        refined = refine_eigenvalue(l, 80, ref_candidates)
        print(f"\n  Refined:")
        for d, w in refined[:5]:
            print(f"    omega = {w.real:.5f} - {abs(w.imag):.5f}i, |diff| = {d:.6e}")

    # Compare with Berti
    if best:
        w_best = best[0][1]
        rel_err = abs(w_best - ref) / abs(ref)
        print(f"\n  Best vs Berti: rel_error = {rel_err:.2e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
