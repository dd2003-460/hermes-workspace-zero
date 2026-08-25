"""
Step 4b: 代入单位矢量约束 ux^2+uz^2=1, vx^2+vy^2+vz^2=1 后重新验证极点
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, factor, sympify, Eq, solve
import pickle

with open('/home/user/chiral_orf_calc/poles.pkl', 'rb') as f:
    d = pickle.load(f)

x, z = d['x'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
n_dot_u, n_dot_v = d['n_dot_u'], d['n_dot_v']
z1, z2, z3, z4 = d['z1'], d['z2'], d['z3'], d['z4']

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

def check_with_unit_constraint(expr, is_u=True):
    """把 ux^2 -> 1-uz^2 (对u) 或 vx^2 -> 1-vz^2-vy^2 (对v) 代入化简"""
    expr = sp.together(expr)
    num, den = sp.fraction(expr)
    num = sp.expand(num)
    if is_u:
        # 用多项式除法消去 ux^2 = 1-uz^2
        num = num.as_poly(ux)
        if num is not None:
            q, r = sp.div(num.as_expr(), ux**2 - (1-uz**2), ux)
            num_reduced = sp.expand(r + q*(ux**2-(1-uz**2)))  # sanity, but really want just r modulo constraint
            # 更直接的方法：反复替换 ux**2 -> 1-uz**2
            num_e = sp.expand(num.as_expr())
            for _ in range(6):
                num_e = num_e.subs(ux**2, 1-uz**2)
                num_e = sp.expand(num_e)
            return sp.simplify(num_e)
    else:
        num_e = sp.expand(num)
        for _ in range(6):
            num_e = num_e.subs(vx**2, 1-vy**2-vz**2)
            num_e = sp.expand(num_e)
        return sp.simplify(num_e)

check1 = check_with_unit_constraint(one_plus_nu.subs(z, z1), is_u=True)
print("(1+n.u) at z=z1, 代入 ux^2=1-uz^2 后 =", check1)

check2 = check_with_unit_constraint(one_plus_nu.subs(z, z2), is_u=True)
print("(1+n.u) at z=z2, 代入 ux^2=1-uz^2 后 =", check2)
