"""
Step 4c: 验证 z3, z4 —— 采用参数化代入法（比反复subs更稳健）
用球坐标参数化 u,v 为单位矢量，代入数值/符号方向余弦，直接验证。
"""
import sympy as sp
from sympy import I, sqrt, sin, cos, symbols, simplify, expand, nsimplify
import pickle

with open('/home/user/chiral_orf_calc/poles.pkl', 'rb') as f:
    d = pickle.load(f)

x, z = d['x'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
n_dot_u, n_dot_v = d['n_dot_u'], d['n_dot_v']
z1, z2, z3, z4 = d['z1'], d['z2'], d['z3'], d['z4']

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

# 用参数化: ux = sin(du), uz = cos(du); vx = sin(dv)*cos(psi), vy=sin(dv)*sin(psi), vz=cos(dv)
du, dv, psi = symbols('delta_u delta_v psi', real=True)

subs_u = {ux: sin(du), uz: cos(du)}
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

expr3 = one_plus_nv.subs(z, z3)
expr3_param = expr3.subs(subs_v).subs(subs_u)
expr3_simpl = sp.simplify(sp.trigsimp(expr3_param))
print("(1+n.v) at z=z3, 参数化后 =", expr3_simpl)

expr4 = one_plus_nv.subs(z, z4)
expr4_param = expr4.subs(subs_v).subs(subs_u)
expr4_simpl = sp.simplify(sp.trigsimp(expr4_param))
print("(1+n.v) at z=z4, 参数化后 =", expr4_simpl)

# 也用同样方法重新确认 z1, z2 (交叉验证前面结果)
expr1 = one_plus_nu.subs(z, z1).subs(subs_u)
print("\n(1+n.u) at z=z1, 参数化后 =", sp.simplify(sp.trigsimp(expr1)))
expr2 = one_plus_nu.subs(z, z2).subs(subs_u)
print("(1+n.u) at z=z2, 参数化后 =", sp.simplify(sp.trigsimp(expr2)))
