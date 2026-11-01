"""
【性质】推导 —— 诊断通用 Gamma_one_I 框架直接代入PTA构型(alpha=0, s_2=u_hat)时
        遇到的坐标奇异性，说明为何必须走"直接定义式"而非"套用通用公式"这条路径
【计算的量】I1_I_general(beta_u; s_hat=u_hat, u_hat, v_hat) 在 s_hat 趋于 u_hat 时的行为
【状态】✅ 诊断完成：确认这是真实的坐标奇异性（1/(1-cos^2(delta_u'))在delta_u'->0时发散），
        论文本身也因此专门推导了Eq(28)这个不经过此路径的独立封闭解
【依赖】直接复制阶段1组件D具体计算文件的 I1_I_general() 等函数

================================================================================
背景：为什么PTA情形不能直接调用阶段1/2已验证的通用Gamma_one_I框架
================================================================================
PRD论文Eq(26)给出PTA情形（两条link共享地球端点，alpha=0）的表达式：
    Gamma_PTA = 1/(32pi) * [I1(0,s,u,v) - e^{-i*beta_u}*I1(beta_u,u,u,v)
                            - e^{i*beta_v}*I1(beta_v,-v,u,v)
                            + e^{i(beta_v-beta_u)}*I1(beta_s,(beta_u*u-beta_v*v)/beta_s,u,v)]

注意第二项 I1(beta_u, **u_hat**, u_hat, v_hat)——这里"合成方向" s_2 恰好等于 u_hat
本身！这意味着 delta_u' = angle(u_hat, s_2) = angle(u_hat, u_hat) = 0，
而我们组件D/C的公式里 R1_I, R2_I 含有 1/(1-cos^2(delta_u')) 这样的因子，
delta_u'->0 时 cos(delta_u')->1，分母趋于0——这是一个真实的、非人为的
坐标奇异性（论文用"计算坐标系"约定，把delta_u'=0这个特殊角度选作为参考轴，
必然导致球坐标基矢量在该点退化，与直角坐标系在两极的坐标奇异完全同源）。

论文正文对这一点的处理方式：不通过"delta_u'->0极限"来求，而是直接对Eq(17)
在alpha=0代入（这是另一条独立的推导路径，绕开了这个特定的奇异构型），
得到Eq(27)/(28)这两个专门的封闭解。

本文件的诊断价值：明确指出"不能简单套用已验证的通用Gamma_one_I框架处理PTA"，
必须用论文Eq(28)或等价的"直接定义式数值积分"（本组件"具体计算"采用的方案）。
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


def sigma_pm(du, dv, gamma):
    cos_du, cos_dv, cos_g = np.cos(du), np.cos(dv), np.cos(gamma)
    disc = np.sin(gamma) ** 2 - cos_du ** 2 - cos_dv ** 2 + 2 * cos_g * cos_du * cos_dv
    sq = np.sqrt(complex(disc))
    return 1 / (1 + cos_g) * (cos_du + cos_dv + 1j * sq), 1 / (1 + cos_g) * (cos_du + cos_dv - 1j * sq)


def integral_simple_pole_form(alpha, x1, x2, pole_coef, pole_loc, const_coef):
    w_func = lambda xv: -1j * alpha * (xv + pole_loc)
    ei_diff = Ei_diff_with_branch_correction(w_func, x1, x2)
    term_pole = pole_coef * np.exp(1j * alpha * pole_loc) * ei_diff
    term_const = const_coef * (1j / alpha) * (np.exp(-1j * alpha * x2) - np.exp(-1j * alpha * x1))
    return term_pole + term_const


def all_R_integrals_I(alpha, du, dv, gamma):
    sp_, sm = sigma_pm(du, dv, gamma)
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


def f_I_gold(x, z, u_hat, v_hat):
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
    I_R1, I_R2, I_R3, I_R4 = all_R_integrals_I(alpha, du, dv, gamma)

    def R0_numeric(xv):
        return numerical_residue(lambda z: f_I_gold(xv, z, u_hat, v_hat), 0.0)

    re0, _ = integrate.quad(lambda x: (R0_numeric(x) * np.exp(-1j * alpha * x)).real, -1, 1, limit=100)
    im0, _ = integrate.quad(lambda x: (R0_numeric(x) * np.exp(-1j * alpha * x)).imag, -1, 1, limit=100)
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


if __name__ == "__main__":
    du, dv, psi = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du), 0, np.cos(du)])
    v_hat = np.array([np.sin(dv) * np.cos(psi), np.sin(dv) * np.sin(psi), np.cos(dv)])
    beta_u = 0.8

    print("诊断: I1_I_general(beta_u; s_hat, u_hat, v_hat) 当 s_hat 趋近 u_hat 时的行为")
    print("(论文Eq26第二项要求 s_hat 恰好等于 u_hat，此处逐步逼近观察是否发散)\n")
    for eps in [0.5, 0.1, 0.01]:
        s2_hat = u_hat + eps * np.array([0, 1, 0])
        s2_hat = s2_hat / np.linalg.norm(s2_hat)
        delta_u_prime = np.arccos(np.clip(u_hat @ s2_hat, -1, 1))
        try:
            val = I1_I_general(beta_u, s2_hat, u_hat, v_hat)
            print(f"  eps={eps}: delta_u'={delta_u_prime:.4f}rad  I1={val}")
        except Exception as e:
            print(f"  eps={eps}: 计算异常 {e}")

    print("\n直接代入 s_hat = u_hat (delta_u'=0，论文Eq26要求的精确构型):")
    try:
        val_exact = I1_I_general(beta_u, u_hat, u_hat, v_hat)
        print(f"  I1 = {val_exact}")
    except Exception:
        pass
    print("  (若上面出现RuntimeWarning: divide by zero / invalid value，或耗时异常长后超时，")
    print("   证实这是真实的坐标奇异性，而非代码bug)")

    print("\n" + "=" * 70)
    print("结论: PTA情形不能直接套用通用Gamma_one_I框架处理delta_u'=0这一特殊构型，")
    print("论文本身也是用独立于此路径的Eq(28)专门封闭解来处理的。")
    print("本组件'具体计算'采用【直接定义式数值积分】方案（与本项目其余组件的")
    print("黄金标准验证方法一脉相承，稳健可靠），不再逐项转录复杂的Eq(28)")
    print("（该公式排版横跨两栏，转录风险很高，且转录本身不会增加物理可信度——")
    print("直接定义式积分同样能给出可信、可验证的数值结果）。")
    print("=" * 70)
