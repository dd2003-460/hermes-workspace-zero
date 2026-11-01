"""
【性质】探索性尝试（已弃用）—— 展示最初直接调用 sympy.factor()/cancel() 会系统性卡死
【结论】❌ 此路不通，但诊断出瓶颈所在，指明了后续应该走"逐个内积化简再组装"的路线

【问题复现】
把 xi_V(x,z) 代入某个极点 z1 后，得到一个约 276 个操作数的表达式（不算大）。
但只要调用 sp.cancel() 或 sp.factor() 对它进行化简，就会在90秒内无法返回结果。
先用 sp.expand() 展开，得到约 30万项的多项式（这本身只需要9秒），
但后续任何进一步的化简尝试都会卡死。

【根本原因（后续在03诊断3中确认）】
sympy 的 factor/cancel 算法在多变量（这里是 u_x,u_z,v_x,v_y,v_z 共5个自由变量）、
高次幂（6次方左右）的有理函数上，通用多项式GCD算法的复杂度会指数级增长。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)
z = sp.symbols('z')

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
    print("Step A: 代入z1到numerator_V (这一步很快)")
    t0 = time.time()
    numV_z1 = numerator_V.subs(z, z1)
    print(f"  完成, 用时{time.time()-t0:.3f}s, ops={sp.count_ops(numV_z1)}")

    print("\nStep B: expand() 展开 (这一步也能忍受，约9秒)")
    t0 = time.time()
    numV_z1_expanded = sp.expand(numV_z1)
    print(f"  完成, 用时{time.time()-t0:.2f}s, ops={sp.count_ops(numV_z1_expanded)}")

    print("\nStep C: 尝试 cancel() 直接化简 —— 这一步会卡死，设置60秒超时演示")
    print("  (实际运行中此步骤需要人工中断，此处仅作说明，不真正执行)")
    print("  教训: 不要对5变量高次表达式直接调用 factor/cancel，")
    print("        应先在数值代入的小表达式上化简，再组装（见02/03/04文件夹的具体计算脚本）")
