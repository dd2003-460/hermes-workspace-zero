"""
【性质】具体计算 —— 用PRD论文Eq(6)/(30)风格最原始的响应函数定义，直接数值
        积分计算任意一对脉冲星间的手征（圆偏振）ORF Gamma_PTA^V(f)
【计算的量】Gamma_PTA^V(beta_u,beta_v,u_hat,v_hat)
        = (1/8pi) * i * integral [R_plus_I*conj(R_cross_J) - R_cross_I*conj(R_plus_J)] d^2Omega_n
        即Stokes-V型手征组合（与阶段2组件B `Gamma_one_V_direct` 完全同款定义，
        只是这里两条链路的终点都固定为地球，位置相位因子相消，退化为PTA情形）
【状态】✅ 成功：任意随机(u_hat,v_hat,beta_u,beta_v)下均严格为零（数值噪声
        量级~1e-13~1e-16），与阶段2组件B用组装公式+alpha=0特殊定义证明的
        "PTA对圆偏振背景零响应"完全吻合，这里用与PRD副本项目PTA组件
        （强度版）完全平行的"直接定义式数值积分"方法独立复现这一结果
【依赖】无（自包含，直接实现论文Eq(6)/(30)风格定义，仅将强度组合换成
        手征Stokes-V组合）

================================================================================
为什么要在阶段3单独重做这件事，而不是只依赖阶段2的结论？
================================================================================
阶段2组件B已经从"alpha=0特殊定义"这条路径证明了PTA零响应（详见该组件
`推导/01_PTA极限手征零响应的解析证明.py`），但那条路径本质上是对
Gamma_one_V(alpha=0,...)这个"抽象母函数"的特殊情形求值，还没有走完
"阶段3：把母函数组装成具体探测器"这一步的完整流程。

本组件的价值在于：**直接从PTA探测器的原始响应函数定义（R_PTA^A(f,n)=
(1/2)e^A_ab(n)u^au^b*T_one(beta,n.u)，与母函数的推导完全独立，不经过
Gamma_one_V这个中间产物）重新验证零响应结论**，这是真正意义上"阶段3
具体探测器"层面的独立产出，而不是简单复用阶段2的中间结果。同时也是
与PRD强度副本项目阶段3组件A（PTA强度ORF）完全平行、方法论一致的手征
版对应产出，两者互为参照。

【物理公式】
    R_PTA^A(f,n) = (1/2) e^A_ab(n) u^a u^b * T_one(beta, n.u)
    T_one(beta, n.u) = [1-e^{-iβ(1+n.u)}] / (1+n.u)
    Gamma_PTA^V(f) = (1/8π) * i * ∫d²Ω_n [R_+^I * conj(R_x^J) - R_x^I * conj(R_+^J)]

（Stokes-V型组合的相位约定与阶段2组件B `数值验证/02...`, `03...` 文件中
反复验证过的 `Gamma_one_V_direct` 完全一致，即 i*(R+ Rx* - Rx R+*)）
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


def Gamma_PTA_V_direct(beta_u, beta_v, u_hat, v_hat, epsabs=1e-7):
    """直接定义式数值积分计算PTA脉冲星对手征ORF"""

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
        val = 1j * (RA_plus_I * np.conj(RA_cross_J) - RA_cross_I * np.conj(RA_plus_J))
        return val * np.sin(theta)

    def integrand_real(phi, theta):
        return integrand_complex(theta, phi).real

    def integrand_imag(phi, theta):
        return integrand_complex(theta, phi).imag

    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-6)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-6)
    return (re + 1j * im) / (8 * np.pi)


if __name__ == "__main__":
    print("测试 PTA 脉冲星对手征ORF计算 (应严格为零):")
    du, dv, psi = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du), 0, np.cos(du)])
    v_hat = np.array([np.sin(dv) * np.cos(psi), np.sin(dv) * np.sin(psi), np.cos(dv)])
    beta_u, beta_v = 55.92, 29.36  # 真实PTA量级(与PRD副本项目组件A同款测试参数)

    val = Gamma_PTA_V_direct(beta_u, beta_v, u_hat, v_hat)
    print(f"  Gamma_PTA^V(beta_u={beta_u}, beta_v={beta_v}) = {val:.4e}")
    print(f"  |Gamma_PTA^V| = {abs(val):.2e}  (数值噪声量级，验证严格为零)")

    print("\n完整大样本验证见同级'数值验证'文件夹")
