"""
【性质】推导 —— 验证"共面构型手征ORF严格为零"这一物理判据
【计算的量】当 s_hat, u_hat, v_hat 三矢量共面(psi=0)时 Gamma_one_V 是否为零；
        对照非共面(psi任意)时是否有非零响应
【状态】✅ 完成，5组共面构型数值噪声量级(1e-7~1e-9)，5组非共面构型明显非零
        (1e-6~1e-2量级，随机psi导致响应大小波动)
【依赖】阶段2组件B"具体计算"文件夹产出(Gamma_one_V)

物理背景：圆偏振（手征）引力波背景的探测要求参与关联的探测器/链路不能
共面——这是因为手性作为赝标量，在镜面反射下变号；若所有几何要素都在
同一平面内，绕该平面法线的镜面反射是构型的对称操作，会使得手征响应
必须等于其自身的相反数，从而恒为零。这与JCAP论文(Ju Chen, Chang Liu,
Yun-Long Zhang, 2410.18916)引言部分引用的论断("isotropic SGWB的圆偏振
分量对平面探测器不可探测，需要非共面的探测器网络")完全一致。
"""
import numpy as np
import sys
sys.path.insert(0, "../具体计算")
mod = __import__("01_组装通用GammaOneV")
Gamma_one_V = mod.Gamma_one_V

if __name__ == "__main__":
    np.random.seed(42)
    print("=== 共面构型 (s_hat, u_hat, v_hat 都在xz平面, psi=0) ===")
    for i in range(5):
        du = np.random.uniform(0.2, np.pi-0.2)
        dv = np.random.uniform(0.2, np.pi-0.2)
        s_hat = np.array([0, 0, 1.0])
        u_hat = np.array([np.sin(du), 0, np.cos(du)])
        v_hat = np.array([np.sin(dv), 0, np.cos(dv)])
        alpha = np.random.uniform(0.3, 2.0)
        bu = np.random.uniform(-2, 2); bv = np.random.uniform(-2, 2)
        val = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)
        print(f"trial{i}: du={du:.3f} dv={dv:.3f} (共面)  Gamma_one_V={val:.3e}")

    print("\n=== 非共面构型 (随机psi != 0, pi) ===")
    for i in range(5):
        du = np.random.uniform(0.2, np.pi-0.2)
        dv = np.random.uniform(0.2, np.pi-0.2)
        psi = np.random.uniform(0.3, np.pi-0.3)
        s_hat = np.array([0, 0, 1.0])
        u_hat = np.array([np.sin(du), 0, np.cos(du)])
        v_hat = np.array([np.sin(dv)*np.cos(psi), np.sin(dv)*np.sin(psi), np.cos(dv)])
        alpha = np.random.uniform(0.3, 2.0)
        bu = np.random.uniform(-2, 2); bv = np.random.uniform(-2, 2)
        val = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)
        print(f"trial{i}: du={du:.3f} dv={dv:.3f} psi={psi:.3f} (非共面)  Gamma_one_V={val:.4e}")
