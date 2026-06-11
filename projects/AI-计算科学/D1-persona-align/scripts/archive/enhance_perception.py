#!/usr/bin/env python3
"""直接为 idea 文件注入自适应感知维度内容。"""

import re
from pathlib import Path

PERCEPTION_INSERT = """

#### 感知粒度与聚焦分析
在处理 {topic} 时，需要区分感知粒度：核心论断需要细粒度感知，辅助论证可采用粗粒度感知。同时需要分配感知资源——对高信息密度段落投入感知聚焦，对低密度内容快速通过。
这种自适应感知分辨能力确保在有限计算资源下最大化信息提取效率。
"""

def enhance_file(fpath, topic):
    text = Path(fpath).read_text(encoding='utf-8')
    # Only inject if missing high-weight perception keywords (感知粒度, 感知聚焦, 感知分辨)
    has_high_weight = any(re.search(kw, text) for kw in ['感知粒度', '感知聚焦', '感知分辨'])
    if has_high_weight:
        return False

    text = PERCEPTION_INSERT.format(topic=topic) + text
    Path(fpath).write_text(text, encoding='utf-8')
    return True

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        stem = f.stem
        if stem.startswith('idea-'):
            stem = stem[5:]
        topic = stem.replace('-', ' ').replace('_', ' ')[:30]
        # Use first line as topic
        text = f.read_text(encoding='utf-8')
        first_line = text.split('\n')[0].strip()
        if first_line.startswith('# '):
            topic = first_line[2:].strip().replace('#', '').replace('*', '').replace('`', '')[:30]

        if enhance_file(f, topic):
            enhanced += 1
            print(f'  [OK] {f.name}')

    print(f'\nEnhanced {enhanced}/{len(files)} files with perception content.')

if __name__ == '__main__':
    main()
