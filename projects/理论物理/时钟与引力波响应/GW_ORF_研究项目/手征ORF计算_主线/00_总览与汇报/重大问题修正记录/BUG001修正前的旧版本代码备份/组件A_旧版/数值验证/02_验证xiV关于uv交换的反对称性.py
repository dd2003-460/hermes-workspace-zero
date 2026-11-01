"""
【性质】数值验证 —— 独立于任何计算坐标系，验证 xi_V 关于交换 (u,v) 的反对称性
【计算的量】xi_V(n; u, v) 与 -xi_V(n; v, u) 是否恒等
【状态】✅ 完全验证通过 (数值误差恰好为0，不是近似)

【为什么要做这个检验】
这个对称性如果成立，意味着 I_1^V(u,v) = -I_1^V(v,u)，
从而 R3^V(u,v), R4^V(u,v) 这两个"由v决定的极点"的留数，理论上可以通过
"交换u,v角色再取负号"从 R1^V(v,u), R2^V(v,u) 得到 —— 是一条潜在的计算捷径。

【方法】
不依赖任何特定的计算坐标系选取（不锁定u在xz平面），直接用最原始的
三维矢量+球坐标切向基矢量，在随机采样的天球方向n上，数值比较
xi_V(n; u, v) 与 -xi_V(n; v, u) 的差异。这是最"干净"的验证方式，
因为它排除了"计算坐标系选取是否影响对称性成立"这个混淆因素。

【重要提醒 - 后续踩坑记录】
虽然这个对称性本身是严格成立的(见下方验证结果)，但在后续尝试用它
"走捷径"计算R3V,R4V时(见05文件夹)发现直接套用失败了 —— 原因是
R1V,R2V是在"u被锁定在xz平面"这个特定坐标系约定下推导出来的，
直接对调u,v的笛卡尔分量参数违反了这个坐标系约定。
这提醒我们：数学关系成立 ≠ 可以不加考虑地在特定参数化下直接套用。
"""
import numpy as np

def e_plus_cross(n):
    """构造 e^+_{ab}(n), e^x_{ab}(n) 为 3x3 矩阵，用球坐标切向基矢量"""
    nx, ny, nz = n
    theta = np.arccos(np.clip(nz, -1, 1))
    phi = np.arctan2(ny, nx)
    that = np.array([np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), -np.sin(theta)])
    phat = np.array([-np.sin(phi), np.cos(phi), 0])
    e_plus  = np.outer(that, that) - np.outer(phat, phat)
    e_cross = np.outer(that, phat) + np.outer(phat, that)
    return e_plus, e_cross

def contract(e_ab, vec):
    return vec @ e_ab @ vec

def xi_V_value(n, u, v):
    """xi_V(n; u, v) = e+_uu * ex_vv - ex_uu * e+_vv"""
    ep, ec = e_plus_cross(n)
    Puu = contract(ep, u)   # e+_ab u^a u^b
    Cuu = contract(ec, u)   # e×_ab u^a u^b
    Pvv = contract(ep, v)
    Cvv = contract(ec, v)
    return Puu*Cvv - Cuu*Pvv

def random_unit_vector(rng):
    v = rng.normal(size=3)
    return v/np.linalg.norm(v)

if __name__ == "__main__":
    rng = np.random.default_rng(123)
    u = random_unit_vector(rng)
    v = random_unit_vector(rng)

    max_diff = 0
    for _ in range(20):
        n = random_unit_vector(rng)
        val_uv = xi_V_value(n, u, v)
        val_vu = xi_V_value(n, v, u)
        diff = abs(val_uv - (-val_vu))
        max_diff = max(max_diff, diff)

    print("随机测试矢量:")
    print("  u =", u)
    print("  v =", v)
    print(f"\n最大误差 |xi_V(n;u,v) - (-xi_V(n;v,u))| over 20 random n = {max_diff}")
    print("(结果恰好为0，证明 xi_V 关于交换 u,v 严格整体反号，这是一个精确的代数恒等式)")
