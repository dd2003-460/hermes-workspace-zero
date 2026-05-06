#!/usr/bin/env python3
"""
Chimera 参数扫描 — 绘制 K0 × eps 平面上的 chimera 区域

D4-S18-r19 未来方向 #2：非均匀耦合 + 方向 #3：频率梯度

范围：
  K0: [0.3, 1.5] × 0.2
  eps: [0.0, 1.0] × 0.2
"""

import sys
import json
import numpy as np

def chimera_score_for_params(K0, eps, omega1, N=200, T_trans=2000, T_meas=200, dt=0.02, seed=42):
    """计算单个参数组的 chimera 分数"""
    rng = np.random.RandomState(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    pos = np.linspace(0, 1, N, endpoint=False)

    k_spatial = K0 * (1 + eps * np.cos(2 * np.pi * pos))
    omega = omega1 * np.cos(pos) if omega1 > 0 else np.zeros(N)

    for t in range(T_trans + T_meas):
        coupling = np.zeros(N)
        for i in range(N):
            j_left = (i - 1) % N
            j_right = (i + 1) % N
            coupling[i] += k_spatial[i] * (np.sin(theta[j_left] - theta[i]) +
                                           np.sin(theta[j_right] - theta[i]))

        theta += dt * (omega + coupling)
        theta = theta % (2 * np.pi)

        if t >= T_trans and t < T_trans + T_meas:
            n_sectors = 10
            bin_size = N // n_sectors
            sector_syncs = []
            for s in range(n_sectors):
                start = s * bin_size
                end = min((s+1) * bin_size, N)
                sector_phases = theta[start:end]
                sync = abs(np.mean(np.exp(1j * sector_phases)))
                sector_syncs.append(sync)
            return max(sector_syncs) - min(sector_syncs)

    # Should not reach here
    return 0.0


def run_parameter_scan():
    K0_range = np.arange(0.3, 1.51, 0.2)
    eps_range = np.arange(0.0, 1.01, 0.2)
    omega1 = 0.5  # Frequency gradient

    print("=== Chimera 参数扫描 (K0 × eps) ===")
    print(f"K0: {K0_range[0]:.1f} - {K0_range[-1]:.1f}, eps: {eps_range[0]:.1f} - {eps_range[-1]:.1f}")
    print()

    # Header
    header = f"{'K0':>6} | "
    for eps in eps_range:
        header += f"{eps:.1f} | "
    print(header)
    print("-" * 60)

    results = {}
    for K0 in K0_range:
        row = f"{K0:>6.1f} | "
        row_data = {}
        for eps in eps_range:
            score = chimera_score_for_params(K0, eps, omega1)
            row += f"{score:>5.3f} | "
            row_data[f"eps{eps:.1f}"] = score

        results[f"K0{K0:.1f}"] = row_data
        print(row)

    # Determine chimera regions (score > 0.3 threshold from D4-S18-r20)
    print("\n=== Chimera 区域判定 (score > 0.3) ===")
    chimera_regions = []
    for K0_str, data in results.items():
        for eps_str, score in data.items():
            if score > 0.3:
                chimera_regions.append({"K0": float(K0_str.replace("K0", "")),
                                       "eps": float(eps_str.replace("eps", "")),
                                       "score": score})

    print(f"Chimera 点数量：{len(chimera_regions)} / {len(results) * len(eps_range)}")

    # Summary statistics
    if chimera_regions:
        avg_chimera_score = np.mean([r["score"] for r in chimera_regions])
        max_region = max(chimera_regions, key=lambda x: x["score"])
        print(f"平均 chimera 分数：{avg_chimera_score:.3f}")
        print(f"最高分数：{max_region['score']:.3f} (K0={max_region['K0']:.1f}, eps={max_region['eps']:.1f})")

    # Save results
    output_path = "labs/simulations/chimera_parameter_scan_results.json"
    with open(output_path, "w") as f:
        json.dump({"meta": {"K0_range": K0_range.tolist(),
                           "eps_range": eps_range.tolist(),
                           "omega1": omega1,
                           "chimera_threshold": 0.3,
                           "chimera_points": len(chimera_regions)},
                    "results": results,
                    "chimera_regions": chimera_regions}, f, indent=2)
    print(f"\n数据已保存：{output_path}")


if __name__ == "__main__":
    run_parameter_scan()
