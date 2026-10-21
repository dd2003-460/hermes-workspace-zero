#!/usr/bin/env python3
"""项目结构审计（project-tidy skill 配套，只读）。

用法: python3 scripts/tidy_audit.py [projects/<path> ...]
输出: 缺标准结构 / 次级子模块数超 3-7 / 顶层杂物 三类清单。
"""
import sys, os, time

SKIP = {'.git', 'node_modules', '.npmcache', '__pycache__', '.DS_Store'}
STD = ['INDEX.md', 'memory', 'tasks']

def count_children(d):
    return [e for e in os.listdir(d)
            if os.path.isdir(os.path.join(d, e)) and e not in SKIP and not e.startswith('.')]

def audit(root, out):
    entries = count_children(root)
    if root != 'projects' and os.path.basename(root.rstrip('/')) != 'projects':
        for want in STD:
            if not os.path.exists(os.path.join(root, want)):
                out['missing'].append(f"{root}: 缺 {want}")
    if not (3 <= len(entries) <= 7):
        out['range'].append(f"{root}: {len(entries)} 个子模块 (3-7 为宜) -> {entries}")
    for sub in entries:
        p = os.path.join(root, sub)
        if os.path.isdir(os.path.join(p, 'memory')):
            audit(p, out)

def main():
    roots = sys.argv[1:] or ['projects']
    out = {'missing': [], 'range': [], 'top': []}
    for r in roots:
        if os.path.isdir(r):
            audit(r, out)
    print(f"# tidy audit {time.strftime('%Y-%m-%d')}\n")
    for k, title in [('missing', '缺标准结构'), ('range', '子模块数超 3-7')]:
        print(f"## {title} ({len(out[k])})")
        for line in out[k]:
            print(f"- {line}")
        print()

if __name__ == '__main__':
    main()
