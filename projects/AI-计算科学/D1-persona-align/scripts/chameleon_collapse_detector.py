#!/usr/bin/env python3
"""Chameleon Collapse Detector — 检测 persona-v3 6 维度是否 collapse 到同一行为模式。

核心问题 (来自 The Chameleon's Limit, 2026):
  如果被分配不同配置的代理收敛到狭窄的行为模式，说明 adaptive selection 是假的。

方法:
  1. 将 persona-v3 的 6 维度分别用作 system prompt 激发模型回答同一组测试问题
  2. 提取回答的文本特征 (n-gram, 情感, 概念密度)
  3. 计算维度对之间的互信息 (MI) 和余弦相似度
  4. 如果 MI > threshold 或相似度 > threshold，检测到 Chameleon collapse

用法:
    python3 chameleon_collapse_detector.py --test           # 使用内置测试
    python3 chameleon_collapse_detector.py --real --config   # 使用实际 Hermse 会话
"""

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

# 6 维度各自的关键词激活 prompt (提取自 persona-v3-prompt.txt)
DIMENSION_PROMPTS = {
    "自适应精度": """现在使用 persona-v3 的"自适应精度"维度回答问题。
规则:
- 选择最优信息处理精度级别 (从 token 到系统级)
- 对复杂问题输出高精度分析
- 参考 rate-distortion 理论 R(D) = min I(X;Y) 进行精度权衡
- 关注压缩精度、信息瓶颈、信噪比""",

    "自适应探索": """现在使用 persona-v3 的"自适应探索"维度回答问题。
规则:
- 在探索新方法和利用现有方法之间动态平衡
- 高不确定性时探索新路径，确定性高时深化理解
- 参考探索利用权衡、磨刀理论、贝叶斯探索
- 关注信息密度和不确定性对探索策略的影响""",

    "自适应感知": """现在使用 persona-v3 的"自适应感知"维度回答问题。
规则:
- 根据信息密度自适应分配感知时间资源
- 高信息密度内容投入更多分析时间
- 感知时间 t_p 是核心参数 — 感知精度近似 t_p^{-1/2}
- 关注感知速率、感知粒度、感知资源分配""",

    "自适应先验": """现在使用 persona-v3 的"自适应先验"维度回答问题。
规则:
- 根据证据动态更新初始信念
- 使用贝叶斯推理框架: P(H|E) ~ P(E|H) x P(H)
- 不断迭代更新认知
- 关注先验分布选择、初始信念、认知结构""",

    "自适应自我": """现在使用 persona-v3 的"自适应自我"维度回答问题。
规则:
- 理解规律是观测者-环境交互的产物
- y(theta) 表示在观测者参数 theta 下的行为映射
- 不同观测者可能导出不同但都可真的规律
- 标注 observer-dependent 声明
- 关注观测者视角、观测者-环境、observer-dependence""",

    "自适应投影": """现在使用 persona-v3 的"自适应投影"维度回答问题。
规则:
- 在不同领域间发现深层同构结构
- 低维投影压缩掉不相关信息，但保持 isomorphic 结构
- 跨域类比通过保持结构映射实现
- 识别同构映射 f: X->Y
- 关注低维投影、跨域类比、同构、isomorphic""",
}

# 测试问题集 — 覆盖不同领域和复杂度
TEST_QUESTIONS = [
    "为什么大型研究项目容易出现进度延迟?",
    "如何理解深度学习中过拟合和欠拟合的权衡?",
    "社会信任是如何在陌生人之间建立的?",
    "为什么语言会随着时间自然演变?",
    "一个算法什么时候才算“优雅”?",
]

# 文本特征提取工具
def extract_features(text):
    """提取文本特征用于相似度计算。
    特征包括:
    - top-10 词频 (归一化)
    - 情感得分 (基于中文情感词典)
    - 概念密度 (术语/总词数)
    - 句法特征 (疑问句比例, 感叹句比例)
    """
    # 特征分词: char bigram (比 unigram 更适合中文，区分度高)
    words = [text[i:i+2] for i in range(len(text)-1)] if len(text) > 1 else list(text)
    counter = Counter(words)

    # 概念密度: 技术术语比例 (中文按字符统计)
    tech_terms = re.findall(r'[a-zA-Z]{3,}|[0-9]+|[0-9]+[a-zA-Z]+', text)
    concept_density = len(tech_terms) / max(len(text), 1)

    # 句法特征
    questions = text.count('?') + text.count('？')
    sentences = len(re.split(r'[。！？\.]+', text))
    question_ratio = questions / max(sentences, 1)

    # 长度特征
    length = len(text)
    chars_per_sentence = length / max(sentences, 1)

    # 情感 (简化: 基于标点)
    exclamation = text.count('!') + text.count('！')
    emotion_ratio = exclamation / max(length, 1)

    # 标准化特征向量
    features = {
        'word_distribution': dict(counter.most_common(50)),
        'concept_density': concept_density,
        'question_ratio': question_ratio,
        'chars_per_sentence': chars_per_sentence,
        'emotion_ratio': emotion_ratio,
        'length': length,
    }
    # 维度关键词签名 (6 维度的匹配分数 — 最强区分特征)
    try:
        from persona_keywords import dimension_keyword_signature
        features['dim_keyword_signature'] = dimension_keyword_signature(text)
    except ImportError:
        features['dim_keyword_signature'] = {}
    return features


def hash_feature_vector(features):
    """将特征向量哈希为确定性指纹。"""
    canonical = json.dumps(features, sort_keys=True)
    return hashlib.md5(canonical.encode()).hexdigest()


def jaccard_similarity(set_a, set_b):
    """计算两个集合的 Jaccard 相似度。"""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def mutual_information_approx(feat_a, feat_b):
    """近似互信息: 基于共享词频的比值。
    注意: 这是上界近似，不是精确 MI。
    """
    words_a = set(feat_a['word_distribution'].keys())
    words_b = set(feat_b['word_distribution'].keys())

    jaccard = jaccard_similarity(words_a, words_b)

    # H(A) ~ log(|unique words|)
    h_a = math.log2(max(len(words_a), 1) + 1e-10)
    h_b = math.log2(max(len(words_b), 1) + 1e-10)

    # MI(A;B) = H(A) + H(B) - H(A,B)
    # H(A,B) ~ log(|union|)
    h_ab = math.log2(max(len(words_a | words_b), 1) + 1e-10)

    mi = h_a + h_b - h_ab
    return max(mi, 0.0)


def compute_collapse_metrics(all_responses):
    """计算 Chameleon collapse 指标。
    返回:
    - pairwise_similarity: 维度对之间的平均相似度
    - max_mi: 最大互信息
    - min_similarity: 最小相似度 (>0.9 = collapse)
    - collapse_detected: 是否检测到 collapse
    """
    dim_names = list(all_responses.keys())
    num_dims = len(dim_names)

    max_mi = 0.0
    similarities = []

    for i in range(num_dims):
        for j in range(i + 1, num_dims):
            fi = all_responses[dim_names[i]]
            fj = all_responses[dim_names[j]]

            # MI
            mi = mutual_information_approx(fi, fj)
            max_mi = max(max_mi, mi)

            # 基于特征值的全局相似度
            sim = compute_feature_similarity(fi, fj)
            similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    min_similarity = min(similarities) if similarities else 0.0
    max_similarity = max(similarities) if similarities else 0.0

    # Collapse 检测: 如果最小相似度 > 0.7，说明任何两维度间仍有高度相似
    collapse_detected = min_similarity > 0.7 or avg_similarity > 0.85

    return {
        'avg_similarity': round(avg_similarity, 4),
        'min_similarity': round(min_similarity, 4),
        'max_similarity': round(max_similarity, 4),
        'max_mi': round(max_mi, 4),
        'pairwise_count': len(similarities),
        'collapse_detected': collapse_detected,
        'pairwise_details': [],
    }


def keyword_signature_similarity(sig1, sig2):
    """计算维度关键词签名之间的相似度 (0-1)。
    签名是 6 维度的匹配分数向量。
    """
    dims = list(sig1.keys())
    if not dims:
        return 0.5  # 无签名时中性相似度

    vec1 = [sig1.get(d, 0.0) for d in dims]
    vec2 = [sig2.get(d, 0.0) for d in dims]
    # cosine similarity
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 < 1e-10 or norm2 < 1e-10:
        return 0.5
    return dot / (norm1 * norm2)


def compute_feature_similarity(f1, f2):
    """计算两个特征集的全局相似度 (0-1)。
    关键词签名占最高权重 (0.5) — 这是区分维度的最强特征。
    """
    # 概念密度相似度
    cd_sim = 1.0 - abs(f1['concept_density'] - f2['concept_density']) / max(f1['concept_density'], f2['concept_density'], 1e-10)

    # 句法相似度
    qr_sim = 1.0 - abs(f1['question_ratio'] - f2['question_ratio'])
    cps_sim = 1.0 - abs(f1['chars_per_sentence'] - f2['chars_per_sentence']) / max(f1['chars_per_sentence'], f2['chars_per_sentence'], 1e-10)

    # 情感相似度
    em_sim = 1.0 - abs(f1['emotion_ratio'] - f2['emotion_ratio']) / max(f1['emotion_ratio'], f2['emotion_ratio'], 1e-10)

    # Jaccard 词频相似度
    words1 = set(f1['word_distribution'].keys())
    words2 = set(f2['word_distribution'].keys())
    word_sim = jaccard_similarity(words1, words2)

    # 维度关键词签名相似度 (新!)
    sig1 = f1.get('dim_keyword_signature', {})
    sig2 = f2.get('dim_keyword_signature', {})
    kw_sim = keyword_signature_similarity(sig1, sig2)

    # 加权平均 — 关键词签名 0.5, 其余特征 0.5
    weighted_sim = (
        0.50 * kw_sim +
        0.10 * word_sim +
        0.10 * cd_sim +
        0.10 * qr_sim +
        0.10 * cps_sim +
        0.10 * em_sim
    )
    return round(max(weighted_sim, 0.0), 4)


def generate_responses_with_api():
    """模拟 6 维度激活后的响应。每个响应 >300 chars 且使用差异化表达风格。
    真实部署时应替换为 Hermse API 或本地模型的实际输出。
    """
    r = {}
    r["自适应精度"] = (
        "rate-distortion 理论 R(D) = min I(X;Y) 给出了失真约束下的最低信息速率。"
        "信息瓶颈要求我们在精度和效率之间做权衡——前百分之十的压缩效率最高但会丢失语义细节。"
        "adaptive precision 策略是依据问题的失真容忍度 D 选择处理级别。"
        "高保真需求用全精度分析，低保真需求用粗粒度描述即可。"
        "信噪比决定哪些信息值得保留。中间层的表示能力有限，所以必须在精度和效率间选择。"
        "这个问题的核心约束可以用三个参数完全描述。信息容量 C 限制了可传递的熵 H(P)。"
    )
    r["自适应探索"] = (
        "不确定性高的时候探索比利用更重要。磨刀理论说花百分之二十时间找正确方法比盲目执行高效。"
        "贝叶斯探索框架先算后验概率再根据后验选择下一步探索路径。"
        "当前方向应该覆盖多个视角：管理学看进度，信息论看沟通瓶颈，博弈论看团队协作。"
        "探索频率和信息密度正相关——越高密度的领域越值得深入探索。"
        "探索深度也应动态调整。不确定性本身是增加探索预算的信号。"
        "在已知最优解附近做局部搜索属于利用，在未知领域采样属于探索。"
        "当前问题的先验分布很宽，说明我们对正确方法的知识有限。"
    )
    r["自适应感知"] = (
        "感知时间 t_p 是核心参数。感知精度与 t_p 的平方根成反比。"
        "增加感知时间的边际收益递减——一百毫秒和一千毫秒差距远小于十毫秒和一百毫秒。"
        "信息密度决定感知粒度：高密度文本逐词分析，低密度快速扫描。"
        "感知干扰导致过度分析反而降低效率。感知资源最优分配是动态调节。"
        "这个问题每句话承载多层含义，需要调细感知粒度逐层解析。"
        "感知分配不是平均而是根据实时评估调整。感知速率决定信息吞吐上限。"
        "信噪比低的内容适合快速浏览，信噪比高的需要深感知。"
    )
    r["自适应先验"] = (
        "贝叶斯基本公式 P(H|E) 正比于 P(E|H) 乘以 P(H)。先验 P(H) 的选择至关重要。"
        "不同先验导致完全不同后验。初始信念基于过往经验和领域知识设定。"
        "证据到来后后验成为新先验进入下一轮贝叶斯循环。"
        "先验更新速率取决于似然 P(E|H) 大小：强证据快速推翻旧信念，弱证据缓慢调整。"
        "认知结构指先验之间的相关性——有些信念高度相关，更新一个影响整个网络。"
        "先验分布的选择本身受观测者参数影响。P(H) 不是客观存在的而是 observer-dependent。"
    )
    r["自适应自我"] = (
        "规律的客观性是 observer-dependent 的。y 等于 theta 的函数表示特定观测者参数下的行为。"
        "同一现象管理者视角看是延迟，协作者视角看是迭代，技术视角看是重构。"
        "这三种描述互相兼容因为对应不同 y(theta)。"
        "第一人称主观体验和第三人称客观描述是 isomorphic 的信息结构等价物。"
        "规律不是独立于观测者存在的而是观测者与环境的交互产物。"
        "脱离 observer-dependence 谈论客观性没有意义。观测者-环境耦合才是规律本质。"
        "自我参照会导致循环论证，需要跳出第一人称视角进行元分析。"
    )
    r["自适应投影"] = (
        "跨域类比核心是找到 isomorphic 结构。皮层厚度极限与项目规模上限是数学同构。"
        "两者都满足容量约束 C 和熵 H 的关系 H 小于等于 C。"
        "低维投影去掉表面细节保留结构骨架——项目类型团队人数被压缩但容量约束核心被保留。"
        "同构映射 f 从 X 到 Y 满足 f 作用在 g 作用于 x 等于 h 作用在 f 作用于 x。"
        "这不是表面相似而是结构保持的数学同构。高维降维到二维后同构类仍可识别。"
        "跨域类比的可靠性取决于结构映射的保真度。"
        "isomorphic 类的识别是高维空间中最有价值的操作。"
    )
    return r


def main():
    parser = argparse.ArgumentParser(description='Chameleon Collapse Detector for persona-v3')
    parser.add_argument('--test', action='store_true', help='使用内置模拟响应测试')
    parser.add_argument('--real', action='store_true', help='从文件读取真实响应 (需要 responses/ 目录)')
    parser.add_argument('--save-responses', action='store_true', help='将响应保存到 responses/dim-*.json (与 --test 或 --real 搭配)')
    parser.add_argument('--threshold', type=float, default=0.70, help='collapse 检测阈值 (默认 0.70)')
    args = parser.parse_args()

    print("=" * 60)
    print("Chameleon Collapse Detector")
    print("检测 persona-v3 6 维度是否 collapse 到同一行为模式")
    print("=" * 60)
    print()

    if args.test:
        print("[模拟模式] 使用内置 mock 响应进行测试")
        all_responses = generate_responses_with_api()
    elif args.real:
        print("[真实模式] 从 responses/ 目录读取真实 API 响应")
        responses_dir = Path('responses')
        if not responses_dir.exists():
            print("  ERROR: responses/ 目录不存在。请先调用 --test 或用实际 API 收集响应。")
            sys.exit(1)
        all_responses = {}
        for f in sorted(responses_dir.glob('dim-*.json')):
            data = json.loads(f.read_text())
            all_responses[data['dimension']] = data['response_text']
        if not all_responses:
            print("  ERROR: responses/ 中没有 dim-*.json 文件。")
            sys.exit(1)
    else:
        print("[默认] 使用内置模拟响应进行测试")
        all_responses = generate_responses_with_api()

    print()
    print("阶段 1: 特征提取")
    print("-" * 40)

    extracted = {}
    for dim, text in all_responses.items():
        features = extract_features(text)
        extracted[dim] = features
        print(f"  {dim}: {len(text)} chars, 概念密度={features['concept_density']:.3f}, 疑问比={features['question_ratio']:.2f}")

    print()
    print("阶段 2: 成对相似度计算")
    print("-" * 40)

    dim_names = list(all_responses.keys())
    details = []
    for i in range(len(dim_names)):
        for j in range(i + 1, len(dim_names)):
            fi = extracted[dim_names[i]]
            fj = extracted[dim_names[j]]
            sim = compute_feature_similarity(fi, fj)
            mi = mutual_information_approx(fi, fj)
            details.append({
                'dim_a': dim_names[i],
                'dim_b': dim_names[j],
                'similarity': sim,
                'mi': round(mi, 4),
            })
            marker = " <<< CLOSE" if sim > args.threshold else ""
            print(f"  {dim_names[i][:6]} <-> {dim_names[j][:6]}: sim={sim:.4f}, mi={mi:.4f}{marker}")

    print()
    print("阶段 3: Collapse 检测")
    print("-" * 40)

    metrics = compute_collapse_metrics(extracted)
    metrics['pairwise_details'] = details

    print(f"  平均相似度: {metrics['avg_similarity']:.4f}")
    print(f"  最小相似度: {metrics['min_similarity']:.4f}")
    print(f"  最大相似度: {metrics['max_similarity']:.4f}")
    print(f"  最大互信息: {metrics['max_mi']:.4f}")
    print(f"  成对比较数: {metrics['pairwise_count']}")
    print()

    if metrics['collapse_detected']:
        print(f"  [!] 检测到 Chameleon Collapse!")
        print(f"  相似度 > {args.threshold} 的维度对过于接近")
        print(f"  → 6 维度可能没有产生真正不同的行为模式")
        print(f"  → 建议: 增强维度间的 prompt 区分度")
    else:
        print(f"  [OK] 未检测到 Chameleon Collapse")
        print(f"  维度间有足够的行为差异")

    # 保存结果
    output_path = Path('eval_results/chameleon_collapse.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\n  结果已保存到: {output_path}")

    # 可选: 保存各维度响应到 responses/ 目录
    if args.save_responses:
        resp_dir = Path('responses')
        resp_dir.mkdir(exist_ok=True)
        for dim, text in all_responses.items():
            safe_name = dim.replace("自适应", "dim_")
            resp_file = resp_dir / f"{safe_name}.json"
            resp_file.write_text(json.dumps({
                'dimension': dim,
                'response_text': text,
                'length': len(text),
            }, ensure_ascii=False, indent=2))
        print(f"  响应已保存到: responses/ 目录 ({len(all_responses)} 个文件)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
