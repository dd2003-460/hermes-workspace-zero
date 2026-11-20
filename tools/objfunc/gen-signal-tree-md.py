#!/usr/bin/env python3
"""从 signal-tree-tiered.json 生成可折叠 md 树 (派生物, 不手改 md)。
用法: python3 tools/objfunc/gen-signal-tree-md.py
"""
import json, os
root = os.path.dirname(os.path.abspath(__file__))
tree = json.load(open(os.path.join(root, 'signal-tree-tiered.json')))
icon = {'缺口':'⬜','部分':'◐','待固化':'◑','已落地':'✓'}
lines = ['# 信号树（D 反馈 → 领域/情况/方法）', '',
 '> 派生物：数据源 `signal-tree-tiered.json`，本文件由 gen-signal-tree-md.py 自动生成。',
 '> 标记：✓已落地 ◐部分 ◑待固化 ⬜缺口 · tier: G全局 D领域 P项目',
 '> 用法：VSCode 大纲视图折叠导航，或 <details> 折叠。只展开你关心的线路。', '']
for d, ss in tree.items():
    n_sig = sum(len(v.get('signals',[])) for v in ss.values())
    n_gap = sum(1 for v in ss.values() if v.get('status')=='缺口')
    lines += [f'## {d}  `{n_sig}信号 · {n_gap}缺口`', '',
              '<details>', f'<summary>{d}（点开看情况）</summary>', '']
    for s, v in ss.items():
        st = v.get('status','?'); ti = v.get('tier','?')
        ticon = {'global':'G','domain':'D','project':'P'}.get(ti,'?')
        lines.append(f'### {icon.get(st,"?")} {s}  `{ticon}·{st}·{len(v.get("signals",[]))}信号`')
        if v.get('method'): lines.append(f'方法：{v["method"]}')
        if v.get('gap'): lines.append(f'缺口：{v["gap"]}')
        if v.get('dest'): lines.append(f'落点：`{v["dest"]}`')
        lines.append('')
    lines += ['</details>', '']
open(os.path.join(root, 'signal-tree.md'),'w').write('\n'.join(lines))
print('OK signal-tree.md', len(lines), 'lines')
