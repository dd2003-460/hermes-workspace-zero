"""
【性质】数值验证 —— BUG-002(sigma_pm分支选择错误)修复后，Gamma_one_V通用组装公式
        (任意alpha,beta_u,beta_v含负值,任意朝向s_hat,u_hat,v_hat)的大样本验证
【计算的量】Gamma_one_V(alpha,beta_u,beta_v,s_hat,u_hat,v_hat) vs.
        手征最原始定义 numerator_V*T_one(bu,n.u)*conj(T_one(bv,n.v))*e^{-i*alpha*n.s}
        直接2D数值积分（归一化1/(32*pi)，与I1定义一致）
【状态】✅ 10组随机参数(beta_u,beta_v含正负,任意朝向)全部通过，误差~1e-9~1e-12
【依赖】本脚本读取同级"具体计算"文件夹产出(Gamma_one_V)

【重要说明：验证脚本本身的一处教训】
第一次尝试验证时，误将 xi_V=numerator_V/denom（已除过分母）与含独立
1/(1+n.u), 1/(1+n.v)因子的T_one相乘，导致重复除以分母，比值系统性错误
（约差sqrt(2)的固定比例，这是我自己验证脚本的bug，不是Gamma_one_V代码的
bug）。修正为"直接用不含分母的numerator_V乘T_one(含自己的分母)"后，
才是真正等价于原始定义的正确构造，随后0/10失败，验证通过。
这个教训被保留在此说明中，提醒后续任何人在搭建独立验证时要留意"核函数是否
已经隐式包含了链路传递函数的分母因子"这类容易重复计算的细节。
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_组装通用GammaOneV")
Gamma_one_V = mod.Gamma_one_V
from scipy import integrate


def T_one(beta, n_dot_u):
    return (1 - np.exp(-1j*beta*(1+n_dot_u))) / (1+n_dot_u)


def Gamma_one_V_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-7):
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
        numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv   # 不除分母！
        n_dot_s = s*cosphi*s_hat[0] + s*sinphi*s_hat[1] + x*s_hat[2]
        Tu = T_one(beta_u, n_dot_u)   # 已经含1/(1+n_dot_u)
        Tv = T_one(beta_v, n_dot_v)   # 已经含1/(1+n_dot_v)
        return numerator_V * Tu * np.conj(Tv) * np.exp(-1j*alpha*n_dot_s) * s

    re, e1 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).real, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    im, e2 = integrate.dblquad(lambda phi, theta: integrand(phi, theta).imag, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    return (re + 1j*im) / (32*np.pi)


if __name__ == "__main__":
    np.random.seed(2026)
    N = 10
    n_fail = 0
    print("测试Gamma_one_V (BUG-002修复后) vs 手征最原始定义:")
    for i in range(N):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u_hat_r = np.random.randn(3); u_hat_r /= np.linalg.norm(u_hat_r)
        v_hat_r = np.random.randn(3); v_hat_r /= np.linalg.norm(v_hat_r)
        alpha_r = np.random.uniform(0.3, 2.0)
        bu = np.random.uniform(-2, 2)
        bv = np.random.uniform(-2, 2)
        val_formula = Gamma_one_V(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        val_direct = Gamma_one_V_direct(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        err = abs(val_formula-val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-2
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")
