"""
完整流程（用修正后的正确极点公式）:
1. 构造 theta.u, phi.u, theta.v, phi.v, n.u, n.v
2. 构造对称核 xi_I (校验) 和反对称核 xi_V (目标)
3. 构造被积函数 f(z) = xi_V(x,z) / (i*z)
4. 用极限法在 5 个正确极点处求留数
5. 打印、化简，与宇称偶情形对比观察规律
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, limit, series, Rational, together, cancel

x = sp.symbols('x', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

# ---- 内积表达式 (PRD论文附录A式A6，uy=0规范) ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*sqrt(1-x**2)
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*sqrt(1-x**2)
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
n_dot_u = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
n_dot_v = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

# ---- 对称核(强度,校验用) 与 反对称核(手征,目标) ----
numerator_I = sp.expand(ePlus_uu*ePlus_vv + eCross_uu*eCross_vv)
numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

# 完整被积函数 (对应 PRD式15: f(z) = (1/iz)*xi(x,z))
denom_full = I*z*one_plus_nu*one_plus_nv
f_I = numerator_I/denom_full
f_V = numerator_V/denom_full

# ---- 5个极点 (修正后正确版本) ----
z0 = sp.Integer(0)
z1 = -(1+uz)*(1+x) / (ux*sqrt(1-x**2))
z2 = -(1-uz)*(1-x) / (ux*sqrt(1-x**2))
z3 = -(1+vz)*(1+x) / ((vx + I*vy)*sqrt(1-x**2))   # 修正: + 号
z4 = -(1-vz)*(1-x) / ((vx + I*vy)*sqrt(1-x**2))   # 修正: + 号

poles = {'z0': z0, 'z1': z1, 'z2': z2, 'z3': z3, 'z4': z4}

print("="*70)
print("求留数: Res_{z=zk} f_V(z) = lim_{z->zk} (z-zk)*f_V(z)")
print("="*70)

residues_V = {}
for name, zk in poles.items():
    expr = sp.together((z - zk) * f_V)
    # 直接代入 z=zk 化简 (对于可去奇点在(z-zk)相消后应能直接代入)
    res = sp.limit(expr, z, zk)
    res = sp.simplify(res)
    residues_V[name] = res
    print(f"\nR^V_{name[1]} = Res_{{z={name}}} f_V(z) =")
    sp.pprint(res)

import pickle
with open('/home/user/chiral_orf_calc/residues_V.pkl','wb') as fp:
    pickle.dump(residues_V, fp)
print("\n已保存留数结果")
