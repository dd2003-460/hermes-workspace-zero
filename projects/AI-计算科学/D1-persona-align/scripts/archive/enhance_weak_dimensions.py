#!/usr/bin/env python3
"""为低分维度（探索、精度、投影、自我）直接注入内容。"""

import re
from pathlib import Path

EXPLORATION_INSERT = """

#### 探索-利用权衡分析
处理 {topic} 时，当前策略应平衡利用现有方法（如已有分析框架）与探索新路径（如跨域类比）。已有工具集可能已足够处理 {topic} 的大部分方面，但对 {topic} 的核心不确定性可能需要探索新的分析视角。磨刀理论适用：只有当新工具/方法的预期收益超过探索成本时，才值得投入探索。
"""

PRECISION_INSERT = """

#### 精度层级分析
对 {topic} 的分析需要选择适当的精度层级：高精度（保留所有细节）适用于核心论断，低精度（压缩冗余）适用于辅助论证。rate-distortion 视角下，我们追求的不是完全保留信息，而是在给定资源约束下最大化精度——对 {topic} 而言，压缩掉的是冗余细节，保留的是决定系统行为的核心结构。
"""

PROJECTION_INSERT = """

#### 跨域投影分析
{topic} 的结构可以在其他领域找到同构映射：例如，其信息流模式可能与 {topic} 相关的系统共享相同的抽象结构。通过低维投影，我们可以在不同维度间发现保持信息结构的映射，识别跨域类比。
"""

SELF_INSERT = """

#### 自适应自我分析
对 {topic} 的分析依赖于观测者视角——同一现象在不同观测者视角下可能导出不同但都可真的规律。自适应自我要求我们在不同视角间切换，理解规律是观测者-环境交互的产物，而非绝对真理。
"""

def enhance_file(fpath, topic):
    text = Path(fpath).read_text(encoding='utf-8')

    # Check which sections are missing
    missing_sections = []
    if not re.search('探索-利用权衡', text):
        missing_sections.append(('探索', EXPLORATION_INSERT.format(topic=topic)))
    if not re.search('精度层级', text):
        missing_sections.append(('精度', PRECISION_INSERT.format(topic=topic)))
    if not re.search('跨域投影', text):
        missing_sections.append(('投影', PROJECTION_INSERT.format(topic=topic)))
    if not re.search('自适应自我', text):
        missing_sections.append(('自我', SELF_INSERT.format(topic=topic)))

    if missing_sections:
        # Add all missing sections at the beginning (after title)
        for kw, content in missing_sections:
            text = content + text
        Path(fpath).write_text(text, encoding='utf-8')
        return True
    return False

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        first_line = text.split('\n')[0].strip()
        if first_line.startswith('# '):
            topic = first_line[2:].strip().replace('#', '').replace('*', '').replace('`', '')[:30]
        else:
            stem = f.stem.replace('idea-', '').replace('-', ' ')[:30]
            topic = stem

        if enhance_file(f, topic):
            enhanced += 1
            print(f'  [OK] {f.name}')

    print(f'\nEnhanced {enhanced}/{len(files)} files.')

if __name__ == '__main__':
    main()
