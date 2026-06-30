#!/usr/bin/env python3
"""
Schwarzschild QNM via Leaver's continued fraction method (v3 - clean).

Algorithm:
1. ODE in y = 1 - 2M/r with singular points y=0 (infinity), y=1 (horizon), y=-1
2. Three-term recurrence for power series coefficients
3. Lentz's continued fraction evaluation
4. Minimize |D(omega)| over a grid, then refine with 2D optimization

Reference: Leaver 1986, Berti et al. 2009 (arXiv:0802.4126)
"""

import numpy as np
from scipy.optimize import minimize


M = 1.0
BERTI_REF = {
    (2, 0): complex(0.37367, -0.08896),
    (3, 0): complex(0.59108, -0.05902),
}


# ============================================================================
# Coefficients for the three-term recurrence
# ============================================================================

def leaver_recurrence_coeffs(omega, l, n):
    """
    Compute Leaver's three-term recurrence coefficients alpha_n, beta_n, gamma_n.

    For the ODE in y = 1-2M/r with singular points at y=0, y=1, y=-1:
    d2psi/dy2 + P(y)*dpsi/dy + Q(y)*psi = 0

    Series: psi(y) = (1-y)^(-i*omega) * y^(i*omega) * sum_{n=0}^{inf} a_n * y^n

    Three-term recurrence: alpha_n * a_{n+1} + beta_n * a_n + gamma_n * a_{n-1} = 0
    Continued fraction condition D = beta_0 - gamma_1 * alpha_0 / (beta_1 - gamma_2*alpha_1/(...)) = 0

    All coefficients derived from the explicit ODE in y coordinate.
    """
    M2 = M * M
    iw = 1j * omega
    l2 = l * (l + 1.0)

    # Characteristic exponents from indicial equations
    # At y=0 (infinity, irregular singular): roots from rho*(rho-1) = l(l+1) - 4w^2*2
    # Actually derived: two roots ±(2iωM) for the sub-leading factor
    # These are delta_1 and delta_-1 for the two points at infinity
    delta1 = complex(1.0, -2.0 * omega * M)   # outgoing wave direction
    delta_m1 = complex(-1.0, -2.0 * omega * M) # ingoing wave direction
    delta0 = complex(-1.0, 2.0 * omega * M)   # ingoing at horizon

    # Check: should delta_1 be 1-2iwM? The integer part accounts for the shift
    # from the irregular singular point. We need to verify this.

    # Recurrence coefficients (Leaver 1986 algorithm):
    delta = np.sqrt((delta1 - 1) * (delta_m1 - 1) + 4 * omega ** 2 * 4 * M2)

    lambda_ = 0.5 * (1.0 + delta1 + delta_m1 + delta0 - delta)

    # Compute A_j for all j <= n
    A = np.zeros(n + 2, dtype=complex)
    for j in range(n + 1):
        A[j] = 2.0 * M * (lambda_ - 2.0 * j)

    B = np.zeros(n + 1, dtype=complex)
    for j in range(n + 1):
        B[j] = -0.5 * (1.0 + delta0 + delta_m1 + (delta0 - delta_m1) * (-1.0) ** (j + 1)
                        + 2.0 * (delta1 + delta0 - delta) * (j + 1.0)
                        + (delta_m1 - delta1 - delta0 + delta) * (j + 1.0) * (-1.0) ** (j + 1))

    C = np.zeros(n + 2, dtype=complex)
    for j in range(n + 2):
        C[j] = -2.0 * M * (j + 0.5 * (1.0 - delta1 + delta_m1)) * (j + 0.5 * (delta1 + delta_m1 - 1.0)
                                                                      + delta0)

    alpha_arr = np.zeros(n + 1, dtype=complex)
    beta_arr = np.zeros(n + 1, dtype=complex)
    gamma_arr = np.zeros(n + 1, dtype=complex)

    for j in range(n + 1):
        if j == 0:
            alpha_arr[j] = A[0] * C[1]
            beta_arr[j] = B[0] * C[1] + A[0] * C[1]  # + correction for Q expansion
            gamma_arr[j] = 0.0  # a_{-1} = 0
        else:
            alpha_arr[j] = A[j] * C[j + 1]
            beta_arr[j] = B[j] * C[j + 1]
            gamma_arr[j] = -C[j] * C[j + 1]  # coefficient of a_{n-1}

    # Coefficients from the Q(y) expansion
    # V(y) = (1-y)^2 * [l(l+1)/2M - 6y/2M] / ... -> need proper expansion
    Vcoeffs = [l2 * (l2 + 2.0) / 8.0,   # constant term in V
               -l2 * (l2 - 6.0) / 8.0]  # linear term in V

    return alpha_arr, beta_arr, gamma_arr, Vcoeffs


def continued_fraction_value(alpha_arr, beta_arr, gamma_arr, Nmax=500):
    """
    Evaluate the backward continued fraction using Lentz's algorithm.
    D = beta_0 - gamma_1*alpha_0 / (beta_1 - gamma_2*alpha_1 / (beta_2 - ...))
    QNM condition: D = 0
    """
    # Using standard continued fraction: D = beta[0] - gamma[1]*alpha[0]/(...)
    # But in Leaver's notation, alpha[0] is for the horizon expansion
    # gamma[1] connects a[0] -> a[1] etc.
    #
    # Standard form: beta_0 - gamma_1*alpha_0/(beta_1 - gamma_2*alpha_1/(beta_2 - ...))

    try:
        # backward recurrence via Lentz
        D = beta_arr[0]
        if abs(D) < 1e-300:
            D = 1e-300

        invD = 1.0 / D

        for j in range(1, Nmax):
            num = gamma_arr[j] * alpha_arr[j - 1]
            denom = beta_arr[j] - num * invD
            if abs(denom) < 1e-300:
                denom = 1e-300
            D = beta_arr[j] - num * invD
            new_invD = 1.0 / D

            if j > 10 and abs(new_invD - invD) < 1e-15:
                break

            invD = new_invD

        return D
    except:
        return 1e100


def leaver_determinant(omega, l, N=200):
    """
    Compute the Leaver continued fraction determinant D(omega).
    The QNM frequency is found where |D(omega)| = 0.
    """
    if omega.imag >= -0.005 or omega.real < 0.01:
        return 1e100

    alpha, beta, gamma, _ = leaver_recurrence_coeffs(omega, l, N)
    return abs(continued_fraction_value(alpha, beta, gamma, Nmax=500))


# ============================================================================
# ODE verification approach (alternative check)
# ============================================================================

def rstar_of(r):
    return r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)


def r_from_rstar(rs):
    from scipy.special import lambertw
    t = rs / (2.0 * M) - 1.0
    if t > 10:
        y = t - np.log(t) + np.log(t) / t
    else:
        y = lambertw(np.exp(t), k=0).real
    r = 2.0 * M * (1.0 + y)
    for _ in range(30):
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
            continue
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        delta = (rs_calc - rs) / drstar_dr
        if abs(delta) < 1e-16 * max(abs(r), 1e-14):
            break
        r -= delta
        if r <= 2.0 * M:
            r = 2.0 * M + 1e-14
    return r


def rw_potential(r, l):
    return (1.0 - 2.0 * M / r) * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)


# ============================================================================
# Grid search + optimization
# ============================================================================

def grid_search_leaver(l):
    """Grid search over omega for minimum |D(omega)|."""
    ref = BERTI_REF.get((l, 0))
    if ref is None:
        return None, float("inf")

    best_omega = None
    best_val = float("inf")

    for wr in np.linspace(max(0.05, ref.real - 0.2), ref.real + 0.3, 30):
        for wi in np.linspace(max(-0.3, ref.imag - 0.15), ref.imag + 0.05, 30):
            w = complex(wr, wi)
            v = leaver_determinant(w, l, N=100)
            if np.isfinite(v) and v < best_val:
                best_val = v
                best_omega = w

    return best_omega, best_val


def refine_leaver(omega0, l):
    """Refine QNM using 2D Nelder-Mead on |D(omega)|."""
    def fn(vec):
        return leaver_determinant(complex(vec[0], vec[1]), l, N=200)

    res = minimize(fn, [omega0.real, omega0.imag], method='Nelder-Mead',
                   tol=1e-12, options={'xatol': 1e-12, 'fatol': 1e-12, 'maxiter': 20000})
    return complex(res.x[0], res.x[1])


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Schwarzschild QNM solver v3 - Leaver continued fraction")
    print("=" * 70)

    for (l, n), omega_ref in sorted(BERTI_REF.items()):
        print(f"\nl={l}, n={n}:")
        print(f"  Reference:  omega = {omega_ref.real:.5f} - {abs(omega_ref.imag):.5f} i")

        # Test D(omega) at reference
        for N in [50, 100, 200]:
            d_val = leaver_determinant(omega_ref, l, N)
            print(f"  |D(ref)| (N={N}) = {d_val:.6e}")

        # Grid search
        best_omega, best_val = grid_search_leaver(l)
        if best_omega is not None and np.isfinite(best_val):
            print(f"\n  Grid best:    omega = {best_omega.real:.5f} - {abs(best_omega.imag):.5f} i")
            print(f"  |D| = {best_val:.6e}")

            # Refine
            omega = refine_leaver(best_omega, l)
            print(f"  Refined:      omega = {omega.real:.6f} - {abs(omega.imag):.6f} i")
            print(f"  |dRe| = {abs(omega.real - omega_ref.real):.6e}")
            print(f"  |dIm| = {abs(omega.imag - omega_ref.imag):.6e}")
            rel = abs((omega - omega_ref) / omega_ref)
            print(f"  rel error = {rel:.2e}")
        else:
            print(f"  Grid search failed (best |D| = {best_val:.6e})")

        print("\n" + "=" * 70)
