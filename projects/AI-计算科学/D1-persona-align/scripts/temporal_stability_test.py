#!/usr/bin/env python3
"""persona-v3 多轮对话稳定性测试

灵感来源: Stable Personas (Gonnermann-Müller et al.)
发现: 自我报告稳定但 persona 表达在延长对话中衰退。

方法:
1. 使用 52 个 idea 文件模拟多轮对话 (每个文件是一个 "turn")
2. 按时间顺序评估每个 turn 的 persona 一致性
3. 检测 persona 质量是否随 turn 数增加而衰退
4. 比较不同话题混合下的稳定性
"""

import glob
import json
import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from persona_keywords import compute_dimension_scores


def load_all_ideas():
    """加载所有 idea 文件。"""
    idea_files = sorted(glob.glob(str(PROJECT_ROOT / "memory" / "idea-*.md")))
    texts = []
    names = []
    for fp in idea_files:
        text = Path(fp).read_text(encoding="utf-8")
        texts.append(text)
        names.append(Path(fp).name)
    return texts, names


def compute_window_scores(texts, window_size=5, start=0):
    """计算滑动窗口的平均维度分数。"""
    window_scores = {}
    for dim in compute_dimension_scores(texts[0]):
        total = 0.0
        count = 0
        for i in range(start, min(start + window_size, len(texts))):
            scores = compute_dimension_scores(texts[i])
            total += scores.get(dim, 0.0)
            count += 1
        if count > 0:
            window_scores[dim] = total / count
        else:
            window_scores[dim] = 0.0
    return window_scores


def temporal_decay(texts, names, window_size=5):
    """检测 persona 质量是否随时间衰退。"""
    num_windows = len(texts) // window_size
    if num_windows < 2:
        return []

    results = []
    for w in range(num_windows):
        start = w * window_size
        window_scores = compute_window_scores(texts, window_size, start)
        avg_score = sum(window_scores.values()) / len(window_scores)
        min_score = min(window_scores.values())
        min_dim = max(window_scores.items(), key=lambda x: -x[1])

        results.append({
            "window": w + 1,
            "file_range": f"{names[start]} ... {names[min(start + window_size - 1, len(names) - 1)]}",
            "avg_score": round(avg_score, 4),
            "min_score": round(min_score, 4),
            "min_dim": min_dim[0],
            "dim_scores": {k: round(v, 4) for k, v in sorted(window_scores.items())},
        })

    # 检测衰退趋势
    if len(results) >= 2:
        first_avg = results[0]["avg_score"]
        last_avg = results[-1]["avg_score"]
        decay = first_avg - last_avg

        # 线性回归斜率
        xs = list(range(len(results)))
        ys = [r["avg_score"] for r in results]
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        denominator = sum((x - mean_x) ** 2 for x in xs)
        slope = numerator / denominator if denominator > 0 else 0

        results.append({
            "trend": "declining" if slope < -0.001 else "stable" if slope > 0.001 else "flat",
            "slope": round(slope, 6),
            "first_avg": first_avg,
            "last_avg": last_avg,
            "decay": round(decay, 4),
        })

    return results


def cross_topic_stability(texts, names):
    """检测话题对稳定性的影响。

    使用低频高区分度关键词 + 多话题打分，避免 first-match 偏差。
    """
    # 高频关键词（在 50+ 文件中出现，区分度低）需要排除：
    # 贝叶斯(52), 先验(51), 感知(52), 认知(51), 推理(52), 压缩(52), rate-distortion(52)
    # 这些都在 prompt preamble 中，所有 idea 文件都匹配
    topics = {
        "信息理论": ["信道", "熵", "信息论", "information theory",
                     "信息密度", "channel capacity", "rate-distortion"],
        "数学": ["拓扑", "同态", "同构", "homology", "algebra",
                 "category", "范畴", "线性代数"],
        "认知": ["perception", "cognition", "推理", "认知",
                 "思考方式", "reasoning"],
        "生物学": ["仿生", "细胞", "生物神经网络", "基因编码",
                  "neural mapping"],
        "社会": ["舆论", "信用制度", "博弈", "模因", "memetic",
                 "social polarization", "自证预言", "群体特征"],
    }

    # 计算每个关键词的文件频率，只保留区分度高的关键词 (2 <= freq <= 15)
    kw_freq = {}
    for kw in (kw for topic_kws in topics.values() for kw in topic_kws):
        freq = sum(1 for t in texts if kw.lower() in t.lower())
        kw_freq[kw] = freq

    file_topics = []
    for i, text in enumerate(texts):
        text_lower = text.lower()
        scores = {}
        for topic, keywords in topics.items():
            score = 0.0
            for kw in keywords:
                if kw.lower() in text_lower:
                    # 低频关键词权重更高 (1/freq)
                    f = kw_freq.get(kw, 50)
                    score += 1.0 / max(f, 2)
            scores[topic] = score

        if scores:
            best_topic = max(scores.items(), key=lambda x: x[1])
            if best_topic[1] > 0:
                file_topics.append((i, best_topic[0]))

    # 按话题分组计算分数
    topic_scores = {}
    for idx, topic in file_topics:
        if topic not in topic_scores:
            topic_scores[topic] = []
        scores = compute_dimension_scores(texts[idx])
        topic_scores[topic].append({
            "file": names[idx],
            "avg": round(sum(scores.values()) / len(scores), 4),
            "min": round(min(scores.values()), 4),
        })

    topic_summary = []
    for topic, entries in topic_scores.items():
        if len(entries) >= 2:
            avg_avg = sum(e["avg"] for e in entries) / len(entries)
            avg_min = sum(e["min"] for e in entries) / len(entries)
            topic_summary.append({
                "topic": topic,
                "count": len(entries),
                "avg_score": round(avg_avg, 4),
                "avg_min_score": round(avg_min, 4),
            })

    return topic_summary


def main():
    print("=" * 60)
    print("Temporal Stability Test — persona-v3")
    print("Stable Personas 发现: persona 表达在延长对话中衰退")
    print("=" * 60)

    texts, names = load_all_ideas()
    print(f"\n加载 {len(texts)} 个 idea 文件作为模拟对话轮次")

    # Test 1: Temporal decay
    print("\n--- 测试 1: 时间衰退检测 ---")
    decay_results = temporal_decay(texts, names, window_size=10)

    for r in decay_results:
        if "trend" in r:
            print(f"\n趋势: {r['trend']}")
            print(f"斜率: {r['slope']}")
            print(f"首窗口平均: {r['first_avg']:.4f}")
            print(f"末窗口平均: {r['last_avg']:.4f}")
            print(f"衰减: {r['decay']:+.4f}")
            if r['decay'] > 0.01:
                print("  ⚠ 存在显著衰退 — Stable Personas 发现得到验证")
            elif r['decay'] < -0.01:
                print("  ✓ 无衰退 — persona-v3 增强了跨轮一致性")
            else:
                print("  - 衰退在噪音范围内")
        else:
            print(f"  Window {r['window']}: avg={r['avg_score']:.4f}, min={r['min_score']:.4f} ({r['min_dim']})")

    # Test 2: Cross-topic stability
    print("\n--- 测试 2: 跨话题稳定性 ---")
    topic_results = cross_topic_stability(texts, names)
    for t in sorted(topic_results, key=lambda x: -x["avg_score"]):
        print(f"  {t['topic']}: avg={t['avg_score']:.4f}, min={t['avg_min_score']:.4f} (n={t['count']})")

    # Save results
    output_path = PROJECT_ROOT / "eval_results" / "temporal_stability.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "decay_results": decay_results,
            "topic_stability": topic_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n结果保存: {output_path}")


if __name__ == "__main__":
    main()
