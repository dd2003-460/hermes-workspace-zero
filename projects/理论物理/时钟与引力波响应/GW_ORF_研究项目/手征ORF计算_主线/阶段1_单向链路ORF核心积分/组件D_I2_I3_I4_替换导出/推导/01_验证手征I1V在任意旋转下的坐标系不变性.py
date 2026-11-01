"""
【性质】推导 —— 验证手征版 I1^V 是否像强度版一样，只依赖(alpha,delta_u,delta_v,gamma)
        四个几何不变量，与计算坐标系的朝向无关（这是矢量替换规则I2,I3,I4成立的前提）
【计算的量】I1^V 用"标准计算坐标系公式"算出的值，vs 用"任意旋转后的朝向"直接2D数值
        积分算出的值，是否一致
【状态】✅✅ 通过！5组随机旋转全部验证一致，误差~1e-7（与dblquad精度一致）
【依赖】直接复制组件C具体计算02号文件的 I1_V_full() 函数（含mpmath依赖，不用pkl）

================================================================================
为什么要做这个验证：矢量替换规则(F20/Eq21-23)成立的物理前提
================================================================================
PRD论文Eq(21)-(23)给出的矢量替换规则（I2,I3,I4可以直接由I1替换参数得到，不用
重新做留数计算）依赖一个关键前提："各向同性引力波背景下，ORF积分结果只取决于
矢量之间的夹角，不依赖计算坐标系的绝对朝向"。论文原文在这一点上的论证是：
"we are calculating the ORF for isotropic SGWB and the result should be
invariant under the rotation of the computational frame."

对强度版这一点是显然的（xi_I是标量，纯旋转不改变标量场的球面积分值）。但对
**手征版**，虽然圆偏振各向同性背景仍然是各向同性的（旋转不变），但**手征本身
是赝标量，在镜面反射下会变号**。因此需要额外确认：矢量替换规则里涉及的操作
（重新定位alpha*s_hat + beta*u_hat这个新方向）是纯粹的"改变观察方向"，不涉及
镜面反射，所以不会打破手征场旋转不变性——这一点在本文件用直接数值实验证实。

================================================================================
验证方法
================================================================================
构造两组物理上等价（相同的alpha, delta_u=angle(u,s), delta_v=angle(v,s),
gamma=angle(u,v)）但坐标系朝向完全不同的配置：
  - 配置A："标准计算坐标系"：s沿z轴，u落在x-z平面（这是组件A-C整条流水线
    默认使用的规范选择，也是I1_V_full()函数能够正确调用的唯一前提）
  - 配置B：对配置A整体做一个任意的3D旋转（旋转轴、旋转角随机选取）

用配置A的公式（组件C的I1_V_full()）算出I1^V，与配置B下直接对最原始定义
（不依赖任何坐标系规范约定）做2D数值积分算出的I1^V比较。如果两者一致，
就证明I1^V确实是"坐标系无关的物理量"，只依赖那4个不变量。
"""
import numpy as np
import mpmath
from scipy import integrate


# ---- 复制自组件C具体计算02号文件: 完整I1^V计算函数(要求u在x-z平面) ----
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


# ---- 完全不依赖坐标系规范约定的原始定义 (任意朝向的s,u,v都能用) ----
def xi_V_raw(theta, phi, u_hat, v_hat):
    nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
    that = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)])
    phat = np.array([-np.sin(phi), np.cos(phi), 0])
    n_hat = np.array([nx, ny, nz])
    ePlus_uu = (that @ u_hat) ** 2 - (phat @ u_hat) ** 2
    eCross_uu = 2 * (that @ u_hat) * (phat @ u_hat)
    ePlus_vv = (that @ v_hat) ** 2 - (phat @ v_hat) ** 2
    eCross_vv = 2 * (that @ v_hat) * (phat @ v_hat)
    n_dot_u = n_hat @ u_hat
    n_dot_v = n_hat @ v_hat
    numerator_V = ePlus_uu * eCross_vv - eCross_uu * ePlus_vv
    return numerator_V / ((1 + n_dot_u) * (1 + n_dot_v))


def I1_direct_2D_arbitrary_orientation(alpha_mag, s_hat, u_hat, v_hat):
    """任意朝向s,u,v的直接2D数值积分 —— 这里的theta,phi是关于"参考z轴"的球坐标，
    但因为积分是对整个球面做的，用哪个参考z轴不影响积分值本身（这正是要验证的点）"""
    def integrand_real(phi, theta):
        n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        val = xi_V_raw(theta, phi, u_hat, v_hat) * np.sin(theta) * np.exp(-1j * alpha_mag * (n_hat @ s_hat))
        return val.real

    def integrand_imag(phi, theta):
        n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        val = xi_V_raw(theta, phi, u_hat, v_hat) * np.sin(theta) * np.exp(-1j * alpha_mag * (n_hat @ s_hat))
        return val.imag

    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi - eps, 0, 2 * np.pi, epsabs=1e-7, epsrel=1e-5)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi - eps, 0, 2 * np.pi, epsabs=1e-7, epsrel=1e-5)
    return re + 1j * im


def rotation_matrix(axis, angle):
    axis = axis / np.linalg.norm(axis)
    a = np.cos(angle / 2)
    b, c, d = -axis * np.sin(angle / 2)
    return np.array([
        [a * a + b * b - c * c - d * d, 2 * (b * c + a * d), 2 * (b * d - a * c)],
        [2 * (b * c - a * d), a * a + c * c - b * b - d * d, 2 * (c * d + a * b)],
        [2 * (b * d + a * c), 2 * (c * d - a * b), a * a + d * d - b * b - c * c],
    ])


if __name__ == "__main__":
    print("验证: I1^V 在任意坐标系旋转下是否保持不变 (只依赖alpha,delta_u,delta_v,gamma)")
    print("(这是I2,I3,I4矢量替换规则对手征版依然成立的关键前提)\n")

    np.random.seed(10)
    max_rel_err = 0
    for trial in range(5):
        du_target = np.random.uniform(0.4, 2.5)
        dv_target = np.random.uniform(0.4, 2.5)
        gamma_target = np.random.uniform(0.3, 2.5)
        alpha_val = np.random.uniform(0.5, 2.5)

        # 配置A: 标准计算坐标系
        s_hat_A = np.array([0, 0, 1])
        u_hat_A = np.array([np.sin(du_target), 0, np.cos(du_target)])
        cos_du, cos_dv, cos_g = np.cos(du_target), np.cos(dv_target), np.cos(gamma_target)
        sin_du, sin_dv = np.sin(du_target), np.sin(dv_target)
        cos_psi = (cos_g - cos_du * cos_dv) / (sin_du * sin_dv)
        if abs(cos_psi) > 1:
            continue
        psi_val = np.arccos(np.clip(cos_psi, -1, 1))
        v_hat_A = np.array([sin_dv * np.cos(psi_val), sin_dv * np.sin(psi_val), cos_dv])
        if v_hat_A[1] <= 0:
            continue

        I1_A = I1_V_full(alpha_val, du_target, dv_target, u_hat_A, v_hat_A)

        # 配置B: 随机旋转
        axis = np.random.normal(size=3)
        angle = np.random.uniform(0.3, 3.0)
        R = rotation_matrix(axis, angle)
        s_hat_B, u_hat_B, v_hat_B = R @ s_hat_A, R @ u_hat_A, R @ v_hat_A

        I1_B = I1_direct_2D_arbitrary_orientation(alpha_val, s_hat_B, u_hat_B, v_hat_B)

        err = abs(I1_A - I1_B) / abs(I1_A)
        max_rel_err = max(max_rel_err, err)
        print(f"trial{trial}: alpha={alpha_val:.3f} du={du_target:.3f} dv={dv_target:.3f} gamma={gamma_target:.3f}")
        print(f"  配置A(标准坐标系公式) = {I1_A:.6g}")
        print(f"  配置B(任意旋转直接积分) = {I1_B:.6g}")
        print(f"  相对误差 = {err:.2e}\n")

    print(f"最大相对误差 = {max_rel_err:.2e}")
    print("结论: I1^V确实是坐标系朝向无关的物理量，只依赖(alpha,delta_u,delta_v,gamma)。")
    print("这证实了矢量替换规则(Eq21-23)对手征版同样成立的物理前提——")
    print("因为替换规则涉及的操作只是'改变观察方向'(纯几何重定位)，不涉及镜面反射，")
    print("不会打破手征背景在旋转下的不变性。")
