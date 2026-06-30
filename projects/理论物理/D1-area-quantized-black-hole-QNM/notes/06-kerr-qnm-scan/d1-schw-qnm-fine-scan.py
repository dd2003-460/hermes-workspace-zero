#!/usr/bin/env python3
"""
Fine scan around my eigenvalue to verify convergence and check for numerical issues.
"""
import numpy as np
from scipy.optimize import minimize

M = 1.0

def r_from_rstar(rs):
    r = max(rs * 0.5 + M, 2.5)
    for _ in range(30):
        f = r + 2*M*np.log(r/(2*M) - 1) - rs
        df = 1 + 2*M/(r - 2*M)
        if abs(df) < 1e-15:
            break
        r = r - f/df
        if r <= 2.0*M:
            r = 2.0*M + 1e-10
        if abs(f) < 1e-14:
            break
    return max(r, 2.0001)

def rw_potential(r, l, c_coeff):
    return (1 - 2*M/r) * (l*(l+1)/r**2 - c_coeff*M/r**3)

def integrate_bc(bc_type, rs_target, omega, l, c_coeff, Nsteps=5000):
    if bc_type == 'ingoing':
        rs_start = -50.0
        N = Nsteps
        drs = (rs_target - rs_start) / N
        psi = np.exp(-1j * omega * rs_start)
        dpsi = -1j * omega * psi
    else:
        rs_start = 70.0
        N = Nsteps
        drs = (rs_target - rs_start) / N
        psi = np.exp(1j * omega * rs_start)
        dpsi = 1j * omega * psi

    for _ in range(N):
        r = r_from_rstar(rs_start)
        V = rw_potential(r, l, c_coeff)
        k1_y = dpsi
        k1_d = -(omega**2 - V) * psi

        r = r_from_rstar(rs_start + drs/2)
        V = rw_potential(r, l, c_coeff)
        k2_y = dpsi + 0.5*drs*k1_d
        k2_d = -(omega**2 - V) * (psi + 0.5*drs*k1_y)

        r = r_from_rstar(rs_start + drs/2)
        V = rw_potential(r, l, c_coeff)
        k3_y = dpsi + 0.5*drs*k2_d
        k3_d = -(omega**2 - V) * (psi + 0.5*drs*k2_y)

        r = r_from_rstar(rs_start + drs)
        V = rw_potential(r, l, c_coeff)
        k4_y = dpsi + drs*k3_d
        k4_d = -(omega**2 - V) * (psi + drs*k3_y)

        psi += (drs/6) * (k1_y + 2*k2_y + 2*k3_y + k4_y)
        dpsi += (drs/6) * (k1_d + 2*k2_d + 2*k3_d + k4_d)

        if abs(psi) > 1e28:
            psi /= abs(psi) * 1e-27
            dpsi /= abs(psi) * 1e-27

    return psi, dpsi

def wronskian_norm(omega, l, c_coeff, Nsteps=5000):
    phi_h, dphi_h = integrate_bc('ingoing', 10.0, omega, l, c_coeff, Nsteps)
    phi_inf, dphi_inf = integrate_bc('outgoing', 10.0, omega, l, c_coeff, Nsteps)
    W = dphi_h * phi_inf - phi_h * dphi_inf
    norm = abs(phi_h) + abs(phi_inf) + abs(dphi_h) + abs(dphi_inf) + 1
    return abs(W) / norm

print("=" * 70)
print("Fine scan around c=6, l=2 minimum")
print("=" * 70)

# Around my found value
center = complex(0.548, -0.071)
for r in np.arange(center.real - 0.1, center.real + 0.11, 0.01):
    for i in np.arange(center.imag - 0.02, center.imag + 0.011, 0.002):
        w = complex(r, i)
        wn = wronskian_norm(w, 2, 6)
        if wn < 0.1:
            print(f"  omega={w.real:.3f}+{w.imag:.3f}i  |W|/norm={wn:.6e}")

# More precise refinement
print("\nNelder-Mead refinement (c=6, l=2):")
obj = lambda x: wronskian_norm(complex(x[0], x[1]), 2, 6)
r = minimize(obj, [0.548, -0.071],
             method='Nelder-Mead', options={'xatol': 1e-15, 'fatol': 1e-20, 'maxiter': 50000, 'adaptive': True})
omega_final = complex(r.x[0], r.x[1])
print(f"  omega = {omega_final.real:.10f} + {omega_final.imag:.10f}i")
print(f"  |W|/norm = {r.fun:.3e}")
print(f"  Berti:       0.37367 - 0.08896i")
print(f"  diff_Berti:  {omega_final.real - 0.37367:.6f} + {omega_final.imag - (-0.08896):.6f}i")

# Also test if increasing N improves convergence
print(f"\n  N=500:    {wronskian_norm(omega_final, 2, 6, 500):.6e}")
print(f"  N=1000:   {wronskian_norm(omega_final, 2, 6, 1000):.6e}")
print(f"  N=2000:   {wronskian_norm(omega_final, 2, 6, 2000):.6e}")
print(f"  N=5000:   {wronskian_norm(omega_final, 2, 6, 5000):.6e}")

# Check the Wronskian near Berti
print(f"\n  |W|/norm at Berti:          {wronskian_norm(complex(0.37367, -0.08896), 2, 6):.6e}")
print(f"  |W|/norm at Cardoso (old):  {wronskian_norm(complex(0.48982, -0.04314), 2, 6):.6e}")

print("\nNow for c=6, l=3:")
center3 = complex(0.523, -0.063)
for r in np.arange(center3.real - 0.15, center3.real + 0.21, 0.01):
    for i in np.arange(center3.imag - 0.02, center3.imag + 0.021, 0.002):
        w = complex(r, i)
        wn = wronskian_norm(w, 3, 6)
        if wn < 0.1:
            print(f"  omega={w.real:.3f}+{w.imag:.3f}i  |W|/norm={wn:.6e}")

obj3 = lambda x: wronskian_norm(complex(x[0], x[1]), 3, 6)
r3 = minimize(obj3, [0.523, -0.063],
             method='Nelder-Mead', options={'xatol': 1e-15, 'fatol': 1e-20, 'maxiter': 50000, 'adaptive': True})
omega_final3 = complex(r3.x[0], r3.x[1])
print(f"\n  omega = {omega_final3.real:.10f} + {omega_final3.imag:.10f}i")
print(f"  |W|/norm = {r3.fun:.3e}")
print(f"  Berti:       0.59108 - 0.05902i")
print(f"  diff_Berti:  {omega_final3.real - 0.59108:.6f} + {omega_final3.imag - (-0.05902):.6f}i")

print("\n=== Done ===")
