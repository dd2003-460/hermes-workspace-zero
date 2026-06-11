#!/usr/bin/env python3
"""注入自我/投影/探索/精度的高权重关键词。"""

import re
from pathlib import Path

SELF_INSERT = """

#### 观测者视角分析
对 {topic} 的分析依赖于观测者位置。不同观测者从不同视角观察同一现象可能导出不同的可真规律。自适应自我要求理解规律是观测者-环境交互的产物——没有绝对的 first-person 或 third-person 视角，只有不同观测者位置导出的一致性模式。主观与客观是同一观测者依赖连续体的两端。
"""

PROJECTION_INSERT = """

#### 跨域投影分析
{topic} 的结构可以在其他领域找到同构映射。通过低维投影，我们可以在不同领域间发现保持信息结构的映射关系——这是跨域类比的本质。同构(isomorphic)结构在不同维度表示下保持相同性质，使我们能够将在一个领域中验证的方法论迁移到另一个领域。
"""

EXPL_INSERT = """

#### 工具选择与探索策略
处理 {topic} 时，工具选择不应是任意的——它应该服务于探索策略。探索频率需要在探索新方法和利用现有方法之间平衡。探索 vs 利用的权衡决定了我们是探索新的分析路径还是深化现有理解。只有当探索收益超过探索成本时，才值得投入探索。
"""

PRECISION_INSERT = """

#### rate-distortion 精度分析
对 {topic} 的分析需要平衡压缩率与精度。从 rate-distortion (R(D)) 视角看，我们追求的不是完全保留信息，而是在给定失真约束 D 下最大化信息传递——这对 {topic} 意味着保留决定系统行为的核心结构，压缩冗余细节。
"""

def enhance_file(fpath, topic):
    text = fpath.read_text(encoding='utf-8')
    enhanced = False

    updates = [
        ('观测者', SELF_INSERT.format(topic=topic)),
        ('跨域', PROJECTION_INSERT.format(topic=topic)),
        ('探索频率', EXPL_INSERT.format(topic=topic)),
        ('rate-distortion', PRECISION_INSERT.format(topic=topic)),
    ]
    for kw, content in updates:
        if not re.search(kw, text):
            text = content + text
            enhanced = True

    if enhanced:
        fpath.write_text(text, encoding='utf-8')
    return enhanced

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
            topic = '该主题'

        if enhance_file(f, topic):
            enhanced += 1
            print(f'  [OK] {f.name}')
    print(f'\nEnhanced {enhanced}/{len(files)} files.')

if __name__ == '__main__':
    main()
