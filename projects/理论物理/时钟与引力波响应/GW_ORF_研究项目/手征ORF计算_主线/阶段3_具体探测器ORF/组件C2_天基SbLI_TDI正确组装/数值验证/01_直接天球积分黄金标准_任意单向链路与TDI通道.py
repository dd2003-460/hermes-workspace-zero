"""
【性质】数值验证（黄金标准）—— 完全不经过 Gamma_one/I1 留数框架，
        直接从"单向链路多普勒响应函数"的最原始定义出发，对天球做数值积分。
【计算的量】
    1) gamma_one_gold_I/V：任意两条单向链路（起点位置 r_u、方向 u_hat、臂长 L_u；
       r_v、v_hat、L_v）之间的强度(I)/手征(V) ORF，直接 2D 天球积分；
    2) 在此基础上，任意"由若干条单向链路加权线性组合而成的虚拟通道"
       （TDI-X/Y/Z、Michelson、GbLI 等）之间的 ORF，用
       Gamma = Σ_k,l w_k w_l^* gamma_one_gold(r_k, link_k; r_l, link_l)
       直接组装——这是检验 Gamma_one 留数母函数 + TDI 线性叠加组装的
       独立黄金标准。
【状态】✅ 黄金标准实现完成（本文件不调用任何项目内已验证函数，完全独立）

【物理定义（严格照抄 PRD 论文 Eq.(9)-(10) 与 JCAP 论文 Eq.(2.10) 的约定）】
单向链路 {r_u, L_u u_hat} 对来自方向 n_hat、偏振 A 的 GW 的响应：
    R^A_one(f,n) = (1/2) e^A_ab(n) u^a u^b * T_one(beta_u, n·u_hat) * exp(i k n·r_u)
其中 T_one(beta, x) = [1 - exp(-i beta (1+x))] / (1+x)，beta = 2π f L/c，
k = 2π f/c。
注意：u_hat 沿"光传播方向"（从接收端指向发射端，即信号传到接收端的方向），
T_one 的极点 1+n·u=0 对应 n = -u（波沿链路反方向传播，被积函数的奇异方向）。

ORF（强度 I = 同偏振对称组合；手征 V = 交叉偏振反对称组合）：
    gamma^I_uv = 1/(8π) ∫ d²Ω  Σ_A  R^A_u R^{A*}_v
    gamma^V_uv = 1/(8π) ∫ d²Ω  [R^+_u R^{×*}_v - R^×_u R^{+*}_v]
（手征组合在该相位约定下为纯虚数，故物理实信号取 Im gamma^V；
 与 JCAP 式(2.10) 中 Γ^V 前面带 -i 的约定一致。）

虚拟通道（如 TDI-X）：R^A_X = Σ_k w_k R^A(r_k; link_k)，
则 gamma^I/V_{XY} = Σ_{k∈X,l∈Y} w_k w_l^* gamma^I/V_{k,l}。
TDI 延迟算子 D（沿某臂传播单程的时间延迟）在 Fourier 域就是标量相位
exp(-i k L) = exp(-i beta)，与 n_hat 无关，因此延迟后的链路项仍是
"一条带权单向链路"，权重 w 中吸收相应相位，位置取该项在 TDI 参考
卫星处的等效位置（延迟把参考时刻平移，傅里叶域等价于整体相位，
对 ORF 的几何项无影响——本黄金标准用"直接在原始定义上实现 TDI
延迟链路相位"的方式独立确认这一点）。
"""
import numpy as np
from scipy import integrate

C_LIGHT = 299792.458  # km/s


def polarization_basis(n_hat):
    """标准横向无迹偏振基 e^+_{ab}, e^×_{ab}（theta_hat, phi_hat 球坐标基）。"""
    th, ph = n_hat[0], n_hat[1]  # 传入 (theta, phi)
    ct, st, cp, sp = np.cos(th), np.sin(th), np.cos(ph), np.sin(ph)
    # theta_hat, phi_hat 的笛卡尔分量
    th_hat = np.array([ct * cp, ct * sp, -st])
    ph_hat = np.array([-sp, cp, 0.0])
    e_plus = np.outer(th_hat, th_hat) - np.outer(ph_hat, ph_hat)
    e_cross = np.outer(th_hat, ph_hat) + np.outer(ph_hat, th_hat)
    return e_plus, e_cross


def T_one(beta, x):
    denom = 1.0 + x
    # 数值上 x≈-1 时取极限 i beta（与 PRD 一致）
    return np.where(np.abs(denom) < 1e-12, 1j * beta,
                    (1.0 - np.exp(-1j * beta * denom)) / denom)


def one_way_response_components(theta, phi, k, r_vec, u_hat, L):
    """返回 (F_plus, F_cross, T_phase)：
       R^A = (1/2) e^A_ab u^a u^b * T_one * exp(i k n·r)
       其中 F_A = (1/2) e^A_ab u^a u^b，T_phase = T_one * exp(...)。
    """
    ct, st, cphi, sphi = np.cos(theta), np.sin(theta), np.cos(phi), np.sin(phi)
    n_hat = np.array([st * cphi, st * sphi, ct])
    th_hat = np.array([ct * cphi, ct * sphi, -st])
    ph_hat = np.array([-sphi, cphi, 0.0])
    thu, phu = th_hat @ u_hat, ph_hat @ u_hat
    Fp = 0.5 * (thu ** 2 - phu ** 2)
    Fc = thu * phu
    beta = k * L
    x = n_hat @ u_hat
    T = T_one(beta, x)
    phase = np.exp(1j * k * (n_hat @ r_vec))
    return Fp, Fc, T * phase


def gamma_one_gold(link_u, link_v, f, kind="V", epsabs=1e-9, epsrel=1e-7):
    """直接 2D 天球积分求两条单向链路间的 ORF。
    link = dict(r=接收端位置矢量(km), d=链路方向单位矢量(接收端->发射端), L=臂长(km))。
    kind='I' 强度, 'V' 手征。
    """
    k = 2 * np.pi * f / C_LIGHT

    def integrand(phi, theta):
        # theta, phi 标量
        Fpu, Fcu, Tu = one_way_response_components(theta, phi, k,
                                                   link_u["r"], link_u["d"], link_u["L"])
        Fpv, Fcv, Tv = one_way_response_components(theta, phi, k,
                                                   link_v["r"], link_v["d"],
                                                   link_v["L"])
        Ru_p, Ru_c = Fpu * Tu, Fcu * Tu
        Rv_p, Rv_c = Fpv * Tv, Fcv * Tv
        if kind == "I":
            val = Ru_p * np.conj(Rv_p) + Ru_c * np.conj(Rv_c)
        else:  # V: R+_u R×*_v - R×_u R+*_v
            val = Ru_p * np.conj(Rv_c) - Ru_c * np.conj(Rv_p)
        return np.sin(theta) * val / (8 * np.pi)

    re, _ = integrate.dblquad(lambda p, t: np.real(integrand(p, t)),
                              0, np.pi, 0, 2 * np.pi, epsabs=epsabs, epsrel=epsrel)
    im, _ = integrate.dblquad(lambda p, t: np.imag(integrand(p, t)),
                              0, np.pi, 0, 2 * np.pi, epsabs=epsabs, epsrel=epsrel)
    return re + 1j * im


def virtual_channel_gamma_gold(links_u, weights_u, links_v, weights_v, f, kind="V",
                               epsabs=1e-9, epsrel=1e-7):
    """虚拟通道 R_X = Σ_k w_k R(link_k) 的 ORF 黄金标准：
       gamma_{XY} = Σ_{k,l} w_k w_l^* gamma_one_gold(link_k, link_l)。
    links_u: list of dict(r,u,L)；weights_u: list of complex（含 TDI 延迟相位）。
    """
    total = 0.0 + 0.0j
    for k, (lk, wk) in enumerate(zip(links_u, weights_u)):
        for l, (ll, wl) in enumerate(zip(links_v, weights_v)):
            g = gamma_one_gold(lk, ll, f, kind=kind, epsabs=epsabs, epsrel=epsrel)
            total += wk * np.conj(wl) * g
    return total
