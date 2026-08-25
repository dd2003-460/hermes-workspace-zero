"""
【性质】推导尝试（未完成，超时）—— 仿照R1V,R2V方法直接对z3计算，记录性能瓶颈
【计算的量】numerator_V(z3) 的化简
【状态】❌ 超时未完成，但诊断出了明确的瓶颈原因

【与R1V,R2V计算的关键差异】
z1,z2 只需要用到关于u的约束: ux^2 = 1-uz^2 (两变量约束)
z3,z4 除了同样需要u的约束外，还需要用到关于v的约束: vx^2 = 1-vy^2-vz^2 (三变量约束)

代码流程完全模仿02/03文件夹的"具体计算"脚本，唯一的区别是补充了
对 vx^2 的降幂替换。但即使加上这个约束，中间表达式规模依然爆炸——
仅仅是 ePlus_uu3 = tdu3^2 - pdu3^2 这一步（对照02文件夹里u侧
对应的运算几乎是瞬间完成），实测就需要0.27秒/17372个操作数，
是u侧对应步骤的百倍量级；后续步骤的规模继续累积，最终导致
整体流程在90~280秒内无法返回。

本文件保留了完整的尝试代码(标注了预计会卡住的位置)，
供后续如果要继续攻克这个问题时参考起点，但不建议直接运行到底
(会长时间无响应)。
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


def sub_reduce_full(expr, zk):
    """加入了对u约束、s约束、以及新增的v约束(vx^2)的降幂"""
    val = sp.together(expr.subs(z, zk))
    num, den = sp.fraction(val)
    num = sp.expand(num); den = sp.expand(den)
    for _ in range(6):
        num = sp.expand(num.subs(ux**2, 1-uz**2)); den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(6):
        num = sp.expand(num.subs(s**2, 1-x**2)); den = sp.expand(den.subs(s**2, 1-x**2))
    for _ in range(4):
        num = sp.expand(num.subs(vx**2, 1-vy**2-vz**2)); den = sp.expand(den.subs(vx**2, 1-vy**2-vz**2))
    return sp.cancel(num/den)


if __name__ == "__main__":
    print("Step 1: 在z3处计算四个内积 (这一步本身较快，约0.2-1秒完成)")
    t0 = time.time()
    tdu3 = sub_reduce_full(theta_dot_u_expr, z3)
    pdu3 = sub_reduce_full(phi_dot_u_expr, z3)
    tdv3 = sub_reduce_full(theta_dot_v_expr, z3)
    pdv3 = sub_reduce_full(phi_dot_v_expr, z3)
    print("完成:", time.time()-t0, "s")
    print("theta.v|z3 =", tdv3)
    print("phi.v|z3   =", pdv3)

    print("\nStep 2: 组装 ePlus_uu3 (此步骤已观察到规模远超预期，是真正瓶颈的开始)")
    t0 = time.time()

    def reduce_expand(e):
        e = sp.expand(e)
        for _ in range(4):
            e = sp.expand(e.subs(vx**2, 1-vy**2-vz**2))
        return e

    ePlus_uu3 = reduce_expand(tdu3**2 - pdu3**2)
    print("完成:", time.time()-t0, "s, ops=", sp.count_ops(ePlus_uu3))
    print("(对照R1V计算中同类步骤通常<0.01秒、ops<20，这里已经膨胀了2个数量级)")
    print("\n后续 eCross_uu3, ePlus_vv3, eCross_vv3 的组装，以及最终numerator_V(z3)")
    print("的通分/降幂，在此规模基础上会进一步累积，最终导致90秒以上无法完成。")
    print("(为避免脚本长时间无响应，此处不再继续往下执行)")
