#!/usr/bin/env python3
"""
Wide frequency scan to locate QNM eigenvalues.
Use the y = 1-2M/r coordinate ODE directly to avoid r_from_rstar issues.

ODE in y: d²ψ/dy² + P(y)·dψ/dy + Q(y)·ψ = 0
P(y) = 2(2y-1) / [y(y-1)]
Q(y) = [4M²ω² - y(y-1)²(l(l+1)+3y-3)] / [y⁴(y-1)⁴]

Horizon: y → 0, with ingoing BC: ψ ~ y^(-2iMω)
Infinity: y → 1, with outgoing BC: ψ ~ (1-y)^(-2iMω) * exp(2iMω/(1-y))

We factor out asymptotic behavior and solve for the regular function φ(y).
"""

import numpy as np
from scipy.integrate import solve_ivp

M = 1.0
BERTI_REF = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def P(y):
    """P(y) = 2(2y-1) / [y(y-1)]"""
    y = np.clip(y, 1e-15, 1.0 - 1e-15)
    return 2.0 * (2.0 * y - 1.0) / (y * (y - 1.0))


def Q(y, omega, l):
    """Q(y) = [4ω² - y(1-y)²(l(l+1)+3y-3)] / [y⁴(1-y)⁴]"""
    y = np.clip(y, 1e-15, 1.0 - 1e-15)
    V_part = y * (1.0 - y)**2 * (l * (l + 1.0) + 3.0 * y - 3.0)
    Q_val = (4.0 * omega**2 - V_part) / (y**4 * (1.0 - y)**4)
    return Q_val


def solve_y_boundary(omega, l, direction, y_start, y_end, y_match, factored=True):
    """
    Integrate the ODE from y_start to y_end.
    direction: 'from_horizon' or 'from_infinity'
    factored: True = solve for factored phi (removes asymptotic behavior)

    ODE: d²ψ/dy² + P·dψ/dy + Q·ψ = 0
    """
    # With factoring: ψ(y) = y^rho * (1-y)^rho * exp(2iω/(1-y)) * φ(y)
    # where rho = -2iω

    rho = -2j * omega  # from y ~ exp(-iω*r*) analysis at horizon

    def ydot(phi, y, factored):
        """Compute dφ/dy and d²φ/dy² from ODE."""
        f_val = phi[1]
        # For factored: psi = A(y)*phi, where A = y^rho * (1-y)^rho * exp(2i*omega/(1-y))
        # psi' = A'*phi + A*phi'
        # psi'' = A''*phi + 2*A'*phi' + A*phi''
        # Substituting into ODE and solving for phi''...
        # This is complex. Let me solve for psi directly (unfactored) first.

        # ODE: phi'' + P*phi' + Q*phi = 0
        phi0 = phi[0]
        phi1 = phi[1]
        return [phi1, -P(y) * phi1 - Q(y, omega, l) * phi0]

    def make_ode(phi_func):
        return lambda y, phi: phi_func(phi, y, factored)

    # Get initial conditions
    if direction == 'from_horizon':
        if factored:
            # Near y=0: psi ~ y^rho = y^(-2iω)
            # phi = psi / [y^rho * (1-y)^rho * exp(2iω/(1-y))]
            # At y=y_start (near 0): phi ~ 1
            # phi' / phi = psi'/psi - d[ln(A)]/dy
            # psi'/psi = rho/y
            # d[ln(A)]/dy = rho/y + rho/(y-1) - 2iω/(1-y)²
            # = rho/y + (-rho + 2iω)/(y-1)
            # rho/(y-1) - 2iω/(1-y)² = rho/(y-1) - 2iω/(1-y)²
            # With rho = -2iω: rho/(y-1) = 2iω/(1-y)
            # So: dlnA/dy = rho/y + 2iω/(1-y) - 2iω/(1-y)²
            # = rho/y + 2iω[1/(1-y) - 1/(1-y)²]
            # = rho/y - 2iω/(1-y)²
            # phi'/phi = rho/y - (rho/y - 2iω/(1-y)²) = 2iω/(1-y)²
            # At small y: phi' = phi * 2iω ≈ -4*omega²

            phi0 = 1.0
            # phi' at small y
            dy0 = 2j * omega / (1.0 - y_start)**2
            phi1_init = dy0  # * phi0
            phi_y = [phi0, phi1_init]
        else:
            # psi ~ y^(-2iω)
            # dpsi/dy = (-2iω)/y * psi = rho/y * psi
            phi_y = [1.0, rho / y_start]  # phi[0]=1

        dpsi_phi0 = phi_y
    elif direction == 'from_infinity':
        if factored:
            # At y=1: similar factorization
            phi0 = 1.0
            # Need to compute the derivative condition
            dy0 = -2j * omega / (1.0 - y_start)**2  # sign flipped
            phi1_init = dy0
            phi_y = [phi0, phi1_init]
        else:
            # ψ ~ (1-y)^(-2iω) * exp(2iω/(1-y))
            # dψ/dy = ψ * [2iω/(1-y)² + 2iω/(1-y)]
            dpsi = 2j * omega / (1.0 - y_start) + 2j * omega / (1.0 - y_start)**2
            phi_y = [1.0, dpsi]

    sol = solve_ivp(
        make_ode(ydot),
        [y_start, y_end] if direction == 'from_horizon' else [y_end, y_start],
        phi_y,
        rtol=1e-10, atol=1e-12,
        dense_output=True,
        max_step=0.01
    )

    return sol


def wronskian_y(omega, l, y_start=0.01, y_end=0.99, y_match=0.5):
    """
    Compute Wronskian of two solutions at y_match.
    Solution 1: integrate from horizon (y_start) to y_match
    Solution 2: integrate from infinity (y_end) to y_match
    """
    def try_solve(omega, l, direction, y_s, y_e):
        rho = -2j * omega

        def deriv(y, Y):
            phi0, phi1 = Y
            p_val = P(y)
            q_val = Q(y, omega, l)
            return [phi1, -p_val * phi1 - q_val * phi0]

        # Initial conditions
        if direction == 'from_horizon':
            Y0 = [1.0, rho / y_s]
        else:
            # At y = 0.99: approaching infinity
            # ψ ~ (1-y)^(-2iω) for the factorized part
            # Factor out exp(2iω/(1-y)) and (1-y)^rho
            # Using unfactored psi
            factor = 2j * omega / (1.0 - y_s)
            dpsi = (factor + 2j * omega / (1.0 - y_s)**2)
            Y0 = [1.0, dpsi]

        if direction == 'from_horizon':
            sol = solve_ivp(deriv, [y_s, y_e], Y0, rtol=1e-10, atol=1e-12, max_step=0.005)
        else:
            sol = solve_ivp(deriv, [y_e, y_s], Y0, rtol=1e-10, atol=1e-12, max_step=0.005)

        if sol.success:
            sol_full = solve_ivp(deriv, [y_s, y_e], Y0, rtol=1e-10, atol=1e-12,
                                dense_output=True, max_step=0.005)
            return sol_full
        return None

    # From horizon
    sol_h = try_solve(omega, l, 'from_horizon', y_start, y_match)
    # From infinity
    sol_i = try_solve(omega, l, 'from_infinity', y_end, y_match)

    if sol_h is None or sol_i is None:
        return None

    # Evaluate at y_match
    ph = sol_h.sol(y_match)
    pf = sol_i.sol(y_match)

    # Wronskian of phi (unfactored)
    W = ph[0] * pf[1] - ph[1] * pf[0]
    return abs(W)


def wronskian_rstar(omega, l, rs_horizon=-50, rs_infinity=150, rs_match=80):
    """Wronskian in r* coordinate - this is the 'standard' formulation."""
    from scipy.special import lambertw

    def r_from_rstar(rs):
        t = rs / (2.0 * M) - 1.0
        y_lw = np.real(lambertw(np.exp(t)))
        r = 2.0 * M * (1.0 + y_lw)
        for _ in range(30):
            rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
            drstar_dr = r**2 / (r - 2.0 * M)**2
            dr = (rs_calc - rs) / drstar_dr
            if abs(dr) < 1e-14:
                break
            r -= dr
            if r <= 2.0 * M:
                r = 2.0 * M + 1e-14
        return r

    def V(r):
        f = 1.0 - 2.0 * M / r
        return f * (l * (l + 1.0) / r**2 - 6.0 * M / r**3)

    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14:
            r = 2.0 * M + 1e-14
        V_val = V(r)
        return [Y[1], -(omega**2 - V_val) * Y[0]]

    def try_rs(omega, l, direction):
        if direction == 'horizon':
            Y0 = [1.0, -1j * omega]
            sol = solve_ivp(deriv, [rs_horizon, rs_match], Y0,
                          rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
        else:
            Y0 = [1.0, 1j * omega]
            sol = solve_ivp(deriv, [rs_infinity, rs_match], Y0,
                          rtol=1e-10, atol=1e-12, max_step=0.2, dense_output=True)
        return sol

    sol_h = try_rs(omega, l, 'horizon')
    sol_i = try_rs(omega, l, 'infinity')

    if not (sol_h.success and sol_i.success):
        return None, None, None

    ph, dph = sol_h.sol(rs_match)
    pf, dpf = sol_i.sol(rs_match)
    W = abs(ph * dpf - dph * pf)
    return W, ph, pf


def wide_scan(l):
    """Scan a wide frequency range to find all modes."""
    best = []
    ref = BERTI_REF[l]

    # Scan real part and imaginary part
    for re_w in np.arange(ref.real - 0.4, ref.real + 0.4, 0.05):
        for im_w in np.arange(ref.imag - 0.15, ref.imag + 0.05, 0.02):
            omega = complex(re_w, im_w)
            W, ph, pf = wronskian_rstar(omega, l)
            if W is not None and W < 1.0:
                best.append((W, omega))

    best.sort()
    return best[:10]


def main():
    print("=" * 70)
    print("Wide Frequency Scan for QNM Eigenvalues")
    print("=" * 70)

    for l in [2, 3]:
        print(f"\nl={l}:")
        ref = BERTI_REF[l]
        print(f"  Berti ref: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        # Single check at reference
        W_ref, _, _ = wronskian_rstar(ref, l)
        print(f"  |W| at Berti ref: {W_ref:.6e}")

        # Quick check at nearby points
        for dr in [0, 0.05, -0.05, 0.1, -0.1]:
            for di in [0, 0.01, -0.01, 0.02, -0.02]:
                omega = ref + complex(dr, di)
                W, _, _ = wronskian_rstar(omega, l)
                if W is not None and W < 1.0:
                    print(f"  w={omega.real:.4f}{omega.imag:.4f}i: |W| = {W:.6e}")

        # Wide scan (less dense to keep runtime reasonable)
        print(f"\n  Broad scan around ref:")
        best = wide_scan(l)
        if best:
            for W, w in best[:8]:
                print(f"    w = {w.real:.5f} - {abs(w.imag):.5f}i, |W| = {W:.6e}")
        else:
            print("    No low-W values found.")

        print(f"\n  Checking: {ref.real:.5f} - {abs(ref.imag):.5f}i (exact Berti)")
        # Verify at exact Berti with more points
        rs_m = 50
        from scipy.special import lambertw

        def rs_check(omega, l, rs_h=-50, rs_inf=150, rs_m=50):
            def rfromrs(rs):
                t = rs / (2*M) - 1
                y_l = np.real(lambertw(np.exp(t)))
                r = 2*M*(1 + y_l)
                for _ in range(30):
                    rc = r + 2*M*np.log(r/(2*M)-1)
                    d = r**2/(r-2*M)**2
                    dr = (rc - rs)/d
                    if abs(dr) < 1e-14:
                        break
                    r -= dr
                    if r <= 2*M:
                        r = 2*M + 1e-14
                return r

            def V(r):
                f = 1 - 2*M/r
                return f*(l*(l+1)/r**2 - 6*M/r**3)

            def od(rst, Y):
                r = rfromrs(rst)
                if r <= 2*M + 1e-14: r = 2*M + 1e-14
                return [Y[1], -(omega**2 - V(r))*Y[0]]

            s1 = solve_ivp(od, [rs_h, rs_m], [1, -1j*omega], rtol=1e-10, atol=1e-12, max_step=0.15, dense_output=True)
            s2 = solve_ivp(od, [rs_inf, rs_m], [1, 1j*omega], rtol=1e-10, atol=1e-12, max_step=0.15, dense_output=True)
            if not (s1.success and s2.success):
                return None
            ph, dph = s1.sol(rs_m)
            pf, dpf = s2.sol(rs_m)
            return abs(ph*dpf - dph*pf), s1, s2

        Wval, s1, s2 = rs_check(ref, l)
        if Wval is not None:
            ph, dph = s1.sol(rs_m)
            pf, dpf = s2.sol(rs_m)
            print(f"  At r*={rs_m}: |W|={Wval:.6e}")
            print(f"    psi_h = {ph:.6e}, dpsi_h = {dph:.6e}")
            print(f"    psi_f = {pf:.6e}, dpsi_f = {dpf:.6e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
