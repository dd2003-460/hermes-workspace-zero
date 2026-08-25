"""
用 sympy.residue() 内置函数直接求 z=0 处的留数 (它是为高阶极点设计的，比手动series更稳健)
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
f_V = numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))

# 为了让residue()好算，把数值代进去 (对通用符号公式太慢，先数值化交叉验证留数定义本身对不对)
xv=0.37; sv=np.sqrt(1-xv**2)
duv=1.1; uxv,uzv=np.sin(duv),np.cos(duv)
vxv,vyv,vzv=0.3,-0.5,np.sqrt(1-0.3**2-0.5**2)

f_V_numeric = f_V.subs({x:xv, s:sv, ux:uxv, uz:uzv, vx:vxv, vy:vyv, vz:vzv})
t0=time.time()
res0 = sp.residue(f_V_numeric, z, 0)
print("sympy.residue 计算 R0V (数值代入版):", time.time()-t0, "s")
print("R0V =", complex(res0))
print("(应与数值围道积分 9.632298+8.940529j 一致)")
