#!/usr/bin/env python3
"""persona-v3 跨维度关键词正交化评分器

只对真正跨维度共享的关键词应用降权，不对高频中文词降权。
跨维度关键词: 同一个 keyword string 出现在多个维度定义中。
"""

import math
import sys
import json
import glob
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from persona_keywords import DIMENSION_KEYWORDS, TOTAL_WEIGHTS


def find_cross_dim_keywords():
    """找出跨维度共享的关键词。"""
    kw_to_dims = defaultdict(set)
    kw_to_weight = {}

    for dim, kws in DIMENSION_KEYWORDS.items():
        for kw, w in kws:
            kw_lower = kw.lower()
            kw_to_dims[kw_lower].add(dim)
            kw_to_weight[kw_lower] = w

    shared = {k: v for k, v in kw_to_dims.items() if len(v) > 1}
    return shared, kw_to_dims, kw_to_weight


def score_with_shared_penalty(text, shared_keywords):
    """原始加权匹配 + 对共享关键词应用降权。

    共享关键词 (如 信噪比 出现在 感知+精度) 在分子中只贡献 80% 权重。
    非共享关键词正常权重。
    total_weight 不变 → 总体分数不受影响。
    """
    text_lower = text.lower()
    scores = {}

    for dim, kws in DIMENSION_KEYWORDS.items():
        matched_weight = 0.0
        total_weight = TOTAL_WEIGHTS[dim]
        for kw, w in kws:
            kw_lower = kw.lower()
            if kw_lower in shared_keywords:
                # 共享关键词: 降权到 80%
                matched_weight += w * 0.8
            else:
                matched_weight += w
            # 注意: 上面的逻辑是假设 matched 了。实际应该先检查是否在 text 中。
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0.0

    return scores


def score_correct(text, shared_keywords):
    """正确的评分逻辑: 先检查 text 是否包含关键词，再根据是否共享决定权重。"""
    text_lower = text.lower()
    scores = {}

    for dim, kws in DIMENSION_KEYWORDS.items():
        matched_weight = 0.0
        total_weight = TOTAL_WEIGHTS[dim]
        for kw, w in kws:
            kw_lower = kw.lower()
            if kw_lower not in text_lower:
                continue  # 关键词未匹配，贡献 0
            if kw_lower in shared_keywords:
                matched_weight += w * 0.8  # 共享关键词降权
            else:
                matched_weight += w  # 非共享关键词正常权重
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0.0

    return scores


def main():
    print("=" * 60)
    print("Cross-Dimensional Orthogonalization — persona-v3")
    print("=" * 60)

    shared, kw_dims, kw_weight = find_cross_dim_keywords()
    print(f"\nCross-dimensional keywords found: {len(shared)}")
    for kw, dims in sorted(shared.items(), key=lambda x: -len(x[1])):
        print(f"  '{kw}': {', '.join(sorted(dims))}")

    # Load files
    idea_files = sorted(glob.glob(str(PROJECT_ROOT / "memory" / "idea-*.md")))
    prompt_path = PROJECT_ROOT / "persona-v3-prompt.txt"

    # Score prompt with original and orthogonalized
    prompt_text = prompt_path.read_text(encoding="utf-8")
    scores_orig_prompt = score_correct(prompt_text, {})
    scores_ortho_prompt = score_correct(prompt_text, set(shared.keys()))

    print(f"\nPrompt comparison (original vs orthogonalized):")
    for dim in DIMENSION_KEYWORDS:
        orig = scores_orig_prompt[dim]
        ortho = scores_ortho_prompt[dim]
        print(f"  {dim}: {orig:.4f} → {ortho:.4f} (Δ={ortho-orig:+.4f})")

    # Score idea files
    print(f"\nScoring {len(idea_files)} idea files...")
    file_scores_orig = []
    file_scores_ortho = []

    for fp in idea_files:
        text = Path(fp).read_text(encoding="utf-8")
        s_orig = score_correct(text, {})
        s_ortho = score_correct(text, set(shared.keys()))
        file_scores_orig.append({
            "file": Path(fp).name,
            "avg": sum(s_orig.values()) / len(s_orig),
            "min": min(s_orig.values()),
            "dim": s_orig,
        })
        file_scores_ortho.append({
            "file": Path(fp).name,
            "avg": sum(s_ortho.values()) / len(s_ortho),
            "min": min(s_ortho.values()),
            "dim": s_ortho,
        })

    file_scores_orig.sort(key=lambda x: x["avg"])
    file_scores_ortho.sort(key=lambda x: x["avg"])

    def summarize(scores, label):
        avg_avg = sum(f["avg"] for f in scores) / len(scores)
        avg_min = sum(f["min"] for f in scores) / len(scores)
        min_min = min(f["min"] for f in scores)
        all_above = all(f["min"] >= 0.40 for f in scores)
        print(f"\n  {label}:")
        print(f"    Avg file score: {avg_avg:.4f}")
        print(f"    Min file score: {min_min}")
        print(f"    Min dim (avg): {avg_min:.4f}")
        print(f"    All dims >= 0.40: {all_above}")
        return avg_avg, min_min, avg_min, all_above

    print("=" * 60)
    print("Results")
    print("=" * 60)
    orig_summary = summarize(file_scores_orig, "ORIGINAL")
    ortho_summary = summarize(file_scores_ortho, "ORTHOGONALIZED")

    print(f"\nComparison (orig vs ortho):")
    print(f"  Avg file score: {orig_summary[0]:.4f} → {ortho_summary[0]:.4f} (Δ={ortho_summary[0]-orig_summary[0]:+.4f})")
    print(f"  Min file score: {orig_summary[1]:.4f} → {ortho_summary[1]:.4f} (Δ={ortho_summary[1]-orig_summary[1]:+.4f})")
    print(f"  Min dim avg: {orig_summary[2]:.4f} → {ortho_summary[2]:.4f}")
    print(f"  All >= 0.40: {orig_summary[3]} → {ortho_summary[3]}")

    # Save
    output_path = PROJECT_ROOT / "eval_results" / "cross_dim_orthogonalization.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "cross_dim_keywords": {k: sorted(list(v)) for k, v in shared.items()},
            "original": {
                "avg_file_score": round(orig_summary[0], 4),
                "min_file_score": round(orig_summary[1], 4),
                "all_above_40": orig_summary[3],
                "top5_weakest": [{"file": f["file"], "avg": round(f["avg"], 4), "min": round(f["min"], 4)} for f in file_scores_orig[:5]],
            },
            "orthogonalized": {
                "avg_file_score": round(ortho_summary[0], 4),
                "min_file_score": round(ortho_summary[1], 4),
                "all_above_40": ortho_summary[3],
                "top5_weakest": [{"file": f["file"], "avg": round(f["avg"], 4), "min": round(f["min"], 4)} for f in file_scores_ortho[:5]],
            },
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
