#!/usr/bin/env python3
"""
精细实验：M 相相变边界
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from labs.simulations.detect_m_phase import m_phase_detection
from labs.simulations.phase_chimera_correct_detection import kuramoto_simulation


def run_fine(K_range, N=64, T=800, runs=5):
    print(f"精细实验：N={N}, T={T}, runs={runs}")
    print(f"{'K':>6} | {'<M>':>4} | {'σ_M':>4} | {'sync':>6}")
    print("-" * 35)

    for K in K_range:
        m_values = []
        sync_values = []

        for _ in range(runs):
            traj, _ = kuramoto_simulation(N=N, K=K, T=T, topology="all_to_all", dt=0.01)
            final_steps = traj[-100:]

            avg_M = sum(m_phase_detection(t)[0] for t in final_steps) / len(final_steps)

            global_sync = abs(np.mean(np.exp(1j * final_steps[-1])))

            m_values.append(avg_M)
            sync_values.append(global_sync)

        avg_M = np.mean(m_values)
        sigma_M = np.std(m_values)
        avg_sync = np.mean(sync_values)
        print(f"{K:>6.2f} | {avg_M:>4.2f} | {sigma_M:>4.2f} | {avg_sync:>6.3f}")


if __name__ == "__main__":
    # 精细扫描过渡区
    run_fine([1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 3.0], runs=8)
