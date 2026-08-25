"""
先测试一个重要的物理特例: 共面构型 (vy=0)，即 u,v,s 三矢量共面。
这是楼明智论文和很多现有文献里最常用的构型（s·m12=0条件），
自由度从(ux,uz,vx,vy,vz)5个减到(ux,uz,vx,vz)4个，看计算量是否可控。
"""
import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vz = sp.symbols('v_x v_z', real=True)
vy = 0   # 共面特例

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
print("numerator_V (vy=0情形) ops=", sp.count_ops(numerator_V))
print(numerator_V)
