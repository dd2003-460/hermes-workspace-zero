"""
【性质】具体计算 —— 天基 SbLI（LISA/Taiji/TianQin 型三星六链路 TDI 探测器）
        的精确（全频率、不做长波/小天线近似）ORF 组装：强度 I 与手征 V。
【计算的量】
    Gamma_TDI_channel_I/V(f, links_X, weights_X, links_Y, weights_Y)
    = Σ_{k∈X, l∈Y} w_k w_l^* Gamma_one(α_kl, β_k, β_l, s_kl, d_k, d_l)
    其中每个"带权单向链路"项 = (接收端位置 r_k, 链路方向 d_k, 臂长 L_k, 复权重 w_k)，
    权重 w_k 吸收 TDI 延迟算子在 Fourier 域的标量相位 e^{-iβ}。
【状态】✅ 正确路径实现（纠正旧组件C"框架根本不匹配"的错误诊断）

【为什么旧诊断是错的】
旧组件C（组件C_天基SbLI...）尝试把 TDI 拆成 T_two（往返链路，GbLI 那一套），
四条猜想全部证伪，得出"Γ_one/I1 框架假设位置独立于方向，与 TDI 往返链路
方向-位置耦合，框架根本不匹配"的结论。但 PRD 论文 Eq.(37)-(38) 明确指出：
SbLI 的 TDI 通道"originally a linear superposition of each one-way link"，
用的是 T_one（单向链路）原生形式，根本不经过 T_two！
    R^A_SbLI = (1/2) e^A_ab Σ_i P_i u_i^a u_i^b T_one(f, n·u_i) e^{ik n·r_i}
    Γ_SbLI   = (1/32π) Σ_{i,j} P_i P_j^* Γ_one(β_i,β_j,α_ij,u_i,v_j,s_ij)
TDI 延迟算子 D（单程光行时间延迟）在 Fourier 域只是与 n_hat 无关的标量
相位 e^{-iβ}，延迟后的测量项仍是"一条带标量权的单向链路"，位置取该项在
TDI 参考时刻的卫星位置。Γ_one 的 (r_u, u_hat, L_u) 三个几何要素本来就是
相互独立的自由输入（PRD Eq.(9)），"位置必须独立于方向"是旧尝试拆 T_two
时人为引入的伪约束。本文件严格按 PRD Eq.(37)-(38) 实现。

【TDI-X 通道（第一代 Michelson，等臂长 L，绕卫星1）】
六条单向链路测量 y_{ij}（i 接收、来自 j 的信号；链路方向 d = 从 i 指向 j，
即光传播方向）：y_21, y_31, y_12, y_13, y_32, y_23。
标准第一代 Michelson X（Estabrook-Tinto 约定，Tinto & Armstrong 1999）：
  X = (y_31 - y_21) + D_1 (y_13 - y_12)
      + D_1 D_3 (y_21 - y_31) + D_1 D_2 D_3 (y_12 - y_13)
等臂长 D_i = D = e^{-iβ}。展开成 8 个带权单向链路项（见 tdi_X_links()）。
本文件对符号约定（哪个 y 取正、延迟相位放哪个位置）不做任何"想当然"假设：
全部由数值验证脚本（01_直接天球积分黄金标准...）与最原始的
"逐条链路 T_one 响应 + 延迟相位直接天球积分"比对确认。
"""
import importlib.util
import os
import numpy as np

C_LIGHT = 299792.458  # km/s

# ----------------------------------------------------------------------
# 从已验证的具体计算文件直接导入 Gamma_one_I / Gamma_one_V（项目自包含约定：
# 下游拷贝而非跨目录导入，但这里为避免 ~400 行重复代码，用 importlib 显式
# 加载已通过大样本黄金标准验证的母函数文件；两文件路径固定且经审计报告
# 代码级 diff 确认与各下游拷贝一致）。
# ----------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_COMP = os.path.dirname(_HERE)                    # 组件C2_天基SbLI_TDI正确组装
_STAGE3 = os.path.dirname(_COMP)                  # 阶段3_具体探测器ORF
_MAIN = os.path.dirname(_STAGE3)                  # 手征ORF计算_主线
_PROJ = os.path.dirname(_MAIN)                    # GW_ORF_研究项目


def _load_module(name, abspath):
    spec = importlib.util.spec_from_file_location(name, abspath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod_V = _load_module(
    "gamma_one_V_mod",
    os.path.join(_MAIN, "阶段2_ORF组装_GammaOne", "组件B_手征版GammaOneV",
                 "具体计算", "01_组装通用GammaOneV.py"))
Gamma_one_V = _mod_V.Gamma_one_V

_mod_I = _load_module(
    "gamma_one_I_mod",
    os.path.join(_PROJ, "PRD强度ORF复现_副本", "阶段3_具体探测器ORF",
                 "组件B_地基GbLI", "具体计算",
                 "01_Gamma_two组装与GbLI四臂差分.py"))
Gamma_one_I = _mod_I.Gamma_one_I


# ----------------------------------------------------------------------
# 通用：任意"带权单向链路线性组合通道"之间的 ORF 组装（PRD Eq.(38)）
# ----------------------------------------------------------------------
def gamma_TDI_channels(terms_u, terms_v, f, kind="V"):
    """terms: list of dict(r=接收端位置(km,np.array), d=链路方向(单位np.array),
                          L=臂长(km), w=复权重(含TDI延迟相位))
    Γ_{XY} = Σ_{k∈X,l∈Y} w_k w_l^* Γ_one(α_kl, β_k, β_l, ŝ_kl, d_k, d_l)
    kind='I' 强度 / 'V' 手征。
    """
    G = Gamma_one_I if kind == "I" else Gamma_one_V
    k_wave = 2 * np.pi * f / C_LIGHT
    total = 0.0 + 0.0j
    for t_u in terms_u:
        for t_v in terms_v:
            r_u, d_u, L_u, w_u = t_u["r"], t_u["d"], t_u["L"], t_u["w"]
            r_v, d_v, L_v, w_v = t_v["r"], t_v["d"], t_v["L"], t_v["w"]
            delta_r = r_v - r_u
            dL = np.linalg.norm(delta_r)
            alpha = k_wave * dL
            beta_u = k_wave * L_u
            beta_v = k_wave * L_v
            cos_g_dir = float(np.clip(d_u @ d_v, -1.0, 1.0))
            cos_du_s = float(np.clip(d_u @ (delta_r / dL), -1.0, 1.0))
            cos_dv_s = float(np.clip(d_v @ (delta_r / dL), -1.0, 1.0))
            # 退化情形：(b1) 两链路方向互相平行/反平行；(b2) 任一链路方向
            # 与分离方向 ŝ 平行/反平行（δ_u 或 δ_v → 0/π，使 σ^± 公式中
            # 1-cos²δ 趋零而 σ^±-cosδ 同时趋零，产生 0/0）。等边 TDI
            # 星座中两卫星连线与第三颗卫星的臂方向正好平行，故 (b2) 常见。
            degen = (abs(abs(cos_g_dir) - 1.0) < 1e-6
                     or abs(abs(cos_du_s) - 1.0) < 1e-6
                     or abs(abs(cos_dv_s) - 1.0) < 1e-6)
            if dL < 1e-9 or alpha < 1e-6 or degen:
                # 退化情形直接用原始定义 2D 天球积分（黄金标准路径），
                # 不调用留数母函数。(a) α=0（两条链路接收端共点，如同一颗
                # TDI 卫星上的两条链路）：留数母函数含 1/α 奇异项（PRD
                # Eq.18 不能直接取 α=0，论文 Eq.26-27 也是单独处理）；
                # (b) 方向共线退化（见上）。这些项在 8×8 双重求和中占
                # 少数，计算量可接受，与 PTA(α=0) 处理哲学一致。
                g = _gamma_one_alpha0(r_u, d_u, L_u, d_v, L_v, f, kind)
            else:
                s_hat = delta_r / dL
                g = G(alpha, beta_u, beta_v, s_hat, d_u, d_v)
            total += w_u * np.conj(w_v) * g
    return total


def _gamma_one_alpha0(r_u, d_u, L_u, d_v, L_v, f, kind):
    """α=0 共点链路对的 ORF：直接原始定义天球积分（不依赖 s_hat）。"""
    from scipy import integrate

    def integ(phi, theta):
        ct, st = np.cos(theta), np.sin(theta)
        cp, sp = np.cos(phi), np.sin(phi)
        n = np.array([st * cp, st * sp, ct])
        th = np.array([ct * cp, ct * sp, -st])
        ph = np.array([-sp, cp, 0.0])
        k_wave = 2 * np.pi * f / C_LIGHT
        out = 0.0 + 0.0j
        fus = []
        for (d, L) in [(d_u, L_u), (d_v, L_v)]:
            thu, phu = th @ d, ph @ d
            Fp = 0.5 * (thu ** 2 - phu ** 2)
            Fc = thu * phu
            x = n @ d
            beta = k_wave * L
            denom = 1 + x
            T = 1j * beta if abs(denom) < 1e-12 else (1 - np.exp(-1j * beta * denom)) / denom
            fus.append((Fp * T, Fc * T))
        (pu, cu), (pv, cv) = fus
        if kind == "I":
            val = pu * np.conj(pv) + cu * np.conj(cv)
        else:
            val = pu * np.conj(cv) - cu * np.conj(pv)
        return st * val / (8 * np.pi)

    re, _ = integrate.dblquad(lambda p, t: np.real(integ(p, t)), 0, np.pi, 0, 2 * np.pi,
                              epsabs=1e-12, epsrel=1e-8)
    im, _ = integrate.dblquad(lambda p, t: np.imag(integ(p, t)), 0, np.pi, 0, 2 * np.pi,
                              epsabs=1e-12, epsrel=1e-8)
    return re + 1j * im


# ----------------------------------------------------------------------
# 第一代 Michelson TDI-X 通道：返回 8 个带权单向链路项
# ----------------------------------------------------------------------
def tdi_michelson_links(r1, r2, r3, L):
    """绕卫星1的第一代 Michelson X 通道（等臂长 L）。
    r1,r2,r3: 三颗卫星位置(km)。链路方向 d_{i<-j} = 从接收端 i 指向发射端 j
    （= 光传播方向，与 T_one(beta, n·d) 的约定一致）。
    返回 terms = [dict(r,d,L,w), ...]（8 项），R_X = Σ w R_one(r,d,L)。
    """
    d_21 = (r2 - r1) / np.linalg.norm(r2 - r1)  # 链路1-2，接收端1指向2
    d_31 = (r3 - r1) / np.linalg.norm(r3 - r1)  # 链路1-3，接收端1指向3
    d_12 = -d_21  # 反向：接收端2指向1
    d_13 = -d_31  # 反向：接收端3指向1
    D = lambda n: np.exp(-1j * 2 * np.pi * 1.0 * L / C_LIGHT * 0)  # 占位（频率相关，见下）
    # 延迟相位在频率 f 处计算，这里返回"几何项 + 延迟阶次"，权重在组装时按 f 算
    # 每项: (r_recv, d_dir, link_L, delay_order, sign)
    # X = (y31 - y21) + D1(y13 - y12) + D1D3(y21 - y31) + D1D2D3(y12 - y13)
    terms_raw = [
        (r1, d_31, +1, 0),   #  y31
        (r1, d_21, -1, 0),   # -y21
        (r3, d_13, +1, 1),   # +D1 y13  (D1: 沿臂1方向延迟一次)
        (r2, d_12, -1, 1),   # -D1 y12
        (r1, d_21, +1, 2),   # +D1D3 y21
        (r1, d_31, -1, 2),   # -D1D3 y31
        (r2, d_12, +1, 3),   # +D1D2D3 y12
        (r3, d_13, -1, 3),   # -D1D2D3 y13
    ]
    return terms_raw, L


def tdi_X_terms(r1, r2, r3, L, f):
    """把 tdi_michelson_links 的几何项在频率 f 处实例化为带权 terms。
    D（单程延迟）= e^{-iβ}，β = 2πfL/c；delay_order 次延迟 → e^{-i β·order}。
    """
    terms_raw, Larm = tdi_michelson_links(r1, r2, r3, L)
    beta = 2 * np.pi * f * L / C_LIGHT
    terms = []
    for (r_recv, d_dir, sign, order) in terms_raw:
        w = sign * np.exp(-1j * beta * order)
        terms.append(dict(r=r_recv, d=d_dir, L=Larm, w=w))
    return terms


def Gamma_TDI_X(r1, r2, r3, L, f, kind="V", other=None):
    """单个三角形探测器 TDI-X 通道的自相关 ORF（other=None），
    或两个三角形探测器 X-X 通道间 ORF（other=(r1',r2',r3',L')）。
    注意：自相关手征 Γ^V_{XX} 对共面单探测器为零（需要非共面，见阶段2），
    两个不同探测器（LISA-Taiji/LISA-TianQin 网络）才有非零手征响应。
    """
    terms_X = tdi_X_terms(r1, r2, r3, L, f)
    if other is None:
        terms_Y = terms_X
    else:
        r1o, r2o, r3o, Lo = other
        terms_Y = tdi_X_terms(r1o, r2o, r3o, Lo, f)
    return gamma_TDI_channels(terms_X, terms_Y, f, kind=kind)
