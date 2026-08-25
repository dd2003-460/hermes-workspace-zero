"""
用和R1V,R2V完全相同的高效方法(逐个内积化简再组装)计算 R3V (z=z3的留数)
"""
import sympy as sp
import numpy as np
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)

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
tdu3 = sub_reduce(theta_dot_u_expr, z3)
pdu3 = sub_reduce(phi_dot_u_expr, z3)
tdv3 = sub_reduce(theta_dot_v_expr, z3)
pdv3 = sub_reduce(phi_dot_v_expr, z3)
print("z3 内积化简完成:", time.time()-t0)
print("theta.v|z3 =", tdv3)
print("phi.v|z3   =", pdv3)

ePlus_uu3  = sp.expand(tdu3**2 - pdu3**2)
eCross_uu3 = sp.expand(2*tdu3*pdu3)
ePlus_vv3  = sp.expand(tdv3**2 - pdv3**2)
eCross_vv3 = sp.expand(2*tdv3*pdv3)

numV_z3 = sp.expand(ePlus_uu3*eCross_vv3 - eCross_uu3*ePlus_vv3)
numV_z3_t = sp.together(numV_z3)
num3, den3 = sp.fraction(numV_z3_t)
num3 = sp.expand(num3); den3 = sp.expand(den3)
for _ in range(6):
    num3 = sp.expand(num3.subs(ux**2, 1-uz**2)); den3 = sp.expand(den3.subs(ux**2, 1-uz**2))
for _ in range(6):
    num3 = sp.expand(num3.subs(s**2, 1-x**2)); den3 = sp.expand(den3.subs(s**2, 1-x**2))
print("numerator_V(z3) 分母:", den3)

# one_plus_nu at z3
onu_z3 = sub_reduce(ux*s*(1+z**2)/(2*z) + uz*x + 1, z3)
print("one_plus_nu(z3) =", onu_z3)

# z3-z4: 用韦达定理，同z1,z2的方法， 对v的二次型: 2z(1+n.v)=A_v*(z-z3)(z-z4), A_v=(vx+i*vy)*s
# sum=z3+z4=-2(vz*x+1)/A_v, prod=1
# (z3-z4)^2 = sum^2-4 = 4(vz*x+1)^2/A_v^2 - 4
# 类比z1,z2的推导: z3-z4 = -2(x+vz)/((vx+i*vy)*s)  (选取与z1-z2同样的符号约定)
z3_minus_z4 = -2*(x+vz)/((vx+sp.I*vy)*s)

A_v = (vx+sp.I*vy)*s
R3V_expr = (num3/den3 * 2) / (sp.I * A_v * z3_minus_z4 * onu_z3)

with open('/home/user/chiral_orf_calc/R3V_expr.pkl','wb') as f:
    pickle.dump(R3V_expr, f)

# 数值验证
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
R3V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R3V_expr, modules='numpy')

def numerical_residue(zk_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = zk_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_V_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

np.random.seed(303)
print("\nR3V 数值检验:")
max_err = 0
for trial in range(6):
    xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec
    z3_val = -(1+vzv)*(1+xv)/((vxv+1j*vyv)*sv)
    res_num = numerical_residue(z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    res_sym = R3V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    err = abs(res_num-res_sym)/max(abs(res_sym),1e-30)
    max_err = max(max_err, err)
    print(f"  trial{trial}: numeric={res_num:.5g} symbolic={res_sym:.5g} err={err:.2e}")
print("最大误差:", max_err)
