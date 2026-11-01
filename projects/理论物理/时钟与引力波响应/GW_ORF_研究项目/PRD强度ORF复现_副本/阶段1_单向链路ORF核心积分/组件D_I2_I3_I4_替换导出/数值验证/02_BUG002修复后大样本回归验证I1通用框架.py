"""
【性质】数值验证 —— BUG-002(sigma_pm分支选择)修复后，I1_I_general(通用坐标系框架，
        是I2_I,I3_I,I4_I的核心依赖)的大样本回归验证
【计算的量】I1_I_general(alpha, s_hat, u_hat, v_hat) 对任意朝向s_hat,u_hat,v_hat
        vs. scipy.dblquad原始定义直接积分
【状态】✅ 复现此前触发bug的确切病态案例(相对误差降到1e-9)，另外10组任意朝向随机
        测试全部通过(误差~1e-9~1e-11)
【依赖】本脚本读取同级"具体计算"文件夹产出，直接import该文件的函数
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_组装I2I3I4强度版")
I1_I_general = mod.I1_I_general
from scipy import integrate


def I1_direct_dblquad(alpha, s_hat, u_hat, v_hat, epsabs=1e-7):
    ux, uy, uz = u_hat; vx, vy, vz = v_hat

    def integrand(phi, theta):
        x = np.cos(theta); s = np.sin(theta)
        cosphi, sinphi = np.cos(phi), np.sin(phi)
        theta_dot_u = ux*x*cosphi + uy*x*sinphi - uz*s
        phi_dot_u = -ux*sinphi + uy*cosphi
        theta_dot_v = vx*x*cosphi + vy*x*sinphi - vz*s
        phi_dot_v = -vx*sinphi + vy*cosphi
        n_dot_u = ux*s*cosphi + uy*s*sinphi + uz*x
        n_dot_v = vx*s*cosphi + vy*s*sinphi + vz*x
        ePlus_uu = theta_dot_u**2 - phi_dot_u**2
        eCross_uu = 2*theta_dot_u*phi_dot_u
        ePlus_vv = theta_dot_v**2 - phi_dot_v**2
        eCross_vv = 2*theta_dot_v*phi_dot_v
        numerator_I = ePlus_uu*ePlus_vv + eCross_uu*eCross_vv
        denom = (1+n_dot_u)*(1+n_dot_v)
        n_dot_s = s*cosphi*s_hat[0] + s*sinphi*s_hat[1] + x*s_hat[2]
        return numerator_I/denom * np.exp(-1j*alpha*n_dot_s) * s

    re, e1 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).real, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    im, e2 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).imag, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    return re + 1j*im


if __name__ == "__main__":
    print("=== 复现此前触发BUG-002的确切病态案例 (alpha=0.1, beta_u=-0.1构型) ===")
    s_hat = np.array([0, 0, 1.0])
    du_, dv_, psi_ = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du_), 0, np.cos(du_)])
    v_hat = np.array([np.sin(dv_)*np.cos(psi_), np.sin(dv_)*np.sin(psi_), np.cos(dv_)])
    v_hat_neg = -v_hat
    alpha, beta_u = 0.1, -0.1
    combo_vec = alpha*s_hat + beta_u*u_hat
    alpha2 = np.linalg.norm(combo_vec)
    s2_hat = combo_vec / alpha2

    val_general = I1_I_general(alpha2, s2_hat, u_hat, v_hat_neg)
    val_direct = I1_direct_dblquad(alpha2, s2_hat, u_hat, v_hat_neg, epsabs=1e-9)
    print(f"I1_I_general(修复后) = {val_general}")
    print(f"direct dblquad       = {val_direct}")
    err = abs(val_general-val_direct)/abs(val_direct)
    print(f"相对误差 = {err:.2e}  (修复前此案例给出 nan+nanj 或数量级错误的结果)")

    print("\n=== 大样本随机测试(任意朝向s_hat,u_hat,v_hat) ===")
    np.random.seed(777)
    N = 10
    n_fail = 0
    for i in range(N):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u_hat_r = np.random.randn(3); u_hat_r /= np.linalg.norm(u_hat_r)
        v_hat_r = np.random.randn(3); v_hat_r /= np.linalg.norm(v_hat_r)
        alpha_r = np.random.uniform(0.1, 2.0)
        val_g = I1_I_general(alpha_r, s_hat_r, u_hat_r, v_hat_r)
        val_d = I1_direct_dblquad(alpha_r, s_hat_r, u_hat_r, v_hat_r, epsabs=1e-7)
        err = abs(val_g-val_d)/max(abs(val_d), 1e-10)
        fail = err > 1e-3
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.3f} err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")
