"""
【性质】具体计算 —— 计算 (1+n.v)|z1，并组装出完整的 R1^V 留数封闭表达式
【计算的量】R1^V = Res_{z=z1} f_V(z)
【状态】✅ 成功（含一次符号修正）

【留数公式】
利用 (1+n.u) 在z1处的因式分解 1+n.u = (ux*s)*(z-z1)(z-z2)/(2z)，得到：
    Res_{z=z1} f_V(z) = numerator_V(z1) * 2 / [i * (ux*s) * (z1-z2) * (1+n.v)|z1]

【关键的符号修正记录】
最初用韦达定理反推 (z1-z2) 时，只验证了 (z1-z2)^2 的值，
没有确定平方根的正确符号分支，错误地用了 z1-z2 = +2(x+uz)/(ux*s)。
用直接相减 sp.simplify(z1-z2) 复核后发现正确应为:
    z1 - z2 = -2(uz+x)/(ux*s)   ← 修正后
这个符号错误曾导致数值验证结果整体差一个负号(相对误差=2.0，
即数值大小相同、符号相反)，通过与直接相减的结果对比发现并修正。
"""
import sympy as sp
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

if __name__ == "__main__":
    # ---- 1. 计算 (1+n.v) 在 z1 处的值 ----
    z1 = -(1+uz)*(1+x) / (ux*s)
    one_plus_nv = s/(2*z)*(vx*(1+z**2) + sp.I*vy*(z**2-1)) + vz*x + 1

    onv_z1 = sp.together(one_plus_nv.subs(z, z1))
    num, den = sp.fraction(onv_z1)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    onv_z1_reduced = sp.cancel(num/den)
    print("one_plus_nv(z1) (化简) =")
    sp.pprint(onv_z1_reduced)

    # ---- 2. 验证 z1-z2 的正确符号 (关键修正点) ----
    z2 = -(1-uz)*(1-x) / (ux*s)
    z1_minus_z2_direct = sp.simplify(z1 - z2)
    print("\nz1-z2 (直接相减,权威结果) =", z1_minus_z2_direct)
    print("(注意: 是 -2(uz+x)/(ux*s)，而不是容易猜错的 +2(x+uz)/(ux*s))")
    z1_minus_z2_correct = -2*(uz+x)/(ux*s)

    # ---- 3. 组装最终 R1V ----
    with open('numV_z1_reduced.pkl', 'rb') as f:
        d = pickle.load(f)
    numV_z1_expr = d['num'] / d['den']

    R1V_expr = (numV_z1_expr * 2) / (sp.I * ux*s * z1_minus_z2_correct * onv_z1_reduced)

    print("\n最终 R1^V 表达式 (符号已修正) 组装完成")
    with open('R1V_CORRECTED.pkl', 'wb') as f:
        pickle.dump(R1V_expr, f)
    print("已保存 R1V_CORRECTED.pkl，正确性已在'数值验证'文件夹中交叉核实")
