"""
检验 R0V 与 R0I 之间是否也有类似简单比例关系 (哪怕不是常数比例,也看看是否有规律)
"""
import sympy as sp
import numpy as np

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
numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv

n_dot_u = ux*s*(1+z**2)/(2*z) + uz*x
n_dot_v = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x
f_V = numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
f_I = numerator_I/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))  # PRD论文原始定义没有32pi等前置系数，这里只看相对比例

# 数值代入后比较 R0V/R0I 的比值是否恒为某个简单虚数常数
f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')
f_I_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_I, modules='numpy')

def numerical_residue(func, z0_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)

np.random.seed(400)
print("R0V / R0I 的比值 (多组随机参数):")
for trial in range(6):
    xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
    duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    vxv,vyv,vzv = vvec
    R0V = numerical_residue(f_V_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    R0I = numerical_residue(f_I_func, 0.0, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    ratio = R0V/R0I
    print(f"  trial{trial}: R0V={R0V:.4g}  R0I={R0I:.4g}  ratio={ratio:.4g}")
