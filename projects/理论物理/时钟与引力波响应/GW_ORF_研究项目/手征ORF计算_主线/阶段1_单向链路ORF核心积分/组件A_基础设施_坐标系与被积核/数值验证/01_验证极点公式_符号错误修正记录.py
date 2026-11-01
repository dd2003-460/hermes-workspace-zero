"""
【性质】数值验证 —— 验证 PRD 论文式(16) 给出的5个极点公式
【计算的量】z0, z1, z2, z3, z4 五个极点是否真的满足 (1+n.u)=0 或 (1+n.v)=0
【状态】✅ 全部通过（论文原文极点公式本身无误，见下方"重大修正说明"）

================================================================================
                    ⚠️ 重大修正说明 (BUG-001 的连带修正) ⚠️
================================================================================
本文件此前（上一轮工作）曾错误地得出"论文极点公式 z3,z4 分母符号有误，
应把 (vx-i*vy) 改成 (vx+i*vy)"的结论，并据此"修正"了 z3,z4。

**这个结论本身是错的，现予以撤销。**

真相是：论文 Eq.(16)/(A7) 打印的 z3,z4（分母 vx-i*vy）本身完全正确。
上一轮工作之所以"验证不通过"，是因为它用来做验证的 n.v 公式本身就是错的
（来自同一处 BUG-001：论文 Eq.(A6) 里 n.v 的 v_y 项符号印刷错误，是 +i*vy，
应为 -i*vy）。用一个错误的 n.v 公式去检验正确的 z3,z4，自然会显示"不通过"；
然后把 z3,z4 也改错，两个错误在特定检验方式下"恰好抵消"，制造了假象的
"验证通过"。这是一次典型的"用带错误的黄金标准做验证，得出错误结论，
再引入第二个错误来凑数"的连锁失误。

详见 `00_总览与汇报/重大问题修正记录/关于PRD论文附录A公式A6的符号错误_详细推导说明.md`
中的完整三层独立验证过程（含用论文自己发表的 R1-R4 封闭解做判决性检验）。

本文件重新组织为：
  Part A: 用【修正后正确的 n.u, n.v 公式】(vy项为 -i) 检验【论文原文未改动的
          z1,z2,z3,z4】，全部应严格通过 (值为0)。
  Part B: 额外展示"如果用错误的 n.v 公式(+i*vy)去检验"会得到看似矛盾的结果，
          以及"如果因此改动 z3,z4"会制造虚假通过——这是留给后来者的方法论教训。
================================================================================
"""
import sympy as sp
from sympy import I, sqrt, symbols, simplify, expand, sin, cos
import numpy as np

x = sp.symbols('x', real=True)
z = sp.symbols('z')
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

# ---- 修正后正确的 n.u, n.v 公式 ----
n_dot_u_correct = ux*sqrt(1-x**2)*(1+z**2)/(2*z) + uz*x
n_dot_v_correct = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) - I*vy*(z**2-1)) + vz*x   # <- 正确: -I

# ---- 论文原文极点公式 (Eq.16/A7)，未做任何改动 ----
z1 = -(1+uz)*(1+x) / (ux*sqrt(1-x**2))
z2 = -(1-uz)*(1-x) / (ux*sqrt(1-x**2))
z3 = -(1+vz)*(1+x) / ((vx - I*vy)*sqrt(1-x**2))     # 论文原文分母 (vx - i*vy)，无需修改
z4 = -(1-vz)*(1-x) / ((vx - I*vy)*sqrt(1-x**2))     # 论文原文分母 (vx - i*vy)，无需修改

du, dv, psi = sp.symbols('delta_u delta_v psi', real=True)
subs_u = {ux: sin(du), uz: cos(du)}
subs_v = {vx: sin(dv)*cos(psi), vy: sin(dv)*sin(psi), vz: cos(dv)}

if __name__ == "__main__":
    print("="*70)
    print("Part A: 用【修正后正确的n.u, n.v公式】检验【论文原文z1,z2,z3,z4(未改动)】")
    print("="*70)
    expr1 = (1+n_dot_u_correct).subs(z, z1).subs(subs_u)
    print("(1+n.u) at z1 (参数化后) =", sp.simplify(sp.trigsimp(expr1)), "  <- 应为0")
    expr2 = (1+n_dot_u_correct).subs(z, z2).subs(subs_u)
    print("(1+n.u) at z2 (参数化后) =", sp.simplify(sp.trigsimp(expr2)), "  <- 应为0")

    expr3 = (1+n_dot_v_correct).subs(z, z3).subs(subs_v)
    val3 = sp.simplify(sp.expand_complex(expr3))
    print("(1+n.v) at z3 (参数化后) =", val3, "  <- 应为0")
    expr4 = (1+n_dot_v_correct).subs(z, z4).subs(subs_v)
    val4 = sp.simplify(sp.expand_complex(expr4))
    print("(1+n.v) at z4 (参数化后) =", val4, "  <- 应为0")

    print("\n多组随机数值抽查 (论文原文z3,z4 + 修正后n.v公式):")
    np.random.seed(42)
    max_err = 0
    for trial in range(8):
        xv = np.random.uniform(-0.9, 0.9)
        dvv = np.random.uniform(0.1, 3.0)
        psiv = np.random.uniform(0.1, 6.0)
        z3v = complex(z3.subs(subs_v).subs({x: xv, dv: dvv, psi: psiv}).evalf())
        z4v = complex(z4.subs(subs_v).subs({x: xv, dv: dvv, psi: psiv}).evalf())
        v3 = complex((1+n_dot_v_correct).subs(subs_v).subs({x: xv, z: z3v, dv: dvv, psi: psiv}).evalf())
        v4 = complex((1+n_dot_v_correct).subs(subs_v).subs({x: xv, z: z4v, dv: dvv, psi: psiv}).evalf())
        max_err = max(max_err, abs(v3), abs(v4))
        print(f"  trial{trial}: x={xv:.3f} dv={dvv:.3f} psi={psiv:.3f}  z3残差={v3:.2e}  z4残差={v4:.2e}")
    print(f"\n结论: 论文原文的极点公式 (z3,z4分母 vx-i*vy, 未改动) 通过全部验证，"
          f"最大残差 = {max_err:.2e} (机器精度量级)")

    print("\n" + "="*70)
    print("Part B (方法论教训展示): 若误用论文Eq(A6)打印的错误n.v公式(+i*vy)去检验")
    print("同样的论文原文z3,z4，会显示'不通过'——但这是黄金标准本身有误，不是z3,z4有误")
    print("="*70)
    n_dot_v_WRONG = sqrt(1-x**2)/(2*z)*(vx*(1+z**2) + I*vy*(z**2-1)) + vz*x  # 论文打印的(有误的)版本
    expr3_wrong = (1+n_dot_v_WRONG).subs(z, z3).subs(subs_v)
    np.random.seed(42)
    xv = np.random.uniform(-0.9, 0.9); dvv = np.random.uniform(0.1, 3.0); psiv = np.random.uniform(0.1, 6.0)
    val_wrong = complex(expr3_wrong.subs({x: xv, dv: dvv, psi: psiv}).evalf())
    print(f"  用错误n.v(+i*vy)检验正确z3: 残差={val_wrong:.4g}  (不为0，容易误导人去怀疑z3有问题)")
    print("  但如第3层判决性检验所证明的(见总览文档)，真正需要修正的是n.v公式的符号，而非z3,z4。")
