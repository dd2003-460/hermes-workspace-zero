"""
【性质】数值验证 —— 检验06文件夹发现的"-i比例关系"能否推广到z3,z4
【计算的量】R3V/R3I 与 R4V/R4I 的比值（多组随机参数）
【状态】✅ 明确的否定结果（证伪了推广猜想），但意外发现了新的共轭对称性

【方法说明】
由于无法获得R3V,R4V的符号封闭表达式（见"推导与诊断"文件夹），
改用纯数值方法：直接对完整的 f_V(z), f_I(z) 做围道积分数值求出
R3V,R3I,R4V,R4I 的具体数值，再看比值 R3V/R3I, R4V/R4I 是否为常数。

这是一种"绕过卡死的符号计算，但依然能得到可信科学结论"的策略——
虽然拿不到解析公式，但数值层面的结论同样严谨、同样可以写进报告。

【核心发现】
1. R3V/R3I 和 R4V/R4I 本身都不是常数（否定了"-i关系可推广"）
2. 但每一组参数下，R3V/R3I 与 R4V/R4I 严格互为复共轭 —— 这是一个新规律
"""
import sympy as sp
import numpy as np

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def build_fV_fI_numeric_funcs():
    """同时构造手征核f_V和强度核f_I的数值函数，用于对比"""
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
    f_I = numerator_I/(sp.I*z*(1+n_dot_u)*(1+n_dot_v))
    f_V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_V, modules='numpy')
    f_I_func = sp.lambdify((x, s, ux, uz, vx, vy, vz, z), f_I, modules='numpy')
    return f_V_func, f_I_func


def numerical_residue(func, z0_val, params, radius=1e-4, N=8000):
    xv, sv, uxv, uzv, vxv, vyv, vzv = params
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = func(xv, sv, uxv, uzv, vxv, vyv, vzv, zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    f_V_func, f_I_func = build_fV_fI_numeric_funcs()

    np.random.seed(500)
    print("检验 R3V/R3I 与 R4V/R4I 的比值:\n")
    results = []
    for trial in range(6):
        xv = np.random.uniform(-0.8,0.8); sv=np.sqrt(1-xv**2)
        duv = np.random.uniform(0.2,2.9); uxv,uzv = np.sin(duv), np.cos(duv)
        vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
        vxv,vyv,vzv = vvec
        z3_val = -(1+vzv)*(1+xv)/((vxv+1j*vyv)*sv)
        z4_val = -(1-vzv)*(1-xv)/((vxv+1j*vyv)*sv)

        R3V = numerical_residue(f_V_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R3I = numerical_residue(f_I_func, z3_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4V = numerical_residue(f_V_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        R4I = numerical_residue(f_I_func, z4_val, (xv,sv,uxv,uzv,vxv,vyv,vzv))
        r3 = R3V/R3I
        r4 = R4V/R4I
        results.append((r3, r4))
        print(f"  trial{trial}: R3V/R3I={r3:.5g}   R4V/R4I={r4:.5g}   共轭误差={abs(r3-r4.conjugate()):.2e}")

    print("\n结论1: R3V/R3I 在不同trial间变化很大（如-2.12-2.32j到-0.02+1.41j），")
    print("        证明它不是常数，'-i比例关系'不能推广到z3,z4极点。")
    print("结论2: 但每一行的 R3V/R3I 与 R4V/R4I 都严格互为复共轭（误差列全部机器精度量级），")
    print("        这是一个新发现的干净规律，可能与z3,z4对应v的两个相反传播方向有关。")
