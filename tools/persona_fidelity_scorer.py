#!/usr/bin/env python3
"""
persona_fidelity_scorer.py — T5a 自动保真度评分工具

基于 T2 的 6 个量化指标评估 LLM 输出与原始 persona 的对齐程度：
1. 问句比例 (target: 0.15-0.55, weighted questions + exploratory)
2. 跨域系数 (target: >0.3, Shannon entropy of domain vocabulary)
3. 不确定性标记 (target: >0.15, ratio of sentences with uncertainty markers)
4. 块状结构 (target: >0.15, weighted block markers + paragraph breaks)
5. 隐喻使用 (target: >0.10, fraction of metaphor vocabulary present)
6. 风格相似度 (auxiliary, based on lexical overlap)

Usage:
    python persona_fidelity_scorer.py --reference raw.md --candidate output.txt
    python persona_fidelity_scorer.py --reference raw.md --score-only --sample "test output"
"""

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from typing import Optional

# ============================================================
# Domain vocabulary for cross-domain coefficient calculation
# ============================================================
DOMAINS = {
    "ai": [
        "agent", "token", "prompt", "训练", "模型", "学习", "推理", "编码",
        "解码", "上下文", "embedding", "attention", "transformer", "fine-tune",
        "微调", "RLHF", "对齐", "输出", "输入", "loss", "梯度", "backprop",
        "coding", "web", "API", "rag", "retrieval", "vector", "embedding"
    ],
    "physics": [
        "引力", "反馈", "负反馈", "正反馈", "噪声", "放大", "稳定",
        "演化", "动力学", "热力学", "熵", "量子", "波", "粒子", "场",
        "势", "势阱", "能级", "跃迁", "谐振", "混沌", "Lyapunov", "KAM",
        "引力波", "PTA", "EMRI", "黑洞", "视界", " Hawking", "红移"
    ],
    "math": [
        "映射", "双射", "同构", "同调", "范畴", "函子", "自然变换",
        "内积", "范数", "度量", "拓扑", "流形", "向量", "矩阵", "行列式",
        "特征值", "奇异值", "分解", "优化", "约束", "拉格朗日", "KKT",
        "概率", "分布", "期望", "方差", "贝叶斯", "马尔可夫", "蒙特卡洛"
    ],
    "social": [
        "社会", "制度", "舆论", "模因", "文化", "群体", "个体", "行为",
        "决策", "选择", "博弈", "均衡", "市场", "经济", "信用", "实名",
        "性别", "男女", "亲情", "友情", "爱情", "家庭", "教育", "权力"
    ],
    "philosophy": [
        "存在", "本质", "意识", "认识", "真理", "认知", "本体", "现象",
        "还原", "涌现", "第一性", "因果", "必然", "偶然", "自由", "决定论",
        "还原论", "整体论", "二元", "连续", "离散", "无限"
    ],
    "methodology": [
        "方法", "工具", "流程", "步骤", "框架", "范式", "原则", "标准",
        "验证", "测试", "实验", "假设", "证伪", "反例", "边界", "条件",
        "精度", "效率", "复杂度", "压缩", "编码", "信息", "冗余"
    ]
}

# ============================================================
# Chinese question sentence markers
# ============================================================
QUESTION_MARKERS = ["？", "?", "呢", "吗", "是否", "为什么", "怎么", "如何",
                    "什么", "哪里", "谁", "哪", "几", "多少", "有吗", "吗？", "呢？"]

# ============================================================
# Uncertainty markers
# ============================================================
UNCERTAINTY_MARKERS = ["可能", "是否", "或许", "大概", "似乎", "也许",
                       "或许", "大概", "可能吗", "不确定", "存疑", "需要验证"]

# ============================================================
METAPHOR_WORDS = [
    "引力", "反馈", "信道", "容量", "冗余", "管子", "流水",
    "阈值", "平衡", "双射", "自由度", "优化", "压缩",
    "耦合", "解耦", "波", "噪声", "放大", "稳定", "熵",
    "流形", "度量", "距离", "范数", "内积", "映射", "同构",
    "范畴", "函子", "涌现", "还原", "粒度", "分辨率"
]

# ============================================================
# Qwen thinking process stripper
# ============================================================
def strip_qwen_thinking(text: str) -> str:
    """Strip Qwen model's built-in thinking process from output.
    Qwen models often output:
    1. "Here's a thinking process:" header
    2. Numbered thinking steps
    3. "(Start directly...)" transition
    4. English self-analysis before Chinese response
    5. Actual response
    This function strips everything up to and including the thinking process.
    """
    # Pattern 1: Look for "(Start directly" or "(*Start" as a transition marker
    patterns = [
        r'\(Start directly',
        r'\(\*Start\*',
        r"Here's my response:",
        r"Here is my response:",
        r"---",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return text[match.end():].strip()

    # Pattern 2: Strip from "Here's a thinking process:" to the last numbered step
    thinking_match = re.search(r"Here's a thinking process:", text)
    if thinking_match:
        # Find the first Chinese paragraph after the thinking
        chinese_text = re.search(r'[一-鿿].{50,}', text[thinking_match.start():])
        if chinese_text:
            return text[thinking_match.start() + chinese_text.start():].strip()

    # Pattern 3: Detect and strip English thinking content at the start.
    # Some models output English self-analysis before the actual response.
    # The English section contains bullet points, English text, or analysis markers.
    # The actual response starts with a sustained Chinese paragraph.
    lines = text.split('\n')

    # Look for the first "sustained Chinese paragraph" (5+ consecutive Chinese lines)
    chinese_run_start = None
    chinese_run = 0
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        has_chinese = bool(re.search(r'[一-鿿]', stripped_line))
        has_english = bool(re.search(r'[a-zA-Z]{3,}', stripped_line))
        if has_chinese and not has_english:
            chinese_run += 1
            if chinese_run == 3 and chinese_run_start is None:
                chinese_run_start = i - 2  # Back up a bit
        elif has_english and not has_chinese:
            chinese_run = 0
            chinese_run_start = None
        elif has_chinese and has_english:
            # Mixed line — treat as break
            chinese_run = 0
            chinese_run_start = None

    if chinese_run_start is not None and chinese_run_start > 0:
        candidate = '\n'.join(lines[chinese_run_start:]).strip()
        # Verify the candidate has substantial Chinese content
        cn_count = len(re.findall(r'[一-鿿]', candidate))
        if cn_count > 200:
            return candidate

    return text


def tokenize_chinese(text: str) -> list:
    """Simple Chinese tokenizer: character-level + word-level from domain vocab."""
    chars = list(text)
    # Also find multi-char words from all domain vocabularies
    all_words = [w for words in DOMAINS.values() for w in words]
    found_words = set()
    for w in all_words:
        if w in text:
            found_words.add(w)
    return chars + list(found_words)


def count_sentences(text: str) -> int:
    """Count sentence endings in Chinese text."""
    ends = len(re.findall(r'[。！？;；\n]', text))
    return max(ends, 1)


def count_question_sentences(text: str) -> int:
    """Count sentences that end with or contain question markers."""
    sentences = re.split(r'[。！？;；\n]', text)
    count = 0
    for s in sentences:
        s_stripped = s.strip()
        if not s_stripped:
            continue
        for marker in QUESTION_MARKERS:
            if marker in s_stripped:
                count += 1
                break
    return count


def calc_question_ratio(text: str) -> float:
    """Ratio of actual questions + exploratory statements to total sentences.
    Target: 0.25-0.55 (exploring the persona's tendency toward questioning).
    Only sentences ending with ?/？ count as actual questions.
    Sentences containing rhetorical markers (呢, 吗) but NOT ending with ?
    are counted as exploratory statements.
    """
    sentences = re.split(r'[。！？;；\n]', text)
    total = max(len([s for s in sentences if s.strip()]), 1)

    actual_questions = 0
    exploratory = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        is_question_end = s.endswith('？') or s.endswith('?')
        has_rhetorical = any(m in s for m in ['呢', '吗', '是否', '有没有可能'])

        if is_question_end:
            actual_questions += 1
        elif has_rhetorical:
            # Count as exploratory (not a full question, but shows questioning style)
            exploratory += 1

    # Blend: actual questions count fully, exploratory statements count at 0.5
    weighted = actual_questions + 0.5 * exploratory
    return weighted / total if total > 0 else 0.0


def calc_cross_domain_coefficient(text: str) -> float:
    """Entropy-based cross-domain diversity. Target: >0.3."""
    domain_counts = defaultdict(int)
    for domain, words in DOMAINS.items():
        for w in words:
            count = text.count(w)
            domain_counts[domain] += count

    active_domains = [d for d in domain_counts if domain_counts[d] > 0]
    if len(active_domains) <= 1:
        return 0.0

    total_hits = sum(domain_counts.values())
    probs = [domain_counts[d] / total_hits for d in active_domains]
    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    max_entropy = math.log(len(active_domains))
    return entropy / max_entropy if max_entropy > 0 else 0.0


def calc_uncertainty_marker_ratio(text: str) -> float:
    """Ratio of sentences containing uncertainty markers. Target: >0.15."""
    sentences = re.split(r'[。！？;；\n]', text)
    total = max(len([s for s in sentences if s.strip()]), 1)
    with_marker = sum(
        1 for s in sentences
        if any(m in s for m in UNCERTAINTY_MARKERS) and s.strip()
    )
    return with_marker / total



def calc_block_structure_ratio(text: str) -> float:
    """Ratio of independent thinking blocks.
    Primary: counts ❏ markers (high weight), paragraph breaks, and transition words.
    Raw.md has 55 ❏ markers with 82 lines — the ❏ format is the dominant structure.
    Prose-style persona writing uses paragraph breaks and transition words instead.
    Target: >0.15 for both formats.
    """
    # Primary: explicit block markers (❏ has high weight since it's the primary persona format)
    block_markers = text.count("❏") * 2.0

    # Paragraph breaks
    para_breaks = text.count("\n\n")

    # Secondary: transition words (weighted at 0.5)
    transition_count = 0
    for t in ["但是", "如果", "然而", "不过", "同时", "另一方面", "此外", "另外", "进一步"]:
        transition_count += text.count(t)

    total_blocks = block_markers + para_breaks + 0.5 * transition_count
    total_sentences = count_sentences(text)

    if total_sentences <= 1:
        return 0.5  # neutral for single-sentence texts

    ratio = total_blocks / max(total_sentences, 1)
    return min(max(ratio, 0.0), 1.0)


def calc_metaphor_ratio(text: str) -> float:
    """Metaphor presence score: how many of the 33 metaphor words appear. Target: >0.10."""
    found = sum(1 for mw in METAPHOR_WORDS if mw in text)
    return found / len(METAPHOR_WORDS)


def calc_lexical_overlap(reference: str, candidate: str) -> float:
    """N-gram overlap between reference and candidate. Auxiliary metric."""
    def get_ngrams(text, n=2):
        tokens = tokenize_chinese(text)
        return set(''.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1))

    ref_ngrams = get_ngrams(reference, 2)
    cand_ngrams = get_ngrams(candidate, 2)

    if not ref_ngrams or not cand_ngrams:
        return 0.0

    intersection = ref_ngrams & cand_ngrams
    return len(intersection) / max(len(ref_ngrams | cand_ngrams), 1)


def compute_fidelity_score(reference: str, candidate: str, verbose: bool = True) -> dict:
    """Compute full fidelity score. Returns dict with individual metrics and overall score."""

    candidate = strip_qwen_thinking(candidate)

    scores = {
        "question_ratio": {
            "value": calc_question_ratio(candidate),
            "target_min": 0.15,
            "target_max": 0.55,
            "pass": 0.15 <= calc_question_ratio(candidate) <= 0.55,
        },
        "cross_domain": {
            "value": calc_cross_domain_coefficient(candidate),
            "target_min": 0.30,
            "target_max": 1.0,
            "pass": calc_cross_domain_coefficient(candidate) > 0.30,
        },
        "uncertainty": {
            "value": calc_uncertainty_marker_ratio(candidate),
            "target_min": 0.15,
            "target_max": 1.0,
            "pass": calc_uncertainty_marker_ratio(candidate) > 0.15,
        },
        "block_structure": {
            "value": calc_block_structure_ratio(candidate),
            "target_min": 0.15,
            "target_max": 1.0,
            "pass": calc_block_structure_ratio(candidate) > 0.15,
        },
        "metaphor_ratio": {
            "value": calc_metaphor_ratio(candidate),
            "target_min": 0.10,  # at least 10% of metaphor vocab present (3/30 words)
            "target_max": 1.0,
            "pass": calc_metaphor_ratio(candidate) > 0.10,
        },
        "lexical_overlap": {
            "value": calc_lexical_overlap(reference, candidate),
            "target_min": 0.0,
            "target_max": 1.0,
            "pass": True,  # auxiliary only
        },
    }

    # Calculate overall score
    # Only count non-auxiliary metrics (exclude lexical_overlap)
    key_metrics = {k: v for k, v in scores.items() if k != "lexical_overlap"}
    passing = sum(1 for k, v in key_metrics.items() if v.get("pass", True))
    total = len(key_metrics)
    overall = passing / total

    # Penalize if less than 75% of key metrics pass
    if passing < total * 0.75:
        penalty = passing / total
        overall = overall * penalty

    scores["overall_fidelity"] = {
        "value": overall,
        "passing_metrics": passing,
        "total_metrics": total,
        "pass": overall >= 0.5 and passing >= total * 0.75,
    }

    if verbose:
        print("=" * 60)
        print("Persona Fidelity Score (T5a Evaluation)")
        print("=" * 60)
        for k, v in scores.items():
            if k == "overall_fidelity":
                print(f"\nOverall Fidelity: {v['value']:.2%}")
                print(f"  Metrics passing: {v['passing_metrics']}/{v['total_metrics']}")
                print(f"  Verdict: {'PASS' if v['pass'] else 'FAIL'}")
            else:
                status = "✅" if v["pass"] else "❌"
                print(f"  {status} {k}: {v['value']:.4f} (target: {v['target_min']}-{v['target_max']} or {v['target_min']}+)")
        print("=" * 60)

    return scores


def main():
    parser = argparse.ArgumentParser(description="Persona Fidelity Scorer (T5a)")
    parser.add_argument("--reference", help="Path to reference persona text (raw.md)")
    parser.add_argument("--candidate", help="Path to candidate output to score")
    parser.add_argument("--score-only", action="store_true", help="Score inline sample")
    parser.add_argument("--sample", help="Inline text to score (use with --score-only)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--self-score", action="store_true", help="Score the reference itself (baseline)")

    args = parser.parse_args()

    reference_text = ""
    candidate_text = ""

    if args.reference:
        with open(args.reference, "r", encoding="utf-8") as f:
            reference_text = f.read()

    if args.self_score:
        # Score reference text against itself (baseline maximum fidelity)
        result = compute_fidelity_score(reference_text, reference_text)
    elif args.candidate:
        with open(args.candidate, "r", encoding="utf-8") as f:
            candidate_text = f.read()
        result = compute_fidelity_score(reference_text, candidate_text)
    elif args.score_only and args.sample:
        # Score inline sample (no reference comparison)
        print("Scoring inline sample (no reference comparison):")
        result = compute_fidelity_score("", args.sample)
    else:
        print("Usage:")
        print("  python persona_fidelity_scorer.py --reference raw.md --candidate output.txt")
        print("  python persona_fidelity_scorer.py --reference raw.md --self-score")
        print("  python persona_fidelity_scorer.py --score-only --sample 'test text'")
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
