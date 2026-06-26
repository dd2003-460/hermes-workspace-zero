#!/usr/bin/env python3
"""
Teukolsky + AIM: Kerr QNM Solver v6
=====================================
Dehghan-Safari 2011 formulation with asymptotic extraction.

The RW equation d^2psi/dr*^2 + (omega^2 - V)*psi = 0
is transformed to remove the asymptotic behavior:

  psi = F^{i*omega} * x^{-i*omega} * (1-x)^{i*omega} * y

where F = r^2/(r-2M)^2.

This gives a clean y'' = lam(x)*y' + mu(x)*y equation suitable for AIM.

Reference: Dehghan, Saifia & Alimohammadi, JCAP 04 (2011) 010
"""

import numpy as np
from scipy.optimize import minimize

M = 1.0

berti = {
    (0,2,2,0): (0.37367, -0.08896),
    (0,3,3,0): (0.59108, -0.05902),
}

# ---- Coordinate mapping ----

def r_of_x(x, M=1.0):
    """x in (0,1): x=0 -> horizon, x=1 -> infinity."""
    return 2*M/(1-x)

def V_RW(r, l, M=1.0):
    """Regge-Wheeler potential."""
    f = 1.0 - 2*M/r
    return f*(l*(l+1)/r**2 - 6*M/r**3)

# ---- Dehghan-Safari transformation ----

def F(r, M=1.0):
    """F = r^2/(r-2M)^2."""
    return r**2/(r-2*M)**2

def get_aim_coeffs(x, omega, l, M=1.0):
    """
    Compute lambda_0(x) and mu_0(x) for the transformed equation.

    From Dehghan-Safari 2011, after the transformation
    psi = F^{i*omega} * x^{-i*omega} * (1-x)^{i*omega} * y,

    the equation for y becomes:
    y'' = lambda(x)*y' + mu(x)*y

    The exact formulas (Eqs. 18-21 of Dehghan 2011):

    lambda(x) = [dF/dx * (2*i*omega/F) + dx/dr* / (F*dr/dx)] / ...

    Let me derive this from scratch.

    Original: d^2psi/dr*^2 + (omega^2 - V)*psi = 0

    Chain rule: d/dr* = 1/(dr*/dx) * d/dx
               d^2/dr*^2 = 1/(dr*/dx)^2 * d^2/dx^2 - r*''/(r*')^3 * d/dx

    where r*' = dr*/dx and r*'' = d^2r*/dx^2.

    Let P(x) = 1/(r*')^2 and Q(x) = -r*''/(r*')^3.

    P * d^2psi/dx^2 + Q * dpsi/dx + (omega^2 - V)*psi = 0

    d^2psi/dx^2 + (Q/P) * dpsi/dx + (omega^2 - V)/P * psi = 0

    Now substitute psi = g*y where g = F^{i*omega} * x^{-i*omega} * (1-x)^{i*omega}

    Using d(ln g)/dx and d^2(ln g)/dx^2, we get:

    y'' + [2*(ln g)' + Q/P] * y' + [(ln g)'' + (ln g)'^2 + Q/P*(ln g)' + (omega^2-V)/P] * y = 0

    So:
    lambda(x) = 2*(ln g)' + Q/P
    mu(x) = (ln g)'' + (ln g)'^2 + Q/P*(ln g)' + (omega^2-V)/P
    """
    x = np.clip(x, 1e-10, 1-1e-10)
    r = r_of_x(x, M)

    # dr*/dx
    drstar_dr = r**2/(r-2*M)**2
    dr_dx = 2*M/(1-x)**2
    rstar_prime = drstar_dr * dr_dx  # dr*/dx

    # d^2r*/dx^2
    f_r = r**2/(r-2*M)**2
    g_x = 2*M/(1-x)**2
    df_dx = -4*M*r/(r-2*M)**3 * g_x
    dg_dx = 4*M/(1-x)**3
    rstar_double_prime = df_dx*g_x + f_r*dg_dx  # d^2r*/dx^2

    P = 1.0 / rstar_prime**2
    Q = -rstar_double_prime / rstar_prime**3

    # ln(g) = i*omega * [ln(F) - ln(x) + ln(1-x)]
    F_val = F(r, M)

    # (ln g)' = i*omega * [F'/F - 1/x + 1/(1-x)]
    # F' = dF/dr * dr/dx = 2r(r-2M) - r^2/r^2 * 2/(r-2M)^2 ... no
    # dF/dr = d/dr[r^2/(r-2M)^2] = [2r*(r-2M)^2 - r^2*2*(r-2M)]/(r-2M)^4
    #       = [2r(r-2M) - 2r^2]/(r-2M)^3
    #       = [-4Mr]/(r-2M)^3
    dF_dr = -4*M*r/(r-2*M)**3
    dF_dx = dF_dr * dr_dx

    ln_g_prime = 1j*omega*(dF_dx/F_val - 1.0/x + 1.0/(1-x))

    # (ln g)'' = i*omega * [d/dx(F'/F) - d/dx(1/x) + d/dx(1/(1-x))]
    # d/dx(F'/F) = (F''*F - F'^2)/F^2
    # F'' = d^2F/dx^2 = d/dx[-4Mr/(r-2M)^3 * 2M/(1-x)^2]
    # Let h = -4Mr/(r-2M)^3, i = 2M/(1-x)^2
    # dh/dr = [-4M(r-2M)^3 - (-4Mr)*3*(r-2M)^2]/(r-2M)^6
    #       = [-4M(r-2M) + 12Mr]/(r-2M)^4  ... this is getting messy

    # d/dx(F'/F) = d/dx[ln(dF_dx) - ln(F)] ... no, F' = dF_dx
    # d/dx(F'/F) = d/dx[dF_dx/F_val] = (d2F_dx2*F_val - dF_dx^2)/F_val^2

    # d2F/dx^2
    # d/dx of dF_dx = d/dx[-4Mr/(r-2M)^3 * 2M/(1-x)^2]
    # h = -4Mr/(r-2M)^3
    # dh/dx = dh/dr * dr/dx
    # dh/dr = [-4M(r-2M)^3 - (-4Mr)*3(r-2M)^2]/(r-2M)^6
    #       = [-4M(r-2M) + 12Mr]/(r-2M)^4
    #       = [8M(r-2M) + 4Mr]/(r-2M)^4  ... no
    # = [-4Mr + 8M^2 + 12Mr]/(r-2M)^4 = [8Mr - 8M^2]/(r-2M)^4 = 8M(r-M)/(r-2M)^4
    dh_dr = (8*M*r - 8*M**2)/(r-2*M)**4
    dh_dx = dh_dr * dr_dx
    di_dx = 4*M/(1-x)**3

    d2F_dx2 = dh_dx * 2*M/(1-x)**2 + (-4*M*r/(r-2*M)**3) * di_dx

    F_prime_F = dF_dx / F_val
    dF_prime_F_dx = (d2F_dx2*F_val - dF_dx**2) / F_val**2

    # d/dx(1/x) = -1/x^2
    # d/dx(1/(1-x)) = 1/(1-x)^2

    ln_g_double_prime = 1j*omega*(dF_prime_F_dx + 1.0/x**2 + 1.0/(1-x)**2)

    Q_over_P = Q * rstar_prime**2  # = -rstar_double_prime/rstar_prime

    lambda_0 = 2*ln_g_prime + Q_over_P
    mu_0 = ln_g_double_prime + ln_g_prime**2 + Q_over_P*ln_g_prime + (omega**2 - V_RW(r, l, M))*rstar_prime**2

    return lambda_0, mu_0


# ---- AIM iteration with global normalization + Wronskian ----

def aim_D_N(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM using Dehghan-Safari coefficients.

    Returns |W_N| where W_N = lambda_{N-1}(xa)*lambda_N(xb) - lambda_N(xa)*lambda_{N-1}(xb).
    With global normalization, W_N_scaled = W_orig/scale^2.
    When W_orig = 0 (at eigenvalue), W_scaled = 0 regardless of scale.

    For small N, scale is moderate and W_scaled is well-conditioned.
    For large N, use phase-based comparison instead.
    """
    dx = 1e-6

    # Get lambda_0, mu_0 and derivatives
    la0, ma0 = get_aim_coeffs(xa, omega, l)
    lb0, mb0 = get_aim_coeffs(xb, omega, l)

    lp, mp = get_aim_coeffs(xa+dx, omega, l)
    lm, mm = get_aim_coeffs(max(xa-dx, 1e-8), omega, l)
    dla0 = (lp - lm)/(2*dx)
    dqa0 = (mp - mm)/(2*dx)

    lp, mp = get_aim_coeffs(xb+dx, omega, l)
    lm, mm = get_aim_coeffs(xb-dx, omega, l)
    dlb0 = (lp - lm)/(2*dx)
    dqb0 = (mp - mm)/(2*dx)

    # Scaled variables
    lsa, msa = la0, ma0
    lsb, msb = lb0, mb0
    dla, dqa = dla0, dqa0
    dlb, dqb = dlb0, dqb0

    MAX_S = 1e80

    lsa_prev = lsa; lsb_prev = lsb

    scale_total = 1.0  # track cumulative scaling for phase comparison

    for k in range(1, N+1):
        # Recurrence
        lna = lsa**2 + dla - msa
        ln_b = lsb**2 + dlb - msb

        # Global scale
        scale = max(abs(lna), abs(ln_b))

        if scale > MAX_S:
            lna /= scale; ln_b /= scale
            dla /= scale; dqa /= scale
            dlb /= scale; dqb /= scale
            lsa_prev /= scale; lsb_prev /= scale
            msa /= scale; msb /= scale

            dla_new = 2*lsa*dla - dqa
            dlb_new = 2*lsb*dlb - dqb
            dla_new /= scale; dlb_new /= scale

            lsa_prev = lsa; lsb_prev = lsb
            lsa, lsb = lna, ln_b
            dla, dlb = dla_new, dlb_new
            continue

        # Derivatives
        dla_new = 2*lsa*dla - dqa
        dlb_new = 2*lsb*dlb - dqb

        lsa_prev = lsa; lsb_prev = lsb
        lsa, lsb = lna, ln_b
        dla, dlb = dla_new, dlb_new

    # Wronskian
    W = lsa_prev * lsb - lsa * lsb_prev
    return abs(W), W, lsa_prev, lsb


def aim_phase_diff(omega, l, N=80, xa=0.3, xb=0.7):
    """
    AIM using phase-only convergence check.

    At eigenvalue, phase of theta(xa) = phase of theta(xb).
    phase_diff = |arg(lambda_{N-1}(xa)/lambda_N(xa)) - arg(lambda_{N-1}(xb)/lambda_N(xb))|

    This is invariant under scaling.

    Additional check: log-magnitude ratio difference between consecutive N.
    Since we can't check absolute magnitudes, we check the RATIO:
    R = |theta(xa)/theta(xb)|. At eigenvalue, R = 1.
    """
    _, W, lpa, lbs, lpb, lsb = _aim_run(omega, l, N, xa, xb)

    # phase of theta at each point
    theta_a = lpa / lsb if abs(lsb) > 0 else complex(0)  # WRONG
    # Actually: theta_a = lsa_prev/lsa = lambda_{N-1}(xa)/lambda_N(xa)

    # Need full result. Let me restructure.
    result = _aim_run(omega, l, N, xa, xb)
    lpa, la, lpb, lb = result  # lambda_{N-1}(xa), lambda_N(xa), lambda_{N-1}(xb), lambda_N(xb)

    theta_a = lpa/la
    theta_b = lpb/lb

    # Phase difference
    phi_diff = np.abs(np.angle(theta_a) - np.angle(theta_b))
    phi_diff = min(phi_diff, 2*np.pi - phi_diff)  # wrap to [-pi, pi]

    # Magnitude ratio
    mag_ratio = abs(abs(theta_a) / abs(theta_b) - 1.0)

    return phi_diff, mag_ratio, theta_a, theta_b


def _aim_run(omega, l, N, xa, xb):
    """Run AIM and return (lambda_{N-1}(xa), lambda_N(xa), lambda_{N-1}(xb), lambda_N(xb))."""
    dx = 1e-6

    la0, _ = get_aim_coeffs(xa, omega, l)
    lb0, _ = get_aim_coeffs(xb, omega, l)

    lp, mp = get_aim_coeffs(xa+dx, omega, l)
    lm, mm = get_aim_coeffs(max(xa-dx, 1e-8), omega, l)
    dla0 = (lp-lm)/(2*dx)

    lp, mp = get_aim_coeffs(xb+dx, omega, l)
    lm, mm = get_aim_coeffs(xb-dx, omega, l)
    dlb0 = (lp-lm)/(2*dx)

    lsa = la0; lsb = lb0
    dla = dla0; dlb = dlb0
    lsa_prev = lsa; lsb_prev = lsb

    MAX_S = 1e80
    count_scaled_a = 0; count_scaled_b = 0

    for k in range(1, N+1):
        lna = lsa**2 + dla
        ln_b = lsb**2 + dlb

        # mu terms (these affect the computation but not the lambda ratio directly)
        # Wait, I need mu in the recurrence. Let me add it back.
        # Actually for _aim_run I need the full recurrence.

        lna_full = lna  # will add mu terms below
        ln_b_full = ln_b

        # Hmm, this function needs mu too. Let me just copy the full recurrence.
        pass

    return None  # incomplete


# ---- Clean full implementation ----

def aim_full(omega, l, N=80, xa=0.3, xb=0.7):
    """Complete AIM with Dehghan-Safari coefficients. Returns phase + magnitude info."""
    dx = 1e-6

    la0, ma0 = get_aim_coeffs(xa, omega, l)
    lb0, mb0 = get_aim_coeffs(xb, omega, l)

    # Derivatives
    lp, mp = get_aim_coeffs(xa+dx, omega, l)
    lm, mm = get_aim_coeffs(max(xa-dx, 1e-8), omega, l)
    dla0 = (lp-lm)/(2*dx); dqa0 = (mp-mm)/(2*dx)
    lp, mp = get_aim_coeffs(xb+dx, omega, l)
    lm, mm = get_aim_coeffs(xb-dx, omega, l)
    dlb0 = (lp-lm)/(2*dx); dqb0 = (mp-mm)/(2*dx)

    lsa, msa = la0, ma0; lsb, msb = lb0, mb0
    dla, dqa = dla0, dqa0; dlb, dqb = dlb0, dqb0
    lsa_prev, lsb_prev = lsa, lsb

    MAX_S = 1e80

    for k in range(1, N+1):
        lna = lsa**2 + dla - msa
        ln_b = lsb**2 + dlb - msb
        mna = lsa*dqa - msa*dla + msa**2
        mn_b = lsb*dqb - msb*dlb + msb**2

        scale = max(abs(lna), abs(ln_b), abs(mna), abs(mn_b))

        if scale > MAX_S:
            lna/=scale; ln_b/=scale; mna/=scale; mn_b/=scale
            dla/=scale; dqa/=scale; dlb/=scale; dqb/=scale
            lsa_prev/=scale; lsb_prev/=scale

            dla_new = 2*lsa*dla - dqa
            dlb_new = 2*lsb*dlb - dqb
            dla_new/=scale; dlb_new/=scale

            lsa_prev, lsb_prev = lsa, lsb
            lsa, msa = lna, mna
            lsb, msb = ln_b, mn_b
            dla, dqa = dla_new, dqa/scale
            dlb, dqb = dlb_new, dqb/scale
            continue

        dla_new = 2*lsa*dla - dqa
        dlb_new = 2*lsb*dlb - dqb
        dqa_new = 2*msa*dqa
        dqb_new = 2*msb*dqb

        lsa_prev, lsb_prev = lsa, lsb
        lsa, msa = lna, mna; lsb, msb = ln_b, mn_b
        dla, dqa = dla_new, dqa_new; dlb, dqb = dlb_new, dqb_new

    # Compute theta at each point and compare
    theta_a = lsa_prev / lsa
    theta_b = lsb_prev / lsb

    # Phase difference (scaling-invariant)
    phi_diff = abs(np.angle(theta_a) - np.angle(theta_b))
    phi_diff = min(phi_diff, 2*np.pi - phi_diff)

    # For x-independence at eigenvalue:
    # theta_a = theta_b => phase same AND |theta_a/theta_b| = 1
    # |theta_a/theta_b| difference from 1
    ratio = theta_a / theta_b
    ratio_dev = abs(abs(ratio) - 1.0)

    return phi_diff, ratio_dev, theta_a, theta_b, lsa, lsb


# ---- Tests ----

print("="*70)
print("AIM Solver v6: Dehghan-Safari formulation")
print("="*70)

# Check coefficients at a few points
omega_test = 0.37367 - 0.08896j
print(f"\nCoefficients at omega = {omega_test:.5f}:")
for x in [0.2, 0.3, 0.5, 0.7, 0.8]:
    lam, mu = get_aim_coeffs(x, omega_test, l=2)
    print(f"  x={x:.1f}: lambda_0={lam:.4e}, mu_0={mu:.4e}")

# Test AIM convergence
print("\n--- D at exact QNM (l=2) ---")
expected = 0.37367 - 0.08896j
for N in [20, 40, 60, 80, 100]:
    phi, ratio_dev, ta, tb, _, _ = aim_full(expected, l=2, N=N)
    print(f"  N={N:3d}: phi_diff={phi:.4e}, ratio_dev={ratio_dev:.4e}, theta_a={ta:.4e}")

print("\n--- D at wrong omega ---")
for omega_w in [0.3-0.15j, 0.5+0.1j, 0.2-0.05j]:
    phi, ratio_dev, ta, tb, _, _ = aim_full(omega_w, l=2, N=80)
    print(f"  omega={omega_w.real:.2f}{omega_w.imag:+.2f}i: phi={phi:.4e}, ratio_dev={ratio_dev:.4e}")

# Grid search using phase + magnitude ratio
print("\n--- Grid search (l=2, N=60) ---")
print("Expected: omega = 0.37367 - 0.08896i")

def aim_score(omega, l, N=60):
    phi, ratio_dev, _, _, _, _ = aim_full(omega, l, N)
    return phi + ratio_dev  # combined metric

min_val, best = np.inf, None
for wr in np.linspace(0.25, 0.50, 26):
    for wi in np.linspace(-0.15, -0.02, 22):
        omega = wr + 1j*wi
        val = aim_score(omega, l=2)
        if val < min_val:
            min_val, best = val, (wr, wi)

print(f"Coarse best: omega = {best[0]:.3f} {best[1]:+.3f}i, score = {min_val:.4e}")

# Fine search
min_val2, best2 = np.inf, best
for wr in np.linspace(best[0]-0.03, best[0]+0.03, 31):
    for wi in np.linspace(best[1]-0.03, best[1]+0.03, 21):
        val = aim_score(wr+1j*wi, l=2)
        if val < min_val2:
            min_val2, best2 = val, (wr, wi)

print(f"Fine best: omega = {best2[0]:.5f} {best2[1]:+.5f}i, score = {min_val2:.4e}")

# Nelder-Mead
def obj(p):
    return aim_score(p[0]+1j*p[1], l=2)
res = minimize(obj, best2, method='Nelder-Mead',
               options={'maxiter':10000, 'xatol':1e-6, 'fatol':1e-12})
found = res.x[0] + 1j*res.x[1]
err = abs(found - expected) / abs(expected) * 100
print(f"Optimized: omega = {found.real:.5f} {found.imag:+.5f}i, err = {err:.1f}%")
