"""
用最原始的三维矢量+数值球面积分，独立于任何计算坐标系的选取，
检验 xi_V(n; u, v) = - xi_V(n; v, u) 这个交换对称性是否成立。
这直接决定了 I_1^V(u,v) = -I_1^V(v,u)，从而 R3^V, R4^V 能否由 R1^V, R2^V 通过交换 u<->v 再反号得到。
"""
import numpy as np

def e_plus(n):
    """构造 e^+_{ab}(n) 为 3x3 矩阵，用球坐标切向基失量"""
    nx, ny, nz = n
    theta = np.arccos(np.clip(nz, -1, 1))
    phi = np.arctan2(ny, nx)
    that = np.array([np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), -np.sin(theta)])
    phat = np.array([-np.sin(phi), np.cos(phi), 0])
    return np.outer(that, that) - np.outer(phat, phat), np.outer(that, phat) + np.outer(phat, that)

def contract(e_ab, vec):
    return vec @ e_ab @ vec

def xi_V_value(n, u, v):
    ep, ec = e_plus(n)
    Puu = contract(ep, u)   # e+_ab u^a u^b
    Cuu = contract(ec, u)   # e x_ab u^a u^b
    Pvv = contract(ep, v)
    Cvv = contract(ec, v)
    return Puu*Cvv - Cuu*Pvv

def random_unit_vector(rng):
    v = rng.normal(size=3)
    return v/np.linalg.norm(v)

rng = np.random.default_rng(123)
u = random_unit_vector(rng)
v = random_unit_vector(rng)

# 随机采样天球上多个点n，比较 xi_V(n;u,v) 与 -xi_V(n;v,u)
max_diff = 0
for _ in range(20):
    n = random_unit_vector(rng)
    val_uv = xi_V_value(n, u, v)
    val_vu = xi_V_value(n, v, u)
    diff = abs(val_uv - (-val_vu))
    max_diff = max(max_diff, diff)

print("u =", u)
print("v =", v)
print("最大误差 |xi_V(n;u,v) - (-xi_V(n;v,u))| over 20 random n =", max_diff)
print("(应接近机器精度 ~1e-14 才说明 xi_V 关于交换 u,v 整体反号)")
