#!/usr/bin/env python3
"""
Diagnostic test: check all ingredients of QNM calculation
independently and look for systematic errors.

Key tests:
1. Check WKB estimate for fundamental mode l=2
2. Check if free-Wronskian (V=0) works correctly
3. Verify boundary conditions with exact known solutions
4. Compare potential depths for different l values
5. Try a pure matrix-method eigenvalue solve (not shooting)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
from scipy.linalg import eig

M = 1.0
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


# ============================================================================
# Tortoise coordinate
# ============================================================================

def rstar_of(r):
    """r* = r + 2M ln(r/2M - 1)"""
    return r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)


def r_from_rstar(rs):
    """Inverse using Lambert W + Newton."""
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(50):
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


# ============================================================================
# Test 1: Verify r_from_rstar is correct
# ============================================================================

def test_r_from_rstar():
    print("=" * 80)
    print("Test 1: r_from_rstar verification")
    print("=" * 80)
    for rs in np.array([-30, -20, -10, -5, -2, -1, 0, 5, 10, 20, 40, 60, 80, 100, 150, 200]):
        r = r_from_rstar(rs)
        rs_check = rstar_of(r)
        err = abs(rs_check - rs)
        ok = "OK" if err < 1e-10 else "FAIL"
        print(f"  rs*={rs:6.0f} -> r={r:14.10f} -> r*_check={rs_check:14.10f}  err={err:.2e}  [{ok}]")


# ============================================================================
# Test 2: Check WKB approximation for fundamental QNM
# ============================================================================

def test_wkb():
    """
    WKB approximation for QNM frequencies (Schwarzschild).
    The standard formula is:
    ω² = V_max - i(n + 1/2) * sqrt(-V''_max)
    where V_max is the peak of the Regge-Wheeler potential.
    """
    print("\n" + "=" * 80)
    print("Test 2: WKB approximation for fundamental QNM")
    print("=" * 80)

    for l in [2, 3]:
        # Find the peak of the RW potential
        r_grid = np.linspace(2*M + 0.1, 50, 50000)
        f = 1.0 - 2.0 * M / r_grid
        V = f * (l*(l+1.0) / r_grid**2 - 6.0 * M / r_grid**3)

        idx_max = np.argmax(V)
        r_max = r_grid[idx_max]
        V_max = V[idx_max]
        w_max = np.sqrt(V_max)  # real part estimate

        # Second derivative (numerical)
        h = 0.01
        Vpp = (V[max(0, idx_max-1)] - 2*V[idx_max] + V[min(len(V)-1, idx_max+1)]) / h**2

        for n in range(3):
            omega_wkb = w_max - 1j * (n + 0.5) * np.sqrt(-Vpp)
            omega_sq = omega_wkb**2

            print(f"\n  l={l}, n={n}:")
            print(f"    V_max = {V_max:.6f} at r* = {rstar_of(r_max):.2f}")
            print(f"    V''_max = {Vpp:.4f}")
            print(f"    sqrt(V_max) = {w_max.real:.5f}  sqrt(-V''_max) = {np.sqrt(-Vpp):.5f}")
            print(f"    WKB: ω ≈ {omega_wkb.real:.5f} - {abs(omega_wkb.imag):.5f}i")
            print(f"    WKB: ω² ≈ {omega_wkb.real**2 - omega_wkb.imag**2:.5f} - {2*omega_wkb.real*abs(omega_wkb.imag):.5f}i")
            if l in BERTI_REF and n < len([k for k in BERTI_REF if k == l]):
                print(f"    Berti:  ω ≈ {BERTI_REF[l].real:.5f} - {abs(BERTI_REF[l].imag):.5f}i")

        # Peak of the different potentials
        for c_name, c_val in [("c=6 (RW)", 6.0), ("c=2 (scalar)", 2.0)]:
            r_grid2 = np.linspace(2*M + 0.1, 50, 50000)
            f2 = 1.0 - 2.0 * M / r_grid2
            V2 = f2 * (l*(l+1.0) / r_grid2**2 - c_val * M / r_grid2**3)
            idx_max2 = np.argmax(V2)
            V_max2 = V2[idx_max2]
            w_max2 = np.sqrt(V_max2)
            print(f"    With {c_name}: V_max = {V_max2:.6f}, sqrt(V_max) = {w_max2.real:.5f}")


# ============================================================================
# Test 3: Free equation Wronskian (V=0) - should be exactly zero or not
# ============================================================================

def test_free_wronskian():
    print("\n" + "=" * 80)
    print("Test 3: Free equation Wronskian (V=0) - must be 2iω for non-QNMs")
    print("=" * 80)

    omega = 0.37367 - 0.08896j
    rs_h = -50
    rs_inf = 150
    rs_m = 0  # Match at r*=0

    def deriv(rs, Y):
        return [Y[1], -omega**2 * Y[0]]

    s1 = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j*omega], rtol=1e-14, atol=1e-14, max_step=0.1)
    s2 = solve_ivp(deriv, [rs_inf, rs_m], [1.0, +1j*omega], rtol=1e-14, atol=1e-14, max_step=0.1)

    if s1.success and s2.success:
        ph, dph = s1.y[:, -1]
        pf, dpf = s2.y[:, -1]
        W = ph*dpf - dph*pf

        # For V=0, solutions are exact exponentials:
        # From horizon: psi_h(r*) = exp(-iωr*), dpsi_h/dr* = -iω*psi_h(r*)
        # At r*=0:  psi_h = exp(0) = 1, dpsi_h = -iω
        # From infinity: psi_inf(r*) = exp(iωr*), dpsi_inf/dr* = iω*psi_inf(r*)
        # At r*=0: psi_inf = 1, dpsi_inf = +iω
        # W = psi_h * dpsi_inf - dpsi_h * psi_inf = 1*(iω) - (-iω)*1 = 2iω

        print(f"  omega = {omega}")
        print(f"  psi_h(r*=0) = {ph}, dpsi_h = {dph}")
        print(f"  psi_inf(r*=0) = {pf}, dpsi_inf = {dpf}")
        print(f"  W = {W}, |W| = {abs(W)}")
        print(f"  Expected |W| = |2iω| = {abs(2j*omega)}")
        print(f"  Ratio |W|/|2iω| = {abs(W)/abs(2j*omega)}")

        # This should give 2iω exactly (up to numerical errors)
        # And NOT be zero (confirming V=0 has no QNMs)


# ============================================================================
# Test 4: Exact Wronskian check with known potential profile
# ============================================================================

def test_potential_profile():
    """Print potential as function of r* for debugging."""
    print("\n" + "=" * 80)
    print("Test 4: RW potential as function of r*")
    print("=" * 80)

    for l in [2, 3]:
        r_grid = np.linspace(2.01, 100, 200)
        rs_vals = rstar_of(r_grid)
        f = 1.0 - 2.0 * M / r_grid
        V6 = f * (l*(l+1.0) / r_grid**2 - 6.0 * M / r_grid**3)
        V2 = f * (l*(l+1.0) / r_grid**2 - 2.0 * M / r_grid**3)

        idx_max = np.argmax(np.abs(V6))
        print(f"\n  l={l}, c=6:")
        print(f"    Peak at r*={rs_vals[idx_max]:.2f}, V_max={V6[idx_max]:.6f}")
        print(f"    r at peak = {r_grid[idx_max]:.4f}")

        # Check if V has a barrier shape (positive barrier means bound-like states)
        has_barrier = np.any(V6 > 0)
        print(f"    V crosses zero: {np.any(np.diff(np.sign(V6)))}")
        print(f"    Has positive barrier: {has_barrier}")

        # For reference: the frequency squared of the QNM
        omega_b = BERTI_REF[l]
        print(f"    ω²_Berti = {omega_b**2}")
        print(f"    ω²_found_min = {(complex(0.454,-0.029))**2}")
        print(f"    ω²_found_min2 = {(complex(0.574,-0.039))**2}")


# ============================================================================
# Test 5: Matrix diagonalization in discretized r*
# ============================================================================

def test_matrix_method():
    """
    Discretize the Schrödinger-like equation:
    d²ψ/dr*² + (ω² - V)ψ = 0
    using finite differences. Convert to eigenvalue problem:
    ω² ψ = -d²ψ/dr*² ψ + Vψ = H ψ
    This finds discrete bound-like states with ω² as eigenvalues.

    Note: For QNMs, ω² has negative imaginary part, so these aren't
    bound states in the usual sense. But the discretized problem
    will have complex eigenvalues near the QNM frequencies.
    """
    print("\n" + "=" * 80)
    print("Test 5: Matrix diagonalization (discretized Schrödinger)")
    print("=" * 80)

    for l in [2]:
        rs = np.linspace(-40, 200, 2001)  # 1501 points from horizon to infinity
        N = len(rs)
        drs = rs[1] - rs[0]

        r = r_from_rstar(rs)
        f = 1.0 - 2.0 * M / r
        V = f * (l*(l+1.0) / r**2 - 6.0 * M / r**3)

        # Second derivative matrix (finite differences)
        d2 = np.zeros((N, N))
        for i in range(N):
            if 0 < i < N-1:
                d2[i, i-1] = 1.0
                d2[i, i] = -2.0
                d2[i, i+1] = 1.0
            else:
                # Dirichlet BC: ψ=0 at boundaries
                d2[i, i] = -2.0
                if i == 0 and i+1 < N:
                    d2[i, i+1] = 1.0
                if i == N-1 and i-1 >= 0:
                    d2[i, i-1] = 1.0

        d2 /= drs**2

        # Full Hamiltonian: -d²/dr*² + V
        H = -d2 + np.diag(V)

        # Diagonalize
        eigenvalues = np.linalg.eigvalsh(H)
        # eigenvalues are real because H is Hermitian (V is real)

        # Sort and pick the ones with smallest real eigenvalue (these correspond to
        # frequencies near the QNM region)
        idx_sorted = np.argsort(np.abs(eigenvalues))
        print(f"  Matrix eigenvalues (lowest 10 in |ω²|):")
        for i in idx_sorted[:10]:
            print(f"    ω² = {eigenvalues[i]:.6f}")
            print(f"    ω = {np.sqrt(eigenvalues[i]):.6f}")

        # QNMs with real ω² are standing waves (NOT quasi-normal modes!)
        # The discrete grid method can't capture outgoing BCs naturally.
        print(f"  Note: Discrete matrix with Dirichlet BC gives real ω² (standing waves)")
        print(f"  This CANNOT reproduce complex QNM frequencies. The eigenvalue")
        print(f"  must be found with complex BCs or other methods.")

        # Check if eigenvalue at Berti works
        omega_b = BERTI_REF[l]
        print(f"\n  Berti: ω² = {omega_b**2:.6f}")
        # For a true QNM, ω² is complex, so this eigenvalue problem is inapplicable
        # for finding QNMs directly.


# ============================================================================
# Test 6: Check if Im(ω) = -Im(ω_Berti) works (sign flip test)
# ============================================================================

def test_sign_flip():
    """Test if flipping the sign of Im(ω) gives better results."""
    print("\n" + "=" * 80)
    print("Test 6: Sign flip test on Im(ω)")
    print("=" * 80)

    for omega_test in [
        ("Berti (standard)", 0.37367 - 0.08896j),
        ("Sign-flipped Im", 0.37367 + 0.08896j),
        ("Time-reversed", -0.37367 - 0.08896j),
        ("Fully reversed", -0.37367 + 0.08896j),
    ]:
        name, omega = omega_test

        # Simple check: integrate horizon-outward with ingoing BC
        rs_h = -40
        rs_m = 80
        l = 2

        def deriv(rs, Y):
            r = r_from_rstar(rs)
            if r <= 2*M: r = 2*M + 1e-14
            f = 1.0 - 2.0*M/r
            V = f * (l*(l+1.0)/r**2 - 6.0*M/r**3)
            return [Y[1], -(omega**2 - V)*Y[0]]

        s1 = solve_ivp(deriv, [rs_h, rs_m], [1.0, -1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2)
        s2 = solve_ivp(deriv, [150, rs_m], [1.0, +1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2)

        if s1.success and s2.success:
            ph, dph = s1.y[:, -1]
            pf, dpf = s2.y[:, -1]
            W = abs(ph*dpf - dph*pf)

            # Also compute B/A from horizon integration
            psih = ph
            dpsih = dph
            exp_ipi = np.exp(1j*omega*rs_m)
            exp_mipi = np.exp(-1j*omega*rs_m)
            A_comp = (dph + 1j*omega*ph) / (2j*omega)
            B_comp = (dph - 1j*omega*ph) / (-2j*omega)
            BA = abs(B_comp/A_comp) if abs(A_comp) > 1e-100 else float('inf')

            print(f"  {name}: ω = {omega.real:.5f}{omega.imag:.5f}i  |W|={W:.6e}  |B/A|@80={BA:.6e}")


# ============================================================================
# Test 7: Systematic parameter scan across omega^2
# ============================================================================

def test_omega2_scan():
    """Scan over omega^2 directly instead of omega."""
    print("\n" + "=" * 80)
    print("Test 7: Scan over omega (grid of ω² values)")
    print("=" * 80)

    # Test specific omega values
    test_vals = [
        ("Berti l=2", complex(0.37367, -0.08896)),
        ("Berti l=3", complex(0.59108, -0.05902)),
        ("L2: found W_min", complex(0.454, -0.029)),
        ("L2: found W_min2", complex(0.574, -0.039)),
        ("L3: found W_min", complex(0.691, -0.034)),
        ("sqrt(l(l+1))/2: l=2", complex(np.sqrt(6)/2, 0)),
        ("sqrt(l(l+1))/2: l=3", complex(np.sqrt(12)/2, 0)),
        ("(l-1/2)/2: l=2", complex(0.75/2, 0)),
        ("(l-1/2)/2: l=3", complex(1.25/2, 0)),
    ]

    rs_m = 80
    print(f"\n  Matching at r* = {rs_m}, c=6:")
    for name, omega in test_vals:
        l = 2 if "l=2" in name or "L2" in name else 3

        def deriv(rs, Y, om=omega):
            r = r_from_rstar(rs)
            if r <= 2*M: r = 2*M + 1e-14
            f = 1.0 - 2.0*M/r
            V = f * (l*(l+1.0)/r**2 - 6.0*M/r**3)
            return [Y[1], -(om**2 - V)*Y[0]]

        s1 = solve_ivp(deriv, [-50, rs_m], [1.0, -1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2)
        s2 = solve_ivp(deriv, [150, rs_m], [1.0, +1j*omega], rtol=1e-10, atol=1e-12, max_step=0.2)

        if s1.success and s2.success:
            ph, dph = s1.y[:, -1]
            pf, dpf = s2.y[:, -1]
            W = abs(ph*dpf - dph*pf) / (abs(ph)*abs(pf))
            print(f"  {name:30s}: |W| = {W:.6e}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    test_r_from_rstar()
    test_wkb()
    test_free_wronskian()
    test_potential_profile()
    test_matrix_method()
    test_sign_flip()
    test_omega2_scan()
    print("\n" + "=" * 80)
    print("All diagnostics complete.")
    print("=" * 80)
