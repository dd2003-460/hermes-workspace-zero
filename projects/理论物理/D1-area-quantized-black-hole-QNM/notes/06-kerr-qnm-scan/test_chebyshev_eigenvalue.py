#!/usr/bin/env python3
"""
Schwarzschild QNM via Chebyshev collocation eigenvalue solver.

The idea is straightforward:
1. Map the problem to a finite interval in r* (say from r* = -70 to +150)
2. Build a Chebyshev differentiation matrix
3. Formulate the eigenvalue problem: (D2 + W^2 - V) psi = 0
4. The QNM frequencies are the complex eigenvalues of this non-Hermitian problem

This is a generalized eigenvalue problem because W appears in the BCs.
We reformulate as: find omega such that the solution satisfies BCs at both ends.

Alternative (simpler): enforce BCs by modifying the first and last rows
of the differential operator, then solve for eigenvalues.

For QNMs: we need the boundary conditions to select outgoing waves only.
In the complex omega plane, we look for isolated eigenvalues.

Key insight: this is NOT a standard Hermitian eigenvalue problem.
H is non-Hermitian, and eigenvalues can be complex.
We need scipy.linalg.eig (generalized eigenvalue problem).
"""

import numpy as np
from scipy.linalg import eig, eigh
import sys


def cheb(N):
    """Chebyshev differentiation matrix of order N on [-1, 1]."""
    if N == 0:
        D = np.zeros((1, 1))
        x = np.array([0.0])
        c = np.array([1.0])
        return D, x, c

    x = np.cos(np.pi * np.arange(N + 1) / N)
    c = np.ones(N + 1)
    c[0] = 2.0
    c[-1] = 2.0
    c = c * ((-1) ** np.arange(N + 1))

    D = np.zeros((N + 1, N + 1))
    for i in range(N + 1):
        for j in range(N + 1):
            if i == j:
                if i == 0:
                    D[i, j] = (2 * N**2 + 1) / 6.0
                elif i == N:
                    D[i, j] = -(2 * N**2 + 1) / 6.0
                else:
                    D[i, j] = -x[i] / (2 * (1 - x[i]**2))
            elif i == j + 1:
                D[i, j] = 0.5 * (x[i] / (x[i] - x[j])) * (c[i] / c[j])
            elif i + 1 == j:
                D[i, j] = 0.5 * (x[i] / (x[i] - x[j])) * (c[i] / c[j])
            else:
                D[i, j] = (c[i] / c[j]) / (x[i] - x[j])

    return D, x, c


def transform_to_rs(D_ch, x_ch, rs_min, rs_max):
    """Convert Chebyshev differentiation matrix on [-1,1] to r* space."""
    rs_grid = 0.5 * (rs_max - rs_min) * x_ch + 0.5 * (rs_max + rs_min)
    D_rs = 2.0 / (rs_max - rs_min) * D_ch
    return D_rs, rs_grid


def build_H_matrix(N, rs_min, rs_max, l, M=1.0):
    """
    Build the Hamiltonian matrix H such that:
    d²ψ/dr*² + (ω² - V)ψ = 0
    => H = -D² + V
    Eigenvalue: H ψ = ω² ψ

    Then enforce boundary conditions by replacing first/last rows.
    """
    # Chebyshev differentiation matrix
    D_ch, x_ch, c = cheb(N)

    # Transform to r* coordinate
    D_rs = transform_to_rs(D_ch, x_ch, rs_min, rs_max)[0]
    rs_grid = transform_to_rs(D_ch, x_ch, rs_min, rs_max)[1]

    # Convert r* to r
    from scipy.special import lambertw
    r_grid = np.zeros(N + 1)
    for k, rs in enumerate(rs_grid):
        t = rs / (2 * M) - 1.0
        if t > 10:
            y = t - np.log(t) + np.log(t) / t
        else:
            y = lambertw(np.exp(t), k=0).real
        r_grid[k] = 2 * M * (1 + y)

    # Potential V = (1-2M/r)[l(l+1)/r² - 6M/r³]
    V_grid = np.zeros(N + 1)
    for k in range(N + 1):
        r = r_grid[k]
        if r > 2 * M + 1e-14:
            V_grid[k] = (1.0 - 2.0 * M / r) * (l * (l + 1) / r**2 - 6.0 * M / r**3)
        else:
            V_grid[k] = 0.0

    # Second derivative matrix
    D2_rs = D_rs @ D_rs

    # Hamiltonian: H = -D² + V (diagonal)
    H = -D2_rs + np.diag(V_grid)

    # Enforce boundary conditions by replacing first and last rows
    # For Dirichlet: ψ = 0 at boundaries (not correct for QNMs)
    # For QNMs, we need to implement the correct boundary conditions differently

    # At the horizon: ingoing wave => no reflection
    # At infinity: outgoing wave => no incoming component

    # The trick: for the generalized eigenvalue problem, we write:
    # (D2 + W^2*I - V) * psi = 0
    # (H - W^2 * I) * psi = 0
    # This is an αHψ = βψ eigenvalue problem where α = -W^2 and the
    # boundary conditions select which eigenvalues correspond to QNMs.

    return H, D2_rs, V_grid, r_grid, rs_grid


def find_eigenvalues(N, l, rs_range=(-70, 150), n_target=10):
    """Find the lowest n_target eigenvalues."""
    H, D2_rs, V_grid, r_grid, rs_grid = build_H_matrix(N, rs_range[0], rs_range[1], l)

    N_dims = N + 1

    # Build identity matrix with boundary conditions removed
    # For QNMs: psi is NOT zero at boundaries. We need a different formulation.

    # Key insight: the boundary conditions for QNMs are:
    # - At r* -> -inf: psi ~ exp(-i*w*r*)  (ingoing)
    # - At r* -> +inf: psi ~ exp(+i*w*r*)  (outgoing)

    # We CAN enforce these by replacing the first and last rows of the
    # differential operator with boundary condition equations.

    # Modified H: first and last rows set to enforce BCs
    H_mod = H.copy()
    D2_rs_mod = D2_rs.copy()

    # Horizon BC: dpsi/dr* + i*w*psi = 0 at rs_min
    # But w is an eigenvalue, so this is a nonlinear eigenvalue problem.

    # For numerical solution: try fixed omega, see if system has non-trivial solution.
    # At the true QNM, det(H(omega)) = 0 (or the boundary conditions are satisfied).

    # Practical approach: for a given omega, solve:
    # [D2_rs - V_grid + omega^2 * I][psi] = 0 with BCs

    # This is equivalent to finding omega such that the boundary conditions
    # are simultaneously satisfied. The eigenvalue problem gives us a starting point.

    # Remove the rows corresponding to boundaries from the eigenvalue problem
    # to find approximate eigenvalues, then verify boundary conditions.

    interior_idx = slice(1, N_dims - 1)
    H_int = H[interior_idx][:, interior_idx]

    eigenvals, eigenvecs = eig(H_int)

    # Find eigenvalues close to expected QNM (small negative imag part, small positive real)
    # Sort by how close they are to a typical QNM
    w2_sorted = sorted(eigenvals, key=lambda e: abs(abs(e)**0.5 - 0.5))

    # Extract the ones with Im(w) < 0 (QNMs)
    w_vals = []
    for w2 in w2_sorted[:n_target*3]:
        w1 = np.sqrt(w2)
        w2_sol = -w1  # both branches
        if w1.imag < 0 and w1.real > 0:
            w_vals.append(w1)
        if w2_sol.imag < 0 and w2_sol.real > 0:
            w_vals.append(w2_sol)

    # Remove duplicates
    w_vals_unique = []
    for w in w_vals:
        is_dup = False
        for w2 in w_vals_unique:
            if abs(w - w2) < 1e-8:
                is_dup = True
                break
        if not is_dup:
            w_vals_unique.append(w)

    return sorted(w_vals_unique, key=lambda w: abs(w.imag))[:n_target]


if __name__ == "__main__":
    print("=" * 70)
    print("Chebyshev Collocation Eigenvalue Solver")
    print("=" * 70)

    BERTI_REF = {
        2: complex(0.37367, -0.08896),
        3: complex(0.59108, -0.05902),
    }

    for l in [2, 3]:
        print(f"\nl={l}:")
        print(f"  Reference: omega = {BERTI_REF[l].real:.5f} - {abs(BERTI_REF[l].imag):.5f} i")

        for N in [80, 120]:
            w_eigs = find_eigenvalues(N, l, rs_range=(-70, 150), n_target=3)

            if w_eigs:
                print(f"\n  N={N} (interior):")
                for i, w in enumerate(w_eigs[:3]):
                    rel = abs((w - BERTI_REF[l]) / BERTI_REF[l])
                    print(f"    w_{i}:  {w.real:.6f} - {abs(w.imag):.6f} i  rel_err = {rel:.2e}")
            else:
                print(f"\n  N={N}: no QNM-like eigenvalues found")

    print("\n" + "=" * 70)
    print("Note: This is a naive Dirichlet eigenvalue solver.")
    print("QNMs need proper complex boundary conditions, which require")
    print("the generalized eigenvalue formulation or shooting method.")
    print("=" * 70)
