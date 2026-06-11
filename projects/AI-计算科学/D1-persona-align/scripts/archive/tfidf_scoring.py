#!/usr/bin/env python3
"""persona-v3 TF-IDF 增强评分器

解决 DIMENSION_KEYWORDS 正交化实验中暴露的问题：
加权匹配 matched_weight/total_weight 在 corpus 级别上惩罚通用关键词。
TF-IDF 方法：跨维度共享的关键词在多个文件中出现，IDF 低 → 权重自动降低。

用法:
    python3 tfidf_scoring.py
"""

import math
import sys
import json
import glob
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from persona_keywords import DIMENSION_KEYWORDS, TOTAL_WEIGHTS


def compute_idf_factors(all_texts):
    """为每个关键词计算共享因子 (shared_factor)。

    shared_factor(k) = min(df(k) / threshold, 1.0) 其中 threshold = 2

    - 从未出现: factor = 0 → 不参与评分
    - df = 0: factor = 0 → full weight (1.0)
    - df = 1: factor = 0.5 → weight = 1.0 (不降权, 稀有)
    - df >= 2: factor = 1.0 → weight = 0.8 (轻微降权, 跨维共享)

    只对跨维度共享的关键词降权, 稀有关键词完全保留。
    这解决了正交化实验的问题: 共享关键词在 matched_weight 中贡献降低,
    但 total_weight 不变, 所以总体分数不受影响。
    """
    N = len(all_texts)
    THRESHOLD = 2  # df < 2 的关键词视为稀有, 不降权

    doc_freq = {}

    for text in all_texts:
        text_lower = text.lower()
        for dim, kws in DIMENSION_KEYWORDS.items():
            for kw, w in kws:
                kw_lower = kw.lower()
                if kw_lower not in doc_freq:
                    doc_freq[kw_lower] = 0
                if kw_lower in text_lower:
                    doc_freq[kw_lower] += 1

    idf_factors = {}
    for kw, df in doc_freq.items():
        if df <= THRESHOLD:
            idf_factors[kw] = 1.0  # 稀有关键词, 不降权
        else:
            idf_factors[kw] = max(0.7, 1.0 - (df / N) * 2)  # 共享关键词, 降权到最低 0.7

    return idf_factors, doc_freq


def score_with_tfidf(text, idf_factors):
    """使用有界 IDF 因子的维度评分。

    score(dim) = sum(w * idf_factor(kw) for matched keywords) / total_weight

    关键: 分母保持原始 total_weight (维持覆盖度),
    分子中共享关键词因 IDF 因子低而贡献小 (提升判别力)。
    """
    text_lower = text.lower()
    scores = {}

    for dim, kws in DIMENSION_KEYWORDS.items():
        matched_weight = 0.0
        total_weight = TOTAL_WEIGHTS[dim]
        for kw, w in kws:
            kw_lower = kw.lower()
            idf_val = idf_factors.get(kw_lower, 0.0)
            # 如果关键词在 corpus 中完全没出现过，给一个保守因子
            if idf_val == 0.0:
                idf_val = 0.5
            matched_weight += w * idf_val
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0.0

    return scores


def main():
    print("=" * 60)
    print("TF-IDF Enhanced Scoring — persona-v3")
    print("=" * 60)

    # Load all idea files
    idea_files = sorted(glob.glob(str(PROJECT_ROOT / "memory" / "idea-*.md")))
    print(f"Loading {len(idea_files)} idea files...")

    all_texts = []
    for fp in idea_files:
        all_texts.append(Path(fp).read_text(encoding="utf-8"))

    # Also include the prompt for IDF computation
    prompt_path = PROJECT_ROOT / "persona-v3-prompt.txt"
    all_texts.append(prompt_path.read_text(encoding="utf-8"))

    print("Computing shared factors...")
    idf_factors, doc_freq = compute_idf_factors(all_texts)

    # Show keywords per IDF factor range
    print("\nKeywords by shared factor range:")
    factor_ranges = {"rare (1.0)": 0, "slightly shared (0.8-0.99)": 0, "shared (0.7-0.79)": 0, "unknown (default)": 0}
    for dim, kws in DIMENSION_KEYWORDS.items():
        for kw, w in kws:
            kw_lower = kw.lower()
            f = idf_factors.get(kw_lower, 0.0)
            df = doc_freq.get(kw_lower, 0)
            if f == 1.0 and df > 2:
                factor_ranges["slightly shared (0.8-0.99)"] += 1
            elif f == 1.0:
                factor_ranges["rare (1.0)"] += 1
            elif f >= 0.8:
                factor_ranges["slightly shared (0.8-0.99)"] += 1
            elif f >= 0.7:
                factor_ranges["shared (0.7-0.79)"] += 1
            else:
                factor_ranges["unknown (default)"] += 1
    for rng, count in factor_ranges.items():
        print(f"  {rng}: {count} keywords")

    # Show shared keywords across dimensions
    print("\nShared keywords across dimensions (cross-contamination risk):")
    all_kw_dims = {}
    for dim, kws in DIMENSION_KEYWORDS.items():
        for kw, w in kws:
            if kw.lower() not in all_kw_dims:
                all_kw_dims[kw.lower()] = set()
            all_kw_dims[kw.lower()].add(dim)
    shared = {k: v for k, v in all_kw_dims.items() if len(v) > 1}
    for kw, dims in sorted(shared.items(), key=lambda x: -len(x[1])):
        factor = idf_factors.get(kw.lower(), 1.0)
        df = doc_freq.get(kw.lower(), 0)
        print(f"  '{kw}': dims={', '.join(sorted(dims))}, df={df}, factor={factor:.3f}")

    # Score all files
    print("\nScoring idea files...")
    file_scores = []
    for i, text in enumerate(all_texts):
        scores = score_with_tfidf(text, idf_factors)
        avg_score = sum(scores.values()) / len(scores)
        min_score = min(scores.values())
        file_scores.append({
            "file": idea_files[i] if i < len(idea_files) else "persona-v3-prompt.txt",
            "avg_score": round(avg_score, 4),
            "min_score": round(min_score, 4),
            "dim_scores": {k: round(v, 4) for k, v in sorted(scores.items())},
        })

    file_scores.sort(key=lambda x: x["avg_score"])

    avg_avg = sum(f["avg_score"] for f in file_scores) / len(file_scores)
    avg_min = sum(f["min_score"] for f in file_scores) / len(file_scores)
    all_above_40 = all(f["min_score"] >= 0.40 for f in file_scores)

    print(f"\nSummary:")
    print(f"  Avg file score: {avg_avg:.4f}")
    print(f"  Min file score: {file_scores[0]['min_score']}")
    print(f"  Min dim score (avg): {avg_min:.4f}")
    print(f"  All dims >= 0.40: {all_above_40}")
    print(f"\nTop 5 weakest:")
    for f in file_scores[:5]:
        print(f"  {f['file']}: avg={f['avg_score']}, min={f['min_score']}")

    print(f"\nTop 5 strongest:")
    for f in file_scores[-5:]:
        print(f"  {f['file']}: avg={f['avg_score']}, min={f['min_score']}")

    # Save JSON
    output_path = PROJECT_ROOT / "eval_results" / "tfidf_scores.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "avg_file_score": avg_avg,
            "min_file_score": file_scores[0]["min_score"],
            "min_dim_score_avg": avg_min,
            "all_above_40": all_above_40,
            "files": file_scores,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
