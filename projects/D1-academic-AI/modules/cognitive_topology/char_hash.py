"""
D1-r02 字符哈希实现 — 零依赖的认知拓扑估计器

与耦合振荡器的对应关系：
┌──────────────┬──────────────────────────────────────┐
│ 物理系统     │ 认知系统                             │
├──────────────┼──────────────────────────────────────┤
│ 相位 θ_i(t)  │ 句子语义向量 v_i                      │
│ 凝聚区       │ 语义特征簇（相似句子聚合）             │
│ I_C = χ+w₂   │ 凝聚区数量（离散态）                   │
│ dI_C/dt      │ 认知状态变化率                        │
└──────────────┴──────────────────────────────────────┘
"""

import numpy as np
import re
from typing import List, Tuple

def _sentence_tokenize(text: str) -> List[str]:
    """中文/英文通用分句"""
    sentences = re.split(r'[。！？.\n]+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def _char_hash(text: str, n_dim: int = 64) -> np.ndarray:
    """字符级哈希投影"""
    vec = np.zeros(n_dim)
    for ch in text:
        vec[ord(ch) % n_dim] += 1
    return vec / (len(text) + 1e-6)

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return float(dot / (norm_a * norm_b)) if norm_a and norm_b else 0.0

def _pairwise(iterable):
    """Sliding window (Python 3.9 compat)"""
    it = iter(iterable)
    a = next(it, None)
    for b in it:
        yield a, b
        a = b


class CognitiveTopologyEstimator:
    def __init__(self, n_dim: int = 64, window: int = 3,
                 cluster_high_sim: float = 0.35,
                 cluster_high_var: float = 0.003,
                 cluster_med_sim: float = 0.30,
                 cluster_low_sim: float = 0.20):
        """
        Parameters
        ----------
        n_dim : 哈希向量维度
        window : 滑动窗口大小（句子数）
        cluster_* : 聚类阈值（针对字符哈希空间校准）
        """
        self.n_dim = n_dim
        self.window = window
        self.cluster_high_sim = cluster_high_sim
        self.cluster_high_var = cluster_high_var
        self.cluster_med_sim = cluster_med_sim
        self.cluster_low_sim = cluster_low_sim

    def estimate_ic(self, text: str) -> Tuple[float, float, List[int]]:
        """估计 I_C 和 |dI_C/dt|"""
        sentences = _sentence_tokenize(text)
        if len(sentences) < self.window:
            return 1.0, 0.0, [1]

        vectors = [_char_hash(s, self.n_dim) for s in sentences]
        ic_sequence = []

        for i in range(0, len(sentences) - self.window + 1):
            window_vecs = vectors[i:i + self.window]
            sims = [_cosine_similarity(a, b) for a, b in _pairwise(window_vecs)]
            avg_sim = np.mean(sims)
            sim_var = np.var(sims)

            if avg_sim > self.cluster_high_sim and sim_var < self.cluster_high_var:
                clusters = 1
            elif avg_sim > self.cluster_med_sim:
                clusters = min(3, max(2, int(4 - avg_sim * 8)))
            elif avg_sim > self.cluster_low_sim:
                clusters = min(5, int(6 - avg_sim * 15) + 1)
            else:
                clusters = max(5, len(window_vecs) + 1)
            ic_sequence.append(clusters)

        if len(ic_sequence) < 2:
            return float(ic_sequence[-1]), 0.0, ic_sequence

        ic = float(np.mean(ic_sequence))
        d_ic = float(np.mean([abs(ic_sequence[j + 1] - ic_sequence[j])
                              for j in range(len(ic_sequence) - 1)]))
        return ic, d_ic, ic_sequence

    def full_analysis(self, text: str) -> dict:
        ic, d_ic, ic_sequence = self.estimate_ic(text)
        t_cog = ic * np.log(1 + max(d_ic, 0))

        return {
            "I_C": round(ic, 2),
            "dIC_dt": round(d_ic, 2),
            "T_cog": round(t_cog, 2),
            "ic_sequence": ic_sequence,
        }
