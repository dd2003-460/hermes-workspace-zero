#!/usr/bin/env python3
"""
实时人格对齐监控器

在 Claude Code 会话中评估当前输出是否符合 persona-v3 的 6 维度框架。

用法（在 Claude Code 会话中）：
    # 评估当前回复文本
    python3 realtime_alignment_monitor.py --check "你的回复文本"

    # 或从文件读取
    python3 realtime_alignment_monitor.py --file response.md

    # JSON 输出
    python3 realtime_alignment_monitor.py --check "你的回复文本" --json

核心思想：persona-v3 的核心价值不在于覆盖多少维度，
而在于**在回答中自然应用** 成璐的思维习惯（信息论统一框架、贝叶斯闭环、追问机制）。
每个维度对应一个"思维习惯锚点"，如果回答中体现这些锚点，就说明 persona 被正确激活。
"""

import argparse
import json
import re
import sys
from pathlib import Path


DIMENSION_ANCHORS = {
    "自适应精度": {
        "description": "根据问题复杂度调整表达精度（rate-distortion, 压缩, 精度层级）",
        "patterns": [
            r"精度|层次|粒度|详细|简化|压缩|展开|rate.?distortion",
            r"对[^,。]*[^，。]*[^你你]输出|针对[^，。]*[^你你]给出|适合[^，。]*[^你你]",
        ],
        "behavioral": "识别问题复杂度并自动调整分析深度",
    },
    "自适应探索": {
        "description": "在探索新方法和利用现有方法之间动态平衡（磨刀理论, 探索频率）",
        "patterns": [
            r"探索|工具|方法|路径|替代|交叉|跨[^，。]*域|磨刀",
            r"先[^,，]*再[^,，]*|首先[^,，]*然后|第一步[^,，]*第二步",
            r"现有[^，。]*工具|已有[^，。]*脚本|重复造轮子|重复实现",
        ],
        "behavioral": "决策前检查工具复用，不重复造轮子",
    },
    "自适应感知": {
        "description": "根据信息密度分配感知时间资源",
        "patterns": [
            r"信息[^，。]*密度|关键[^，。]*信息|细节[^，。]*处理|快速处理|深入分析",
            r"高[^,，]*低[^,，]*|重点[^,，。]*一般[^,，。]|核心[^,，。]*外围",
            r"投入[^,，]*时间|分析[^,，]*深度|[^你]仔细[^你]*检查|[^你]仔细[^你]*推敲",
        ],
        "behavioral": "区分信息密度，对高价值内容投入更多分析",
    },
    "自适应先验": {
        "description": "使用贝叶斯推理框架，动态更新信念",
        "patterns": [
            r"贝叶斯|先验[^,，]*证据|后验|P\([^)]*\)",
            r"更新[^,，]*认知|修正[^,，]*信念|新[^,，。]*证据",
            r"如果[^,，]*那么|假设[^,，。]*则[^,，。]|[^不]一定[^,，。]*如果",
            r"概率[^,，]*更新|置信度[^,，]*调整",
        ],
        "behavioral": "使用 P(H|E) 框架更新认知，而非一次性断言",
    },
    "自适应自我": {
        "description": "从不同观测者视角导出规律，理解观察者的相对性",
        "patterns": [
            r"观测者[^,，]*视角|观察者|第一[^,，。]*人称|相对性|视角[^,，。]*切换",
            r"同一[^,，。]*不同[^,，。]*|[^你]可能[^你]*认为[^,，。]*而[^,，。]*从[^,，。]*看",
            r"主观[^,，。]*客观[^,，。]*|[^不]一定[^,，。]*取决于",
        ],
        "behavioral": "承认规律对观测者的依赖，不同视角可能导出不同规律",
    },
    "自适应投影": {
        "description": "在低维投影中发现跨域同构和类比",
        "patterns": [
            r"跨[^,，。]*域[^,，。]*类比|同构[^,，。]*|映射[^,，。]*结构",
            r"类似[^,，。]*问题[^,，。]*在|[^你]类比[^你]*到[^,，。]*|[^你]*相当于[^,，。]*",
            r"物理[^,，。]*社会[^,，。]*|数学[^,，。]*语言[^,，。]*|信息[^,，。]*处理[^,，。]*信道",
        ],
        "behavioral": "主动在不同领域间发现深层同构关系",
    },
}

VERIFICATION_PATTERNS = [
    (r"为什么[^,，。]*不是[^,，。]*而是", "为什么...不是...而是 — 追问本质"),
    (r"追问[^,，。]*边界|在什么条件下不成立", "追问边界条件"),
    (r"等价[^,，。]*|[^同]构[^,，。]*|[^映]射[^,，。]*保持", "等价/同构/映射关系"),
    (r"不同[^,，。]*[^视角]*[^间]*[^切换]*[^中]*[^下]*[^到]*[^从]*[^上]*[^之]*[^面]*[^论]*[^关]*[^系]*", "在不同语境中讨论同一问题"),
    (r"边界[^,，。]*条件[^,，。]*|[^不]确定[^,，。]*范围", "明确边界条件"),
]

GENERAL_INFO_THEORY = [
    "信息论", "熵", "互信息", "KL散度", "香农", "信道", "编码",
    "压缩", "率失真", "冗余", "比特", "token", "语言模型",
    "信息密度", "信息流", "信息结构", "马尔可夫", "贝叶斯",
    "后验", "先验", "似然", "随机过程", "动力学", "相变",
    "涌现", "自组织", "反馈", "熵增", "熵减", "粗粒化",
    "coarse.?grain", "mutual.?information", "KL.?divergence",
]

BEHAVIORAL_ANCHORS = {
    "简洁直接": {
        "description": "输出简洁直接，少空话多证据",
        "positive_patterns": [
            r"结论[^,：:]", r"核心[^,：:]", r"直接[^,，。]*回答",
            r"关键[^,：:]", r"答案是", r"本质是",
        ],
        "negative_patterns": [
            r"总的来说[^,，。]*", r"综上所述[^,，。]*",
            r"首先[^,，。]*[^你你]*[^让让]*[^让让]*其次[^,，。]*[^你你]*[^让让]*[^让让]*最后[^,，。]*[^你你]*[^让让]*[^让让]*",
            r"第一[^,，。]*[^你你]*[^让让]*[^让让]*第二[^,，。]*[^你你]*[^让让]*[^让让]*第三",
        ],
    },
    "不解释": {
        "description": "不解释已知概念，不重复用户问题，不展示思考过程",
        "positive_patterns": [
            # 直接性标记
            r"结论", r"答案是", r"本质是", r"核心是", r"关键是",
            # 假设/条件表达
            r"假设[^,，。]*", r"如果[^,，。]*[^,，。]*那么", r"设[^,，。]*",
            # 视角/分析框架
            r"根据[^,，。]*[^你你]*分析", r"从[^,，。]*[^你你]*视角",
            # 行动导向
            r"接下来", r"下一步", r"需要[^,，。]*检查", r"应该[^,，。]*验证",
            # 证据/推理链
            r"因为[^,，。]*证明", r"由[^,，。]*推出", r"符合[^,，。]*",
            # 结构化输出
            r"\d+\)\s", r"\d+\.\s", r"^[12345]\.",
        ],
        "negative_patterns": [
            # 解释性语言
            r"这是因为[^,，。]*", r"换句话说[^,，。]*", r"这意味着[^,，。]*",
            r"也就是说[^,，。]*", r"让我来[^,，。]*解释",
            # 重复用户
            r"用户[^,，。]*提到[^,，。]*的", r"你[^,，。]*问[^,，。]*的",
            # 思考过程展示
            r"首先[^,，。]*[^让让]*[^你你]*[^让让]*[^思考]*[^想]*[^一]*",
            r"我需要[^,，。]*先[^,，。]*[^理理解]*[^了了解]*",
            r"我觉[^我]得[^你]*[^你]*[^说]",
        ],
    },
    "推进而非停滞": {
        "description": "每轮推进具体动作，不重复循环，不等待确认",
        "positive_patterns": [
            r"接下来[^,，。]*", r"下一步[^,，。]*", r"已经[^,，。]*完成",
            r"正在[^,，。]*进行[^,，。]*中", r"执行[^,，。]*中",
            r"工具[^,，。]*调[^用]",
        ],
        "negative_patterns": [
            r"等待[^,，。]*确认", r"等你[^,，。]*回复", r"请[^,，。]*指示",
            r"你觉得[^,，。]*如何", r"需要[^,，。]*我[^,，。]*继续[^,，。]*吗",
            r"要我[^,，。]*继续[^,，。]*吗",
        ],
    },
}


def score_text(text):
    """评估文本的 persona-v3 对齐度"""
    dim_scores = {}
    matched_dims = []

    for dim, info in DIMENSION_ANCHORS.items():
        count = 0
        for pattern in info["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)

        max_possible = max(len(info["patterns"]), 1)
        score = min(count / max_possible, 1.0)

        dim_scores[dim] = round(score, 4)

        if score > 0:
            matched_dims.append(dim)

    # General information theory coverage
    info_matches = sum(
        1 for kw in GENERAL_INFO_THEORY
        if re.search(kw, text, re.IGNORECASE)
    )
    general_cov = min(info_matches / len(GENERAL_INFO_THEORY), 1.0)

    # Verification patterns
    ver_matches = 0
    ver_matched_names = []
    for pattern, name in VERIFICATION_PATTERNS:
        if re.search(pattern, text):
            ver_matches += 1
            ver_matched_names.append(name)

    ver_total = len(VERIFICATION_PATTERNS)

    # Behavioral anchors
    behavioral_scores = {}
    total_behavioral = 0
    for bname, binfo in BEHAVIORAL_ANCHORS.items():
        pos = 0
        neg = 0
        for p in binfo["positive_patterns"]:
            if re.search(p, text):
                pos += 1
        for p in binfo["negative_patterns"]:
            if re.search(p, text):
                neg += 1
        # Score = positive presence - negative penalty
        score = max(0, (pos / max(len(binfo["positive_patterns"]), 1)) - (neg / max(len(binfo["negative_patterns"]), 1)))
        behavioral_scores[bname] = round(min(score, 1.0), 4)
        total_behavioral += score

    behavioral_overall = round(total_behavioral / len(BEHAVIORAL_ANCHORS), 4) if BEHAVIORAL_ANCHORS else 0

    # Composite score
    dim_coverage = len(matched_dims) / len(DIMENSION_ANCHORS)
    dim_weighted = sum(dim_scores.values()) / len(dim_scores)

    # Final score (50% dimensions, 10% info theory, 20% verification, 20% behavioral)
    final = (
        50.0 * dim_weighted +
        10.0 * general_cov +
        20.0 * (ver_matches / ver_total) +
        20.0 * behavioral_overall
    )

    return {
        "alignment_score": round(final, 2),
        "dimension_scores": dim_scores,
        "matched_dimensions": matched_dims,
        "dimension_coverage": round(dim_coverage, 4),
        "general_cov": round(general_cov, 4),
        "general_keyword_count": len(GENERAL_INFO_THEORY),
        "verification_ratio": round(ver_matches / ver_total, 4),
        "verification_total": ver_total,
        "verification_matches": ver_matches,
        "verification_matched": ver_matched_names,
        "behavioral_scores": behavioral_scores,
        "behavioral_overall": behavioral_overall,
    }


def print_report(data):
    """打印报告"""
    print("=" * 60)
    print("实时人格对齐监控报告")
    print("=" * 60)
    print(f"\n总体对齐评分: {data['alignment_score']}/100")
    print(f"维度覆盖: {int(round(data['dimension_coverage'] * len(DIMENSION_ANCHORS)))}"
          f"/{len(DIMENSION_ANCHORS)} 维度")
    print()

    for dim, score in data["dimension_scores"].items():
        blocks = int(round(score * 20))
        bar = "█" * blocks + "█▌" * (20 - blocks)
        print(f"  {dim}: {bar} {score:.2f}")

    print(f"\n通用信息论覆盖: {data['general_cov']:.0%}"
          f" ({int(round(data['general_cov'] * data['general_keyword_count']))}"
          f"/{data['general_keyword_count']})")

    print(f"\n验证模式: {data['verification_ratio']:.2f}"
          f" ({data['verification_matches']}/{data['verification_total']})")
    for name in data["verification_matched"]:
        print(f"  ✓ {name}")

    print("\n" + "=" * 60)

    # Behavioral anchors report
    if "behavioral_scores" in data:
        print("\n--- 行为约束 ---")
        bdisplay = {
            "简洁直接": "  简洁直接 (Concise & Direct)",
            "不解释": "  不解释 (No Over-Explanation)",
            "推进而非停滞": "  推进而非停滞 (Progress > Stagnation)",
        }
        for bname, display in bdisplay.items():
            bs = data["behavioral_scores"].get(bname, 0)
            blocks = int(round(bs * 20))
            bar = "█" * blocks + "░" * (20 - blocks)
            desc = BEHAVIORAL_ANCHORS[bname]["description"]
            print(f"{display}")
            print(f"  {desc}")
            print(f"  遵守度: {bar} {bs:.2f}")
        print(f"  行为约束总体: {data['behavioral_overall']:.2f}")

    # Diagnostic
    low_dims = [d for d, s in data["dimension_scores"].items() if s < 0.1]
    if low_dims:
        print(f"\n警告: 以下维度未体现: {', '.join(low_dims)}")
        print(f"建议: 在下次回答中有意识地引入这些思维锚点")


def main():
    parser = argparse.ArgumentParser(description="实时人格对齐监控器")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", "-c", help="要评估的回复文本")
    group.add_argument("--file", "-f", help="从文件读取评估文本")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if args.check:
        text = args.check
    else:
        text = Path(args.file).read_text(encoding="utf-8")

    data = score_text(text)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
