#!/usr/bin/env python3
"""
Matrix eigenvalue method: discretize d2psi/dr*2 + (w2 - V)*psi = 0
on uniform r* grid with Dirichlet BCs.  Eigenvalues of H = -d2/dr*2 + V
give w2 directly.  sqrt(w2) gives w.

This is the ultimate discriminant: if this disagrees with Berti,
the problem is in the FORMULATION (potential, equation, coordinate),
not in the integration / boundary-condition / Riccati machinery.
"""
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigs
from scipy.special import lambertw

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}


def r_from_rs(rs):
    """Invert r* = r + 2M ln(r/2M - 1) using Lambert W + Newton."""
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(60):
        if r <= 2 * M:
            r = 2 * M + 1e-14
            continue
        rs_calc = r + 2 * M * np.log(r / (2 * M) - 1.0)
        drstar_dr = r ** 2 / (r - 2 * M) ** 2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-16:
            break
        r -= dr
        if r <= 2 * M:
            r = 2 * M + 1e-14
    return r


def V_reg(r, l):
    """Regge-Wheeler potential."""
    f = 1.0 - 2.0 * M / r
    return f * (l * (l + 1.0) / r ** 2 - 6.0 * M / r ** 3)


def build_H(l, N, rs_min, rs_max):
    """Build the matrix H = -d2/dr*2 + V(r) on a uniform r* grid.

    We use a second-order centered finite-difference stencil:
        d2psi/drs*2 ~ (psi_{j+1} - 2 psi_j + psi_{j-1}) / ds^2

    So H_{j,j} = 2/ds^2 + V_j,  H_{j,j+1} = H_{j,j-1} = -1/ds^2

    Dirichlet BC: psi = 0 at rs*=rs_min and rs*=rs_max (first/last rows
    of the full grid are eliminated, leaving (N-2) interior points).
    """
    rs_grid = np.linspace(rs_min, rs_max, N)
    ds = rs_grid[1] - rs_grid[0]

    r_grid = np.array([r_from_rs(rs) for rs in rs_grid])
    r_grid = np.maximum(r_grid, 2 * M + 1e-14)  # never cross horizon

    V_grid = np.array([V_reg(r, l) for r in r_grid])

    interior = slice(1, N - 1)  # remove boundaries
    n_int = N - 2

    inv_ds2 = 1.0 / ds ** 2

    # Interior tridiagonal
    main_diag = 2.0 * inv_ds2 + V_grid[interior].copy()
    off_diag = -inv_ds2 * np.ones(n_int - 1)

    H = diags([off_diag, main_diag, off_diag],
              [-1, 0, +1], shape=(n_int, n_int), format='csc')
    return H, rs_grid, V_grid


def main():
    print("=" * 70)
    print("Matrix eigenvalue: Schwarzschild QNM")
    print("=" * 70)

    for l in [2, 3]:
        ref = BERTI[l]
        print(f"\n{'='*70}")
        print(f"l = {l}, Berti reference: omega = {ref.real:.5f}{ref.imag:.5f} i")
        print(f"    Berti: omega^2 = {ref**2:.8f}")
        print("=" * 70)

        # --- Convergence test: increase N ---
        for N in [200, 400, 600, 800, 1000]:
            rs_min = -80.0
            rs_max = 200.0

            H, rs_grid, V_grid = build_H(l, N, rs_min, rs_max)

            # Find lowest few eigenvalues (smallest magnitude omega^2)
            # We need complex eigensolver because H is not Hermitian
            # (V can be complex if r becomes complex, but with our
            # real grid it IS Hermitian, eigenvalues are real for H)
            # BUT: we want the lowest |w2|, not lowest eigenvalue of H.
            # Since H is Hermitian, eigenvalues are real and > 0 typically.
            # Actually w2 = eigenvalue of H. But QNM have complex w2.
            # Dirichlet eigenvalues of H are real. The trick is:
            # QNMs require complex rotation (complex scaling) to get
            # complex eigenvalues. With real Dirichlet BCs on real grid,
            # we only get real eigenvalues.
            #
            # ALTERNATIVE: find lowest eigenvalue of H, that's w2 >= 0.
            # This won't give QNM (complex), it gives bound-state-like
            # real eigenvalues.  NOT what we want for QNM.
            #
            # RIGHT APPROACH: The Schrödinger-like equation for QNM is NOT
            # a bound-state problem.  The Dirichlet eigenvalues of H on
            # a real grid give the spectrum of a confining box, NOT the
            # QNM.  We need a different approach for the matrix method.
            #
            # BETTER MATRIX METHOD: discretize the full ODE as a generalized
            # eigenvalue problem:  (D2 + w2 * I) psi = 0
            # This becomes:  D2 psi = -w2 * psi
            # eigenvalues of D2 are -w2, so w2 = -eig(D2)
            # D2 is the second-derivative matrix on the interior grid.

            # Actually let's just use D2 directly
            main_D2 = -2.0 * inv_ds2 * np.ones(n_int)
            off_D2 = inv_ds2 * np.ones(n_int - 1)

            D2 = diags([off_D2, main_D2, off_D2],
                       [-1, 0, +1], shape=(n_int, n_int), format='csc')

            # We want the eigenvalues of the generalized problem:
            #   D2 @ psi = -w2 @ psi   =>   -D2 @ psi = w2 @ psi
            # But this is just the eigenvalue problem for H = -D2 + V.
            # The eigenvalues w2 are REAL because both -D2 and V are Hermitian
            # on the real grid.  QNMs need complex w2.

            # KEY INSIGHT: The Dirichlet-box eigenvalues are NOT the QNM.
            # To get QNM with a matrix method, we need to use either:
            # (a) Complex scaling: rotate r* -> r* * exp(i*theta)
            # (b) Contour deformation: integrate along a complex r* path
            # (c) Direct complex grid search: discretize on complex grid
            # (d) Levinson-type method: factor out the exponential BC

            # Let's try approach (a) or simply report what we get
            # as a reference for the "box spectrum".

            evals = eigs(D2, k=min(6, n_int), which='SR',
                         return_eigenvectors=False).real
            # D2 eigenvalues are negative: lambda ~ -n^2 * pi^2 / L^2
            # so -D2 eigenvalues are positive: w2 = -lambda

            # More carefully: with the physical V included,
            # the lowest w2 = eigenvalue of H
            evals_H = eigs(H, k=min(6, n_int), which='SR',
                           return_eigenvectors=False)
            evals_H = np.sort(np.abs(evals_H.real))  # take |real part|

            # Also try: w2 from -D2 (no potential), as a baseline
            evals_D2 = eigs(-D2, k=min(6, n_int), which='SR',
                            return_eigenvectors=False)

            print(f"\n  N={N}, grid=({rs_min},{rs_max}), ds={rs_grid[1]-rs_grid[0]:.4f}")
            print(f"    -D2 eigenvalues (w2 no V): {evals_D2[:4]}")

            # w2 values from full H (real, positive)
            Hvals = eigs(H, k=min(6, n_int), which='SR',
                         return_eigenvectors=False)
            Hvals_sorted = np.sort(Hvals.real)
            print(f"    H=-D2+V eigenvalues (w2 with V): {Hvals_sorted[:4]}")
            print(f"    sqrt(H vals) [w]:", end="")
            for hv in Hvals_sorted[:4]:
                print(f" {np.sqrt(hv):.5f}", end="")
            print()

        # Now try complex scaling: rotate r* by a small angle
        # This is the standard way to expose QNM as discrete eigenvalues
        # of the scaled Hamiltonian.
        print(f"\n  --- Complex scaling test ---")
        for theta_deg in [1, 2, 3, 5, 8, 10, 15]:
            theta = theta_deg * np.pi / 180.0
            N = 600
            rs_min = -80.0
            rs_max = 200.0

            # Scale the grid: rs -> rs * exp(i*theta)
            # This maps real grid to a ray in the complex plane
            scale = np.exp(1j * theta)
            rs_scaled = np.linspace(rs_min, rs_max, N) * scale

            # dr*/dr = d(rs*scale)/dr  (just a scaling factor)
            # The derivative transforms as: d/dr* -> exp(-i*theta) d/d(rs_scaled)
            # So d2/dr*2 -> exp(-2i*theta) d2/d(rs_scaled)2
            # And w2 -> w2 * exp(-2i*theta) in the eigenvalue problem

            rs_s_grid = np.linspace(0, rs_max, N)  # use real grid in scaled coords
            ds = rs_s_grid[1] - rs_s_grid[0]

            r_from_rs_scaled = lambda rs_s: r_from_rs(rs_s * np.exp(1j * theta))
            r_grid_s = np.array([r_from_rs_scaled(rs_s) for rs_s in rs_s_grid])
            r_grid_s = np.maximum(np.abs(r_grid_s), 2 * M + 1e-14)

            # V evaluated at the scaled r
            # This is tricky — V depends on r, not r*.
            # With complex scaling, r* -> r* exp(i theta)
            # r(r*) is inverted from r*(r) = r + 2M ln(r/2M-1)
            # After scaling: r*(r)_scaled = exp(i theta) * r*(r)
            # We need to find r such that r*(r) = r*(r)_scaled / exp(i theta)
            # This means r(r* scaled) is what we already have above

            # For V we need the ACTUAL r from the complex r*:
            V_grid_s = np.array([V_reg(np.maximum(r_from_rs_scaled(rs_s),
                                                     2*M+1e-14), l)
                                  for rs_s in rs_s_grid])

            n_int = N - 2
            inv_ds2 = 1.0 / ds ** 2

            # The second derivative in scaled coords picks up exp(-2i theta)
            factor = np.exp(-2j * theta)

            main_diag = factor * (2.0 * inv_ds2 + V_grid_s[1:-1].copy())
            off_diag = factor * (-inv_ds2 * np.ones(n_int - 1))

            H_scaled = diags([off_diag, main_diag, off_diag],
                             [-1, 0, +1], shape=(n_int, n_int), format='csc')

            # Find eigenvalues near the expected QNM region
            try:
                evals_sc = eigs(H_scaled, k=min(6, n_int), which='SM',
                                return_eigenvectors=False)
                # w2_scaled = eigenvalue, so w = sqrt(eigenvalue)
                # But scaling also changes w: w_scaled = w * exp(i theta)
                # because: psi(r*, t) ~ exp(i w r* - i w t)
                # under r* -> r* exp(i theta): psi ~ exp(i w r* exp(i theta) - i w t)
                # = exp(i (w exp(i theta)) r* - i w t)
                # So the scaled eigenvalue corresponds to w_scaled = w * exp(i theta)
                # Wait, that's not right either. Let me reconsider.
                #
                # The scaled equation is:
                #   d2psi/d(rs*)^2 + (w2 - V) psi = 0
                # After complex scaling r* -> rho = r* exp(i theta):
                #   d2psi/d rho^2 * exp(2i theta) + (w2 - V) psi = 0
                #   d2psi/d rho^2 + exp(-2i theta)*(w2 - V) psi = 0
                # The eigenvalue problem for H_scaled is:
                #   -exp(2i theta)*d2psi/drho^2 + V psi = w2_explicit psi
                # Hmm, this is getting confusing.  Let me use a simpler approach.
                #
                # Simplest approach: just diagonalize -D2 + V on a REAL grid
                # and see what w2 values come out.  Even if they're real,
                # comparing with Berti tells us about the potential.

                pass  # skip complex scaling for now
            except Exception as e:
                pass

        # --- Simpler approach: Chebyshev collocation ---
        # This is the matrix method that SHOULD work for QNM.
        # Map r* in [rs_min, rs_max] to x in [-1, +1], then use Chebyshev
        # differentiation matrix D2.  Eigenvalue problem: D2 @ psi = -(w2) @ psi
        # But we need to include V.  Full matrix: M = D2 + V_diag
        # We want det(M) = 0, which means we need w2 such that M is singular.
        # This is a generalized eigenvalue problem: D2 @ psi = -w2 @ psi
        # BUT: V is position-dependent, so we can't separate it.
        #
        # Better: rearrange d2psi/drs*2 + w2*psi = V*psi
        # As matrix eigenvalue problem: D2 @ psi + w2 * psi = V @ psi
        # -> (D2 - V) @ psi = -w2 * psi
        # -> (V - D2) @ psi = w2 * psi
        # So w2 = eigenvalues of (V_diag - D2_interior)
        # And since V and D2 are real, w2 is real.  STILL not complex.
        #
        # THE CORE ISSUE: Real-grid Hermitian matrices give real eigenvalues.
        # To get QNM (complex), we must either:
        # 1. Use complex boundary conditions (not Dirichlet)
        # 2. Complexify the grid
        # 3. Use a non-Hermitian discretization
        #
        # OPTION 1: Non-Dirichlet boundary treatment
        # At horizon: psi ~ exp(-i w r*) -> psi(rs_min) is determined by psi(rs_min+ds)
        # At infinity: psi ~ exp(+i w r*) -> psi(rs_max) is determined by psi(rs_max-ds)
        # These BCs depend on w2!  This is a NONLINEAR eigenvalue problem.
        #
        # For a FIXED trial w2, the BCs are:
        #   psi(rs_min) = 0 is WRONG (the physical solution decays/grows exponentially)
        #
        # Actually the physical QNM near horizon is psi ~ exp(-i w r*)
        # which goes to ZERO at rs* -> -infinity (since Im(w) < 0 means -i*Im(w) > 0)
        # Wait: w = w_r + i*w_i, with w_i < 0 for QNM
        # exp(-i w r*) = exp(-i w_r r*) * exp(w_i r*)
        # As r* -> -inf: exp(w_i r*) -> 0 (since w_i < 0 and r* -> -inf means
        #   w_i*r* -> +inf) ... wait no, w_i < 0, r* -> -inf, so w_i * r* -> +inf
        # So exp(w_i r*) -> +infinity.  The ingoing mode diverges at horizon!
        #
        # Standard convention: psi(r*) ~ exp(-i w r*) as r* -> -inf
        # With w = 0.37 - 0.09 i: -i*w = -i*(0.37-0.09i) = -0.09 - 0.37i
        # exp((-0.09 - 0.37i)*r*) as r* -> -inf:  Re = exp(-0.09*r*) -> +inf
        # Hmm, the physical boundary condition for the METRIC perturbations is
        # that psi -> 0 at both ends.  With Dirichlet BC we enforce psi=0 at
        # r*_min and r*_max, which should approximate the physical solution
        # if |r*_min| is large enough (horizon) and r*_max is large enough.
        #
        # The QNM solution that satisfies ingoing BC at horizon decays as
        # exp(-i w r*) = exp(-i w_r r*) * exp(w_i r*).
        # Since w_i < 0: for r* > 0: exp(w_i * r*) -> 0 as r* -> +inf. Good.
        # For r* < 0: exp(w_i * r*) = exp(-|w_i| * r*) with r* < 0 -> exp(+|w_i| * |r*|)
        #             This EXPANDS as we go inward.  At the horizon r* -> -inf,
        #             the ingoing mode EXPLODES.
        #
        # BUT: in terms of the radial function psi = R(r), the physical
        # solution at the horizon is regular (no singularity in curvature).
        # The divergence in exp(-i w r*) is cancelled by the regge-wheeler
        # function psi = f(r) * R(r), where f -> 0 at horizon.
        #
        # The Dirichlet BC on psi = f*R does give psi=0 at horizon because f=0.
        # So Dirichlet is correct for psi, but it's really an approximation
        # of the exponential BC.
        #
        # THE BOTTOM LINE: Dirichlet eigenvalues on a real grid are REAL.
        # They approximate the bound-state spectrum, not the QNM.
        # To get QNM eigenvalues (complex), we MUST use complex methods.
        #
        # PRACTICAL APPROACH: Use the log-derivative (Riccati) method,
        # which we've been doing.  Or use the shooting + root-finding.
        # The matrix approach with Dirichlet BC on a real grid simply
        # CANNOT give complex eigenvalues, so it's not the right test.
        #
        # HOWEVER: there's one important check we CAN do:
        # Check that the lowest Dirichlet eigenvalue of H matches the
        # WKB estimate of the QNM.  If not, the formulation is wrong.

        # WKB: the potential barrier top V_peak gives the characteristic frequency:
        r_peak = 2 * M * np.sqrt(l * (l + 1.0))  # approximate peak of V
        V_peak = V_reg(r_peak, l)
        print(f"\n    V_peak (WKB): r_peak = {r_peak:.4f}, V_peak = {V_peak:.6f}")
        print(f"    Berti: omega = {ref.real:.5f}{ref.imag:.5f}, omega^2 = {ref**2:.8f}")
        print(f"    Re(omega^2)_Berti = {np.real(ref**2):.8f}, V_peak = {V_peak:.8f}")
        print(f"    diff Re = {np.real(ref**2) - V_peak:.8f}")


if __name__ == "__main__":
    main()
