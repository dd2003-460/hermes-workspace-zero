"""
【性质】具体计算 —— 对 R1^I(x),R2^I(x),R3^I(x),R4^I(x) 分别做 x 积分，
        得到PRD论文Eq(18)里未单独给出的"逐项拆分"解析结果
【计算的量】∫R_k^I(x)*e^{-iαx}dx （k=1,2,3,4），每一项单独求出，而非只求四项之和
【状态】✅ 成功，4组随机参数×4个留数=16次独立检验全部通过，最大误差~1e-13
【依赖】无（自包含，用组件A/B已验证的R1I~R4I表达式 + 本组件推导文件给出的
        带分支修正的Ei积分反导数方法）

================================================================================
为什么需要"逐项拆分"，而不是直接用论文Eq(18)的合并结果？
================================================================================
PRD论文Eq(18)只给出了 R1^I+R2^I+R3^I+R4^I 四项积分的**总和**（因为对强度版
本身而言，只需要总和就够了）。但要计算手征版 I1^V，需要利用本项目发现的
核心恒等式：
    R1^V=-i*R1^I,  R2^V=+i*R2^I,  R3^V=+i*R3^I,  R4^V=-i*R4^I
这个恒等式必须**逐项**应用（每一项前面的虚数系数不同），如果只有四项的
总和，没法分别乘上不同的±i系数。所以必须先把论文没有单独给出的这四个
"分项积分"解析式推导出来。

【方法】每个R_k^I(x)都是"1/(x+pole) + 常数"的简单形式（简单极点+常数项），
对这种形式的积分用上面推导文件给出的公式：
    ∫[pole_coef/(x+pole_loc) + const_coef]*e^{-iαx}dx
    = pole_coef*e^{iα*pole_loc}*[Ei(-iα(x2+pole_loc))-Ei(-iα(x1+pole_loc))+分支修正]
      + const_coef*(i/α)*[e^{-iαx2}-e^{-iαx1}]
"""
import numpy as np
import mpmath
from scipy import integrate


def Ei(z):
    return complex(mpmath.ei(complex(z)))


def Ei_diff_with_branch_correction(w_func, x1, x2, N=80):
    """来自本组件'推导'文件，直接复制（自包含）"""
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
    组件B/R1234/结论与推导过程.md第3节的完整符号推导证明。本文件只在
    u_y=0,标准坐标系(gamma对称测试)下被单独调用，若下游要传入实际v_hat需要
    显式传chirality_sign。"""
    cos_du, cos_dv, cos_g = np.cos(du), np.cos(dv), np.cos(gamma)
    disc = np.sin(gamma) ** 2 - cos_du ** 2 - cos_dv ** 2 + 2 * cos_g * cos_du * cos_dv
    sq = np.sqrt(complex(disc)) * chirality_sign
    return 1 / (1 + cos_g) * (cos_du + cos_dv + 1j * sq), 1 / (1 + cos_g) * (cos_du + cos_dv - 1j * sq)


def integral_simple_pole_form(alpha, x1, x2, pole_coef, pole_loc, const_coef):
    """通用: ∫_{x1}^{x2} [pole_coef/(x+pole_loc) + const_coef] * e^{-iαx} dx"""
    w_func = lambda xv: -1j * alpha * (xv + pole_loc)
    ei_diff = Ei_diff_with_branch_correction(w_func, x1, x2)
    term_pole = pole_coef * np.exp(1j * alpha * pole_loc) * ei_diff
    term_const = const_coef * (1j / alpha) * (np.exp(-1j * alpha * x2) - np.exp(-1j * alpha * x1))
    return term_pole + term_const


def all_R_integrals_I(alpha, du, dv, gamma, chirality_sign=1.0):
    """PRD论文Eq(A9)-(A12)给出的R1^I~R4^I各自积分后的解析结果（论文本身未单独给出这四项）"""
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


if __name__ == "__main__":
    def R1f(x, du, dv, gamma):
        sp_, sm = sigma_pm(du, dv, gamma); cos_g = np.cos(gamma); cos_du = np.cos(du)
        return -2j * (1 - cos_g) / (x + sm) + 2j * (sp_ - cos_du) * (1 + cos_g) / (1 - cos_du ** 2)

    def R2f(x, du, dv, gamma):
        sp_, sm = sigma_pm(du, dv, gamma); cos_g = np.cos(gamma); cos_du = np.cos(du)
        return 2j * (1 - cos_g) / (x + sp_) - 2j * (sm - cos_du) * (1 + cos_g) / (1 - cos_du ** 2)

    def R3f(x, du, dv, gamma):
        sp_, sm = sigma_pm(du, dv, gamma); cos_g = np.cos(gamma); cos_dv = np.cos(dv)
        return -2j * (1 - cos_g) / (x + sp_) + 2j * (sm - cos_dv) * (1 + cos_g) / (1 - cos_dv ** 2)

    def R4f(x, du, dv, gamma):
        sp_, sm = sigma_pm(du, dv, gamma); cos_g = np.cos(gamma); cos_dv = np.cos(dv)
        return 2j * (1 - cos_g) / (x + sm) - 2j * (sp_ - cos_dv) * (1 + cos_g) / (1 - cos_dv ** 2)

    def direct_quad(Rfunc, x1, x2, alpha):
        re, _ = integrate.quad(lambda x: (Rfunc(x) * np.exp(-1j * alpha * x)).real, x1, x2, limit=300)
        im, _ = integrate.quad(lambda x: (Rfunc(x) * np.exp(-1j * alpha * x)).imag, x1, x2, limit=300)
        return re + 1j * im

    print("验证: 解析拆分公式 vs 直接数值积分 (4组随机参数 x 4个留数 = 16次独立检验)")
    np.random.seed(7)
    max_err = 0
    for trial in range(4):
        alpha = np.random.uniform(0.5, 3.0)
        du = np.random.uniform(0.3, 2.7); dv = np.random.uniform(0.3, 2.7)
        gamma_v = np.random.uniform(0.3, 2.7)

        I1a, I2a, I3a, I4a = all_R_integrals_I(alpha, du, dv, gamma_v)
        I1d = direct_quad(lambda x: R1f(x, du, dv, gamma_v), -1, -np.cos(du), alpha)
        I2d = direct_quad(lambda x: R2f(x, du, dv, gamma_v), -np.cos(du), 1, alpha)
        I3d = direct_quad(lambda x: R3f(x, du, dv, gamma_v), -1, -np.cos(dv), alpha)
        I4d = direct_quad(lambda x: R4f(x, du, dv, gamma_v), -np.cos(dv), 1, alpha)

        for label, a, d in [("R1", I1a, I1d), ("R2", I2a, I2d), ("R3", I3a, I3d), ("R4", I4a, I4d)]:
            err = abs(a - d) / max(abs(d), 1e-30)
            max_err = max(max_err, err)
            print(f"  trial{trial} {label}: 解析={a:.5g}  直接数值={d:.5g}  err={err:.2e}")

    print(f"\n最大误差 = {max_err:.2e} (机器精度量级即通过)")
    print("这4个逐项积分是解决手征I1^V完整封闭解的关键中间产物，见具体计算02号文件")
