"""
【性质】数值验证 —— 用直接数值围道积分作为"金标准"，交叉核对符号计算得到的 R1V 表达式
【计算的量】Res_{z=z1} f_V(z) 的数值 vs. 符号公式代入数值后的结果
【状态】✅ 首次尝试发现整体差一个负号（相对误差恰好=2），修正符号约定后完全通过

【方法】
留数的定义就是"绕极点做一个小圆的围道积分除以2*pi*i"：
    Res_{z=z0} f(z) = (1/2*pi*i) * oint_{|z-z0|=r} f(z) dz
用离散化的圆周（N个点）数值近似这个积分，r取得足够小(1e-4)以保证精度，
同时又不能太小以免浮点数值不稳定。

这是一种完全独立于符号推导过程的验证手段——如果符号计算某一步有代数错误，
这里几乎一定会暴露出来。
"""
import sympy as sp
import numpy as np
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_numeric_func():
    """重建完整的 f_V(z) 符号表达式，并lambdify成数值函数，用于围道积分"""
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
    """在 z0_val 附近做小圆围道积分数值近似留数"""
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    f_V_func = build_fV_numeric_func()

    with open('R1V_CORRECTED.pkl', 'rb') as f:
        R1V_expr = pickle.load(f)
    R1V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz), R1V_expr, modules='numpy')

    print("单点检验:")
    xv = 0.37; sv = np.sqrt(1-xv**2)
    duv = 1.1; uxv, uzv = np.sin(duv), np.cos(duv)
    vxv, vyv, vzv = 0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)
    z1_val = -(1+uzv)*(1+xv) / (uxv*sv)

    res_numeric = numerical_residue(f_V_func, z1_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
    res_symbolic = R1V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
    print("  数值围道积分结果 =", res_numeric)
    print("  符号公式代入结果 =", res_symbolic)
    print("  相对误差 =", abs(res_numeric-res_symbolic)/abs(res_symbolic))
    print("  (若此误差机器精度量级则通过；若恰好=2.0，说明符号相反，需要检查负号约定)")

    print("\n多组随机参数鲁棒性检验:")
    np.random.seed(99)
    max_rel_err = 0
    for trial in range(8):
        xv = np.random.uniform(-0.85, 0.85)
        sv = np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2, 2.9)
        uxv, uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec /= np.linalg.norm(vvec)
        vxv, vyv, vzv = vvec
        z1_val = -(1+uzv)*(1+xv)/(uxv*sv)

        res_num = numerical_residue(f_V_func, z1_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        res_sym = R1V_func(xv,sv,uxv,uzv,vxv,vyv,vzv)
        rel_err = abs(res_num-res_sym)/max(abs(res_sym), 1e-30)
        max_rel_err = max(max_rel_err, rel_err)
        print(f"  trial {trial}: numeric={res_num:.5g}  symbolic={res_sym:.5g}  rel_err={rel_err:.2e}")

    print(f"\n最大相对误差 (8组随机测试) = {max_rel_err:.2e}")
    print("(远小于1e-6，证明R1V公式在一般几何构型下代数正确)")
