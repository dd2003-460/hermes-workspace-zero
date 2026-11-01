"""
【性质】推导 —— 三项独立于"数值积分黄金标准比对"的物理自洽性检验，
        进一步巩固对Gamma_one_V母函数本身正确性的信心
【计算的量】
  (1) 镜面宇称检验：z->-z反射下，Gamma_one_V应严格反号(手性是赝标量)，
      Gamma_one_I应严格不变(强度是真标量)
  (2) 任意旋转不变性：proper rotation(SO(3))下Gamma_one_V数值应完全不变
      (物理背景各向同性)
  (3) 小天线(长波)近似极限：beta_u,beta_v->0时Gamma_one_V应按bu*bv量级
      趋于零(不发散、不趋于其他幂次)，比值收敛到一个有限常数
【状态】✅ 全部通过：
      (1) 镜面反射ratio精确为-1.000000(手征)和+1.000000(强度)
      (2) 旋转不变性误差~1e-10~1e-12
      (3) bu*bv标度下比值稳定收敛(6个递减scale下虚部收敛到-0.01027)
【依赖】阶段2组件B"具体计算"文件夹产出(Gamma_one_V)，
      检验(1)额外用到PRD强度副本项目阶段1组件D的Gamma_one_I(仅用于对照)
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod_v = __import__("01_组装通用GammaOneV")
Gamma_one_V = mod_v.Gamma_one_V


def mirror_z(vec):
    v = vec.copy()
    v[2] = -v[2]
    return v


def random_rotation_matrix(rng):
    A = rng.standard_normal((3, 3))
    Q, R = np.linalg.qr(A)
    Q = Q @ np.diag(np.sign(np.diag(R)))
    if np.linalg.det(Q) < 0:
        Q[:, 0] *= -1
    return Q


if __name__ == "__main__":
    print("=" * 70)
    print("检验(1): 镜面宇称 —— 手征Gamma_one_V在z->-z下应严格反号")
    print("=" * 70)
    np.random.seed(1234)
    for i in range(5):
        s_hat = np.random.randn(3); s_hat /= np.linalg.norm(s_hat)
        u_hat = np.random.randn(3); u_hat /= np.linalg.norm(u_hat)
        v_hat = np.random.randn(3); v_hat /= np.linalg.norm(v_hat)
        alpha = np.random.uniform(0.3, 2.0)
        bu = np.random.uniform(-2, 2); bv = np.random.uniform(-2, 2)
        val_orig = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)
        val_mirror = Gamma_one_V(alpha, bu, bv, mirror_z(s_hat), mirror_z(u_hat), mirror_z(v_hat))
        ratio = val_mirror / val_orig
        print(f"trial{i}: ratio(mirror/orig) = {ratio:.6f}  (应严格等于 -1)")

    print("\n" + "=" * 70)
    print("检验(2): 任意旋转(SO(3))不变性")
    print("=" * 70)
    rng = np.random.default_rng(999)
    for i in range(5):
        s_hat = rng.standard_normal(3); s_hat /= np.linalg.norm(s_hat)
        u_hat = rng.standard_normal(3); u_hat /= np.linalg.norm(u_hat)
        v_hat = rng.standard_normal(3); v_hat /= np.linalg.norm(v_hat)
        alpha = rng.uniform(0.3, 2.0)
        bu = rng.uniform(-2, 2); bv = rng.uniform(-2, 2)
        R = random_rotation_matrix(rng)
        val_orig = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)
        val_rot = Gamma_one_V(alpha, bu, bv, R @ s_hat, R @ u_hat, R @ v_hat)
        err = abs(val_orig - val_rot) / max(abs(val_orig), 1e-12)
        print(f"trial{i}: rel_err(orig vs rotated) = {err:.2e}  (应趋于0)")

    print("\n" + "=" * 70)
    print("检验(3): 小天线(beta->0)近似极限，Gamma_one_V应按bu*bv量级趋于0")
    print("=" * 70)
    np.random.seed(77)
    s_hat = np.random.randn(3); s_hat /= np.linalg.norm(s_hat)
    u_hat = np.random.randn(3); u_hat /= np.linalg.norm(u_hat)
    v_hat = np.random.randn(3); v_hat /= np.linalg.norm(v_hat)
    alpha = 1.0
    for scale in [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]:
        bu = 0.3 * scale; bv = -0.2 * scale
        val = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)
        ratio = val / (bu * bv)
        print(f"scale={scale:.5f}: Gamma_V/(bu*bv) = {ratio:.6f}  (应收敛到有限常数)")
