#!/usr/bin/env python3
"""索引一致性检查器：检查 INDEX.md 与实际文件系统状态是否一致"""
import os
import sys
import re

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/Users/a1-6/Desktop/workspace/projects'

issues = []
all_index = []

# 1. 扫描所有 INDEX.md
for r, d, files in os.walk(ROOT):
    for f in files:
        if f == 'INDEX.md':
            all_index.append(os.path.relpath(os.path.join(r, f), ROOT))

print("=" * 60)
print(f"索引一致性检查报告")
print(f"根目录: {ROOT}")
print(f"INDEX.md 数: {len(all_index)}")
print("=" * 60)

declared_pat = re.compile(r'^\s*(?:├|└)\s+`([^`]+)`\s')  # code block structure
declared_pipe = re.compile(r'^\s*\|\s+`([^`]+?)`\s*\|')  # pipe table first col
skip_words = re.compile(r'(已废弃|已迁移|已归档|已清理|保留 INDEX|未实现|待实现|no|empty)')
common_files = re.compile(r'\.(md|json|py|txt|pdf|png|jpg|jpeg|gif|svg|csv|yaml|yml|toml|cfg|ini|log|sh|bash|zip|tar|gz|wav|mp3|mp4|avi)$', re.IGNORECASE)

real_missing = []
stale_refs = []

for idx_rel in sorted(all_index):
    path = os.path.join(ROOT, idx_rel)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    parent = os.path.dirname(path)

    for i, line in enumerate(lines):
        # Skip comment lines
        if line.strip().startswith('<!--') or line.strip().startswith('-->'):
            continue
        # Skip lines that are clearly file references (not directory declarations)
        if common_files.search(line):
            continue

        # Match code block structure lines like:  ├── `memory/` → ...
        for match in declared_pat.finditer(line):
            path_str = match.group(1).strip()
            if skip_words.search(line):
                continue  # Already noted as migrated/deleted
            name = path_str.rstrip('/')
            check = os.path.join(parent, name)
            if not os.path.isdir(check):
                real_missing.append((idx_rel, i+1, path_str))

        # Match pipe table first col: | `memory/` | desc |
        for match in declared_pipe.finditer(line):
            path_str = match.group(1).strip()
            if skip_words.search(line):
                continue
            # If this looks like a file reference, skip it
            if common_files.search(path_str):
                continue
            name = path_str.rstrip('/')
            check = os.path.join(parent, name)
            if not os.path.isdir(check):
                real_missing.append((idx_rel, i+1, path_str))

print()
if real_missing:
    print(f"发现 {len(real_missing)} 个不一致问题 (声明目录不存在):")
    for f_idx, ln, dec in sorted(real_missing):
        print(f"  {f_idx}:{ln} — `{dec}` 声明存在但目录/文件不在")
else:
    print("未发现不一致。所有 STRUCTURE/LINE 声明的目录均存在。")

print()
print(f"覆盖扫描: {len(all_index)} 个 INDEX.md")
print("=" * 60)
