#!/usr/bin/env python3
"""
Robust AIM solver for Schwarzschild QNMs.

After extensive debugging:
- UNSCALED AIM diverges by ~1e200 before overflow (doubly exponential)
- FULL SCALING at each step makes ALL delta_n identical (0.000000e+00)
- Need: scale only to prevent overflow while preserving DIFFERENCES between points

Strategy: Use "partial" scaling where the ratio at each point is maintained,
but different points keep independent scales.

The ratio test:
  r_a = alpha_N(xa) / alpha_{N-1}(xa)
  r_b = alpha_N(xb) / alpha_{N-1}(xb)
  At eigenvalue: r_a ≈ r_b (the ratio converges to the AIM limit)

BUT after scaling, alpha_N and alpha_{N-1} may have different scale factors.
Solution: Track the cumulative scaling factors.
"""

import numpy as np

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


def get_f_g(y, l, omega):
    """Get f(x), g(x) for AIM: psi'' = f(x) psi' + g(x) psi
    f = J'(y)/J(y), g = -J(y)^2*(omega^2 - V)
    """
    y = np.clip(y, 1e-10, 1.0 - 1e-10)
    r = r_of_y(y)
    V = rw_potential(r, l)
    J_val = 2.0 * M / (y**2 * (1.0 - y)**2)
    J_prime = 4.0 * M * (1.0 - 2.0 * y) / (y**3 * (1.0 - y)**3)
    f_val = J_prime / J_val  # = 2(2y-1) / [y(y-1)]  (analytically!)
    g_val = -J_val**2 * (omega**2 - V)
    return f_val, g_val


def aim_ratio_test(omega, l, N=100, xa=0.3, xb=0.7):
    """
    AIM ratio test with independent scaling per point.

    At each step k:
      1. Compute alpha_{k} at x, x+eps, x-eps for both xa and xb
      2. Apply independent scaling factors per location (to prevent overflow)
      3. Track the ratio alpha_k / alpha_{k-1} at each location

    The ratio test converges: r_k(x) -> alpha_k/alpha_{k-1} which is
    the "AIM eigenvalue" at that location. At the QNM eigenvalue,
    r_k(xa) ≈ r_k(xb).

    The tricky part: scaling per point breaks the ratio comparison.
    Solution: track cumulative scale factors so we can reconstruct
    the true ratio.
    """
    eps = 5e-7
    pts_a = [xa - eps, xa, xa + eps]
    pts_b = [xb - eps, xb, xb + eps]

    def init_f_g(pts):
        f = np.array([get_f_g(y, l, omega)[0] for y in pts], dtype=complex)
        g = np.array([get_f_g(y, l, omega)[1] for y in pts], dtype=complex)
        return f, g

    f_a, g_a = init_f_g(pts_a)
    f_b, g_b = init_f_g(pts_b)

    # alpha_0 = g (center point)
    alpha_a = g_a.copy()
    alpha_b = g_b.copy()

    # Track ratio: alpha_N / alpha_{N-1} at each center point
    # ratio = alpha[1] / alpha_prev[1]
    # BUT if scaling was applied, alpha[1] = true_alpha[1] / scale
    # and alpha_prev[1] = true_alpha_prev[1] / scale_prev
    # So ratio = (alpha[1]/alpha_prev[1]) * (scale_prev/scale)
    # We need to track the scale factors.

    # Scale factor history (for center point only)
    scale_a = 1.0
    scale_b = 1.0
    cum_scale_a = 1.0  # cumulative product of all scale factors
    cum_scale_b = 1.0

    # Previous alpha for ratio computation (PRE-scaling)
    alpha_prev = alpha_a.copy()

    for k in range(N):
        # Derivatives (center point)
        dalpha_a = (alpha_a[2] - alpha_a[0]) / (2 * eps)
        dalpha_b = (alpha_b[2] - alpha_b[0]) / (2 * eps)

        # alpha_{k+1} = alpha_k' + f * alpha_k
        alpha_a_new = dalpha_a + f_a * alpha_a
        alpha_b_new = dalpha_b + f_b * alpha_b

        # Track scale factors
        sa_a = abs(alpha_a_new[1])
        sa_b = abs(alpha_b_new[1])
        SC_THRESHOLD = 1e100

        scale_factor_a = 1.0
        scale_factor_b = 1.0

        if sa_a > SC_THRESHOLD:
            alpha_a_new /= sa_a
            scale_factor_a = sa_a
        if sa_b > SC_THRESHOLD:
            alpha_b_new /= sa_b
            scale_factor_b = sa_b

        if any(np.isnan(v) for v in alpha_a_new) or any(np.isnan(v) for v in alpha_b_new):
            return np.inf, np.inf

        # Accumulated scale
        cum_scale_a *= scale_factor_a
        cum_scale_b *= scale_factor_b

        # Ratio at this step: true_alpha_new / alpha_prev
        # alpha_new[1] (scaled) = true_alpha_new[1] / scale_factor
        # So: true_alpha_new = alpha_new[1] * scale_factor (for center)
        # ratio_true = true_alpha_new[1] / true_alpha_prev[1]
        # But we need to undo the scaling of alpha_prev:
        # alpha_prev = true_alpha_prev / (cum_scale * scale_factor_prev)

        # Hmm, this is getting complicated. Let me use a different approach:
        # Track alpha centered at the center point with its OWN scale.
        # At each step, the ratio is computed from the UNscaled values.

        # SIMPLER: Don't scale individual points. Just scale the center value
        # at each step to control magnitude. The left/right values can overflow
        (alpha_a_prev_center, alpha_b_prev_center) = (alpha_a[1].copy()
        )

        # Scale only the center to reasonable range
        if abs(alpha_a[1]) > SC_THRESHOLD:
            alpha_a[1] = alpha_a[1] / abs(alpha_a[1])
        if abs(alpha_b[1]) > SC_THRESHOLD:
            alpha_b[1] = alpha_b[1] / abs(alpha_b[1])

        # Move to next iteration
        alpha_prev = alpha_a.copy()
        alpha_a = alpha_a_new
        alpha_b = alpha_b_new

    # At the end, alpha_prev = alpha_{N-1}, alpha = alpha_N
    # Need to UNDO any scaling applied to alpha_prev and alpha
    # Actually this approach is fundamentally broken.

    # NEW APPROACH: Use the ORIGINAL delta_n formula but with a SINGLE global scale.
    # Scale ALL alpha values simultaneously by the same factor.
    # This preserves ratios at each point, AND preserves the difference of
    # delta values (since they're all scaled by the same factor).

    # Redo:
    return aim_delta_global_scale(omega, l, N, xa, xb, eps)


def aim_delta_global_scale(omega, l, N=100, xa=0.7, xb=0.7):
    """
    Global scaling: scale ALL values (left, center, right at both xa and xb)
    by the SAME factor. This preserves all ratios AND the Wronskian ratio.
    """
    eps = 5e-7

    pts = np.array([xa, xb])  # Just two points
    # Need to expand to 3 points per location for derivatives

    pts_a = np.array([xa - eps, xa, xa + eps])
    pts_b = np.array([xb - eps, xb, xb + eps])

    # Initial alpha_0 = g (get the g value at each point)
    alpha = np.zeros((2, 3), dtype=complex)
    for s, side in enumerate([pts_a, pts_b]):
        for j, y in enumerate(side):
            alpha[s, j] = get_f_g(y, l, omega)[1]  # alpha_0 = g

    MAX_S = 1e100

    for k in range(N):
        # Save previous
        alpha_prev = alpha.copy()

        # Central difference for each side
        dalpha = np.zeros_like(alpha)
        for s in range(2):
            dalpha[s, 1] = (alpha[s, 2] - alpha[s, 0]) / (2 * eps)

        # Get f values
        f = np.zeros(2, dtype=complex)
        for s, side in enumerate([pts_a, pts_b]):
            f[s] = get_f_g(side[1], l, omega)[0]  # f at center

        # alpha_{k+1} = alpha_k' + f * alpha_k
        alpha_new = np.zeros_like(alpha)
        for s in range(2):
            # For all 3 points
            if s == 0:
                f_pts = np.array([get_f_g(y, l, omega)[0] for y in pts_a], dtype=complex)
            else:
                f_pts = np.array([get_f_g(y, l, omega)[0] for y in pts_b], dtype=complex)
            dalpha_s = np.zeros(3, dtype=complex)
            dalpha_s[1] = (alpha[s, 2] - alpha[s, 0]) / (2 * eps)
            alpha_new[s, 1] = dalpha_s[1] + f_pts[1] * alpha[s, 1]
            # Don't need left/right for the delta computation at center

        # Global scale
        sc = max(abs(alpha_new[s, 1]) for s in range(2))
        if sc > MAX_S:
            for s in range(2):
                alpha_new[s, :] /= sc

        if any(np.isnan(alpha_new)) or any(np.isinf(alpha_new)):
            return np.inf, np.inf

        alpha = alpha_new

    # delta = alpha_N' - f * alpha_N
    dalpha_a = (alpha[0, 2] - alpha[0, 0]) / (2 * eps)
    dalpha_b = (alpha[1, 2] - alpha[1, 0]) / (2 * eps)

    delta_a = dalpha_a - f[0] * alpha[0, 1]
    delta_b = dalpha_b - f[1] * alpha[1, 1]

    return delta_a, delta_b


def aim_criterion_detailed(omega, l, N=100, xa=0.3, xb=0.7):
    """
    Most careful implementation yet.

    We maintain (for EACH of the two locations independently):
      - alpha_n at y - eps, y, y + eps (for computing alpha_n' at center)
      - f(y) at each point
      - Apply scaling to prevent overflow

    CRITICAL: For the delta criterion, we use the formula:
      delta_n = alpha_n' - f * alpha_n

    If scaling factor at iteration k is s_k, then:
      alpha_k(scaled) = alpha_k(true) / prod(s_j)

    So: delta_n(scaled) = delta_n(true) / prod(all scales)

    Since we need delta_n(xa) / delta_n(xb), the prod cancels IF
    both sides use the SAME product. But they have independent scales!

    So delta_a / delta_b = (delta_a_true / prod_a) / (delta_b_true / prod_b)
                        = (delta_a_true / delta_b_true) * (prod_b / prod_a)

    At eigenvalue: delta_a_true = delta_b_true, so ratio = prod_b / prod_a.
    For ratio = 1: prod_a = prod_b. But these are independently computed,
    so ratio != 1 generally.

    This means: the DELTA CRITERION REQUIRES either unscaled values or
    linked scaling between the two locations.

    ALTERNATIVE: ratio test on the alpha values directly.
      r_a = alpha_N[center, a] / alpha_{N-1}[center, a]
      r_b = alpha_N[center, b] / alpha_{N-1}[center, b]

    After independent scaling:
      alpha_N^scaled = alpha_N^true / scale_N
      alpha_{N-1}^scaled = alpha_{N-1}^true / scale_{N-1}
      ratio_scaled = (alpha_N^true / alpha_{N-1}^true) * (scale_{N-1} / scale_N)

    So the ratio is only correct up to factor (scale_{N-1}/scale_N), which
    is independent of the location! So:
      r_a_scaled / r_b_scaled = (r_a_true / r_b_true) * [scale_{N-1,a}/scale_{N,a}] / [scale_{N-1,b}/scale_{N,b}]
                              = (r_a_true / r_b_true) * [scale_{N-1,a}*scale_{N,b}] / [scale_{N,a}*scale_{N-1,b}]

    The scale factor correction depends on the ratio of scale factors.
    At eigenvalue: r_a_true = r_b_true, so r_a_scaled / r_b_scaled should equal
    scale_correction. But scale_correction is NOT 1 in general.

    BOTTOM LINE: independent scaling breaks the eigenvalue criterion.
    The solution: use LOG SCALE.

    Or just run unscaled for small N and find approximate eigenvalues,
    then refine with shooting method.
    """

    eps = 1e-7

    pts_a = np.array([xa - eps, xa, xa + eps])
    pts_b = np.array([xb - eps, xb, xb + eps])

    # Initialize: compute log(alpha_0) instead of alpha_0
    def log_at(y):
        g_val = get_f_g(y, l, omega)[1]
        return np.log(g_val) if g_val != 0 else complex(-1e30, 0)

    log_alpha_a = np.array([log_at(y) for y in pts_a], dtype=complex)
    log_alpha_b = np.array([log_at(y) for y in pts_b], dtype=complex)
    f_a = np.array([get_f_g(y, l, omega)[0] for y in pts_a], dtype=complex)
    f_b = np.array([get_f_g(y, l, omega)[0] for y in pts_b], dtype=complex)

    SCALE_TH = 1e300

    for k in range(N):
        # alpha_n' via: exp(log_alpha_n(y+h)) - exp(log_alpha_n(y-h)) / 2h
        # = (exp(diff) - 1) * exp(log_alpha(y)) / 2h ... not helpful

        # Actually: alpha' = d/dy (exp(log_alpha)) = exp(log_alpha) * d(log_alpha)/dy
        # So: alpha'(center) = alpha[1] * dlog_alpha[1]
        # where dlog_alpha is the derivative of log(alpha)

        # But dlog_alpha at center needs log_alpha at ±eps, not log_alpha at ±eps itself...
        # Wait: we track log_alpha at 3 points, so:
        # dlog_alpha[1] = (log_alpha[2] - log_alpha[0]) / (2eps)
        # alpha'[1] = exp(log_alpha[1]) * dlog_alpha[1]

        log_dalpha_a = (log_alpha_a[2] - log_alpha_a[0]) / (2 * eps)
        log_dalpha_b = (log_alpha_b[2] - log_alpha_b[0]) / (2 * eps)

        # alpha'[1] = alpha[1] * d(log_alpha)/dy
        dalpha_a = np.exp(log_alpha_a[1]) * log_dalpha_a
        dalpha_b = np.exp(log_alpha_b[1]) * log_dalpha_b

        # alpha_new = dalpha + f * alpha (center points only)
        alpha_a = np.exp(log_alpha_a[1])
        alpha_b = np.exp(log_alpha_b[1])

        alpha_new_a = dalpha_a + f_a[1] * alpha_a
        alpha_new_b = dalpha_b + f_b[1] * alpha_b

        # log(alpha_new) with scale handling
        sc_a = abs(alpha_new_a)
        sc_b = abs(alpha_new_b)

        # log|alpha_new| = log|sc| + log|alpha_new/sc|
        # For alpha_new: log(1) = 0 when normalized
        if sc_a > SCALE_TH:
            log_alpha_a_new = np.log(alpha_new_a / sc_a) + np.log(sc_a)
        else:
            log_alpha_a_new = np.log(alpha_new_a)

        if sc_b > SCALE_TH:
            log_alpha_b_new = np.log(alpha_new_b / sc_b) + np.log(sc_b)
        else:
            log_alpha_b_new = np.log(alpha_new_b)

        if np.isnan(log_alpha_a_new) or np.isnan(log_alpha_b_new):
            return np.inf, np.inf

        log_alpha_a_new = np.array([
            log_alpha_a_new,  # center
            log_alpha_a_new,  # need to track neighbors too!
            log_alpha_a_new,
        ], dtype=complex)

    # This log approach is broken because we can't differentiate neighbors correctly
    return aim_log_stable(omega, l, N, xa, xb)


def aim_log_stable(omega, l, N=80, xa=0.3, xb=0.7):
    """
    Log-domain AIM with proper 3-point tracking.

    At each iteration:
      1. exp(alpha_log[pts]) to get alpha[pts]
      2. Compute derivative alpha'(center) = alpha(center) * dlog_alpha(center)
         where dlog_alpha(center) ≈ (log_alpha[right] - log_alpha[left]) / (2eps)
         This is EXACT: d/dy exp(log_alpha) = exp(log_alpha) * d(log_alpha)/dy

      3. Compute new log_alpha = log(alpha'(center) + f*alpha(center))
         With scale: log_alpha_new = log(alpha_new / sc) + log(sc)

      4. For neighbors: repeat steps 1-3.

    The key: we track log_alpha at 3 points simultaneously, so we get the
    derivative information for the NEXT iteration naturally.

    But step 3 means: alpha_new at center is a function of alpha at center
    and alpha' at center. Similarly for neighbors.

    Let's implement this properly.
    """
    eps = 1e-7
    pts_a = np.array([xa - eps, xa, xa + eps])
    pts_b = np.array([xb - eps, xb, xb + eps])

    def init_log_alpha(pts):
        return np.array([np.log(get_f_g(y, l, omega)[1]) for y in pts], dtype=complex)

    def get_f(pts):
        return np.array([get_f_g(y, l, omega)[0] for y in pts], dtype=complex)

    log_a = init_log_alpha(pts_a)
    log_b = init_log_alpha(pts_b)
    f_a = get_f(pts_a)
    f_b = get_f(pts_b)

    THRESH = 1e300

    for k in range(N):
        # Step 1: exponentiate
        a = np.exp(log_a)  # alpha values at pts_a
        b = np.exp(log_b)  # alpha values at pts_b

        # Step 2: derivative of log for each side
        dlog_a = np.zeros(3, dtype=complex)
        dlog_b = np.zeros(3, dtype=complex)
        for s, (logs) in enumerate([log_a, log_b]):
            dlog_a[1] = (log_a[2] - log_a[0]) / (2 * eps)
            dlog_b[1] = (log_b[2] - log_b[0]) / (2 * eps)

        # dlog for all points: for i=0, use backward; for i=2, use forward
        # Actually for the derivative at center: only need center point
        # For neighbors: need derivative at ±eps which requires ±2*eps

        # Actually, the NEXT iteration needs alpha at neighbors, which needs
        # log_alpha at neighbors. log_alpha at neighbor i is:
        # log(alpha'(neighbor) + f(neighbor)*alpha(neighbor))
        # where alpha'(neighbor) = alpha[neighbor] * dlog[neighbor]
        # And dlog at neighbor requires log at neighbors' neighbors.
        # Since we only have 3 points, the leftmost needs a -eps beyond, which we don't have.

        # Compromise: use forward/backward differences at boundaries
        dlog_a = np.zeros(3, dtype=complex)
        dlog_b = np.zeros(3, dtype=complex)
        for side_idx, logs in enumerate([log_a, log_b]):
            dlog_s = np.zeros(3, dtype=complex)
            dlog_s[1] = (logs[2] - logs[0]) / (2 * eps)  # central
            dlog_s[0] = (logs[1] - logs[0]) / eps  # forward difference for left
            dlog_s[2] = (logs[2] - logs[1]) / eps  # backward difference for right
            if side_idx == 0:
                dlog_a = dlog_s
            else:
                dlog_b = dlog_s

        # Step 3: compute new alpha for each point
        a_new = np.zeros(3, dtype=complex)
        b_new = np.zeros(3, dtype=complex)
        for i in range(3):
            a_new[i] = a[i] * dlog_a[i] + f_a[i] * a[i]
            b_new[i] = b[i] * dlog_b[i] + f_b[i] * b[i]

        # Step 4: log with scale handling
        a_scale = [max(abs(v), 1e-300) for v in a_new]
        b_scale = [max(abs(v), 1e-300) for v in b_new]

        log_a_new = np.log(a_new / a_scale)  # log of unit-magnitude complex number

        # This doesn't work because we've lost the log-magnitude information.
        # Need to track log-magnitude separately.

        # FINALLY: separate log-magnitude and log-phase tracking.
        # mu_k = log|alpha_k| (real), theta_k = arg(alpha_k) (real)
        # Then alpha_k = exp(mu_k) * exp(i*theta_k) = |alpha_k| * e^{i*theta_k}

        # For derivatives:
        # alpha' = d/dy(exp(mu + i*theta)) = exp(mu + i*theta) * (d(mu+i*theta)/dy)
        # So: alpha' = alpha * (d(mu)/dy + i*d(theta)/dy)

        pass

    # Let me implement this properly with magnitude-phase separation
    return aim_magphase(omega, l, N, xa, xb)


def aim_magphase(omega, l, N=100, xa=0.3, xb=0.7):
    """
    AIM in log-magnitude + phase domain.
    Track: mu_i = log|alpha(y_i)|, theta_i = arg(alpha(y_i))
    for i = 0, 1, 2 (left, center, right).

    alpha = exp(mu) * e^{i*theta}
    alpha' = exp(mu + i*theta) * (mu' + i*theta')

    Then: alpha_new = alpha' + f * alpha = alpha * (mu' + i*theta' + f)
    log|alpha_new| = log|alpha| + log|mu' + i*theta' + f|
    arg(alpha_new) = arg(alpha) + arg(mu' + i*theta' + f)
    """
    eps = 5e-7

    pts_a = np.array([xa - eps, xa, xa + eps])
    pts_b = np.array([xb - eps, xb, xb + eps])

    def init_side(pts):
        g_vals = np.array([get_f_g(y, l, omega)[1] for y in pts], dtype=complex)
        mu = np.log(np.abs(g_vals))
        theta = np.angle(g_vals)
        f_vals = np.array([get_f_g(y, l, omega)[0] for y in pts], dtype=complex)
        return mu, theta, f_vals

    mu_a, theta_a, f_a = init_side(pts_a)
    mu_b, theta_b, f_b = init_side(pts_b)

    for k in range(N):
        # Derivatives: mu' and theta' at each point
        def central_diff(arr):
            result = np.zeros(3, dtype=float)
            result[1] = (arr[2] - arr[0]) / (2 * eps)  # central
            result[0] = (arr[1] - arr[0]) / eps  # forward
            result[2] = (arr[2] - arr[1]) / eps  # backward
            return result

        dmu_a = central_diff(mu_a)
        dtheta_a = central_diff(theta_a)
        dmu_b = central_diff(mu_b)
        dtheta_b = central_diff(theta_b)

        # alpha'(y) = alpha(y) * (dmu(y) + i*dtheta(y))
        # alpha_new(y) = alpha(y) * (dmu(y) + i*dtheta(y) + f(y))
        # log|alpha_new(y)| = log|alpha(y)| + log|dmu + i*dtheta + f(y)|
        # arg(alpha_new(y)) = arg(alpha(y)) + arg(dmu + i*dtheta + f(y))

        # At each point:
        def step(mu_s, theta_s, dmu_s, dtheta_s, f_s):
            # z = dmu + i*dtheta + f (complex)
            z = dmu_s + 1j * dtheta_s + f_s  # complex array
            log_z_abs = np.log(np.abs(z))
            log_z_arg = np.angle(z)

            # Check for zeros in z
            zero_mask = np.abs(z) < 1e-300
            log_z_abs = np.where(zero_mask, -690.0, log_z_abs)  # log(1e-300)
            log_z_arg = np.where(zero_mask, 0.0, log_z_arg)

            new_mu = mu_s + log_z_abs
            new_theta = theta_s + log_z_arg
            return new_mu, new_theta

        mu_a_new, theta_a_new = step(mu_a, theta_a, dmu_a, dtheta_a, f_a)
        mu_b_new, theta_b_new = step(mu_b, theta_b, dmu_b, dtheta_b, f_b)

        # Check for NaN/Inf in log-magnitude (from zeros or overflow)
        if np.any(np.isnan(mu_a_new)) or np.any(np.isnan(mu_b_new)):
            return np.inf, np.inf

        mu_a, theta_a = mu_a_new, theta_a_new
        mu_b, theta_b = mu_b_new, theta_b_new

    # Compute delta at the two locations (center points only)
    # delta_N = alpha_N' - f * alpha_N = alpha_N * (dlog_alpha_N - f) ... no
    # delta = alpha' - f * alpha = alpha * (mu' + i*theta' + f) ... wait that IS alpha' + f*alpha

    # Hmm, delta = alpha_N' - f*alpha_N
    # alpha_N' = alpha_N * (dmu[1] + i*dtheta[1])
    # delta = alpha_N * dmu[1] + i*dtheta[1] - f*alpha_N
    #       = alpha_N * (dmu[1] + i*dtheta[1] - f)

    dmu_a = central_diff_func(mu_a)
    dtheta_a = central_diff_func(theta_a)
    dmu_b = central_diff_func(mu_b)
    dtheta_b = central_diff_func(theta_b)

    # Hmm I forgot to define central_diff_func. Let me just redo this inline.
    dmu_ac = (mu_a[2] - mu_a[0]) / (2 * eps)
    dtheta_ac = (theta_a[2] - theta_a[0]) / (2 * eps)
    dmu_bc = (mu_b[2] - mu_b[0]) / (2 * eps)
    dtheta_bc = (theta_b[2] - theta_b[0]) / (2 * eps)

    alpha_a_center = np.exp(mu_a[1]) * np.exp(1j * theta_a[1])
    alpha_b_center = np.exp(mu_b[1]) * np.exp(1j * theta_b[1])

    delta_a = alpha_a_center * (dmu_ac + 1j * dtheta_ac - f_a[1])
    delta_b = alpha_b_center * (dmu_bc + 1j * dtheta_bc - f_b[1])

    return delta_a, delta_b


def central_diff_func(arr):
    return np.array([(arr[2] - arr[0]) / (2 * 5e-7), (arr[2] - arr[0]) / (2 * 5e-7), (arr[2] - arr[0]) / (2 * 5e-7)])


def main():
    print("=" * 70)
    print("Robust AIM Solver - Log Magnitude/Phase Formulation")
    print("=" * 70)

    l = 2
    ref = BERTI_REF[l]
    print(f"\nl={l}, reference: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

    # Test the log-mag/phase AIM
    print("\n=== Log-magnitude/phase AIM ===")

    for N in [60, 100, 140]:
        print(f"\nN={N}:")
        for dr in [0.0, 0.05, -0.05]:
            for di in [0.0, 0.02, -0.02]:
                w = ref + complex(dr, di)
                da, db = aim_magphase(w, l, N=N, xa=0.3, xb=0.7)
                diff = abs(da - db) if not np.isnan(da) and not np.isinf(da) else np.inf
                if diff < 1e20:
                    print(f"    w={w.real:.4f}-{abs(w.imag):.4f}i: |dA-dB| = {diff:.6e}")

    # Also test reference
    print("\n=== Reference value detailed scan ===")
    for N in [60, 80, 100]:
        da, db = aim_magphase(ref, l, N=N, xa=0.3, xb=0.7)
        print(f"  N={N}: delta_a = {da:.6e}, delta_b = {db:.6e}, |diff| = {abs(da-db):.6e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
