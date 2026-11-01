"""
【性质】具体计算 —— 组装 R3V, R4V 的最终符号封闭解
【计算的量】R3^V(x; δ_u, δ_v, γ), R4^V(x; δ_u, δ_v, γ)
【状态】✅ 成功（利用推导文件夹证明的严格恒等式 R3V=i*R3I, R4V=-i*R4I，
        直接用论文Eq(A11),(A12)的强度版封闭解乘以±i得到，完全不需要重新硬算）
【依赖】无（论文Eq(A9)-(A12)的封闭解是自包含的解析表达式）

【方法说明】
上一轮工作卡在"R3V,R4V的sympy符号推导因v的三变量约束导致中间表达式膨胀，
反复超时"的困境（v_x^2=1-v_y^2-v_z^2比u的两变量约束u_x^2=1-u_z^2复杂得多）。

本次发现的恒等式 R3^V=+i*R3^I, R4^V=-i*R4^I（见"推导与诊断"文件夹的严格
符号证明）彻底绕开了这个困境：不需要对xi_V重新做一遍完整的留数计算，
只需要复用论文自己已经发表、用δ_u,δ_v,γ,σ^±表示的、简洁得多的强度版
封闭解 R3^I (Eq.A11), R4^I (Eq.A12)，乘以 i 或 -i 即可。

这是"下游只调用上游已验证产出，不重复造轮子"设计哲学的完美体现——
这里的"上游已验证产出"就是PRD论文本身发表的强度ORF结果。
"""
import sympy as sp

x, delta_u, delta_v, gamma = sp.symbols('x delta_u delta_v gamma', real=True)

cos_du, cos_dv, cos_g = sp.cos(delta_u), sp.cos(delta_v), sp.cos(gamma)
disc = sp.sin(gamma)**2 - cos_du**2 - cos_dv**2 + 2*cos_g*cos_du*cos_dv
sigma_plus = 1/(1+cos_g)*(cos_du + cos_dv + sp.I*sp.sqrt(disc))
sigma_minus = 1/(1+cos_g)*(cos_du + cos_dv - sp.I*sp.sqrt(disc))

# 论文 Eq.(A11): R3^I(x) —— 强度版封闭解 (从PRD论文原文直接抄录，未做任何改动)
R3_I = -2*sp.I*(1-cos_g)/(x+sigma_plus) + 2*sp.I*(sigma_minus-cos_dv)*(1+cos_g)/(1-cos_dv**2)

# 论文 Eq.(A12): R4^I(x)
R4_I = 2*sp.I*(1-cos_g)/(x+sigma_minus) - 2*sp.I*(sigma_plus-cos_dv)*(1+cos_g)/(1-cos_dv**2)

# ---- 手征版: 直接乘以 ±i (本次发现的核心恒等式) ----
R3_V = sp.I * R3_I
R4_V = -sp.I * R4_I

if __name__ == "__main__":
    print("R3^V(x; delta_u, delta_v, gamma) = i * R3^I =")
    print(" ", sp.simplify(R3_V))
    print("\nR4^V(x; delta_u, delta_v, gamma) = -i * R4^I =")
    print(" ", sp.simplify(R4_V))

    import pickle
    with open('R3V_R4V_closed_form.pkl', 'wb') as f:
        pickle.dump({'R3_V': R3_V, 'R4_V': R4_V, 'R3_I': R3_I, 'R4_I': R4_I}, f)
    print("\n已保存 R3V_R4V_closed_form.pkl")
    print("正确性验证见同级'数值验证'文件夹（独立3D黄金标准围道积分交叉核实）")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    print("sigma^+ =", sp.latex(sigma_plus))
    print()
    print("sigma^- =", sp.latex(sigma_minus))
    print()
    print("R3^I(x) =", sp.latex(R3_I))
    print()
    print("R4^I(x) =", sp.latex(R4_I))
    print()
    print("R3^V(x) = i*R3^I(x) =", sp.latex(sp.simplify(R3_V)))
    print()
    print("R4^V(x) = -i*R4^I(x) =", sp.latex(sp.simplify(R4_V)))
