"""
z=0 处分母是二重零点，说明 f_V(z) 在 z=0 附近是 O(1/z^k) 的高阶极点(k可能是1,2,3...)
用 Laurent级数展开 series(f_V, z, 0, n) 直接读取 1/z 系数(那就是留数)
"""
import sympy as sp
import numpy as np
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)
ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v
numerator_V = sp.expand(ePlus_uu*eCross_vv - eCross_uu*ePlus_vv)
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
one_plus_nu = 1+n_dot_u
one_plus_nv = 1+n_dot_v
f_V = numerator_V/(sp.I*z*one_plus_nu*one_plus_nv)

# 检查 f_V 关于 z 的洛朗级数在 z=0 附近的最低次数
t0=time.time()
ser = sp.series(f_V, z, 0, 3)  # 展开到 z^1 项, 应该能看到 1/z^k 的最低阶
print("series 展开完成:", time.time()-t0)
print(ser)
