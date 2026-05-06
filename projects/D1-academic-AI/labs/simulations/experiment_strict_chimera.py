#!/usr/bin/env python3
"""
严格 chimera 重现实验 — Abrams-Strogatz (2004) 设置

关键参数（D4-S18-r19 提出的未来方向）：
  N >= 500, T_transient >= 5000, eps in [0.5, 1.0]

设置：
  K(x) = K0 * (1 + eps * cos(2*pi*x))
  omega(x) = omega0 + omega1 * cos(x)  # 频率梯度
  ring topology coupling

chimerascore = max(bin_syncs) - min(bin_syncs)
"""

import sys
import json
import numpy as np

def run_strict_chimera(
    N=500,
    K0=1.0,
    epsilons=[0.5, 0.8, 1.0],
    omega0=0.0,
    omega1=0.5,
    T_transient=5000,
    T_measure=1000,
    dt=0.02,
    runs=3,
    seed=42
):
    """
    运行严格 chimera 重现实验。

    N: 振子数（>=500）
    K0: 基础耦合强度（strict chimera range: 0.5 < K0 < 2.0）
    eps: 空间耦合变化幅度
    omega1: 频率梯度幅度
    """
    print(f"=== 严格 Chimera 重现实验 ===")
    print(f"N={N}, K0={K0}, omega0={omega0}, omega1={omega1}")
    print(f"T_transient={T_transient}, T_measure={T_measure}, dt={dt}")
    print(f"{'ε':>6} | {'score':>10} | {'sync':>8} | {'std_score':>10}")
    print("-" * 50)

    results = {}

    for eps in epsilons:
        scores_all = []
        syncs_all = []

        for r in range(runs):
            rng = np.random.RandomState(seed + r)

            # Initialize positions and phases
            pos = np.linspace(0, 1, N, endpoint=False)
            theta = rng.uniform(0, 2*np.pi, N)

            # Spatial coupling weights (ring neighbors only)
            k_spatial = K0 * (1 + eps * np.cos(2 * np.pi * pos))

            # Spatial frequency gradient
            omega = omega0 + omega1 * np.cos(pos)

            # Simulate transient + measure
            for t in range(T_transient + T_measure):
                # Ring coupling
                coupling = np.zeros(N)
                for i in range(N):
                    j_left = (i - 1) % N
                    j_right = (i + 1) % N
                    coupling[i] += k_spatial[i] * (np.sin(theta[j_left] - theta[i]) +
                                                   np.sin(theta[j_right] - theta[i]))

                # Evolution with frequency gradient
                theta += dt * (omega + coupling)
                theta = theta % (2 * np.pi)

                # Record during measurement window
                if t >= T_transient and t < T_transient + T_measure:
                    n_sectors = 16  # Higher resolution than previous 10
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
                    scores_all.append(score)

            # Global synchronization measure
            global_sync = abs(np.mean(np.exp(1j * theta)))
            syncs_all.append(global_sync)

        avg_score = np.mean(scores_all)
        avg_sync = np.mean(syncs_all)
        std_score = np.std(scores_all)

        # High chimera score (>0.3) suggests chimera state
        is_chimera = avg_score > 0.3

        print(f"{eps:.1f} | {avg_score:>10.3f} | {avg_sync:>8.3f} | {std_score:>10.3f} {'[CHIMERA] ' if is_chimera else ''}")
        results[eps] = {
            "score": avg_score,
            "sync": avg_sync,
            "std_score": std_score,
            "is_chimera": is_chimera,
            "scores": scores_all
        }

    print(f"\n=== 结论 ===")
    chimera_eps = [eps for eps, r in results.items() if r["is_chimera"]]
    if chimera_eps:
        print(f"观测到 chimera 态：eps = {chimera_eps}")
        print("解释：空间异质耦合导致局部同步/异步分区，符合 Abrams-Strogatz 定义")
    else:
        print("未观测到严格 chimera 态")
        print("可能原因：1) N 不足  2) T_transient 不够  3) K0/eps 参数不在临界区")

    # Save raw scores for analysis (numpy types need conversion)
    def numpy_encoder(obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    output_path = "labs/simulations/chimera_strict_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=numpy_encoder)
    print(f"\n原始数据已保存：{output_path}")

    return results


if __name__ == "__main__":
    run_strict_chimera()
