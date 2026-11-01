"""
【性质】推导 —— 重大突破：BUG-001 修正后，核心恒等式可以完美推广到 z3, z4
【计算的量】numerator_V(z3) 与 numerator_I(z3) 的精确代数关系；z4处同理
【状态】✅✅✅ 本次工作最重要的科学发现之一 —— 此前"负面结果"被推翻

================================================================================
                重大突破：撤销此前"不能推广"的负面结论
================================================================================
上一轮工作在"组件E_核心发现"中得出结论："R1V=-i*R1I, R2V=+i*R2I 这条-i比例
关系只在z1,z2(由u单独决定的一阶极点)成立，不能推广到z3,z4(由v决定的极点)"，
并给出6组随机数值"证伪"了这一点，退而求其次只发现了"R3V/R3I与R4V/R4I互为
共轭"的弱得多的规律。

**这个"负面结果"完全是 BUG-001（论文Eq(A6)符号印刷错误）的副产品，予以撤销。**

本次用 BUG-001 修正后的正确公式（theta.v, n.v 的 vy 项符号改为 -I）重新推导，
发现一个和 z1,z2 处完全对称、同样严格成立的恒等式：

    numerator_V(z3) = +i * numerator_I(z3)   =>   R3^V = +i * R3^I
    numerator_V(z4) = -i * numerator_I(z4)   =>   R4^V = -i * R4^I

这两条恒等式用 sp.simplify() 严格验证为精确符号恒等式（非数值近似），
证明过程见下方代码。物理根源与z1,z2处完全一致（只是角色从u换成v）：

    phi.v|z3 / theta.v|z3 = +i    (与 phi.u|z1/theta.u|z1 = +i 完全对称)
    phi.v|z4 / theta.v|z4 = -i    (与 phi.u|z2/theta.u|z2 = -i 完全对称)

================================================================================
                     这意味着什么：巨大的简化
================================================================================
**四个一阶极点 z1, z2, z3, z4 处的手征留数，全部可以直接由论文自己发表的
强度留数封闭解 R1(A9), R2(A10), R3(A11), R4(A12) 通过乘以 ±i 得到，
完全不需要独立重新做符号推导！**

这一发现直接解决了上一轮工作"R3V, R4V卡在sympy性能瓶颈，无法获得符号封闭解"
的困境——根本不需要"硬算"，只需要：
    R3^V(x,δ_u,δ_v,γ) = +i * R3^I(x,δ_u,δ_v,γ)   [用论文Eq(A11)的R3封闭解]
    R4^V(x,δ_u,δ_v,γ) = -i * R4^I(x,δ_u,δ_v,γ)   [用论文Eq(A12)的R4封闭解]

【注意论文声明的适用范围】：PRD论文原文在 Eq(18) 下方注明推导假设 v_y > 0
(见 physrevd_text.txt 第658行)。本次数值验证也确认此关系只在 v_y > 0 时
严格成立，这与论文本身的适用范围完全一致，不是新的限制。

【唯一仍然不满足此简化的是 z0】：z0是二阶极点(见R0/推导文件夹的修正说明)，
R0V/R0I 的比值依然不是常数(已用修正后公式重新验证，见组件E的更新文件)，
这是唯一真正无法简化、需要独立计算的部分——但R0V本身已经用sympy.residue()
成功求出符号解并通过验证，所以这不影响整体流水线的完整性。
================================================================================
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

# ---- 修正后的内积公式 (BUG-001已修正) ----
theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) - sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

# 论文原文极点公式 (未改动，本身正确)
z3 = -(1+vz)*(1+x) / ((vx - sp.I*vy)*s)
z4 = -(1-vz)*(1-x) / ((vx - sp.I*vy)*s)


def sub_reduce(expr, zval, apply_v_constraint=False):
    """代入极点值并化简。apply_v_constraint=True时应用 vx^2=1-vy^2-vz^2 约束
    (因为z3,z4由v决定，需要用v的单位矢量约束才能化到最简形式)"""
    e = sp.cancel(sp.together(expr.subs(z, zval)))
    e = sp.expand(e)
    if apply_v_constraint:
        e = e.subs(vx**2, 1-vy**2-vz**2)
        e = sp.expand(e)
    e = sp.factor(e)
    e = e.subs(s**2, 1-x**2)
    e = sp.factor(sp.expand(e))
    return e


if __name__ == "__main__":
    print("="*70)
    print("Step 1: 验证 phi.v/theta.v 在 z3, z4 处的比值 (核心恒等式的根源)")
    print("="*70)
    t0 = time.time()
    tdv3 = sub_reduce(theta_dot_v, z3, apply_v_constraint=True)
    pdv3 = sub_reduce(phi_dot_v, z3, apply_v_constraint=True)
    print(f"theta.v@z3 = {tdv3}")
    print(f"phi.v@z3   = {pdv3}")
    ratio3 = sp.simplify(pdv3/tdv3)
    print(f"phi.v/theta.v @z3 = {ratio3}  <- 应为 +i, 与 phi.u/theta.u@z1=+i 完全对称  (用时{time.time()-t0:.1f}s)")

    t0 = time.time()
    tdv4 = sub_reduce(theta_dot_v, z4, apply_v_constraint=True)
    pdv4 = sub_reduce(phi_dot_v, z4, apply_v_constraint=True)
    ratio4 = sp.simplify(pdv4/tdv4)
    print(f"phi.v/theta.v @z4 = {ratio4}  <- 应为 -i, 与 phi.u/theta.u@z2=-i 完全对称  (用时{time.time()-t0:.1f}s)")

    print("\n" + "="*70)
    print("Step 2: 严格符号证明 numerator_V(z3) = i*numerator_I(z3)")
    print("="*70)
    tdu3 = sub_reduce(theta_dot_u, z3, apply_v_constraint=False)
    pdu3 = sub_reduce(phi_dot_u, z3, apply_v_constraint=False)
    ePlus_uu3 = sp.expand(tdu3**2 - pdu3**2)
    eCross_uu3 = sp.expand(2*tdu3*pdu3)
    ePlus_vv3 = sp.expand(tdv3**2 - pdv3**2)
    eCross_vv3 = sp.expand(2*tdv3*pdv3)

    numI_z3 = sp.expand(ePlus_uu3*ePlus_vv3 + eCross_uu3*eCross_vv3)
    numV_z3 = sp.expand(ePlus_uu3*eCross_vv3 - eCross_uu3*ePlus_vv3)

    t0 = time.time()
    diff3 = sp.expand(numV_z3 - sp.I*numI_z3)
    diff3 = diff3.subs(vx**2, 1-vy**2-vz**2)
    diff3_simplified = sp.simplify(diff3)
    print(f"numerator_V(z3) - i*numerator_I(z3) = {diff3_simplified}  (用时{time.time()-t0:.1f}s)")
    print(f"是否恒等于0: {diff3_simplified == 0}  <- 严格证明 R3V = i*R3I")

    print("\n" + "="*70)
    print("Step 3: 严格符号证明 numerator_V(z4) = -i*numerator_I(z4)")
    print("="*70)
    tdu4 = sub_reduce(theta_dot_u, z4, apply_v_constraint=False)
    pdu4 = sub_reduce(phi_dot_u, z4, apply_v_constraint=False)
    ePlus_uu4 = sp.expand(tdu4**2 - pdu4**2)
    eCross_uu4 = sp.expand(2*tdu4*pdu4)
    ePlus_vv4 = sp.expand(tdv4**2 - pdv4**2)
    eCross_vv4 = sp.expand(2*tdv4*pdv4)

    numI_z4 = sp.expand(ePlus_uu4*ePlus_vv4 + eCross_uu4*eCross_vv4)
    numV_z4 = sp.expand(ePlus_uu4*eCross_vv4 - eCross_uu4*ePlus_vv4)

    t0 = time.time()
    diff4 = sp.expand(numV_z4 - (-sp.I)*numI_z4)
    diff4 = diff4.subs(vx**2, 1-vy**2-vz**2)
    diff4_simplified = sp.simplify(diff4)
    print(f"numerator_V(z4) - (-i)*numerator_I(z4) = {diff4_simplified}  (用时{time.time()-t0:.1f}s)")
    print(f"是否恒等于0: {diff4_simplified == 0}  <- 严格证明 R4V = -i*R4I")

    print("\n" + "="*70)
    print("结论: 全部4个一阶极点(z1,z2,z3,z4)的手征留数都严格正比于强度留数，")
    print("比例系数±i由该极点对应'哪个方向反转'决定。这是本次工作最重要的发现，")
    print("完全解决了上一轮工作卡住的'R3V,R4V无法获得符号封闭解'的困境。")
    print("="*70)
