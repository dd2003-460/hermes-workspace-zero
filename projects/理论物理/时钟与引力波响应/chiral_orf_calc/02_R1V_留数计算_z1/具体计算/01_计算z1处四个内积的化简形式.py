"""
【性质】具体计算 —— 求 theta.u, phi.u, theta.v, phi.v 在极点 z=z1 处的化简值
【计算的量】theta.u|z1, phi.u|z1, theta.v|z1, phi.v|z1
【状态】✅ 成功，结果非常干净

【方法说明】
这是"逐个内积化简再组装"策略的第一步（该策略的发现过程见上级目录
"01_基础设施/探索性尝试_已弃用/诊断3"）。核心技巧：
  1. 代入极点 z1 后先 together() 通分
  2. 提取分子分母，用 expand() 展开
  3. 反复用几何约束 ux^2=1-uz^2, s^2=1-x^2 (s=sqrt(1-x^2)) 做降幂替换
  4. 最后用 cancel() 约分

由于每个内积单独处理时表达式规模很小（几十到一百多个操作数），
这一整套流程对每个内积只需要 <0.1 秒。

【重要中间结果（后续多处都会用到）】
    theta.u|z1 = -(uz+x)/s
    phi.u|z1   = -i*(uz+x)/s = i * (theta.u|z1)
这个 "phi.u = i*theta.u" 的简洁比例关系，正是06文件夹里
"核心发现：R1V = -i*R1I" 这一恒等式的直接源头。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)   # s = sqrt(1-x^2)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

z1 = -(1+uz)*(1+x) / (ux*s)

theta_dot_u_expr = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u_expr   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v_expr = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v_expr   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)


def sub_and_simplify(expr, zk, label, verbose=True):
    """代入极点zk，通分、展开、cancel化简。这是本次任务的核心加速技巧函数。"""
    t0 = time.time()
    val = expr.subs(z, zk)
    val = sp.together(val)
    val = sp.cancel(val)
    if verbose:
        print(f"  {label}: ops={sp.count_ops(val)}  time={time.time()-t0:.3f}s")
    return val


def reduce_with_constraints(expr):
    """用约束 ux^2=1-uz^2, s^2=1-x^2 反复降幂化简"""
    e = sp.together(expr)
    num, den = sp.fraction(e)
    num = sp.expand(num)
    den = sp.expand(den)
    for _ in range(4):
        num = sp.expand(num.subs(ux**2, 1-uz**2))
        den = sp.expand(den.subs(ux**2, 1-uz**2))
    for _ in range(4):
        num = sp.expand(num.subs(s**2, 1-x**2))
        den = sp.expand(den.subs(s**2, 1-x**2))
    return sp.factor(sp.cancel(num/den))


if __name__ == "__main__":
    print("Step 1: 逐一代入z1并cancel (未加约束降幂)")
    tdu = sub_and_simplify(theta_dot_u_expr, z1, "theta.u")
    pdu = sub_and_simplify(phi_dot_u_expr, z1, "phi.u")
    tdv = sub_and_simplify(theta_dot_v_expr, z1, "theta.v")
    pdv = sub_and_simplify(phi_dot_v_expr, z1, "phi.v")

    print("\nStep 2: 补充约束降幂，得到最简形式")
    tdu_r = reduce_with_constraints(tdu)
    pdu_r = reduce_with_constraints(pdu)
    tdv_r = reduce_with_constraints(tdv)
    pdv_r = reduce_with_constraints(pdv)

    print("\n最终结果:")
    print("theta.u|z1 (化简后) ="); sp.pprint(tdu_r)
    print("\nphi.u|z1 (化简后) ="); sp.pprint(pdu_r)
    print("\ntheta.v|z1 (化简后) ="); sp.pprint(tdv_r)
    print("\nphi.v|z1 (化简后) ="); sp.pprint(pdv_r)

    print("\n关键观察: phi.u|z1 / theta.u|z1 =", sp.simplify(pdu_r/tdu_r))
    print("(这个简洁的 i 比例关系是06文件夹核心发现的源头)")
