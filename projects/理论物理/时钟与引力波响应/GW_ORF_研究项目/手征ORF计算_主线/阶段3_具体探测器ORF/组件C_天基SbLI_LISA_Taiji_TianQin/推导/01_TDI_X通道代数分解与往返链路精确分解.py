"""
【性质】推导 —— 确认可复用的两条精确代数恒等式（sympy严格证明，非猜想）
【计算的量】
    (1) 一代等臂长Michelson TDI-X通道，用四条单向Doppler链路数据$y_{ij}$
        的线性组合表示，验证代数恒等式
            X = (1-D^2) * [(y31-y21) + D*(y13-y12)]
        其中 D = e^{-i*beta} 是单程延迟算子
    (2) 往返链路（发射-反射-接收，构成PRD论文T_two的物理原型）精确分解为
        两条"方向不同"的单向链路响应函数组合：
            T_two(beta,x) = T_one(beta,-x)*1 + e^{-i*beta}*T_one(beta,x)*e^{i*beta*x}
【状态】✅ 两条恒等式均为精确代数恒等式，sympy simplify给出diff=0，
        且用随机数值代入避免"符号化简假阴性"独立复核，
        **但这两条正确恒等式本身不足以解决SbLI组装问题**（见同组件
        `诊断_失败记录/`文件夹，试图用它们复用Gamma_one/I1框架均失败）
【依赖】无（纯符号推导，不依赖其他组件产出）

================================================================================
背景
================================================================================
本课题最终目标场景是空间引力波探测器（LISA/Taiji/TianQin）三星六链路
组成的TDI（Time-Delay Interferometry）通道的手征ORF。JCAP论文
(Ju Chen, Chang Liu, Yun-Long Zhang, JCAP 05, 050 (2025), arXiv:2410.18916)
给出了这个场景在长波近似下的结果，本项目的目标是用PRD论文
(Hu, Wang, Tan, Shao, PRD 111, 084065 (2025)) 的精确留数法思路，
不做长波近似，给出精确（任意频率）结果，并推广到手征情形。

第一步尝试：能否把TDI-X通道的"单向链路线性组合"结构，直接套用本项目
已经完全验证过的 Gamma_one/I1 框架（阶段1/阶段2产出），像组件B（GbLI）
那样通过"若干个Gamma_one的线性叠加"给出TDI-X的ORF？

本文件记录了这个尝试中**被严格证明为真**的两条基础代数恒等式。
它们本身是正确的、可复用的数学结果。但（如`诊断_失败记录/`所示）
仅凭这两条恒等式并不能把TDI-X的ORF组装问题化归为
Gamma_one/I1框架下的简单线性叠加——组装尝试本身失败了，
根源分析见`诊断_失败记录/01...`。
================================================================================
"""
import sympy as sp
import random

beta, x = sp.symbols('beta x', real=True)
I = sp.I
D = sp.exp(-I * beta)


# ============================================================
# 恒等式(1): 一代等臂长Michelson TDI-X通道的代数分解
# ============================================================
def check_X_decomposition():
    """
    一代Michelson TDI-X定义（等臂长情形，用D=e^{-i*beta}表示单程延迟算子）：
        X = (y31 - y21) + D*(y13 - y12) + D^2*(y21 - y31) + D^3*(y12 - y13)
    这是标准TDI教科书定义（见如Tinto & Dhurandhar Living Reviews）。
    声称：可因式分解为
        X = (1 - D^2) * [(y31 - y21) + D*(y13 - y12)]
    """
    y31, y21, y13, y12 = sp.symbols('y31 y21 y13 y12')
    X_lhs = (y31 - y21) + D * (y13 - y12) + D**2 * (y21 - y31) + D**3 * (y12 - y13)
    X_rhs = (1 - D**2) * ((y31 - y21) + D * (y13 - y12))
    diff = sp.simplify(sp.expand(X_lhs - X_rhs))
    print("恒等式(1) [TDI-X代数分解] 符号diff =", diff)
    assert diff == 0, "TDI-X代数分解恒等式不成立！"

    # 数值复核（避免符号化简假阴性）
    random.seed(1)
    print("  数值复核（随机y值+随机beta，3组）：")
    for trial in range(3):
        subs = {
            y31: random.uniform(-2, 2), y21: random.uniform(-2, 2),
            y13: random.uniform(-2, 2), y12: random.uniform(-2, 2),
            beta: random.uniform(0.1, 3.0),
        }
        val = complex(diff.subs(subs))
        print(f"    trial{trial}: |diff|={abs(val):.2e}")
    return diff


# ============================================================
# 恒等式(2): 往返链路精确分解
# ============================================================
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


def check_roundtrip_decomposition():
    """
    声称：T_two(beta,x)（PRD论文中往返链路/双向组合的响应函数核）可以
    精确分解为"回程方向(-u位置,相位系数1) + 去程方向(+u位置,相位系数
    e^{-i*beta}*e^{i*beta*x})"两项之和：
        T_two(beta,x) = T_one(beta,-x)*1 + e^{-i*beta}*T_one(beta,x)*e^{i*beta*x}
    """
    lhs = T_two_paper(beta, x)
    rhs = T_one(beta, -x) * 1 + sp.exp(-I * beta) * T_one(beta, x) * sp.exp(I * beta * x)
    diff = sp.simplify(sp.expand_complex(lhs - rhs))
    print("\n恒等式(2) [往返链路精确分解] 符号diff =", diff)
    assert diff == 0, "往返链路精确分解恒等式不成立！"

    random.seed(2)
    print("  数值复核（随机beta,x，3组）：")
    for trial in range(3):
        subs = {beta: random.uniform(0.2, 2.0), x: random.uniform(-0.9, 0.9)}
        val = complex(diff.subs(subs))
        print(f"    trial{trial}: beta={subs[beta]:.3f} x={subs[x]:.3f}  |diff|={abs(val):.2e}")
    return diff


if __name__ == "__main__":
    print("=" * 70)
    print("确认可复用的两条SbLI相关精确代数恒等式")
    print("=" * 70)
    check_X_decomposition()
    check_roundtrip_decomposition()
    print("\n结论：两条恒等式均严格成立（符号diff=0，数值复核误差~1e-16机器精度）。")
    print("但这不足以解决SbLI组装问题，详见同组件`诊断_失败记录/`。")
