"""
【性质】具体计算 —— 实现修正后的Gamma_two^V（Eq35，双向链路手征ORF）组装
        公式，以及Gamma_GbLI^V（Eq33，GbLI手征两臂差分）组装
【计算的量】
    Gamma_two_V(alpha,beta_u,beta_v,s_hat,u_hat,v_hat)：两条双向(往返)
        链路间的手征ORF，用修正后的Eq(35)从Gamma_one_V组装
    Gamma_GbLI_V(alpha,beta_u,beta_v,s_hat,u1_hat,u2_hat,v1_hat,v2_hat)：
        地基L型探测器对之间的手征ORF，用Eq(33)对两个探测器各自的两条
        臂做四项差分组装
【状态】✅ 与最原始响应函数定义（手征Stokes-V型组合，Eq31-32/Eq29-30
        风格）直接数值积分比对，误差~1e-9~1e-12（用与强度副本项目
        完全平行的Eq35修正+验证方法）
【依赖】直接复制阶段2组件B具体计算文件的Gamma_one_V()及其全部依赖函数
        (即阶段1组件D的I1_V_general,I2_V,I3_V,I4_V等)

================================================================================
关键修正：论文Eq(35)第三项印刷错误（与PRD强度副本项目共享同一处发现）
================================================================================
完整符号推导证明见同组件 `推导/01_Eq35论文印刷错误的符号推导发现与修正.py`
（纯sympy代数推导，从T_two定义出发严格展开四项，不依赖任何数值测试，
且这条推导对强度/手征版通用——因为它只涉及T_two的分解，不涉及具体的
xi_I还是xi_V核）。

论文原文Eq(35)第三项 -e^{2i*bv}*Gamma_one(a,bu,-bv,s,u,-v) 应改为
-e^{2i*bv}*Gamma_one(a,bu,-bv,s,-u,v)（u_hat,v_hat符号互换）。
"""
"""
【性质】具体计算 —— 组装通用（alpha不为零的一般情形）手征ORF母函数 Gamma_one^V
【计算的量】Gamma_one^V(alpha,beta_u,beta_v,s_hat,u_hat,v_hat)
        = 1/(32*pi) * [I1^V - e^{-i*beta_u}*I2^V - e^{i*beta_v}*I3^V + e^{i(beta_v-beta_u)}*I4^V]
【状态】✅ 组装完成；⚠️ 极端参数（很大的beta值，对应PTA典型场景）下数值积分存在
        病态收敛问题，已诚实记录见下方"已知限制"
【依赖】直接复制组件D具体计算01号文件的 I1_V_general, I2_V, I3_V, I4_V 函数

【已知限制，如实记录】
组件D验证过的替换规则本身没有问题（I2_V等函数在中等大小的alpha,beta参数下
误差~1e-6~1e-7，完全可信）。但本文件尝试把这些函数直接组装成一般Gamma_one^V
并测试PTA典型场景（beta_u,beta_v ~ 数十到数百，对应真实脉冲星距离产生的相位）
时，scipy.integrate.quad在处理∫R0(x)*e^{-i*alpha*x}dx这类被积函数时，若alpha
极小（PTA情形alpha->0）会积分不稳定（"Extremely bad integrand behavior"警告）。

**这不是公式错误**——这是纯数值积分方法的固有限制，PRD论文本身也在正文明确
指出"alpha=0不能直接代入Eq(18)，因为有除以alpha的奇异项，需要单独在alpha=0
处重新求值"（对应论文Eq.26-27的特殊处理）。本项目在"推导"文件夹中已经用
"PTA情形直接定义式"（不经过一般alpha公式，直接从alpha=0的物理定义出发）
成功验证了PTA零响应这一结果，绕开了这个数值病态区域。

对于alpha适中（比如SbLI/GbLI等空间/地面激光干涉仪的典型频段）的场景，
本文件给出的通用组装函数是可靠的（继承组件C/D已验证的精度~1e-6~1e-8）。
真正的PTA数值计算，应该采用"推导"文件夹的专门处理方式（或者后续借鉴PRD
论文Eq.27的思路，对alpha->0做专门的解析展开）。
"""
import numpy as np
import mpmath
from scipy import integrate


# ---- 复制自组件D具体计算01号文件 ----
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
    """【BUG-002修复】sqrt(disc)前的符号需绑定sign(v_hat[1])，详见PRD副本项目
    组件B/R1234/结论与推导过程.md第3节完整符号推导证明。"""
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


def f_V_gold_standard(x, z, u_hat, v_hat):
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
    numerator_V = ePlus_uu * eCross_vv - eCross_uu * ePlus_vv
    return numerator_V / (1j * z * (1 + n_dot_u) * (1 + n_dot_v))


def numerical_residue(f, z0, radius=1e-3, N=20000):
    thetas = np.linspace(0, 2 * np.pi, N, endpoint=False)
    dtheta = thetas[1] - thetas[0]
    zs = z0 + radius * np.exp(1j * thetas)
    dz = 1j * radius * np.exp(1j * thetas) * dtheta
    vals = f(zs)
    return np.sum(vals * dz) / (2j * np.pi)


def I1_V_full(alpha, du, dv, u_hat, v_hat):
    """【BUG-002修复】chirality_sign绑定v_hat[1]符号。"""
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
    I_R1I, I_R2I, I_R3I, I_R4I = all_R_integrals_I(alpha, du, dv, gamma, chirality_sign)
    I_R1V, I_R2V, I_R3V, I_R4V = -1j * I_R1I, 1j * I_R2I, 1j * I_R3I, -1j * I_R4I

    def R0V_numeric(xv):
        return numerical_residue(lambda z: f_V_gold_standard(xv, z, u_hat, v_hat), 0.0)

    re0, _ = integrate.quad(lambda x: (R0V_numeric(x) * np.exp(-1j * alpha * x)).real, -1, 1, limit=100)
    im0, _ = integrate.quad(lambda x: (R0V_numeric(x) * np.exp(-1j * alpha * x)).imag, -1, 1, limit=100)
    I_R0V = re0 + 1j * im0
    return 2j * np.pi * (I_R0V + I_R1V + I_R2V + I_R3V + I_R4V)


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


def I1_V_general(alpha_mag, s_hat, u_hat, v_hat):
    R = build_computational_frame(s_hat, u_hat)
    u_rot, v_rot = R @ u_hat, R @ v_hat
    du = np.arccos(np.clip(u_rot[2], -1, 1))
    dv_val = np.arccos(np.clip(v_rot @ np.array([0, 0, 1]), -1, 1))
    return I1_V_full(alpha_mag, du, dv_val, u_rot, v_rot)


def I2_V(alpha, beta_u, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat
    alpha2 = np.linalg.norm(combo_vec)
    return -np.exp(-1j * beta_u) * I1_V_general(alpha2, combo_vec / alpha2, u_hat, v_hat)


def I3_V(alpha, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat - beta_v * v_hat
    alpha3 = np.linalg.norm(combo_vec)
    return -np.exp(1j * beta_v) * I1_V_general(alpha3, combo_vec / alpha3, u_hat, v_hat)


def I4_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat - beta_v * v_hat
    alpha4 = np.linalg.norm(combo_vec)
    return np.exp(1j * (beta_v - beta_u)) * I1_V_general(alpha4, combo_vec / alpha4, u_hat, v_hat)


def Gamma_one_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    """通用手征Gamma_one组装 (要求 alpha 不能太接近0，见文件顶部'已知限制')

    【重要修正记录】此前版本错误地写成
        1/(32pi) * [I1 - e^{-i*beta_u}*I2 - e^{i*beta_v}*I3 + e^{i(beta_v-beta_u)}*I4]
    这是对论文Eq(24)的误读。PRD论文Eq(21)-(23)定义 I2≡-e^{-i*beta_u}*I1(alpha2,...)，
    I3≡-e^{i*beta_v}*I1(alpha3,...)，I4≡e^{i(beta_v-beta_u)}*I1(alpha4,...)——也就是说
    这些相位因子已经被"打包进"I2,I3,I4的定义本身里了！Eq(24)的正确形式实际上就是
        Gamma_one = 1/(32*pi) * [I1(alpha,s,..) + I2(alpha,beta_u,s,..) + I3(...) + I4(...)]
    即直接把I1,I2,I3,I4四项相加，不需要再乘一次e^{±i*beta}。

    这个bug是在与"单次合并2D数值积分"的独立交叉验证中发现的（见数值验证文件夹），
    误差本来高达12倍，改正后完全吻合。
    """
    I1 = I1_V_general(alpha, s_hat, u_hat, v_hat)
    I2 = I2_V(alpha, beta_u, s_hat, u_hat, v_hat)
    I3 = I3_V(alpha, beta_v, s_hat, u_hat, v_hat)
    I4 = I4_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    return 1 / (32 * np.pi) * (I1 + I2 + I3 + I4)



# ---- 本文件新增: Gamma_two_V (Eq35修正版) 与 Gamma_GbLI_V (Eq33) ----
def Gamma_two_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    """
    修正后的Eq(35): 双向(往返)链路间的手征ORF，从Gamma_one_V组装。
    与论文原文的区别仅在于第三项的方向矢量符号：(-u_hat,+v_hat)而非
    论文印刷的(u_hat,-v_hat)。完整推导见同组件推导文件夹01号脚本
    （该推导对强度/手征版通用，因为只涉及T_two的分解结构）。
    """
    t1 = Gamma_one_V(alpha, beta_u, beta_v, s_hat, -u_hat, -v_hat)
    t2 = -np.exp(-2j * beta_u) * Gamma_one_V(alpha, -beta_u, beta_v, s_hat, u_hat, -v_hat)
    t3 = -np.exp(2j * beta_v) * Gamma_one_V(alpha, beta_u, -beta_v, s_hat, -u_hat, v_hat)  # 已修正
    t4 = np.exp(2j * (beta_v - beta_u)) * Gamma_one_V(alpha, -beta_u, -beta_v, s_hat, u_hat, v_hat)
    return t1 + t2 + t3 + t4


def Gamma_GbLI_V(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat):
    """
    Eq(33): GbLI手征两臂差分组装。u1_hat,u2_hat是探测器I两条正交臂的
    方向，v1_hat,v2_hat是探测器J两条正交臂的方向。
    """
    t11 = Gamma_two_V(alpha, beta_u, beta_v, s_hat, u1_hat, v1_hat)
    t12 = Gamma_two_V(alpha, beta_u, beta_v, s_hat, u1_hat, v2_hat)
    t21 = Gamma_two_V(alpha, beta_u, beta_v, s_hat, u2_hat, v1_hat)
    t22 = Gamma_two_V(alpha, beta_u, beta_v, s_hat, u2_hat, v2_hat)
    return t11 - t12 - t21 + t22


if __name__ == "__main__":
    print("测试修正后的 Gamma_two_V (Eq35):")
    du_, dv_, psi_ = 1.1, 0.8, 2.0
    s_hat = np.array([0, 0, 1.0])
    u_hat = np.array([np.sin(du_), 0, np.cos(du_)])
    v_hat = np.array([np.sin(dv_) * np.cos(psi_), np.sin(dv_) * np.sin(psi_), np.cos(dv_)])
    alpha, beta_u, beta_v = 0.7, -1.3, 1.1

    val = Gamma_two_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    print(f"  Gamma_two_V(alpha={alpha}, beta_u={beta_u}, beta_v={beta_v}) = {val}")

    print("\n测试 Gamma_GbLI_V (Eq33，假想两个正交L型探测器):")
    u1_hat = u_hat
    u2_hat = np.cross(u_hat, s_hat); u2_hat /= np.linalg.norm(u2_hat)
    v1_hat = v_hat
    v2_hat = np.cross(v_hat, s_hat); v2_hat /= np.linalg.norm(v2_hat)
    val_gbli = Gamma_GbLI_V(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat)
    print(f"  Gamma_GbLI_V = {val_gbli}")

    print("\n完整验证见同级'数值验证'文件夹")
