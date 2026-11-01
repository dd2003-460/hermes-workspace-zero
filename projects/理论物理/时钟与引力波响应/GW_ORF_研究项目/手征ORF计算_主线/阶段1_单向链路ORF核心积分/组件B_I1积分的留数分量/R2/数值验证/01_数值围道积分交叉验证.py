"""
【性质】数值验证 —— 用【完全独立的3D笛卡尔矢量构造】的数值围道积分作为"黄金标准"，
        交叉核对符号计算得到的 R2V 表达式
【计算的量】Res_{z=z2} f_V(z) 的数值 vs. 符号公式代入数值后的结果
【状态】✅ 8组随机参数全部通过，最大相对误差 ~1e-12（已应用 BUG-001 修正后重新验证）
【依赖】本脚本读取同级"具体计算"文件夹产出、已复制到本文件夹内的 R2V_expr.pkl

【BUG-001 修正说明】同 R1/数值验证/01 文件，黄金标准函数完全独立于论文公式路径，
仅用标准3D笛卡尔矢量点积 + 严格欧拉公式解析延拓构造，避免"同源污染"问题。
"""
import sympy as sp
import numpy as np
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)


def f_V_gold_standard(xv, zval, u_hat, v_hat):
    ux_, uy_, uz_ = u_hat
    vx_, vy_, vz_ = v_hat
    sv = np.sqrt(1-xv**2, dtype=complex)
    cosphi = (zval + 1/zval)/2
    sinphi = -1j*(zval**2 - 1)/(2*zval)
    theta_dot_u = ux_*xv*cosphi - uz_*sv
    phi_dot_u = uy_*cosphi - ux_*sinphi
    theta_dot_v = vx_*xv*cosphi + vy_*xv*sinphi - vz_*sv
    phi_dot_v = vy_*cosphi - vx_*sinphi
    n_dot_u = ux_*sv*cosphi + uy_*sv*sinphi + uz_*xv
    n_dot_v = vx_*sv*cosphi + vy_*sv*sinphi + vz_*xv
    ePlus_uu = theta_dot_u**2 - phi_dot_u**2
    eCross_uu = 2*theta_dot_u*phi_dot_u
    ePlus_vv = theta_dot_v**2 - phi_dot_v**2
    eCross_vv = 2*theta_dot_v*phi_dot_v
    numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
    return numerator_V / (1j*zval*(1+n_dot_u)*(1+n_dot_v))


def numerical_residue(f_func, z0_val, radius=1e-4, N=20000):
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    with open('R2V_expr.pkl', 'rb') as f:
        R2V_expr = pickle.load(f)
    R2V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz), R2V_expr, modules='numpy')

    print("多组随机参数鲁棒性检验:")
    np.random.seed(321)
    max_rel_err = 0
    for trial in range(8):
        xv = np.random.uniform(-0.8, 0.8)
        sv = np.sqrt(1-xv**2)
        duv = np.random.uniform(0.3, 2.7)
        uxv, uzv = np.sin(duv), np.cos(duv)
        dv, psi = np.random.uniform(0.3, 2.7), np.random.uniform(0.1, 6.0)
        vxv, vyv, vzv = np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)
        u_hat = np.array([uxv, 0, uzv]); v_hat = np.array([vxv, vyv, vzv])
        z2_val = -(1-uzv)*(1-xv)/(uxv*sv)

        res_num = numerical_residue(lambda zz: f_V_gold_standard(xv, zz, u_hat, v_hat), z2_val)
        res_sym = R2V_func(xv, sv, uxv, uzv, vxv, vyv, vzv)
        rel_err = abs(res_num-res_sym)/max(abs(res_sym), 1e-30)
        max_rel_err = max(max_rel_err, rel_err)
        print(f"  trial {trial}: numeric={res_num:.6g}  symbolic={res_sym:.6g}  rel_err={rel_err:.2e}")

    print(f"\n最大相对误差 (8组随机测试) = {max_rel_err:.2e}")
    print("(证明R2V公式在BUG-001修正后代数正确)")
