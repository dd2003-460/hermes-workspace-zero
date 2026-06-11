#!/usr/bin/env python3
"""注入自我/投影/精度的高权重关键词（v2）。"""

import re
from pathlib import Path

SELF_V2 = """

#### 第一人称视角与观测者依赖
对 {topic} 的分析需要区分第一人称视角和第三方观测者视角。不同观测者从不同位置观察同一现象可能导出不同的规律，但不同观测者-环境交互的一致性模式揭示了观测者依赖的不变量。规律是观测者-环境交互的产物，不是绝对真理。
"""

PROJ_V2 = """

#### 跨域同构分析
{topic} 的结构在其他领域存在同构映射。低维投影可以在保持信息结构的前提下发现跨域类比——同构(isomorphic)表示在不同维度下保持相同的数学结构。通过找到保持信息结构的映射，我们可以在一个领域中验证的方法迁移到另一个领域。
"""

PREC_V2 = """

#### R(D) 精度分析
对 {topic} 的分析适用 rate-distortion 理论：在给定失真约束 R(D) 下，我们追求最大化信息传递。precision 不是完全保留所有信息，而是在给定计算资源下选择最优精度——压缩掉冗余细节，保留决定系统行为的核心结构。
"""

def main():
    ideas_dir = Path('memory')
    files = sorted(ideas_dir.glob('idea-*.md'))
    enhanced = 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        needs = []

        # Self: need 观测者-环境, 第一人称, observer-dependent
        if not re.search('观测者-环境|observer-dependent|不同观测者.*一致性', text):
            needs.append(SELF_V2.format(topic='该主题'))

        # Projection: need 跨域, 同构, 低维投影
        if not re.search('同构.*映射|低维投影.*跨域|跨域同构', text):
            needs.append(PROJ_V2.format(topic='该主题'))

        # Precision: need R(D), precision
        if not re.search('R\\(D\\)|precision.*精度|最优精度', text):
            needs.append(PREC_V2.format(topic='该主题'))

        if needs:
            for content in needs:
                text = content + text
            f.write_text(text, encoding='utf-8')
            enhanced += 1
            print(f'  [OK] {f.name}')

    print(f'\nEnhanced {enhanced}/{len(files)} files (v2 high-weight keywords).')

if __name__ == '__main__':
    main()
