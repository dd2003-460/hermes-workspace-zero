#!/usr/bin/env python3
"""persona-v3 测试时优化原型 (Test-Time Optimization Prototype)

灵感来源:
- MATO (arXiv:2605.25342): 推理时通过可调乘数 (adjustable multipliers) 操纵目标优先级
- UniScale (arXiv:2605.30898): 自适应推理时缩放

核心思想: 不修改 prompt 或重新训练，仅在推理时根据检测到的维度满足程度
动态调整评分权重，模拟"像人一样自适应调整优先级"的行为。

用法:
    python3 test_time_optimize.py
"""

import glob
import json
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from persona_keywords import DIMENSION_KEYWORDS, compute_dimension_scores


def dim_satisfaction(text):
    """计算每个维度的满足程度 (0-1)。"""
    return compute_dimension_scores(text)


def detect_undersatisfied(satisfaction, threshold=0.40):
    """检测 undersatisfied 维度 (分数 < threshold)。"""
    return {dim: score for dim, score in satisfaction.items() if score < threshold}


def compute_adjusted_scores(base_scores, undersatisfied, multiplier=1.5):
    """根据 undersatisfied 维度应用动态乘数调整。

    模拟 MATO 方法:
    - undersatisfied 维度: 乘数 > 1.0 (boost)
    - over-satisfied 维度: 乘数 < 1.0 (reduce)
    - balanced 维度: 乘数 = 1.0 (maintain)

    返回调整后的分数和乘数映射。
    """
    multipliers = {}
    adjusted = {}

    threshold = 0.40
    for dim, score in base_scores.items():
        if dim in undersatisfied:
            # Undersatisfied: boost 乘数
            # 乘数大小与 undersatisfaction 程度成正比
            deficit = threshold - score
            multipliers[dim] = min(1.0 + deficit * 2.0, multiplier)
        elif score > threshold * 1.5:
            # Over-satisfied: reduce 乘数
            excess = score - threshold * 1.5
            multipliers[dim] = max(0.7, 1.0 - excess)
        else:
            # Balanced: no change
            multipliers[dim] = 1.0

    for dim, score in base_scores.items():
        adjusted[dim] = score * multipliers[dim]

    # Normalize to [0, 1]
    max_possible = sum(
        DIMENSION_KEYWORDS[dim][0][1] * multipliers[dim]
        for dim in DIMENSION_KEYWORDS
    )
    if max_possible > 0:
        for dim in adjusted:
            # Simple normalization: divide by max possible weight
            max_dim_score = sum(w for _, w in DIMENSION_KEYWORDS[dim])
            adjusted[dim] = min(1.0, adjusted[dim] / max_dim_score)

    return adjusted, multipliers


def evaluate_optimization(file_text, file_name, initial_threshold=0.40):
    """对单个文件执行测试时优化评估。"""
    base_scores = dim_satisfaction(file_text)
    undersatisfied = detect_undersatisfied(base_scores, initial_threshold)
    avg_base = sum(base_scores.values()) / len(base_scores)
    min_base = min(base_scores.values())

    if undersatisfied:
        # 应用测试时优化
        opt_scores, opt_multipliers = compute_adjusted_scores(base_scores, undersatisfied)
        avg_opt = sum(opt_scores.values()) / len(opt_scores)
        min_opt = min(opt_scores.values())
        optimized = True
    else:
        opt_scores = base_scores
        opt_multipliers = {d: 1.0 for d in base_scores}
        avg_opt = avg_base
        min_opt = min_base
        optimized = False

    return {
        "file": file_name,
        "base_avg": round(avg_base, 4),
        "base_min": round(min_base, 4),
        "base_scores": {k: round(v, 4) for k, v in sorted(base_scores.items())},
        "undersatisfied": {k: round(v, 4) for k, v in undersatisfied.items()},
        "optimized": optimized,
        "opt_avg": round(avg_opt, 4),
        "opt_min": round(min_opt, 4),
        "opt_scores": {k: round(v, 4) for k, v in sorted(opt_scores.items())},
        "multipliers": {k: round(v, 4) for k, v in opt_multipliers.items()},
    }


def test_with_sample_file(idea_files):
    """用 sample idea file 演示测试时优化过程。"""
    from persona_keywords import compute_dimension_scores

    print("=" * 60)
    print("Test-Time Optimization — Sample Response Demo")
    print("=" * 60)

    # Load the weakest idea file as "response"
    weakest = sorted(idea_files)[0]
    idea_path = PROJECT_ROOT / "memory" / weakest
    response_text = idea_path.read_text(encoding="utf-8")

    base_scores = compute_dimension_scores(response_text)
    avg_base = sum(base_scores.values()) / len(base_scores)
    min_base = min(base_scores.values())

    print(f"\nSample response: {weakest}")
    print(f"Base scores: avg={avg_base:.4f}, min={min_base:.4f}")
    print(f"\nPer-dimension scores:")
    for dim, score in sorted(base_scores.items()):
        undersatisfied = " <--- undersatisfied" if score < 0.40 else ""
        print(f"  {dim}: {score:.4f}{undersatisfied}")

    # Show what multipliers WOULD be applied with stress test threshold
    stress_threshold = 0.30
    undersatisfied_stress = {d: s for d, s in base_scores.items() if s < stress_threshold}
    if undersatisfied_stress:
        print(f"\nUnder stress test (threshold={stress_threshold}):")
        for dim, score in sorted(base_scores.items()):
            if score < stress_threshold:
                deficit = stress_threshold - score
                mult = min(1.0 + deficit * 2.0, 2.0)
                adjusted = score * mult
                print(f"  {dim}: {score:.4f} × {mult:.2f} → {adjusted:.4f}")
    else:
        print(f"\nAll dims above stress threshold ({stress_threshold})")
        # Show what would happen with intermediate threshold
        for dim, score in sorted(base_scores.items()):
            if score < 0.60:
                deficit = 0.60 - score
                mult = min(1.0 + deficit, 1.3)
                adjusted = score * mult
                print(f"  {dim}: {score:.4f} × {mult:.2f} → {adjusted:.4f}")

def main():
    print("=" * 60)
    print("Test-Time Optimization Prototype — persona-v3")
    print("Inspired by MATO (adjustable multipliers) and UniScale")
    print("=" * 60)

    # Load idea files
    idea_files = sorted(glob.glob(str(PROJECT_ROOT / "memory" / "idea-*.md")))
    print(f"\nLoading {len(idea_files)} idea files...")

    # Score all files
    results = []
    for fp in idea_files:
        text = Path(fp).read_text(encoding="utf-8")
        result = evaluate_optimization(text, Path(fp).name)
        results.append(result)

    # Summary statistics
    needs_opt = sum(1 for r in results if r["optimized"])
    no_opt = sum(1 for r in results if not r["optimized"])

    base_avgs = [r["base_avg"] for r in results]
    opt_avgs = [r["opt_avg"] for r in results]

    print(f"\nResults: {needs_opt} files need optimization, {no_opt} already balanced")
    print(f"\nBase: avg={sum(base_avgs)/len(base_avgs):.4f}, min={min(base_avgs):.4f}")
    print(f"Opt:  avg={sum(opt_avgs)/len(opt_avgs):.4f}, min={min(opt_avgs):.4f}")

    # Show worst 5 files
    print(f"\nBottom 5 files (lowest base scores):")
    for r in sorted(results, key=lambda x: x["base_avg"])[:5]:
        print(f"  {r['file']}: avg={r['base_avg']:.4f}, min={r['base_min']:.4f}")
        if r["undersatisfied"]:
            print(f"    Undersatisfied: {', '.join(r['undersatisfied'].keys())}")
            print(f"    Multipliers: {', '.join(f'{k}={v:.2f}' for k, v in r['multipliers'].items() if v != 1.0)}")

    # Sample demo
    print(f"\n{'=' * 60}")
    test_with_sample_file(idea_files)

    # Save JSON
    output_path = PROJECT_ROOT / "eval_results" / "test_time_optimize.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_files": len(results),
                "needs_optimization": needs_opt,
                "already_balanced": no_opt,
                "base_avg": round(sum(base_avgs) / len(base_avgs), 4),
                "opt_avg": round(sum(opt_avgs) / len(opt_avgs), 4),
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
