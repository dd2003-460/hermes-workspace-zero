"""
加速版流程: 用符号 s 代替 sqrt(1-x^2)，把所有运算变成纯有理函数代数(避免sympy处理根式的性能坑)
"""
import sympy as sp
from sympy import I, symbols, simplify, expand, together, cancel, fraction, Poly

x, s = sp.symbols('x s', real=True)   # s 代表 sqrt(1-x^2)，只在最后验证时用 s^2=1-x^2
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

# ---- 内积表达式，sqrt(1-x^2) 全部替换为 s ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
numerator_I = sp.expand(ePlus_uu*ePlus_vv + eCross_uu*eCross_vv)

one_plus_nu = sp.together(1 + n_dot_u)
one_plus_nv = sp.together(1 + n_dot_v)

# 把 f_V(z) 写成 P(z)/Q(z) 的形式 (Q应含有 z, one_plus_nu的分母, one_plus_nv的分母)
f_V_full = numerator_V / (I*z*one_plus_nu*one_plus_nv)
f_V_full = sp.together(f_V_full)
num_fV, den_fV = sp.fraction(f_V_full)
num_fV = sp.Poly(sp.expand(num_fV), z)
den_fV = sp.Poly(sp.expand(den_fV), z)
print("f_V(z) 分子关于z的次数:", num_fV.degree())
print("f_V(z) 分母关于z的次数:", den_fV.degree())

import pickle
with open('/home/user/chiral_orf_calc/fast_data.pkl','wb') as fp:
    pickle.dump(dict(x=x,s=s,z=z,ux=ux,uz=uz,vx=vx,vy=vy,vz=vz,
                      num_fV=num_fV.as_expr(), den_fV=den_fV.as_expr(),
                      numerator_V=numerator_V, numerator_I=numerator_I), fp)
print("saved fast_data.pkl")
