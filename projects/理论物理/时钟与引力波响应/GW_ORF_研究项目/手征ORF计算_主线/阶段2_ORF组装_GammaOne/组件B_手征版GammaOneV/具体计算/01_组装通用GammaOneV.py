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


def R0V_analytic(x, u_hat, v_hat):
    """【解析封闭式】手征原点二阶极点留数 R_0^V(x) 完整 24 项分子。"""
    ux, uy, uz = u_hat
    vx, vy, vz = v_hat
    s2 = 1.0 - x**2
    x2 = x**2
    x3 = x**3
    denom = s2 * ux * vx + 1j * s2 * ux * vy
    num = (2*s2*ux**2*vz**2*x - 2*s2*uz**2*vx**2*x - 4j*s2*uz**2*vx*vy*x + 2*s2*uz**2*vy**2*x
           - 2j*ux**2*vx*vy*x3 + 2j*ux**2*vx*vy*x + 2*ux**2*vy**2*x3 - 2*ux**2*vy**2*x
           + 2*ux**2*vz**2*x3 - 2*ux**2*vz**2*x + 2*ux**2*vz*x2 - 2*ux**2*vz
           - 2*ux*uz*vx*x2 + 2*ux*uz*vx - 2j*ux*uz*vy*x2 + 2j*ux*uz*vy
           + 2*ux*vx*vz*x2 - 2*ux*vx*vz + 2j*ux*vy*vz*x2 - 2j*ux*vy*vz
           - 2*uz**2*vx**2*x3 + 2*uz**2*vx**2*x - 4j*uz**2*vx*vy*x3 + 4j*uz**2*vx*vy*x
           + 2*uz**2*vy**2*x3 - 2*uz**2*vy**2*x - 2*uz*vx**2*x2 + 2*uz*vx**2
           - 4j*uz*vx*vy*x2 + 4j*uz*vx*vy + 2*uz*vy**2*x2 - 2*uz*vy**2)
    return num / denom


def I1_V_full(alpha, du, dv, u_hat, v_hat):
    """【BUG-002修复】chirality_sign绑定v_hat[1]符号。R0V 改用 24 项解析封闭式。"""
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
    I_R1I, I_R2I, I_R3I, I_R4I = all_R_integrals_I(alpha, du, dv, gamma, chirality_sign)
    I_R1V, I_R2V, I_R3V, I_R4V = -1j * I_R1I, 1j * I_R2I, 1j * I_R3I, -1j * I_R4I

    re0, _ = integrate.quad(lambda x: (R0V_analytic(x, u_hat, v_hat) * np.exp(-1j * alpha * x)).real, -1, 1, limit=100)
    im0, _ = integrate.quad(lambda x: (R0V_analytic(x, u_hat, v_hat) * np.exp(-1j * alpha * x)).imag, -1, 1, limit=100)
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


if __name__ == "__main__":
    print("测试通用Gamma_one^V计算 (中等大小的alpha,beta参数，数值稳健区域):")
    s_hat = np.array([0, 0, 1])
    du_v, dv_v, psi_v = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du_v), 0, np.cos(du_v)])
    v_hat = np.array([np.sin(dv_v) * np.cos(psi_v), np.sin(dv_v) * np.sin(psi_v), np.cos(dv_v)])
    alpha_val, beta_u_val, beta_v_val = 1.0, 0.8, 0.6

    val = Gamma_one_V(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)
    print(f"  Gamma_one^V(alpha={alpha_val}, beta_u={beta_u_val}, beta_v={beta_v_val}) = {val}")
    print("\n完整数值验证及PTA零响应极限的独立验证，见同级'数值验证'文件夹与'推导'文件夹")
