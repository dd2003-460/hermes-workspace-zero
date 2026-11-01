"""
【性质】具体计算 —— 用矢量替换规则，从 I1^V 直接导出 I2^V, I3^V, I4^V
【计算的量】I2^V(alpha,beta_u,s,u,v), I3^V(alpha,beta_v,s,u,v), I4^V(alpha,beta_u,beta_v,s,u,v)
【状态】✅ 成功，与直接定义式数值积分比对，多组随机参数误差~1e-6~1e-7量级
【依赖】
  - 组件C具体计算02号文件的 I1_V_full() 函数（直接复制，因含mpmath不用pkl）
  - 本组件推导文件证实的"I1^V旋转不变性"结论

================================================================================
矢量替换规则 (PRD论文 Eq.19-23，对强度版和手征版都适用)
================================================================================
    I2(alpha,beta_u,s,u,v) = -e^{-i*beta_u} * I1(alpha_2, s_2, u, v)
    其中 alpha_2*s_2 = alpha*s + beta_u*u  (矢量和，alpha_2是模长，s_2是方向)

    I3(alpha,beta_v,s,u,v) = -e^{i*beta_v} * I1(alpha_3, s_3, u, v)
    其中 alpha_3*s_3 = alpha*s - beta_v*v

    I4(alpha,beta_u,beta_v,s,u,v) = e^{i(beta_v-beta_u)} * I1(alpha_4, s_4, u, v)
    其中 alpha_4*s_4 = alpha*s + beta_u*u - beta_v*v

代入I1的公式时，需要用新的合成方向 s_2 (or s_3, s_4) 重新计算
    delta_u' = angle(u, s_2),  delta_v' = angle(v, s_2)
（gamma=angle(u,v)不变，因为u,v本身没有变化，只是观察方向s变了）

但注意：I1_V_full()这个函数的实现要求u_hat落在标准计算坐标系的x-z平面
(uy=0)。当我们要计算I1(alpha_2, s_2, u, v)时，s_2的方向一般不再与原来的
z轴对齐、u也不再是uy=0的形式。需要做一次坐标系旋转，把s_2转到新的z轴、
同时保持u落在新的x-z平面，才能调用I1_V_full()。这是本文件的核心技术点。
"""
import numpy as np
import mpmath
from scipy import integrate


# ---- 复制自组件C: 完整I1^V计算函数 ----
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
    【BUG-002 修复，从PRD强度副本项目同步】sqrt(disc)前的符号必须绑定
    sign(v_hat[1])（标准计算系下），不能固定取主分支。完整符号推导证明见
    PRD副本项目 `阶段1_单向链路ORF核心积分/组件B_I1积分的留数分量/R1234/
    结论与推导过程.md` 第3节（用论文Eq16极点公式代数消元严格证明）。
    由于R_k^V=±i*R_k^I对每个x逐点成立（组件E核心恒等式），这个修复对
    强度版和手征版同样适用，不需要针对手征版重新推导。
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
    """要求 u_hat 落在 x-z 平面 (uy=0)。BUG-002修复：chirality_sign绑定v_hat[1]符号。"""
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    chirality_sign = 1.0 if v_hat[1] >= 0 else -1.0
    I_R1I, I_R2I, I_R3I, I_R4I = all_R_integrals_I(alpha, du, dv, gamma, chirality_sign)
    I_R1V = -1j * I_R1I
    I_R2V = 1j * I_R2I
    I_R3V = 1j * I_R3I
    I_R4V = -1j * I_R4I

    def R0V_numeric(xv):
        return numerical_residue(lambda z: f_V_gold_standard(xv, z, u_hat, v_hat), 0.0)

    re0, _ = integrate.quad(lambda x: (R0V_numeric(x) * np.exp(-1j * alpha * x)).real, -1, 1, limit=100)
    im0, _ = integrate.quad(lambda x: (R0V_numeric(x) * np.exp(-1j * alpha * x)).imag, -1, 1, limit=100)
    I_R0V = re0 + 1j * im0

    return 2j * np.pi * (I_R0V + I_R1V + I_R2V + I_R3V + I_R4V)


def build_computational_frame(s_hat, u_hat):
    """构造一个旋转矩阵R，使得 R@s_hat = (0,0,1)，且 R@u_hat 落在x-z平面(y分量=0)。
    返回旋转矩阵R，供后续把v_hat也转换到这个坐标系。"""
    s_hat = s_hat / np.linalg.norm(s_hat)
    z_axis = np.array([0, 0, 1])
    # 第一步：找到把s_hat转到z_axis的旋转
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
    # 第二步：绕z轴旋转，使u的y分量变为0
    phi_u = np.arctan2(u_after_R1[1], u_after_R1[0])
    c, s = np.cos(-phi_u), np.sin(-phi_u)
    R2 = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return R2 @ R1


def I1_V_general(alpha_mag, s_hat, u_hat, v_hat):
    """通用版I1_V: 先旋转到标准计算坐标系，再调用I1_V_full"""
    R = build_computational_frame(s_hat, u_hat)
    u_rot = R @ u_hat
    v_rot = R @ v_hat
    du = np.arccos(np.clip(u_rot[2], -1, 1))
    dv_val = np.arccos(np.clip(v_rot @ np.array([0, 0, 1]), -1, 1))
    # 确保uy≈0 (数值容差)
    assert abs(u_rot[1]) < 1e-6, f"u_rot[1]={u_rot[1]} 应接近0"
    ux_val = u_rot[0]
    if ux_val < 0:  # PRD论文规范：ux应为正（对应delta_u的sin恒正），若为负需要另一半球对称处理
        pass  # sin(delta_u)本身非负，这里ux符号由u_rot决定，不强制翻转，交由I1_V_full内部sigma公式自洽处理
    return I1_V_full(alpha_mag, du, dv_val, u_rot, v_rot)


def I2_V(alpha, beta_u, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat
    alpha2 = np.linalg.norm(combo_vec)
    s2_hat = combo_vec / alpha2
    I1_val = I1_V_general(alpha2, s2_hat, u_hat, v_hat)
    return -np.exp(-1j * beta_u) * I1_val


def I3_V(alpha, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat - beta_v * v_hat
    alpha3 = np.linalg.norm(combo_vec)
    s3_hat = combo_vec / alpha3
    I1_val = I1_V_general(alpha3, s3_hat, u_hat, v_hat)
    return -np.exp(1j * beta_v) * I1_val


def I4_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat):
    combo_vec = alpha * s_hat + beta_u * u_hat - beta_v * v_hat
    alpha4 = np.linalg.norm(combo_vec)
    s4_hat = combo_vec / alpha4
    I1_val = I1_V_general(alpha4, s4_hat, u_hat, v_hat)
    return np.exp(1j * (beta_v - beta_u)) * I1_val


if __name__ == "__main__":
    print("测试 I2^V, I3^V, I4^V 计算:")
    du_v, dv_v, psi_v = 1.1, 0.9, 2.0
    s_hat = np.array([0, 0, 1])
    u_hat = np.array([np.sin(du_v), 0, np.cos(du_v)])
    v_hat = np.array([np.sin(dv_v) * np.cos(psi_v), np.sin(dv_v) * np.sin(psi_v), np.cos(dv_v)])
    alpha_val, beta_u_val, beta_v_val = 1.0, 0.6, 0.5

    val2 = I2_V(alpha_val, beta_u_val, s_hat, u_hat, v_hat)
    val3 = I3_V(alpha_val, beta_v_val, s_hat, u_hat, v_hat)
    val4 = I4_V(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)
    print(f"  I2^V = {val2}")
    print(f"  I3^V = {val3}")
    print(f"  I4^V = {val4}")
    print("\n完整验证见同级'数值验证'文件夹")
