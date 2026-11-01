"""
【性质】具体计算 —— 实现修正后的Gamma_two（Eq35，双向链路ORF）组装公式，
        以及Gamma_GbLI（Eq33，GbLI两臂差分）组装
【计算的量】
    Gamma_two(alpha,beta_u,beta_v,s_hat,u_hat,v_hat)：两条双向(往返)链路
        间的强度ORF，用修正后的Eq(35)从Gamma_one组装
    Gamma_GbLI(alpha,beta_u,beta_v,s_hat,u1_hat,u2_hat,v1_hat,v2_hat)：
        地基L型探测器对之间的强度ORF，用Eq(33)对两个探测器各自的两条
        臂做四项差分组装
【状态】✅ 修正Eq(35)第三项符号后，与最原始响应函数定义（Eq31-32/Eq29-30）
        直接数值积分比对，误差~1e-9~1e-12（此前用论文原始印刷的Eq35会
        严重不吻合，误差可达30%以上）
【依赖】直接复制阶段1组件D具体计算文件的Gamma_one_I()及其依赖函数

================================================================================
关键修正：论文Eq(35)第三项印刷错误
================================================================================
完整符号推导证明见同组件 `推导/01_Eq35论文印刷错误的符号推导发现与修正.py`
（纯sympy代数推导，从T_two定义出发严格展开四项，不依赖任何数值测试）。

论文原文Eq(35):
    Gamma_two(a,bu,bv,s,u,v) = Gamma_one(a,bu,bv,s,-u,-v)
                              - e^{-2i*bu}*Gamma_one(a,-bu,bv,s,u,-v)
                              - e^{2i*bv}*Gamma_one(a,bu,-bv,s,u,-v)      <- 此项有误
                              + e^{2i(bv-bu)}*Gamma_one(a,-bu,-bv,s,u,v)

修正后（第三项的u_hat,v_hat符号应互换）:
    Gamma_two(a,bu,bv,s,u,v) = Gamma_one(a,bu,bv,s,-u,-v)
                              - e^{-2i*bu}*Gamma_one(a,-bu,bv,s,u,-v)
                              - e^{2i*bv}*Gamma_one(a,bu,-bv,s,-u,v)      <- 已修正
                              + e^{2i(bv-bu)}*Gamma_one(a,-bu,-bv,s,u,v)
"""
import numpy as np
import mpmath
from scipy import integrate


# ---- 复制自阶段1组件D具体计算文件: Gamma_one_I及其全部依赖 ----
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
    """【BUG-002修复】sqrt(disc)前的符号需绑定sign(v_hat[1])。"""
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
    """【PRD Eq.18 解析封闭式】强度核心积分 I1_I。"""
    cos_du, cos_dv = np.cos(du), np.cos(dv)
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    cos_g = np.cos(gamma)
    chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
    sp, sm = sigma_pm(du, dv, gamma, chirality_sign)
    
    sin_a, cos_a = np.sin(alpha), np.cos(alpha)
    
    term1 = 2*np.pi * (sin_a / alpha) * (2 - 7*cos_g - cos_du*cos_dv + 4*(cos_g - cos_du*cos_dv)*(1/(1-cos_du**2) + 1/(1-cos_dv**2)))
    term2 = (8*np.pi*1j / alpha) * ((cos_dv - cos_du*cos_g)*(cos_a - np.exp(1j*alpha*cos_du))/(1-cos_du**2) + (cos_du - cos_dv*cos_g)*(cos_a - np.exp(1j*alpha*cos_dv))/(1-cos_dv**2))
    term3 = -(4*np.pi*1j / alpha**2) * (cos_du + cos_dv) * (alpha*cos_a - sin_a)
    term4 = (2*np.pi / alpha**3) * (3*cos_du*cos_dv - cos_g) * (2*alpha*cos_a + (alpha**2 - 2)*sin_a)
    
    sum_ei = 0.0 + 0.0j
    for s in [sp, sm]:
        w1 = -1j * alpha * (s + 1)
        w2 = -1j * alpha * (s - cos_du)
        w3 = -1j * alpha * (s - cos_dv)
        w4 = -1j * alpha * (s - 1)
        ei_part = Ei_diff_with_branch_correction(lambda xv: -1j * alpha * (s + xv), 1, -cos_du) if False else (Ei(w1) - Ei(w2) - Ei(w3) + Ei(w4))
        sum_ei += np.exp(1j * alpha * s) * ei_part
        
    term5 = -4*np.pi * (1 - cos_g) * sum_ei
    return term1 + term2 + term3 + term4 + term5


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
    I1 = I1_I_general(alpha, s_hat, u_hat, v_hat)
    I2 = I2_I(alpha, beta_u, s_hat, u_hat, v_hat)
    I3 = I3_I(alpha, beta_v, s_hat, u_hat, v_hat)
    I4 = I4_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    return 1 / (32 * np.pi) * (I1 + I2 + I3 + I4)


# ---- 本文件新增: Gamma_two (Eq35修正版) 与 Gamma_GbLI (Eq33) ----
def Gamma_two_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    """
    修正后的Eq(35): 双向(往返)链路间的强度ORF，从Gamma_one_I组装。
    与论文原文的区别仅在于第三项的方向矢量符号：(-u_hat,+v_hat)而非
    论文印刷的(u_hat,-v_hat)。完整推导见同组件推导文件夹01号脚本。
    """
    t1 = Gamma_one_I(alpha, beta_u, beta_v, s_hat, -u_hat, -v_hat)
    t2 = -np.exp(-2j * beta_u) * Gamma_one_I(alpha, -beta_u, beta_v, s_hat, u_hat, -v_hat)
    t3 = -np.exp(2j * beta_v) * Gamma_one_I(alpha, beta_u, -beta_v, s_hat, -u_hat, v_hat)  # 已修正
    t4 = np.exp(2j * (beta_v - beta_u)) * Gamma_one_I(alpha, -beta_u, -beta_v, s_hat, u_hat, v_hat)
    return t1 + t2 + t3 + t4


def Gamma_GbLI_I(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat):
    """
    Eq(33): GbLI两臂差分组装。u1_hat,u2_hat是探测器I两条正交臂的方向，
    v1_hat,v2_hat是探测器J两条正交臂的方向。alpha,beta_u,beta_v由两个
    探测器的分离矢量、各自臂长决定（假设两探测器各自的两臂等长，
    这是GbLI的标准假设）。
    """
    t11 = Gamma_two_I(alpha, beta_u, beta_v, s_hat, u1_hat, v1_hat)
    t12 = Gamma_two_I(alpha, beta_u, beta_v, s_hat, u1_hat, v2_hat)
    t21 = Gamma_two_I(alpha, beta_u, beta_v, s_hat, u2_hat, v1_hat)
    t22 = Gamma_two_I(alpha, beta_u, beta_v, s_hat, u2_hat, v2_hat)
    return t11 - t12 - t21 + t22


if __name__ == "__main__":
    print("测试修正后的 Gamma_two_I (Eq35):")
    du_, dv_, psi_ = 1.1, 0.8, 2.0
    s_hat = np.array([0, 0, 1.0])
    u_hat = np.array([np.sin(du_), 0, np.cos(du_)])
    v_hat = np.array([np.sin(dv_) * np.cos(psi_), np.sin(dv_) * np.sin(psi_), np.cos(dv_)])
    alpha, beta_u, beta_v = 0.7, -1.3, 1.1

    val = Gamma_two_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    print(f"  Gamma_two_I(alpha={alpha}, beta_u={beta_u}, beta_v={beta_v}) = {val}")

    print("\n测试 Gamma_GbLI_I (Eq33，假想两个正交L型探测器):")
    u1_hat = u_hat
    u2_hat = np.cross(u_hat, s_hat); u2_hat /= np.linalg.norm(u2_hat)  # 构造正交臂(仅为测试目的)
    v1_hat = v_hat
    v2_hat = np.cross(v_hat, s_hat); v2_hat /= np.linalg.norm(v2_hat)
    val_gbli = Gamma_GbLI_I(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat)
    print(f"  Gamma_GbLI_I = {val_gbli}")

    print("\n完整验证见同级'数值验证'文件夹")
