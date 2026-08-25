"""
重新构建：把 x 声明为实数符号 (real=True)，避免 re(x)/im(x) 混入
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, sin, cos, together, fraction

x = sp.symbols('x', real=True)
z = sp.symbols('z')   # z 在单位圆上是复数，不设实数
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

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

numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
numerator_V = sp.expand(numerator_V)

# 5个极点
z0 = sp.Integer(0)
z1 = -(1+uz)*(1+x) / (ux*sqrt(1-x**2))
z2 = -(1-uz)*(1-x) / (ux*sqrt(1-x**2))
z3 = -(1+vz)*(1+x) / ((vx - I*vy)*sqrt(1-x**2))
z4 = -(1-vz)*(1-x) / ((vx - I*vy)*sqrt(1-x**2))

one_plus_nu = 1 + n_dot_u
one_plus_nv = 1 + n_dot_v

du, dv, psi = sp.symbols('delta_u delta_v psi', real=True)
subs_u = {ux: sin(du), uz: cos(du)}
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

for name, expr, zk in [('z1',one_plus_nu,z1), ('z2',one_plus_nu,z2),
                        ('z3',one_plus_nv,z3), ('z4',one_plus_nv,z4)]:
    val = expr.subs(z, zk).subs(subs_v).subs(subs_u)
    val_s = sp.simplify(sp.expand_complex(val))
    print(f"(1+n.·) at {name} =", val_s)

import dill
with open('/home/user/chiral_orf_calc/real_data.pkl','wb') as f:
    dill.dump(dict(x=x,z=z,ux=ux,uz=uz,vx=vx,vy=vy,vz=vz,
                    theta_dot_u=theta_dot_u, phi_dot_u=phi_dot_u,
                    theta_dot_v=theta_dot_v, phi_dot_v=phi_dot_v,
                    n_dot_u=n_dot_u, n_dot_v=n_dot_v,
                    numerator_I=numerator_I, numerator_V=numerator_V,
                    z0=z0,z1=z1,z2=z2,z3=z3,z4=z4), f)
print("saved")
