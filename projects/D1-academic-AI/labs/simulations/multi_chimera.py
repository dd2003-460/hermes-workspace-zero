#!/usr/bin/env python3
"""
多 chimera 共存实验 v7 - Abrams-Strogatz 架构修复版
实验目标：验证 I_C >= 2 的 chimera 条件
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform

class StrogatzChimera:
    """基于 Abrams-Strogatz  chimera 模型的模拟器"""

    def __init__(self, n=128, k_regions=3):
        self.n = n
        self.k_regions = k_regions
        # 环形排列
        self.theta = np.random.uniform(0, 2*np.pi, n)

    def local_coupling(self, i):
        """ Abrams-Strogatz 耦合系数——K^2 - p 切换规则"""
        # K_i^2 的切换规则：一段 region 高 K，另一段低 K
        region = (i * self.k_regions) // self.n
        return 1.5 if region == 0 else 0.01

    def step(self, g=0.03, sigma=0.0, dt=0.005):
        dtheta = np.zeros(self.n)

        # 全局平均相位
        z_g = np.mean(np.exp(1j * self.theta))

        for i in range(self.n):
            Ki = self.local_coupling(i)
            # 局部耦合
            for d in range(-3, 4):
                if d == 0: continue
                j = (i + d) % self.n
                Kj = self.local_coupling(j)
                dtheta[i] += (Ki + Kj)/2 * np.sin(self.theta[j] - self.theta[i])
            # 全局耦合
            dtheta[i] += g * np.mean(np.sin(self.theta - self.theta[i]))
            # 环境噪声
            if sigma > 0:
                dtheta[i] += sigma * np.sin(self.theta[i] + i/self.n * np.pi/2)

        self.theta = (self.theta + dtheta * dt) % (2*np.pi)

    def simulate(self, T=3000, g=0.03, sigma=0.0, dt=0.005):
        traj = np.zeros((T, self.n))
        for t in range(T):
            traj[t] = self.theta.copy()
            self.step(g, sigma, dt)
        return traj

def measure_chimera(traj, n_segments=3):
    """测量 chimera 模式"""
    T, n = traj.shape
    seg_sync = np.zeros(n_segments)
    seg_phase = np.zeros(n_segments)

    seg_size = n // n_segments
    for s in range(n_segments):
        start = s * seg_size
        seg = traj[-1, start:start+seg_size]
        seg_sync[s] = abs(np.mean(np.exp(1j * seg)))
        seg_phase[s] = np.mean(seg)

    return seg_sync, seg_phase

def estimate_topology(traj):
    """简单拓扑估计"""
    T, n = traj.shape
    steady = traj[T-2000:]

    n_samples = min(T-2000, 150)
    stride = max(1, (T-2000) // n_samples)
    idx = np.arange(n_samples) * stride + (T-2000 - stride*(n_samples-1))

    # Fix: idx is relative to traj, so convert to steady indices
    idx = idx - (T - 2000)
    idx = idx[idx < len(steady)]  # Clamp to steady bounds

    X = steady[idx]
    X_c = X - X.mean(axis=0)
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

if __name__ == "__main__":
    print("=== 多 chimera 共存实验 v7 ( Abrams-Strogatz) ===\n")

    configs = [
        (64,  3000, 0.03, 0.0,   0.0, "基准"),
        (64,  3000, 0.03, 0.3,   0.0, "梯度"),
        (64,  3000, 0.03, 0.3,   0.08, "噪声0.08"),
        (64,  3000, 0.03, 0.3,   0.15, "噪声0.15"),
        (128, 4000, 0.03, 0.3,   0.12, "N=128"),
    ]

    for n, T, g, K_grad, sigma, name in configs:
        np.random.seed(42)
        sim = StrogatzChimera(n=n)
        traj = sim.simulate(T, g, sigma)
        betti = estimate_topology(traj)
        I_C, chi, w2 = compute_I_C(betti)
        seg_sync, seg_phase = measure_chimera(traj)
        is_chimera = any(0.2 < s < 0.9 for s in seg_sync)

        print(f"{name:8s}: I_C={I_C:.1f} | χ={chi:.0f} w2={w2}")
        print(f"           betti=[{betti[0]:.1f},{betti[1]:.1f},{betti[2]:.1f}]")
        print(f"           空间同步={seg_sync}, chimera={'✓' if is_chimera else ''}")
        print()
