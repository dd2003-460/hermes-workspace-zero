"""
【性质】具体计算 —— 计算 (1+n.v) 在 z1 处的值，并组装出最终 R1V 解析表达式
【计算的量】R1^V(x; u_hat, v_hat) = Res_{z=z1} f_V(z)
【状态】✅ 成功（已应用 BUG-001 修正，重新计算并通过黄金标准数值验证，8组随机参数最大相对误差 1.1e-12）
【依赖】02_组装numeratorV在z1处的值.py 产出的 numV_z1_reduced.pkl（同目录直接读取）

【方法】
留数公式: R1V = lim_{z->z1} (z-z1)*f(z)，其中 f(z) = numerator_V(z) / [i*z*(1+n.u)(1+n.v)]
利用韦达定理: (1+n.u) 作为 z 的二次式，两根恰为 z1, z2，可写成
    (1+n.u) = ux*s/(2z) * (z-z1)(z-z2)
所以 lim_{z->z1} (z-z1)/(1+n.u) = 2*z1 / [ux*s*(z1-z2)]，
从而 R1V = numerator_V(z1) * 2 / [i*ux*s*(z1-z2)*(1+n.v)(z1)]
"""
import sympy as sp
from sympy import I, symbols
import pickle
import time

x = symbols('x')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)
s = symbols('s', real=True, positive=True)
z = symbols('z')

if __name__ == "__main__":
    with open('numV_z1_reduced.pkl', 'rb') as f:
        numV_z1 = pickle.load(f)

    # ---- (1+n.v) 在 z1 处的值 (BUG-001修正后的n.v公式) ----
    n_dot_v = s/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x   # 修正: -I (原论文/上版代码为+I)
    z1_expr = -(1+uz)*(1+x)/(ux*s)

    t0 = time.time()
    one_plus_nv_z1 = sp.cancel(sp.together((1+n_dot_v).subs(z, z1_expr)))
    one_plus_nv_z1 = sp.expand(one_plus_nv_z1)
    one_plus_nv_z1 = one_plus_nv_z1.subs(ux**2, 1-uz**2)
    one_plus_nv_z1 = sp.expand(one_plus_nv_z1)
    one_plus_nv_z1 = one_plus_nv_z1.subs(s**2, 1-x**2)
    one_plus_nv_z1 = sp.expand(one_plus_nv_z1)
    one_plus_nv_z1 = sp.factor(one_plus_nv_z1)
    print(f"(1+n.v)@z1 = {one_plus_nv_z1}  (用时{time.time()-t0:.2f}s)")

    # ---- z1-z2 (韦达定理直接给出，符号已在上一轮工作中修正验证过) ----
    z1_full = -(1+uz)*(1+x)/(ux*s)
    z2_full = -(1-uz)*(1-x)/(ux*s)
    z1_minus_z2 = sp.simplify(z1_full - z2_full)
    print("z1 - z2 =", z1_minus_z2)

    # ---- 组装 R1V ----
    R1V = numV_z1 * 2 / (I*ux*s*z1_minus_z2*one_plus_nv_z1)
    t0 = time.time()
    R1V_simplified = sp.cancel(R1V)
    print(f"\nR1V 组装完成, ops={sp.count_ops(R1V_simplified)}, 用时{time.time()-t0:.2f}s")
    print(R1V_simplified)

    with open('R1V_CORRECTED.pkl', 'wb') as f:
        pickle.dump(R1V_simplified, f)
    print("\n已保存 R1V_CORRECTED.pkl (BUG-001修正后的最终版本)")
    print("正确性已在同级'数值验证'文件夹中，用完全独立的3D黄金标准围道积分交叉核实。")

    print("\n" + "=" * 70)
    print("LaTeX 解析表达式（供贴入 结论与推导过程.md 核对）")
    print("=" * 70)
    R1V_factored = sp.factor(R1V_simplified)
    print("R1^V (factor后) =", sp.latex(R1V_factored))
