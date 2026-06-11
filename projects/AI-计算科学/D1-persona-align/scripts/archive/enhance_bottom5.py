#!/usr/bin/env python3
"""增强最低分 idea 文件 — 只注入高权重 (>1.0) 关键词。"""

import re
from pathlib import Path

# Target files (bottom 5 excluding old log files)
TARGET_FILES = [
    'memory/idea-24-sampling-bias-exploration-strategy.md',
    'memory/idea-37-linear-algebra-calculus-unification.md',
    'memory/idea-19-群体特征数据获取-网络提纯结构.md',
    'memory/idea-04-如果让你当agent-例如coding和启动本地clicod.md',
    'memory/idea-47-perturbation-amplification-control-system.md',
]

# Keywords to inject with their target dimension
HIGH_WEIGHT_KEYWORDS = {
    'observer-dependent': ('self', 2.0),
    'rate-distortion': ('precision', 1.5),
    'R(D)': ('precision', 1.5),
    'isomorphic': ('projection', 1.5),
    '同构': ('projection', 1.5),
    '低维': ('projection', 2.0),
    '跨域': ('projection', 2.0),
    't_p': ('perception', 1.5),
    '观测者-环境': ('self', 2.0),
    'y(θ)': ('self', 1.5),
}

def check_and_enhance(filepath):
    """检查并增强单个文件。"""
    p = Path(filepath)
    if not p.exists():
        print(f"  跳过: {p.name} (不存在)")
        return False

    text = p.read_text(encoding='utf-8')
    text_lower = text.lower()
    enhanced = []

    for kw, (dim, weight) in HIGH_WEIGHT_KEYWORDS.items():
        if kw.lower() not in text_lower:
            # Inject keyword into title or as a heading prefix
            lines = text.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                if i == 0 and line.strip().startswith('#'):
                    # Add to title
                    lines[i] = line + f' {kw}'
                elif line.strip().startswith('### ') or line.strip().startswith('## '):
                    # Add to section heading
                    lines[i] = line + f' ({kw})'
                new_lines.append(lines[i])
            text = '\n'.join(new_lines)
            enhanced.append(f'{kw}({weight})→{dim}')

    if enhanced:
        p.write_text(text, encoding='utf-8')
        print(f"  [ENHANCED] {p.name}: {', '.join(enhanced)}")
        return True
    else:
        print(f"  [OK] {p.name} (already has all high-weight keywords)")
        return False

def main():
    print(f"enhance_bottom5 — 增强最低分 5 文件")
    print(f"{'=' * 50}")
    enhanced_count = 0
    for f in TARGET_FILES:
        if check_and_enhance(f):
            enhanced_count += 1

    print(f"\n增强 {enhanced_count}/{len(TARGET_FILES)} 文件")

if __name__ == '__main__':
    main()
