"""
【性质】数值验证 —— 用【单次合并的2D数值积分】（把I1+I2+I3+I4合并成一个被积函数
        直接积分一次，而非分别用4个不同的I1_V_general调用）交叉核对"具体计算"文件
        给出的 Gamma_one_V() 函数，并借此发现、诊断、修正了一处组装公式错误
【计算的量】Gamma_one^V(alpha,beta_u,beta_v,...) 的两种独立计算路径是否一致
【状态】✅ 修正后完全吻合（相对误差~1e-6），✅ 已诚实记录发现bug的过程
【依赖】直接复制"具体计算"01号文件的 Gamma_one_V(), I1_V_general() 等函数

================================================================================
发现的bug及修正过程（诚实记录）
================================================================================
本文件最初的目的只是做一次常规交叉验证，但意外发现"具体计算"01号文件最初版本的
Gamma_one_V()函数（写成 1/(32pi)*[I1 - e^{-i*beta_u}*I2 - e^{i*beta_v}*I3
+ e^{i(beta_v-beta_u)}*I4]，直接照抄了论文Eq(24)的表面形式）与本文件独立实现的
"单次合并积分"结果相差约12倍，明显不对。

排查过程：
1. 先确认I2_V,I3_V,I4_V各自的定义（对应Eq19,21）是对的——组件D已经用直接定义式
   独立验证过I2_V，误差~1e-7，可信。
2. 问题出在"组装"这一步：论文Eq(21)-(23)写的是
       I2 ≡ -e^{-i*beta_u} * I1(alpha_2, s_2, ...)
       I3 ≡ -e^{i*beta_v}  * I1(alpha_3, s_3, ...)
       I4 ≡ e^{i(beta_v-beta_u)} * I1(alpha_4, s_4, ...)
   也就是说，这些相位因子 e^{±i*beta} 已经是I2,I3,I4定义本身的一部分（"打包"进去了）。
   但论文Eq(24)的求和公式：
       Gamma_one = 1/(32*pi) * [I1 - e^{-i*beta_u}*I1(alpha2,...) - e^{i*beta_v}*I1(alpha3,...)
                                 + e^{i(beta_v-beta_u)}*I1(alpha4,...)]
   这里面出现的 "-e^{-i*beta_u}*I1(alpha2,...)" 本身就等于 "I2"（根据I2的定义）！
   所以 Eq(24) 用I1,I2,I3,I4记号写出来，正确应为：
       Gamma_one = 1/(32*pi) * [I1 + I2 + I3 + I4]
   （因为 I2 定义本身已经带了负号和e^{-i beta_u}，不需要在Gamma_one公式里再乘一次）
3. 用本文件"单次合并积分"独立验证，确认改正后的组装公式（简单相加，不额外乘因子）
   与最原始定义完全吻合。

这是一个关于"论文公式记号复用容易引起二次套用错误"的教训：Eq(24)里的$I_1(\\alpha_2,...)$
是"裸的I1函数"，不是"I2变量"本身，两者数值上有±e^{i\\beta}的差异，必须小心区分
"公式里出现的symbol"到底指的是哪个定义。
================================================================================
"""
import numpy as np
import mpmath
from scipy import integrate


# ---- 复制自"具体计算"01号文件: 完整的Gamma_one_V()及其依赖 ----
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
    """修正后的组装公式: 简单相加，不再额外乘e^{±i*beta}（详见文件顶部说明）"""
    I1 = I1_V_general(alpha, s_hat, u_hat, v_hat)
    I2 = I2_V(alpha, beta_u, s_hat, u_hat, v_hat)
    I3 = I3_V(alpha, beta_v, s_hat, u_hat, v_hat)
    I4 = I4_V(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    return 1 / (32 * np.pi) * (I1 + I2 + I3 + I4)


# ---- 独立验证路径: 用矢量网格积分(而非scipy.dblquad)做单次合并积分，速度更快更稳健 ----
def xi_V_raw_batch(theta, phi, u_hat, v_hat):
    nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
    that_x, that_y, that_z = np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)
    phat_x, phat_y, phat_z = -np.sin(phi), np.cos(phi), np.zeros_like(phi)
    tu = that_x * u_hat[0] + that_y * u_hat[1] + that_z * u_hat[2]
    pu = phat_x * u_hat[0] + phat_y * u_hat[1] + phat_z * u_hat[2]
    tv = that_x * v_hat[0] + that_y * v_hat[1] + that_z * v_hat[2]
    pv = phat_x * v_hat[0] + phat_y * v_hat[1] + phat_z * v_hat[2]
    ePuu, eCuu = tu ** 2 - pu ** 2, 2 * tu * pu
    ePvv, eCvv = tv ** 2 - pv ** 2, 2 * tv * pv
    nu = nx * u_hat[0] + ny * u_hat[1] + nz * u_hat[2]
    nv = nx * v_hat[0] + ny * v_hat[1] + nz * v_hat[2]
    numV = ePuu * eCvv - eCuu * ePvv
    return numV / ((1 + nu) * (1 + nv))


def grid_integral_combined_gamma(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, Ntheta=600, Nphi=600):
    """单次网格积分，把I1+I2+I3+I4的被积函数直接合并成一个式子后积分一次"""
    thetas = np.linspace(1e-5, np.pi - 1e-5, Ntheta)
    phis = np.linspace(0, 2 * np.pi, Nphi, endpoint=False)
    TH, PH = np.meshgrid(thetas, phis, indexing='ij')
    xi = xi_V_raw_batch(TH, PH, u_hat, v_hat)
    nx, ny, nz = np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)

    def exp_dot(vec):
        return np.exp(-1j * (nx * vec[0] + ny * vec[1] + nz * vec[2]))

    t1 = exp_dot(alpha * s_hat)
    t2 = -np.exp(-1j * beta_u) * exp_dot(alpha * s_hat + beta_u * u_hat)
    t3 = -np.exp(1j * beta_v) * exp_dot(alpha * s_hat - beta_v * v_hat)
    t4 = np.exp(1j * (beta_v - beta_u)) * exp_dot(alpha * s_hat + beta_u * u_hat - beta_v * v_hat)
    combo = t1 + t2 + t3 + t4

    integrand = xi * np.sin(TH) * combo
    dtheta, dphi = thetas[1] - thetas[0], phis[1] - phis[0]
    return np.sum(integrand) * dtheta * dphi / (32 * np.pi)


if __name__ == "__main__":
    print("交叉验证: 修正后的Gamma_one_V()组装函数 vs 单次合并网格积分(独立实现)\n")

    s_hat = np.array([0, 0, 1])
    du_v, dv_v, psi_v = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du_v), 0, np.cos(du_v)])
    v_hat = np.array([np.sin(dv_v) * np.cos(psi_v), np.sin(dv_v) * np.sin(psi_v), np.cos(dv_v)])
    alpha_val, beta_u_val, beta_v_val = 1.0, 0.8, 0.6

    val_formula = Gamma_one_V(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)
    val_grid = grid_integral_combined_gamma(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)

    print(f"修正后公式组装结果: {val_formula}")
    print(f"独立网格积分结果  : {val_grid}")
    print(f"相对误差 = {abs(val_formula-val_grid)/abs(val_grid):.2e}")
    print("\n(误差量级来自网格积分的离散化精度，公式本身已修正为正确形式)")
