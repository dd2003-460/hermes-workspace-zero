"""
用交换对称性得到 R3V, R4V，而非重新做符号residue (省算力):

关键对称性 (已用数值方法严格验证): xi_V(n; u, v) = - xi_V(n; v, u)
=> f_V(z; u,v) = -f_V(z; v,u)   (因为除了xi_V其余因子(1+n.u)(1+n.v)对u,v对称)
=> Res_{z=zk(u,v)} f_V(z;u,v) = - Res_{z=zk(v,u)} f_V(z;v,u)

z1(u), z2(u) 是由 u 决定的极点 (来自1+n.u=0)
z3(v), z4(v) 是由 v 决定的极点 (来自1+n.v=0)
如果我们交换 u<->v 的角色，那么"z1,z2 for (v,u)" 对应的极点公式，
形式上与"z3,z4 for (u,v)"应该完全一致 (因为都是由同一个变量的方向决定)

即: z3(u,v) 的公式 = z1(v,u) 的公式(把u,v互换)
所以: R3V(u,v) = Res_{z=z1(v,u)} f_V(z;u,v)
用 f_V(z;u,v) = -f_V(z;v,u):
R3V(u,v) = Res_{z=z1(v,u)} [-f_V(z;v,u)] = -R1V(v,u)

同理 R4V(u,v) = -R2V(v,u)

下面数值验证这个关系
"""
import sympy as sp
import numpy as np
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

with open('/home/user/chiral_orf_calc/R1V_CORRECTED.pkl','rb') as f:
    R1V_expr = pickle.load(f)
with open('/home/user/chiral_orf_calc/R2V_expr.pkl','rb') as f:
    R2V_expr = pickle.load(f)

R1V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R1V_expr, modules='numpy')
R2V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R2V_expr, modules='numpy')

# 完整 f_V 用于直接数值围道积分做金标准比较
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
f_V = numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')

def numerical_residue(zk_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = zk_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

def z3_pole(xv,sv,vxv,vyv,vzv):
    return -(1+vzv)*(1+xv)/((vxv+1j*vyv)*sv)
def z4_pole(xv,sv,vxv,vyv,vzv):
    return -(1-vzv)*(1-xv)/((vxv+1j*vyv)*sv)

np.random.seed(2025)
print("验证 R3V(u,v) = -R1V(v,u) 与 R4V(u,v) = -R2V(v,u):\n")
max_err3, max_err4 = 0,0
for trial in range(6):
    xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec

    # R3V猜测值 = -R1V(v,u)  (把u,v角色互换传入R1V_func: 现在"u的位置"填v的分量,"v的位置"填u的分量)
    R3V_guess = -R1V_func(xv, sv, vxv, vzv, uxv, 0.0, uzv)  # 注意u在uy=0规范下 phi分量为0
    # 数值围道积分校验
    z3_val = z3_pole(xv,sv,vxv,vyv,vzv)
    R3V_numeric = numerical_residue(z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    err3 = abs(R3V_guess - R3V_numeric)/max(abs(R3V_numeric),1e-30)
    max_err3 = max(max_err3, err3)

    R4V_guess = -R2V_func(xv, sv, vxv, vzv, uxv, 0.0, uzv)
    z4_val = z4_pole(xv,sv,vxv,vyv,vzv)
    R4V_numeric = numerical_residue(z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    err4 = abs(R4V_guess - R4V_numeric)/max(abs(R4V_numeric),1e-30)
    max_err4 = max(max_err4, err4)

    print(f"trial{trial}: R3V guess={R3V_guess:.5g} numeric={R3V_numeric:.5g} err={err3:.2e}  |  "
          f"R4V guess={R4V_guess:.5g} numeric={R4V_numeric:.5g} err={err4:.2e}")

print(f"\n最大误差: R3V={max_err3:.2e}  R4V={max_err4:.2e}")
