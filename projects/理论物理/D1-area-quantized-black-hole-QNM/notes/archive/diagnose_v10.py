#!/usr/bin/env python3
"""诊断 NaN 源头"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')
np.set_printoptions(precision=12, suppress=True)

M = 1.0
l = 2
s = -2
x0 = 2.0
omega = complex(0.3737, -0.0890)

def alpha_func(z):
    return (z - x0) * (1 - 3 * z) / (z * (z + 1))

def beta_func(z):
    l2 = l * (l + 1)
    M2 = M * M
    V_eff = (l2 + (1 - s*s) * (z - 3)) / (4 * M2 * z * z * (z + 1))
    return 4 * M2 * omega**2 * (x0 / z)**2 - x0**2 * V_eff / (z * z * (z + 1))

def taylor_coeffs_contour(f, x0, n_terms, R=0.3, M_int=1024):
    theta = np.linspace(0, 2*np.pi, M_int, endpoint=False)
    z = x0 + R * np.exp(1j * theta)
    fval = f(z)
    coeffs = np.zeros(n_terms, dtype=complex)
    for n in range(n_terms):
        coeffs[n] = np.sum(fval * np.exp(-1j * n * theta)) / M_int / (R ** n)
    return coeffs

Nfrac = 100
n_terms = Nfrac + 5

alpha = taylor_coeffs_contour(alpha_func, x0, n_terms, R=0.3, M_int=1024)
beta = taylor_coeffs_contour(beta_func, x0, n_terms, R=0.3, M_int=1024)

gamma = 1.0 - 2.0j * omega * x0

A = np.zeros(Nfrac + 2, dtype=complex)
B = np.zeros(Nfrac + 2, dtype=complex)
C = np.zeros(Nfrac + 2, dtype=complex)

for n in range(Nfrac + 2):
    if n >= 1:
        A[n] = -0.5 * (alpha[n - 1] - beta[n - 1])
    B[n] = beta[n] - n * (n + 1 - gamma)
    C[n] = (n + 1) * (n + 1 - gamma)

# 连分数计算，追踪 NaN 源头
print("连分数计算追踪:")
D = 0.0 + 0.0j
first_nan = None

for n in range(Nfrac, 0, -1):
    if abs(D) < 1e-30:
        D = 1e-30 * (1 + 1e-10j)
    
    term = A[n + 1] * C[n] / D
    denom = B[n] - term
    
    if not np.isfinite(denom).all():
        print(f"  n={n}: 首次出现 NaN!")
        print(f"    B[{n}]={B[n]}")
        print(f"    A[{n+1}]={A[n+1]}")
        print(f"    C[{n}]={C[n]}")
        print(f"    D_prev={D}")
        print(f"    term=A*C/D={term}")
        print(f"    denom={denom}")
        first_nan = n
        break
    
    D = denom

# 检查 A, B, C 是否增长太快
print(f"\n检查 A, B, C 的范数:")
for check_n in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 101]:
    print(f"  n={check_n}: |A|={abs(A[check_n]):.6e}, |B|={abs(B[check_n]):.6e}, |C|={abs(C[check_n]):.6e}")
