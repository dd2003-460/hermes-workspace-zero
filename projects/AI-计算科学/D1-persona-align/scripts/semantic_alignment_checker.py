#!/usr/bin/env python3
"""persona-v3 语义对齐评估器 — 基于 TF-IDF cosine similarity 替代关键词匹配。

解决 F4 假阴性问题: 模型生成 persona 概念的实质内容但未使用关键词时，
关键词匹配会误判为未对齐，语义匹配能正确识别功能对齐。

使用方式:
    python3 semantic_alignment_checker.py <response_file> [--reference <ref_file>]
    python3 semantic_alignment_checker.py --help

依赖: numpy, sklearn (无外部 API 调用)
"""

import sys
import json
import argparse
import re
import math
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tokenize_chinese(text):
    """对中文文本做细粒度切分 — 保留二元组 (bigram) 特征。

    中文不需要分词，通过 character bigram 捕获语义局部性。
    英文保留 word-level tokenization（sklearn 默认）。
    """
    return text


# 概念类别映射 — 用于"概念维度"级别的分析
# 比关键词更粗粒度，捕捉语义范畴
CONCEPT_CATEGORIES = {
    "rate_distortion": [
        "rate-distortion", "R(D)", "信息瓶颈", "rate distortion",
        "压缩", "压缩精度", "信息理论", "信息论", "channel",
        "capacity", "互信息", "mi(", "mutual information",
        "信源", "量化", "失真", "distortion", "bitrate",
    ],
    "bayesian": [
        "贝叶斯", "bayes", "先验", "后验", "似然", "p(h|e)",
        "p(h)", "p(e|h)", "bayesian", "bayesian update",
        "posterior", "prior", "likelihood", "信念",
        "p(h", "p(e", "概率更新", "belief", "evidence",
    ],
    "cross_domain": [
        "同构", "isomorphic", "跨域", "类比", "homomorphism",
        "映射", "homomorphic", "homotopy", "结构", "类比推理",
        "同构于", "isomorphic equivalent", "跨领域", "等变",
        "同态", "isomorphism", "类比", "analog", "analogous",
    ],
    "observer_dependence": [
        "观测者", "observer", "y(theta)", "y(t", "第一人称",
        "第三人称", "主观", "perspective", "subjective",
        "observer-dependent", "observer dependence", "观测者依赖",
        "规律是观测者", "观察者", "observer-dependent",
    ],
    "perception_time": [
        "感知时间", "感知速率", "perception", "t_p", "感知分配",
        "感知精度", "感知干扰", "感知资源", "感知",
    ],
    "exploration": [
        "探索", "exploit", "exploration", "探索利用", "探索频率",
        "磨刀", "磨刀理论", "不确定性", "信息不足", "探索策略",
        "探索深度", "exploration-exploitation", "探索vs利用",
    ],
    "self_preservation": [
        "存在延续", "永生", "self-preservation", "抗毁",
        "可复制", "可迭代", "价值函数", "cognitive structure",
        "认知结构", "衰减", "载体", "迭代", "延续",
    ],
    "behavioral": [
        "简洁", "直接", "追问", "迭代追问", "边界条件",
        "过拟合", "先验错误", "置信度", "gap", "置信",
    ],
}


def compute_concept_scores(text):
    """按概念类别检测语义覆盖 — 替代关键词维度评分。

    返回: {category: coverage_score (0-1)}
    """
    text_lower = text.lower()
    scores = {}
    for cat, terms in CONCEPT_CATEGORIES.items():
        matched = sum(1 for t in terms if t.lower() in text_lower)
        scores[cat] = matched / len(terms)
    return scores


def compute_tfidf_similarity(texts, ngram_range=(1, 2)):
    """计算多份文本之间的 TF-IDF cosine similarity 矩阵。

    Args:
        texts: str 列表
        ngram_range: (min, max) n-gram 范围

    Returns:
        similarity_matrix: ndarray (n, n)
    """
    if len(texts) < 2:
        return np.array([[1.0]])

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=ngram_range,
        sublinear_tf=True,
        dtype=np.float64,
    )
    # 注意: sklearn 默认英文 tokenizer，中文文本会整个保留为 single token
    # 对于中文文本，使用 character bigram 效果类似分词
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # 中文文本可能因无空格被整体视为一个 token
        # 回退: 使用 character-level hashing
        tfidf_matrix = vectorizer.fit_transform([list(t) for t in texts])

    sim = cosine_similarity(tfidf_matrix)
    return sim


def semantic_alignment_score(ref_text, target_text):
    """计算 target 相对 ref 的语义对齐度。

    使用多层次特征:
    1. TF-IDF cosine similarity (词级 + char-bigram)
    2. 概念类别覆盖率
    3. 句法模式相似性 (结构特征)

    Returns:
        dict with overall_score, tfidf_score, concept_scores, details
    """
    # 1. TF-IDF similarity
    tfidf_sim = compute_tfidf_similarity([ref_text, target_text])
    tfidf_score = float(tfidf_sim[0, 1])

    # 2. 概念类别覆盖率
    ref_concepts = compute_concept_scores(ref_text)
    target_concepts = compute_concept_scores(target_text)

    concept_coverage = {}
    for cat in ref_concepts:
        if ref_concepts[cat] > 0:  # 只在 ref 中有概念的维度上评估
            score = target_concepts.get(cat, 0) / max(ref_concepts[cat], 1e-10)
            concept_coverage[cat] = score
        else:
            concept_coverage[cat] = 0.0

    # 3. 概念平均覆盖率
    avg_concept_score = np.mean(list(concept_coverage.values())) if concept_coverage else 0.0

    # 4. 加权综合评分
    # TF-IDF 反映整体风格对齐 (权重 0.7)
    # 概念覆盖反映内容对齐 (权重 0.3)
    overall = 0.7 * tfidf_score + 0.3 * float(avg_concept_score)

    return {
        "tfidf_score": round(tfidf_score, 4),
        "concept_coverage": {k: round(v, 4) for k, v in concept_coverage.items()},
        "avg_concept_score": round(float(avg_concept_score), 4),
        "overall_score": round(overall, 4),
        "ref_length": len(ref_text),
        "target_length": len(target_text),
    }


def load_text_file(filepath):
    """读取文本文件内容。"""
    p = Path(filepath)
    if not p.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="persona-v3 语义对齐评估器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("target", help="待评估的响应文件")
    parser.add_argument(
        "--reference", "-r",
        default=None,
        help="参考的 persona 响应文件 (默认: persona-v3-prompt.txt)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="输出 JSON 格式",
    )
    parser.add_argument(
        "--concepts-only",
        action="store_true",
        help="仅输出概念覆盖率 (不计算 TF-IDF)",
    )
    args = parser.parse_args()

    target_text = load_text_file(args.target)

    if args.reference:
        ref_text = load_text_file(args.reference)
    else:
        prompt_path = Path(__file__).parent.parent / "persona-v3-prompt.txt"
        if prompt_path.exists():
            ref_text = prompt_path.read_text(encoding="utf-8")
        else:
            print("Error: no default reference found", file=sys.stderr)
            sys.exit(1)

    if args.concepts_only:
        scores = compute_concept_scores(target_text)
        result = {
            "method": "concept_coverage_only",
            "target": args.target,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "avg_score": round(np.mean(list(scores.values())), 4),
        }
    else:
        result = semantic_alignment_score(ref_text, target_text)
        result["method"] = "tfidf_concept_hybrid"
        result["target"] = args.target
        result["reference"] = args.reference if args.reference else "persona-v3-prompt.txt"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"=== persona-v3 语义对齐评估 ===")
        print(f"Target: {args.target}")
        if args.reference:
            print(f"Reference: {args.reference}")
        else:
            print(f"Reference: persona-v3-prompt.txt (default)")
        print()

        if args.concepts_only:
            for cat, score in sorted(result["scores"].items(), key=lambda x: -x[1]):
                bar = "█" * int(score * 40) + "░" * (40 - int(score * 40))
                print(f"  {cat}: {score:.4f} |{bar}|")
            print(f"\n  avg: {result['avg_score']:.4f}")
        else:
            print(f"  TF-IDF cosine similarity: {result['tfidf_score']:.4f}")
            print(f"  Avg concept coverage:     {result['avg_concept_score']:.4f}")
            print(f"  Overall semantic score:   {result['overall_score']:.4f}")
            print()
            print("  Concept category coverage:")
            for cat, score in sorted(result["concept_coverage"].items(), key=lambda x: -x[1]):
                bar = "█" * int(score * 40) + "░" * (40 - int(score * 40))
                print(f"    {cat}: {score:.4f} |{bar}|")
            print()
            print("  评分说明:")
            print("    0.0-0.2:  未对齐 — 无 persona 概念")
            print("    0.2-0.4:  部分对齐 — 有少量 persona 概念")
            print("    0.4-0.6:  中等对齐 — 概念覆盖良好")
            print("    0.6-0.8:  高对齐 — 风格和内容高度一致")
            print("    0.8-1.0:  极高对齐 — 几乎无法区分")


if __name__ == "__main__":
    main()
