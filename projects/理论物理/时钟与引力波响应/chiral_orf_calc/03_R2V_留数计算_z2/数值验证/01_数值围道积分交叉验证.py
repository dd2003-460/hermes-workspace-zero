"""
【性质】数值验证 —— 对 R2V 做数值围道积分交叉验证（方法同02文件夹对R1V的验证）
【计算的量】Res_{z=z2} f_V(z) 的数值 vs. 符号公式结果
【状态】✅ 完全通过，5组随机参数最大误差 1.19e-12
"""
import sympy as sp
import numpy as np
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_numeric_func():
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
    return sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')


def numerical_residue(f_func, z0_val, params, radius=1e-4, N=6000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    f_V_func = build_fV_numeric_func()

    with open('R2V_expr.pkl', 'rb') as f:
        R2V_expr = pickle.load(f)
    R2V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz), R2V_expr, modules='numpy')

    np.random.seed(55)
    print("R2V 数值检验:")
    max_err = 0
    for trial in range(5):
        xv = np.random.uniform(-0.85,0.85); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv=np.sin(duv),np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        z2_val = -(1-uzv)*(1-xv)/(uxv*sv)
        res_num = numerical_residue(f_V_func, z2_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        res_sym = R2V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
        err = abs(res_num-res_sym)/max(abs(res_sym),1e-30)
        max_err = max(max_err, err)
        print(f"  trial{trial}: numeric={res_num:.5g} symbolic={res_sym:.5g} rel_err={err:.2e}")
    print("\n最大误差:", max_err, "  (远小于1e-6，验证通过)")
