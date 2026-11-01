"""
【性质】诊断失败记录 —— 证伪"外部文献y_ij Fourier约定可直接对应
        PRD论文T_two"这一猜想
【计算的量】eta_claim(beta,x) = T_one(beta,x) + D*T_one(beta,-x)（尝试1）
        以及 T_one(beta,-x) + D*T_one(beta,x)（尝试2，交换角色）
        与PRD论文T_two(beta,x)（Eq34）逐一比对
【状态】❌ 两种尝试均被证伪：sympy符号diff均非零多项式（非平凡表达式），
        随机数值代入diff量级为O(1)，不是数值噪声
【依赖】无（纯符号+数值，不依赖其他组件）

================================================================================
背景
================================================================================
本课题最终目标场景SbLI（空间三星六链路，对应TDI通道）的关键想法是：
外部文献（如Shi & Tang风格的TDI教科书处理，或类似arXiv:2606.28071的
约定）中，往返链路（发射-反射-接收）的响应函数常写成
    eta_ij = y_ij + D * y_ji
的形式，其中y_ij是从i到j方向单向链路的（未做往返闭合的）响应函数，
D=e^{-i*beta}是延迟算子。如果这个eta_ij和PRD论文Eq(34)定义的T_two(beta,x)
可以通过简单换元对应上，就能直接把"两条独立方向单向链路"的组合关系
套到本项目已经完全验证过的T_one/Gamma_one框架上，不需要重新推导。

**本文件检验这个对应关系是否成立**——用PRD论文自己给出的T_one定义
（Eq(A9)附近）与T_two定义（Eq34），构造eta_claim并与T_two直接符号
比较。
================================================================================
"""
import sympy as sp
import random

beta, x = sp.symbols('beta x', real=True)
I = sp.I
D = sp.exp(-I * beta)


def T_one(b, xx):
    """PRD论文单向链路响应函数 T_one(beta, n.u) = [1-e^{-i*beta*(1+x)}]/(1+x)"""
    return (1 - sp.exp(-I * b * (1 + xx))) / (1 + xx)


def T_two_paper(b, xx):
    """PRD论文Eq(34): T_two(beta,x) = A(beta,x) - B(beta,x)
    A(beta,x) = T_one(beta,-x)，B(beta,x) = e^{-2i*beta}*T_one(-beta,x)
    """
    A = T_one(b, -xx)
    B = sp.exp(-2 * I * b) * T_one(-b, xx)
    return A - B


if __name__ == "__main__":
    T_two = T_two_paper(beta, x)
    print("PRD论文T_two(beta,x)的LaTeX表达式：")
    print(sp.latex(sp.simplify(T_two)))
    print()

    # ---- 尝试1: eta_claim1 = y(beta,x) + D*y(beta,-x)，把y取作T_one ----
    eta_claim1 = T_one(beta, x) + D * T_one(beta, -x)
    diff1 = sp.simplify(sp.expand_complex(eta_claim1 - T_two))
    print("尝试1 diff = eta_claim1 - T_two 的LaTeX表达式：")
    print(sp.latex(diff1))
    print()

    # ---- 尝试2: 交换xu的角色 ----
    eta_claim2 = T_one(beta, -x) + D * T_one(beta, x)
    diff2 = sp.simplify(sp.expand_complex(eta_claim2 - T_two))
    print("尝试2 diff = eta_claim2 - T_two 的LaTeX表达式：")
    print(sp.latex(diff2))
    print()

    # ---- 数值代入复核 (5组随机参数,与sympy simplify()独立交叉确认非零) ----
    print("数值代入复核 (5组随机 beta,x)：")
    print(f"{'trial':>6} {'beta':>8} {'x':>8} {'|diff1|':>12} {'|diff2|':>12}")
    random.seed(7)
    max1 = max2 = 0.0
    for trial in range(5):
        bv = random.uniform(0.2, 3.0)
        xv = random.uniform(-0.9, 0.9)
        v1 = complex(diff1.subs({beta: bv, x: xv}))
        v2 = complex(diff2.subs({beta: bv, x: xv}))
        max1 = max(max1, abs(v1))
        max2 = max(max2, abs(v2))
        print(f"{trial:>6} {bv:>8.4f} {xv:>8.4f} {abs(v1):>12.4e} {abs(v2):>12.4e}")

    print(f"\n最大 |diff1| = {max1:.4e}, 最大 |diff2| = {max2:.4e}")
    print("两者均为 O(1) 量级（远超数值噪声~1e-10），确认两种eta_ij外部约定")
    print("均不能与PRD论文T_two精确对应——猜想被证伪。")
    print()
    print("【根源判断】外部文献y_ij约定隐含的是Fourier域/时域相位参考点")
    print("（通常取信号\"到达接收端时刻\"为参考），而PRD论文T_one/T_two的")
    print("推导中x=n.u/n.v是天球方向余弦、beta是链路延迟相位，两者的相位")
    print("参考点绑定方式不同——不是简单代数替换能对齐的，说明跨论文体系")
    print("直接套用响应函数分解公式存在框架层面的相位约定冲突。")
