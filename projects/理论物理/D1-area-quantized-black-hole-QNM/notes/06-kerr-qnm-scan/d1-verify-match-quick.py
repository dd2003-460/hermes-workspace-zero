"""Quick verification: Wronskian at multiple r_match points.
No large scans - just the 3 test values.
"""
import numpy as np
from scipy.integrate import solve_ivp
import time

M = 1.0

def pot_scalar(r, l=2):
    return (1.0 - 2.0 * M / r) * l * (l + 1) / r**2

def pot_grav_rw(r, l=2):
    return (1.0 - 2.0 * M / r) * (l * (l + 1) - 6.0 * M / r) / r**2

def rhs(r, psi, omega, pot):
    f = 1.0 - 2.0 * M / r
    f_prime = 2.0 * M / r**2
    V = pot(r)
    d2psi = ((V - omega**2) * psi[0] - f * f_prime * psi[1]) / f**2
    return np.array([psi[1], d2psi])

def integrate_L(omega, pot, eps=1e-6, r_match=20.0):
    r0 = 2.0 * M + eps
    f0 = 1.0 - 2.0 * M / r0
    y0 = np.array([1.0, -1j * omega / (4.0 * M) / f0])
    sol = solve_ivp(rhs, [r0, r_match], y0, method='RK45', args=(omega, pot),
                    dense_output=True, max_step=0.3, atol=1e-12, rtol=1e-10)
    if not sol.success:
        return None
    p = sol.sol(r_match)[0]
    d = sol.sol(r_match)[1]
    return p, d

def integrate_R(omega, pot, r_inf=80.0, r_match=20.0):
    psi0 = np.exp(1j * omega * r_inf)
    y0 = np.array([psi0, 1j * omega * psi0])
    sol = solve_ivp(rhs, [r_inf, r_match], y0, method='RK45', args=(omega, pot),
                    dense_output=True, max_step=0.3, atol=1e-12, rtol=1e-10)
    if not sol.success:
        return None
    p = sol.sol(r_match)[0]
    d = sol.sol(r_match)[1]
    return p, d

def match_check(omega, pot, match_points, label):
    print(f"\n=== {label} ===")
    print(f"omega = {omega.real:.6f} + {omega.imag:.6f}i")

    results = []
    for rm in match_points:
        pL, dL = integrate_L(omega, pot, r_match=rm)
        pR, dR = integrate_R(omega, pot, r_match=rm)
        if pL is None:
            print(f"  r_match={rm:.1f}: FAILED")
            continue

        W = dL * pR - pL * dR
        ratio_val = pL / pR if abs(pR) > 1e-30 else float('inf')
        ratio_der = dL / dR if abs(dR) > 1e-30 else float('inf')

        results.append((rm, np.abs(W), abs(ratio_val), abs(ratio_der)))
        print(f"  r_match={rm:.1f}: |W|={np.abs(W):.6e}, |pL/pR|={abs(ratio_val):.6e}, |dL/dR|={abs(ratio_der):.6e}")

    # Check consistency
    if len(results) >= 2:
        w1 = results[0][1]
        w2 = results[-1][1]
        rel_diff = abs(w1 - w2) / max(w1, w2, 1e-30)
        if rel_diff < 0.1:
            print(f"  -> Wronskian CONSISTENT (rel_diff={rel_diff:.4f})")
        else:
            print(f"  -> Wronskian DEPENDS on r_match (rel_diff={rel_diff:.4f})")

    return results

t0 = time.time()
# Test 1: My found scalar eigenvalue at multiple r_match
my_scalar = complex(0.273568, -0.026196)
match_check(my_scalar, pot_scalar, [10, 15, 20, 30, 50],
            "My scalar eigenvalue (0.273568 - 0.026196i)")

# Test 2: Berti scalar value at multiple r_match
berti_scalar = complex(0.27204, -0.03150)
match_check(berti_scalar, pot_scalar, [10, 15, 20, 30, 50],
            "Berti scalar (0.27204 - 0.03150i)")

# Test 3: Berti gravitational value at multiple r_match
berti_grav = complex(0.37367, -0.08896)
match_check(berti_grav, pot_grav_rw, [10, 15, 20, 30, 50],
            "Berti gravitational (0.37367 - 0.08896i)")

print(f"\nTotal time: {time.time()-t0:.1f}s")
