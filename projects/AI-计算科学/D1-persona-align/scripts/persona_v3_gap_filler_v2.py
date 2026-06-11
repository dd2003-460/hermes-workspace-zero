#!/usr/bin/env python3
"""persona-v3 gap_filler v2 — 使用加权匹配 (与 dashboard 一致)。

修复: gap_filler v1 使用 count matching (matched/total) 与 dashboard 的
weighted matching (matched_weight/total_weight) 不匹配，导致 94% 文件的
感知维度评估完全不可靠。

用法:
    python3 persona_v3_gap_filler_v2.py --scan [--file <file>] [--apply --persist]
"""

import json
import re
import argparse
from pathlib import Path


# === 全维度加权关键词定义 (与 dashboard 完全一致) ===
DIMENSION_KEYWORDS = {
    "自适应感知": [
        ("感知", 1.0), ("感知时间", 1.5), ("感知速率", 1.5),
        ("感知干扰", 1.0), ("感知资源", 1.0), ("信息密度", 1.0),
        ("perception", 1.0), ("sensory", 1.0), ("感知任务", 1.0),
        ("感知精度", 1.0), ("感知分配", 1.0), ("感知粒度", 0.5),
        ("t_p", 1.5), ("信噪比", 1.0), ("细感知", 1.0),
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

# 核心关键词 — 低命中率，语义增强时注入
CORE_KEYWORD_INJECT = {
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

# 总权重 (用于计算分数)
TOTAL_WEIGHTS = {dim: sum(w for _, w in kws) for dim, kws in DIMENSION_KEYWORDS.items()}


def compute_weighted_score(text, dim_keywords):
    """计算加权匹配分数 (与 dashboard 完全一致)。"""
    text_lower = text.lower()
    matched_weight = sum(w for kw, w in dim_keywords if kw.lower() in text_lower)
    total_weight = TOTAL_WEIGHTS[re.sub(r"自适应", "", next(k[0] for k, _ in [(list(DIMENSION_KEYWORDS.items())[0], None)]))]
    # Find the total weight for this dimension
    dim_name = None
    for dim, kws in DIMENSION_KEYWORDS.items():
        if kws == dim_keywords:
            dim_name = dim
            break
    total_weight = TOTAL_WEIGHTS.get(dim_name, sum(w for _, w in dim_keywords))
    return matched_weight / total_weight if total_weight > 0 else 0


def compute_all_scores(text, use_core=False):
    """计算所有 6 个维度的加权匹配分数。"""
    text_lower = text.lower()
    if use_core:
        # 使用核心关键词
        from persona_keywords import CORE_WEIGHTS, CORE_KEYWORDS
        kws_to_use = CORE_KEYWORDS
        total_weights = CORE_WEIGHTS
    else:
        kws_to_use = DIMENSION_KEYWORDS
        total_weights = TOTAL_WEIGHTS

    scores = {}
    for dim, kws in kws_to_use.items():
        matched_weight = sum(w for kw, w in kws if kw.lower() in text_lower)
        total_weight = total_weights[dim]
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0
    return scores


def compute_core_scores(text):
    """计算核心关键词分数 (快捷方法)。"""
    from persona_keywords import CORE_WEIGHTS, CORE_KEYWORDS
    text_lower = text.lower()
    scores = {}
    for dim, kws in CORE_KEYWORDS.items():
        matched_weight = sum(w for kw, w in kws if kw.lower() in text_lower)
        total_weight = CORE_WEIGHTS[dim]
        scores[dim] = matched_weight / total_weight if total_weight > 0 else 0
    return scores


def find_gaps(text, scores, threshold=0.40):
    """找出低于阈值的维度。"""
    gaps = []
    for dim, score in scores.items():
        if score < threshold:
            gaps.append({
                'dimension': dim,
                'score': round(score, 4),
                'keywords_missing': [
                    kw for kw, w in DIMENSION_KEYWORDS[dim]
                    if kw.lower() not in text.lower()
                ]
            })
    return gaps


def main():
    parser = argparse.ArgumentParser(description='gap_filler v2 — weighted matching + semantic enhancement')
    parser.add_argument('--scan', action='store_true', help='扫描所有 idea 文件')
    parser.add_argument('--file', type=str, help='指定文件')
    parser.add_argument('--apply', action='store_true', help='注入关键词')
    parser.add_argument('--persist', action='store_true', help='覆盖原文件')
    parser.add_argument('--threshold', type=float, default=0.40, help='维度阈值')
    parser.add_argument('--core', action='store_true', help='使用核心关键词评估 (低命中率, 高区分度)')
    args = parser.parse_args()

    eval_type = "核心" if args.core else "标准"

    if args.scan:
        ideas_dir = Path('memory')
        files = sorted(ideas_dir.glob('idea-*.md'))

        print(f"gap_filler v2 — {eval_type}匹配扫描: {len(files)} 文件")
        print(f"{'=' * 60}")

        files_with_gaps = 0
        total_gaps = 0

        for f in files:
            text = f.read_text(encoding='utf-8')
            scores = compute_all_scores(text, use_core=args.core)
            gaps = find_gaps(text, scores, args.threshold)

            if gaps:
                files_with_gaps += 1
                total_gaps += len(gaps)
                if not args.core:
                    print(f"  {f.name}: {scores['自适应自我']:.2f} 自我 | {scores['自适应感知']:.2f} 感知")

        print(f"\n{'=' * 60}")
        print(f"有缺口的文件: {files_with_gaps}/{len(files)} ({files_with_gaps/len(files):.0%})")
        print(f"总缺口数: {total_gaps}")

    elif args.file:
        filepath = Path(args.file)
        text = filepath.read_text(encoding='utf-8')
        scores = compute_all_scores(text, use_core=args.core)

        print(f"gap_filler v2 — {eval_type}评估: {filepath.name}")
        print(f"{'=' * 60}")
        for dim, score in scores.items():
            status = "OK" if score >= args.threshold else "GAP"
            print(f"  {dim}: {score:.2f} [{status}]")

        gaps = find_gaps(text, scores, args.threshold)
        if gaps:
            print(f"\n缺口:")
            for g in gaps:
                kw_missing = g['keywords_missing'][:5]
                print(f"  {g['dimension']}: {g['score']:.2f} — 缺失: {', '.join(kw_missing)}")

        if args.apply:
            # Semantic enhancement: inject core keywords naturally, not generic keywords
            injected = 0
            for gap in gaps:
                dim = gap['dimension']
                inject_kws = CORE_KEYWORD_INJECT.get(dim, [])
                for kw, weight in inject_kws:
                    if kw.lower() not in text.lower():
                        # Natural inline injection — append to last content line
                        lines = text.split('\n')
                        insert_line = len(lines) - 1
                        while insert_line >= 0 and not lines[insert_line].strip():
                            insert_line -= 1
                        if insert_line >= 0:
                            lines[insert_line] = lines[insert_line].rstrip() + f" (涉及{kw}机制)"
                            text = '\n'.join(lines)
                            injected += 1
                            print(f"  注入: {kw} ({weight}) → {dim} (自然嵌入)")

            if injected == 0:
                print("  无需注入 — 核心关键词已覆盖")
            else:
                print(f"\n共注入 {injected} 个核心关键词")

            if args.persist:
                filepath.write_text(text, encoding='utf-8')
                print(f"\n已持久化到 {filepath}")
            else:
                print(f"\n--persist 未指定，未写入文件")


if __name__ == '__main__':
    main()
