#!/usr/bin/env python3
"""
persona-v3 section-level alignment test

将 prompt 按维度章节拆分，评估每章在其对应维度上的对齐度 vs 其他维度。
检测"keyword mention vs actual embodiment"问题——一个讨论精度的章节可能只是
提到精度术语，但没有真正体现高精度推理风格。

Usage:
    python3 section_alignment_test.py
"""

import sys
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROMPT_FILE = PROJECT_ROOT / "persona-v3-prompt.txt"

# Import shared keyword library
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from persona_keywords import DIMENSION_KEYWORDS, compute_dimension_scores


def load_prompt():
    if not PROMPT_FILE.exists():
        print(f"ERROR: {PROMPT_FILE} not found")
        sys.exit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")


def split_sections(text):
    """按 ### 级别标题拆分 prompt 为 section dict."""
    sections = {}
    lines = text.split("\n")
    current_key = None
    current_lines = []

    for line in lines:
        if line.startswith("### "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines)
            key = line[4:].strip()
            current_key = key
            current_lines = [line]
        elif current_key is not None:
            current_lines.append(line)
        else:
            # preamble before any ### header
            if "preamble" not in sections:
                sections["preamble"] = []
            sections["preamble"].append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines)

    # Ensure preamble is also a joined string
    if "preamble" in sections and isinstance(sections["preamble"], list):
        sections["preamble"] = "\n".join(sections["preamble"])

    return sections


def dimension_hotspot_score(text, target_dim, all_dims):
    """计算 text 在 target_dim 上的得分 vs 在其他 dim 上的得分。

    Returns:
        hotspot_ratio: target_dim_score / sum(all_scores) — 越高说明越聚焦
        scores: {dim: score}
    """
    scores = compute_dimension_scores(text)
    total = sum(scores.values())
    if total < 1e-10:
        return 0.0, scores

    hotspot = scores.get(target_dim, 0.0) / total
    return hotspot, scores


def expected_dimension_for_section(section_name, all_dim_names):
    """判断 section 名称对应哪个预期维度。"""
    dim_keywords_map = {
        "自适应精度": ["精度"],
        "自适应探索": ["探索"],
        "自适应感知": ["感知"],
        "自适应先验": ["先验"],
        "自适应自我": ["自我", "观测者"],
        "自适应投影": ["投影", "跨域", "同构"],
    }

    for dim, keywords in dim_keywords_map.items():
        if any(kw in section_name for kw in keywords):
            return dim

    return None


def main():
    text = load_prompt()
    sections = split_sections(text)
    all_dim_names = list(DIMENSION_KEYWORDS.keys())

    print("=" * 60)
    print("Section-Level Alignment Test")
    print("=" * 60)
    print(f"Prompt: {PROMPT_FILE.name} ({len(text)} chars, {len(sections)} sections)")
    print()

    results = []
    for sec_name, sec_text in sections.items():
        expected = expected_dimension_for_section(sec_name, all_dim_names)
        hotspot, scores = dimension_hotspot_score(sec_text, sec_name if expected is None else expected, all_dim_names)

        results.append({
            "section": sec_name,
            "expected_dim": expected,
            "hotspot_ratio": hotspot,
            "scores": scores,
        })

        top_dim = max(scores.items(), key=lambda x: x[1])
        status = "OK" if top_dim[0] == expected or expected is None else f"MISMATCH (expected {expected})"

        print(f"  [{status}] {sec_name}")
        if expected:
            print(f"    Expected dim: {expected}")
        print(f"    Hotspot ratio: {hotspot:.3f} (target / total)")
        print(f"    Top dimension: {top_dim[0]} = {top_dim[1]:.4f}")
        dim_scores_str = ", ".join(f"{k}: {v:.4f}" for k, v in sorted(scores.items(), key=lambda x: -x[1]))
        print(f"    All dims: {dim_scores_str}")
        print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    named = [r for r in results if r["expected_dim"] is not None]
    mismatches = [r for r in named if max(r["scores"].items(), key=lambda x: x[1])[0] != r["expected_dim"]]

    print(f"Sections with expected dimension: {len(named)}")
    print(f"Mismatches: {len(mismatches)}")
    if mismatches:
        for m in mismatches:
            top = max(m["scores"].items(), key=lambda x: x[1])
            print(f"  - {m['section']}: expected {m['expected_dim']}, got {top[0]} (hotspot={m['hotspot_ratio']:.3f})")

    avg_hotspot = sum(r["hotspot_ratio"] for r in named) / len(named) if named else 0
    print(f"\nAvg hotspot ratio (named sections): {avg_hotspot:.3f}")
    print("  > Higher = more dimension-specific content")
    print("  > If low: section mentions keywords but doesn't embody the dimension")

    # Save JSON
    output_path = PROJECT_ROOT / "eval_results" / "section_alignment.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_data = {
        "prompt": str(PROMPT_FILE.name),
        "total_sections": len(sections),
        "named_sections": len(named),
        "mismatches": len(mismatches),
        "avg_hotspot": avg_hotspot,
        "sections": results,
    }
    import json
    output_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2))
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
