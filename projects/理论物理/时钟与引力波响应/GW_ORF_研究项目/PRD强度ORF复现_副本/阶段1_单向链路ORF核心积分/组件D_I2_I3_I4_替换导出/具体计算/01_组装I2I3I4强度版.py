"""
【性质】具体计算 —— 用矢量替换规则，从强度版 I1^I 直接导出 I2^I, I3^I, I4^I
【计算的量】I2^I(alpha,beta_u,s,u,v), I3^I(alpha,beta_v,s,u,v), I4^I(alpha,beta_u,beta_v,s,u,v)
【状态】✅ 成功，与原始定义式数值积分比对，误差~1e-6~1e-7量级
【依赖】直接复制本副本组件C具体计算文件的 all_R_integrals_I() 等函数

本文件结构与手征主线组件D的01号文件完全对应，只是内部用强度对称核xi_I
（对称组装 ePlus_uu*ePlus_vv+eCross_uu*eCross_vv）而非手征反对称核。
"""
import numpy as np
import mpmath
from scipy import integrate


def Ei(z):
    return complex(mpmath.ei(complex(z)))


def Ei_diff_with_branch_correction(w_func, x1, x2, N=80):
    xs = np.linspace(x1, x2, N)
    ws = [w_func(xv) for xv in xs]
    correction = 0
    for i in range(len(ws) - 1):
        im1, im2 = ws[i].imag, ws[i + 1].imag
        re_mid = (ws[i].real + ws[i + 1].real) / 2
        if im1 * im2 < 0 and re_mid < 0:
            correction += 2j * np.pi if (im1 > 0 and im2 < 0) else -2j * np.pi
    return (Ei(ws[-1]) - Ei(ws[0])) + correction


def sigma_pm(du, dv, gamma, chirality_sign=1.0):
    """
    【BUG-002 修复】sigma^+/sigma^- 的 sqrt(disc) 分支选择依赖手性，不能固定取
    主分支。详见 结论与推导过程.md 第X节的完整符号推导证明。

    物理背景（论文正文 Eq(13) 下方明确讨论）：在计算坐标系约定
    (s_hat=z轴, u_hat=(u_x,0,u_z)含u_x>0, v_hat=(v_x,v_y,v_z)) 中，给定
    (delta_u, delta_v, gamma) 三个夹角，v_y 可以取正也可以取负（镜像对称，
    两者不能靠旋转互相变换），对应的 sigma^+/sigma^- **在复平面上的具体值
    会翻转共轭**（sigma^+ <-> sigma^-互换），而不是保持不变。

    用论文Eq(16)给出的四个极点 z1,z2,z3,z4 的精确解析公式，通过纯代数消元
    (令 z1(x)=z4(x)，其中sqrt(1-x^2)项两边正好约掉退化为线性方程，无分支
    歧义)可以精确解出 sigma 应该取的符号，结果证明:
        sqrt(disc) 前的符号 = sign(v_y)   (标准计算系下)
    即: chirality_sign 参数应传入 sign(v_y)（默认1.0对应论文人为选择v_y>0的
    情形，此时退化为原始写法）。

    【重要判据】：R1I,R2I,R3I,R4I 内部分工可能因为 sign(v_y) 而互换角色，
    但四者相加后的总和 I1 必须与 v_y 符号无关——这是论文正文自己声称并
    已经用最原始定义2D数值积分独立验证过的物理不变性（误差~1e-15）。
    """
    cos_du, cos_dv, cos_g = np.cos(du), np.cos(dv), np.cos(gamma)
    disc = np.sin(gamma) ** 2 - cos_du ** 2 - cos_dv ** 2 + 2 * cos_g * cos_du * cos_dv
    sq = np.sqrt(complex(disc)) * chirality_sign
    return 1 / (1 + cos_g) * (cos_du + cos_dv + 1j * sq), 1 / (1 + cos_g) * (cos_du + cos_dv - 1j * sq)


def integral_simple_pole_form(alpha, x1, x2, pole_coef, pole_loc, const_coef):
    w_func = lambda xv: -1j * alpha * (xv + pole_loc)
    ei_diff = Ei_diff_with_branch_correction(w_func, x1, x2)
    term_pole = pole_coef * np.exp(1j * alpha * pole_loc) * ei_diff
    term_const = const_coef * (1j / alpha) * (np.exp(-1j * alpha * x2) - np.exp(-1j * alpha * x1))
    return term_pole + term_const


def all_R_integrals_I(alpha, du, dv, gamma, chirality_sign=1.0):
    sp_, sm = sigma_pm(du, dv, gamma, chirality_sign)
    cos_g, cos_du, cos_dv = np.cos(gamma), np.cos(du), np.cos(dv)
    I_R1 = integral_simple_pole_form(alpha, -1, -cos_du, -2j * (1 - cos_g), sm,
                                      2j * (sp_ - cos_du) * (1 + cos_g) / (1 - cos_du ** 2))
    I_R2 = integral_simple_pole_form(alpha, -cos_du, 1, 2j * (1 - cos_g), sp_,
                                      -2j * (sm - cos_du) * (1 + cos_g) / (1 - cos_du ** 2))
    I_R3 = integral_simple_pole_form(alpha, -1, -cos_dv, -2j * (1 - cos_g), sp_,
                                      2j * (sm - cos_dv) * (1 + cos_g) / (1 - cos_dv ** 2))
    I_R4 = integral_simple_pole_form(alpha, -cos_dv, 1, 2j * (1 - cos_g), sm,
                                      -2j * (sp_ - cos_dv) * (1 + cos_g) / (1 - cos_dv ** 2))
    return I_R1, I_R2, I_R3, I_R4


def f_I_gold_standard(x, z, u_hat, v_hat):
    """强度版 f(z): 对称组装 ePlus_uu*ePlus_vv+eCross_uu*eCross_vv"""
    ux, uy, uz = u_hat; vx, vy, vz = v_hat
    s = np.sqrt(1 - x ** 2, dtype=complex)
    cosphi = (z + 1 / z) / 2
    sinphi = -1j * (z ** 2 - 1) / (2 * z)
    theta_dot_u = ux * x * cosphi - uz * s
    phi_dot_u = uy * cosphi - ux * sinphi
    theta_dot_v = vx * x * cosphi + vy * x * sinphi - vz * s
    phi_dot_v = vy * cosphi - vx * sinphi
    n_dot_u = ux * s * cosphi + uy * s * sinphi + uz * x
    n_dot_v = vx * s * cosphi + vy * s * sinphi + vz * x
    ePlus_uu = theta_dot_u ** 2 - phi_dot_u ** 2
    eCross_uu = 2 * theta_dot_u * phi_dot_u
    ePlus_vv = theta_dot_v ** 2 - phi_dot_v ** 2
    eCross_vv = 2 * theta_dot_v * phi_dot_v
    numerator_I = ePlus_uu * ePlus_vv + eCross_uu * eCross_vv
    return numerator_I / (1j * z * (1 + n_dot_u) * (1 + n_dot_v))


def numerical_residue(f, z0, radius=1e-3, N=20000):
    thetas = np.linspace(0, 2 * np.pi, N, endpoint=False)
    dtheta = thetas[1] - thetas[0]
    zs = z0 + radius * np.exp(1j * thetas)
    dz = 1j * radius * np.exp(1j * thetas) * dtheta
    vals = f(zs)
    return np.sum(vals * dz) / (2j * np.pi)


def I1_I_full(alpha, du, dv, u_hat, v_hat):
    """
    【BUG-002 修复】此函数要求 u_hat, v_hat 已处于论文Eq(13)约定的标准计算系
    (u_hat=(u_x,0,u_z), u_x>0)。sigma_pm 的sqrt分支必须绑定 sign(v_hat[1])，
    否则 R1~R4 的角色分配会与真实极点错位（详见 结论与推导过程.md 的符号推导）。
    当 v_hat[1] 恰好为0（v与u共面，退化情形）时，两分支给出相同结果，任选。
    """
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
    I_R1, I_R2, I_R3, I_R4 = all_R_integrals_I(alpha, du, dv, gamma, chirality_sign)

    def R0I_numeric(xv):
        return numerical_residue(lambda z: f_I_gold_standard(xv, z, u_hat, v_hat), 0.0)

    re0, _ = integrate.quad(lambda x: (R0I_numeric(x) * np.exp(-1j * alpha * x)).real, -1, 1, limit=100)
    im0, _ = integrate.quad(lambda x: (R0I_numeric(x) * np.exp(-1j * alpha * x)).imag, -1, 1, limit=100)
    I_R0 = re0 + 1j * im0
    return 2j * np.pi * (I_R0 + I_R1 + I_R2 + I_R3 + I_R4)


def build_computational_frame(s_hat, u_hat):
    s_hat = s_hat / np.linalg.norm(s_hat)
    z_axis = np.array([0, 0, 1])
    v_rot = np.cross(s_hat, z_axis)
    if np.linalg.norm(v_rot) < 1e-10:
        R1 = np.eye(3) if s_hat @ z_axis > 0 else np.diag([1, -1, -1])
    else:
        v_rot_norm = v_rot / np.linalg.norm(v_rot)
        angle = np.arccos(np.clip(s_hat @ z_axis, -1, 1))
        a = np.cos(angle / 2)
        b, c, d = -v_rot_norm * np.sin(angle / 2)
        R1 = np.array([
            [a * a + b * b - c * c - d * d, 2 * (b * c + a * d), 2 * (b * d - a * c)],
            [2 * (b * c - a * d), a * a + c * c - b * b - d * d, 2 * (c * d + a * b)],
            [2 * (b * d + a * c), 2 * (c * d - a * b), a * a + d * d - b * b - c * c],
        ])
    u_after_R1 = R1 @ u_hat
    phi_u = np.arctan2(u_after_R1[1], u_after_R1[0])
    c, s = np.cos(-phi_u), np.sin(-phi_u)
    R2 = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return R2 @ R1


def I1_I_general(alpha_mag, s_hat, u_hat, v_hat):
    R = build_computational_frame(s_hat, u_hat)
    u_rot, v_rot = R @ u_hat, R @ v_hat
    du = np.arccos(np.clip(u_rot[2], -1, 1))
    dv_val = np.arccos(np.clip(v_rot @ np.array([0, 0, 1]), -1, 1))
    return I1_I_full(alpha_mag, du, dv_val, u_rot, v_rot)


def I2_I(alpha, beta_u, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat
    alpha2 = np.linalg.norm(combo_vec)
    return -np.exp(-1j * beta_u) * I1_I_general(alpha2, combo_vec / alpha2, u_hat, v_hat)


def I3_I(alpha, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat - beta_v * v_hat
    alpha3 = np.linalg.norm(combo_vec)
    return -np.exp(1j * beta_v) * I1_I_general(alpha3, combo_vec / alpha3, u_hat, v_hat)


def I4_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat - beta_v * v_hat
    alpha4 = np.linalg.norm(combo_vec)
    return np.exp(1j * (beta_v - beta_u)) * I1_I_general(alpha4, combo_vec / alpha4, u_hat, v_hat)


def Gamma_one_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    """正确组装公式(与手征主线同样的教训): 简单相加，I2,I3,I4定义已含相位因子"""
    I1 = I1_I_general(alpha, s_hat, u_hat, v_hat)
    I2 = I2_I(alpha, beta_u, s_hat, u_hat, v_hat)
    I3 = I3_I(alpha, beta_v, s_hat, u_hat, v_hat)
    I4 = I4_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    return 1 / (32 * np.pi) * (I1 + I2 + I3 + I4)


if __name__ == "__main__":
    print("测试强度版 I2^I, I3^I, I4^I, Gamma_one^I:")
    s_hat = np.array([0, 0, 1])
    du_v, dv_v, psi_v = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du_v), 0, np.cos(du_v)])
    v_hat = np.array([np.sin(dv_v) * np.cos(psi_v), np.sin(dv_v) * np.sin(psi_v), np.cos(dv_v)])
    alpha_val, beta_u_val, beta_v_val = 1.0, 0.8, 0.6

    print(f"  I2^I = {I2_I(alpha_val, beta_u_val, s_hat, u_hat, v_hat)}")
    print(f"  I3^I = {I3_I(alpha_val, beta_v_val, s_hat, u_hat, v_hat)}")
    print(f"  I4^I = {I4_I(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)}")
    print(f"  Gamma_one^I = {Gamma_one_I(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)}")
