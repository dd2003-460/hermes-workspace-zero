"""
【性质】数值验证 —— BUG-002(sigma_pm分支选择)修复后，Gamma_one_I通用组装公式
        (任意alpha,beta_u,beta_v,含负值,任意朝向s_hat,u_hat,v_hat)的大样本验证
【计算的量】Gamma_one_I(alpha,beta_u,beta_v,s_hat,u_hat,v_hat) vs.
        最原始响应函数定义(论文Eq6/Eq24)直接2D数值积分
【状态】✅ 10组随机参数(beta_u,beta_v含正负,任意朝向)全部通过，误差~1e-11~1e-12
        （此前修复前，正是在beta_u或beta_v出现负值时触发BUG-002，导致GbLI组件
        排查Gamma_two时长期卡住——现已定位并修复根源）
【依赖】本脚本读取阶段1组件D"具体计算"文件夹产出(Gamma_one_I)，以及阶段3组件A
        "具体计算"文件夹产出(T_one, polarization_tensors，用于独立构造直接定义)
"""
import numpy as np
import sys
sys.path.insert(0, "../../../阶段1_单向链路ORF核心积分/组件D_I2_I3_I4_替换导出/具体计算")
sys.path.insert(0, "../../../阶段3_具体探测器ORF/组件A_PTA/具体计算")
mod = __import__("01_组装I2I3I4强度版")
pta_mod = __import__("01_PTA脉冲星对ORF直接定义式数值积分")
Gamma_one_I = mod.Gamma_one_I
T_one = pta_mod.T_one
polarization_tensors = pta_mod.polarization_tensors
from scipy import integrate


def Gamma_one_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-8):
    """最原始定义 (论文Eq6+Eq24): Gamma_one = (1/8pi) int R_I^A * conj(R_J^A)"""
    def integrand_complex(theta, phi):
        n_hat = np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_u = n_hat @ u_hat; n_dot_v = n_hat @ v_hat; n_dot_s = n_hat @ s_hat
        Tu = T_one(beta_u, n_dot_u); Tv = T_one(beta_v, n_dot_v)
        ePlus_uu = u_hat @ e_plus @ u_hat; eCross_uu = u_hat @ e_cross @ u_hat
        ePlus_vv = v_hat @ e_plus @ v_hat; eCross_vv = v_hat @ e_cross @ v_hat
        RA_plus_I = 0.5*ePlus_uu*Tu; RA_cross_I = 0.5*eCross_uu*Tu
        RA_plus_J = 0.5*ePlus_vv*Tv; RA_cross_J = 0.5*eCross_vv*Tv
        return (RA_plus_I*np.conj(RA_plus_J) + RA_cross_I*np.conj(RA_cross_J)) * np.sin(theta) * np.exp(-1j*alpha*n_dot_s)

    def integrand_real(phi, theta): return integrand_complex(theta, phi).real
    def integrand_imag(phi, theta): return integrand_complex(theta, phi).imag
    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi-eps, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi-eps, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    return (re + 1j*im) / (8*np.pi)


if __name__ == "__main__":
    np.random.seed(31337)
    N = 10
    n_fail = 0
    print(f"测试 Gamma_one_I (BUG-002修复后) vs 最原始定义, {N}组随机参数 (beta_u,beta_v含正负):")
    for i in range(N):
        s_hat_r = np.random.randn(3); s_hat_r /= np.linalg.norm(s_hat_r)
        u_hat_r = np.random.randn(3); u_hat_r /= np.linalg.norm(u_hat_r)
        v_hat_r = np.random.randn(3); v_hat_r /= np.linalg.norm(v_hat_r)
        alpha_r = np.random.uniform(0.1, 2.0)
        bu = np.random.uniform(-3, 3)
        bv = np.random.uniform(-3, 3)
        val_formula = Gamma_one_I(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        val_direct = Gamma_one_direct(alpha_r, bu, bv, s_hat_r, u_hat_r, v_hat_r)
        err = abs(val_formula-val_direct) / max(abs(val_direct), 1e-10)
        fail = err > 1e-3
        n_fail += fail
        print(f"trial{i}: alpha={alpha_r:.2f} bu={bu:+.2f} bv={bv:+.2f}  err={err:.2e} {'FAIL' if fail else 'ok'}")
    print(f"\n{n_fail}/{N} 失败")
