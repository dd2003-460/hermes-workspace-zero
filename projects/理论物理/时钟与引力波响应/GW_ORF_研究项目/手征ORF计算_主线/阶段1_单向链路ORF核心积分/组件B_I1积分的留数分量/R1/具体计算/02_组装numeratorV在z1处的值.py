"""
【性质】具体计算 —— 用上一步化简好的四个内积，组装 numerator_V 在 z1 处的值
【计算的量】numerator_V(z1) = ePlus_uu(z1)*eCross_vv(z1) - eCross_uu(z1)*ePlus_vv(z1)
【状态】✅ 成功（已应用 BUG-001 修正）
【依赖】01_计算z1处四个内积的化简形式.py 的化简结果（本文件内直接复制，非import）

【BUG-001 修正说明】见同目录 01 号文件开头，theta.v@z1 已用正确符号(-I)重算。
"""
import sympy as sp
from sympy import I, symbols
import time

x = symbols('x')
ux, uz = symbols('u_x u_z', real=True)
vx, vy, vz = symbols('v_x v_y v_z', real=True)
s = symbols('s', real=True, positive=True)

# ---- 从上一步(01号文件)复制过来的、已化简好的四个内积在z1处的值 (BUG-001修正后) ----
tdu_z1 = -(uz + x)/s
pdu_z1 = -I*(uz + x)/s
tdv_z1 = (ux*vz*x**2 - ux*vz - uz*vx*x**2 + I*uz*vy*x - vx*x + I*vy*x**2) / (ux*s)
pdv_z1 = -(I*uz*vx + uz*vy*x + I*vx*x + vy)/(ux*s)

if __name__ == "__main__":
    ePlus_uu_z1 = sp.expand(tdu_z1**2 - pdu_z1**2)
    eCross_uu_z1 = sp.expand(2*tdu_z1*pdu_z1)
    ePlus_vv_z1 = sp.expand(tdv_z1**2 - pdv_z1**2)
    eCross_vv_z1 = sp.expand(2*tdv_z1*pdv_z1)

    print("ePlus_uu@z1  =", sp.factor(ePlus_uu_z1))
    print("eCross_uu@z1 =", sp.factor(eCross_uu_z1))
    ratio = sp.simplify(eCross_uu_z1/ePlus_uu_z1)
    print("eCross_uu/ePlus_uu @z1 =", ratio, " <- 核心恒等式的基础: 在z1处严格等于 +I")

    t0 = time.time()
    numV_z1 = sp.expand(ePlus_uu_z1*eCross_vv_z1 - eCross_uu_z1*ePlus_vv_z1)
    numV_z1 = numV_z1.subs(ux**2, 1-uz**2)
    numV_z1 = sp.expand(numV_z1)
    numV_z1 = numV_z1.subs(s**2, 1-x**2)
    numV_z1 = sp.expand(numV_z1)
    print(f"\nnumerator_V(z1) 组装完成, ops={sp.count_ops(numV_z1)}, 用时{time.time()-t0:.2f}s")

    # 同时算出 numerator_I(z1) 用于交叉核对 -i 比例关系（组件E的核心发现）
    numI_z1 = sp.expand(ePlus_uu_z1*ePlus_vv_z1 + eCross_uu_z1*eCross_vv_z1)
    numI_z1 = numI_z1.subs(ux**2, 1-uz**2); numI_z1 = sp.expand(numI_z1)
    numI_z1 = numI_z1.subs(s**2, 1-x**2); numI_z1 = sp.expand(numI_z1)
    diff_check = sp.simplify(numV_z1 - (-I)*numI_z1)
    print("检验 numerator_V(z1) - (-I)*numerator_I(z1) =", diff_check, " <- 若为0，核心恒等式在新公式下依然成立")

    import pickle
    with open('numV_z1_reduced.pkl', 'wb') as f:
        pickle.dump(numV_z1, f)
    print("\n已保存 numV_z1_reduced.pkl")
