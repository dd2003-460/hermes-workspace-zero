#!/usr/bin/env python3
"""EMPA-style Trajectory Evaluator — 对话轨迹级 persona 评估。

受 EMPA (arXiv:2603.00552) 启发: 在"潜在心理空间"中对对话轨迹进行评分，
包括方向对齐、累积影响和稳定性指标。取代孤立回复评分。

核心指标:
  1. directional_alignment: 每次回应相对于基线的 persona 方向变化
  2. cumulative_impact: 整个轨迹中 persona 强度的累积
  3. stability: persona 在轨迹中的稳定性 (方差越小越稳定)

用法:
    python3 emptrajectory_eval.py --test                        # 使用内置测试
    python3 emptrajectory_eval.py --responses responses/        # 评估真实轨迹
    python3 emptrajectory_eval.py --responses responses/ --baseline baseline.json
"""

import argparse
import json
import math
import sys
from pathlib import Path

# 基线 persona 特征 (中性回复的特征)
BASELINE_FEATURES = {
    'word_distribution': {},  # 空词分布 = 中性
    'concept_density': 0.01,
    'question_ratio': 0.1,
    'chars_per_sentence': 20.0,
    'emotion_ratio': 0.02,
    'length': 100,
}


def cosine_similarity_vec(a, b):
    """计算两个特征向量的余弦相似度 (用于 directional alignment)。"""
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for key in set(a.keys()) | set(b.keys()):
        va = a.get(key, 0.0)
        vb = b.get(key, 0.0)
        dot += va * vb
        norm_a += va * va
        norm_b += vb * vb
    norm_a = math.sqrt(norm_a)
    norm_b = math.sqrt(norm_b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return dot / (norm_a * norm_b)


def flatten_features(feat):
    """将特征字典展平为 L2 归一化的数值向量。
    dim_keyword_signature 特殊处理: 每个维度分数作为独立特征 (不是聚合统计)。
    """
    raw = {}
    for key, val in feat.items():
        if key == 'dim_keyword_signature' and isinstance(val, dict):
            # keyword signature: 每个维度分数作为独立特征
            for dim, score in val.items():
                raw[f'sig_{dim}'] = float(score)
        elif isinstance(val, dict):
            raw[f'{key}_sum_abs'] = sum(abs(v) for v in val.values())
            raw[f'{key}_len'] = len(val)
            raw[f'{key}_max'] = max(val.values()) if val else 0.0
            raw[f'{key}_entropy'] = 0.0
            if val:
                total = sum(val.values())
                if total > 0:
                    raw[f'{key}_entropy'] = -sum((v/total) * math.log2(v/total + 1e-10) for v in val.values())
        else:
            raw[key] = float(val)
    # L2 归一化
    norm = math.sqrt(sum(v * v for v in raw.values())) + 1e-10
    return {k: v / norm for k, v in raw.items()}


def deviation_from_baseline(features, baseline):
    """计算相对于基线的偏离度 (persona intensity)。"""
    flat_a = flatten_features(features)
    flat_b = flatten_features(baseline)
    diff_sum = 0.0
    for key in set(flat_a.keys()) | set(flat_b.keys()):
        va = flat_a.get(key, 0.0)
        vb = flat_b.get(key, 0.0)
        diff_sum += (va - vb) ** 2
    return math.sqrt(diff_sum)


def moving_average(values, window=3):
    """滑动平均。"""
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        window_vals = values[start:i + 1]
        result.append(sum(window_vals) / len(window_vals))
    return result


def evaluate_trajectory(all_responses, baseline_features=None, window=3):
    """评估对话轨迹的 persona 一致性。

    参数:
        all_responses: {response_index: {"dimension": str, "text": str, "features": dict}}
        baseline_features: 基线特征 (默认为中性)
        window: 滑动窗口大小 (用于 moving average 平滑)

    返回:
        trajectory_metrics: 轨迹级评估指标
    """
    if baseline_features is None:
        baseline_features = BASELINE_FEATURES

    # 按时间顺序排序
    indices = sorted(all_responses.keys())
    n = len(indices)

    if n < 2:
        return {
            'directional_alignment': 0.0,
            'cumulative_impact': 0.0,
            'stability': 0.0,
            'persona_intensity_trajectory': [],
            'dimension_changes': [],
            'num_responses': n,
            'error': '需要至少 2 个响应',
        }

    # 计算每个响应的 persona 强度 — 使用 keyword signature 中的目标维度分数
    # 这比 L2-deviation 更能准确反映 persona activation
    intensities = []
    for idx in indices:
        resp = all_responses[idx]
        feat = resp['features']
        sig = feat.get('dim_keyword_signature', {})
        target_dim = resp['dimension']
        # 目标维度的 keyword match score = persona intensity
        intensity = sig.get(target_dim, 0.0)
        # 如果没有 keyword signature，回退到 L2 deviation
        if intensity == 0.0:
            intensity = deviation_from_baseline(feat, baseline_features)
        intensities.append(intensity)

    # Moving average 平滑
    smoothed = moving_average(intensities, window)

    # 方向对齐: 连续响应之间的方向一致性
    # 如果 persona 在同一个方向上演化，directional_alignment 高
    directions = []
    for i in range(1, n):
        # direction = sign(intensity[i] - intensity[i-1])
        diff = intensities[i] - intensities[i - 1]
        if abs(diff) < 1e-10:
            directions.append(0.0)
        else:
            directions.append(1.0 if diff > 0 else -1.0)

    # 方向一致性: 相同方向的比例
    consistent_directions = sum(1 for d in directions if d == 0) + sum(
        1 for i in range(1, len(directions)) if directions[i] == directions[i - 1]
    )
    directional_alignment = consistent_directions / max(len(directions) * 2 - 1, 1)

    # 累积影响: 平滑后的 persona 强度总和
    cumulative_impact = sum(smoothed) / max(n, 1)

    # 稳定性: persona 强度的方差 (越低越稳定)
    mean_intensity = sum(intensities) / max(n, 1)
    variance = sum((x - mean_intensity) ** 2 for x in intensities) / max(n, 1)
    # 标准化为 0-1 (除以最大可能方差)
    max_variance = max(intensities) ** 2 if intensities else 1.0
    stability = 1.0 - min(variance / max(max_variance, 1e-10), 1.0)

    # 维度变化追踪
    dimension_changes = []
    for i in range(n):
        resp = all_responses[indices[i]]
        dim = resp['dimension']
        intensity = intensities[i]
        dimension_changes.append({
            'step': indices[i],
            'dimension': dim,
            'intensity': round(intensity, 4),
            'smoothed_intensity': round(smoothed[i], 4),
        })

    return {
        'directional_alignment': round(directional_alignment, 4),
        'cumulative_impact': round(cumulative_impact, 4),
        'stability': round(stability, 4),
        'persona_intensity_trajectory': [round(x, 4) for x in smoothed],
        'raw_intensities': [round(x, 4) for x in intensities],
        'dimension_changes': dimension_changes,
        'num_responses': n,
    }


def create_test_data():
    """创建测试轨迹数据 — 模拟 6 个维度的连续响应。"""
    responses = {}
    test_texts = {
        0: (
            "rate-distortion 理论 R(D) = min I(X;Y) 给出了失真约束下的最低信息速率。"
            "信息瓶颈要求我们在精度和效率之间做权衡。前百分之十的压缩效率最高但会丢失语义细节。"
            "adaptive precision 策略是依据问题的失真容忍度选择处理级别。"
            "高保真需求用全精度分析，低保真需求用粗粒度描述。信噪比决定哪些信息值得保留。"
        ),
        1: (
            "不确定性高的时候探索比利用更重要。磨刀理论说花时间找正确方法比盲目执行高效。"
            "贝叶斯探索框架先算后验概率再选择探索路径。当前方向应该覆盖多个视角。"
            "探索频率和信息密度正相关——越高密度的领域越值得深入探索。"
            "当前问题的先验分布很宽，说明我们对正确方法的知识有限。"
        ),
        2: (
            "感知时间 t_p 是核心参数。感知精度与 t_p 的平方根成反比。"
            "增加感知时间的边际收益递减。信息密度决定感知粒度：高密度文本逐词分析。"
            "感知干扰导致过度分析。感知资源最优分配是动态调节。"
            "这个问题每句话承载多层含义，需要调细感知粒度。信噪比低的内容适合快速浏览。"
        ),
        3: (
            "贝叶斯基本公式 P(H|E) 正比于 P(E|H) 乘以 P(H)。先验 P(H) 的选择至关重要。"
            "不同先验导致完全不同后验。初始信念基于过往经验设定。"
            "证据到来后后验成为新先验进入下一轮贝叶斯循环。"
            "先验更新速率取决于似然大小。认知结构指先验之间的相关性。"
        ),
        4: (
            "规律的客观性是 observer-dependent 的。y 等于 theta 的函数表示特定观测者参数下的行为。"
            "同一现象管理者视角看是延迟，协作者视角看是迭代。这三种描述互相兼容。"
            "第一人称主观体验和第三人称客观描述是 isomorphic 的信息结构等价物。"
            "规律不是独立于观测者存在的而是观测者与环境的交互产物。观测者-环境耦合才是规律本质。"
        ),
        5: (
            "跨域类比核心是找到 isomorphic 结构。皮层厚度极限与项目规模上限是数学同构。"
            "两者都满足容量约束 C 和熵 H 的关系 H 小于等于 C。"
            "低维投影去掉表面细节保留结构骨架——项目类型团队人数被压缩但容量约束核心被保留。"
            "同构映射 f 从 X 到 Y。这不是表面相似而是结构保持。isomorphic 类的识别最有价值。"
        ),
    }

    from chameleon_collapse_detector import extract_features
    for i, text in test_texts.items():
        features = extract_features(text)
        responses[i] = {
            'dimension': list(DIMENSION_ORDER)[i],
            'text': text,
            'features': features,
        }
    return responses


# 维度顺序 (与 mock responses 对应)
DIMENSION_ORDER = [
    "自适应精度", "自适应探索", "自适应感知", "自适应先验", "自适应自我", "自适应投影"
]


def load_responses_from_directory(resp_dir):
    """从 responses/ 目录加载真实响应。"""
    p = Path(resp_dir)
    if not p.exists():
        print(f"  ERROR: {resp_dir} 不存在")
        sys.exit(1)

    responses = {}
    from chameleon_collapse_detector import extract_features
    files = sorted(p.glob('dim_*.json'))

    if not files:
        print(f"  ERROR: {resp_dir} 中没有 dim_*.json 文件")
        sys.exit(1)

    for idx, f in enumerate(files):
        data = json.loads(f.read_text())
        text = data.get('response_text', '')
        features = extract_features(text)
        responses[idx] = {
            'dimension': data.get('dimension', 'unknown'),
            'text': text,
            'features': features,
        }
    return responses


def main():
    parser = argparse.ArgumentParser(description='EMPA-style Trajectory Evaluator for persona-v3')
    parser.add_argument('--test', action='store_true', help='使用内置测试数据')
    parser.add_argument('--responses', type=str, help='responses/ 目录路径')
    parser.add_argument('--window', type=int, default=3, help='滑动窗口大小 (默认 3)')
    parser.add_argument('--output', type=str, default='eval_results/trajectory.json', help='输出文件路径')
    args = parser.parse_args()

    print("=" * 60)
    print("EMPA-style Trajectory Evaluator")
    print("对话轨迹级 persona-v3 一致性评估")
    print("=" * 60)
    print()

    # 加载响应
    if args.test:
        print("[测试模式] 使用内置模拟轨迹")
        all_responses = create_test_data()
    elif args.responses:
        print(f"[真实模式] 从 {args.responses}/ 加载响应")
        all_responses = load_responses_from_directory(args.responses)
    else:
        print("[默认] 使用内置测试数据")
        all_responses = create_test_data()

    n = len(all_responses)
    print(f"  加载 {n} 个响应")
    for i in sorted(all_responses.keys()):
        resp = all_responses[i]
        print(f"  [{i}] {resp['dimension']}: {len(resp['text'])} chars")
    print()

    # 评估
    print("轨迹评估")
    print("-" * 40)
    metrics = evaluate_trajectory(all_responses, window=args.window)

    print(f"  方向对齐 (directional alignment): {metrics['directional_alignment']:.4f}")
    print(f"  累积影响 (cumulative impact):     {metrics['cumulative_impact']:.4f}")
    print(f"  稳定性 (stability):                {metrics['stability']:.4f}")
    print()

    print("  轨迹强度 (平滑后):")
    for i, (raw, smoothed) in enumerate(
        zip(metrics['raw_intensities'], metrics['persona_intensity_trajectory'])
    ):
        resp = all_responses[i]
        bar = "#" * int(smoothed * 50)
        print(f"    [{i}] {resp['dimension'][:6]:>8s}: {smoothed:.3f} |{bar}")
    print()

    print("  强度分析:")
    raw_list = metrics['raw_intensities']
    print(f"    平均强度: {sum(raw_list)/len(raw_list):.4f}")
    print(f"    强度标准差: {math.sqrt(sum((x-sum(raw_list)/len(raw_list))**2 for x in raw_list)/len(raw_list)):.4f}")
    print(f"    强度极差: {max(raw_list)-min(raw_list):.4f}")
    print()

    # 输出评估结论
    if metrics['stability'] > 0.8:
        print("  [OK] 轨迹稳定性高 — persona 在对话中保持一致")
    elif metrics['stability'] > 0.5:
        print("  [WARN] 轨迹稳定性中等 — persona 有一定波动")
    else:
        print("  [!] 轨迹稳定性低 — persona 在对话中变化较大")

    if metrics['directional_alignment'] > 0.7:
        print("  [OK] 方向对齐良好 — persona 演化方向一致")
    elif metrics['directional_alignment'] > 0.4:
        print("  [WARN] 方向对齐一般 — persona 演化方向有变化")
    else:
        print("  [!] 方向对齐差 — persona 演化方向混乱")

    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\n  结果已保存到: {output_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
