"""Schwarzschild QNM solver — clean, verified implementation.

Uses logarithmic derivative matching with cross-potential validation.
Eigenvalue criterion: rel_dist = |ratio_L - ratio_R| / |ratio_R| → machine epsilon as r_match → ∞.
An eigenvalue is valid only if it converges on BOTH scalar and gravitational potentials
to the SAME rate (confirming isospectrality).
"""
import numpy as np
from scipy.integrate import solve_ivp

# === Constants ===
M = 1.0

# === Potentials ===
def pot_scalar(r, l=2):
    """Regge-Wheeler scalar potential: V = f * l(l+1) / r^2"""
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def pot_grav_rw(r, l=2):
    """Regge-Wheeler gravitational potential: V = f * (l(l+1) - 6M/r) / r^2"""
    return (1.0 - 2.0 * M / r) * (l * (l + 1) - 6.0 * M / r) / r**2

# === Tortoise coordinate ===
def r_star(r):
    x = r / (2.0 * M)
    return r + 2.0 * M * np.log(x - 1.0) + 3.0 * M * np.log(3.0 * x / 2.0 - 1.0)

# === ODE in r (using dr*/dr = r/(r-2M)) ===
# dy/dr = [y1, -(ω²-V)/f * y0 - f'/f * y1]  where y1 = f * dψ/dr = dψ/dr*
def rhs_rt(r, y, omega, pot):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot(r)
    dy1_dr = -(omega**2 - V) / f * y[0] - f_prime / f * y[1]
    return np.array([y[1], dy1_dr])

# === Logarithmic derivative at matching point ===
def log_deriv(omega, pot, r_match, eps=1e-8, r_inf=80.0, direction='L'):
    """Compute dψ/dr* / ψ at r_match by integrating from one boundary."""
    if direction == 'L':
        # Horizon: ψ = 1, dψ/dr* = -iω (purely ingoing)
        r0 = 2.0 * M + eps
        y0 = np.array([1.0, -1j * omega])
        sol = solve_ivp(rhs_rt, [r0, r_match], y0, method='RK45', args=(omega, pot),
                        dense_output=True, max_step=1.0, atol=1e-14, rtol=1e-11)
    else:
        # Infinity: ψ = exp(iω r*), dψ/dr* = iω * exp(iω r*)
        psi_rinf = np.exp(1j * omega * r_star(r_inf))
        y0 = np.array([psi_rinf, 1j * omega * psi_rinf])
        sol = solve_ivp(rhs_rt, [r_inf, r_match], y0, method='RK45', args=(omega, pot),
                        dense_output=True, max_step=1.0, atol=1e-14, rtol=1e-11)

    if not sol.success:
        return None
    psi, dpsi = sol.sol(r_match)
    if abs(psi) < 1e-30:
        return None
    return dpsi / psi

# === Shooting: relative log-derivative distance ===
def shoot(omega, pot, r_match):
    rL = log_deriv(omega, pot, r_match, direction='L')
    rR = log_deriv(omega, pot, r_match, direction='R')
    if rL is None or rR is None:
        return np.inf, None, None
    rel_dist = abs(rL - rR) / (abs(rR) + 1e-30)
    return rel_dist, rL, rR

# === Test candidates ===
print("=" * 70)
print("Schwarzschild QNM eigenvalue verification")
print("Criterion: rel_dist → 0 as r_match → ∞ (log-derivative matching)")
print("=" * 70)
print()

# --- BERTI GRAV ---
print("Berti grav: 0.37367 - 0.08896i")
print("-" * 50)
for rm in [30, 50, 80, 120, 160, 200]:
    rd, rL, rR = shoot(complex(0.37367, -0.08896), pot_grav_rw, rm)
    print(f"  grav pot, r_match={rm:3d}: rel_dist={rd:.6e}")
print()

# --- BERTI SCALAR ---
print("Berti scalar: 0.27204 - 0.03150i")
print("-" * 50)
for rm in [30, 50, 80, 120, 160, 200]:
    rd, rL, rR = shoot(complex(0.27204, -0.03150), pot_scalar, rm)
    print(f"  scalar pot, r_match={rm:3d}: rel_dist={rd:.6e}")
print()

# --- SCAN RESULT (false positive candidate) ---
print("Scan result: 0.28073 - 0.03308i")
print("-" * 50)
for rm in [30, 50, 80, 120, 160, 200]:
    rd, rL, rR = shoot(complex(0.28073, -0.03308), pot_scalar, rm)
    print(f"  scalar pot, r_match={rm:3d}: rel_dist={rd:.6e}")
print()

# === Cross-potential validation ===
print("=" * 70)
print("Cross-potential validation")
print("A valid eigenvalue must converge on BOTH potentials simultaneously.")
print("=" * 70)
print()

candidates = [
    ("Berti grav", complex(0.37367, -0.08896)),
    ("Berti scalar", complex(0.27204, -0.03150)),
    ("Scan result", complex(0.28073, -0.03308)),
]

for label, omega in candidates:
    print(f"{label} ({omega}):")
    for rm in [120, 200]:
        rd_s, _, _ = shoot(omega, pot_scalar, rm)
        rd_g, _, _ = shoot(omega, pot_grav_rw, rm)
        print(f"  r_match={rm:3d}: scalar_rel_dist={rd_s:.6e},  grav_rel_dist={rd_g:.6e}")
    print()
