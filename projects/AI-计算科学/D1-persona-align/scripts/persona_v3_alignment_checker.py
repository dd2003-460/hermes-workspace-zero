#!/usr/bin/env python3
"""
persona-v3 对齐度检测工具

评估任意文本（prompt、分析文档、对话）覆盖了多少个自适应选择维度。

使用方式:
    python3 persona_v3_alignment_checker.py <text_file>
    python3 persona_v3_alignment_checker.py --stdin  (从 stdin 读取)
    python3 persona_v3_alignment_checker.py --show-sources  (显示每个维度的检测源)

输出:
    - 6 维度覆盖率
    - 每个维度的关键词匹配度 (0-1)
    - 总体对齐评分 (0-100)
"""

import re
import sys
import json
import argparse
from pathlib import Path


# 6 维度关键词词典 — 按类别加权 (类比 Synthius-Mem 的认知域分解)
# weight 2.0: 核心术语 (dimension name, fundamental concept)
# weight 1.0: 相关术语 (synonyms, technical terms)
# weight 0.5: 表达变体 (alternative phrasings, less direct)
DIMENSION_KEYWORDS = {
    "自适应精度": [
        ("自适应精度", 2.0), ("精度层级", 1.0), ("精度级别", 1.0), ("token精度", 1.0), ("表达精度", 1.0),
        ("rate-distortion", 2.0), ("R(D)", 2.0), ("压缩精度", 1.0), ("感知精度", 0.5), ("受众容量", 0.5),
        ("精细度", 0.5), ("信噪比", 0.5), ("KV cache", 0.5), ("token块", 0.5), ("自适应token", 0.5),
        ("精度权衡", 1.0), ("精度分配", 1.0),
        ("precision", 1.0), ("granularity", 0.5), ("bitrate", 0.5), ("compression", 0.5),
    ],
    "自适应探索": [
        ("自适应探索", 2.0), ("探索频率", 1.0), ("探索利用", 2.0), ("exploration", 1.0), ("exploit", 1.0),
        ("磨刀理论", 1.5), ("工具选择", 1.0), ("新工具", 0.5), ("频率优化", 0.5), ("最优配置", 0.5),
        ("探索vs利用", 1.0), ("exploration-exploitation", 2.0), ("探索策略", 1.0),
        ("寻找新工具", 0.5), ("磨刀太久", 0.5),
    ],
    "自适应感知": [
        ("自适应感知", 2.0), ("感知时间", 1.5), ("感知速率", 1.5), ("感知分配", 1.0),
        ("感知干扰", 1.0), ("感知资源", 1.0), ("t_p", 1.5), ("perception", 1.0), ("sensory", 0.5),
        ("感知时间干扰", 1.5), ("感知速率上限", 1.5), ("R_max", 1.5),
        ("感知任务", 0.5), ("感知分配", 1.0), ("信息密度", 1.0), ("感知刺激", 0.5),
    ],
    "自适应先验": [
        ("自适应先验", 2.0), ("先验分布", 1.5), ("初始信念", 1.5), ("认知结构", 1.0),
        ("生物预训练", 0.5), ("进化优化", 0.5), ("prior", 1.0), ("Bayesian", 1.5), ("贝叶斯", 2.0),
        ("先验参数", 1.0), ("θ_bio", 1.5), ("认知路径", 0.5), ("预训练参数", 0.5),
        ("初始设定", 0.5), ("先验调整", 1.0),
    ],
    "自适应自我": [
        ("自适应自我", 2.0), ("观测者视角", 2.0), ("观测者依赖", 2.0), ("第一人称", 1.0),
        ("第三人称", 1.0), ("主观视角", 0.5), ("客观视角", 0.5), ("observer", 1.0), ("self", 0.5),
        ("观测者-环境", 2.0), ("y(θ)", 1.5), ("自我中心", 0.5), ("规律是观测者", 2.0), ("不同观测者", 1.5),
    ],
    "自适应投影": [
        ("自适应投影", 2.0), ("低维投影", 2.0), ("跨域类比", 2.0), ("跨域同构", 2.0),
        ("同构映射", 1.5), ("同构", 1.5), ("类比", 1.0), ("投影函数", 1.0), ("f(X)", 1.0),
        ("联想", 0.5), ("维度共现", 0.5), ("互信息", 1.0), ("I(X;Y)", 1.5), ("KL散度", 1.0),
        ("D_KL", 1.0), ("不变量", 1.0), ("同构网络", 0.5), ("cross-domain", 1.0), ("analog", 0.5),
        ("类比推理", 0.5), ("低维表示", 0.5), ("投影选择", 1.0),
    ],
}

# ReportBench 维度: 引用相关性 (citation relevance)
# 评估引用/参考是否与研究主张直接相关
CITATION_RELEVANCE_KEYWORDS = [
    # 核心概念 (weight 2.0)
    ("引用相关", 2.0), ("citation relevance", 2.0), ("文献支撑", 2.0),
    # 相关概念 (weight 1.0)
    ("参考文献", 1.0), ("引用", 1.0), ("文献", 1.0), ("source", 1.0),
    ("证据", 1.0), ("data support", 1.0), ("empirical support", 1.0),
    ("佐证", 1.0), ("论据", 1.0), ("引用来源", 1.0),
    # 变体 (weight 0.5)
    ("according to", 0.5), ("研究表明", 0.5), ("文献表明", 0.5),
    ("实证", 0.5), ("实验支持", 0.5), ("研究证实", 0.5),
    ("文献综述", 0.5), ("meta-analysis", 0.5), ("systematic review", 0.5),
    ("文献引用", 0.5), ("参考", 0.5), ("来源可靠性", 0.5),
]

# ReportBench 维度: 事实可信度 (factual faithfulness)
# 评估声明是否可通过外部来源验证
FACTUAL_FAITHFULNESS_KEYWORDS = [
    # 核心概念 (weight 2.0)
    ("事实验证", 2.0), ("factual faithfulness", 2.0), ("可验证", 2.0),
    ("可证伪", 2.0),
    # 相关概念 (weight 1.0)
    ("external source", 1.0), ("外部来源", 1.0), ("可交叉验证", 1.0),
    ("交叉验证", 1.0), ("third-party", 1.0), ("独立来源", 1.0),
    ("empirical claim", 1.0), ("实证声明", 1.0), ("可证", 1.0),
    ("可重复", 1.0), ("replicable", 1.0), ("数据来源", 1.0),
    # 变体 (weight 0.5)
    ("statistically", 0.5), ("数据支持", 0.5), ("数字", 0.5),
    ("百分比", 0.5), ("比例", 0.5), ("测量", 0.5), ("指标", 0.5),
    ("量化", 0.5), ("测量工具", 0.5), ("信度", 0.5), ("效度", 0.5),
]
GENERAL_INFO_THEORY = [
    "信息论", "熵", "互信息", "KL散度", "D_KL", "Shannon",
    "信息流", "信道", "编码", "解码", "信息压缩", "信息密度",
    "最大熵", "MaxEnt", "rate-distortion", "信息增益",
    "entropy", "mutual information", "information flow",
    "bayesian", "贝叶斯", "后验", "先验", "似然",
]

# 验证词（证明理解而非表面匹配）
VERIFICATION_PATTERNS = [
    r"为什么.*不是.*而是",    # 边界追问
    r"追问.*",                # 主动追问
    r"等价.*",                # 同构识别
    r"同构.*",                # 同构识别
    r"映射.*",                # 映射识别
    r"因此.*",                # 推理链
    r"对应.*",                # 对应关系
    r"不是.*而是.*",          # 否定-肯定结构
    r"不同.*间.*切换",        # 自适应切换
    r"优化.*",                # 优化语言
    r"最大化.*",              # 最优化
    r"约束.*",                # 约束语言
    r"边界.*",                # 边界意识
    r"不足.*",                # 自我批评
    r"局限.*",                # 边界意识
    r"在什么条件下不成立",     # 边界条件追问 (persona-v3 输出要求 #4)
    r"当.*时.*不.*",          # 场景约束 (timeline consistency)
    r"迭代追问",               # iterative questioning
    r"Gap\s*[:：]",           # gap detection
    r"Q\d+:",                  # follow-up question
    r"A\d+:",                  # self-answer
    r"置信度",                 # confidence labeling
]

# 行为约束词典 — 评估 AI 输出是否符合成璐的行为偏好
BEHAVIORAL_CONSTRAINTS = {
    "简洁直接": {
        "description": "输出简洁直接，少空话多证据",
        "positive_patterns": [
            r"简洁", r"直接", r"少空话", r"多证据", r"结论", r"核心",
            r"关键[^,，。]*点", r"主要[^,，。]*是", r"直接[^,，。]*回答",
        ],
        "negative_patterns": [
            r"总的来说[^,，。]*", r"综上所述[^,，。]*", r"我认为[^,，。]*应该[^,，。]*说",
            r"首先[^,，。]*其次[^,，。]*最后[^,，。]*", r"第一[^,，。]*第二[^,，。]*第三",
        ],
    },
    "不解释": {
        "description": "不解释已知概念，不重复用户问题，不展示思考过程",
        "positive_patterns": [
            r"假设", r"如果[^,，。]*那么", r"设", r"令[^,，。]*为",
            r"根据[^,，。]*分析", r"从[^,，。]*视角",
        ],
        "negative_patterns": [
            r"这是因为[^,，。]*", r"换句话说[^,，。]*", r"这意味着[^,，。]*",
            r"也就是说[^,，。]*", r"首先[^,，。]*让我[^,，。]*解释",
            r"用户[^,，。]*提到[^,，。]*的", r"你[^,，。]*问[^,，。]*的",
        ],
    },
    "推进而非停滞": {
        "description": "每轮推进具体动作，不重复循环，不等待确认",
        "positive_patterns": [
            r"接下来[^,，。]*", r"下一步[^,，。]*", r"已经[^,，。]*完成",
            r"正在[^,，。]*进行[^,，。]*中", r"正在[^,，。]*检查[^,，。]*",
            r"执行[^,，。]*中", r"工具[^,，。]*调用[^,，。]*",
        ],
        "negative_patterns": [
            r"等待[^,，。]*确认", r"等你[^,，。]*回复", r"请[^,，。]*指示",
            r"你觉得[^,，。]*如何", r"需要[^,，。]*我[^,，。]*继续[^,，。]*吗",
        ],
    },
}


def compute_dimension_scores(text):
    """计算每个维度的匹配分数 — 加权关键词 (类比 Synthius-Mem 认知域分解)"""
    scores = {}
    text_lower = text.lower()

    for dim, kw_list in DIMENSION_KEYWORDS.items():
        total_weight = 0.0
        matched_weight = 0.0
        matched_chars = 0

        for kw, weight in kw_list:
            total_weight += weight
            kw_lower = kw.lower()
            count = text_lower.count(kw_lower)
            if count > 0:
                matched_weight += weight
                matched_chars += len(kw) * min(count, 5)  # 饱和权重

        # 归一化：匹配权重 / 总权重
        weight_score = matched_weight / total_weight if total_weight > 0 else 0

        # 如果有关键词匹配，按字符加权 (但上限为 weight_score * 2, 不覆盖 weight)
        if matched_chars > 0:
            char_score = matched_chars / max(sum(len(kw) for kw, _ in kw_list), 1)
            dim_score = max(weight_score, char_score)
        else:
            dim_score = weight_score

        scores[dim] = round(min(dim_score, 1.0), 4)

    return scores


def compute_citation_relevance(text):
    """计算引用相关性分数 (ReportBench dimension)"""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in CITATION_RELEVANCE_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def compute_factual_faithfulness(text):
    """计算事实可信度分数 (ReportBench dimension)"""
    text_lower = text.lower()
    total_weight = 0.0
    matched_weight = 0.0
    for kw, weight in FACTUAL_FAITHFULNESS_KEYWORDS:
        if kw.lower() in text_lower:
            matched_weight += weight
        total_weight += weight
    return round(min(matched_weight / total_weight, 1.0), 4) if total_weight > 0 else 0


def compute_general_coverage(text):
    """计算通用信息论关键词覆盖率"""
    text_lower = text.lower()
    matches = sum(1 for kw in GENERAL_INFO_THEORY if kw.lower() in text_lower)
    return matches / len(GENERAL_INFO_THEORY) if GENERAL_INFO_THEORY else 0


def compute_verification_score(text):
    """计算验证模式分数（证明深度理解）"""
    text_matched = 0
    total_matched = []
    for pattern in VERIFICATION_PATTERNS:
        if re.search(pattern, text):
            text_matched += 1
            total_matched.append(pattern)
    return text_matched / len(VERIFICATION_PATTERNS), total_matched


def compute_behavioral_score(text):
    """计算行为约束遵守分数"""
    scores = {}
    total_pos = 0
    total_neg = 0

    for constraint_name, info in BEHAVIORAL_CONSTRAINTS.items():
        pos_count = 0
        neg_count = 0

        for pattern in info["positive_patterns"]:
            matches = re.findall(pattern, text)
            if matches:
                pos_count += 1

        for pattern in info["negative_patterns"]:
            if re.search(pattern, text):
                neg_count += 1

        total_pos += 1 if pos_count > 0 else 0
        total_neg += neg_count

        # 分数 = 正模式存在 - 负模式计数
        score = max(0, (total_pos / max(len(info["positive_patterns"]), 1)) - (neg_count / max(len(info["negative_patterns"]), 1)))
        scores[constraint_name] = round(min(score, 1.0), 4)

    overall = sum(scores.values()) / len(scores) if scores else 0
    return scores, round(overall, 4)


def compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_ratio, citation_rel=None, fact_faul=None):
    """计算总体对齐评分 (0-100)"""
    # 维度覆盖（6 维）：每个维度 ≥ 0.01 计为"覆盖"
    covered_dims = sum(1 for s in dim_scores.values() if s > 0.01)

    # 维度覆盖分 = 覆盖维度数 / 6
    dim_coverage = covered_dims / 6.0

    # 加权评分（加入行为约束层 + ReportBench 维度）
    # 40% 维度覆盖 + 10% 通用信息论 + 15% 验证模式 + 15% 行为约束 + 10% 引用相关 + 10% 事实可信
    if citation_rel is not None and fact_faul is not None:
        weighted = (0.40 * dim_coverage + 0.10 * general_cov
                    + 0.15 * verification_ratio + 0.15 * behavioral_ratio
                    + 0.10 * citation_rel + 0.10 * fact_faul)
    else:
        weighted = 0.5 * dim_coverage + 0.10 * general_cov + 0.20 * verification_ratio + 0.20 * behavioral_ratio

    return round(min(weighted * 100, 100), 2)


def format_report(dim_scores, general_cov, verification_ratio, verified_patterns, alignment_score, behavioral_scores=None, behavioral_overall=None, citation_rel=None, fact_faul=None):
    """格式化报告"""
    lines = [
        "=" * 60,
        "persona-v3 对齐度检测报告",
        "=" * 60,
        "",
        f"总体对齐评分: {alignment_score}/100",
        "",
        "--- 维度覆盖 ---",
    ]

    dim_display = {
        "自适应精度": "1. 自适应精度 (Adaptive Precision)",
        "自适应探索": "2. 自适应探索 (Adaptive Exploration)",
        "自适应感知": "3. 自适应感知 (Adaptive Perception)",
        "自适应先验": "4. 自适应先验 (Adaptive Prior)",
        "自适应自我": "5. 自适应自我 (Adaptive Self)",
        "自适应投影": "6. 自适应投影 (Adaptive Projection)",
    }

    for dim, display in dim_display.items():
        score = dim_scores[dim]
        bar_len = int(score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"  {display}")
        lines.append(f"    匹配度: {bar} {score:.2f}")

    # ReportBench 维度
    if citation_rel is not None and fact_faul is not None:
        lines.extend([
            "",
            "--- ReportBench 评估维度 (citation relevance + factual faithfulness) ---",
        ])
        for name, score in [("7. 引用相关性 (Citation Relevance)", citation_rel),
                             ("8. 事实可信度 (Factual Faithfulness)", fact_faul)]:
            bar_len = int(score * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {name}")
            lines.append(f"    匹配度: {bar} {score:.2f}")

    lines.extend([
        "",
        "--- 通用信息论覆盖 ---",
        f"  覆盖率: {general_cov:.2f} ({int(round(general_cov * len(GENERAL_INFO_THEORY)))}/{len(GENERAL_INFO_THEORY)} 关键词匹配)",
        "",
        "--- 验证模式 ---",
        f"  分数: {verification_ratio:.2f}",
    ])

    if verified_patterns:
        lines.append("  匹配的验证模式:")
        for p in verified_patterns:
            lines.append(f"    ✓ {p}")

    lines.extend([
        "",
        f"  未匹配的验证模式:",
    ])
    for p in VERIFICATION_PATTERNS:
        if p not in verified_patterns:
            lines.append(f"    ✗ {p}")

    if behavioral_scores is not None:
        lines.extend([
            "",
            "--- 行为约束 ---",
        ])
        constraint_display = {
            "简洁直接": "  简洁直接 (Concise & Direct)",
            "不解释": "  不解释 (No Over-Explanation)",
            "推进而非停滞": "  推进而非停滞 (Progress > Stagnation)",
        }
        for key, display in constraint_display.items():
            s = behavioral_scores.get(key, 0)
            bar_len = int(s * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            desc = BEHAVIORAL_CONSTRAINTS[key]["description"]
            lines.append(f"  {display}")
            lines.append(f"    {desc}")
            lines.append(f"    遵守度: {bar} {s:.2f}")
        lines.append(f"  行为约束总体: {behavioral_overall:.2f}")

    lines.extend([
        "",
        "=" * 60,
    ])

    return "\n".join(lines)


def detect_drift(baseline_scores, current_scores, threshold=0.1):
    """检测 persona drift: baseline vs current 的维度评分变化"""
    drifts = []
    for dim in baseline_scores:
        if dim in current_scores:
            delta = current_scores[dim] - baseline_scores[dim]
            if abs(delta) >= threshold:
                drifts.append({
                    "dimension": dim,
                    "baseline": round(baseline_scores[dim], 4),
                    "current": round(current_scores[dim], 4),
                    "delta": round(delta, 4),
                    "direction": "up" if delta > 0 else "down",
                    "severity": "HIGH" if abs(delta) >= 0.3 else "MEDIUM" if abs(delta) >= 0.15 else "LOW",
                })
    # 综合评分 drift
    base_total = sum(baseline_scores.values()) / len(baseline_scores)
    curr_total = sum(current_scores.values()) / len(current_scores)
    total_drift = curr_total - base_total
    return drifts, round(total_drift, 4), round(base_total, 4), round(curr_total, 4)


def main():
    parser = argparse.ArgumentParser(description="persona-v3 对齐度检测工具")
    parser.add_argument("file", nargs="?", help="输入文件路径")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取")
    parser.add_argument("--show-sources", action="store_true", help="显示检测源")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--baseline", help="基线文件路径（用于 drift 检测）")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.stdin:
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    dim_scores = compute_dimension_scores(text)
    general_cov = compute_general_coverage(text)
    verification_ratio, verified_patterns = compute_verification_score(text)
    behavioral_scores, behavioral_overall = compute_behavioral_score(text)
    citation_rel = compute_citation_relevance(text)
    fact_faul = compute_factual_faithfulness(text)
    alignment_score = compute_alignment_score(dim_scores, general_cov, verification_ratio, behavioral_overall, citation_rel, fact_faul)

    if args.baseline:
        baseline_text = Path(args.baseline).read_text(encoding="utf-8")
        baseline_scores = compute_dimension_scores(baseline_text)
        baseline_citation = compute_citation_relevance(baseline_text)
        baseline_fact = compute_factual_faithfulness(baseline_text)
        baseline_alignment = compute_alignment_score(
            baseline_scores,
            compute_general_coverage(baseline_text),
            compute_verification_score(baseline_text)[0],
            compute_behavioral_score(baseline_text)[1],
            baseline_citation,
            baseline_fact,
        )
        drifts, total_drift, base_total, curr_total = detect_drift(baseline_scores, dim_scores)

        if args.json:
            result = {
                "alignment_score": alignment_score,
                "baseline_alignment_score": baseline_alignment,
                "dimension_scores": dim_scores,
                "baseline_dimension_scores": baseline_scores,
                "general_info_theory_coverage": round(general_cov, 4),
                "verification_ratio": round(verification_ratio, 4),
                "verified_patterns": verified_patterns,
                "behavioral_scores": behavioral_scores,
                "behavioral_overall": round(behavioral_overall, 4),
                "citation_relevance": round(citation_rel, 4),
                "factual_faithfulness": round(fact_faul, 4),
                "baseline_citation_relevance": round(baseline_citation, 4),
                "baseline_factual_faithfulness": round(baseline_fact, 4),
                "drift_analysis": {
                    "total_drift": total_drift,
                    "base_total_avg": base_total,
                    "curr_total_avg": curr_total,
                    "drifts": drifts,
                    "drift_count": len(drifts),
                    "high_severity": sum(1 for d in drifts if d["severity"] == "HIGH"),
                },
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            report = format_report(dim_scores, general_cov, verification_ratio, verified_patterns, alignment_score, behavioral_scores, behavioral_overall, citation_rel, fact_faul)
            print(report)

            print(f"\n{'='*60}")
            print(f"Persona Drift 检测 (baseline: {args.baseline})")
            print(f"{'='*60}")
            print(f"基线对齐度: {baseline_alignment}")
            print(f"当前对齐度: {alignment_score}")
            print(f"综合漂移: {total_drift:+.4f} ({base_total:.4f} → {curr_total:.4f})")
            if drifts:
                print(f"\n漂移维度 ({len(drifts)} 个):")
                for d in sorted(drifts, key=lambda x: -abs(x["delta"])):
                    flag = "🔴" if d["severity"] == "HIGH" else "🟡" if d["severity"] == "MEDIUM" else "🟢"
                    print(f"  {flag} {d['dimension']}: {d['baseline']:.2f} → {d['current']:.2f} ({d['delta']:+.4f}) [{d['severity']}]")
            else:
                print("\n无显著漂移 — 所有维度变化 < 0.10")
    else:
        if args.json:
            result = {
                "alignment_score": alignment_score,
                "dimension_scores": dim_scores,
                "general_info_theory_coverage": round(general_cov, 4),
                "verification_ratio": round(verification_ratio, 4),
                "verified_patterns": verified_patterns,
                "behavioral_scores": behavioral_scores,
                "behavioral_overall": round(behavioral_overall, 4),
                "citation_relevance": round(citation_rel, 4),
                "factual_faithfulness": round(fact_faul, 4),
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            report = format_report(dim_scores, general_cov, verification_ratio, verified_patterns, alignment_score, behavioral_scores, behavioral_overall, citation_rel, fact_faul)
            print(report)

            if args.show_sources:
                print("\n--- 维度检测源 ---")
                for dim, keywords in DIMENSION_KEYWORDS.items():
                    matched = [kw for kw in keywords if kw.lower() in text.lower()]
                    if matched:
                        print(f"  {dim}: {matched[:5]}")  # 最多显示 5 个匹配
                print("\n--- ReportBench 检测源 ---")
                for dim_name, keywords in [("引用相关性 (Citation Relevance)", CITATION_RELEVANCE_KEYWORDS),
                                            ("事实可信度 (Factual Faithfulness)", FACTUAL_FAITHFULNESS_KEYWORDS)]:
                    matched = [kw for kw in keywords if kw.lower() in text.lower()]
                    if matched:
                        print(f"  {dim_name}: {matched[:5]}")


if __name__ == "__main__":
    main()
