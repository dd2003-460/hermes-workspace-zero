#!/usr/bin/env python3
"""
空间异质耦合 chimera 实验 — 验证严格 chimera 存在性（长时模拟版）

 Abrams-Strogatz (2004) 设置：
 K(x) = K0 * (1 + ε·cos(2πx))  +  ring 拓扑耦合
"""

import sys
sys.path.insert(0, '.')
import numpy as np


def run_chimera_experiment(N=100, K0=1.5, epsilons=[0.0, 0.3, 0.5, 0.8, 1.0],
                           T_transient=5000, T_measure=500, dt=0.02, runs=3, seed=42):
    """
    运行空间 chimera 实验。

    T_transient: 瞬态消除（达到稳态）
    T_measure: 测量窗口长度
    runs: 重复次数
    """
    print(f"N={N}, K0={K0}, T_transient={T_transient}, T_measure={T_measure}")
    print(f"{'ε':>6} | {'chimerascore':>14} | {'sync':>8}")
    print("-" * 35)

    results = {}

    for eps in epsilons:
        scores = []
        syncs = []

        for r in range(runs):
            rng = np.random.RandomState(seed + r)
            theta = rng.uniform(0, 2*np.pi, N)
            pos = np.linspace(0, 1, N)

            # Precompute normalized spatial coupling (ring-only)
            # Only neighbors matter; spatial factor scales coupling strength
            k_spatial = K0 * (1 + eps * np.cos(2 * np.pi * pos))  # spatial coupling weights

            # Simulate transient + measure
            for t in range(T_transient + T_measure):
                coupling = np.zeros(N)
                for i in range(N):
                    for j in [i-1, i+1]:  # ring neighbors only
                        j = j % N
                        coupling[i] += k_spatial[i] * np.sin(theta[j] - theta[i])

                theta = theta + dt * coupling

                # Record during measurement window
                if t >= T_transient and t < T_transient + T_measure:
                    n_sectors = 10
                    bin_size = N // n_sectors
                    sector_syncs = []

                    for s in range(n_sectors):
                        start = s * bin_size
                        end = min((s+1) * bin_size, N)
                        sector_phases = theta[start:end]
                        sync = abs(np.mean(np.exp(1j * sector_phases)))
                        sector_syncs.append(sync)

                    sector_syncs = np.array(sector_syncs)
                    score = sector_syncs.max() - sector_syncs.min()
                    scores.append(score)

            global_sync = abs(np.mean(np.exp(1j * theta)))
            syncs.append(global_sync)

        avg_score = np.mean(scores)
        avg_sync = np.mean(syncs)
        print(f"{eps:.1f} | {avg_score:>14.3f} | {avg_sync:>8.3f}")
        results[eps] = {"score": avg_score, "sync": avg_sync}

    return results


if __name__ == "__main__":
    run_chimera_experiment()
