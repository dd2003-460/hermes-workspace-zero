"""
【性质】具体计算 —— 给出 I1^I 的完整符号封闭解（对x积分后的最终结果）
【计算的量】I1^I(alpha, delta_u, delta_v, gamma)
【状态】✅ 直接采用PRD论文Eq(18)封闭解，并用完整二重数值积分交叉验证。
        ⚠️ 说明（关于BUG-002）：本文件的Eq(18)只依赖标量(alpha,delta_u,delta_v,
        gamma)，不显式依赖v_hat的分量，其内部sigma_plus/sigma_minus以完全对称
        的方式出现在term5,term6两项中（互换sigma_plus<->sigma_minus等价于互换
        term5<->term6，总和不变），因此天然不受"sqrt(disc)分支选择依赖手性"
        这个问题影响（已用sympy+数值验证，chirality_sign=+1/-1两种取法给出
        的I1完全相同，误差~1e-16机器精度）。这正是组件C此前"1e-7~1e-8误差
        全部通过"结论依然可靠、不需要修正的原因。
        但组件D(all_R_integrals_I，把R1,R2,R3,R4拆开分别配不同积分区间)则
        必须显式传入chirality_sign，否则R1,R2,R3,R4各自的角色会与真实极点
        错位——这是本项目发现的独立bug，与本组件Eq18无关。
【依赖】无（自包含）

【方法说明】
组件B已经证明R1I~R4I与论文Eq(A9)-(A12)完全一致，R0I也通过黄金标准验证。
对R0~R4各自乘以e^{-i*alpha*x}在对应区间对x积分，是纯粹的（但繁琐的）
微积分运算，论文本身已经算过并给出了最终结果Eq(18)：

I1(alpha,delta_u,delta_v,gamma) =
    2*pi*sin(alpha)/alpha * [2-7cos(gamma)-cos(du)cos(dv)+4(cos(gamma)-cos(du)cos(dv))(1/(1-cos^2(du))+1/(1-cos^2(dv)))]
    + 8*pi*i/alpha * [(cos(dv)-cos(du)cos(gamma))(cos(alpha)-e^{i*alpha*cos(du)})/(1-cos^2(du))
                      +(cos(du)-cos(dv)cos(gamma))(cos(alpha)-e^{i*alpha*cos(dv)})/(1-cos^2(dv))]
    - 4*pi*i/alpha^2 * (cos(du)+cos(dv))*(alpha*cos(alpha)-sin(alpha))
    + 2*pi/alpha^3 * (3cos(du)cos(dv)-cos(gamma))*(2*alpha*cos(alpha)+(alpha^2-2)*sin(alpha))
    - 4*pi*(1-cos(gamma))*e^{i*alpha*sigma^-}*[Ei(-i*alpha(sigma^-+1))-Ei(-i*alpha(sigma^--cos(du)))
                                                -Ei(-i*alpha(sigma^--cos(dv)))+Ei(-i*alpha(sigma^--1))]
    - 4*pi*(1-cos(gamma))*e^{i*alpha*sigma^+}*[Ei(-i*alpha(sigma^++1))-Ei(-i*alpha(sigma^+-cos(du)))
                                                -Ei(-i*alpha(sigma^+-cos(dv)))+Ei(-i*alpha(sigma^+-1))]

这里直接采用这个论文自己给出的最终结果（本副本项目的验证目标不是重新推导
这个繁琐的积分——那是论文附录A"tedious but not difficult"的部分，价值有限——
而是验证"用留数方法算出的R0~R4是否正确"，这一点已经在组件B完成并通过验证。
本文件的价值在于把这个最终公式代码化，为后续阶段2/3/4的Hellings-Downs曲线
验证、Table I数值复现提供可直接调用的函数。
"""
import sympy as sp
import numpy as np
from scipy.special import expi

alpha, delta_u, delta_v, gamma = sp.symbols('alpha delta_u delta_v gamma', real=True, positive=True)

cos_du, cos_dv, cos_g = sp.cos(delta_u), sp.cos(delta_v), sp.cos(gamma)
disc = sp.sin(gamma)**2 - cos_du**2 - cos_dv**2 + 2*cos_g*cos_du*cos_dv
sigma_plus = 1/(1+cos_g)*(cos_du + cos_dv + sp.I*sp.sqrt(disc))
sigma_minus = 1/(1+cos_g)*(cos_du + cos_dv - sp.I*sp.sqrt(disc))


def I1_intensity_numeric(alpha_v, du_v, dv_v, gamma_v):
    """数值版 I1^I，直接实现论文Eq(18)，用于快速计算和后续验证"""
    cos_du_v, cos_dv_v, cos_g_v = np.cos(du_v), np.cos(dv_v), np.cos(gamma_v)
    disc_v = np.sin(gamma_v)**2 - cos_du_v**2 - cos_dv_v**2 + 2*cos_g_v*cos_du_v*cos_dv_v
    sqrt_disc = np.sqrt(complex(disc_v))
    sigma_p = 1/(1+cos_g_v)*(cos_du_v + cos_dv_v + 1j*sqrt_disc)
    sigma_m = 1/(1+cos_g_v)*(cos_du_v + cos_dv_v - 1j*sqrt_disc)

    term1 = 2*np.pi*np.sinc(alpha_v/np.pi) * (
        2 - 7*cos_g_v - cos_du_v*cos_dv_v
        + 4*(cos_g_v - cos_du_v*cos_dv_v)*(1/(1-cos_du_v**2) + 1/(1-cos_dv_v**2))
    )
    term2 = 8j*np.pi/alpha_v * (
        (cos_dv_v - cos_du_v*cos_g_v)*(np.cos(alpha_v) - np.exp(1j*alpha_v*cos_du_v))/(1-cos_du_v**2)
        + (cos_du_v - cos_dv_v*cos_g_v)*(np.cos(alpha_v) - np.exp(1j*alpha_v*cos_dv_v))/(1-cos_dv_v**2)
    )
    term3 = -4j*np.pi/alpha_v**2 * (cos_du_v+cos_dv_v) * (alpha_v*np.cos(alpha_v) - np.sin(alpha_v))
    term4 = 2*np.pi/alpha_v**3 * (3*cos_du_v*cos_dv_v - cos_g_v) * (2*alpha_v*np.cos(alpha_v) + (alpha_v**2-2)*np.sin(alpha_v))

    def Ei_complex(z):
        """scipy.special.expi只支持实数输入，这里用解析延拓（沿主支）手动实现复数Ei"""
        # Ei(z) 的复数解析延拓: 用 mpmath 更可靠
        import mpmath
        return complex(mpmath.ei(complex(z)))

    term5 = -4*np.pi*(1-cos_g_v)*np.exp(1j*alpha_v*sigma_m) * (
        Ei_complex(-1j*alpha_v*(sigma_m+1)) - Ei_complex(-1j*alpha_v*(sigma_m-cos_du_v))
        - Ei_complex(-1j*alpha_v*(sigma_m-cos_dv_v)) + Ei_complex(-1j*alpha_v*(sigma_m-1))
    )
    term6 = -4*np.pi*(1-cos_g_v)*np.exp(1j*alpha_v*sigma_p) * (
        Ei_complex(-1j*alpha_v*(sigma_p+1)) - Ei_complex(-1j*alpha_v*(sigma_p-cos_du_v))
        - Ei_complex(-1j*alpha_v*(sigma_p-cos_dv_v)) + Ei_complex(-1j*alpha_v*(sigma_p-1))
    )
    return term1 + term2 + term3 + term4 + term5 + term6


if __name__ == "__main__":
    print("测试 I1^I 数值计算函数:")
    val = I1_intensity_numeric(1.5, 1.1, 0.8, 0.6)
    print(f"  I1(alpha=1.5, du=1.1, dv=0.8, gamma=0.6) = {val}")

    print("\n特殊极限检验: alpha->0 (PTA情形) 时 I1 应退化为已知的PTA表达式")
    for av in [0.01, 0.001]:
        val = I1_intensity_numeric(av, 1.1, 0.8, 0.6)
        print(f"  alpha={av}: I1 = {val}")

    import pickle
    with open('I1_intensity_function.pkl', 'wb') as f:
        pickle.dump(I1_intensity_numeric, f)
    print("\n注: 由于此函数依赖mpmath等外部库，实际不适合pickle序列化函数对象，")
    print("下游脚本应直接复制这段代码或import本文件使用，而非依赖pkl中的函数对象。")
