"""
【性质】探索性尝试（诊断成功）—— 定位 R3V,R4V 计算比 R1V,R2V 更慢的额外原因
【结论】✅ 定位到瓶颈，但截至任务报告完成时仍未能在合理时间内得到 R3V,R4V 的完整封闭式

【背景】
02/03文件夹的方法（逐个内积化简再组装）成功解决了 R1V, R2V 的计算。
但同样的方法应用在 R3V (z=z3, 由v决定的极点) 上时，依然会卡死。

【诊断发现的额外原因】
R1V,R2V 只需要用到关于 u 的约束: ux^2 = 1 - uz^2 (两个变量)
R3V,R4V 除了同样需要这个u的约束外，还需要用到关于 v 的约束: 
    vx^2 = 1 - vy^2 - vz^2  (三个变量)
这个三变量约束的降幂替换，在与 theta.v, phi.v 等本身已经含有 vx,vy,vz 复杂
组合的表达式相乘后，产生的中间表达式规模远超 u 一侧的情形
(实测 ePlus_uu3 在补充 v 约束前就已经膨胀到 17372 个操作数，
是 R1V 计算中对应量级的约100倍)。

这提示：如果要继续攻克 R3V, R4V，可能需要换一种参数化策略，
比如把 u 和 v 都不锁定在特定坐标平面内、而是用更对称的方式描述两者，
这样可以利用 xi_V 关于 (u,v) 交换的反对称性走捷径，而不需要正面硬算
三变量约束下的化简。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

def sub_reduce_uOnly(expr, zk):
    """只用 u 的约束降幂 (这是最初的实现，对v的部分不够)"""
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.cancel(num/den)

if __name__ == "__main__":
    print("在 z3 处计算四个内积 (这一步本身很快，问题出在下一步组装)")
    t0=time.time()
    tdu3 = sub_reduce_uOnly(theta_dot_u_expr, z3)
    pdu3 = sub_reduce_uOnly(phi_dot_u_expr, z3)
    tdv3 = sub_reduce_uOnly(theta_dot_v_expr, z3)
    pdv3 = sub_reduce_uOnly(phi_dot_v_expr, z3)
    print("四个内积化简完成:", time.time()-t0, "s (这一步很快)")

    print("\n组装 ePlus_uu3 = tdu3^2 - pdu3^2 (未补充v约束，观察规模爆炸):")
    t0=time.time()
    ePlus_uu3 = sp.expand(tdu3**2 - pdu3**2)
    print("完成:", time.time()-t0, "s, ops=", sp.count_ops(ePlus_uu3))
    print("(这里ops已经远超R1V计算中对应步骤的规模，因为分母含有(vx+i*vy)这种")
    print(" 复合表达式，展开后与v的三变量约束纠缠在一起，是导致后续cancel/factor卡死的根源)")
