"""
Clean Schwarzschild QNM solver via shooting method.
Direct integration of psi'' + (omega^2 - V)psi = 0
in tortoise coordinate r*.

Berti et al. PRD 79, 044006 (2009), arXiv:0802.4126
Table I: l=2, s=0 (scalar): omega*M = 0.37367 - 0.08896i
Table I: l=2, s=2 (gravitational): omega*M = 0.37367 - 0.08896i (isospectral)
Table I: l=3, s=0: omega*M = 0.59108 - 0.05902i
Table I: l=3, s=2: omega*M = 0.59108 - 0.05902i
"""
import numpy as np
from scipy.integrate import solve_ivp

# ============================================================
# 1. Tortoise coordinate and potential
# ============================================================
M = 1.0
r_plus = 2.0 * M  # horizon

def r_star(r):
    """Schwarzschild tortoise coordinate: r* = r + 2M*ln(r/2M - 1) + 3M*ln(3r/2M - 1)"""
    x = r / (2.0 * M)
    return r + 2.0 * M * np.log(np.abs(x - 1.0)) + 3.0 * M * np.log(np.abs(3.0 * x / 2.0 - 1.0))

def r_star_horizon():
    """r* -> -infinity at horizon."""
    return -np.inf

def potential_RW(r, c=2):
    """Regge-Wheeler potential with parameter c.
    c=2: scalar (s=0)
    c=6: gravitational (s=2)
    """
    f = 1.0 - 2.0 * M / r
    return f * (2.0 * r + c * M) / r**3

# ============================================================
# 2. ODE in tortoise coordinate
# ============================================================
def rhs(r_star_arr, omega):
    """psi'' = (V - omega^2) * psi
    Returns array [[psi'], [psi'']] for solve_ivp.
    """
    # Need r as function of r*; use inverse numerically
    # For efficiency, work directly in r coordinate with chain rule
    raise NotImplementedError

def rhs_in_r(r, psi, omega):
    """Compute (psi'', psi''') for the system psi' = y, y' = (V-omega^2)*psi.
    State: [psi, dpsi/dr]
    """
    ddr_to_drstar = 1.0 / (1.0 - 2.0 * M / r)  # dr*/dr = 1/f
    d2r_to_drstar2 = -2.0 * M / r / (r * (1.0 - 2.0 * M / r)**2)
    V = potential_RW(r)
    f = 1.0 - 2.0 * M / r

    # d^2psi/drstar^2 = f^2 * d^2psi/dr^2 + f*f' * dpsi/dr
    # = (V - omega^2) * psi
    # So: f^2 * psi''_r + f*f' * psi'_r = (V - omega^2) * psi
    # => psi''_r = [(V - omega^2)*psi - f*f'*psi'_r] / f^2

    f_prime = 2.0 * M / r**2
    d2psi_dr2 = ((potential_RW(r) - omega**2) * psi[0] - f * f_prime * psi[1]) / (f**2)

    return np.array([psi[1], d2psi_dr2])

# ============================================================
# 3. Boundary conditions at horizon
# ============================================================
def horizon_bc(omega, eps=1e-8):
    """Near horizon: psi ~ exp(-i*omega*r*/(4M)) = exp(-i*omega/(4M) * (r+2M*ln(r/2M-1)+...))
    psi ~ (r/2M - 1)^(-i*omega/(4M)) * r^(-i*omega/(4M)) * exp(-i*omega*r/(4M))

    Use psi(r+) = 1 (arbitrary normalization)
    dpsi/dr at r = r+ + eps

    Analytic: psi ~ exp(-i*omega*r*/(4M))
    ln psi ~ -i*omega*r*/(4M)
    d(ln psi)/dr = -i*omega/(4M) * dr*/dr = -i*omega/(4M) * 1/f
    dpsi/dr = psi * (-i*omega/(4M)) / f

    As r -> r+: f -> 0, so dpsi/dr diverges as 1/f!

    Better: work with u = psi, where u satisfies u''_rstar + (omega^2 - V)u = 0
    Near horizon: V -> 0, so u ~ exp(+-i*omega*r*/(4M))
    u' ~ -i*omega/(4M) * u (ingoing)

    But u' = du/dr* = f * du/dr, so:
    du/dr = u' / f = -i*omega/(4M) * u / f -> infinity at horizon

    Solution: integrate from r+ + eps where eps is small but finite.
    """
    r0 = r_plus + eps
    f0 = 1.0 - 2.0 * M / r0
    # psi(r0) = 1, psi'(r0) = -i*omega/(4M) / f0
    psi0 = 1.0
    dpsi0 = -1j * omega / (4.0 * M) / f0 * psi0
    return np.array([psi0, dpsi0])

# ============================================================
# 4. Boundary condition at infinity
# ============================================================
def infinity_bc(omega, r0=None):
    """At infinity: psi ~ exp(i*omega*r)
    psi'(r) = i*omega * psi(r)
    """
    if r0 is None:
        r0 = 50.0 * M  # large but finite

    # psi(r0) = exp(i*omega*r0)
    psi0 = np.exp(1j * omega * r0)
    dpsi0 = 1j * omega * psi0
    return np.array([psi0, dpsi0]), r0

# ============================================================
# 5. Shooting: integrate from both sides to matching point
# ============================================================
def shoot_wronskian(omega, r_match=None):
    """Compute Wronskian at matching point.
    W = psi_L' * psi_R - psi_L * psi_R'
    QNM when W = 0.

    Returns W / |psi_L|^2 / |psi_R|^2 (normalized)
    """
    if r_match is None:
        r_match = 10.0 * M  # matching point

    # Integrate left from horizon to r_match
    if np.isfinite(r_match):
        # horizon → r_match
        r_span = [r_plus + 1e-6, r_match]
        y0 = horizon_bc(omega)

        sol_L = solve_ivp(rhs_in_r, r_span, y0, method='RK45',
                         args=(omega,), dense_output=True,
                         max_step=0.1, atol=1e-12, rtol=1e-10)

        if not sol_L.success:
            return np.inf

        psi_L = sol_L.sol(r_match)[0]
        dpsi_L_dr = sol_L.sol(r_match)[1]
    else:
        return np.inf

    # Integrate right from infinity to r_match
    y0_r, r_inf = infinity_bc(omega)
    r_span_r = [r_inf, r_match]

    # Need to reverse integration: r_inf → r_match
    sol_R = solve_ivp(rhs_in_r, r_span_r, y0_r, method='RK45',
                     args=(omega,), dense_output=True,
                     max_step=0.1, atol=1e-12, rtol=1e-10)

    if not sol_R.success:
        return np.inf

    psi_R = sol_R.sol(r_match)[0]
    dpsi_R_dr = sol_R.sol(r_match)[1]

    # Wronskian
    W = (dpsi_L_dr * psi_R - psi_L * dpsi_R_dr)

    # Normalized
    norm = np.abs(psi_L) * np.abs(psi_R)
    if norm < 1e-30:
        return np.inf

    return W / norm

# ============================================================
# 6. Scan for eigenvalue
# ============================================================
def find_eigenvalue(l_range=np.arange(0.1, 0.8, 0.02),
                    i_range=np.arange(-0.15, -0.01, 0.005)):
    """Grid search for the QNM eigenvalue."""
    best_W = np.inf
    best_omega = None

    print("Grid search for QNM eigenvalue:")
    for real_omega in l_range:
        for imag_omega in i_range:
            omega = complex(real_omega, imag_omega)
            W = shoot_wronskian(omega)
            if np.isfinite(W):
                abs_W = np.abs(W)
                if abs_W < best_W:
                    best_W = abs_W
                    best_omega = omega

    print(f"  Best: omega = {best_omega.real:.5f} + {best_omega.imag:.5f}i")
    print(f"  |W| = {best_W:.6e}")
    return best_omega, best_W

# ============================================================
# 7. Refined search
# ============================================================
def refine_eigenvalue(omega0, n_points=200):
    """Fine grid search around omega0."""
    dr = 0.01
    di = 0.002
    r_range = np.linspace(omega0.real - dr, omega0.real + dr, n_points)
    i_range = np.linspace(omega0.imag - di, omega0.imag + di, n_points)

    best_W = np.inf
    best_omega = omega0

    print(f"\nRefined search around {omega0}:")
    for r in r_range:
        for i in i_range:
            omega = complex(r, i)
            W = shoot_wronskian(omega)
            if np.isfinite(W):
                abs_W = np.abs(W)
                if abs_W < best_W:
                    best_W = abs_W
                    best_omega = omega

    print(f"  Refined: omega = {best_omega.real:.6f} + {best_omega.imag:.6f}i")
    print(f"  |W| = {best_W:.6e}")
    return best_omega, best_W

# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Clean Schwarzschild QNM - Shooting Method")
    print("Equation: d^2psi/dr*^2 + (omega^2 - V)psi = 0")
    print("Berti 2009 Table I (M=1):")
    print("  l=2:  omega = 0.37367 - 0.08896i")
    print("  l=3:  omega = 0.59108 - 0.05902i")
    print("=" * 60)

    omega_best, W_best = find_eigenvalue()
    omega_refined, W_refined = refine_eigenvalue(omega_best)

    print(f"\nFinal result: omega = {omega_refined.real:.6f} + {omega_refined.imag:.6f}i")
    print(f"Expected:     omega = 0.37367 - 0.08896i")
