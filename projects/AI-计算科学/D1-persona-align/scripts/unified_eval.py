#!/usr/bin/env python3
"""persona-v3 统一评估管道 — 一次运行 gap_filler + chameleon + trajectory。

用法:
    python3 unified_eval.py --scan          # 扫描所有 idea 文件
    python3 unified_eval.py --scan --top N  # 只评估最弱/最强 N 个文件
    python3 unified_eval.py --prompt        # 评估 persona-v3-prompt.txt
"""

import argparse
import json
import math
import sys
from pathlib import Path

# Resolve all paths relative to the script's parent directory (project root)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Import from evaluation tools
try:
    from persona_keywords import compute_dimension_scores, DIMENSION_KEYWORDS, TOTAL_WEIGHTS
except ImportError:
    print("ERROR: persona_keywords.py not found", file=sys.stderr)
    sys.exit(1)

# Semantic evaluation (optional)
try:
    from semantic_alignment_checker import semantic_alignment_score, compute_concept_scores
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

# unified_eval 不依赖 chameleon_collapse_detector 的 extract_features
# (chameleon 指标由 compute_chameleon_metrics 独立计算)


def score_file(filepath, ref_text=None, use_semantic=False):
    """对单个文件做完整评估。"""
    text = filepath.read_text(encoding='utf-8')

    # 1. gap_filler 评估 (关键词匹配)
    scores = compute_dimension_scores(text)

    # 2. 每个维度的匹配分数
    keyword_matches = {dim: sum(1 for kw, _ in kws if kw.lower() in text.lower())
                       / len(kws) for dim, kws in DIMENSION_KEYWORDS.items()}

    # 3. 维度签名
    sig = compute_dimension_scores(text)

    # 4. 表面特征 — char bigram count (用于 chameleon, 内联计算)
    bigram_count = len([text[i:i+2] for i in range(len(text)-1)]) if len(text) > 1 else 0

    result = {
        'path': str(filepath),
        'filename': filepath.name,
        'length': len(text),
        'keyword_scores': scores,
        'keyword_match_ratios': keyword_matches,
        'avg_keyword_score': round(sum(scores.values()) / 6, 4),
        'min_keyword_score': round(min(scores.values()), 4),
        'bigram_features': bigram_count,
    }

    # 5. 语义评估 (可选)
    if use_semantic and HAS_SEMANTIC and ref_text:
        sem_result = semantic_alignment_score(ref_text, text)
        result['semantic_scores'] = sem_result

    return result


def compute_chameleon_metrics(files_data):
    """从所有文件的关键词签名计算 chameleon collapse 指标。
    聚合文件级分数 → 每个维度的平均 keyword signature → 计算维度间相似度。
    """
    dim_names = list(DIMENSION_KEYWORDS.keys())

    # 聚合: 计算每个维度在所有文件上的平均分数
    dim_aggregate = {d: [] for d in dim_names}
    for fd in files_data:
        for d in dim_names:
            dim_aggregate[d].append(fd['keyword_scores'].get(d, 0.0))

    # 平均
    avg_sigs = {d: sum(v) / len(v) for d, v in dim_aggregate.items()}

    # 计算维度间 cosine similarity
    # 修复: 之前的 vec_i == vec_j (bug), 现在改为比较维度分数向量
    similarities = []
    for i in range(len(dim_names)):
        for j in range(i + 1, len(dim_names)):
            dim_i = dim_names[i]
            dim_j = dim_names[j]
            # vec_i: 维度 i 在所有文件上的分数向量
            vec_i = dim_aggregate[dim_i]
            # vec_j: 维度 j 在所有文件上的分数向量
            vec_j = dim_aggregate[dim_j]
            dot = sum(a * b for a, b in zip(vec_i, vec_j))
            norm_i = math.sqrt(sum(a * a for a in vec_i))
            norm_j = math.sqrt(sum(b * b for b in vec_j))
            if norm_i > 1e-10 and norm_j > 1e-10:
                sim = dot / (norm_i * norm_j)
            else:
                sim = 0.0
            similarities.append(sim)

    if not similarities:
        return None

    return {
        'avg_similarity': round(sum(similarities) / len(similarities), 4),
        'min_similarity': round(min(similarities), 4),
        'max_similarity': round(max(similarities), 4),
        'collapse_detected': any(s > 0.7 for s in similarities),
        'dim_aggregate_sigs': {k: round(v, 4) for k, v in avg_sigs.items()},
    }


def compute_trajectory_metrics(files_data):
    """从文件评估计算 trajectory 指标。"""
    if len(files_data) < 2:
        return None

    # 假设文件按某种顺序排列构成"对话轨迹"
    # 用 keyword match ratio 计算 persona 强度
    intensities = []
    for fd in files_data:
        sig = fd['keyword_scores']
        # 取最高分作为 persona 强度
        intensity = max(sig.values())
        intensities.append(intensity)

    # 方向对齐
    directions = []
    for i in range(1, len(intensities)):
        diff = intensities[i] - intensities[i - 1]
        if abs(diff) < 1e-10:
            directions.append(0.0)
        else:
            directions.append(1.0 if diff > 0 else -1.0)

    consistent = sum(1 for i in range(1, len(directions)) if directions[i] == directions[i - 1])
    directional_alignment = consistent / max(len(directions) - 1, 1)

    # 稳定性
    mean_i = sum(intensities) / len(intensities)
    variance = sum((x - mean_i) ** 2 for x in intensities) / len(intensities)
    max_i = max(intensities) if intensities else 1.0
    stability = 1.0 - min(variance / max(max_i ** 2, 1e-10), 1.0)

    return {
        'directional_alignment': round(directional_alignment, 4),
        'cumulative_impact': round(sum(intensities) / len(intensities), 4),
        'stability': round(stability, 4),
        'intensity_std': round(math.sqrt(variance), 4),
        'intensity_range': round(max(intensities) - min(intensities), 4),
    }


def pearson_correlation(xs, ys):
    """计算 Pearson 相关系数。"""
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x < 1e-10 or std_y < 1e-10:
        return 0.0
    return cov / (std_x * std_y)


def main():
    parser = argparse.ArgumentParser(description='persona-v3 统一评估管道')
    parser.add_argument('--scan', action='store_true', help='扫描 memory/idea-*.md')
    parser.add_argument('--prompt', action='store_true', help='评估 persona-v3-prompt.txt')
    parser.add_argument('--top', type=int, help='只评估最弱/最强 N 个文件')
    parser.add_argument('--output', default=str(PROJECT_ROOT / 'eval_results' / 'unified_report.json'), help='输出路径')
    parser.add_argument('--semantic', action='store_true',
                        help='同时运行语义评估 (需 semantic_alignment_checker.py)')
    args = parser.parse_args()

    print("=" * 60)
    print("persona-v3 统一评估管道")
    print("=" * 60)

    # 语义评估引用
    ref_text = None
    if args.semantic:
        if not HAS_SEMANTIC:
            print("  [!] semantic_alignment_checker.py 未找到, 跳过语义评估", file=sys.stderr)
        else:
            prompt_path = PROJECT_ROOT / 'persona-v3-prompt.txt'
            if prompt_path.exists():
                ref_text = prompt_path.read_text(encoding='utf-8')
            else:
                print("  [!] 未找到 persona-v3-prompt.txt, 跳过语义评估", file=sys.stderr)

    # 收集文件
    files = []
    if args.scan:
        ideas_dir = PROJECT_ROOT / 'memory'
        files = sorted(ideas_dir.glob('idea-*.md'))
        print(f"\n扫描 {len(files)} 个 idea 文件")
    elif args.prompt:
        prompt_path = PROJECT_ROOT / 'persona-v3-prompt.txt'
        files = [prompt_path]
        print("\n评估 persona-v3-prompt.txt")
    else:
        print("用法: --scan (扫描 idea 文件) 或 --prompt (评估 prompt)")
        sys.exit(1)

    print(f"  语义评估: {'ON' if args.semantic else 'OFF'}")
    if args.semantic:
        print(f"  引用文件: persona-v3-prompt.txt ({len(ref_text)} chars)")

    if args.top:
        # 先评估所有文件
        all_data = []
        for f in files:
            all_data.append(score_file(f, ref_text=ref_text, use_semantic=args.semantic))

        # 按平均 keyword score 排序
        all_data.sort(key=lambda x: x['avg_keyword_score'])

        # 取最弱 N 个 + 最强 N 个
        if len(all_data) > args.top * 2:
            top_files = all_data[:args.top] + all_data[-args.top:]
            filtered_files = top_files
            print(f"  Top-{args.top} 最弱 + Top-{args.top} 最强 (共 {len(top_files)} 文件)")
        else:
            filtered_files = all_data
            print(f"  文件数不足 {args.top*2}, 全部 {len(all_data)} 文件")

        files_data = filtered_files
    else:
        files_data = [score_file(f, ref_text=ref_text, use_semantic=args.semantic) for f in files]
        print(f"  评估 {len(files_data)} 文件")

    # 评估报告
    results = {
        'files': [],
        'summary': {},
        'chameleon': {},
        'trajectory': {},
    }

    # 文件级评估
    has_semantic_data = any('semantic_scores' in fd for fd in files_data)
    for fd in files_data:
        file_result = {
            'path': fd['filename'],
            'length': fd['length'],
            'avg_score': fd['avg_keyword_score'],
            'min_score': fd['min_keyword_score'],
            'keyword_scores': fd['keyword_scores'],
            'keyword_match_ratios': fd['keyword_match_ratios'],
        }
        if 'semantic_scores' in fd:
            file_result['semantic_scores'] = fd['semantic_scores']
        results['files'].append(file_result)

    # 汇总统计
    avg_scores = [fd['avg_keyword_score'] for fd in files_data]
    min_scores = [fd['min_keyword_score'] for fd in files_data]
    results['summary'] = {
        'num_files': len(files_data),
        'avg_avg_score': round(sum(avg_scores) / len(avg_scores), 4) if avg_scores else 0,
        'min_avg_score': round(min(avg_scores), 4) if avg_scores else 0,
        'max_avg_score': round(max(avg_scores), 4) if avg_scores else 0,
        'avg_min_score': round(sum(min_scores) / len(min_scores), 4) if min_scores else 0,
        'all_pass_040': all(s >= 0.40 for s in min_scores) if min_scores else False,
    }

    # Chameleon collapse (跨维度相似度)
    chameleon = compute_chameleon_metrics(files_data)
    results['chameleon'] = chameleon or {'error': '文件数不足'}

    # Trajectory metrics
    trajectory = compute_trajectory_metrics(files_data)
    results['trajectory'] = trajectory or {'error': '文件数不足'}

    # 输出
    print(f"\n{'=' * 60}")
    print(f"评估结果汇总")
    print(f"{'=' * 60}")
    print(f"\n文件级: 平均 {results['summary']['avg_avg_score']}, "
          f"最小 {results['summary']['min_avg_score']}, "
          f"最大 {results['summary']['max_avg_score']}")
    print(f"维度最小分: {results['summary']['avg_min_score']}")
    print(f"所有维度 >= 0.40: {results['summary']['all_pass_040']}")

    print(f"\nChameleon Collapse:")
    if results['chameleon'].get('collapse_detected'):
        print(f"  [!] 检测到 collapse — 维度间相似度过高")
    else:
        print(f"  [OK] 未检测到 collapse")
    print(f"  平均相似度: {results['chameleon'].get('avg_similarity', 'N/A')}")
    print(f"  最大相似度: {results['chameleon'].get('max_similarity', 'N/A')}")

    if results['trajectory']:
        print(f"\nTrajectory:")
        print(f"  方向对齐: {results['trajectory'].get('directional_alignment', 'N/A')}")
        print(f"  累积影响: {results['trajectory'].get('cumulative_impact', 'N/A')}")
        print(f"  稳定性: {results['trajectory'].get('stability', 'N/A')}")
        print(f"  强度标准差: {results['trajectory'].get('intensity_std', 'N/A')}")

    # 语义评估对比
    if has_semantic_data:
        keyword_scores = [fd['avg_keyword_score'] for fd in files_data]
        semantic_scores = [fd['semantic_scores']['overall_score']
                          for fd in files_data if 'semantic_scores' in fd]

        if keyword_scores and semantic_scores:
            n = min(len(keyword_scores), len(semantic_scores))
            keyword_scores = keyword_scores[:n]
            semantic_scores = semantic_scores[:n]

            corr = pearson_correlation(keyword_scores, semantic_scores)

            results['semantic_comparison'] = {
                'pearson_correlation': round(corr, 4),
                'num_pairs': n,
                'keyword_avg': round(sum(keyword_scores) / n, 4),
                'semantic_avg': round(sum(semantic_scores) / n, 4),
            }

            print(f"\n语义 vs 关键词 对比:")
            print(f"  Pearson 相关系数: {corr:.4f}")
            print(f"  关键词平均: {sum(keyword_scores)/n:.4f}")
            print(f"  语义平均:   {sum(semantic_scores)/n:.4f}")
            if corr > 0.8:
                print(f"  [OK] 高度相关 — 关键词评估与语义评估一致")
            elif corr > 0.5:
                print(f"  [!] 中度相关 — 部分不一致")
            else:
                print(f"  [!] 低相关 — 两种评估方式显著不一致")
                print(f"       (可能检测到假阴性)")

    # 保存
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n结果保存到: {output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
