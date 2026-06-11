#!/usr/bin/env python3
"""persona-v3 关键词库 — 6 维度加权关键词定义 (从 gap_filler_v2 共享)。

所有工具共享同一份关键词定义，确保评估一致性。
"""

DIMENSION_KEYWORDS = {
    "自适应感知": [
        ("感知", 1.0), ("感知时间", 1.5), ("感知速率", 1.5),
        ("感知干扰", 1.0), ("感知资源", 1.0), ("信息密度", 1.0),
        ("perception", 1.0), ("sensory", 1.0), ("感知任务", 1.0),
        ("感知精度", 1.0), ("感知分配", 1.0), ("感知粒度", 0.5),
        ("t_p", 1.5), ("细感知", 1.0),
    ],
    "自适应探索": [
        ("探索", 1.0), ("探索频率", 1.5), ("探索利用", 1.5),
        ("不确定性", 1.0), ("工具选择", 1.0), ("磨刀", 1.0),
        ("exploration", 1.0), ("exploit", 1.0), ("探索深度", 1.0),
    ],
    "自适应精度": [
        ("精度", 1.0), ("rate-distortion", 1.5), ("R(D)", 1.5),
        ("压缩", 1.0), ("信息瓶颈", 1.0), ("压缩精度", 1.0),
        ("adaptive precision", 1.0), ("信噪比", 1.0),
    ],
    "自适应自我": [
        ("观测者", 1.0), ("observer-dependent", 2.0), ("observer-dependence", 2.0),
        ("观测者-环境", 2.0), ("y(θ)", 1.5), ("第一人称", 1.0),
        ("第三人称", 1.0), ("自我视角", 1.0), ("规律是观测者", 1.0),
    ],
    "自适应投影": [
        ("低维", 2.0), ("跨域", 2.0), ("同构", 1.5), ("isomorphic", 1.5),
        ("类比", 1.0), ("映射", 1.0), ("结构", 1.0), ("高维", 1.0),
    ],
    "自适应先验": [
        ("先验", 1.0), ("贝叶斯", 1.5), ("P(H)", 1.5), ("P(H|E)", 1.5),
        ("后验", 1.0), ("先验分布", 1.0), ("认知结构", 1.0),
    ],
}

# 核心关键词 — 在 52 个 gap_filler 增强 idea 文件中命中率 < 50%
# 这些关键词难以被模板注入命中，能区分真实语义对齐
CORE_KEYWORDS = {
    "自适应感知": [
        ("感知干扰", 1.0), ("perception", 1.0), ("sensory", 1.0),
        ("感知任务", 1.0), ("感知分配", 1.0),
    ],
    "自适应探索": [
        ("探索利用", 1.5), ("exploration", 1.0), ("exploit", 1.0),
        ("探索深度", 1.0),
    ],
    "自适应精度": [
        ("信息瓶颈", 1.0), ("压缩精度", 1.0), ("adaptive precision", 1.0),
    ],
    "自适应自我": [
        ("observer-dependence", 2.0), ("y(θ)", 1.5), ("自我视角", 1.0),
    ],
    "自适应投影": [
        ("高维", 1.0),
    ],
    "自适应先验": [
        ("先验分布", 1.0),
    ],
}

TOTAL_WEIGHTS = {dim: sum(w for _, w in kws) for dim, kws in DIMENSION_KEYWORDS.items()}
CORE_WEIGHTS = {dim: sum(w for _, w in kws) for dim, kws in CORE_KEYWORDS.items()}


def compute_dimension_scores(text):
    """计算文本对 6 个维度的关键词匹配分数。

    返回: {dim_name: score (0-1)} — score = matched_weight / total_weight
    """
    text_lower = text.lower()
    scores = {}
    for dim, kws in DIMENSION_KEYWORDS.items():
        matched_weight = sum(w for kw, w in kws if kw.lower() in text_lower)
        total_weight = TOTAL_WEIGHTS[dim]
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0.0
    return scores


def compute_core_scores(text):
    """计算文本对 6 个维度的核心关键词匹配分数。

    核心关键词命中率低 (< 50%)，难以被模板注入伪造，
    能更好区分真实语义对齐和关键词注入。

    返回: {dim_name: score (0-1)} — score = matched_weight / total_weight
    """
    text_lower = text.lower()
    scores = {}
    for dim, kws in CORE_KEYWORDS.items():
        matched_weight = sum(w for kw, w in kws if kw.lower() in text_lower)
        total_weight = CORE_WEIGHTS[dim]
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0.0
    return scores


def dimension_keyword_signature(text):
    """计算文本的维度关键词签名 — 6 维度的匹配分数。
    这是区分不同维度的最强特征。
    """
    return compute_dimension_scores(text)
