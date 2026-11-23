#!/usr/bin/env python3
"""T-PUB-1 workshop figures — 数据直接读 data/*.json, 可复现.
Usage: /opt/homebrew/bin/python3 make_figures.py
Output: figures/fig1-format-reliability.png, figures/fig2-mechanism.png
"""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
OUT = os.path.join(BASE, 'figures')
os.makedirs(OUT, exist_ok=True)

d = json.load(open(os.path.join(DATA, 'prompt_variant_formal.json')))
res = d['results']
variants = ['V1_strict', 'V2_loose', 'V3_engineer']
labels = ['V1\nstrict', 'V2\nloose', 'V3\nengineer']

# ---- Fig 1: format reliability + flip rate (two panels) ----
fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))

# Panel A: format failure rate (LLM judge) vs mechanical (0)
fail = []
for v in variants:
    outs = res[v]
    n_fail = sum(1 for o in outs.values() if not o['parseable'])
    fail.append(n_fail / len(outs) * 100)
x = np.arange(3)
bars = axes[0].bar(x - 0.15, fail, 0.3, color='#d62728', alpha=0.85, label='LLM judge (27b)')
bars2 = axes[0].bar(x + 0.15, [0, 0, 0], 0.3, color='#2ca02c', alpha=0.85, label='Mechanical judge')
for i, (v, f) in enumerate(zip(variants, fail)):
    n = sum(1 for o in res[v].values() if not o['parseable'])
    axes[0].text(i - 0.15, f + 1.5, f'{f:.0f}%\n({n}/67)', ha='center', fontsize=9)
axes[0].text(1.85, 5, '0/67', ha='center', fontsize=9, color='#2ca02c')
axes[0].set_xticks(x); axes[0].set_xticklabels(labels, fontsize=10)
axes[0].set_ylim(0, 100); axes[0].set_ylabel('Format failure rate (%)')
axes[0].set_title('(a) Format reliability', fontsize=11)
axes[0].legend(fontsize=8, loc='upper right')
axes[0].grid(axis='y', alpha=0.3)

# Panel B: flip rate (parseable outputs, both verdicted)
flips = []
for v in variants:
    agree = disagree = 0
    for o in res[v].values():
        if not o['parseable']:
            continue
        for c in o['llm']:
            lv, mv = o['llm'][c], o['mech'][c]
            if lv is None or mv is None:
                continue
            if lv == mv: agree += 1
            else: disagree += 1
    flips.append(disagree / (agree + disagree) * 100)
bars3 = axes[1].bar(x, flips, 0.5, color='#1f77b4', alpha=0.85)
for i, f in enumerate(flips):
    axes[1].text(i, f + 1.5, f'{f:.1f}%', ha='center', fontsize=9)
axes[1].axhline(50, color='k', ls='--', lw=1, alpha=0.6)
axes[1].text(2.4, 51, 'coin flip (50%)', fontsize=8, ha='right')
axes[1].set_xticks(x); axes[1].set_xticklabels(labels, fontsize=10)
axes[1].set_ylim(0, 75); axes[1].set_ylabel('Verdict disagreement rate (%)')
axes[1].set_title('(b) Flip rate (parseable subset)', fontsize=11)
axes[1].grid(axis='y', alpha=0.3)

fig.tight_layout()
fig.savefig(os.path.join(OUT, 'fig1-format-reliability.png'), dpi=200)
plt.close(fig)
print(f'fig1: fail={["%.1f" % f for f in fail]}%  flips={["%.1f" % f for f in flips]}%')

# ---- Fig 2: mechanism probe (mt500 vs mt2000) ----
mp = json.load(open(os.path.join(DATA, 'mt_probe2.json')))
by_oid = {}
for rec in mp:
    by_oid.setdefault(rec['oid'], {})[rec['mt']] = rec

fig, ax = plt.subplots(figsize=(7, 3.4))
oids = sorted(by_oid.keys())
y = np.arange(len(oids))
for mt, color, label in [(500, '#d62728', 'mt=500'), (2000, '#2ca02c', 'mt=2000')]:
    lengths = []
    for oid in oids:
        rec = by_oid[oid].get(mt)
        lengths.append(rec['raw_len'] if rec else 0)
    ax.barh(y + (0.18 if mt == 500 else -0.18), lengths, 0.36, color=color, alpha=0.85, label=label)
    for i, oid in enumerate(oids):
        rec = by_oid[oid].get(mt)
        if rec:
            mark = '✓' if rec['parseable'] else '✗'
            ax.text(rec['raw_len'] + 30, i + (0.18 if mt == 500 else -0.18),
                    f"{mark} {rec['finish_reason']}", va='center', fontsize=8)
ax.set_yticks(y); ax.set_yticklabels([o.replace('T-PUB-1-', '') for o in oids], fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Raw output length (chars)')
ax.legend(fontsize=8, loc='lower right')
ax.set_title('Mechanism probe: token budget vs output length and parseability', fontsize=11)
ax.grid(axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'fig2-mechanism.png'), dpi=200)
plt.close(fig)
recov = [o for o in oids if by_oid[o].get(500, {}).get('parseable') is False and by_oid[o].get(2000, {}).get('parseable') is True]
print(f'fig2: {len(oids)} oids, recovered mt500→mt2000: {recov}')
