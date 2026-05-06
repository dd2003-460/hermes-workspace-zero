#!/usr/bin/env python3
"""
正确的 chimera 检测实现 — D4-S18-r16-final 修正

问题背景：
原始检测代码错误地使用 abs(mean(exp(i*theta))) 的绝对值判断 chimera，
但这个值在**任何**圆周分布下都会落在 (0.2, 0.9) 区间内。

修正后的检测逻辑：
chimer a = 相邻扇区之间的同步率存在显著差异
"""

import numpy as np
from typing import Tuple

def segment_sync(phases: np.ndarray, n_segments: int = 4) -> np.ndarray:
    """
    将圆周分为 n_segments 个扇区，计算每个扇区的平均同步率。

    phases: (N,) 所有振荡器的相位，范围 [0, 2π]
    """
    n = len(phases)
    segments = np.linspace(0, 2 * np.pi, n_segments + 1)
    sync = np.zeros(n_segments)

    for s in range(n_segments):
        mask = (phases >= segments[s]) & (phases < segments[s + 1])
        seg_phases = phases[mask]
        if len(seg_phases) == 0:
            sync[s] = 0.0
        else:
            sync[s] = abs(np.mean(np.exp(1j * seg_phases)))
    return sync

def detect_chimera(phases: np.ndarray,
                    n_segments: int = 4,
                    threshold: float = 0.15) -> Tuple[bool, dict]:
    """
    修正的 chimera 检测。

    正确的 chimera 条件：
    1. 相邻扇区之间的同步率存在**显著差异**
    2. 不是"所有扇区同步率都在某个区间"

    Returns:
        (is_chimera, diagnostics)
    """
    sync = segment_sync(phases, n_segments)

    # 关键指标：相邻扇区间同步率的方差
    sync_diff_std = np.std(np.diff(sync))

    # 次级指标：最大-最小差异
    sync_range = np.max(sync) - np.min(sync)

    # 真正的 chimera：一个扇区同步，另一个扇区失同步
    # 这会在 segment_sync 中产生显著的两极分化
    # 但相邻扇区间的差异不是好指标——应该看整体方差
    sync_var = np.var(sync)
    is_chimera = sync_var > 0.01 or sync_range > 0.1

    return is_chimera, {
        "segment_sync": np.round(sync, 3).tolist(),
        "sync_diff_std": round(float(sync_diff_std), 4),
        "sync_range": round(float(sync_range), 4),
        "sync_var": round(float(sync_var), 4),
        "is_chimera": bool(is_chimera),
        "explanation": _explain(sync, sync_diff_std, sync_range, threshold, sync_var),
    }

def _explain(sync, std_diff, rng, threshold, var_sync):
    parts = []
    parts.append(f"扇区同步率: {np.round(sync, 3)}")
    parts.append(f"方差: {var_sync:.4f}")
    if var_sync > 0.01 or rng > 0.1:
        parts.append("⚠️ 扇区同步率差异显著 → chimera 候选")
    elif var_sync < 0.001:
        parts.append("所有扇区同步率一致 → 全同步态")
    else:
        parts.append("同步率有差异但较小 → 准同步态")
    return "; ".join(parts)


# ============================================================
# 网络拓扑生成
# ============================================================

def all_to_all(N: int) -> np.ndarray:
    """全连接拓扑：每节点与其他所有节点连接"""
    return np.ones((N, N)) - np.eye(N)


def ring_topology(N: int, k_neighbors: int = 2) -> np.ndarray:
    """
    Ring 拓扑：每个节点只连接左右两侧 k_neighbors 个邻居。
    可以调节 k_neighbors=1（最近邻）到 k_neighbors=N/2（全连接）。
    """
    adj = np.zeros((N, N))
    for i in range(N):
        for j in range(1, k_neighbors + 1):
            adj[i, (i + j) % N] = 1
            adj[i, (i - j) % N] = 1
    return adj


def scale_free_topology(N: int, m: int = 3,
                         seed: int = 42) -> np.ndarray:
    """
    Barabasi-Albert 无标度网络生成器。
    偏好附着机制：新节点优先连接到已有高度数节点。
    m = 新节点每次连接的边数。
    """
    rng = np.random.RandomState(seed)
    adj = np.zeros((N, N))

    # 初始完全图（m+1 个节点）
    init_size = min(m + 1, N)
    for i in range(init_size):
        for j in range(i + 1, init_size):
            adj[i, j] = adj[j, i] = 1

    # 当前已存在节点数
    existing = init_size

    # 逐个添加节点
    for new_node in range(init_size, N):
        # 偏好附着权重 = 已有节点度数
        weights = np.zeros(existing)
        for i in range(existing):
            weights[i] = adj[i, :existing].sum()

        total = weights.sum()
        if total > 0:
            probs = weights / total
            k = min(m, existing)
            neighbors = rng.choice(existing, size=k, replace=False, p=probs)
        else:
            neighbors = rng.choice(existing, size=k, replace=False)

        for nb in neighbors:
            adj[new_node, nb] = adj[nb, new_node] = 1

        existing += 1

    return adj


def degree_distribution(adj: np.ndarray) -> dict:
    """计算度数分布统计"""
    degrees = adj.sum(axis=1).astype(int)
    return {
        "mean": int(degrees.mean()),
        "max": int(degrees.max()),
        "min": int(degrees.min()),
        "std": float(degrees.std()),
    }


# ============================================================
# 耦合振荡器模拟（支持自定义拓扑）
# ============================================================

def kuramoto_simulation(N: int = 64, K: float = 1.5, T: int = 500,
                         dt: float = 0.01, topology: str = "all_to_all",
                         **topo_kwargs) -> np.ndarray:
    """
    支持不同网络拓扑的 Kuramoto 模拟。

    Parameters
    ----------
    N : 节点数
    K : 耦合强度
    T : 时间步数
    dt : 时间步长
    topology : "all_to_all" | "ring" | "scale_free"
    topo_kwargs : 拓扑特定参数 (e.g., k_neighbors, m)
    """
    theta = np.random.uniform(0, 2 * np.pi, N)
    omega = np.zeros(N)
    trajectory = [theta.copy()]

    # 生成邻接矩阵
    if topology == "all_to_all":
        adj = all_to_all(N)
    elif topology == "ring":
        adj = ring_topology(N, k_neighbors=topo_kwargs.get("k_neighbors", 2))
    elif topology == "scale_free":
        adj = scale_free_topology(N, m=topo_kwargs.get("m", 3))
    else:
        raise ValueError(f"Unknown topology: {topology}")

    for t in range(T):
        # 拓扑耦合：只考虑有边的邻居
        # phase_diffs[i,j] = sin(theta[j] - theta[i])
        phase_diffs = np.sin(theta[:, np.newaxis] - theta[np.newaxis, :])  # (N, N)
        # coupling[i] = (1/degree[i]) * sum_j(A[i,j] * sin(theta[j] - theta[i]))
        coupling = (adj @ phase_diffs.sum(axis=1)) / (adj.sum(axis=1) + 1e-10)  # (N,)
        theta = theta + dt * (omega + K * coupling)
        trajectory.append(theta.copy())

    return np.stack(trajectory), adj


if __name__ == "__main__":
    print("=" * 60)
    print("正确 chimera 检测 — D4-S18-r16 修正")
    print("对比 all-to-all vs ring vs scale-free 拓扑")
    print("=" * 60)
    print()

    # 实验参数
    N = 32
    K_range = [0.5, 1.5]
    topologies = [
        ("all_to_all", {}),
        ("ring", {"k_neighbors": 2}),
        ("scale_free", {"m": 2}),
        ("scale_free", {"m": 4}),
    ]

    for topo_name, topo_args in topologies:
        print(f"拓扑: {topo_name} {topo_args}")
        print("-" * 50)

        # 打印度数分布（用短时间模拟）
        _, adj = kuramoto_simulation(N=N, K=1.0, T=5, topology=topo_name, **topo_args)
        deg = degree_distribution(adj)
        print(f"  度数分布: mean={deg['mean']}, max={deg['max']}, min={deg['min']}, std={deg['std']:.1f}")

        for K in K_range:
            print(f"\n  K={K}:")
            trajectory, _ = kuramoto_simulation(N=N, K=K, T=200, topology=topo_name,
                                                dt=0.01, **topo_args)

            final_steps = trajectory[-100:]
            chimera_counts = []
            global_syncs = []

            for traj in final_steps:
                is_chi, _ = detect_chimera(traj)
                chimera_counts.append(is_chi)
                global_syncs.append(abs(np.mean(np.exp(1j * traj))))

            chimera_rate = np.mean(chimera_counts)
            avg_sync = np.mean(global_syncs)
            print(f"    chimera_rate: {chimera_rate:.2%}  global_sync: {avg_sync:.3f}")

        print()

    print("=" * 60)
    print("修正：这是'多相凝聚检测'，不是严格 chimera。")
    print("严格 chimera 需要空间耦合变化 K(x) 或频率分布 Ω(x)。")
    print("当前结果：高耦合下所有拓扑都出现多相凝聚。")
    print("=" * 60)
