#!/usr/bin/env python3
"""
实验：chimera 时间涨落 vs 梯度锁相稳定性

D4-S18-r22 提出的区分标准 #1

真正 chimera 的特征：
- 局部同步区在时间上会涨落/交换
- 没有完全冻结的空间结构

梯度锁相的特征：
- 空间结构相对稳定（锁在频率梯度上）

设计：在长时间模拟中比较空间相关性衰减。
"""

import numpy as np
import json


def simulate_windowed_chimera_score(theta, N, window=50, T_sim=10000, dt=0.02):
    """
    返回时间序列：每个窗口的局部 chimera_score
    """
    n_windows = T_sim // window
    scores = np.zeros(n_windows)

    for w in range(n_windows):
        local_scores = []
        for j in range(0, N, window):
            end = min(j + window, N)
            sector_sync = abs(np.mean(np.exp(1j * theta[j:end])))
            local_scores.append(sector_sync)

        scores[w] = max(local_scores) - min(local_scores)

    return scores


def spatial_correlation_decay(phases_before, phases_after, N):
    """计算两个时刻相位分布的空间相关性"""
    # 在空间上对齐比较
    corr = 0
    for i in range(N):
        corr += np.cos(phases_before[i] - phases_after[i])
    return corr / N


def run_chimera_time_analysis(N=500, T=20000, dt=0.02, seed=42):
    """比较两种设置的 chimera 时间行为"""
    configs = [
        {
            "name": "pure_chimera",  # omega1=0, epsilon>0
            "K0": 1.0, "eps": 0.5, "omega1": 0.0
        },
        {
            "name": "gradient_locking",  # omega1>0, eps>0
            "K0": 1.0, "eps": 0.5, "omega1": 0.5
        },
    ]

    results = {}

    for config in configs:
        print(f"Simulating: {config['name']} (T={T})...")
        rng = np.random.RandomState(seed)
        theta = rng.uniform(0, 2*np.pi, N)
        pos = np.linspace(0, 1, N, endpoint=False)

        k_spatial = config["K0"] * (1 + config["eps"] * np.cos(2 * np.pi * pos))
        omega = config["omega1"] * np.cos(pos) if config["omega1"] > 0 else np.zeros(N)

        # 时间序列采样
        n_snapshots = 50
        snapshot_interval = T // n_snapshots
        phases_snapshots = []
        scores_before_trans = []

        # Transient burn-in
        for t in range(2000):
            coupling = np.zeros(N)
            for i in range(N):
                j_left = (i - 1) % N
                j_right = (i + 1) % N
                coupling[i] += k_spatial[i] * (np.sin(theta[j_left] - theta[i]) +
                                               np.sin(theta[j_right] - theta[i]))
            theta += dt * (omega + coupling)
            theta = theta % (2 * np.pi)

        # Record post-transient
        phases_snapshots.append(theta.copy())
        chimera_before = max(phases) - min(phases) if False else abs(np.mean(np.exp(1j * theta)))

        for t in range(2000, T, snapshot_interval):
            coupling = np.zeros(N)
            for i in range(N):
                j_left = (i - 1) % N
                j_right = (i + 1) % N
                coupling[i] += k_spatial[i] * (np.sin(theta[j_left] - theta[i]) +
                                               np.sin(theta[j_right] - theta[i]))
            theta += dt * (omega + coupling)
            theta = theta % (2 * np.pi)

            if t >= 2000:
                phases_snapshots.append(theta.copy())

        # Analysis
        # 1. Time series of local chimera scores
        window_size = max(N // 20, 25)
        time_scores = simulate_windowed_chimera_score(
            phases_snapshots[-1], N, window=window_size, T_sim=T
        )

        # 2. Spatial correlation between consecutive snapshots
        correlations = []
        for i in range(len(phases_snapshots) - 1):
            corr = spatial_correlation_decay(
                phases_snapshots[i], phases_snapshots[i+1], N
            )
            correlations.append(corr)

        # 3. Size variance of coherent regions over time
        n_time_samples = min(20, len(phases_snapshots))
        region_sizes = []
        for i in range(0, len(phases_snapshots), max(1, len(phases_snapshots)//n_time_samples)):
            p = phases_snapshots[i]
            # Simple binary split: 0 to pi vs pi to 2pi
            sizes = [np.sum(p < np.pi), np.sum(p >= np.pi)]
            region_sizes.append(sizes)

        size_var_time = float(np.var([s[0] - s[1] for s in region_sizes])) if region_sizes else 0
        avg_region_var = float(np.mean([abs(s[0] - s[1]) / N for s in region_sizes])) if region_sizes else 0

        # Time score statistics
        score_stability = float(np.std(time_scores)) if len(time_scores) > 1 else 0

        result = {
            "name": config["name"],
            "global_coherence": float(abs(np.mean(np.exp(1j * phases_snapshots[-1])))),
            "score_stability": score_stability,  # Lower = more stable
            "spatial_corr_std": float(np.std(correlations)) if correlations else 0,
            "spatial_corr_mean": float(np.mean(correlations)) if correlations else 0,
            "size_var_over_time": size_var_time,
            "avg_region_variance": avg_region_var,
        }

        results[config["name"]] = result

        print(f"  Global coherence: {result['global_coherence']:.3f}")
        print(f"  Score stability (std): {result['score_stability']:.4f}")
        print(f"  Spatial corr (mean, std): {result['spatial_corr_mean']:.4f}, {result['spatial_corr_std']:.4f}")
        print(f"  Size variance over time: {result['size_var_over_time']:.1f}")
        print()

    output_path = "labs/simulations/chimera_temporal_analysis_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    run_chimera_time_analysis(N=500, T=15000, dt=0.02)
