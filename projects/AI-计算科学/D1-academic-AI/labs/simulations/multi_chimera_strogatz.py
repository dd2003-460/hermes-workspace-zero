#!/usr/bin/env python3
"""
多 chimera 共存实验 - Abrams-Strogatz 架构 (v6)

核心修正：
- chimera 不能通过人为分区产生
- 需要局部强耦合 + 全局弱耦合 + K 梯度
- 多 chimera 通过环境自由度（耦合系数调制）实现
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
import sys

# ============================================================
# Abrams-Strogatz Chimera 模型
# ============================================================

class StrogatzChimeraSimulator:
    """
    Abrams-Strogatz (2004) chimera 模型
    dθ_i/dt = ω_i + K_local·sin(θ_i-k - θ_i+k) + g·sin(θ̄ - θ_i)

    Chimera 产生：局部强耦合 + 全局弱耦合 + 相位记忆
    """

    def __init__(self, n=128, K_grad_strength=0.3):
        """
        创建环形 chimera 模型。

        K_grad_strength 控制耦合强度的空间变化：
        - 0: 均匀耦合，无法产生 chimera
        - 适中: 空间非均匀，但区域不显著
        - 高: 可能导致多 chimera 模式
        """
        self.n = n
        self.K_grad = K_grad_strength
        self.theta = np.random.uniform(0, 2*np.pi, n)
        self.omega = np.zeros(n)  # 固定频率，可选噪声

    def get_local_coupling(self, i, window=5):
        """局部耦合系数——空间梯度"""
        K_center = 1.5
        # 正弦空间梯度（避免人工分区）
        return K_center * (1 + self.K_grad * np.sin(2*np.pi * i / self.n))

    def step(self, g=0.03, sigma_env=0.0, dt=0.005, env_coupling_phase=np.pi/3):
        """
        单步演化

        env_coupling_phase: 环境耦合的相位偏移
        - 不同相位 → 空间不同区域有不同耦合强度
        - 这是"环境自由度"的代理
        """
        # 全局平均相位
        z_global = np.mean(np.exp(1j * self.theta))
        global_coupling = g * z_global

        dtheta = np.zeros(self.n)

        for i in range(self.n):
            # 局部耦合
            for d in range(-3, 4):
                if d == 0:
                    continue
                j = (i + d) % self.n
                K_ij = 0.5 * (self.get_local_coupling(i) + self.get_local_coupling(j))
                dtheta[i] += K_ij * np.sin(self.theta[j] - self.theta[i])

            # 全局耦合
            dtheta[i] += g * global_coupling.imag

            # 环境耦合——通过相位偏移引入空间异质性
            if sigma_env > 0:
                dtheta[i] += sigma_env * np.sin(self.theta[i] + env_coupling_phase)

        self.theta = (self.theta + (dtheta + self.omega) * dt) % (2*np.pi)

    def simulate(self, T=5000, g=0.03, sigma_env=0.0, dt=0.005):
        """运行模拟"""
        traj = np.zeros((T, self.n))
        stats_history = []

        for t in range(T):
            traj[t] = self.theta.copy()

            # 测量 chimera 指标
            z_global = np.mean(np.exp(1j * self.theta))
            stats = {
                't': t,
                'z_global': abs(z_global),
                'theta_mean': np.mean(self.theta),
                'theta_std': np.std(self.theta),
            }
            stats_history.append(stats)

            self.step(g, sigma_env, dt)

        return traj, stats_history


def sliding_chimera_region(traj, t_idx, window=20):
    """
    使用滑动窗口检测 chimera 空间结构

    chimera 定义：滑动窗口内序参量在 {0, 1} 之间震荡
    """
    if t_idx < window:
        return None

    theta_window = traj[t_idx-window:t_idx+1]

    # 计算每个 agent 在时间窗口内的序参量
    z_per_agent = np.zeros(len(traj[t_idx-window:t_idx+1]))
    for i, window_data in enumerate(theta_window):
        z_per_agent[i] = abs(np.mean(np.exp(1j * window_data)))

    # chimera 区域判断
    return z_per_agent

def measure_space_segments(traj, t_idx, n_segments=3):
    """
    测量空间 N 个连续段的平均同步性

    这是检测 chimera 的经典方法
    """
    T = t_idx
    theta_now = traj[T]
    n_agents = len(traj[0])

    seg_size = n_agents // n_segments
    seg_sync = np.zeros(n_segments)
    seg_phase = np.zeros(n_segments)

    for s in range(n_segments):
        start = s * seg_size
        end = start + seg_size
        seg = theta_now[start:end]
        seg_sync[s] = abs(np.mean(np.exp(1j * seg)))
        seg_phase[s] = np.mean(seg)

    return seg_sync, seg_phase

# ============================================================
# 拓扑估计
# ============================================================

def estimate_topology_simple(traj):
    """简化的拓扑估计：只关注时间序列的结构"""
    T, n = traj.shape
    start = max(0, T - 2000)
    steady = traj[start:]

    # 取几个代表性 agent 的时间序列
    n_repr = 5
    sample_agents = np.linspace(0, n-1, n_repr, dtype=int)
    X = steady[:, sample_agents].T  # (n_repr, T_steady)

    X_c = X - X.mean(axis=1, keepdims=True)

    # PCA
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    n_dim = min(max(2, int(np.sum(S > 0.001*S[0]))), 3)

    emb = X_c @ Vt.T[:, :n_dim]
    dist = squareform(pdist(emb))

    if dist.size == 0:
        return np.array([1.0, 0.0, 0.0])

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

    b1 = 0
    if b0_avg < 2 and n_dim >= 2:
        angles = np.arctan2(emb[:, 1], emb[:, 0])
        angle_diff = np.diff(angles)
        angle_diff = ((angle_diff + np.pi) % (2*np.pi)) - np.pi
        b1 = max(1, int(round(np.sum(np.abs(angle_diff)) / (2*np.pi))))

    b2 = max(0, b0_avg - 1) if b0_avg > 1 else 0

    return np.array([b0_avg, float(b1), b2])


def compute_I_C(betti):
    chi = sum((-1)**i * b for i, b in enumerate(betti))
    w2 = 1 if betti[1] % 2 == 1 else 0
    return abs(chi) + w2, chi, w2


# ============================================================
# 主实验
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("多 chimera 共存实验 - Abrams-Strogatz 架构 (v6)")
    print("=" * 70)
    print()

    configs = [
        ("基准",   128, 5000, 0.03, 0.0,  0.0,  "均匀耦合"),
        ("中梯度", 128, 5000, 0.03, 0.3,  0.0,  "空间梯度"),
        ("环境",   128, 5000, 0.03, 0.3,  0.08, "空间梯度+环境噪声"),
        ("强环境", 128, 5000, 0.03, 0.3,  0.15, "强环境噪声"),
        ("小N",     64, 5000, 0.03, 0.3,  0.10, "N=64 中耦合"),
    ]

    for name, n, T, g, K_grad, sigma_env, desc in configs:
        np.random.seed(42)
        sim = StrogatzChimeraSimulator(n, K_grad)
        traj, _ = sim.simulate(T, g, sigma_env)

        # 空间分段同步性
        seg_sync, seg_phase = measure_space_segments(traj, T-1, n_segments=3)

        # 判断 chimera 模式
        is_chimera = any(0.2 < s < 0.9 for s in seg_sync)

        # 全局序参量
        z_global = abs(np.mean(np.exp(1j * traj[-1])))

        # 拓扑估计
        betti = estimate_topology_simple(traj)
        I_C, chi, w2 = compute_I_C(betti)

        print(f"{name:6s} ({desc:15s}): I_C={I_C:.1f} | χ={chi:.0f} w2={w2}")
        print(f"           betti=[{betti[0]:.1f},{betti[1]:.1f},{betti[2]:.1f}]")
        print(f"           空间同步={seg_sync}, 全局|z|={z_global:.3f}, chimera={'✓' if is_chimera else ''}")
        print()

    print("=" * 70)
    print("理论说明：I_C ≥ 2 需要复杂拓扑结构")
    print("当前的 chimera 实验目标是在单 chimera 基础上实现多 chimera")
    print("I_C 的理论预测需要 ≥ 2 个拓扑环，这对应多 chimera 共存")
