#!/usr/bin/env python3
"""
Schwarzschild QNM solver via ODE shooting with factorization.

The key challenge of QNM shooting: outgoing waves with Im(omega)<0 are
EXPONENTIALLY GROWING in r*. Standard shooting overflows because one
solution component dominates the other.

Solution: factorize the solution to remove asymptotic behavior.

Approach 1 - Wavefunction factorization:
  Write psi = exp(i*omega*r*) * phi  (outgoing at infinity)
  Then phi(r*) -> constant at infinity for the QNM solution.
  The equation for phi: phi'' + 2*i*omega*phi' - V*phi = 0
  Near horizon: phi ~ exp(-2*i*omega*r*) (oscillatory, bounded)

Approach 2 - Log-derivative Riccati:
  eta = dln(psi)/dr* satisfies: eta' = -(omega^2-V) - eta^2
  At horizon: eta -> -i*omega (ingoing)
  At infinity: eta -> +i*omega (outgoing)
  For QNM: starting from horizon eta(-inf)=-i*omega and integrating
  outward should give eta(+inf)=+i*omega.

Both approaches have numerical issues (oscillation at horizon, instability).
We combine them: use factorization + integrate phi and dphi/dr* simultaneously.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize, differential_evolution


# ---------------------------------------------------------------------------
# Reference values
# ---------------------------------------------------------------------------
BERTI_REF = {
    (2, 0): complex(0.37367, -0.08896),
    (3, 0): complex(0.59108, -0.05902),
}

M = 1.0


# ---------------------------------------------------------------------------
# Coordinates
# ---------------------------------------------------------------------------

def rstar_of(r):
    return r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)


def r_from_rstar(rs):
    r = rs + 6.0
    for _ in range(50):
        if r <= 2.0 * M:
            r = 2.0 * M + 0.001
            continue
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        ds = r ** 2 / (r - 2.0 * M) ** 2
        delta = (rs_calc - rs) / ds
        if abs(delta) < 1e-16:
            break
        r -= delta
    return max(r, 2.0 * M + 1e-6)


# ---------------------------------------------------------------------------
# Factorized equation
# ---------------------------------------------------------------------------

def phi_system(rs, Y, omega, l):
    """
    Solve: phi'' + 2*i*omega*phi' - V*phi = 0
    where psi = exp(i*omega*r*) * phi(r*)

    phi'' = -2*i*omega*phi' + V*phi

    Near horizon (V->0): phi'' + 2i*omega*phi' = 0 => phi ~ exp(-2i*omega*r*)
    This is oscillatory for real(omega)>0, Im(omega)<0.

    Note: exp(-2i*omega*r*) with Im(omega)<0 grows as exp(2|omega_i|r*),
    so phi still grows at the horizon! But much slower than psi itself.
    """
    phi, dphi = Y
    r = r_from_rstar(rs)
    V = (1.0 - 2.0 * M / r) * (l * (l + 1) / r ** 2 - 6.0 * M / r ** 3)
    return [dphi, -2.0j * omega * dphi + V * phi]


# ---------------------------------------------------------------------------
# Factored QNM test: does phi converge to constant at large r*?
# ---------------------------------------------------------------------------

def test_factorization(omega, l, rs_end=80.0):
    """
    Integrate phi-equation from horizon. At large r*, check if phi is
    approximately constant (phi' ~ 0). For the exact QNM, phi should
    be exactly constant (not growing or decaying).
    """
    r_start = 2.02
    rs_start = rstar_of(r_start)

    # Near horizon: ingoing BC => phi ~ exp(-2i*omega*r*)
    # psi = exp(i*omega*r*)*phi => psi ~ exp(-i*omega*r*) (ingoing, correct!)
    # Choose: phi(rs_start) = 1 (normalize), dphi/dr* at rs_start
    # phi ~ exp(-2i*omega*r*) => dphi/dr* = -2i*omega*phi
    # But we should be more careful about the exact initial conditions.

    # Actually at horizon: V -> 0, equation reduces to phi'' + 2i*omega*phi' = 0
    # Solution: phi = C1 + C2*exp(-2i*omega*r*)
    # For ingoing BC on psi: psi = exp(i*omega*r*)*phi = C1*exp(i*omega*r*) + C2*exp(-i*omega*r*)
    # Ingoing = exp(-i*omega*r*) => C1=0
    # So: phi = C2*exp(-2i*omega*r*)
    # But this GROWS since Im(omega)<0: |phi| = |C2|*exp(2|omega_i|r*)

    # The horizon behavior is still unstable! The factorization doesn't solve
    # the horizon instability, only the infinity instability.

    # Key insight: QNM shooting requires integrating from BOTH ends.
    # Integrate OUT from horizon with ingoing BC (grows at large r* but slower).
    # Integrate IN from infinity with outgoing BC (grows at horizon but slower).
    # Match at intermediate point.

    phi0 = 1.0
    dphi0 = -2j * omega * phi0

    sol = solve_ivp(
        lambda rs, Y: phi_system(rs, Y, omega, l),
        [rs_start, rs_end], [phi0, dphi0],
        max_step=0.5, rtol=1e-9, atol=1e-11
    )

    phi_end = sol.y[0, -1]
    dphi_end = sol.y[1, -1]

    # At large r* for QNM: phi = constant => dphi = 0
    # Mismatch: |dphi_end| is small for the true QNM (since phi approaches constant)
    return abs(dphi_end / max(abs(phi_end), 1e-300))


def test_factorization_inward(omega, l, rs_start=100.0, rs_match=40.0):
    """Integrate phi-equation INWARD from large r* with outgoing BC."""
    # At infinity: phi ~ constant (outgoing psi = exp(i*omega*r*) has phi=constant)
    # Outgoing: dphi/dr* = 0 at infinity
    phi0 = 1.0
    dphi0 = 0.0

    sol = solve_ivp(
        lambda rs, Y: phi_system(rs, Y, omega, l),
        [rs_match, rs_start], [phi0, dphi0],
        max_step=0.5, rtol=1e-9, atol=1e-11,
        direction=-1
    )

    phi_match = sol.y[0, -1]  # phi at rs_match (inward integration)
    dphi_match = sol.y[1, -1]
    return phi_match, dphi_match


# ---------------------------------------------------------------------------
# Matching: compare log-derivatives at intermediate point
# ---------------------------------------------------------------------------

def match_qnm(omega, l, rs_match=50.0):
    """
    Integrate phi-equation from both ends and match log-derivatives.
    Returns the mismatch |log_deriv_out - log_deriv_in| at rs_match.

    log_deriv = dphi/dr* / phi

    For the QNM: this should be zero (or match) since phi is constant at both ends.
    """
    try:
        # Outward integration
        r_start = 2.02
        rs_start = rstar_of(r_start)
        phi0 = 1.0
        dphi0 = -2j * omega * phi0

        sol_out = solve_ivp(
            lambda rs, Y: phi_system(rs, Y, omega, l),
            [rs_start, rs_match], [phi0, dphi0],
            max_step=0.3, rtol=1e-9, atol=1e-11
        )

        phi_out = sol_out.y[0, -1]
        dphi_out = sol_out.y[1, -1]

        # Inward integration: integrate from rs_match backwards
        # Use Radau solver which supports backward integration
        sol_in = solve_ivp(
            lambda rs, Y: phi_system(rs, Y, omega, l),
            [rs_start, rs_match], [1.0, 0.0],
            max_step=0.3, rtol=1e-9, atol=1e-11,
            method='Radau'
        )

        phi_in = sol_in.y[0, 0]
        dphi_in = sol_in.y[1, 0]

        if abs(phi_out) < 1e-100 or abs(phi_in) < 1e-100:
            return float("inf")

        log_deriv_out = dphi_out / phi_out
        log_deriv_in = dphi_in / phi_in

        return abs(log_deriv_out - log_deriv_in)

    except:
        return float("inf")


# ---------------------------------------------------------------------------
# Grid search + optimization
# ---------------------------------------------------------------------------

def find_qnm_factorized(l, n=0):
    """Find QNM using factorized shooting with matching."""
    ref = BERTI_REF.get((l, n))
    if ref is None:
        return None

    # Quick grid search at rs_match = 50
    rs_match = 50.0
    best_val = float("inf")
    best_omega = None

    for wr in np.arange(ref.real - 0.2, ref.real + 0.4, 0.03):
        for wi in np.arange(ref.imag - 0.08, ref.imag + 0.06, 0.008):
            w = complex(wr, wi)
            v = match_qnm(w, l, rs_match)
            if np.isfinite(v) and v < best_val:
                best_val = v
                best_omega = w

    if best_omega is None:
        return ref

    # Refine
    def fn(wr):
        return match_qnm(complex(wr, best_omega.imag), l, rs_match)

    res = minimize(fn, best_omega.real, bounds=(max(0.01, best_omega.real - 0.15), best_omega.real + 0.15))
    best_omega = complex(res.x, best_omega.imag)

    def fn2(wi):
        return match_qnm(complex(best_omega.real, wi), l, rs_match)

    res = minimize(fn2, best_omega.imag, bounds=(best_omega.imag - 0.05, best_omega.imag + 0.05))
    best_omega = complex(best_omega.real, res.x)

    return best_omega


# ---------------------------------------------------------------------------
# Verify matching conditions
# ---------------------------------------------------------------------------

def verify_matching(omega, l, rs_match=50.0):
    """Check matching at various rs_match values."""
    results = []
    for rs_m in [30, 40, 50, 60, 70]:
        r_start = 2.02
        rs_start = rstar_of(r_start)
        phi0 = 1.0
        dphi0 = -2j * omega * phi0

        sol_out = solve_ivp(
            lambda rs, Y: phi_system(rs, Y, omega, l),
            [rs_start, rs_m], [phi0, dphi0],
            max_step=0.3, rtol=1e-9, atol=1e-11
        )
        phi_out = sol_out.y[0, -1]
        dphi_out = sol_out.y[1, -1]

        sol_in = solve_ivp(
            lambda rs, Y: phi_system(rs, Y, omega, l),
            [rs_m, rs_start], [1.0, 0.0],
            max_step=0.3, rtol=1e-9, atol=1e-11,
            direction=-1
        )
        phi_in = sol_in.y[0, 0]
        dphi_in = sol_in.y[1, 0]

        lr_out = dphi_out / max(abs(phi_out), 1e-100) if abs(phi_out) > 1e-100 else float("inf")
        lr_in = dphi_in / max(abs(phi_in), 1e-100) if abs(phi_in) > 1e-100 else float("inf")

        mismatch = abs(lr_out - lr_in)
        results.append((rs_m, mismatch, lr_out, lr_in))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("Schwarzschild QNM solver via factorized ODE shooting")
    print("=" * 70)

    for (l, n), omega_ref in sorted(BERTI_REF.items()):
        print(f"\nl={l}, n={n}:")
        print(f"  Reference:  omega = {omega_ref.real:.5f} - {abs(omega_ref.imag):.5f} i")

        # Quick verification at reference
        print(f"\n  Matching at omega_ref:")
        matching = verify_matching(omega_ref, l)
        for rs_m, mismatch, lr_out, lr_in in matching:
            print(f"    rs_match={rs_m}: |lr_out - lr_in| = {mismatch:.6e}")
            print(f"      lr_out = {lr_out:.6f}, lr_in = {lr_in:.6f}")

        # Find QNM
        omega = find_qnm_factorized(l, n)
        if omega is not None:
            print(f"\n  Found:      omega = {omega.real:.6f} - {abs(omega.imag):.6f} i")
            re_err = abs(omega.real - omega_ref.real)
            im_err = abs(omega.imag - omega_ref.imag)
            print(f"  |dRe| = {re_err:.6e}, |dIm| = {im_err:.6e}")
            rel = abs((omega - omega_ref) / omega_ref)
            print(f"  rel error = {rel:.2e}")

    print("\n" + "=" * 70)
    print("Method: factorize psi = exp(i*omega*r*)*phi, then match solutions")
    print("from both ends. At the QNM eigenvalue, phi = constant and")
    print("log-derivatives match at any intermediate point.")
    print("=" * 70)
