#!/usr/bin/env python3
"""
Quality check script for persona-v3 analysis drafts.

Scans all idea-*.md files and reports:
- TODO placeholders
- Generic evidence lists (non-specific)
- Placeholder math expressions
- Line count
- Tier classification (based on quality heuristics)
"""

import os
import re
import sys
from collections import defaultdict

MEM_DIR = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/memory"

def analyze_file(filepath):
    """Analyze a single analysis file for quality issues."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    filename = os.path.basename(filepath)
    
    # Count issues
    issues = {
        'TODO': [],
        'placeholder_math': [],
        'generic_evidence': [],
        'generic_cross_ref': [],
    }
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # TODO check
        if 'TODO' in stripped:
            issues['TODO'].append((i, stripped[:80]))
        
        # Placeholder math
        if '需要根据具体' in stripped or '关键信息关系式' in stripped:
            issues['placeholder_math'].append((i, stripped[:80]))
        
        # Generic evidence
        if '跨域类比支持' in stripped or '信息论约束' in stripped or '实证/数学证据' in stripped:
            issues['generic_evidence'].append((i, stripped[:80]))
        
        # Generic cross-domain
        if 'TODO: 需要针对每个idea具体分析跨域类比' in stripped:
            issues['generic_cross_ref'].append((i, stripped[:80]))
    
    return {
        'filename': filename,
        'path': filepath,
        'lines': len(lines),
        'chars': len(content),
        'issues': issues,
        'issue_count': sum(len(v) for v in issues.values()),
        'has_tier1_mapping': '与 persona-v3 的统一映射' in content,
        'has_complete_bayes': 'P(H₀|E)' in content and '≈' in content,
    }

def main():
    results = []
    issues_by_type = defaultdict(list)
    
    for fname in os.listdir(MEM_DIR):
        if not fname.startswith('idea-') or not fname.endswith('.md'):
            continue
        
        fpath = os.path.join(MEM_DIR, fname)
        result = analyze_file(fpath)
        results.append(result)
        
        for issue_type, issue_list in result['issues'].items():
            if issue_list:
                issues_by_type[issue_type].append((fname, len(issue_list)))
    
    # Sort by issue count (descending)
    results.sort(key=lambda r: r['issue_count'], reverse=True)
    
    # Print summary
    print("=" * 80)
    print("PERSONA-V3 ANALYSIS QUALITY REPORT")
    print("=" * 80)
    print()
    
    # Issue summary
    print("ISSUES BY TYPE:")
    print("-" * 40)
    for issue_type, issue_list in sorted(issues_by_type.items()):
        print(f"  {issue_type}: {len(issue_list)} files affected")
    print()
    
    # Print top 10 worst files
    print("TOP 10 WORST FILES (by issue count):")
    print("-" * 40)
    for r in results[:10]:
        badge = "TIER1" if r['issue_count'] == 0 else "TIER2"
        print(f"  [{badge}] {r['filename'][:60]}")
        print(f"         {r['lines']} lines, {r['chars']} chars, {r['issue_count']} issues")
        for issue_type, issue_list in r['issues'].items():
            if issue_list:
                print(f"         {issue_type}: {len(issue_list)} instances")
    print()
    
    # Tier classification
    tier1 = [r for r in results if r['issue_count'] == 0 and r['lines'] >= 150]
    tier2 = [r for r in results if r['issue_count'] > 0 or r['lines'] < 150]
    
    print(f"Tier 1 (complete): {len(tier1)} files")
    print(f"Tier 2 (needs refinement): {len(tier2)} files")
    print(f"Total analysis files: {len(results)}")
    print(f"Total lines: {sum(r['lines'] for r in results)}")
    print()
    
    # Recommend next refinement targets
    if tier2:
        print("RECOMMENDED REFINEMENT TARGETS (sorted by priority):")
        print("-" * 40)
        # Priority: fewer issues + shorter lines = easier to fix + higher impact
        priority_list = sorted(tier2, key=lambda r: (r['issue_count'], -r['lines']))
        for i, r in enumerate(priority_list[:10], 1):
            print(f"  #{i}: {r['filename'][:60]} ({r['lines']}L, {r['issue_count']} issues)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
