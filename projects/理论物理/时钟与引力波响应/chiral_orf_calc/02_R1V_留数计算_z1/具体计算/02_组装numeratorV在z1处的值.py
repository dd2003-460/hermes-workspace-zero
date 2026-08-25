"""
【性质】具体计算 —— 用化简好的四个内积，组装 numerator_V(z1) = xi_V 的分子在z1处的值
【计算的量】numerator_V(z1) = e+_uu(z1)*ex_vv(z1) - ex_uu(z1)*e+_vv(z1)
【状态】✅ 成功

【方法说明】
这是"逐个内积化简再组装"策略的第二步。关键教训（详见01_基础设施/探索性尝试/诊断1,3）：
组装时只用 expand()，绝不能对最终乘积调用 factor()（会卡死）。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

# 复用上一步(01)已经算出的、在z1处化简好的四个内积值
tdu = -(uz+x)/s
pdu = -sp.I*(uz+x)/s
tdv = (ux*vz*x**2 - ux*vz - uz*vx*x**2 - sp.I*uz*vy*x - vx*x - sp.I*vy*x**2) / (ux*s)
pdv = -(sp.I*uz*vx + uz*vy*x + sp.I*vx*x + vy) / (ux*s)


if __name__ == "__main__":
    t0 = time.time()
    ePlus_uu  = sp.expand(tdu**2 - pdu**2)
    eCross_uu = sp.expand(2*tdu*pdu)
    print("u侧: ePlus_uu, eCross_uu 组装完成:", time.time()-t0, "s")
    print("  ePlus_uu  =", ePlus_uu)
    print("  eCross_uu =", eCross_uu)
    print("  (注意: eCross_uu = i * ePlus_uu，这是phi.u=i*theta.u的直接推论)")

    t0 = time.time()
    ePlus_vv  = sp.expand(tdv**2 - pdv**2)
    eCross_vv = sp.expand(2*tdv*pdv)
    print("\nv侧: ePlus_vv, eCross_vv 组装完成:", time.time()-t0, "s, ops=",
          sp.count_ops(ePlus_vv), sp.count_ops(eCross_vv))

    t0 = time.time()
    term1 = sp.expand(ePlus_uu * eCross_vv)
    term2 = sp.expand(eCross_uu * ePlus_vv)
    numerator_V_z1 = sp.expand(term1 - term2)
    print("\nnumerator_V(z1) = term1-term2 组装完成:", time.time()-t0,
          "s, ops=", sp.count_ops(numerator_V_z1))

    # 用约束进一步降幂化简 (只用expand，不用factor)
    numV_together = sp.together(numerator_V_z1)
    num, den = sp.fraction(numV_together)
    num = sp.expand(num)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2))
    print("\n最终 numerator_V(z1) 的分母 =", den)
    print("分子 (降幂化简后, ops=%d):" % sp.count_ops(num))
    sp.pprint(num)

    import pickle
    with open('numV_z1_reduced.pkl', 'wb') as f:
        pickle.dump({'num': num, 'den': den}, f)
    print("\n已保存 numV_z1_reduced.pkl 供后续步骤使用")
