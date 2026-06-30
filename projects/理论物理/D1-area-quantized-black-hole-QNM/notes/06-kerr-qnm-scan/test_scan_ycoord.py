#!/usr/bin/env python3
"""
Wronskian scan in y = 1 - 2M/r coordinate.
Horizon: y = 0, Infinity: y = 1
ODE: d2psi/dy2 + P(y)*dpsi/dy + Q(y)*psi = 0

Verified with sympy:
  J = dy/dr* = y*(1-y)²/(2M)
  P = J'/J = (3y-1)/[y(y-1)]
  Q = [4ω² - y(y-1)²(l(l+1) + 3y - 3)] / [y²(y-1)⁴]  (M=1)
"""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0
BERTI_REF = {
    2: complex(0.37367, -0.08896),
    3: complex(0.59108, -0.05902),
}


def P_y(y, c=6.0):
    """P(y) = (3y-1)/[y(y-1)]. Verified with sympy."""
    # Clip to avoid singularities at y=0,1
    y = np.clip(y, 1e-14, 1.0 - 1e-14)
    return (3.0 * y - 1.0) / (y * (y - 1.0))


def Q_y(y, omega, l, c=6.0):
    """Q(y) from sympy derivation. c=6 for gravitational, c=2 for scalar."""
    y = np.clip(y, 1e-14, 1.0 - 1e-14)
    # From sympy: Q = [4ω² - y(y-1)²(l(l+1) + cy - 3y + 3y - 3)]/[y²(y-1)⁴]
    # where the V/J² term gives: [l(l+1) + 3y - 3] depends on c via the potential.
    # Actually for c≠6: V = y*(y-1)²*[l(l+1) + (c/2-3)*2y/(y-1) - 3]/(4M²)
    # Hmm, let me compute the V/J² term directly.
    r = 2.0 * M / (1.0 - y)
    f = y  # since f = 1-2M/r = 1-(1-y) = y
    V = f * (l * (l + 1.0) / r**2 - c * M / r**3)
    J2 = y**2 * (1.0 - y)**4 / (4.0 * M**2)  # J = y(1-y)^2/(2M)
    Q_val = (omega**2 - V) / J2
    return Q_val


def wronskian_ycoord(omega, l, y_horizon=1e-6, y_infinity=1.0 - 1e-6, y_match=0.5, c=6.0):
    """Compute Wronskian in y-coordinate, matching at y_match."""
    def deriv(y, Y):
        P_val = P_y(y, c=c)
        Q_val = Q_y(y, omega, l, c=c)
        return [Y[1], -P_val * Y[1] - Q_val * Y[0]]

    # From horizon (y small): ingoing BC
    # r* → -∞ as y → 0, ψ ~ exp(-iωr*) ~ y^(-2iω)
    rho = -2.0j * omega
    y1 = [1.0, rho / y_horizon]

    # From infinity (y → 1): outgoing BC
    # r* → +∞ as y → 1, ψ ~ exp(iωr*) ~ (1-y)^(-2iω)
    rho2 = 2j * omega
    y2 = [1.0, rho2 / (1.0 - y_infinity)]

    s1 = solve_ivp(deriv, [y_horizon, y_match], y1,
                   rtol=1e-11, atol=1e-13, max_step=0.01, dense_output=True)
    s2 = solve_ivp(deriv, [y_infinity, y_match], y2,
                   rtol=1e-11, atol=1e-13, max_step=0.01, dense_output=True)

    if not (s1.success and s2.success):
        return None

    ph, dph = s1.sol(y_match)
    pf, dpf = s2.sol(y_match)
    W = abs(ph * dpf - dph * pf)
    norm = abs(ph) * abs(pf)
    if norm < 1e-300:
        return None
    return W / norm


def main():
    print("=" * 80)
    print("QNM Scan in y = 1 - 2M/r Coordinate (horizon->infinity)")
    print("=" * 80)

    t0 = time.time()

    for l in [2, 3]:
        ref = BERTI_REF[l]
        pot_names = ["Gravitational (c=6)", "Scalar (c=2)"]
        pot_cs = [6.0, 2.0]

        print(f"\nl = {l}, Berti: omega = {ref.real:.5f} - {abs(ref.imag):.5f}i")

        for pot_name, pot_c in zip(pot_names, pot_cs):
            print(f"\n  {pot_name}:")

            # Test at Berti reference at different matching points
            for y_match in [0.1, 0.3, 0.5, 0.7, 0.9]:
                W = wronskian_ycoord(ref, l, y_match=y_match, c=pot_c)
                if W is not None:
                    print(f"    y_match={y_match:.1f}: |W|/norm = {W:.6e}")
                else:
                    print(f"    y_match={y_match:.1f}: FAILED")

            # Scan
            print(f"    Coarse scan:")
            best = []
            for dr in np.linspace(-0.15, 0.25, 17):
                for di in np.linspace(-0.15, 0.10, 15):
                    omega = ref + complex(dr, di)
                    W = wronskian_ycoord(omega, l, y_match=0.5, c=pot_c)
                    if W is not None and W < 5.0:
                        best.append((W, omega))
            best.sort()
            for W, omega in best[:5]:
                rel_err = abs(omega - ref) / abs(ref)
                print(f"      {omega.real:.5f} - {abs(omega.imag):.5f}i: |W| = {W:.6e}  rel_err = {rel_err:.3f}")

        total = time.time() - t0
        print(f"  Elapsed: {total:.0f}s")

    print(f"\nTotal: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
