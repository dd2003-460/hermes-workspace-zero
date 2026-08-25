"""
采用 PRD 论文自己的角度参数化 (对应论文式13附近的说法："ORF只依赖 alpha, gamma, delta_u, delta_v 四个参数")：
  u_x = sin(delta_u),  u_z = cos(delta_u)
  v_z = cos(delta_v)
  v_x = (cos(gamma) - cos(delta_u)*cos(delta_v)) / sin(delta_u)
  v_y = sqrt(sin(gamma)^2 - cos(delta_u)^2 - cos(delta_v)^2 + 2*cos(gamma)*cos(delta_u)*cos(delta_v)) / sin(delta_u)

其中 cos(gamma) = u.v,  cos(delta_u) = u.s,  cos(delta_v) = v.s
这个参数化远比笛卡尔分量更紧凑，因为只有3个独立角度变量。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True)   # s = sqrt(1-x^2)
z = sp.symbols('z')
du, dv, gam = sp.symbols('delta_u delta_v gamma', real=True, positive=True)

ux = sp.sin(du)
uz = sp.cos(du)
vz = sp.cos(dv)
vx = (sp.cos(gam) - sp.cos(du)*sp.cos(dv)) / sp.sin(du)
vy_sq_arg = sp.sin(gam)**2 - sp.cos(du)**2 - sp.cos(dv)**2 + 2*sp.cos(gam)*sp.cos(du)*sp.cos(dv)
vy = sp.sqrt(vy_sq_arg) / sp.sin(du)

print("参数化设置完成: ux,uz,vx,vy,vz 均已用 delta_u, delta_v, gamma 表示")
print("vx =", vx)
print("vy =", vy)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = sp.together(theta_dot_u**2 - phi_dot_u**2)
eCross_uu = sp.together(2*theta_dot_u*phi_dot_u)
ePlus_vv  = sp.together(theta_dot_v**2 - phi_dot_v**2)
eCross_vv = sp.together(2*theta_dot_v*phi_dot_v)

t0 = time.time()
numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
print("构造 numerator_V (未展开) 用时", time.time()-t0)
print("count_ops (未展开):", sp.count_ops(numerator_V))

import pickle
with open('/home/user/chiral_orf_calc/angle_data.pkl','wb') as f:
    pickle.dump(dict(x=x,s=s,z=z,du=du,dv=dv,gam=gam,
                      ux=ux,uz=uz,vx=vx,vy=vy,vz=vz,
                      numerator_V=numerator_V), f)
print("saved")
