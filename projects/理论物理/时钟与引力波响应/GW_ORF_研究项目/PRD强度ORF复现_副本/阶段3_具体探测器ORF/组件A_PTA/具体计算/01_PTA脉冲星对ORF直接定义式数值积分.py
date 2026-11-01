"""
【性质】具体计算 —— 用PRD论文Eq(6)/(30)最原始的响应函数定义，直接数值积分
        计算任意一对脉冲星间的强度ORF Gamma_PTA(f)
【计算的量】Gamma_PTA(f; beta_u, beta_v, u_hat, v_hat) = (1/8pi) * integral sum_A
        R_PTA,I^A(f,n) * conj(R_PTA,J^A(f,n)) d^2Omega_n
【状态】✅ 成功，与本组件"数值验证"给出的独立蒙特卡洛/网格积分交叉核实，
        与alpha->0极限（Hellings-Downs曲线主导项）在beta_u,beta_v很大时定性吻合
【依赖】无（自包含，直接实现论文Eq(6),(30)）

================================================================================
为什么不逐项转录论文复杂的Eq(28)封闭解，而是走直接定义式数值积分？
================================================================================
详见同组件"推导"文件夹的诊断：PTA情形对应通用Gamma_one_I框架里的一个特殊
构型（delta_u'=0，即s_2恰好与u_hat重合），这是真实的坐标奇异性，通用公式
（组件C/D已验证）无法直接套用。

论文本身用Eq(28)给出了一个独立的、不经过此路径的完整封闭解，但该公式：
  1. 项数众多、跨越两栏排版，转录风险很高（本项目已两次在类似情形栽过跟头：
     手征主线BUG-001、本副本项目Hellings-Downs系数错误，都是转录导致）
  2. 转录得再准确，也只是把论文的解析结果"抄一遍"，不会比"直接数值积分定义式"
     更有说服力——反而验证起来更麻烦（需要再实现一遍论文式26/28的每一项）

**本项目的策略**：直接从PRD论文Eq(6)/(30)"响应函数+ORF"的最原始定义出发，
对天球方向做直接数值积分。这条路径的物理正确性不依赖任何中间解析结果的
转录准确性，是本项目一贯采用的"黄金标准"方法，且已经在阶段1-2的全部组件
中反复验证可靠（误差量级~1e-6~1e-8）。

【物理公式，直接取自论文Eq(6)/(30)】
    R_PTA^A(f,n) = (1/2) e^A_ab(n) u^a u^b * T_one(beta, n.u) * e^{i2πf n.r/c}
    T_one(beta, n.u) = [1-e^{-iβ(1+n.u)}] / (1+n.u)
    Gamma_PTA(f) = (1/8π) ∫d²Ω_n Σ_A R_PTA,I^A(f,n) * conj(R_PTA,J^A(f,n))

对PTA而言，两条link的终点都是地球（公共参考点，位置矢量在计算坐标系里
都设为原点），所以 e^{i2πf n.r/c} 这个相位因子对两条link相同、在做复共轭
乘积时相消，不需要显式包含。
"""
import numpy as np
from scipy import integrate


def T_one(beta, n_dot_u):
    """PRD论文式(6)：单向链路传递函数"""
    return (1 - np.exp(-1j * beta * (1 + n_dot_u))) / (1 + n_dot_u)


def polarization_tensors(n_hat):
    """构造 e^+_ab(n), e^x_ab(n) 3x3矩阵"""
    nx, ny, nz = n_hat
    theta = np.arccos(np.clip(nz, -1, 1))
    phi = np.arctan2(ny, nx)
    theta_hat = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)])
    phi_hat = np.array([-np.sin(phi), np.cos(phi), 0])
    e_plus = np.outer(theta_hat, theta_hat) - np.outer(phi_hat, phi_hat)
    e_cross = np.outer(theta_hat, phi_hat) + np.outer(phi_hat, theta_hat)
    return e_plus, e_cross


def Gamma_PTA_direct(beta_u, beta_v, u_hat, v_hat):
    """直接定义式数值积分计算PTA脉冲星对ORF (论文Eq6+Eq30)"""

    def integrand_complex(theta, phi):
        n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_u = n_hat @ u_hat
        n_dot_v = n_hat @ v_hat
        Tu = T_one(beta_u, n_dot_u)
        Tv = T_one(beta_v, n_dot_v)
        ePlus_uu = u_hat @ e_plus @ u_hat
        eCross_uu = u_hat @ e_cross @ u_hat
        ePlus_vv = v_hat @ e_plus @ v_hat
        eCross_vv = v_hat @ e_cross @ v_hat
        RA_plus_I = 0.5 * ePlus_uu * Tu
        RA_cross_I = 0.5 * eCross_uu * Tu
        RA_plus_J = 0.5 * ePlus_vv * Tv
        RA_cross_J = 0.5 * eCross_vv * Tv
        val = (RA_plus_I * np.conj(RA_plus_J) + RA_cross_I * np.conj(RA_cross_J)) * np.sin(theta)
        return val

    def integrand_real(phi, theta):
        return integrand_complex(theta, phi).real

    def integrand_imag(phi, theta):
        return integrand_complex(theta, phi).imag

    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi - eps, 0, 2 * np.pi, epsabs=1e-9, epsrel=1e-7)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi - eps, 0, 2 * np.pi, epsabs=1e-9, epsrel=1e-7)
    return (re + 1j * im) / (8 * np.pi)


if __name__ == "__main__":
    print("测试 PTA 脉冲星对 ORF 计算:")
    du, dv, psi = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du), 0, np.cos(du)])
    v_hat = np.array([np.sin(dv) * np.cos(psi), np.sin(dv) * np.sin(psi), np.cos(dv)])
    beta_u, beta_v = 50.0, 45.0

    val = Gamma_PTA_direct(beta_u, beta_v, u_hat, v_hat)
    print(f"  Gamma_PTA(beta_u={beta_u}, beta_v={beta_v}) = {val}")

    print("\n完整验证见同级'数值验证'文件夹（用独立的向量化网格积分交叉核实）")
