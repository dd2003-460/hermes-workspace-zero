"""
1. 用expand化简R0V（避免factor卡死），数值验证
2. 用sympy.residue()同法求 R3V, R4V (对v的两个极点)
3. 汇总所有5个留数并交叉验证与利用交换对称性得到的R3V,R4V是否一致
"""
import sympy as sp
import numpy as np
import time, pickle

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

t0=time.time()
R0V_sym = sp.residue(f_V, z, 0)
R0V_sym_expanded = sp.expand(R0V_sym)
print("R0V 符号residue + expand:", time.time()-t0, "s, ops=", sp.count_ops(R0V_sym_expanded))

# 数值交叉验证 (多组随机参数)
R0V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R0V_sym_expanded, modules='numpy')

def numerical_residue_z0(params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

np.random.seed(77)
print("\nR0V 多组随机数值检验:")
max_err = 0
for trial in range(5):
    xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec
    res_num = numerical_residue_z0((xv,sv,uxv,uzv,vxv,vyv,vzv))
    res_sym = R0V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    err = abs(res_num-res_sym)/max(abs(res_sym),1e-30)
    max_err = max(max_err, err)
    print(f"  trial{trial}: numeric={res_num:.5g}  symbolic={res_sym:.5g}  rel_err={err:.2e}")
print("最大误差:", max_err)

with open('/home/user/chiral_orf_calc/R0V_final.pkl','wb') as f:
    pickle.dump(R0V_sym_expanded, f)
