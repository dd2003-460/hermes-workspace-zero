#!/usr/bin/env python3
"""Validate gap_filler against dashboard — quantify the count vs weighted matching mismatch."""

import json
import re
from pathlib import Path

# Keywords gap_filler uses for perception (from persona_v3_gap_filler.py)
GAP_FILLER_PERCEPTION_KEYWORDS = [
    "感知", "感知时间", "感知速率", "感知干扰", "感知资源",
    "信息密度", "perception", "sensory", "感知任务", "感知精度",
    "感知分配", "感知粒度"
]

# Keywords dashboard uses (from persona_v3_dashboard.py) with weights
DASHBOARD_PERCEPTION_KEYWORDS = [
    ("感知", 1.0), ("感知时间", 1.5), ("感知速率", 1.5),
    ("感知干扰", 1.0), ("感知资源", 1.0), ("信息密度", 1.0),
    ("perception", 1.0), ("sensory", 1.0), ("感知任务", 1.0),
    ("感知精度", 1.0), ("感知分配", 1.0), ("感知粒度", 0.5),
    ("t_p", 1.5), ("信噪比", 1.0), ("细感知", 1.0),
]

def gap_filler_score(text):
    """Simulate gap_filler count matching."""
    text_lower = text.lower()
    matched = sum(1 for kw in GAP_FILLER_PERCEPTION_KEYWORDS if kw in text_lower)
    total = len(GAP_FILLER_PERCEPTION_KEYWORDS)
    return matched / total

def dashboard_score(text):
    """Simulate dashboard weighted matching."""
    text_lower = text.lower()
    matched_weight = sum(w for kw, w in DASHBOARD_PERCEPTION_KEYWORDS if kw in text_lower)
    total_weight = sum(w for _, w in DASHBOARD_PERCEPTION_KEYWORDS)
    return matched_weight / total_weight

def main():
    ideas_dir = Path('memory')
    idea_files = sorted(ideas_dir.glob('idea-*.md'))

    results = []
    mismatches = 0

    for f in idea_files:
        text = f.read_text(encoding='utf-8')
        gf = gap_filler_score(text)
        db = dashboard_score(text)
        diff = abs(gf - db)

        is_mismatch = abs(gf - db) > 0.1

        results.append({
            'file': f.name,
            'gap_filler': round(gf, 4),
            'dashboard': round(db, 4),
            'diff': round(diff, 4),
            'mismatch': is_mismatch,
        })
        if is_mismatch:
            mismatches += 1

    # Summary
    total = len(results)
    print(f"gap_filler vs dashboard 感知维度匹配对比")
    print(f"文件数: {total}")
    print(f"不匹配数: {mismatches} ({mismatches/total:.0%})")
    print(f"\n最严重不匹配 (Top 10):")

    mismatches_sorted = sorted(results, key=lambda x: x['diff'], reverse=True)
    for r in mismatches_sorted[:10]:
        flag = "⚠️" if r['mismatch'] else ""
        print(f"  {flag} {r['file']}: gap_filler={r['gap_filler']:.2f} dashboard={r['dashboard']:.2f} diff={r['diff']:.2f}")

    # Save report
    report = {
        'total': total,
        'mismatches': mismatches,
        'mismatch_rate': round(mismatches / total, 4),
        'top_mismatches': mismatches_sorted[:10],
    }
    Path('validation-gap-vs-dashboard.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n报告: validation-gap-vs-dashboard.json")

if __name__ == '__main__':
    main()
