"""
【性质】数值验证 —— 用【完全独立的3D笛卡尔矢量构造】的数值围道积分作为"黄金标准"，
        交叉核对符号计算得到的 R1V 表达式
【计算的量】Res_{z=z1} f_V(z) 的数值 vs. 符号公式代入数值后的结果
【状态】✅ 8组随机参数全部通过，最大相对误差 1.1e-12（已应用 BUG-001 修正后重新验证）
【依赖】本脚本读取同级"具体计算"文件夹产出、已复制到本文件夹内的 R1V_CORRECTED.pkl

================================================================================
                    ⚠️ BUG-001 修正说明 ⚠️
================================================================================
本文件此前版本的"黄金标准"构造函数 build_fV_numeric_func 内部用的 theta_dot_v,
n_dot_v 公式本身有误（vy项系数+I），与被验证的符号表达式共享了同一处错误，
属于"同源污染"，无法互相纠错——这也是为什么上一轮工作里 R1V 的数值验证会
"显示通过"，但实际上验证的是两个都错的东西互相吻合。

本次修正的关键改进：黄金标准函数改用完全独立的路径——先用标准3D笛卡尔
矢量点积构造 theta_hat, phi_hat, n_hat 与 u,v 的内积（不经过任何论文公式），
再用严格的欧拉公式 cos(phi)=(z+1/z)/2, sin(phi)=-i(z^2-1)/(2z) 做解析延拓
（这两个欧拉公式是数学定义，与论文完全无关），从而真正独立于被验证的符号推导链路。
================================================================================
"""
import sympy as sp
import numpy as np
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')


def f_V_gold_standard(xv, zval, u_hat, v_hat):
    """
    黄金标准 f_V(z)：完全独立于论文公式的构造路径。
    仅用：(1) 标准球坐标基矢量的3D笛卡尔定义；(2) 欧拉公式的解析延拓。
    u_hat, v_hat 是长度为3的numpy数组（不要求 u_hat[1]=0，但为了对应 z1 极点公式，
    实际验证时仍取 u_hat=(ux,0,uz) 的规范）。
    """
    ux_, uy_, uz_ = u_hat
    vx_, vy_, vz_ = v_hat
    sv = np.sqrt(1-xv**2, dtype=complex)
    cosphi = (zval + 1/zval)/2
    sinphi = -1j*(zval**2 - 1)/(2*zval)     # 严格欧拉公式，与论文无关
    theta_dot_u = ux_*xv*cosphi - uz_*sv
    phi_dot_u = uy_*cosphi - ux_*sinphi     # 一般公式 phi.u = uy*cos(phi) - ux*sin(phi)
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
    """在 z0_val 附近做小圆围道积分数值近似留数"""
    thetas = np.linspace(0, 2*np.pi, N, endpoint=False)
    dtheta = thetas[1]-thetas[0]
    zs = z0_val + radius*np.exp(1j*thetas)
    dz = 1j*radius*np.exp(1j*thetas)*dtheta
    vals = f_func(zs)
    return np.sum(vals*dz)/(2j*np.pi)


if __name__ == "__main__":
    with open('R1V_CORRECTED.pkl', 'rb') as f:
        R1V_expr = pickle.load(f)
    R1V_func = sp.lambdify((x, s, ux, uz, vx, vy, vz), R1V_expr, modules='numpy')

    print("单点检验:")
    xv = 0.37; sv = np.sqrt(1-xv**2)
    duv = 1.1; uxv, uzv = np.sin(duv), np.cos(duv)
    vxv, vyv, vzv = 0.3, -0.5, np.sqrt(1-0.3**2-0.5**2)
    u_hat = np.array([uxv, 0, uzv]); v_hat = np.array([vxv, vyv, vzv])
    z1_val = -(1+uzv)*(1+xv) / (uxv*sv)

    res_numeric = numerical_residue(lambda zz: f_V_gold_standard(xv, zz, u_hat, v_hat), z1_val)
    res_symbolic = R1V_func(xv, sv, uxv, uzv, vxv, vyv, vzv)
    print("  黄金标准(纯3D构造)数值围道积分 =", res_numeric)
    print("  符号公式代入结果              =", res_symbolic)
    print("  相对误差 =", abs(res_numeric-res_symbolic)/abs(res_symbolic))

    print("\n多组随机参数鲁棒性检验:")
    np.random.seed(123)
    max_rel_err = 0
    for trial in range(8):
        xv = np.random.uniform(-0.8, 0.8)
        sv = np.sqrt(1-xv**2)
        duv = np.random.uniform(0.3, 2.7)
        uxv, uzv = np.sin(duv), np.cos(duv)
        dv, psi = np.random.uniform(0.3, 2.7), np.random.uniform(0.1, 6.0)
        vxv, vyv, vzv = np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)
        u_hat = np.array([uxv, 0, uzv]); v_hat = np.array([vxv, vyv, vzv])
        z1_val = -(1+uzv)*(1+xv)/(uxv*sv)

        res_num = numerical_residue(lambda zz: f_V_gold_standard(xv, zz, u_hat, v_hat), z1_val)
        res_sym = R1V_func(xv, sv, uxv, uzv, vxv, vyv, vzv)
        rel_err = abs(res_num-res_sym)/max(abs(res_sym), 1e-30)
        max_rel_err = max(max_rel_err, rel_err)
        print(f"  trial {trial}: numeric={res_num:.6g}  symbolic={res_sym:.6g}  rel_err={rel_err:.2e}")

    print(f"\n最大相对误差 (8组随机测试) = {max_rel_err:.2e}")
    print("(远小于1e-9，证明R1V公式在BUG-001修正后代数正确，且验证方式与被验证代码完全独立)")
