"""
【性质】推导 —— 独立验证论文正文（Eq13下方）声称的物理不变性
【计算的量】I1(alpha,delta_u,delta_v,gamma) 是否与 v_y 的正负号无关
        (即 v_hat -> mirror(v_hat) 关于x-z平面反射后，I1是否不变)
【状态】✅ 完成，5组随机参数误差~1e-15~1e-16（机器精度），完全证实论文声称
【依赖】无（自包含，scipy.dblquad原始定义直接积分，不涉及任何留数/sigma公式）

用最原始定义(scipy.dblquad高精度数值积分，不经过任何留数/sigma公式)独立验证这个论文声称，
如果这个不变性成立，就可以反过来用它作为"黄金判据"检验sigma_pm的哪种分支选择是对的
（这也是BUG-002修复方案的关键正确性保证：chirality_sign的引入只是让R1,R2,R3,R4各自
内部的角色分配正确，四者相加后的总和I1必然还是同一个值，不会因为引入这个修正而破坏
论文本身声称的这条物理不变性）。
"""
import numpy as np
from scipy import integrate

def I1_direct_dblquad(alpha, u_hat, v_hat, epsabs=1e-9):
    ux,uy,uz = u_hat; vx,vy,vz = v_hat
    def integrand(phi, theta):
        x = np.cos(theta); s = np.sin(theta)
        cosphi, sinphi = np.cos(phi), np.sin(phi)
        theta_dot_u = ux*x*cosphi + uy*x*sinphi - uz*s
        phi_dot_u = -ux*sinphi + uy*cosphi
        theta_dot_v = vx*x*cosphi + vy*x*sinphi - vz*s
        phi_dot_v = -vx*sinphi + vy*cosphi
        n_dot_u = ux*s*cosphi+uy*s*sinphi+uz*x
        n_dot_v = vx*s*cosphi+vy*s*sinphi+vz*x
        ePlus_uu = theta_dot_u**2-phi_dot_u**2
        eCross_uu = 2*theta_dot_u*phi_dot_u
        ePlus_vv = theta_dot_v**2-phi_dot_v**2
        eCross_vv = 2*theta_dot_v*phi_dot_v
        numerator_I = ePlus_uu*ePlus_vv+eCross_uu*eCross_vv
        denom = (1+n_dot_u)*(1+n_dot_v)
        n_dot_s = x
        return numerator_I/denom * np.exp(-1j*alpha*n_dot_s) * s
    re,e1 = integrate.dblquad(lambda phi,theta: integrand(phi,theta).real, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    im,e2 = integrate.dblquad(lambda phi,theta: integrand(phi,theta).imag, 0, np.pi, 0, 2*np.pi, epsabs=epsabs, epsrel=epsabs)
    return re+1j*im

np.random.seed(2025)
print("检验 I1(v_y) == I1(-v_y) (5组随机参数, 高精度 epsabs=1e-9):")
max_diff = 0
for i in range(5):
    du_r = np.random.uniform(0.2, np.pi-0.2)
    u_hat = np.array([np.sin(du_r),0,np.cos(du_r)])
    dv_r = np.random.uniform(0.2, np.pi-0.2)
    psi_r = np.random.uniform(0.2, np.pi-0.2)  # ensures v_y != 0 clearly
    v_hat_pos = np.array([np.sin(dv_r)*np.cos(psi_r), np.sin(dv_r)*np.sin(psi_r), np.cos(dv_r)])
    v_hat_neg = np.array([np.sin(dv_r)*np.cos(psi_r), -np.sin(dv_r)*np.sin(psi_r), np.cos(dv_r)])
    alpha = np.random.uniform(0.3,2.5)
    val_pos = I1_direct_dblquad(alpha, u_hat, v_hat_pos)
    val_neg = I1_direct_dblquad(alpha, u_hat, v_hat_neg)
    diff = abs(val_pos-val_neg)
    max_diff = max(max_diff, diff)
    print(f"trial{i}: alpha={alpha:.3f} du={du_r:.3f} dv={dv_r:.3f} v_y=+{np.sin(dv_r)*np.sin(psi_r):.3f}")
    print(f"   I1(v_y>0)={val_pos}")
    print(f"   I1(v_y<0)={val_neg}")
    print(f"   |diff|={diff:.2e}")
print(f"\n最大差异: {max_diff:.2e}  (应接近0，验证论文正文声称的不变性)")
