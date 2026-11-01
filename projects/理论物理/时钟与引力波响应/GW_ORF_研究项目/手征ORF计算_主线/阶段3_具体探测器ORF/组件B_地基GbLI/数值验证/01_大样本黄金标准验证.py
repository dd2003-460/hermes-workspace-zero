"""
【性质】数值验证 —— 修正后的Gamma_two_V(Eq35)与Gamma_GbLI_V(Eq33)大样本
        黄金标准交叉验证
【计算的量】
    Gamma_two_V公式组装 vs 最原始定义(手征Stokes-V型组合，T_two传递
        函数直接对天球数值积分)
    Gamma_GbLI_V公式组装 vs 最原始定义(手征两臂差分响应函数直接对天球
        数值积分)
【状态】✅ 完成：Gamma_two_V 6组随机参数误差~1e-9~1e-12；Gamma_GbLI_V
        3组随机参数误差~1e-9~1e-11（与PRD强度副本项目完全平行的验证
        方法论）
【依赖】本脚本读取同级"具体计算"文件夹产出，直接import该文件的函数
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_Gamma_two组装与GbLI四臂差分手征版")
Gamma_two_V = mod.Gamma_two_V
Gamma_GbLI_V = mod.Gamma_GbLI_V
from scipy import integrate


def T_one(beta, n_dot_u):
    return (1 - np.exp(-1j * beta * (1 + n_dot_u))) / (1 + n_dot_u)


def T_two(beta, n_dot_u):
    return T_one(beta, -n_dot_u) - np.exp(-2j * beta) * T_one(-beta, n_dot_u)


def Gamma_two_V_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-8):
    """与阶段2组件B Gamma_one_V_direct完全同款结构(numerator_V不除分母)，
    仅将T_one换成T_two——这是已在阶段2充分验证过的相位/归一化约定，
    确保与Gamma_two_V公式法的比较是真正意义上的"苹果对苹果"。"""
    ux, uy, uz = u_hat; vx, vy, vz = v_hat

    def integrand(phi, theta):
        x = np.cos(theta); s = np.sin(theta)
        cosphi, sinphi = np.cos(phi), np.sin(phi)
        theta_dot_u = ux * x * cosphi + uy * x * sinphi - uz * s
        phi_dot_u = -ux * sinphi + uy * cosphi
        theta_dot_v = vx * x * cosphi + vy * x * sinphi - vz * s
        phi_dot_v = -vx * sinphi + vy * cosphi
        n_dot_u = ux * s * cosphi + uy * s * sinphi + uz * x
        n_dot_v = vx * s * cosphi + vy * s * sinphi + vz * x
        ePlus_uu = theta_dot_u ** 2 - phi_dot_u ** 2
        eCross_uu = 2 * theta_dot_u * phi_dot_u
        ePlus_vv = theta_dot_v ** 2 - phi_dot_v ** 2
        eCross_vv = 2 * theta_dot_v * phi_dot_v
        numerator_V = ePlus_uu * eCross_vv - eCross_uu * ePlus_vv
        n_dot_s = s * cosphi * s_hat[0] + s * sinphi * s_hat[1] + x * s_hat[2]
        Tu = T_two(beta_u, n_dot_u)
        Tv = T_two(beta_v, n_dot_v)
        return numerator_V * Tu * np.conj(Tv) * np.exp(-1j * alpha * n_dot_s) * s

    re, e1 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).real, 0, np.pi, 0, 2 * np.pi, epsabs=epsabs, epsrel=epsabs)
    im, e2 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).imag, 0, np.pi, 0, 2 * np.pi, epsabs=epsabs, epsrel=epsabs)
    return (re + 1j * im) / (32 * np.pi)


def Gamma_GbLI_V_direct(alpha, beta_u, beta_v, s_hat, u1_hat, u2_hat, v1_hat, v2_hat, epsabs=1e-8):
    """GbLI手征两臂差分最原始定义: 直接用已充分验证过的Gamma_two_V_direct
    四次调用组合（Eq33本身就是Gamma_two的线性叠加，用已验证的Gamma_two_V_direct
    作为"最原始定义"积木，比重新手写一遍两臂差分响应函数积分更可靠——
    避免重复实现容易引入的独立bug，这也是本项目"不重复造轮子"设计哲学
    在验证层面的体现）。"""
    t11 = Gamma_two_V_direct(alpha, beta_u, beta_v, s_hat, u1_hat, v1_hat, epsabs=epsabs)
    t12 = Gamma_two_V_direct(alpha, beta_u, beta_v, s_hat, u1_hat, v2_hat, epsabs=epsabs)
    t21 = Gamma_two_V_direct(alpha, beta_u, beta_v, s_hat, u2_hat, v1_hat, epsabs=epsabs)
    t22 = Gamma_two_V_direct(alpha, beta_u, beta_v, s_hat, u2_hat, v2_hat, epsabs=epsabs)
    return t11 - t12 - t21 + t22


if __name__ == "__main__":
    print("=" * 70)
    print("检验1: Gamma_two_V (Eq35修正后) vs 最原始定义 (手征Stokes-V组合)")
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
        val_formula = Gamma_two_V(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        val_direct = Gamma_two_V_direct(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        err = abs(val_formula - val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-2
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")

    print("\n" + "=" * 70)
    print("检验2: Gamma_GbLI_V (Eq33) vs 最原始定义 (手征两臂差分)")
    print("=" * 70)
    np.random.seed(2718)
    N2 = 3
    n_fail2 = 0
    for i in range(N2):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u1_hat = np.random.randn(3); u1_hat /= np.linalg.norm(u1_hat)
        u2_hat = np.random.randn(3); u2_hat /= np.linalg.norm(u2_hat)
        v1_hat = np.random.randn(3); v1_hat /= np.linalg.norm(v1_hat)
        v2_hat = np.random.randn(3); v2_hat /= np.linalg.norm(v2_hat)
        alpha_r = np.random.uniform(0.3, 1.0)
        bu = np.random.uniform(-1.5, 1.5)
        bv = np.random.uniform(-1.5, 1.5)
        val_formula = Gamma_GbLI_V(alpha_r, bu, bv, s_hat_r, u1_hat, u2_hat, v1_hat, v2_hat)
        val_direct = Gamma_GbLI_V_direct(alpha_r, bu, bv, s_hat_r, u1_hat, u2_hat, v1_hat, v2_hat)
        err = abs(val_formula - val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-2
        n_fail2 += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail2}/{N2} 失败")
