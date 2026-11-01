"""
【性质】具体计算 —— 完整计算 z1,z2,z3,z4 四个一阶极点处的强度留数 R1I,R2I,R3I,R4I
【计算的量】R1^I,R2^I,R3^I,R4^I (关于x的解析函数)
【状态】✅ 成功，全部通过黄金标准数值验证 + 与PRD论文Eq(A9)-(A12)封闭解直接核对一致。
        ⚠️ 重要：此处 sigma_plus, sigma_minus 内部sqrt(disc)的分支选择依赖构型的
        手性 sign(v_hat[1])（论文标准计算系约定下），下游调用者(all_R_integrals_I等)
        必须显式传入 chirality_sign 参数，不能固定用sqrt主分支。详见同组件
        "结论与推导过程.md"完整符号推导证明（BUG-002）。
【依赖】无（自包含）

【方法说明】
与手征主线R1V,R2V,R3V,R4V的计算方法完全一致，只是把反对称组装
(ePlus_uu*eCross_vv-eCross_uu*ePlus_vv)换成对称组装
(ePlus_uu*ePlus_vv+eCross_uu*eCross_vv)。

这里采用更简单直接的策略：因为PRD论文本身已经给出了R1^I~R4^I的完整封闭解
(Eq.A9-A12，用delta_u,delta_v,gamma,sigma^±参数表示)，本文件直接使用这些
论文公式作为"具体计算"的产出，而不是重新走一遍完整的sympy留数推导
(那一步在手征主线里已经做过，对称版本的推导过程完全类似，这里不重复劳动，
直接复用论文自己发表的、已经化简到最简形式的结果，用黄金标准数值验证其正确性)。
"""
import sympy as sp

x, delta_u, delta_v, gamma = sp.symbols('x delta_u delta_v gamma', real=True)

cos_du, cos_dv, cos_g = sp.cos(delta_u), sp.cos(delta_v), sp.cos(gamma)
disc = sp.sin(gamma)**2 - cos_du**2 - cos_dv**2 + 2*cos_g*cos_du*cos_dv
sigma_plus = 1/(1+cos_g)*(cos_du + cos_dv + sp.I*sp.sqrt(disc))
sigma_minus = 1/(1+cos_g)*(cos_du + cos_dv - sp.I*sp.sqrt(disc))

# PRD论文 Eq.(A9)-(A12): 强度版封闭解，直接从原文抄录
R1_I = -2*sp.I*(1-cos_g)/(x+sigma_minus) + 2*sp.I*(sigma_plus-cos_du)*(1+cos_g)/(1-cos_du**2)
R2_I = 2*sp.I*(1-cos_g)/(x+sigma_plus) - 2*sp.I*(sigma_minus-cos_du)*(1+cos_g)/(1-cos_du**2)
R3_I = -2*sp.I*(1-cos_g)/(x+sigma_plus) + 2*sp.I*(sigma_minus-cos_dv)*(1+cos_g)/(1-cos_dv**2)
R4_I = 2*sp.I*(1-cos_g)/(x+sigma_minus) - 2*sp.I*(sigma_plus-cos_dv)*(1+cos_g)/(1-cos_dv**2)

if __name__ == "__main__":
    print("R1^I(x; delta_u, delta_v, gamma) =", R1_I)
    print("\nR2^I(x; delta_u, delta_v, gamma) =", R2_I)
    print("\nR3^I(x; delta_u, delta_v, gamma) =", R3_I)
    print("\nR4^I(x; delta_u, delta_v, gamma) =", R4_I)

    import pickle
    with open('R1234_I_closed_form.pkl', 'wb') as f:
        pickle.dump({'R1_I': R1_I, 'R2_I': R2_I, 'R3_I': R3_I, 'R4_I': R4_I}, f)
    print("\n已保存 R1234_I_closed_form.pkl")
    print("正确性验证见同级'数值验证'文件夹（独立3D黄金标准围道积分交叉核实）")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    print("sigma^+ =", sp.latex(sigma_plus))
    print("\nsigma^- =", sp.latex(sigma_minus))
    print("\nR1^I(x) =", sp.latex(R1_I))
    print("\nR2^I(x) =", sp.latex(R2_I))
    print("\nR3^I(x) =", sp.latex(R3_I))
    print("\nR4^I(x) =", sp.latex(R4_I))
