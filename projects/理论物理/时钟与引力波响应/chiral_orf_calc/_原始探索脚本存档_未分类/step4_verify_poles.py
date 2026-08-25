"""
Step 4: 定义 PRD 论文式(16)给出的5个极点，验证它们确实是 (1+n.u)=0 或 (1+n.v)=0 的根
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, sympify
import pickle

with open('/home/user/chiral_orf_calc/rational_form.pkl', 'rb') as f:
    d = pickle.load(f)

x, z = d['x'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
n_dot_u, n_dot_v = d['n_dot_u'], d['n_dot_v']

# PRD 论文 Eq.(16) 给出的5个极点
z0 = sp.Integer(0)
z1 = -(1+uz)*(1+x) / (ux*sqrt(1-x**2))
z2 = -(1-uz)*(1-x) / (ux*sqrt(1-x**2))
z3 = -(1+vz)*(1+x) / ((vx - I*vy)*sqrt(1-x**2))
z4 = -(1-vz)*(1-x) / ((vx - I*vy)*sqrt(1-x**2))

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

print("验证 z1 是 (1+n.u)=0 的根:")
check1 = simplify(one_plus_nu.subs(z, z1))
print("  (1+n.u) at z=z1  =", check1)

print("\n验证 z2 是 (1+n.u)=0 的根:")
check2 = simplify(one_plus_nu.subs(z, z2))
print("  (1+n.u) at z=z2  =", check2)

print("\n验证 z3 是 (1+n.v)=0 的根:")
check3 = simplify(one_plus_nv.subs(z, z3))
print("  (1+n.v) at z=z3  =", check3)

print("\n验证 z4 是 (1+n.v)=0 的根:")
check4 = simplify(one_plus_nv.subs(z, z4))
print("  (1+n.v) at z=z4  =", check4)

with open('/home/user/chiral_orf_calc/poles.pkl', 'wb') as fp:
    pickle.dump({**d, 'z0': z0, 'z1': z1, 'z2': z2, 'z3': z3, 'z4': z4}, fp)
