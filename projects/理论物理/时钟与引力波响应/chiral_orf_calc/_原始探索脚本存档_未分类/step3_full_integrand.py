"""
Step 3: 构造完整被积函数 f(z) = (1/(iz)) * xi_V(x,z) / [(1+n.u)(1+n.v)]
并化为关于 z 的有理函数 P(z)/Q(z)，为寻找极点、算留数做准备。
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, together, cancel, fraction, Poly, factor
import pickle

with open('/home/user/chiral_orf_calc/xi_data.pkl', 'rb') as f:
    d = pickle.load(f)

x, z = d['x'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
n_dot_u, n_dot_v = d['n_dot_u'], d['n_dot_v']
numerator_V = d['numerator_V']

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

# xi_V(x,z) = numerator_V / [(1+n.u)(1+n.v)]
# f(z) = (1/(i*z)) * xi_V
f_z = numerator_V / (I*z*one_plus_nu*one_plus_nv)

# 化成 P(z)/Q(z) 有理函数形式 (通分)
f_z_together = together(f_z)
numer, denom = fraction(f_z_together)
numer = expand(numer)
denom = expand(denom)

print("分母 denom (应为 z, (1+n.u)*2z, (1+n.v)*2z 三部分乘积构成的多项式) ...")
print("denom 展开后长度:", len(str(denom)))
print()
print("denom 的因式分解:")
denom_factored = factor(denom)
print(denom_factored)

with open('/home/user/chiral_orf_calc/rational_form.pkl', 'wb') as fp:
    pickle.dump({**d, 'numer': numer, 'denom': denom, 'denom_factored': denom_factored}, fp)
print("\n已保存 rational_form.pkl")
