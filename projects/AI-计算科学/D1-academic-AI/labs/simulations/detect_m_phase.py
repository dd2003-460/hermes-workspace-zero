#!/usr/bin/env python3
"""
M 相凝聚检测 — D4-S18-r18 定理的工程实现

检测相位空间中的凝聚区数量 M。
方法：k-means 聚类 + 区域纯度判定
"""

import numpy as np
from typing import Tuple, List


def phases_to_points(phases: np.ndarray) -> np.ndarray:
    """将相位映射到复平面单位圆上的点"""
    return np.column_stack([np.cos(phases), np.sin(phases)])


def count_clusters(phases: np.ndarray, max_m: int = 5) -> int:
    """
    用简单的两阶段聚类估计凝聚区数量：
    1. 用 DBSCAN-like 密度阈值将点分组
    2. 合并距离过近的组
    """
    points = phases_to_points(phases)
    n = len(points)
    assigned = np.zeros(n, dtype=bool)
    clusters = []

    # 阶段1：基于密度的分组
    for i in range(n):
        if assigned[i]:
            continue
        # 找距离小于阈值的点
        dists = np.linalg.norm(points - points[i], axis=1)
        neighborhood = np.where(dists < 0.3)[0]
        # 检查邻居密度
        if len(neighborhood) < max(4, n * 0.05):
            clusters.append([i])
            assigned[i] = True
            continue
        for j in neighborhood:
            if not assigned[j]:
                clusters.append([j])
                assigned[j] = True

    # 合并距离很近的簇
    merged = [clusters[0]] if clusters else []
    for c in clusters[1:]:
        centroid_new = np.mean(points[c], axis=0)
        merged_all = np.vstack([merged[-1][0:0].reshape(0,2), centroid_new])
        for m_idx, m_cluster in enumerate(merged):
            centroid_merged = np.mean(points[m_cluster], axis=0) if m_cluster else np.zeros(2)
            dist = np.linalg.norm(centroid_merged - centroid_new)
            if dist > 0.2:
                merged.append(c)
                break
        else:
            # 太近，合并
            if merged:
                merged[-1] = np.concatenate([np.array(merged[-1]), np.array(c)])

    # 简化：用简单距离分组
    if merged == [clusters[0]] if clusters else [] and len(clusters) > 1:
        # 回退：用距离最近的聚类中心
        return simple_cluster_count(points)

    return len(merged)


def simple_cluster_count(points: np.ndarray) -> int:
    """简化聚类计数：基于角分布的峰值检测"""
    angles = np.arctan2(points[:, 1], points[:, 0])
    hist, _ = np.histogram(angles, bins=8, range=(0, 2*np.pi))
    # 计算峰数（密度 > 10% 均值的地方）
    threshold = hist.mean() * 0.1
    peaks = sum(1 for h in hist if h > threshold)
    return max(1, peaks)


def m_phase_detection(phases: np.ndarray, n_bins: int = 32) -> Tuple[int, dict]:
    """
    M 相凝聚检测 — 改进版（32 bins，含相邻区域合并）

    Returns:
        (M, diagnostics)
    """
    points = phases_to_points(phases)
    angles = np.arctan2(points[:, 1], points[:, 0])

    # 高角度分辨率
    bin_edges = np.linspace(0, 2*np.pi, n_bins + 1)
    counts, _ = np.histogram(angles, bins=bin_edges)

    # 只保留显著活跃的区域（> 1% 总分布）
    threshold = len(phases) * 0.01
    active_regions = np.where(counts > threshold)[0]
    if len(active_regions) == 0:
        return 0, {}

    if len(active_regions) == 1:
        return 1, {
            "active_regions": active_regions.tolist(),
            "region_counts": counts[active_regions].tolist(),
            "center_angles": [float(np.rad2deg(bin_edges[active_regions[0]] + bin_edges[active_regions[0]+1])/2)],
            "center_weights": [float(counts[active_regions[0]] / counts.sum())],
        }

    # 合并距离过近的活跃区域（距离 <= 2 bins = 同一凝聚区）
    merged = [active_regions[0]]
    for r in active_regions[1:]:
        if r - merged[-1] <= 2:
            merged[-1] = r
        else:
            merged.append(r)

    M = len(merged)

    centers = np.array([(bin_edges[r] + bin_edges[r+1]) / 2 for r in merged])
    center_weights = counts[merged] / counts.sum()

    return M, {
        "active_regions": merged,
        "region_counts": counts[merged].tolist(),
        "center_angles": np.rad2deg(centers).tolist(),
        "center_weights": center_weights.tolist(),
    }


if __name__ == "__main__":
    np.random.seed(42)

    np.random.seed(42)

    # 测试：M=1（全同步）
    phases_m1 = np.random.normal(0.5, 0.1, 64) % (2*np.pi)
    M1, diag1 = m_phase_detection(phases_m1)
    print(f"M=1 全同步测试: M={M1}, regions={diag1['active_regions']}")

    # 测试：M=2（两个凝聚区）
    n_half = 32
    phases_m2 = np.concatenate([
        np.random.normal(0, 0.3, n_half) % (2*np.pi),
        np.random.normal(3.14, 0.3, n_half) % (2*np.pi)
    ])
    M2, diag2 = m_phase_detection(phases_m2)
    print(f"M=2 双凝聚测试: M={M2}, regions={diag2['active_regions']}")

    # 测试：均匀分布（无凝聚）
    phases_unif = np.random.uniform(0, 2*np.pi, 64)
    M3, diag3 = m_phase_detection(phases_unif)
    print(f"均匀分布测试: M={M3}, regions={diag3['active_regions']}")
