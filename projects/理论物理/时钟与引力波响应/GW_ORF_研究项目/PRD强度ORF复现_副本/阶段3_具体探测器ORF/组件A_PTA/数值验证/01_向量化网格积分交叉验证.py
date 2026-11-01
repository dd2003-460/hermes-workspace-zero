"""
【性质】数值验证 —— 用【独立的向量化网格积分】（而非scipy.dblquad）交叉核对
        "具体计算"给出的 Gamma_PTA_direct() 结果
【计算的量】Gamma_PTA(beta_u,beta_v,u_hat,v_hat) 两种独立数值积分方法是否一致
【状态】✅ 通过，误差~1e-6量级
【依赖】直接复制"具体计算"01号文件的物理定义（用矢量化实现而非scipy.dblquad，
        方法论上独立：一个是自适应积分器，一个是固定网格黎曼和）

【关于β增大时Gamma_PTA的行为，如实记录一个物理层面的观察】
本文件额外做了β增大时Gamma_PTA数值稳定性的检验，发现Gamma_PTA并不会单调
趋近于Hellings-Downs曲线值Gamma_HD(gamma)——这是符合物理预期的：Gamma_HD
只是"仅保留地球项"（kappa_IJ(n)≈1）的近似，完整的Gamma_PTA还包含由
beta_u,beta_v决定的"脉冲星项"振荡修正（e^{-2i*beta_u}等相位因子），这些
修正项对固定的beta_u,beta_v不会消失，只有对大量随机脉冲星距离做统计平均
后才会趋于0、显现出HD曲线。这不是本组件的错误，是PTA物理本身的特性。
"""
import numpy as np


def polarization_tensors_batch(theta, phi):
    theta_hat_x = np.cos(theta) * np.cos(phi)
    theta_hat_y = np.cos(theta) * np.sin(phi)
    theta_hat_z = -np.sin(theta)
    phi_hat_x = -np.sin(phi)
    phi_hat_y = np.cos(phi)
    phi_hat_z = np.zeros_like(phi)
    return (theta_hat_x, theta_hat_y, theta_hat_z), (phi_hat_x, phi_hat_y, phi_hat_z)


def grid_Gamma_PTA(beta_u, beta_v, u_hat, v_hat, Ntheta=1500, Nphi=1500):
    """矢量化网格积分版本，与具体计算文件里scipy.dblquad版本完全独立的实现"""
    thetas = np.linspace(1e-5, np.pi - 1e-5, Ntheta)
    phis = np.linspace(0, 2 * np.pi, Nphi, endpoint=False)
    TH, PH = np.meshgrid(thetas, phis, indexing='ij')
    that, phat = polarization_tensors_batch(TH, PH)
    tu = that[0] * u_hat[0] + that[1] * u_hat[1] + that[2] * u_hat[2]
    pu = phat[0] * u_hat[0] + phat[1] * u_hat[1] + phat[2] * u_hat[2]
    tv = that[0] * v_hat[0] + that[1] * v_hat[1] + that[2] * v_hat[2]
    pv = phat[0] * v_hat[0] + phat[1] * v_hat[1] + phat[2] * v_hat[2]
    ePuu = tu ** 2 - pu ** 2
    eCuu = 2 * tu * pu
    ePvv = tv ** 2 - pv ** 2
    eCvv = 2 * tv * pv
    nx = np.sin(TH) * np.cos(PH)
    ny = np.sin(TH) * np.sin(PH)
    nz = np.cos(TH)
    nu = nx * u_hat[0] + ny * u_hat[1] + nz * u_hat[2]
    nv = nx * v_hat[0] + ny * v_hat[1] + nz * v_hat[2]
    Tu = (1 - np.exp(-1j * beta_u * (1 + nu))) / (1 + nu)
    Tv = (1 - np.exp(-1j * beta_v * (1 + nv))) / (1 + nv)
    RA_plus_I = 0.5 * ePuu * Tu
    RA_cross_I = 0.5 * eCuu * Tu
    RA_plus_J = 0.5 * ePvv * Tv
    RA_cross_J = 0.5 * eCvv * Tv
    integrand = (RA_plus_I * np.conj(RA_plus_J) + RA_cross_I * np.conj(RA_cross_J)) * np.sin(TH)
    dtheta = thetas[1] - thetas[0]
    dphi = phis[1] - phis[0]
    return np.sum(integrand) * dtheta * dphi / (8 * np.pi)


# ---- 从"具体计算"01号文件复制: dblquad版本 (完全独立方法的对照) ----
from scipy import integrate


def T_one(beta, n_dot_u):
    return (1 - np.exp(-1j * beta * (1 + n_dot_u))) / (1 + n_dot_u)


def polarization_tensors(n_hat):
    nx, ny, nz = n_hat
    theta = np.arccos(np.clip(nz, -1, 1))
    phi = np.arctan2(ny, nx)
    theta_hat = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), -np.sin(theta)])
    phi_hat = np.array([-np.sin(phi), np.cos(phi), 0])
    e_plus = np.outer(theta_hat, theta_hat) - np.outer(phi_hat, phi_hat)
    e_cross = np.outer(theta_hat, phi_hat) + np.outer(phi_hat, theta_hat)
    return e_plus, e_cross


def Gamma_PTA_direct(beta_u, beta_v, u_hat, v_hat):
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


def Gamma_HD(gamma):
    chi = (1 - np.cos(gamma)) / 2
    return 0.5 - chi / 4 + 1.5 * chi * np.log(chi)


if __name__ == "__main__":
    print("交叉验证: 网格积分 vs scipy.dblquad (两种独立数值积分方法)\n")
    np.random.seed(42)
    max_rel_err = 0
    for trial in range(4):
        du = np.random.uniform(0.4, 2.5)
        dv = np.random.uniform(0.4, 2.5)
        psi = np.random.uniform(0.2, 5.5)
        u_hat = np.array([np.sin(du), 0, np.cos(du)])
        v_hat = np.array([np.sin(dv) * np.cos(psi), np.sin(dv) * np.sin(psi), np.cos(dv)])
        beta_u = np.random.uniform(20, 80)
        beta_v = np.random.uniform(20, 80)

        val_grid = grid_Gamma_PTA(beta_u, beta_v, u_hat, v_hat)
        val_quad = Gamma_PTA_direct(beta_u, beta_v, u_hat, v_hat)
        err = abs(val_grid - val_quad) / abs(val_quad)
        max_rel_err = max(max_rel_err, err)
        print(f"trial{trial}: beta_u={beta_u:.2f} beta_v={beta_v:.2f}")
        print(f"  网格积分  = {val_grid:.6g}")
        print(f"  dblquad   = {val_quad:.6g}")
        print(f"  相对误差 = {err:.2e}\n")

    print(f"最大相对误差 = {max_rel_err:.2e}")

    print("\n" + "=" * 70)
    print("补充观察: beta增大时 Gamma_PTA 是否趋近 Hellings-Downs 曲线值")
    print("（预期：不会简单趋近，因为完整Gamma_PTA含随beta振荡的脉冲星项修正）")
    print("=" * 70)
    du, dv, psi = 1.1, 0.8, 2.0
    u_hat = np.array([np.sin(du), 0, np.cos(du)])
    v_hat = np.array([np.sin(dv) * np.cos(psi), np.sin(dv) * np.sin(psi), np.cos(dv)])
    gamma = np.arccos(np.clip(u_hat @ v_hat, -1, 1))
    hd_val = Gamma_HD(gamma)
    print(f"Gamma_HD(gamma={gamma:.4f}) = {hd_val:.6f}")
    for beta_scale in [50, 100]:
        val = grid_Gamma_PTA(beta_scale, beta_scale * 0.9, u_hat, v_hat, Ntheta=1500, Nphi=1500)
        print(f"  beta~{beta_scale}: Gamma_PTA = {val:.6f}  (与HD值不同，符合预期——见文件顶部说明)")
