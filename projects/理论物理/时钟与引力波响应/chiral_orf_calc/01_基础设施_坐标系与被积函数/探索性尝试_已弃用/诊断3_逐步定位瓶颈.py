"""
【性质】探索性尝试（诊断成功）—— 逐步排查到底是 subs 慢、expand 慢、还是 cancel/factor 慢
【结论】✅ 成功定位瓶颈：subs 和 expand 都很快，真正的瓶颈是通用的 cancel()/factor()

【诊断过程】
分别单独计时 subs(), expand(), cancel() 三个操作，发现：
  - numerator_V.subs(z, z1)：0.01秒（快）
  - sp.expand(...)：9.3秒，展开成约30万项的多项式（能接受）
  - sp.cancel(...)：90秒仍不返回（卡死）

这确认了问题出在 sympy 通用的有理函数化简算法上，而不是代入或展开本身。

【最终解决方案（用在02/03/04的"具体计算"脚本里）】
不要对"整个大表达式"调用cancel/factor，而是：
  1. 先把 theta.u, phi.u, theta.v, phi.v 这四个"小"内积分别代入极点、
     分别用 together+expand+反复用约束(ux^2=1-uz^2, s^2=1-x^2)降幂+cancel 化简
     （每个内积本身只有几十到一百多个操作数，cancel在这个规模上很快，<0.1秒）
  2. 化简后的四个内积表达式已经非常干净（例如 theta.u|z1 = -(uz+x)/s 这种简洁形式）
  3. 再用这些干净的小表达式去组装 e+_uu, ex_uu 等乘积，此时表达式不会再爆炸
  4. 最后只用 expand()（不用 factor/cancel）组装最终的 numerator_V(zk)
"""
import sympy as sp
import time, sys

x, s = sp.symbols('x s', real=True, positive=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

theta_dot_u = ux*x*(1+z**2)/(2*z) - uz*s
phi_dot_u   = sp.I*ux*(z**2-1)/(2*z)
theta_dot_v = vx*x*(1+z**2)/(2*z) + sp.I*vy*x*(z**2-1)/(2*z) - vz*s
phi_dot_v   = sp.I*vx*(z**2-1)/(2*z) + vy*(1+z**2)/(2*z)

ePlus_uu  = theta_dot_u**2 - phi_dot_u**2
eCross_uu = 2*theta_dot_u*phi_dot_u
ePlus_vv  = theta_dot_v**2 - phi_dot_v**2
eCross_vv = 2*theta_dot_v*phi_dot_v

numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
z1 = -(1+uz)*(1+x) / (ux*s)

if __name__ == "__main__":
    print("诊断: subs, expand 各自计时 (证明它们本身不是瓶颈)")
    t0=time.time()
    numV_z1 = numerator_V.subs(z, z1)
    print("subs done", time.time()-t0, "ops=", sp.count_ops(numV_z1))

    t0=time.time()
    numV_z1_expanded = sp.expand(numV_z1)
    print("expand done", time.time()-t0, "size:", sp.count_ops(numV_z1_expanded))
    print("\n结论: subs和expand都很快。真正卡死的是对这个展开后的大表达式再调用cancel()")
    print("(此处不再重复执行cancel()演示卡死，避免脚本运行超时)")

    print("\n" + "="*60)
    print("正确做法演示: 逐个内积先化简，再组装 (这是02/03/04文件夹采用的方法)")
    print("="*60)
    def sub_and_simplify(expr, label):
        t0=time.time()
        val = expr.subs(z, z1)
        val = sp.together(val)
        val = sp.cancel(val)
        print(f"  {label}: ops={sp.count_ops(val)}  time={time.time()-t0:.3f}s")
        return val
    tdu = sub_and_simplify(theta_dot_u, "theta.u")
    pdu = sub_and_simplify(phi_dot_u, "phi.u")
    print("  ↑ 单独对每个内积调用cancel都在0.1秒以内完成，这就是解决方案")
