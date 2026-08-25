"""
更聪明的留数计算：
利用 1+n.u = A_u*(z-z1)*(z-z2)/(2z), 其中 A_u = ux*s   (u的二次型系数)
     1+n.v = A_v*(z-z3)*(z-z4)/(2z), 其中 A_v = s*(vx+i*vy)  (v的二次型系数)
这样 f_V(z) = numerator_V(z) / [i*z * one_plus_nu * one_plus_nv]

Res_{z=z1} f_V = lim_{z->z1} (z-z1)*f_V(z)
  = lim (z-z1)* numerator_V(z) / [i*z * A_u(z-z1)(z-z2)/(2z) * one_plus_nv(z)]
  = lim  numerator_V(z) * 2 / [i * A_u * (z-z2) * one_plus_nv(z)]
  = numerator_V(z1) * 2 / [i * A_u * (z1-z2) * one_plus_nv(z1)]

这样只需要代入 numerator_V(z1) 和 one_plus_nv(z1) 两次替换,不需要展开大多项式.
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv   # 不提前 expand，保持因式结构，加速代入

one_plus_nu = ux*s*(1+z**2)/(2*z) + uz*x + 1
one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1

A_u = ux*s
A_v = s*(vx + sp.I*vy)

z1 = -(1+uz)*(1+x) / (ux*s)
z2 = -(1-uz)*(1-x) / (ux*s)
z3 = -(1+vz)*(1+x) / (A_v)
z4 = -(1-vz)*(1-x) / (A_v)
z0 = sp.Integer(0)

def residue_at_u_pole(zk, z_other):
    """ z=z1 或 z2 (来自 1+n.u 的二次型因子) """
    t0=time.time()
    numV_at = numerator_V.subs(z, zk)
    onv_at  = one_plus_nv.subs(z, zk)
    expr = numV_at * 2 / (sp.I*A_u*(zk - z_other)*onv_at)
    print(f"  子表达式代入完成 {time.time()-t0:.2f}s，开始化简...")
    t1=time.time()
    res = sp.simplify(sp.together(expr))
    print(f"  化简完成 {time.time()-t1:.2f}s")
    return res

def residue_at_v_pole(zk, z_other):
    """ z=z3 或 z4 (来自 1+n.v 的二次型因子) """
    t0=time.time()
    numV_at = numerator_V.subs(z, zk)
    onu_at  = one_plus_nu.subs(z, zk)
    expr = numV_at * 2 / (sp.I*A_v*(zk - z_other)*onu_at)
    print(f"  子表达式代入完成 {time.time()-t0:.2f}s，开始化简...")
    t1=time.time()
    res = sp.simplify(sp.together(expr))
    print(f"  化简完成 {time.time()-t1:.2f}s")
    return res

print("="*60)
print("计算 R1^V = Res_{z=z1}")
R1 = residue_at_u_pole(z1, z2)
print("R1^V =")
sp.pprint(R1)

import pickle
with open('/home/user/chiral_orf_calc/R1V.pkl','wb') as f:
    pickle.dump(R1, f)
