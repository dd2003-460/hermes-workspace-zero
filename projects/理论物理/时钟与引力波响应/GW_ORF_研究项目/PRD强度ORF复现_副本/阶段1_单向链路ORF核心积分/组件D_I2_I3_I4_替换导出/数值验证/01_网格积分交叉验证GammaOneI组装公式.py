"""
【性质】数值验证 —— 用单次网格积分验证强度版 Gamma_one^I 的组装公式
【计算的量】Gamma_one^I(alpha,beta_u,beta_v,...) 组装公式 vs 独立网格积分
【状态】✅ 通过，误差~1e-5量级（网格积分离散化精度）
【依赖】直接复制"具体计算"01号文件的 Gamma_one_I() 等函数

【背景说明】这个验证同时确认了手征主线组件B里发现的"Gamma_one组装公式"教训
(I1+I2+I3+I4简单相加，不需要再乘e^{±i*beta}) 对强度版同样适用——这本来就
应该如此，因为I2,I3,I4的定义（Eq19-23）对强度版和手征版是完全相同的矢量
替换规则，只是里面调用的I1函数换成对称版本还是反对称版本的区别。
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
    """【BUG-002修复,与具体计算文件同步】sqrt(disc)分支需绑定 sign(v_hat[1])。"""
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
    I1 = I1_I_general(alpha, s_hat, u_hat, v_hat)
    I2 = I2_I(alpha, beta_u, s_hat, u_hat, v_hat)
    I3 = I3_I(alpha, beta_v, s_hat, u_hat, v_hat)
    I4 = I4_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat)
    return 1 / (32 * np.pi) * (I1 + I2 + I3 + I4)


def xi_I_raw_batch(theta, phi, u_hat, v_hat):
    """强度对称核: xi_I，用向量化网格计算"""
    that_x, that_y, that_z = np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)
    phat_x, phat_y, phat_z = -np.sin(phi), np.cos(phi), np.zeros_like(phi)
    tu = that_x * u_hat[0] + that_y * u_hat[1] + that_z * u_hat[2]
    pu = phat_x * u_hat[0] + phat_y * u_hat[1] + phat_z * u_hat[2]
    tv = that_x * v_hat[0] + that_y * v_hat[1] + that_z * v_hat[2]
    pv = phat_x * v_hat[0] + phat_y * v_hat[1] + phat_z * v_hat[2]
    ePuu, eCuu = tu ** 2 - pu ** 2, 2 * tu * pu
    ePvv, eCvv = tv ** 2 - pv ** 2, 2 * tv * pv
    nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
    nu = nx * u_hat[0] + ny * u_hat[1] + nz * u_hat[2]
    nv = nx * v_hat[0] + ny * v_hat[1] + nz * v_hat[2]
    numI = ePuu * ePvv + eCuu * eCvv
    return numI / ((1 + nu) * (1 + nv))


def grid_integral_combined_gamma_I(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, Ntheta=600, Nphi=600):
    thetas = np.linspace(1e-5, np.pi - 1e-5, Ntheta)
    phis = np.linspace(0, 2 * np.pi, Nphi, endpoint=False)
    TH, PH = np.meshgrid(thetas, phis, indexing='ij')
    xi = xi_I_raw_batch(TH, PH, u_hat, v_hat)
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
    print("验证强度版 Gamma_one^I 组装公式 vs 独立网格积分:\n")
    s_hat = np.array([0, 0, 1])
    du_v, dv_v, psi_v = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du_v), 0, np.cos(du_v)])
    v_hat = np.array([np.sin(dv_v) * np.cos(psi_v), np.sin(dv_v) * np.sin(psi_v), np.cos(dv_v)])
    alpha_val, beta_u_val, beta_v_val = 1.0, 0.8, 0.6

    val_formula = Gamma_one_I(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)
    val_grid = grid_integral_combined_gamma_I(alpha_val, beta_u_val, beta_v_val, s_hat, u_hat, v_hat)

    print(f"公式组装结果: {val_formula}")
    print(f"独立网格积分: {val_grid}")
    print(f"相对误差 = {abs(val_formula-val_grid)/abs(val_grid):.2e}")
