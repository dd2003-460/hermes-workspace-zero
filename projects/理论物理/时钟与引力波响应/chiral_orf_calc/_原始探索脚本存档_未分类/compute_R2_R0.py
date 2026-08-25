"""
用同样高效流程计算 R2^V (z=z2的留数) 和 R0^V (z=0的留数)
"""
import sympy as sp
import time, pickle
import numpy as np

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

# ---------- R2^V: z=z2 ----------
z2 = -(1-uz)*(1-x) / (ux*s)

def sub_reduce(expr, zk):
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

t0=time.time()
tdu2 = sub_reduce(theta_dot_u_expr, z2)
pdu2 = sub_reduce(phi_dot_u_expr, z2)
tdv2 = sub_reduce(theta_dot_v_expr, z2)
pdv2 = sub_reduce(phi_dot_v_expr, z2)
print("z2 内积化简完成:", time.time()-t0)
print("theta.u|z2 =", tdu2)
print("phi.u|z2   =", pdu2)

ePlus_uu2  = sp.expand(tdu2**2 - pdu2**2)
eCross_uu2 = sp.expand(2*tdu2*pdu2)
ePlus_vv2  = sp.expand(tdv2**2 - pdv2**2)
eCross_vv2 = sp.expand(2*tdv2*pdv2)

numV_z2 = sp.expand(ePlus_uu2*eCross_vv2 - eCross_uu2*ePlus_vv2)
numV_z2_t = sp.together(numV_z2)
num2, den2 = sp.fraction(numV_z2_t)
num2 = sp.expand(num2); den2 = sp.expand(den2)
for _ in range(6):
    num2 = sp.expand(num2.subs(ux**2, 1-uz**2)); den2 = sp.expand(den2.subs(ux**2, 1-uz**2))
for _ in range(6):
    num2 = sp.expand(num2.subs(s**2, 1-x**2)); den2 = sp.expand(den2.subs(s**2, 1-x**2))
print("numerator_V(z2) 分母 =", den2)

onv_z2 = sub_reduce(s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1, z2)
print("one_plus_nv(z2) =", onv_z2)

z2_minus_z1 = -(-2*(uz+x)/(ux*s))  # = -(z1-z2)
R2V_expr = (num2/den2 * 2) / (sp.I * ux*s * z2_minus_z1 * onv_z2)

with open('/home/user/chiral_orf_calc/R2V_expr.pkl','wb') as f:
    pickle.dump(R2V_expr, f)

# 数值验证
R2V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R2V_expr, modules='numpy')

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
f_V = numerator_V / (sp.I*z*(1+n_dot_u)*(1+n_dot_v))
f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')

def numerical_residue(z0_val, params, radius=1e-4, N=6000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

np.random.seed(55)
print("\nR2V 数值检验:")
max_err=0
for trial in range(5):
    xv = np.random.uniform(-0.85,0.85); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv=np.sin(duv),np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec
    z2_val = -(1-uzv)*(1-xv)/(uxv*sv)
    res_num = numerical_residue(z2_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    res_sym = R2V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    err = abs(res_num-res_sym)/max(abs(res_sym),1e-30)
    max_err = max(max_err, err)
    print(f"  trial{trial}: numeric={res_num:.5g} symbolic={res_sym:.5g} rel_err={err:.2e}")
print("最大误差:", max_err)
