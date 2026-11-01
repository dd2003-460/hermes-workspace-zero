"""
【性质】数值验证 —— 对推导/04文件构造的真实LIGO H1-L1几何构型，用独立的
        最原始定义(scipy.dblquad直接2D积分)交叉验证Gamma_one_I和Gamma_one_V
【计算的量】固定f=0.5Hz,假想臂长L=1e6km(使信号明显不为零)时的
        Gamma_one_I, Gamma_one_V公式法 vs 直接积分法
【状态】✅ 完成，两者误差~1e-11~1e-12
【依赖】阶段2组件B"具体计算"文件夹产出(Gamma_one_V)，PRD强度副本项目
        阶段1组件D产出(Gamma_one_I)，PRD副本项目阶段3组件A产出(T_one,
        polarization_tensors)
"""
import numpy as np
import sys
sys.path.insert(0, "../../../../PRD强度ORF复现_副本/阶段1_单向链路ORF核心积分/组件D_I2_I3_I4_替换导出/具体计算")
sys.path.insert(0, "../具体计算")
sys.path.insert(0, "../../../../PRD强度ORF复现_副本/阶段3_具体探测器ORF/组件A_PTA/具体计算")
mod_i = __import__("01_组装I2I3I4强度版")
mod_v = __import__("01_组装通用GammaOneV")
pta_mod = __import__("01_PTA脉冲星对ORF直接定义式数值积分")
Gamma_one_I = mod_i.Gamma_one_I
Gamma_one_V = mod_v.Gamma_one_V
T_one = pta_mod.T_one
polarization_tensors = pta_mod.polarization_tensors
from scipy import integrate


H1_vertex = np.array([-2.161414928e6, -3.834695183e6, 4.600350224e6])
H1_xarm = np.array([-0.2239, 0.7998, 0.5569])
L1_vertex = np.array([-7.427604472e4, -5.496283720e6, 3.224257018e6])
L1_xarm = np.array([-0.9546, -0.1416, -0.2622])
u_hat = H1_xarm / np.linalg.norm(H1_xarm)
v_hat = L1_xarm / np.linalg.norm(L1_xarm)
sep_vec = L1_vertex - H1_vertex
sep_dist = np.linalg.norm(sep_vec)
s_hat = sep_vec / sep_dist
c = 299792.458


def Gamma_one_I_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-8):
    def integrand_complex(theta, phi):
        n_hat = np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_u = n_hat @ u_hat; n_dot_v = n_hat @ v_hat; n_dot_s = n_hat @ s_hat
        Tu = T_one(beta_u, n_dot_u); Tv = T_one(beta_v, n_dot_v)
        ePlus_uu = u_hat @ e_plus @ u_hat; eCross_uu = u_hat @ e_cross @ u_hat
        ePlus_vv = v_hat @ e_plus @ v_hat; eCross_vv = v_hat @ e_cross @ v_hat
        RA_plus_I = 0.5*ePlus_uu*Tu; RA_cross_I = 0.5*eCross_uu*Tu
        RA_plus_J = 0.5*ePlus_vv*Tv; RA_cross_J = 0.5*eCross_vv*Tv
        return (RA_plus_I*np.conj(RA_plus_J)+RA_cross_I*np.conj(RA_cross_J))*np.sin(theta)*np.exp(-1j*alpha*n_dot_s)
    def integrand_real(phi, theta): return integrand_complex(theta, phi).real
    def integrand_imag(phi, theta): return integrand_complex(theta, phi).imag
    eps = 1e-6
    re, _ = integrate.dblquad(integrand_real, eps, np.pi-eps, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    im, _ = integrate.dblquad(integrand_imag, eps, np.pi-eps, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    return (re+1j*im) / (8*np.pi)


def Gamma_one_V_direct(alpha, beta_u, beta_v, s_hat, u_hat, v_hat, epsabs=1e-8):
    def integrand(phi, theta):
        n_hat = np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
        e_plus, e_cross = polarization_tensors(n_hat)
        n_dot_u = n_hat @ u_hat; n_dot_v = n_hat @ v_hat; n_dot_s = n_hat @ s_hat
        Tu = T_one(beta_u, n_dot_u); Tv = T_one(beta_v, n_dot_v)
        ePlus_uu = u_hat @ e_plus @ u_hat; eCross_uu = u_hat @ e_cross @ u_hat
        ePlus_vv = v_hat @ e_plus @ v_hat; eCross_vv = v_hat @ e_cross @ v_hat
        numerator_V = ePlus_uu*eCross_vv - eCross_uu*ePlus_vv
        return numerator_V * Tu * np.conj(Tv) * np.exp(-1j*alpha*n_dot_s) * np.sin(theta)
    re, _ = integrate.dblquad(lambda phi, theta: integrand(phi, theta).real, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    im, _ = integrate.dblquad(lambda phi, theta: integrand(phi, theta).imag, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=1e-7)
    return (re+1j*im) / (32*np.pi)


if __name__ == "__main__":
    f = 0.5
    L_arm = 1e6  # 假想臂长(非LIGO真实4km)，使信号明显不为零
    alpha = 2*np.pi*f*sep_dist/c
    beta = 2*np.pi*f*L_arm/c
    print(f"alpha={alpha:.4f}, beta={beta:.4f}")

    val_I_formula = Gamma_one_I(alpha, beta, beta, s_hat, u_hat, v_hat)
    val_I_direct = Gamma_one_I_direct(alpha, beta, beta, s_hat, u_hat, v_hat)
    print(f"\nGamma_one_I formula = {val_I_formula}")
    print(f"Gamma_one_I direct  = {val_I_direct}")
    print(f"rel err = {abs(val_I_formula-val_I_direct)/abs(val_I_direct):.2e}")

    val_V_formula = Gamma_one_V(alpha, beta, beta, s_hat, u_hat, v_hat)
    val_V_direct = Gamma_one_V_direct(alpha, beta, beta, s_hat, u_hat, v_hat)
    print(f"\nGamma_one_V formula = {val_V_formula}")
    print(f"Gamma_one_V direct  = {val_V_direct}")
    print(f"rel err = {abs(val_V_formula-val_V_direct)/abs(val_V_direct):.2e}")
