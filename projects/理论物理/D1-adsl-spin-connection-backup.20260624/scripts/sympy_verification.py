#!/usr/bin/env python3
"""
AdSL 引力 BTZ 黑洞 Spin Connection 运动方程验证
"""
from sympy import symbols, simplify, expand, Rational, diff

r, ell, M, J, b = symbols('r ell M J b', real=True)
ell2 = ell**2

# === 微分形式代数 ===
# 1-form: (f, g, h) = f*dv + g*dr + h*dphi
# 2-form: (A, B, C) = A*dv∧dr + B*dv∧dphi + C*dr∧dphi

def safe_diff(expr, var):
    if hasattr(expr, 'diff'):
        return expr.diff(var)
    return 0

def d_1form(f):
    """d(f*dv + g*dr + h*dphi) = (df/dr)*dr∧dv + (dg/dr)*dr∧dr + (dh/dr)*dr∧dphi
    = -(df/dr)*dv∧dr + (dh/dr)*dr∧dphi
    Returns 2-form: (-df/dr, 0, dh/dr)
    """
    return (-safe_diff(f[0], r), 0, safe_diff(f[2], r))

def wedge(a, b):
    """Wedge of two 1-forms → 2-form"""
    return (
        expand(a[0]*b[1] - a[1]*b[0]),
        expand(a[0]*b[2] - a[2]*b[0]),
        expand(a[1]*b[2] - a[2]*b[1])
    )

def add2(*fs):
    r = (0, 0, 0)
    for f in fs:
        r = (r[0]+f[0], r[1]+f[1], r[2]+f[2])
    return r

def smul(s, f):
    return (expand(s*f[0]), expand(s*f[1]), expand(s*f[2]))

def simp(f):
    return tuple(simplify(x) for x in f)

def is_zero(f):
    return all(simplify(x) == 0 for x in f)

# 指标升降 (η = antidiag(1,1,1))
def lower_idx(a):
    return (a[1], a[0], a[2])

# ε^{012} = -1 (det η = -1)
eps_up = {
    (0,1,2):-1, (0,2,1):1, (1,0,2):1, (1,2,0):-1, (2,0,1):-1, (2,1,0):1
}
# ε_{012} = +1
eps_dn = {
    (0,1,2):1, (0,2,1):-1, (1,0,2):-1, (1,2,0):1, (2,0,1):1, (2,1,0):-1
}

def eps_sum(eps_dict, a_idx, f_1forms, use_lower=False):
    """Compute ε^{a..} or ε_{a..} sum over wedge products of 1-forms"""
    result = (0, 0, 0)
    for b in range(3):
        for c in range(b+1, 3):
            key = (a_idx, b, c)
            e_val = eps_dict.get(key, 0)
            if e_val != 0:
                forms = f_1forms
                if use_lower:
                    forms = [lower_idx(x) for x in f_1forms]
                w = wedge(forms[b], forms[c])
                result = (result[0]+e_val*w[0], result[1]+e_val*w[1], result[2]+e_val*w[2])
    return result

# === 场定义 ===
e = [
    ((ell2*M - r**2)/(2*ell2), 1, -J/2),
    (1, 0, 0),
    (0, 0, r),
]

omega = [
    (0, 0, -b/2),
    (0, 0, 1),
    (0, 0, 0),
]

kappa = [
    (J/(2*ell2), 0, Rational(1,2)*(r**2/ell2 - M - b)),
    (0, 0, 0),
    (-r/ell2, 0, 0),
]

sigma = [(-kappa[i][0], -kappa[i][1], -kappa[i][2]) for i in range(3)]

omega_l = [lower_idx(omega[i]) for i in range(3)]
e_l = [lower_idx(e[i]) for i in range(3)]
sigma_l = [lower_idx(sigma[i]) for i in range(3)]

# ========== 方程 1: R_a = dω^a - (1/2)ε^{abc}ω_b∧ω_c = 0 ==========
print("=" * 60)
print("方程 1: R_a = 0 (几何曲率)")
print("=" * 60)

all_pass = True
for a in range(3):
    dw = d_1form(omega[a])  # = (0,0,0) since ω has constant coefficients
    corr = eps_sum(eps_up, a, omega_l, use_lower=False)
    corr = smul(Rational(-1, 2), corr)
    Ra = simp(add2(dw, corr))
    ok = is_zero(Ra)
    if not ok: all_pass = False
    print(f"  R^{{{a}}} = {Ra}  {'✓' if ok else '✗'}")
print(f"  总结: {'全部通过 ✓' if all_pass else '有非零分量 ✗'}")

# ========== 方程 2: T_a + ε_{abc}σ^b∧e^c = 0 ==========
# T_a = de_a - ε_{abc}ω^b∧e^c
print()
print("=" * 60)
print("方程 2: T_a + ε_{abc}σ^b∧e^c = 0 (修正挠率)")
print("=" * 60)

all_pass = True
for a in range(3):
    dea = d_1form(e_l[a])
    # T_a = de_a - ε_{abc}ω^b∧e^c (用上标 ω^b, e^c)
    corr_T = eps_sum(eps_dn, a, omega, use_lower=False)
    corr_T = smul(-1, corr_T)
    Ta = add2(dea, corr_T)

    # ε_{abc}σ^b∧e^c
    se = eps_sum(eps_dn, a, sigma, use_lower=False)

    total = simp(add2(Ta, se))
    ok = is_zero(total)
    if not ok: all_pass = False
    Ta_s = simp(Ta)
    se_s = simp(se)
    print(f"  a={a}: T_a={Ta_s}, σe={se_s}, total={total}  {'✓' if ok else '✗'}")
print(f"  总结: {'全部通过 ✓' if all_pass else '有非零分量 ✗'}")

# ========== 方程 3: F_a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0 ==========
# F^a = D_ωσ^a + (1/2)ε^{abc}σ_b∧σ_c
# D_ωσ^a = dσ^a - ε^{abc}ω_b∧σ_c
print()
print("=" * 60)
print("方程 3: F_a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0 (σ曲率)")
print("=" * 60)

all_pass = True
for a in range(3):
    dsa = d_1form(sigma[a])

    # D_ωσ^a = dσ^a - ε^{abc}ω_b∧σ_c
    corr_Dw = eps_sum(eps_up, a, sigma_l, use_lower=False)
    # ω_b are lowered: ω_l
    corr_Dw = (0, 0, 0)
    for b in range(3):
        for c in range(b+1, 3):
            key = (a, b, c)
            e_val = eps_up.get(key, 0)
            if e_val != 0:
                w = wedge(omega_l[b], sigma_l[c])
                corr_Dw = (corr_Dw[0]-e_val*w[0], corr_Dw[1]-e_val*w[1], corr_Dw[2]-e_val*w[2])
    Dw_sigma = add2(dsa, corr_Dw)

    # (1/2)ε^{abc}σ_b∧σ_c (using lowered σ)
    corr_ss = (0, 0, 0)
    for b in range(3):
        for c in range(b+1, 3):
            key = (a, b, c)
            e_val = eps_up.get(key, 0)
            if e_val != 0:
                w = wedge(sigma_l[b], sigma_l[c])
                corr_ss = (corr_ss[0]+Rational(1,2)*e_val*w[0],
                           corr_ss[1]+Rational(1,2)*e_val*w[1],
                           corr_ss[2]+Rational(1,2)*e_val*w[2])

    Fa_up = add2(Dw_sigma, corr_ss)
    Fa = lower_idx(Fa_up)

    # (1/2ℓ²)ε_{abc}e^b∧e^c
    ee = (0, 0, 0)
    for b in range(3):
        for c in range(b+1, 3):
            key = (a, b, c)
            e_val = eps_dn.get(key, 0)
            if e_val != 0:
                w = wedge(e[b], e[c])
                ee = (ee[0]+e_val*w[0], ee[1]+e_val*w[1], ee[2]+e_val*w[2])
    ee = smul(Rational(1, 2*ell2), ee)

    total = simp(add2(Fa, ee))
    ok = is_zero(total)
    if not ok: all_pass = False
    Fa_s = simp(Fa)
    ee_s = simp(ee)
    print(f"  a={a}: F_a={Fa_s}, ee/2ℓ²={ee_s}, total={total}  {'✓' if ok else '✗'}")
print(f"  总结: {'全部通过 ✓' if all_pass else '有非零分量 ✗'}")

print()
print("=" * 60)
print("全部验证完成")
print("=" * 60)
