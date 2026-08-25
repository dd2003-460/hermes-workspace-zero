"""
用 sympy.residue() 计算 R3V (z=z3), R4V (z=z4)
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

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)
z4 = -(1-vz)*(1-x) / ((vx + sp.I*vy)*s)

def numerical_residue(zk_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = zk_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

print("计算 R3V via sympy.residue()...")
t0=time.time()
R3V_sym = sp.residue(f_V, z, z3)
print("完成:", time.time()-t0, "s, ops(未expand)=", sp.count_ops(R3V_sym))

print("\n计算 R4V via sympy.residue()...")
t0=time.time()
R4V_sym = sp.residue(f_V, z, z4)
print("完成:", time.time()-t0, "s, ops(未expand)=", sp.count_ops(R4V_sym))

# 数值验证
R3V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R3V_sym, modules='numpy')
R4V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R4V_sym, modules='numpy')

np.random.seed(31)
print("\nR3V, R4V 数值检验:")
max_err3, max_err4 = 0, 0
for trial in range(5):
    xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec
    z3_val = complex(z3.subs({x:xv,s:sv,vx:vxv,vy:vyv,vz:vzv}))
    z4_val = complex(z4.subs({x:xv,s:sv,vx:vxv,vy:vyv,vz:vzv}))

    res3_num = numerical_residue(z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    res3_sym = R3V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    err3 = abs(res3_num-res3_sym)/max(abs(res3_sym),1e-30)
    max_err3 = max(max_err3, err3)

    res4_num = numerical_residue(z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    res4_sym = R4V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    err4 = abs(res4_num-res4_sym)/max(abs(res4_sym),1e-30)
    max_err4 = max(max_err4, err4)

    print(f"  trial{trial}: R3V numeric={res3_num:.5g} symbolic={res3_sym:.5g} err={err3:.2e}  |  "
          f"R4V numeric={res4_num:.5g} symbolic={res4_sym:.5g} err={err4:.2e}")

print(f"\n最大误差: R3V={max_err3:.2e}  R4V={max_err4:.2e}")

with open('/home/user/chiral_orf_calc/R3V_R4V.pkl','wb') as f:
    pickle.dump(dict(R3V=R3V_sym, R4V=R4V_sym), f)
