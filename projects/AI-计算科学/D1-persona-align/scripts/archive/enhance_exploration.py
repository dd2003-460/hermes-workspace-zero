#!/usr/bin/env python3
"""为 idea 文件补充高权重探索关键词。"""

import re
from pathlib import Path

EXPL_UPDATE = """

#### 探索-利用分配
对 {topic} 的分析需要在探索新路径和利用现有方法之间做权衡。探索频率不应盲目提高——只有当探索收益超过探索成本时，才值得投入新的分析路径。工具选择应服务于探索策略，而非反过来被工具限制问题定义。磨刀理论提醒我们：如果直接分析 {topic} 的结构已经足够清晰，就不应浪费时间探索新工具。
"""

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        has_high = any(re.search(kw, text) for kw in ['探索频率', '探索策略', '探索路径', '探索成本'])
        if has_high:
            continue
        text = EXPL_UPDATE.format(topic='该主题') + text
        Path(f).write_text(text, encoding='utf-8')
        enhanced += 1
        print(f'  [OK] {f.name}')
    print(f'\nUpdated {enhanced}/{len(files)} files.')

if __name__ == '__main__':
    main()
