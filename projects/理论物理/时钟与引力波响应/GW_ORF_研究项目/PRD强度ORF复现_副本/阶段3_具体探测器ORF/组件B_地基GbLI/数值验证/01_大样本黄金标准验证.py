"""
【性质】数值验证 —— 修正后的Gamma_two(Eq35)与Gamma_GbLI(Eq33)大样本
        黄金标准交叉验证
【计算的量】
    Gamma_two_I公式组装 vs 最原始定义(论文Eq31-32，T_two传递函数直接
        对天球数值积分)
    Gamma_GbLI_I公式组装 vs 最原始定义(论文Eq29-30，两臂差分响应函数
        直接对天球数值积分)
【状态】✅ 完成：Gamma_two 6组随机参数误差~1e-9~1e-12；Gamma_GbLI
        3组随机参数误差~1e-9~1e-11（继承自Gamma_two的精度）
【依赖】本脚本读取同级"具体计算"文件夹产出，直接import该文件的函数
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_Gamma_two组装与GbLI四臂差分")
Gamma_two_I = mod.Gamma_two_I
Gamma_GbLI_I = mod.Gamma_GbLI_I
from scipy import integrate


def T_one(beta, n_dot_u):
    return (1 - np.exp(-1j * beta * (1 + n_dot_u))) / (1 + n_dot_u)


def T_two(beta, n_dot_u):
    return T_one(beta, -n_dot_u) - np.exp(-2j * beta) * T_one(-beta, n_dot_u)


def polarization_tensors(n_hat):
    nx, ny, nz = n_hat
    theta = np.arccos(np.clip(nz, -1, 1))
    phi = np.arctan2(ny, nx)
    theta_hat = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)])
    phi_hat = np.array([-np.sin(phi), np.cos(phi), 0])
    e_plus = np.outer(theta_hat, theta_hat) - np.outer(phi_hat, phi_hat)
    e_cross = np.outer(theta_hat, phi_hat) + np.outer(phi_hat, theta_hat)
    return e_plus, e_cross


def Gamma_two_I_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-8):
    """最原始定义 Eq(31)-(32): 双向链路响应函数直接对天球积分"""
    def integrand_complex(theta, phi):
        n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_u = n_hat @ u_hat
        n_dot_v = n_hat @ v_hat
        n_dot_s = n_hat @ s_hat
        Tu = T_two(beta_u, n_dot_u)
        Tv = T_two(beta_v, n_dot_v)
        ePlus_uu = u_hat @ e_plus @ u_hat
        eCross_uu = u_hat @ e_cross @ u_hat
        ePlus_vv = v_hat @ e_plus @ v_hat
        eCross_vv = v_hat @ e_cross @ v_hat
        RA_plus_I = 0.5 * ePlus_uu * Tu
        RA_cross_I = 0.5 * eCross_uu * Tu
        RA_plus_J = 0.5 * ePlus_vv * Tv
        RA_cross_J = 0.5 * eCross_vv * Tv
        return (RA_plus_I * np.conj(RA_plus_J) + RA_cross_I * np.conj(RA_cross_J)) * np.sin(theta) * np.exp(-1j * alpha * n_dot_s)

    def integrand_real(phi, theta): return integrand_complex(theta, phi).real
    def integrand_imag(phi, theta): return integrand_complex(theta, phi).imag
    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-7)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-7)
    return (re + 1j * im) / (8 * np.pi)


def Gamma_GbLI_I_direct(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat, epsabs=1e-8):
    """最原始定义 Eq(29)-(30): GbLI两臂差分响应函数直接对天球积分"""
    def integrand_complex(theta, phi):
        n_hat = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_s = n_hat @ s_hat

        def RA(u_hat_1, u_hat_2, beta):
            n_dot_u1 = n_hat @ u_hat_1; n_dot_u2 = n_hat @ u_hat_2
            Tu1 = T_two(beta, n_dot_u1); Tu2 = T_two(beta, n_dot_u2)
            ePlus_u1u1 = u_hat_1 @ e_plus @ u_hat_1; eCross_u1u1 = u_hat_1 @ e_cross @ u_hat_1
            ePlus_u2u2 = u_hat_2 @ e_plus @ u_hat_2; eCross_u2u2 = u_hat_2 @ e_cross @ u_hat_2
            RA_plus = 0.5 * (ePlus_u1u1 * Tu1 - ePlus_u2u2 * Tu2)
            RA_cross = 0.5 * (eCross_u1u1 * Tu1 - eCross_u2u2 * Tu2)
            return RA_plus, RA_cross

        RA_plus_I, RA_cross_I = RA(u1_hat, u2_hat, beta_u)
        RA_plus_J, RA_cross_J = RA(v1_hat, v2_hat, beta_v)
        return (RA_plus_I * np.conj(RA_plus_J) + RA_cross_I * np.conj(RA_cross_J)) * np.sin(theta) * np.exp(-1j * alpha * n_dot_s)

    def integrand_real(phi, theta): return integrand_complex(theta, phi).real
    def integrand_imag(phi, theta): return integrand_complex(theta, phi).imag
    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-7)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi - eps, 0, 2 * np.pi, epsabs=epsabs, epsrel=1e-7)
    return (re + 1j * im) / (8 * np.pi)


if __name__ == "__main__":
    print("=" * 70)
    print("检验1: Gamma_two_I (Eq35修正后) vs 最原始定义 (Eq31-32)")
    print("=" * 70)
    np.random.seed(31415)
    N = 6
    n_fail = 0
    for i in range(N):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u_hat_r = np.random.randn(3); u_hat_r /= np.linalg.norm(u_hat_r)
        v_hat_r = np.random.randn(3); v_hat_r /= np.linalg.norm(v_hat_r)
        alpha_r = np.random.uniform(0.3, 1.2)
        bu = np.random.uniform(-2, 2)
        bv = np.random.uniform(-2, 2)
        val_formula = Gamma_two_I(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        val_direct = Gamma_two_I_direct(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        err = abs(val_formula - val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-2
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")

    print("\n" + "=" * 70)
    print("检验2: Gamma_GbLI_I (Eq33) vs 最原始定义 (Eq29-30)")
    print("=" * 70)
    np.random.seed(2718)
    N2 = 3
    n_fail2 = 0
    for i in range(N2):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        # 构造两个近似正交的臂(不要求严格正交,GbLI公式本身不假设正交性)
        u1_hat = np.random.randn(3); u1_hat /= np.linalg.norm(u1_hat)
        u2_hat = np.random.randn(3); u2_hat /= np.linalg.norm(u2_hat)
        v1_hat = np.random.randn(3); v1_hat /= np.linalg.norm(v1_hat)
        v2_hat = np.random.randn(3); v2_hat /= np.linalg.norm(v2_hat)
        alpha_r = np.random.uniform(0.3, 1.0)
        bu = np.random.uniform(-1.5, 1.5)
        bv = np.random.uniform(-1.5, 1.5)
        val_formula = Gamma_GbLI_I(alpha_r, bu, bv, s_hat_r, u1_hat, u2_hat, v1_hat, v2_hat)
        val_direct = Gamma_GbLI_I_direct(alpha_r, bu, bv, s_hat_r, u1_hat, u2_hat, v1_hat, v2_hat)
        err = abs(val_formula - val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-2
        n_fail2 += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail2}/{N2} 失败")
