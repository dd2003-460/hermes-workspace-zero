"""
【性质】数值验证 —— BUG-002(sigma_pm分支选择错误，从PRD强度副本项目同步发现)
        修复后，手征I1_V_general的大样本回归验证
【计算的量】I1_V_general(alpha, s_hat, u_hat, v_hat) 任意朝向 vs.
        scipy.dblquad手征原始定义(numerator_V=ePlus_uu*eCross_vv-eCross_uu*ePlus_vv)
        直接积分
【状态】✅ 12组任意朝向随机测试全部通过，误差~1e-8~1e-11
        (修复前同样测试约50%失败，误差量级可达几百倍)
【依赖】本脚本读取同级"具体计算"文件夹产出，直接import该文件的函数
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_组装I2VI3VI4V")
I1_V_general = mod.I1_V_general
from scipy import integrate


def I1_V_direct_dblquad(alpha, s_hat, u_hat, v_hat, epsabs=1e-7):
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
        numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
        denom = (1+n_dot_u)*(1+n_dot_v)
        n_dot_s = s*cosphi*s_hat[0] + s*sinphi*s_hat[1] + x*s_hat[2]
        return numerator_V/denom * np.exp(-1j*alpha*n_dot_s) * s

    re, e1 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).real, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    im, e2 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).imag, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    return re + 1j*im


if __name__ == "__main__":
    np.random.seed(2024)
    N = 12
    n_fail = 0
    print("测试手征I1_V_general (BUG-002修复后) vs 原始定义, 任意朝向:")
    for i in range(N):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u_hat_r = np.random.randn(3); u_hat_r /= np.linalg.norm(u_hat_r)
        v_hat_r = np.random.randn(3); v_hat_r /= np.linalg.norm(v_hat_r)
        alpha_r = np.random.uniform(0.3, 2.0)
        val_g = I1_V_general(alpha_r, s_hat_r, u_hat_r, v_hat_r)
        val_d = I1_V_direct_dblquad(alpha_r, s_hat_r, u_hat_r, v_hat_r)
        err = abs(val_g-val_d) / max(abs(val_d), 1e-10)
        fail = err > 1e-3
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.3f} err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")
