#!/usr/bin/env python3
"""
实验：区分 chimera 态 vs 频率梯度导致的表面 chimera 分数

D4-S18-r21 的发现：频率梯度 ω≠0 时，当前 chimera_score 方法对所有参数返回高分
这意味着 chimera_score 测量的是"局部同步不均匀性"，而非真正的 chimera 态。

真正的 chimera 判定需要验证：
1. 局部区域内高同步（同步区）
2. 全局上不均匀（存在异步区）

"""

import numpy as np
import json


def simulate_phases(N=500, T=6000, dt=0.02, **params):
    """模拟并返回最终的相位分布"""
    rng = np.random.RandomState(42)
    theta = rng.uniform(0, 2*np.pi, N)
    pos = np.linspace(0, 1, N, endpoint=False)

    K0 = params.get('K0', 1.0)
    eps = params.get('eps', 0.5)
    omega1 = params.get('omega1', 0.0)

    k_spatial = K0 * (1 + eps * np.cos(2 * np.pi * pos))
    omega = omega1 * np.cos(pos) if omega1 > 0 else np.zeros(N)

    for t in range(T):
        coupling = np.zeros(N)
        for i in range(N):
            j_left = (i - 1) % N
            j_right = (i + 1) % N
            coupling[i] += k_spatial[i] * (np.sin(theta[j_left] - theta[i]) +
                                           np.sin(theta[j_right] - theta[i]))
        theta += dt * (omega + coupling)
        theta = theta % (2 * np.pi)

    return theta


def kmeans_cluster(X, k, n_init=3, random_state=42):
    """简单 K-means 实现（不依赖 sklearn）"""
    import warnings
    warnings.filterwarnings('ignore')
    rng = np.random.RandomState(random_state)
    N = len(X)
    X = X.reshape(-1, 1)  # Ensure 2D

    best_labels = None
    best_inertia = float('inf')

    for init in range(n_init):
        # 随机选初始中心
        try:
            centers_idx = rng.choice(N, k, replace=False)
        except ValueError:
            centers_idx = rng.randint(0, N, k)
        centers = X[centers_idx].copy()

        for iteration in range(100):
            # 分配
            dists = np.zeros((N, k))
            for c in range(k):
                dists[:, c] = np.sum((X - centers[c]) ** 2, axis=1)
            labels = np.argmin(dists, axis=1)

            # 更新中心
            new_centers = centers.copy()
            has_empty = False
            for c in range(k):
                mask = (labels == c).astype(bool)
                n_points = int(np.sum(mask))
                if n_points > 0:
                    new_centers[c] = np.mean(X[mask], axis=0)
                else:
                    has_empty = True
                    # 重新初始化空簇
                    new_centers[c] = X[rng.randint(0, N)]

            # 收敛判断
            if np.linalg.norm(new_centers - centers) < 1e-6 and not has_empty:
                centers = new_centers
                break
            centers = new_centers

        # 计算惯性
        inertia = 0.0
        for c in range(k):
            mask = (labels == c).astype(bool)
            n_points = int(np.sum(mask))
            if n_points > 0:
                inertia += float(np.sum((X[mask] - centers[c]) ** 2))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()

    return best_labels, best_inertia


def silhouette_score(X, labels):
    """简单轮廓系数计算"""
    N = len(X)
    X = X.reshape(-1, 1)  # Ensure 2D
    unique_labels = list(set(labels))
    if len(unique_labels) <= 1:
        return 0.0

    scores = np.zeros(N)
    for i in range(N):
        same_cluster = np.where(labels == labels[i])[0]
        other_clusters = np.setdiff1d(np.arange(N), same_cluster)

        # a(i) = 同簇内平均距离
        if len(same_cluster) > 1:
            a_i = np.mean(np.sum((X[same_cluster] - X[i]) ** 2, axis=1))
        else:
            a_i = 0

        # b(i) = 到其他簇最小平均距离
        b_i = float('inf')
        for label in unique_labels:
            if label != labels[i]:
                other = np.where(labels == label)[0]
                if len(other) > 0:
                    mean_dist = np.mean(np.sum((X[other] - X[i]) ** 2, axis=1))
                    b_i = min(b_i, mean_dist)

        # 轮廓系数
        denom = max(a_i, b_i)
        if denom > 0:
            scores[i] = (b_i - a_i) / denom
        else:
            scores[i] = 0

    return float(np.mean(scores))


def chimera_cluster_analysis(phases, num_clusters=10):
    """
    使用朴素 k-means 聚类分析相位分布。

    真正 chimera 的判定条件：
    1. 聚类数 C < N（不是每个振子独立）
    2. 聚类大小方差大（有的聚集群一致，有的分散）
    3. 空间上聚类不混合（同步区和异步区空间分离）
    """
    N = len(phases)

    # 尝试不同聚类数，找到最优（用轮廓系数）
    best_score = -1
    best_k = 2
    for k in range(2, min(15, N // 10)):
        labels, _ = kmeans_cluster(phases, k, n_init=3)
        if len(set(labels)) > 1:
            score = silhouette_score(phases, labels)
            if score > best_score:
                best_score = score
                best_k = k

    # 统计每个聚类的统计量
    cluster_stats = {}
    for k in range(best_k):
        mask = labels == k
        cluster_size = np.sum(mask)
        cluster_mean_phase = np.mean(phases[mask])
        cluster_coherence = abs(np.mean(np.exp(1j * phases[mask])))
        cluster_stats[k] = {
            "size": int(cluster_size),
            "size_fraction": float(cluster_size / N),
            "mean_phase": float(cluster_mean_phase),
            "coherence": float(cluster_coherence)
        }

    # 聚类大小方差（真正 chimera 应该高）
    sizes = [c["size"] for c in cluster_stats.values()]
    size_variance = float(np.var(sizes)) if sizes else 0

    # 高相干聚类占比（true chimera: 部分区高度相干）
    high_coherence_ratio = sum(1 for c in cluster_stats.values()
                                if c["coherence"] > 0.9) / best_k

    # 空间隔离：检查相邻振子是否属于不同聚类
    spatial_segregation = 0
    for i in range(N - 1):
        if labels[i] != labels[i + 1]:
            spatial_segregation += 1
    spatial_segregation /= (N - 1)  # 归一化

    return {
        "k": int(best_k),
        "silhouette": float(best_score),
        "cluster_stats": cluster_stats,
        "size_variance": size_variance,
        "high_coherence_ratio": high_coherence_ratio,
        "spatial_segregation": spatial_segregation
    }


def global_coherence(phases):
    """全局相干度：R = |sum(e^{i*theta_i})| / N"""
    N = len(phases)
    return abs(np.sum(np.exp(1j * phases))) / N


def run_comparison():
    """比较不同耦合配置下的相位结构"""
    configs = [
        {"K0": 1.0, "eps": 0.0, "omega1": 0.0, "name": "uniform_coupling"},
        {"K0": 1.0, "eps": 0.0, "omega1": 0.5, "name": "freq_gradient_only"},
        {"K0": 1.0, "eps": 0.5, "omega1": 0.0, "name": "spatial_coupling_only"},
        {"K0": 1.0, "eps": 0.5, "omega1": 0.5, "name": "both"},
    ]

    results = {}
    for config in configs:
        print(f"Simulating: {config['name']}...")
        phases = simulate_phases(N=500, T=6000, **config)

        result = {
            "name": config["name"],
            "global_coherence": float(global_coherence(phases)),
            "cluster_analysis": chimera_cluster_analysis(phases, num_clusters=10)
        }
        results[config["name"]] = result

        # Print summary
        ca = result["cluster_analysis"]
        print(f"  Global R: {result['global_coherence']:.3f}")
        print(f"  Best K: {ca['k']}, Silhouette: {ca['silhouette']:.3f}")
        print(f"  Size var: {ca['size_variance']:.1f}")
        print(f"  High-coherence ratio: {ca['high_coherence_ratio']:.2f}")
        print(f"  Spatial segregation: {ca['spatial_segregation']:.3f}")
        print()

    # Save full results
    output_path = "labs/simulations/chimera_vs_freq_gradient_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    run_comparison()
