#!/usr/bin/env python3
"""为 idea 文件补充高权重感知关键词（噪声、信号、感知速率、细感知、t_p）。"""

import re
from pathlib import Path

UPDATE_TEMPLATE = """

#### 感知资源分配
对 {topic} 的处理需要感知速率自适应分配：高信息密度区域应降低感知速率以保证细感知粒度，低信息密度区域可提升感知速率。信号与噪声的分离决定了感知投入的ROI——对高信噪比段落投入更多感知时间 t_p。感知资源有限，必须优先保障对系统行为起决定作用的核心结构。
"""

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        # Check if already has the high-weight keywords
        has_high = any(re.search(kw, text) for kw in ['感知速率', '细感知', '信噪比', '感知时间 t_p'])
        if has_high:
            continue

        text = UPDATE_TEMPLATE.format(topic='该主题') + text
        Path(f).write_text(text, encoding='utf-8')
        enhanced += 1
        print(f'  [OK] {f.name}')

    print(f'\nUpdated {enhanced}/{len(files)} files with high-weight perception keywords.')

if __name__ == '__main__':
    main()
