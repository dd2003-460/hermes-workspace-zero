#!/usr/bin/env python3
"""Verify persona-v3 prompt against alignment keywords."""

import re
import json
from pathlib import Path

# Keywords from dashboard weighted matching that matter
HIGH_WEIGHT = {
    'observer-dependent': 2.0,
    'isomorphic': 1.5,
    'rate-distortion': 1.5,
    'R(D)': 1.5,
    '低维': 2.0,
    '跨域': 2.0,
    '同构': 1.5,
    'rate_distortion': 1.0,
    't_p': 1.5,
    '感知速率': 1.5,
    '感知粒度': 0.5,
    '观测者-环境': 2.0,
    'y(θ)': 1.5,
}

LOW_WEIGHT = [
    '感知时间', '感知干扰', '感知资源', '信息密度', '信噪比',
    '贝叶斯', '先验分布', '探索利用', '跨域类比',
]

def main():
    prompt_path = Path('persona-v3-prompt.txt')
    text = prompt_path.read_text(encoding='utf-8').lower()
    text_upper = prompt_path.read_text(encoding='utf-8')

    matched_high = []
    total_weight = sum(HIGH_WEIGHT.values())
    matched_weight = 0

    for kw, w in HIGH_WEIGHT.items():
        if kw.lower() in text:
            matched_high.append(f'{kw}({w})')
            matched_weight += w

    # Count low-weight matches
    low_matches = sum(1 for kw in LOW_WEIGHT if kw.lower() in text)

    high_score = matched_weight / total_weight if total_weight > 0 else 0
    low_score = low_matches / len(LOW_WEIGHT) if LOW_WEIGHT else 0

    print(f"persona-v3 Prompt Verification")
    print(f"================================")
    print(f"Prompt length: {len(text)} chars")
    print(f"")
    print(f"High-weight keywords (dashboard-critical):")
    print(f"  Matched: {len(matched_high)}/{len(HIGH_WEIGHT)}")
    print(f"  Weight: {matched_weight:.1f}/{total_weight:.1f} → score={high_score:.2f}")
    print(f"  匹配: {', '.join(matched_high)}")
    print(f"")
    print(f"Low-weight keywords: {low_matches}/{len(LOW_WEIGHT)} 匹配")
    print(f"")
    print(f"Overall high-weight score: {high_score:.2f}")
    print(f"PASS: {'YES' if high_score >= 0.6 else 'NO'} (threshold 0.6)")

    # Save JSON report
    report = {
        'prompt_length': len(text),
        'high_weight_total': total_weight,
        'high_weight_matched': matched_weight,
        'high_weight_score': round(high_score, 4),
        'matched_keywords': matched_high,
        'low_weight_matches': low_matches,
        'low_weight_total': len(LOW_WEIGHT),
        'pass': high_score >= 0.6,
    }

    out = Path('verification-report-prompt.json')
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReport saved to {out}")

if __name__ == '__main__':
    main()
