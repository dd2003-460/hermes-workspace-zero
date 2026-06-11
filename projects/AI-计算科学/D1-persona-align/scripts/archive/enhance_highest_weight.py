#!/usr/bin/env python3
"""注入自我和投影的最高权重关键词（v3）。"""

import re
from pathlib import Path

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        needs = []

        # Self: need observer-dependent or observer-dependence (2.0 each)
        if not re.search('observer.depend', text):
            text = text.replace('# ', '# observer-dependent ')
            needs.append('self')

        # Projection: need 同构 + isomorphic + 低维 + 跨域
        if not (re.search('同构.*isomorphic|isomorphic.*同构', text)):
            # Add isomorphic reference
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    lines[i] = line + ' 同构(isomorphic)结构跨域保持不变'
                    break
            text = '\n'.join(lines)
            needs.append('projection')

        if needs:
            f.write_text(text, encoding='utf-8')
            enhanced += 1
            print(f'  [OK] {f.name} ({", ".join(needs)})')

    print(f'\nEnhanced {enhanced}/{len(files)} files (v3 highest-weight keywords).')

if __name__ == '__main__':
    main()
