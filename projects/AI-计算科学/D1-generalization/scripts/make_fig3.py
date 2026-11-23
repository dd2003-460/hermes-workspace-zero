"""fig3: 瞎猜概率界（F4）— 10 题 P(全瞎猜全对) 对数柱状图。
数据源: scripts/guess_bound.py 的解析界（同瞎猜模型定义），结果落盘 data/guess_bound_results.json。
"""
import sys, math, json
sys.path.insert(0, 'scripts')
import formula_judge as fj

SPECS = json.load(open('/tmp/tpub1_extracted.json'))['specs']

def hit_prob(cp):
    kind, tol = cp.get('kind'), cp.get('tolerance', 0.02)
    gv = fj.eval_gold(cp['gold'])
    if kind == 'calc' and tol == 0 and gv is not None: return 1/101
    if kind in ('calc','fact') and gv is not None: return 2*tol/1.5 if tol > 0 else 1/101
    if kind == 'bool': return 0.5
    return 0.01

data = {}
for qid, spec in sorted(SPECS.items()):
    p = math.exp(sum(math.log(hit_prob(cp)) for cp in spec['checkpoints']))
    data[qid] = (spec['type'], p)

out = {qid: {'type': t, 'P_all_correct_by_guess': p} for qid,(t,p) in data.items()}
json.dump(out, open('tasks/T-PUB-1/data/guess_bound_results.json','w'), indent=1)
print(json.dumps(out, indent=1))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

qs = sorted(data)
labels = [q.split('-')[-1] for q in qs]
vals = [data[q][1] for q in qs]
colors = ['#4477AA' if data[q][0]=='full' else '#EE6677' for q in qs]

fig, ax = plt.subplots(figsize=(5.5, 3.6), dpi=200)
bars = ax.bar(labels, vals, color=colors, edgecolor='black', linewidth=0.5)
ax.set_yscale('log')
ax.set_ylim(1e-11, 1e-3)
ax.axhline(1e-4, color='k', ls='--', lw=1)
ax.text(9.4, 2e-4, 'threshold 1e-4', ha='right', fontsize=8)
ax.set_ylabel('P(all correct by guess)')
ax.set_xlabel('Task (Q01-Q07 full-rank, Q08-Q10 rank-deficient)')
ax.legend(handles=[Patch(color='#4477AA', label='full-rank'), Patch(color='#EE6677', label='rank-deficient')], fontsize=8, frameon=False)
ax.tick_params(axis='x', labelsize=8)
ax.tick_params(axis='y', labelsize=8)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v*1.4, f'{v:.1e}', ha='center', fontsize=6.5, rotation=90, va='bottom')
plt.tight_layout()
plt.savefig('tasks/T-PUB-1/figures/fig3-guess-bound.png', dpi=200)
print('fig3 saved')
