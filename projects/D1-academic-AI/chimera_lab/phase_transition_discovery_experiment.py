#!/usr/bin/env python3
"""
D4-S18-r16 Extension：有序-无序相变中的 I_C 演化分析

从 R1-R3 结果得出的关键发现：
1. chimera 检测率为 0.000（不存在混合同步态）
2. I_C 随 K 变化（R2: ΔI_C = -1.462）
3. EAI = 0 因为 chimera 始终为 0

**新理论假设**：我们观测的不是 chimera，而是
**有序-无序相变中的拓扑演化**。

新实验设计：
1. 增强 I_C 时间序列分析（更高时间分辨率）
2. 直接测量 |dI_C/dt| 而非依赖 chimera 变化
3. 寻找 I_C 极值点对应的临界参数
4. 测试噪声能否触发 I_C 相变（无需 chimera）
"""

import numpy as np
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 核心模拟器
# ============================================================

class ChimeraSimulator:
    def __init__(self, n=64, seed=42):
        self.n = n
        np.random.seed(seed)
        self.theta = np.random.uniform(0, 2*np.pi, n)

    def step(self, K=1.5, g=0.03, sigma_env=0.0, dt=0.005):
        z_global = np.mean(np.exp(1j * self.theta))
        dtheta = np.zeros(self.n)

        for i in range(self.n):
            for d in range(-3, 4):
                if d == 0:
                    continue
                j = (i + d) % self.n
                K_ij = 0.5 * (K + 1.5)
                dtheta[i] += K_ij * np.sin(self.theta[j] - self.theta[i])
            dtheta[i] += g * z_global.imag
            if sigma_env > 0:
                dtheta[i] += sigma_env * np.sin(self.theta[i] + i/self.n * np.pi/2)

        self.theta = (self.theta + dtheta * dt) % (2*np.pi)

    def simulate_fast(self, T, K=1.5, g=0.03, sigma_env=0.0, dt=0.01, save_every=10):
        """
        快速模拟 + 定时快照保存

        save_every: 每隔多少步保存一次快照（而非每一步）
        """
        snapshot_interval = max(1, T // save_every)
        snapshots = []

        for t in range(T):
            if t % snapshot_interval == 0:
                snapshots.append({
                    't': t,
                    'theta': self.theta.copy()
                })
            self.step(K, g, sigma_env, dt)

        return snapshots

    def simulate_full(self, T, K=1.5, g=0.03, sigma_env=0.0, dt=0.005):
        """完整轨迹保存（慢但完整）"""
        traj = np.zeros((T, self.n))
        for t in range(T):
            traj[t] = self.theta.copy()
            self.step(K, g, sigma_env, dt)
        return traj


# ============================================================
# 测量模块（更精确的拓扑+I_C）
# ============================================================

def estimate_topology_fast(snapshot):
    """基于单快照的空间拓扑估计（比时间序列快）"""
    theta = snapshot
    n = len(theta)

    # 生成空间坐标（圆上均匀分布）
    coords = np.column_stack([
        np.cos(2 * np.pi * np.arange(n) / n),
        np.sin(2 * np.pi * np.arange(n) / n)
    ])

    # 基于相位相似度构建距离矩阵
    exp_i = np.exp(1j * theta)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            dist_matrix[i, j] = dist_matrix[j, i] = np.abs(exp_i[i] - exp_i[j])

    # 连接阈值
    threshold = np.percentile(dist_matrix[dist_matrix > 0], 70)

    # 连通分量（b_0）
    parent = np.arange(n)
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py: parent[px] = py

    for i in range(n):
        for j in range(i+1, n):
            if dist_matrix[i, j] < threshold:
                union(i, j)

    b0 = len(set(find(i) for i in range(n)))

    # b_1: 通过空间循环检测
    angles = np.arange(n) * 2 * np.pi / n
    theta_diff = np.diff(angles)
    theta_diff = ((theta_diff + np.pi) % (2 * np.pi)) - np.pi
    b1 = max(1, int(round(np.sum(np.abs(theta_diff)) / (2 * np.pi))))

    b2 = max(0, b0 - 1) if b0 > 1 else 0

    return np.array([float(b0), float(b1), float(b2)])

def compute_I_C(betti):
    chi = sum((-1)**i * b for i, b in enumerate(betti))
    w2 = 1 if betti[1] % 2 == 1 else 0
    return abs(chi) + w2

def global_sync_order(traj_or_snapshot):
    """全局同步序参量（Riemann 模长）"""
    if isinstance(traj_or_snapshot, np.ndarray) and len(traj_or_snapshot.shape) > 1:
        theta = traj_or_snapshot[-1]  # 取最后时间步
    else:
        theta = traj_or_snapshot
    return abs(np.mean(np.exp(1j * theta)))


# ============================================================
# 增强测量指标
# ============================================================

def compute_enriched_index(snapshot, I_C_prev=None, chimera_prev=None):
    """
    增强探索指数：不依赖 chimera，直接测量 I_C 演化

    修正版三元等价性：
    探索活跃态 ≈ 高 |dI_C/dt| 且 I_C > 1
    """
    betti = estimate_topology_fast(snapshot)
    I_C = compute_I_C(betti)

    dIC_dt = 0.0
    if I_C_prev is not None:
        dIC_dt = abs(I_C - I_C_prev)

    # 修正版 EAI（不依赖 chimera）
    # EAI_new = |dI_C/dt| × (I_C - 1) × log(I_C)
    EAI_new = dIC_dt * max(0, I_C - 1) * np.log(I_C + 1e-10)

    sync = global_sync_order(snapshot)

    return {
        'I_C': I_C,
        'betti': betti.tolist(),
        'dIC_dt': dIC_dt,
        'EAI_new': EAI_new,
        'sync': sync
    }


# ============================================================
# 协议 1：I_C 动力学高精度扫描
# ============================================================

def protocol_IC_dynamics(K_range, n_trials=3, T_warmup=1000, T_measure=2000):
    """
    高精度 I_C 动力学扫描

    核心问题：I_C 如何响应 K 变化？
    - I_C(K) 的函数形式是什么？
    - 是否存在临界 K* 使得 I_C 最活跃？
    """
    print("\n" + "=" * 70)
    print("协议 1：I_C 动力学高精度扫描（增强指标）")
    print("=" * 70)

    results = []

    for K in K_range:
        print(f"\nK = {K:.3f}", end="  ", flush=True)

        I_C_list = []
        dIC_dt_list = []
        EAI_list = []
        sync_list = []
        high_EAI_count = 0
        EAI_threshold = 0.1

        for trial in range(n_trials):
            sim = ChimeraSimulator(n=64, seed=42 + trial)
            snapshots = sim.simulate_fast(T_warmup + T_measure, K=K, save_every=50)

            if len(snapshots) < 2:
                continue

            prev_I_C = None
            for snap in snapshots[T_warmup // 50:]:  # 跳过预热
                metrics = compute_enriched_index(snap['theta'], prev_I_C)

                I_C_list.append(metrics['I_C'])
                dIC_dt_list.append(metrics['dIC_dt'])
                EAI_list.append(metrics['EAI_new'])
                sync_list.append(metrics['sync'])

                if metrics['EAI_new'] > EAI_threshold:
                    high_EAI_count += 1

                prev_I_C = metrics['I_C']

        I_C_mean = np.mean(I_C_list) if I_C_list else 0
        I_C_std = np.std(I_C_list) if I_C_list else 0
        avg_dIC_dt = np.mean(dIC_dt_list) if dIC_dt_list else 0
        avg_EAI_new = np.mean(EAI_list) if EAI_list else 0
        avg_sync = np.mean(sync_list) if sync_list else 0

        print(f"I_C={I_C_mean:.3f}±{I_C_std:.3f} | avg_dIC_dt={avg_dIC_dt:.3f} | avg_EAI={avg_EAI_new:.3f} | sync={avg_sync:.3f} | high_EAI={high_EAI_count}")

        results.append({
            'K': float(K),
            'I_C_mean': float(I_C_mean),
            'I_C_std': float(I_C_std),
            'avg_dIC_dt': float(avg_dIC_dt),
            'avg_EAI_new': float(avg_EAI_new),
            'high_EAI_pct': float(high_EAI_count / max(1, len(EAI_list)) * 100),
            'avg_sync': float(avg_sync)
        })

    return results


# ============================================================
# 协议 2：噪声触发 I_C 相变
# ============================================================

def protocol_noise_IC_transition(K_fixed=1.5, sigma_range, n_trials=3):
    """
    噪声触发实验

    核心假设：噪声可以在 I_C 动力学中引入额外的活跃度，
              即使在没有 chimera 的情况下也能增强 I_C 演化。
    """
    print("\n" + "=" * 70)
    print("协议 2：噪声触发 I_C 相变（不含 chimera）")
    print("=" * 70)

    results = []

    for sigma in sigma_range:
        print(f"\nsigma = {sigma:.3f}", end="  ", flush=True)

        EAI_sum = 0
        I_C_sum = 0
        high_EAI_count = 0

        for trial in range(n_trials):
            sim = ChimeraSimulator(n=64, seed=42 + trial)
            snapshots = sim.simulate_fast(2000, K=K_fixed, sigma_env=sigma, save_every=20)

            if len(snapshots) < 2:
                continue

            prev_I_C = None
            trial_EAI = []
            for snap in snapshots:
                metrics = compute_enriched_index(snap['theta'], prev_I_C)
                trial_EAI.append(metrics['EAI_new'])
                if metrics['EAI_new'] > 0.1:
                    high_EAI_count += 1
                I_C_sum += metrics['I_C']
                prev_I_C = metrics['I_C']

            EAI_sum += np.mean(trial_EAI)

        avg_EAI = EAI_sum / n_trials
        avg_IC = I_C_sum / (n_trials * len(snapshots)) if snapshots else 0

        print(f"avg_EAI={avg_EAI:.3f} | I_C_mean={avg_IC:.3f} | high_EAI_pct={high_EAI_count/max(1,n_trials*len(snapshots))*100:.1f}%")

        results.append({
            'sigma': float(sigma),
            'avg_EAI': float(avg_EAI),
            'avg_IC': float(avg_IC),
            'high_EAI_pct': float(high_EAI_count / max(1, n_trials * len(snapshots)) * 100)
        })

    return results


# ============================================================
# 协议 3：时间演化序列分析
# ============================================================

def protocol_time_evolution(K=1.5, T=5000, n_windows=10):
    """
    长时间序列 + 窗口化 I_C 演化

    测量：I_C(t) 的时间自相关性、衰减时间尺度
    """
    print("\n" + "=" * 70)
    print("协议 3：时间演化序列分析（I_C 动力学特征）")
    print("=" * 70)

    sim = ChimeraSimulator(n=64, seed=42)
    snapshots = sim.simulate_full(T, K=K, save_every=100)

    if len(snapshots) < n_windows:
        print("警告：快照不足")
        return None

    win_size = len(snapshots) // n_windows
    I_C_series = []
    EAI_series = []

    for w in range(n_windows):
        # 窗口两端的快照
        snap_start = snapshots[w * win_size]
        snap_end = snapshots[min((w + 1) * win_size - 1, len(snapshots) - 1)]

        betti_start = estimate_topology_fast(snap_start['theta'])
        betti_end = estimate_topology_fast(snap_end['theta'])
        I_C_start = compute_I_C(betti_start)
        I_C_end = compute_I_C(betti_end)

        I_C_series.append(I_C_start)
        EAI_series.append(abs(I_C_end - I_C_start) * max(0, I_C_start - 1) * np.log(I_C_start + 1e-10))

        print(f"W={w:2d}: t={snap_start['t']:5d}-{snap_end['t']:5d} | "
              f"I_C: {I_C_start:.1f}→{I_C_end:.1f} | b0: {betti_start[0]:.1f}→{betti_end[0]:.1f}")

    I_C_corr = np.corrcoef(np.arange(len(I_C_series)), I_C_series)[0, 1] if len(I_C_series) > 2 else 0
    EAI_mean = np.mean(EAI_series) if EAI_series else 0
    EAI_max = max(EAI_series) if EAI_series else 0

    print(f"\nI_C(t) 自相关: {I_C_corr:.3f}")
    print(f"EAI 均值: {EAI_mean:.3f}, EAI 最大: {EAI_max:.3f}")

    return {'I_C_series': I_C_series, 'EAI_series': EAI_series}


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("D4-S18-r16 Extension：有序-无序相变中的 I_C 演化")
    print("新方向：基于 chimera=0 事实的修正实验")
    print("=" * 70)

    all_results = {}

    try:
        # 协议 1：I_C 动力学高精度扫描
        all_results['IC_dynamics'] = protocol_IC_dynamics(
            K_range=[0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0],
            n_trials=3
        )

        # 协议 2：噪声触发
        all_results['noise_IC'] = protocol_noise_IC_transition(
            K_fixed=1.5,
            sigma_range=[0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30],
            n_trials=3
        )

        # 协议 3：时间演化
        all_results['time_evolution'] = protocol_time_evolution(K=1.5, T=5000, n_windows=10)

        # 保存结果
        output = {
            'IC_dynamics': all_results['IC_dynamics'],
            'noise_IC': all_results['noise_IC'],
            'time_evolution_summary': {
                'IC_corr': float(all_results['time_evolution']['I_C_series'][-1] - all_results['time_evolution']['I_C_series'][0])
                if all_results['time_evolution'] else None
            }
        }

        with open('/tmp/r16_extension_results.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("\n" + "=" * 70)
        print("结果已保存到 /tmp/r16_extension_results.json")
        print("=" * 70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
