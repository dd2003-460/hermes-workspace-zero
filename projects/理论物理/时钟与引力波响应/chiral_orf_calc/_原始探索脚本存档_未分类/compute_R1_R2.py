"""
用角度参数化 (delta_u, delta_v, gamma) + 交换对称性，求 R1^V, R2^V (对应u的两个极点)。
R3^V, R4^V 由对称性 xi_V(u,v)=-xi_V(v,u) 直接得到 (在最后一步给出关系式，不需重新算)。

策略: 先把 f_V(z) 写成 numerator_V(z) / [i*z*(1+n.u)*(1+n.v)]，
利用 1+n.u = (ux*s)*(z-z1)*(z-z2)/(2z)  这一因式分解，
Res_{z=z1} f_V = numerator_V(z1) * 2 / [i * (ux*s) * (z1-z2) * (1+n.v)|_{z=z1}]
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)  # s = sin(theta) = sqrt(1-x^2) > 0 for theta in (0,pi)
z = sp.symbols('z')
du, dv, gam = sp.symbols('delta_u delta_v gamma', real=True, positive=True)

ux = sp.sin(du)
uz = sp.cos(du)
vz = sp.cos(dv)
vx = (sp.cos(gam) - sp.cos(du)*sp.cos(dv)) / sp.sin(du)
vy = sp.sqrt(sp.sin(gam)**2 - sp.cos(du)**2 - sp.cos(dv)**2 + 2*sp.cos(gam)*sp.cos(du)*sp.cos(dv)) / sp.sin(du)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv

one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1

z1 = -(1+uz)*(1+x) / (ux*s)
z2 = -(1-uz)*(1-x) / (ux*s)

print("开始计算 R1^V...")
t0 = time.time()
numV_z1 = sp.together(numerator_V.subs(z, z1))
print("  numerator_V at z1 substituted,", time.time()-t0, "s; size:", sp.count_ops(numV_z1))

t0 = time.time()
onv_z1 = sp.together(one_plus_nv.subs(z, z1))
print("  one_plus_nv at z1 substituted,", time.time()-t0, "s")

t0 = time.time()
R1V_raw = numV_z1 * 2 / (sp.I * ux*s * (z1-z2) * onv_z1)
R1V_raw = sp.together(R1V_raw)
print("  R1V_raw formed,", time.time()-t0, "s; size:", sp.count_ops(R1V_raw))

t0 = time.time()
R1V = sp.simplify(R1V_raw)
print("  R1V simplified,", time.time()-t0, "s")
print("\nR1^V =")
sp.pprint(R1V)

import pickle
with open('/home/user/chiral_orf_calc/R1V_result.pkl','wb') as f:
    pickle.dump(dict(R1V=R1V, x=x,s=s,du=du,dv=dv,gam=gam), f)
print("\n saved R1V_result.pkl")
