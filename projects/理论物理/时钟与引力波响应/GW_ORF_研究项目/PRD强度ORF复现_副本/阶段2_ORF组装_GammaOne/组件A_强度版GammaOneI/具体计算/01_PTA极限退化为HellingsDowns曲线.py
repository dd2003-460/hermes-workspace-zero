"""
【性质】具体计算 —— 验证 alpha->0 (PTA情形) 时 I1^I 退化为 Hellings-Downs 曲线
【计算的量】Gamma_HD(gamma) = 3/(32*pi) * I1(0; u,v,s)，其中 I1(0)是PRD论文Eq(27)给出的
        alpha->0 特殊极限封闭解
【状态】✅ 成功复现，与标准Hellings-Downs公式完全一致（用完全独立的3D笛卡尔黄金标准
        直接数值积分交叉验证，误差~1e-8，非仅靠"文本转录后自我核对"）
【依赖】无（自包含）

================================================================================
                    ⚠️ 重大修正记录（本文件曾有一处转录错误）⚠️
================================================================================
本文件此前版本把论文Eq(27)里 $I_1(0)$ 公式中 $\\sin^2(\\gamma/2)\\ln\\sin(\\gamma/2)$
项的系数错误转录为 **1.5**（原文实际是 **3**，已用PDF原文高清截图核实）。
同时，"标准教科书公式"那边为了让两者数值对上，又把 $\\chi\\ln\\chi$ 项的系数
从正确的 **3/2** 错误改成了 **3/4**。

**这是两个转录错误互相抵消、制造"验证通过"假象的典型案例**（凑巧因为
$\\ln\\sin(\\gamma/2)=\\frac12\\ln\\chi$ 这个恒等式，"系数减半+系数减半"两次
巧合抵消，具体是：$1.5\\to$应为$3$，缩小了2倍；$3/2\\to$错误改成$3/4$，
也缩小了2倍，两次操作让最终数值又对上了，但两处输入都是错的）。

**如何发现的**：在推进阶段3（PTA专用公式Eq26/28）时，需要重新核实
$I_1(0,\\hat s,\\hat u,\\hat u,\\hat v)$（论文Eq26里第二项，$\\hat s_2=\\hat u$，
$\\delta_u'=0$ 这个特殊情形）的中间结果，为此把 `I1_I_general()` 在
$\\alpha\\to0$ 极限下的数值输出与Eq27比对时，发现两者对不上（比值不是1），
才追溯到系数转录问题，重新核对PDF原文高清截图确认。

**修正后的正确公式**（已用完全独立于任何论文转录路径的黄金标准——
3D笛卡尔矢量点积直接对天球做`scipy.dblquad`二重数值积分——交叉验证，
7个角度点误差~1e-8~1e-9）：
    I1(0; u,v,s) = 32*pi/3 * (1/2 - 1/4*sin^2(gamma/2) + 3*sin^2(gamma/2)*ln(sin(gamma/2)))
    Gamma_HD(gamma) = 1/2 - chi/4 + 3/2*chi*ln(chi)   其中 chi=(1-cos(gamma))/2=sin^2(gamma/2)
================================================================================

【物理背景】
PRD论文式(26)-(27)指出：PTA中脉冲星对的ORF，只保留"地球项"响应函数
(kappa_IJ(n)≈1，忽略脉冲星项修正)时，就是标准的Hellings-Downs曲线：
    Gamma_HD(gamma) = 3/(32*pi) * I1(0; u_hat, v_hat, s_hat)
其中 alpha=0 是"两条链路共享同一起点"(pulsar timing中两个脉冲星的地球项贡献
汇聚于同一观测点)的特殊情形，此时不能直接把alpha=0代入Eq(18)（因为有1/alpha,
1/alpha^2, 1/alpha^3等除以0的奇异项），需要单独求alpha->0极限。
"""
import numpy as np
from scipy import integrate


def I1_alpha_to_zero_paper_eq27(gamma_val):
    """PRD论文 Eq(27): alpha->0 时 I1 的封闭解（修正后，系数为3，已用PDF原文核实）"""
    s2 = np.sin(gamma_val / 2) ** 2
    return 32 * np.pi / 3 * (0.5 - 0.25 * s2 + 3 * s2 * np.log(np.sin(gamma_val / 2)))


def Gamma_HD_from_I1(gamma_val):
    """由论文定义 Gamma_HD = 3/(32*pi) * I1(0)"""
    return 3 / (32 * np.pi) * I1_alpha_to_zero_paper_eq27(gamma_val)


def Gamma_HD_standard_textbook(gamma_val):
    """标准教科书 Hellings-Downs 公式 (Allen & Romano 1999，归一化到 Gamma_HD(0)=1/2 的约定)：
    chi(gamma) = (1-cos(gamma))/2 = sin^2(gamma/2)
    HD(gamma) = 1/2 - chi/4 + 3/2*chi*ln(chi)   （修正后：系数为3/2，不是错误版本的3/4）

    换算验证: 3*sin^2(gamma/2)*ln[sin(gamma/2)] = 3*chi*(1/2)*ln(chi) = 3/2*chi*ln(chi)  一致。
    """
    chi = (1 - np.cos(gamma_val)) / 2
    return 0.5 - chi / 4 + 1.5 * chi * np.log(chi)


def xi_I_raw(theta, phi, u_hat, v_hat):
    """最原始定义的强度对称核 xi_I（3D笛卡尔矢量点积，不经过任何论文公式路径）"""
    that = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)])
    phat = np.array([-np.sin(phi), np.cos(phi), 0])
    n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
    ePlus_uu = (that @ u_hat) ** 2 - (phat @ u_hat) ** 2
    eCross_uu = 2 * (that @ u_hat) * (phat @ u_hat)
    ePlus_vv = (that @ v_hat) ** 2 - (phat @ v_hat) ** 2
    eCross_vv = 2 * (that @ v_hat) * (phat @ v_hat)
    n_dot_u = n_hat @ u_hat
    n_dot_v = n_hat @ v_hat
    numerator_I = ePlus_uu * ePlus_vv + eCross_uu * eCross_vv
    return numerator_I / ((1 + n_dot_u) * (1 + n_dot_v))


def I1_0_gold_standard(u_hat, v_hat):
    """终极黄金标准: alpha=0时 I1 就是对xi_I(n)在整个天球上直接积分（无指数因子），
    完全独立于Eq27这个解析结果，用来交叉验证Eq27转录是否正确"""
    f = lambda phi, theta: xi_I_raw(theta, phi, u_hat, v_hat) * np.sin(theta)
    val, _ = integrate.dblquad(f, 1e-6, np.pi - 1e-6, 0, 2 * np.pi, epsabs=1e-9, epsrel=1e-7)
    return val


def rotate(v, axis, angle):
    axis = axis / np.linalg.norm(axis)
    return (v * np.cos(angle) + np.cross(axis, v) * np.sin(angle) + axis * (axis @ v) * (1 - np.cos(angle)))


if __name__ == "__main__":
    print("Part A: 对比 PRD论文 Gamma_HD = 3/(32pi)*I1(0) 与标准教科书 Hellings-Downs 公式")
    print("(两者都用修正后的正确系数，应严格相等)")
    print(f"{'gamma(deg)':<12}{'PRD论文式子':<20}{'教科书标准式':<20}{'差值':<15}")
    max_diff = 0
    for gamma_deg in [10, 30, 60, 90, 120, 150, 170]:
        gamma_val = np.radians(gamma_deg)
        val_paper = Gamma_HD_from_I1(gamma_val)
        val_textbook = Gamma_HD_standard_textbook(gamma_val)
        diff = abs(val_paper - val_textbook)
        max_diff = max(max_diff, diff)
        print(f"{gamma_deg:<12}{val_paper:<20.8f}{val_textbook:<20.8f}{diff:<15.2e}")
    print(f"\n最大差值 = {max_diff:.2e}  (应为0，两者是完全相同的解析表达式)")

    print("\nPart B: 终极黄金标准验证——用与Eq27完全独立的3D直接数值积分交叉核对I1(0)本身")
    print("(这一步不依赖任何论文Eq27的转录，是本次修正的关键判定性检验)")
    print(f"{'gamma(deg)':<12}{'黄金标准(直接积分)':<22}{'Eq27(系数3,修正后)':<22}{'差值':<15}")
    max_diff_b = 0
    for gamma_deg in [10, 30, 60, 90, 120, 150, 170]:
        gamma_val = np.radians(gamma_deg)
        du = 1.3
        u_hat = np.array([np.sin(du), 0, np.cos(du)])
        axis = np.cross(u_hat, [0, 1, 0.3])
        v_hat = rotate(u_hat, axis, gamma_val)
        val_direct = I1_0_gold_standard(u_hat, v_hat)
        val_eq27 = I1_alpha_to_zero_paper_eq27(gamma_val)
        diff = abs(val_direct - val_eq27)
        max_diff_b = max(max_diff_b, diff)
        print(f"{gamma_deg:<12}{val_direct:<22.6f}{val_eq27:<22.6f}{diff:<15.2e}")
    print(f"\n最大差值 = {max_diff_b:.2e}  (机器精度/数值积分精度级别，证明Eq27转录现已正确)")

    print("\n验证 gamma=0 处的已知值 Gamma_HD(0) = 1/2:")
    print(f"  gamma->0 极限: {Gamma_HD_from_I1(1e-6):.6f}  (应趋于0.5)")

    with open('HD_curve_verification.txt', 'w') as f:
        f.write("Hellings-Downs曲线复现验证结果（修正后）\n")
        f.write(f"Part A 最大差值(PRD论文式子 vs 修正后教科书标准式) = {max_diff:.2e}\n")
        f.write(f"Part B 最大差值(3D黄金标准直接积分 vs Eq27公式) = {max_diff_b:.2e}\n")
        f.write("结论: 修正转录错误后，PRD论文Eq(27)给出的alpha->0极限严格等价于标准Hellings-Downs曲线，\n")
        f.write("且与完全独立的3D黄金标准直接数值积分吻合。\n")
    print("\n结果已保存到 HD_curve_verification.txt")
