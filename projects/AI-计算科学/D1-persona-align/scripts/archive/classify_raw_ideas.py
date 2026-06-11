#!/usr/bin/env python3
"""
Raw idea classifier and indexer for raw.md.

Reads raw.md, extracts all ideas (marked with ❏), classifies them into
domains, assigns actionability scores, and produces a structured index.

Usage:
    python classify_raw_ideas.py [raw.md path]
"""

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# Domain keywords for classification (Chinese + English)
DOMAIN_KEYWORDS = {
    "ai_training": ["ai训练", "训练数据", "rag", "检索", "cot", "链式推理", "模型大小",
                     "ai训练", "token", "词元", "embedding", "pretrain", "微调", "lora",
                     "transformer", "注意力", "上下文", "kv cache"],
    "ai_reasoning": ["推理", "规划能力", "agent", "coding agent", "clicoding",
                      "规划", "tool", "工具", "路由", "搜索", "web"],
    "information_theory": ["信息论", "信息因子", "信道容量", "冗余", "压缩", "编码",
                            "解码", "互信息", "熵", "Kolmogorov", "信息密度"],
    "social_science": ["社科", "社会学", "群体", "模因", "舆论", "信用", "文化",
                        "男女", "行为惯性", "人际关系", "恋爱", "婚姻", "消费",
                        "社会舆论", "历史周期率", "自证预言", "正反馈", "负反馈"],
    "mathematics": ["数学", "同调群", "几何", "算法效率", "线性代数", "积分",
                     "微分", "范数", "内积", "度量", "流形", "拓扑", "微扰",
                     "概率", "统计", "动力学", "优化", "泛函"],
    "cross_domain": ["交叉", "量化", "气体动理论", "市场建模", "流量经济",
                      "科学计算", "变步长", "生物神经网络", "仿生", "泥地", "高速路",
                      "分类", "正交化", "分析", "方法论"],
    "philosophy": ["生命", "死亡", "意识", "存在", "感知", "直觉", "本质",
                    "世界模型", "智能", "选择压力", "相变", "定义"],
    "practical": ["小说", "笔记", "idea", "反注入prompt", "安全", "长期守则",
                   "硬编码", "自适应token", "图形界面", "openclaw", "记忆系统"],
}

# Actionability criteria
ACTIONABLE_KEYWORDS = ["算法", "工具", "脚本", "实现", "代码", "搜索", "验证",
                        "评测", "实验", "构建", "部署", "编译", "修复", "优化"]

NON_ACTIONABLE_KEYWORDS = ["是否", "为什么", "如果", "什么", "能否", "意义", "本质"]


def extract_ideas(raw_path: str) -> list[dict]:
    """Extract all ideas from raw.md file."""
    text = Path(raw_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    ideas = []
    current_section = None

    for line in lines:
        # Detect section headers (non-indented lines that are not idea markers)
        if "❏" not in line and line.strip() and not line.startswith(" "):
            if "idea" in line.lower() or "openclaw" in line.lower() or "小说" in line.lower():
                current_section = line.strip()
            continue

        # Extract idea
        match = re.match(r'\s*❏\s*(.*)', line)
        if match:
            idea_text = match.group(1).strip()
            if idea_text:
                ideas.append({
                    "text": idea_text,
                    "section": current_section,
                })

    return ideas


def classify_idea(idea_text: str) -> str:
    """Classify an idea into a domain based on keyword matching."""
    scores = defaultdict(float)

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in idea_text:
                scores[domain] += 1

    if not scores or max(scores.values()) == 0:
        return "uncategorized"

    return max(scores, key=scores.get)


def actionability_score(idea_text: str) -> str:
    """Score how actionable an idea is."""
    actionable_count = sum(1 for kw in ACTIONABLE_KEYWORDS if kw in idea_text)
    non_actionable_count = sum(1 for kw in NON_ACTIONABLE_KEYWORDS if kw in idea_text)

    # Link-based ideas
    if "http" in idea_text:
        return "external_ref"

    if actionable_count > non_actionable_count + 1:
        return "high"
    elif actionable_count > 0 or non_actionable_count == 0:
        return "medium"
    elif non_actionable_count > 0:
        return "low"
    return "medium"


def generate_index(ideas: list[dict], classifications: list[str], action_scores: list[str]):
    """Generate and print a structured index."""
    # Group by domain
    by_domain = defaultdict(list)
    for idea, domain, score in zip(ideas, classifications, action_scores):
        by_domain[domain].append((idea, score))

    # Print summary
    total = len(ideas)
    print(f"# Raw Ideas Index — {total} ideas classified")
    print(f"Generated: 2026-05-24")
    print()

    domain_counts = defaultdict(int)
    for d in classifications:
        domain_counts[d] += 1

    print("## Domain Distribution"),
    print()
    for domain in sorted(domain_counts, key=domain_counts.get, reverse=True):
        if domain == "uncategorized":
            continue
        count = domain_counts[domain]
        bar = "█" * count + "░" * (max(domain_counts.values()) - count)
        print(f"  {domain:20s} {bar} ({count})")

    uncategorized = domain_counts.get("uncategorized", 0)
    if uncategorized > 0:
        print(f"  {'uncategorized':20s} {'░' * max(domain_counts.values())} ({uncategorized})")

    print()
    print("## Actionability Distribution")
    print()
    action_counts = defaultdict(int)
    for s in action_scores:
        action_counts[s] += 1
    for level in ["high", "medium", "low", "external_ref"]:
        if level in action_counts:
            count = action_counts[level]
            print(f"  {level:10s}: {count}")

    print()
    print("## Ideas by Domain")
    print()

    for domain in sorted(domain_counts, key=domain_counts.get, reverse=True):
        if domain == "uncategorized":
            continue
        items = by_domain[domain]
        print(f"### {domain}")
        print()
        for i, (idea, score) in enumerate(items, 1):
            # Truncate long texts
            display = idea[:80] + "..." if len(idea) > 80 else idea
            print(f"  {i}. [{score:6s}] {display}")
        print()

    # Uncategorized
    if uncategorized > 0:
        print("### uncategorized")
        print()
        for i, (idea, score) in enumerate(by_domain["uncategorized"], 1):
            display = idea[:80] + "..." if len(idea) > 80 else idea
            print(f"  {i}. [{score:6s}] {display}")
        print()

    # Save structured JSON
    structured = []
    for idea, domain, score in zip(ideas, classifications, action_scores):
        structured.append({
            "text": idea["text"],
            "section": idea["section"],
            "domain": domain,
            "actionability": score,
        })

    output_path = Path(__file__).parent.parent / "memory" / "raw-ideas-index.json"
    output_path.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"## Structured index saved to: {output_path}")


def main():
    raw_path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "raw" / "raw.md"
    raw_path = Path(raw_path)

    if not raw_path.exists():
        print(f"Error: {raw_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {raw_path}...")
    ideas = extract_ideas(str(raw_path))
    print(f"Extracted {len(ideas)} ideas.")

    classifications = [classify_idea(idea["text"]) for idea in ideas]
    action_scores = [actionability_score(idea["text"]) for idea in ideas]

    generate_index(ideas, classifications, action_scores)


if __name__ == "__main__":
    main()
