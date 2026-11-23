"""T-PUB-1 Figure 1-2 生成（论文级, matplotlib, PDF+PNG）
Figure 1: 格式失败率 3 变体 + Wilson CI vs 机械 judge 0%
Figure 2: 机制面板 — mt500/mt2000 行为类矩阵 (6 case × 2 mt, 确定性探针 5rep 标注)
数据源: /tmp/prompt_variant_formal.json, /tmp/judge_determinism.json, /tmp/mt_probe2.json
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 9, 'axes.linewidth': 0.6, 'pdf.fonttype': 42, 'ps.fonttype': 42})
OUT = 'figures'
import os; os.makedirs(OUT, exist_ok=True)

# ---------- Figure 1 ----------
d = json.load(open('/tmp/prompt_variant_formal.json'))
def wilson(k, n, z=1.96):
    p = k/n; den = 1+z*z/n
    c = (p+z*z/(2*n))/den; h = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0, c-h), min(1, c+h)

variants = ['V1_strict', 'V2_loose', 'V3_engineer']
labels = ['V1 strict', 'V2 loose', 'V3 engineer', 'Mechanical judge']
rates, los, his, ns = [], [], [], []
for v in variants:
    vres = d['results'][v]
    n = len(vres); k = sum(1 for r in vres.values() if not r['parseable'])
    lo, hi = wilson(k, n)
    rates.append(k/n); los.append(k/n-lo); his.append(hi-k/n); ns.append(f'{k}/{n}')
rates.append(0.0); los.append(0.0); his.append(0.0); ns.append('0/67')

fig, ax = plt.subplots(figsize=(4.6, 2.7))
colors = ['#d62728', '#d62728', '#d62728', '#2ca02c']
y = np.arange(len(labels))[::-1]
plot_rates = [max(r, 0.012) for r in rates]  # 0% 给最小可见宽度
ax.barh(y, plot_rates, xerr=[los, his], color=colors, alpha=0.85, ecolor='k', capsize=3, height=0.55)
for yi, r, n, c in zip(y, rates, ns, colors):
    if r > 0.05:
        ax.text(r - 0.02, yi, f'{r*100:.1f}%  ({n})', va='center', ha='right', fontsize=8.5, color='white', fontweight='bold')
    else:
        ax.text(0.02, yi, f'{r*100:.1f}%  ({n})', va='center', ha='left', fontsize=8.5, color=c, fontweight='bold')
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlim(0, 1.0); ax.set_xlabel('Format failure rate (unparseable output)')
ax.set_title('Format reliability: LLM vs mechanical judge', fontsize=10)
fig.tight_layout()
fig.savefig(f'{OUT}/fig1-format-reliability.pdf'); fig.savefig(f'{OUT}/fig1-format-reliability.png', dpi=200)
plt.close(fig)
print('fig1 done')

# ---------- Figure 2 ----------
# 行为类: 来自确定性探针 (5rep) + mt_probe2
det = json.load(open('/tmp/judge_determinism.json'))
# case 定义: (label, mt500 状态, mt2000 状态, 行为类, 注释)
cases = [
    ('Q01', 'fail', 'pass 5/5', 'TR', 'truncation-recoverable'),
    ('Q02', 'fail', 'pass',       'TR', 'truncation-recoverable'),
    ('Q06', 'fail', 'pass',       'TR', 'truncation-recoverable'),
    ('Q04', 'fail', 'flip 3/5',   'BF', 'borderline (temp-0 flip)'),
    ('Q03', 'fail', 'fail 0/5',   'CF', 'convergence failure'),
    ('Q05', 'fail', 'fail',       'CF', 'convergence failure'),
]
cls_color = {'TR': '#2ca02c', 'BF': '#ff7f0e', 'CF': '#d62728'}
fig, ax = plt.subplots(figsize=(5.4, 3.0))
# 网格: 行=case, 列=mt
for i, (lab, s500, s2000, cls, note) in enumerate(cases):
    y0 = len(cases) - 1 - i
    # mt500 cell
    ax.add_patch(plt.Rectangle((0, y0), 1, 0.9, facecolor='#d62728', alpha=0.75))
    ax.text(0.5, y0+0.45, 'fail', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    # mt2000 cell
    if cls == 'TR':
        ax.add_patch(plt.Rectangle((1, y0), 1, 0.9, facecolor='#2ca02c', alpha=0.75))
        ax.text(1.5, y0+0.45, s2000, ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
    elif cls == 'BF':
        ax.add_patch(plt.Rectangle((1, y0), 1, 0.9, facecolor='#ff7f0e', alpha=0.75))
        ax.text(1.5, y0+0.45, s2000, ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
    else:
        ax.add_patch(plt.Rectangle((1, y0), 1, 0.9, facecolor='#d62728', alpha=0.75))
        ax.text(1.5, y0+0.45, s2000, ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
    ax.text(-0.08, y0+0.45, lab, ha='right', va='center', fontsize=9)
    ax.text(2.15, y0+0.45, note, ha='left', va='center', fontsize=7.5, color='0.25')
ax.set_xlim(-0.6, 6.2); ax.set_ylim(-0.1, len(cases))
ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(['mt = 500', 'mt = 2000'], fontsize=9)
ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
ax.set_title('Mechanism: behavior classes under max_tokens (V1 strict)', fontsize=10)
# legend
import matplotlib.patches as mpatches
leg = [mpatches.Patch(color='#2ca02c', label='recoverable'),
       mpatches.Patch(color='#ff7f0e', label='borderline flip'),
       mpatches.Patch(color='#d62728', label='fail / convergence')]
ax.legend(handles=leg, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=7.5, frameon=False)
fig.subplots_adjust(bottom=0.24, top=0.90)
fig.savefig(f'{OUT}/fig2-mechanism-behavior-classes.pdf'); fig.savefig(f'{OUT}/fig2-mechanism-behavior-classes.png', dpi=200)
plt.close(fig)
print('fig2 done')
