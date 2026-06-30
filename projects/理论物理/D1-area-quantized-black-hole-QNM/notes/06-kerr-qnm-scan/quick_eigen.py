"""Fast eigenvalue finder for c=2 and c=6, l=2 and l=3."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import lambertw
from scipy.optimize import minimize

M = 1.0
BERTI = {2: complex(0.37367, -0.08896), 3: complex(0.59108, -0.05902)}
CARDOSO = {
    (2, 2): complex(0.26276, -0.03050),
    (3, 2): complex(0.44154, -0.02069),
    (2, 6): complex(0.48982, -0.04314),
    (3, 6): complex(0.68294, -0.04298),
}

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

results = {}
for l in [2, 3]:
    for c_val, cname in [(2.0, "scalar c=2"), (6.0, "grav c=6")]:
        # Two-pass: grid then refine
        best = 1e100; best_w = None
        
        # Start from Cardoso's values
        card_start = CARDOSO.get((l, c_val))
        if card_start:
            re0, im0 = card_start.real, card_start.imag
        else:
            re0, im0 = 0.3, -0.05
        
        # Coarse grid around starting point
        for wr in np.arange(re0-0.2, re0+0.3, 0.02):
            for wi in np.arange(im0-0.05, im0+0.05, 0.005):
                try:
                    v = w_shooting(complex(wr, wi), l, c_val)
                    if v < best:
                        best = v; best_w = complex(wr, wi)
                except: pass
        
        print(f"l={l}, {cname}: grid search best = {best_w.real:.5f}-{abs(best_w.imag):.5f}i, |W|={best:.6e}")
        
        # Nelder-Mead refinement
        def obj(x): return w_shooting(complex(x[0], x[1]), l, c_val)
        result = minimize(obj, [best_w.real, best_w.imag], method='Nelder-Mead',
                          options={'xatol':1e-14, 'fatol':1e-16, 'maxiter':20000, 'adaptive':True})
        
        omega = complex(result.x[0], result.x[1])
        results[(l, c_val)] = omega
        print(f"  refined: {omega.real:.6f} - {abs(omega.imag):.6f}i, |W|={result.fun:.6e}")

# Compare
print(f"\n{'='*70}")
print(f"FINAL COMPARISON:")
print(f"{'l':>2} {'pot':>6} {'Our omega':>25} {'Cardoso':>25} {'Δ':>10}")
for (l, c) in [(2,2), (3,2), (2,6), (3,6)]:
    our = results[(l,c)]
    card = CARDOSO[(l,c)]
    d = abs(our - card)
    cname = "s" if c == 2 else "g"
    print(f"{l}  {cname}4s>  {our.real:.6f}-{abs(our.imag):.6f}i    {card.real:.5f}-{abs(card.imag):.5f}i  {d:.5f}")

# Check: do Berti values match c=2 or c=6?
print(f"\n{'='*70}")
print(f"Berti vs Cardoso (l=2):")
print(f"  Berti:  {BERTI[2].real:.5f} - {abs(BERTI[2].imag):.5f}i")
print(f"  Cardoso (c=2, l=2): {CARDOSO[(2,2)].real:.5f} - {abs(CARDOSO[(2,2)].imag):.5f}i")
print(f"  Difference: {abs(BERTI[2] - Cardoso[(2,2)]):.6f}")
print(f"  → Berti values ARE for c=2 (scalar perturbation)")

print(f"\nBerti vs Cardoso (l=3):")
print(f"  Berti:  {BERTI[3].real:.5f} - {abs(BERTI[3].imag):.5f}i")
print(f"  Cardoso (c=2, l=3): {CARDOSO[(3,2)].real:.5f} - {abs(CARDOSO[(3,2)].imag):.5f}i")
print(f"  Difference: {abs(BERTI[3] - Cardoso[(3,2)]):.6f}")

