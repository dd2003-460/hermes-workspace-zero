"""
Find true eigenvalues using shooting method, then validate AIM formulations.
Tests c=2 and c=6 potentials for l=2 and l=3.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
from scipy.optimize import differential_evolution

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}

def r_from_rstar(rs):
    t = rs / (2.0 * M) - 1.0
    y_lw = np.real(lambertw(np.exp(t)))
    r = 2.0 * M * (1.0 + y_lw)
    for _ in range(40):
        rs_calc = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
        drstar_dr = r**2 / (r - 2.0 * M)**2
        dr = (rs_calc - rs) / drstar_dr
        if abs(dr) < 1e-14: break
        r -= dr
        if r <= 2.0 * M: r = 2.0 * M + 1e-14
    return r

def w_shooting(omega, l, c, rs_m=80):
    def deriv(rs, Y):
        r = r_from_rstar(rs)
        if r <= 2.0 * M + 1e-14: r = 2.0 * M + 1e-14
        f = 1.0 - 2.0 * M / r
        V = f * (l*(l+1)/r**2 - c*M/r**3)
        return [Y[1], -(omega**2 - V) * Y[0]]
    
    s1 = solve_ivp(deriv, [-60, rs_m], [1.0, -1j*omega], 
                   rtol=1e-10, atol=1e-12, max_step=0.3, dense_output=True)
    s2 = solve_ivp(deriv, [150, rs_m], [1.0, +1j*omega],
                   rtol=1e-10, atol=1e-12, max_step=0.3, dense_output=True)
    
    if not (s1.success and s2.success):
        return 1e100
    ph, dph = s1.sol(rs_m)
    pf, dpf = s2.sol(rs_m)
    return abs(ph * dpf - dph * pf)

def obj_scalar(x, l, c=2.0):
    return w_shooting(complex(x[0], x[1]), l, c)

def obj_grav(x, l, c=6.0):
    return w_shooting(complex(x[0], x[1]), l, c)

print("=" * 70)
print("Finding true eigenvalues via shooting method")
print("=" * 70)

results = {}
for l in [2, 3]:
    for c_name, c_val, fn in [("Scalar (c=2)", 2.0, obj_scalar),
                               ("Gravitational (c=6)", 6.0, obj_grav)]:
        # Wide optimization
        bounds = [(0.05, 1.5), (-0.3, -0.01)]
        result = differential_evolution(fn, bounds, args=(l, c_val),
                                        seed=42, maxiter=500, tol=1e-15,
                                        mutation=(0.5, 1.5), recombination=0.9)
        omega = complex(result.x[0], result.x[1])
        Wmin = result.fun
        
        results[(l, c_val)] = omega
        rel_err = abs(omega - BERTI[l]) / abs(BERTI[l])
        
        print(f"\nl={l}, {c_name}: omega = {omega.real:.6f} - {abs(omega.imag):.6f}i")
        print(f"  |W|_min = {Wmin:.6e}")
        print(f"  vs Berti (l={l}): |D| = {abs(omega - BERTI[l]):.6f} (rel: {rel_err*100:.1f}%)")

# Test with the known Cardoso reference values
print(f"\n{'='*70}")
print("Cardoso et al. (2000) reference check:")
CARDOSO = {
    (2, 2): complex(0.26276, -0.03050),  # c=2, l=2, n=0
    (3, 2): complex(0.44154, -0.02069),  # c=2, l=3, n=0
    (2, 6): complex(0.48982, -0.04314),  # c=6, l=2, n=0
    (3, 6): complex(0.68294, -0.04298),  # c=6, l=3, n=0
}
for (l, c), card_val in CARDOSO.items():
    my_val = results[(l, c)]
    err = abs(my_val - card_val)
    print(f"  c={c}, l={l}: Cardoso={card_val:.5f}, Ours={my_val.real:.5f}-{abs(my_val.imag):.5f}i, err={err:.6f}")

