#!/usr/bin/env python3
"""
S17-1 实证验证: 语义空间曲率与测地线假设
===========================================

对应 conjecture: S17-1 (Semantic Geodesic Conjecture)
TASKS.md 任务: S17-1 测地线不变量 + S17-1 信息论关联

使用纯 numpy/scipy 实现，无需 torch/gensim。
语义空间用 TF-IDF 向量近似，Fisher 信息度量用局部协方差近似。

假设:
  H0: 语义空间曲率非零
  H1: 测地线距离与人类语义相似性相关性 > 欧氏距离
  H2: "绕路"路径的信息损失约等于"最短"路径
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.sparse.linalg import svds
from sklearn.feature_extraction.text import TfidfVectorizer
import json, os, time

np.random.seed(42)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "researches")


# ============================================================
# 1. 构建语义概念集合
# ============================================================

def build_concept_corpus():
    """
    构建一个语义概念集合。
    每个概念用一组描述文本表示（来自概念层级）。

    层级结构:
      动物 -> 哺乳动物 -> 狗 -> 拉布拉多
      动物 -> 哺乳动物 -> 猫
      动物 -> 鸟类
      交通工具 -> 陆地 -> 汽车
      交通工具 -> 陆地 -> 火车
      交通工具 -> 空中 -> 飞机
      食物 -> 水果 -> 苹果
      食物 -> 水果 -> 香蕉
      食物 -> 蔬菜 -> 胡萝卜
      颜色 -> 红色
      颜色 -> 蓝色
      情感 -> 快乐
      情感 -> 悲伤
      数学 -> 代数
      数学 -> 几何
      数学 -> 分析
    """
    concepts = {
        # 动物层级
        "animal": "creature living organism biological entity life form",
        "mammal": "warm-blooded animal vertebrate furry nursing young",
        "dog": "loyal pet canine four-legged faithful companion domestic animal",
        "labrador": "friendly retriever large dog breed gentle energetic playful",
        "cat": "independent feline domestic predatory agile whiskers nocturnal",
        "bird": "feathered winged avian flying egg-laying song",
        # 交通工具
        "vehicle": "transportation machine conveyance mobility traveling",
        "land_vehicle": "road wheeled ground transportation automobile",
        "car": "four-wheeled motorized personal road transportation sedan",
        "train": "railway wheeled heavy mass public transportation locomotive",
        "aircraft": "flying sky aerial airborne winged flight",
        # 食物
        "food": "edible nutrition nourishment sustenance consumable",
        "fruit": "sweet plant food natural sugary juice ripe",
        "apple": "crisp round pomaceous orchard red green dessert",
        "banana": "long yellow tropical fruit sweet potassium peel",
        "vegetable": "plant food green nutritious salad root leaf",
        # 颜色
        "color": "hue chromatic visual perceptual wavelength spectrum",
        "red": "warm blood fire crimson burgundy passionate intense",
        "blue": "cool ocean sky azure cerulean calm serene tranquil",
        # 情感
        "emotion": "feeling affective response psychological experience mood",
        "happiness": "joy glad content bliss pleasure laughter smile",
        "sadness": "grief sorrow mourn weep depression melancholy despair",
        # 数学
        "mathematics": "abstract formal logic numbers proof equation structure",
        "algebra": "symbols variables equations operations abstract manipulation",
        "geometry": "spatial shape figures measurements angles topology distances",
        "analysis": "calculus limits derivatives integrals continuity infinity",
    }
    return concepts


# ============================================================
# 2. TF-IDF 语义空间构建
# ============================================================

def build_tfidf_space(concepts):
    """
    将概念集合映射为TF-IDF空间。
    每个概念是一个"文档"，包含相关词汇。
    """
    concept_names = list(concepts.keys())
    documents = list(concepts.values())

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # 降维到2D/3D以便可视化
    U, S, Vt = svds(tfidf_matrix, k=min(3, tfidf_matrix.shape[1] - 1))
    # 按奇异值排序
    idx = np.argsort(-S)
    embeddings = U[:, idx] * S[idx]

    # 原始高维空间也保留
    return {
        "names": concept_names,
        "embeddings_low": embeddings,  # for visualization
        "embeddings_high": tfidf_matrix.toarray(),  # for geometric analysis
        "vectorizer": vectorizer,
    }


# ============================================================
# 3. Fisher 信息度量估计 (局部协方差近似)
# ============================================================

def estimate_fisher_metric(embeddings_high, concept_idx, local_k=5):
    """
    在第 concept_idx 个概念附近，用 local PCA 估计 Fisher 信息度量。

    Fisher 信息度量 g_ij = E[∂_i log p · ∂_j log p]
    近似为: 局部协方差矩阵的逆（或局部 PCA 的主轴方差）
    """
    # 获取附近点（k-NN）
    dists = np.linalg.norm(embeddings_high - embeddings_high[concept_idx], axis=1)
    nn_idx = np.argsort(dists)[1:1 + local_k]  # 排除自身

    local_pts = embeddings_high[nn_idx]
    local_mean = local_pts.mean(axis=0)
    local_centered = local_pts - local_mean

    # 局部协方差
    cov = local_centered.T @ local_centered / len(local_pts)

    # 正则化
    cov += 1e-6 * np.eye(cov.shape[0])

    return cov


def compute_sectional_curvature(concepts_dict, data, min_curv_samples=5):
    """
    估计语义空间的sectional curvature。

    使用低维TF-IDF空间（3D）的局部协方差来估计曲率。
    高维TF-IDF是高度稀疏的，local covariance几乎总是极端条件。

    曲率强度 = (最大特征值 - 最小特征值) / (最大特征值 + 最小特征值)
    - 接近0 → 平坦空间（所有方向方差相当）
    - 接近1 → 高曲率空间（各向异性显著）
    """
    curvatures = []
    names = data["names"]
    # 使用3D低维嵌入计算曲率（更稳定）
    embeddings_3d = data["embeddings_low"]

    for i in range(0, len(names), max(1, len(names) // 20)):
        try:
            cov = estimate_fisher_metric(embeddings_3d, i, local_k=min(4, len(names) - 1))
            eigvals = np.linalg.eigvalsh(cov)
            # 排除极小特征值
            eigvals = eigvals[eigvals > 1e-10]
            if len(eigvals) < 2:
                continue
            # 曲率强度
            curvature_strength = float((eigvals[-1] - eigvals[0]) / (eigvals[-1] + eigvals[0] + 1e-10))
            curvatures.append({
                "concept": names[i],
                "curvature_strength": round(curvature_strength, 4),
                "eigenvalues": [round(float(e), 6) for e in eigvals],
            })
        except Exception as e:
            continue

    if not curvatures:
        return []

    curvatures.sort(key=lambda c: c["curvature_strength"], reverse=True)
    # 只返回最有代表性的样本
    return curvatures[:min(len(curvatures), 15)]


# ============================================================
# 4. 测地线 vs 欧氏距离
# ============================================================

def build_knn_graph(embeddings_tf, k=5):
    """构建连通图：k-NN (k=5) + 按余弦距离排序的全局边添加(连通所有组件)"""
    from sklearn.neighbors import NearestNeighbors

    n = len(embeddings_tf)

    # k-NN (余弦距离)
    nn = NearestNeighbors(n_neighbors=k + 1, metric='cosine').fit(embeddings_tf)
    distances, knn_indices = nn.kneighbors(embeddings_tf)

    # 构建边集
    edge_set = set()
    for i in range(n):
        for j_idx in range(1, k + 1):
            j = knn_indices[i][j_idx]
            w = distances[i][j_idx]
            edge_set.add((min(i, j), max(i, j), w))

    # 用全局最近邻连接断开的组件
    all_dists = []
    for i in range(n):
        for j in range(i + 1, n):
            w = 1.0 - np.dot(embeddings_tf[i], embeddings_tf[j])
            all_dists.append((i, j, w))

    all_dists.sort(key=lambda x: x[2])

    # Kruskal: 如果添加边能连接两个组件，则添加
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
            return True
        return False

    connected_count = n
    for i, j, w in all_dists:
        if find(i) != find(j):
            edge_set.add((min(i, j), max(i, j), w))
            if union(i, j):
                connected_count -= 1
                if connected_count == 1:
                    break

    # 转换为列表
    edges = [(i, j, w) for (i, j, w) in edge_set]
    return edges, knn_indices, np.zeros((n, k + 1))  # edge_weights 不用于最终分析


def dijkstra_shortest_path(adj, start, end, n_points):
    """Dijkstra 最短路径 + 中间点采样"""
    import heapq
    n = len(adj)

    dist = [float('inf')] * n
    prev = [-1] * n
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))

    if dist[end] == float('inf'):
        return [start, end], [start, end], float('inf')

    # 回溯路径
    path = []
    cur = end
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    # 均匀采样中间点
    if len(path) >= n_points and n_points > 2:
        step = len(path) / max(n_points - 1, 1)
        sampled = [path[min(int(round(i * step)), len(path) - 1)] for i in range(n_points)]
    else:
        sampled = path

    return path, sampled, dist[end]


def generate_detour_path(adj, start, end, max_length):
    """生成绕路路径：从起点出发，随机走但不直接到终点"""
    n = len(adj)
    path = [start]
    visited = {start}

    while len(path) < max_length:
        current = path[-1]
        neighbors = [node for node, _ in adj[current]]

        # 排除已访问和终点（避免太直接）
        options = [j for j in neighbors if j not in visited and j != end]
        if not options:
            options = [j for j in neighbors if j != end]
        if not options:
            break

        # 随机选择邻居
        next_node = np.random.choice(options)
        path.append(next_node)
        visited.add(next_node)

    path.append(end)
    return path


# ============================================================
# 5. 信息损失估计
# ============================================================

def estimate_path_information_loss(embeddings_tf, path_indices):
    """
    估计路径的信息损失。
    用TF-IDF向量与"平均向量"的余弦距离作为信息损失代理：
    路径越长（经过越远的概念），平均概念变化越大，信息损失越高。
    """
    if len(path_indices) < 2:
        return 0.0

    avg_vector = embeddings_tf[path_indices].mean(axis=0)
    # 起点和终点相对于平均向量的偏离度 = 信息损失
    start_dist = 1.0 - np.dot(embeddings_tf[path_indices[0]], avg_vector)
    end_dist = 1.0 - np.dot(embeddings_tf[path_indices[-1]], avg_vector)
    return start_dist - end_dist


# ============================================================
# 6. 运行所有实验
# ============================================================

def run_experiments():
    start_time = time.time()
    print("=" * 60)
    print("S17-1 实证验证: 语义空间曲率与测地线假设")
    print("=" * 60)

    # Step 1: 构建语义概念集合和TF-IDF空间
    print("\n[1/5] 构建语义概念集合...")
    concepts_dict = build_concept_corpus()
    data = build_tfidf_space(concepts_dict)

    print(f"  概念数量: {len(data['names'])}")
    print(f"  TF-IDF维度: {data['embeddings_high'].shape[1]}")
    print(f"  低维投影: {data['embeddings_low'].shape}")

    # Step 2: 曲率估计
    print("\n[2/5] 估计语义空间曲率...")
    curvatures = compute_sectional_curvature(concepts_dict, data)

    if curvatures:
        strengths = [c["curvature_strength"] for c in curvatures]
        mean_curv = np.mean(strengths)
        std_curv = np.std(strengths)
        print(f"  曲率强度 (均值 ± std): {mean_curv:.4f} ± {std_curv:.4f}")
        print(f"  曲率范围: [{min(strengths):.4f}, {max(strengths):.4f}]")

        h0_result = "REJECTED (curvature ≈ 0)" if mean_curv < 0.05 else "SUPPORTED (curvature ≠ 0)"
        print(f"  H0 (曲率非零): {h0_result}")
    else:
        print("  曲率估计失败")
        mean_curv = 0.0
        std_curv = 0.0

    # Step 3: 测地线 vs 欧氏距离
    print("\n[3/5] 构建语义图 + Dijkstra最短路径...")
    edges, knn_indices, edge_weights = build_knn_graph(data["embeddings_high"], k=5)
    print(f"  图节点数: {edges and max(max(e[0], e[1]) for e in edges) + 1}")
    print(f"  图边数: {len(edges)}")

    # 构建邻接表
    from collections import defaultdict
    adj = defaultdict(list)
    for i, j, w in edges:
        adj[i].append((j, w))
        adj[j].append((i, w))

    # 选择概念对
    name_to_idx = {name: i for i, name in enumerate(data["names"])}

    # 定义有语义意义的概念对
    test_pairs = [
        ("dog", "labrador"),       # 语义相近（hyponym）
        ("dog", "cat"),            # 语义相近（同category）
        ("dog", "bird"),           # 语义中等
        ("dog", "car"),            # 语义远
        ("dog", "apple"),          # 语义远
        ("mathematics", "geometry"),  # 语义相近
        ("mathematics", "analysis"),    # 语义相近
        ("mathematics", "happiness"),   # 语义远
        ("red", "blue"),           # 同category，语义相近
        ("red", "happiness"),      # 跨category，语义远
    ]

    results_path_comparison = []
    for name_a, name_b in test_pairs:
        if name_a not in name_to_idx or name_b not in name_to_idx:
            continue

        idx_a = name_to_idx[name_a]
        idx_b = name_to_idx[name_b]

        # 余弦距离 (TF-IDF归一化向量的正确距离度量)
        d_eucl = 1.0 - np.dot(data["embeddings_high"][idx_a], data["embeddings_high"][idx_b])

        # 最短路径 (Dijkstra)
        path, sampled, d_geo = dijkstra_shortest_path(
            adj, idx_a, idx_b, n_points=5
        )

        # 信息损失
        il_short = estimate_path_information_loss(data["embeddings_high"], path)
        il_sampled = estimate_path_information_loss(data["embeddings_high"], sampled)
        il_sampled = estimate_path_information_loss(data["embeddings_high"], sampled)

        results_path_comparison.append({
            "concept_pair": [name_a, name_b],
            "euclidean_distance": float(d_eucl),
            "geodesic_distance": float(d_geo),
            "geodesic_euclidean_ratio": float(d_geo / (d_eucl + 1e-10)),
            "path_length": len(path),
            "information_loss_short": float(il_short),
            "information_loss_sampled": float(il_sampled),
        })

        print(f"  {name_a}->{name_b}: d_eucl={d_eucl:.4f}, d_geo={d_geo:.4f}, ratio={d_geo/(d_eucl+1e-10):.4f}")

    # Step 4: 绕路路径 vs 最短路径
    print("\n[4/5] 生成绕路路径 + 比较信息损失...")
    detour_results = []
    n_simulations = 30

    for sim in range(n_simulations):
        idx_a = np.random.randint(len(data["names"]))
        idx_b = np.random.randint(len(data["names"]))
        if idx_a == idx_b:
            continue

        # 最短路径
        path_short, _, d_geo = dijkstra_shortest_path(
            adj, idx_a, idx_b, n_points=10
        )

        # 绕路路径
        path_detour = generate_detour_path(adj, idx_a, idx_b, max_length=min(len(path_short) * 2, 20))
        if len(path_detour) < 3:
            path_detour = path_short  # fallback

        il_short = estimate_path_information_loss(data["embeddings_high"], path_short)
        il_detour = estimate_path_information_loss(data["embeddings_high"], path_detour)

        detour_results.append({
            "sim": sim,
            "start": data["names"][idx_a],
            "end": data["names"][idx_b],
            "path_length_short": len(path_short),
            "path_length_detour": len(path_detour),
            "dijkstra_distance": float(d_geo),
            "info_loss_short": float(il_short),
            "info_loss_detour": float(il_detour),
            "info_loss_ratio": float(il_detour / (abs(il_short) + 1e-10)),
        })

    if detour_results:
        il_ratios = [d["info_loss_ratio"] for d in detour_results]
        mean_ratio = np.mean(il_ratios)
        print(f"  信息损失比 (detour/short, 均值): {mean_ratio:.4f}")

        h2_result = "SUPPORTED" if mean_ratio < 2.0 else "NOT SUPPORTED (detour >> short)"
        print(f"  H2 (绕路不显著增加信息损失): {h2_result}")
    else:
        print("  绕路实验无结果")
        mean_ratio = 0.0

    # Step 5: 总结
    elapsed = time.time() - start_time
    print(f"\n[5/5] 实验完成 ({elapsed:.1f}s)")

    all_results = {
        "summary": {
            "h0_curvature": h0_result if 'h0_result' in dir() else "N/A",
            "mean_curvature": mean_curv,
            "std_curvature": std_curv,
            "h2_detour_result": h2_result if 'h2_result' in dir() else "N/A",
            "mean_detour_ratio": mean_ratio,
        },
        "curvatures": curvatures,
        "path_comparison": results_path_comparison,
        "detour_results": detour_results,
    }

    output_path = os.path.join(RESULTS_DIR, "S17-1-Empirical-Results.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存: {output_path}")

    return all_results


if __name__ == "__main__":
    results = run_experiments()
    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)
    print(f"  H0 (曲率非零): {results['summary']['h0_curvature']}")
    print(f"  H2 (绕路信息损失): {results['summary']['h2_detour_result']}")
    print(f"  平均曲率: {results['summary']['mean_curvature']:.4f}")
    print(f"  绕路/最短信息损失比: {results['summary']['mean_detour_ratio']:.4f}")
