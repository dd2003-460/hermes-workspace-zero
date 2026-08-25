"""
1. 计算 R0^V = Res_{z=0} f_V(z)
2. 用交换对称性 xi_V(u,v) = -xi_V(v,u) 推导 R3^V, R4^V 与 R1^V, R2^V 的关系并数值验证
"""
import sympy as sp
import numpy as np
import pickle

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
numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x

# ---- R0^V: z=0 是简单极点吗？先看 f_V(z)*z 在 z->0 的极限 ----
one_plus_nu = 1+n_dot_u
one_plus_nv = 1+n_dot_v
f_V = numerator_V/(sp.I*z*one_plus_nu*one_plus_nv)

# z*f_V(z) 在 z->0 时，需要先把含1/z的项处理干净。用级数展开
zf_V = sp.together(z*f_V)
num0, den0 = sp.fraction(zf_V)
num0 = sp.expand(num0)
den0 = sp.expand(den0)
# 提取den0关于z的最低次项，看看z=0是否是den0的零点 (若是，则需要更小心处理)
den0_poly = sp.Poly(den0, z)
print("den0 (关于z的多项式) 的最低次数项:", den0_poly.all_coeffs()[-3:])

# 直接用 limit
import time
t0=time.time()
R0V = sp.limit(zf_V, z, 0)
print("R0V via limit:", time.time()-t0, "s")
print("R0V =", R0V)

with open('/home/user/chiral_orf_calc/R0V.pkl','wb') as f:
    pickle.dump(R0V, f)
