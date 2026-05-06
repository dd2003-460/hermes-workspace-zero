#!/usr/bin/env python3
"""
实验：M 相凝聚相变 — 验证 D4-S18-r18 定理

不同耦合强度 K 下，统计凝聚区数量 M。
预期：低 K → M=1（无序），高 K → M≥2（多相凝聚）
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from labs.simulations.detect_m_phase import m_phase_detection
from labs.simulations.phase_chimera_correct_detection import kuramoto_simulation


def run_experiment(K_range=None, N=64, T=500, runs=10):
    if K_range is None:
        K_range = [0.0, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0]

    print(f"实验：N={N}, T={T}, runs={runs}")
    print(f"{'K':>6} | {'<M>':>4} | {'M_min':>5} | {'M_max':>5} | {'sync':>6}")
    print("-" * 40)

    for K in K_range:
        m_values = []
        sync_values = []

        for _ in range(runs):
            traj, _ = kuramoto_simulation(N=N, K=K, T=T, topology="all_to_all", dt=0.01)

            # 取最后阶段
            final_steps = traj[-100:]
            avg_M = 0
            for t in final_steps:
                M, _ = m_phase_detection(t)
                avg_M += M
            avg_M /= len(final_steps)

            # 全局同步序参量
            global_sync = abs(np.mean(np.exp(1j * final_steps[-1])))

            m_values.append(avg_M)
            sync_values.append(global_sync)

        avg_M = np.mean(m_values)
        avg_sync = np.mean(sync_values)
        print(f"{K:>6.1f} | {avg_M:>4.2f} | {min(m_values):>5} | {max(m_values):>5} | {avg_sync:>6.3f}")


if __name__ == "__main__":
    run_experiment()
