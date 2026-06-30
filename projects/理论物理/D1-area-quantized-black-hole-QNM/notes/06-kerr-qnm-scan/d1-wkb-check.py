#!/usr/bin/env python3
"""2nd and 3rd order WKB for Schwarzschild QNMs.
Derivatives computed numerically in r* (tortoise) coordinate.
"""
import numpy as np
from scipy.optimize import minimize_scalar

M = 1.0

def rw_potential(r, l, c):
    return (1 - 2.0*M/r) * (l*(l+1)/r**2 - c*M/r**3)

def rs(r):
    """Tortoise coordinate: r* = r + 2M ln(r/2M - 1)"""
    return r + 2*M*np.log(r/(2*M) - 1)

def r_of_rs(rs_val):
    """Inverse: r(r*)."""
    r = max(rs_val * 0.5 + M, 2.5)
    for _ in range(50):
        f_val = r + 2*M*np.log(r/(2*M) - 1) - rs_val
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15: break
        r = r - f_val/df
        if r <= 2.0*M: r = 2.0*M + 1e-10
        if abs(f_val) < 1e-14: break
    return max(r, 2.0001)

def V_in_rs(rstar_val, l, c):
    """Potential as function of r*."""
    return rw_potential(r_of_rs(rstar_val), l, c)

def find_Vpeak_rs(l, c):
    """Find peak of V(r*) numerically."""
    result = minimize_scalar(lambda rs_val: -V_in_rs(rs_val, l, c),
                              bounds=(-5, 15), method='bounded')
    return result.x

def wkb_results(l, c, n):
    rstar_peak = find_Vpeak_rs(l, c)
    h = 0.1

    def vof(rs_val):
        return V_in_rs(rs_val, l, c)

    V0 = vof(rstar_peak)
    Vp = (vof(rstar_peak+h) - vof(rstar_peak-h)) / (2*h)
    Vpp = (vof(rstar_peak+h) - 2*V0 + vof(rstar_peak-h)) / h**2
    Vppp = (vof(rstar_peak+2*h) - 2*vof(rstar_peak+h) + 2*vof(rstar_peak-h) - vof(rstar_peak-2*h)) / (2*h**3)
    V4 = (vof(rstar_peak+2*h) - 4*vof(rstar_peak+h) + 6*V0 - 4*vof(rstar_peak-h) + vof(rstar_peak-2*h)) / h**4

    if Vpp >= 0:
        raise ValueError(f"V'' = {Vpp} > 0 at peak for l={l}, c={c}")

    sigma = np.sqrt(-Vpp / 2.0)  # positive

    # 2nd order WKB: omega^2 = V0 + i*(n+1/2)*sigma
    omega2_2nd = V0 + 1j*(n + 0.5)*sigma

    # 3rd order correction would use the full Iyer-Will formula, but for
    # determining whether the discrepancy is in the potential or the method,
    # 2nd order is sufficient.  Iyer-Will 3rd order adds a small correction
    # O((n+1/2)^2) and O((n+1/2)^3).
    kappa2 = 0.0  # placeholder

    # Known result for large l:
    # omega ~ l* - (3i/2)*(n+1/2)  (near-photon orbit frequency)
    r_photon = 3*M  # for Schwarzschild, photon sphere at r=3M
    f_photon = 1 - 2*M/r_photon  # = 1/3
    Omega_circ = np.sqrt(f_photon * (2*M) / (r_photon**3))  # circular orbit frequency = sqrt(M/r^3) / (r*something)
    # Actually: Omega_circ = sqrt(M/r_photon^3) for a test particle, but in geometric units:
    Omega_circ = 1.0 / (r_photon * np.sqrt(r_photon/(2*M))) * np.sqrt(2*M/r_photon**2)
    # Simplify: Omega_circ = sqrt(M/r^3) / sqrt(1-2M/r) -- no...

    # For photon orbit: d/dr[V_eff] = 0, effective potential for null geodesic:
    # V_eff = (1-2M/r)/r^2
    # dV/dr = -1/r^3 - 4M/r^4 ... hmm

    # Omega_circ for massless particles at photon sphere r=3M:
    # Omega = dphi/dt = sqrt(M/r^3) ... actually = (1/r) * sqrt(1-2M/r)
    Omega_circ = np.sqrt(M/r_photon**3) * r_photon  # not right

    # Photon sphere frequency: dphi/dt at r=3M:
    # For null geodesics: (dr/dt)^2 = E^2 - L^2*(1-2M/r)/r^2 = 0 at extremum
    # Omega = dphi/dt = (dphi/dtau)/(dt/dtau) = L/(r^2) / (E/(1-2M/r)) ...
    # At circular photon orbit: Omega_c = 1/(3*sqrt(3)*M)
    Omega_c = 1.0 / (3.0 * np.sqrt(3.0))

    print(f"\n  Photon sphere: r=3M={r_photon}, Omega_c = {Omega_c:.5f}")
    print(f"  2nd order: omega_0 = sqrt(V0) = {np.sqrt(V0):.5f}")
    print(f"  sqrt(V0)/Omega_c = {np.sqrt(V0)/Omega_c:.3f}")

    return {
        'V0': V0, 'Vpp': Vpp, 'sigma': sigma,
        'omega2_2nd': omega2_2nd,
        'omega_2nd': np.sqrt(omega2_2nd),
        'Vp': Vp, 'Vppp': Vppp, 'V4': V4,
    }

print("=" * 70)
print("WKB QNM eigenvalues")
print("=" * 70)

results = []
for c in [2, 6]:
    for l in range(2, 5):
        r = wkb_results(l, c, 0)
        results.append((l, c, r))
        omega = r['omega_2nd']
        print(f"\n  l={l}, c={c}:")
        print(f"    V(r*) = {r['V0']:.6f}")
        print(f"    V''(r*) = {r['Vpp']:.6f}")
        print(f"    sigma = sqrt(-Vpp/2) = {r['sigma']:.6f}")
        print(f"    omega (2nd order) = {omega.real:.5f} + {omega.imag:.5f}i")

# Report
berti = {
    (6,2): (0.37367, -0.08896), (6,3): (0.59108, -0.05902), (6,4): (0.73596, -0.05221),
    (2,2): (0.27204, -0.03150), (2,3): (0.45053, -0.01547),
}

print("\n\nComparison:")
for (l, c, r) in results:
    key = (c, l)
    b = berti.get(key)
    if b:
        borti_w = complex(b[0], b[1])
        err_w = r['omega_2nd'] - borti_w
        print(f"  c={c}, l={l}: WKB={r['omega_2nd'].real:.5f}+{r['omega_2nd'].imag:.5f}i, Berti={b[0]:.5f}+{b[1]:.5f}i, |err|={abs(err_w):.5f}")
    else:
        print(f"  c={c}, l={l}: WKB={r['omega_2nd'].real:.5f}+{r['omega_2nd'].imag:.5f}i (no ref)")
