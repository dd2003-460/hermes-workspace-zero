"""
【性质】推导尝试（失败，但有诊断价值）—— 试图用交换对称性从R1V,R2V"偷懒"得到R3V,R4V
【计算的量】猜测 R3V(u,v) = -R1V(v,u), R4V(u,v) = -R2V(v,u)
【状态】❌ 失败：数值检验相对误差接近1（完全不匹配）

【失败原因分析】
06文件夹已经严格验证 xi_V(n;u,v) = -xi_V(n;v,u)（交换对称性成立）。
理论上，如果把 R1V,R2V 公式里 u,v 的角色互换（并加负号），
应该能得到 R3V,R4V —— 因为 z3,z4 (由v决定的极点) 和 z1,z2 (由u决定的极点)
在数学结构上是"同一件事情，把u,v互换角色而已"。

但直接这样做失败了。原因是：推导 R1V,R2V 时，我们特意选取了
"计算坐标系"使得 u 落在 x-z 平面内（u_y=0 的规范选择）。
这个规范选择破坏了 u,v 的完全对称性 —— R1V_func 的参数签名里，
"u的位置"这个参数槽默认预设了第三个分量(uy)为0，
而实际的v一般有非零的y分量。直接把v的三个分量硬塞进"u的位置"，
违反了推导时的坐标系前提，所以结果是错的。

这是一次有教训意义的失败：验证一个抽象的数学对称性成立，
不代表可以在具体的、带坐标系规范选择的参数化公式里直接套用。
"""
import sympy as sp
import numpy as np
import pickle


def numerical_residue(f_func, zk_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = zk_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)


def build_fV_numeric_func():
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
    f_V = numerator_V/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
    return sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')


if __name__ == "__main__":
    x, s = sp.symbols('x s', real=True, positive=True)
    ux, uz = sp.symbols('u_x u_z', real=True)
    vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

    with open('R1V_CORRECTED.pkl', 'rb') as f:
        R1V_expr = pickle.load(f)
    with open('R2V_expr.pkl', 'rb') as f:
        R2V_expr = pickle.load(f)
    R1V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R1V_expr, modules='numpy')
    R2V_func = sp.lambdify((x,s,ux,uz,vx,vy,vz), R2V_expr, modules='numpy')
    f_V_func = build_fV_numeric_func()

    def z3_pole(xv,sv,vxv,vyv,vzv):
        return -(1+vzv)*(1+xv)/((vxv+1j*vyv)*sv)

    np.random.seed(2025)
    print("验证猜想 R3V(u,v) = -R1V(v,u) —— 结果应显示严重不匹配:\n")
    for trial in range(3):
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec

        # 错误的尝试: 直接把v的分量塞进u的位置(忽略了uy=0的坐标系约定)
        R3V_guess = -R1V_func(xv, sv, vxv, vzv, uxv, 0.0, uzv)
        z3_val = z3_pole(xv,sv,vxv,vyv,vzv)
        R3V_numeric = numerical_residue(f_V_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        err = abs(R3V_guess - R3V_numeric)/max(abs(R3V_numeric),1e-30)
        print(f"trial{trial}: guess={R3V_guess:.5g}  numeric(金标准)={R3V_numeric:.5g}  相对误差={err:.2e}")

    print("\n结论: 相对误差接近1，说明这个'偷懒'的交换代入方法是错误的。")
    print("根本原因: R1V,R2V的推导预设了u落在xz平面(uy=0)，")
    print("直接对调u,v的笛卡尔分量违反了这个坐标系前提。")
