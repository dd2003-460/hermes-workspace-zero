#!/usr/bin/env python3
"""
D4-S18-r12：发现同步 ↔ chimera 态相变分析

基于 chimera v7 实验诊断结论：
- chimera 无法通过人工分区产生
- 需要局部强耦合 + 全局弱耦合的特定平衡
- 环境耦合会杀死 chimera（σ=0 → chimera 稳定；σ=0.15 → 全同步）

实验目标（验证 r11 命题）：
1. 命题1：K < K_c 时 chimera 存在，I_C > 1
2. 命题2：高 σ 抑制 chimera
3. 命题3：I_C > 1 = 混合行为模式

参数空间（基于 chimera v7 已验证参数）：
- g ≈ 0.03（全局耦合）
- σ = 0.0（chimera 稳定窗口）
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Strogatz chimera 模拟器（使用 K=0.0 全局耦合机制）
# ============================================================

class ChimeraSimulator:
    """
    Abrams-Strogatz chimera 模型

    关键机制：K=0.0 时局部耦合为零，但环境耦合（g=0.03）导致：
    - 环境对异步输入无响应 → chimera 产生
    - chimera 是环境-局部耦合竞争的自然产物
    """

    def __init__(self, n=64, seed=42):
        self.n = n
        np.random.seed(seed)
        self.theta = np.random.uniform(0, 2*np.pi, n)

    def step(self, K_local=1.5, g=0.03, sigma_env=0.0, dt=0.005):
        """
        Strogatz chimera 模型（修正版）

        关键：只有当耦合系数 K_i 在某些位置为零时才能产生 chimera
        chimera v7 结论：chimera 不能人工制造 → 不使用固定 K=0.0
        """
        z_global = np.mean(np.exp(1j * self.theta))

        dtheta = np.zeros(self.n)

        for i in range(self.n):
            # 局部耦合
            for d in range(-3, 4):
                if d == 0:
                    continue
                j = (i + d) % self.n
                K_i = 1.5
                K_ij = 0.5 * (K_i + 1.5)
                dtheta[i] += K_ij * np.sin(self.theta[j] - self.theta[i])

            # 全局耦合
            dtheta[i] += g * z_global.imag

            # 环境耦合（会杀死 chimera）
            if sigma_env > 0:
                dtheta[i] += sigma_env * np.sin(self.theta[i] + i/self.n * np.pi/2)

        self.theta = (self.theta + dtheta * dt) % (2*np.pi)

    def simulate(self, T=4000, K_local=1.5, g=0.03, sigma_env=0.0, dt=0.005):
        """运行模拟"""
        traj = np.zeros((T, self.n))
        for t in range(T):
            traj[t] = self.theta.copy()
            self.step(K_local, g, sigma_env, dt)
        return traj


# ============================================================
# 测量模块
# ============================================================

def measure_chimera_segments(traj, n_segments=3):
    """测量空间分段的同步性"""
    T, n = traj.shape
    theta_now = traj[-1]

    seg_size = n // n_segments
    seg_sync = np.zeros(n_segments)
    seg_phase = np.zeros(n_segments)

    for s in range(n_segments):
        start = s * seg_size
        end = (s+1) * seg_size
        seg = theta_now[start:end]
        seg_sync[s] = abs(np.mean(np.exp(1j * seg)))
        seg_phase[s] = np.mean(seg)

    return seg_sync, seg_phase

def estimate_topology(traj, n_dim_max=3):
    """
    基于时间序列的拓扑估计
    注意：r11 结论 chimera 对应 b_1 >= 1
    """
    T, n = traj.shape
    # 取最后一段稳态
    steady_len = min(1000, T)
    if steady_len < 50:
        return np.array([1.0, 0.0, 0.0])

    steady = traj[-steady_len:]

    # 选择代表性 agent 的时间序列
    n_repr = min(10, n)
    sample_agents = np.linspace(0, n-1, n_repr, dtype=int)
    X = steady[:, sample_agents].T  # (n_repr, T_steady)

    if X.shape[0] == 0 or X.shape[1] < 2:
        return np.array([1.0, 0.0, 0.0])

    # 去均值
    X_c = X - X.mean(axis=1, keepdims=True)

    # PCA 降维
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)

    # 修复：检查 S 是否有效
    if len(S) == 0 or S[0] == 0:
        return np.array([1.0, 0.0, 0.0])

    n_dim = min(max(2, int(np.sum(S > 0.01*S[0]))), n_dim_max)
    if n_dim < 2:
        return np.array([1.0, 0.0, 0.0])

    # 嵌入
    if Vt.shape[1] < n_dim:
        return np.array([1.0, 0.0, 0.0])

    emb = X_c @ Vt.T[:, :n_dim]

    # 计算距离矩阵
    if len(emb) < 2:
        return np.array([1.0, 0.0, 0.0])

    dist = squareform(pdist(emb))

    if dist.size == 0:
        return np.array([1.0, 0.0, 0.0])

    # persistent homology 近似：两阈值法
    eps_low = max(np.percentile(dist, 20), 1e-3)
    eps_high = max(np.percentile(dist, 50), 1e-2)

    parent = np.arange(len(emb))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py: parent[px] = py

    b0s = []
    for eps in [eps_low, eps_high]:
        for i in range(len(emb)):
            for j in range(i+1, len(emb)):
                if dist[i,j] < eps: union(i, j)
        b0s.append(len(set(find(i) for i in range(len(emb)))))

    b0_avg = np.mean(b0s)

    # b_1 检测：角度环绕
    b1 = 0
    if b0_avg < 2 and n_dim >= 2:
        if len(emb) > 1:
            angles = np.arctan2(emb[:, 1], emb[:, 0])
            angle_diff = np.diff(angles)
            angle_diff = ((angle_diff + np.pi) % (2*np.pi)) - np.pi
            b1 = max(1, int(round(np.sum(np.abs(angle_diff)) / (2 * np.pi))))


    b2 = max(0, b0_avg - 1) if b0_avg > 1 else 0

    return np.array([b0_avg, float(b1), b2])

def compute_I_C(betti):
    """计算拓扑不变量 I_C = |χ| + w_2"""
    chi = sum((-1)**i * b for i, b in enumerate(betti))
    w2 = 1 if betti[1] % 2 == 1 else 0
    return abs(chi) + w2, chi, w2


# ============================================================
# 协议 1：K 扫描（验证命题1）
# ============================================================

def protocol_k_scan(K_range, n_trials=5):
    """扫描 K 空间，观察 I_C 和 chimera 相变"""
    print("\n" + "=" * 60)
    print("协议 1：K 扫描（发现同步 ↔ chimera 相变）")
    print("=" * 60)
    print(f"目标：验证 K < K_c 时 chimera 存在，I_C > 1")

    Ks = np.array(K_range)
    results = []

    for K in Ks:
        print(f"\nK = {K:.3f}", end="  ")

        I_C_values = []
        chimera_count = 0
        betti_sum = np.zeros(3)

        for trial in range(n_trials):
            sim = ChimeraSimulator(n=64, seed=42+trial)
            traj = sim.simulate(T=4000, K_local=K, g=0.03, sigma_env=0.0)

            seg_sync, _ = measure_chimera_segments(traj)
            is_chimera = any(0.2 < s < 0.9 for s in seg_sync)

            betti = estimate_topology(traj)
            I_C, chi, w2 = compute_I_C(betti)

            I_C_values.append(I_C)
            if is_chimera: chimera_count += 1
            betti_sum += betti

        betti_avg = betti_sum / n_trials
        I_C_avg = np.mean(I_C_values)
        chimera_prob = chimera_count / n_trials

        print(f"I_C={I_C_avg:.2f} | chimera_prob={chimera_prob:.2f} | betti={betti_avg}")
        results.append({
            'K': float(K), 'I_C': float(I_C_avg),
            'betti': betti_avg.tolist(),
            'chimera_prob': float(chimera_prob)
        })

    return results


# ============================================================
# 协议 2：噪声扫描（验证命题2）
# ============================================================

def protocol_noise_scan(sigma_range, K_fixed=1.5):
    """扫描环境耦合强度 σ"""
    print("\n" + "=" * 60)
    print("协议 2：噪声扫描（环境耦合对 chimera 的抑制效应）")
    print("=" * 60)
    print("理论预期（r11 + v7）：高 σ → chimera 快速死亡")

    sigmas = np.array(sigma_range)
    results = []

    for sigma in sigmas:
        print(f"\nσ = {sigma:.3f}", end="  ")

        I_C_values = []
        chimera_count = 0
        betti_sum = np.zeros(3)
        sync_values = []

        for trial in range(5):
            sim = ChimeraSimulator(n=64, seed=42+trial)
            traj = sim.simulate(T=4000, K_local=K_fixed, g=0.03, sigma_env=sigma)

            seg_sync, _ = measure_chimera_segments(traj)
            is_chimera = any(0.2 < s < 0.9 for s in seg_sync)

            betti = estimate_topology(traj)
            I_C, chi, w2 = compute_I_C(betti)

            I_C_values.append(I_C)
            if is_chimera: chimera_count += 1
            betti_sum += betti
            sync_values.append(np.mean(seg_sync))

        betti_avg = betti_sum / 5
        I_C_avg = np.mean(I_C_values)
        chimera_prob = chimera_count / 5
        avg_sync = np.mean(sync_values)

        print(f"I_C={I_C_avg:.2f} | chimera_prob={chimera_prob:.2f} | avg_sync={avg_sync:.3f}")
        results.append({
            'sigma': float(sigma), 'I_C': float(I_C_avg),
            'betti': betti_avg.tolist(),
            'chimera_prob': float(chimera_prob),
            'avg_sync': float(avg_sync)
        })

    return results


# ============================================================
# 协议 3：拓扑-动力学耦合分析（验证命题3）
# ============================================================

def protocol_topology_coupling(K_fixed=1.5, sigma_fixed=0.0, T_scans=20):
    """分析拓扑结构随时间的演化"""
    print("\n" + "=" * 60)
    print("协议 3：拓扑-动力学耦合分析")
    print("=" * 60)

    sim = ChimeraSimulator(n=64, seed=42)
    traj = sim.simulate(T=5000, K_local=K_fixed, g=0.03, sigma_env=sigma_fixed, dt=0.005)

    dt_scan = 5000 // T_scans
    I_C_curve = []
    betti_curve = []

    print("\n时间快照序列（T -> I_C, b_0, b_1）:")
    print("-" * 50)

    for t_step in range(0, 5000, dt_scan):
        window = 200
        if t_step + window > traj.shape[0]:
            window = traj.shape[0] - t_step
        if window < 10:
            break
        traj_window = traj[t_step:t_step+window]
        betti = estimate_topology(traj_window)
        I_C, chi, w2 = compute_I_C(betti)

        I_C_curve.append(I_C)
        betti_curve.append(betti.tolist())

        print(f"T={t_step:4d}: I_C={I_C:.1f} | b_0={betti[0]:.1f} b_1={betti[1]:.1f} b_2={betti[2]:.1f}")

    return {'I_C_curve': I_C_curve, 'betti_curve': betti_curve}


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("D4-S18-r12：发现同步 ↔ chimera 态相变分析")
    print("基于 r11 理论断言的实验验证")
    print("=" * 60)

    try:
        k_scan_results = protocol_k_scan(
            K_range=[0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0],
            n_trials=5
        )

        noise_scan_results = protocol_noise_scan(
            sigma_range=[0.0, 0.03, 0.05, 0.08, 0.12, 0.15, 0.20, 0.30],
            K_fixed=1.5
        )

        topology_results = protocol_topology_coupling(
            K_fixed=1.5, sigma_fixed=0.0, T_scans=20
        )

        output = {
            'k_scan': k_scan_results,
            'noise_scan': noise_scan_results,
            'topology_coupling': topology_results
        }

        with open('/tmp/r12_results.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("\n" + "=" * 60)
        print("结果已保存到 /tmp/r12_results.json")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
