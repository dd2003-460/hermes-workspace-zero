#!/usr/bin/env python3
"""Generate 4 figures for S18-1 paper."""

import numpy as np
import os

# Load experimental results
results_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../researches/S18-1-experimental-results.json"
)
import json
results = json.load(open(results_path))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Find a usable font
font_found = False
for fp in fm.fontManager.ttflist:
    if any(k in fp.name.lower() for k in ['dejavu', 'sans', 'mono']):
        plt.rcParams['font.family'] = fp.name
        font_found = True
        break
if not font_found:
    plt.rcParams['font.family'] = 'DejaVu Sans'

# ============================================================================
# Fig 1: Phase Transition
# ============================================================================

betas = results["experiment_1_phase_transition"]["betas"]
mean_k = results["experiment_1_phase_transition"]["mean_complexity"]
std_k = results["experiment_1_phase_transition"]["std_complexity"]

fig, ax = plt.subplots(1, 1, figsize=(8, 5))
ax.fill_between(betas, [m-s for m,s in zip(mean_k, std_k)],
                [m+s for m,s in zip(mean_k, std_k)], alpha=0.2, color='steelblue')
ax.plot(betas, mean_k, 'b-', linewidth=2, label=r'$\langle K \rangle$')
ax.axvline(x=results["beta_c_detection"]["beta_c"], color='red', linestyle='--',
           alpha=0.5, label=r'$\beta_c \approx %.3f$' % results["beta_c_detection"]["beta_c"])
ax.set_xlabel(r'$\beta$ (complexity penalty)', fontsize=14)
ax.set_ylabel(r'Mean Selected Complexity $\langle K \rangle$', fontsize=14)
ax.set_title(r'Phase Transition in Tool Complexity', fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.set_xlim(0, 2.0)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Fig01-phase-transition.png"), dpi=150)
plt.close(fig)

# ============================================================================
# Fig 2: Complexity Matching
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(12, 8))
axes = axes.flatten()

beta_vals = [0.05, 0.2, 0.5, 1.0, 2.0]
colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']

for i, beta in enumerate(beta_vals):
    key = f"beta_{beta}"
    data = results["experiment_2_complexity_matching"][key]
    task_c = np.array(data["task_complexity"])
    sel_c = np.array(data["selected_complexity"])
    gap = np.array(data["gap"])

    # Group by task complexity and average
    unique_tasks = sorted(set(task_c))
    avg_sel = [np.mean(sel_c[task_c == tc]) for tc in unique_tasks]

    ax = axes[i]
    ax.plot(unique_tasks, avg_sel, 'o-', color=colors[i], linewidth=2, markersize=6, label=r'$\beta = %.2f$' % beta)
    ax.plot([0.5, 12.5], [0.5, 12.5], 'k--', alpha=0.3, label='ideal match')
    ax.set_xlabel('Task Complexity $C_{\\mathrm{task}}$', fontsize=10)
    ax.set_ylabel('Selected Complexity', fontsize=10)
    ax.set_title(r'$\beta = %.2f$, avg gap = %.2f' % (beta, np.mean(gap)), fontsize=11)
    ax.legend(fontsize=8)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0.5, 12.5)
    ax.grid(alpha=0.3)

fig.text(0.5, 0.02, 'Task Complexity', ha='center', fontsize=14)
fig.text(0.02, 0.5, 'Selected Complexity', va='center', rotation='vertical', fontsize=14)
fig.suptitle(r'Complexity Matching at Different $\beta$', fontsize=16, fontweight='bold', y=0.96)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Fig02-complexity-matching.png"), dpi=150)
plt.close(fig)

# ============================================================================
# Fig 3: Router vs Random
# ============================================================================

task_c = np.array(results["experiment_3_router_vs_random"]["task_complexity"])
adaptive = np.array(results["experiment_3_router_vs_random"]["adaptive_score"])
random_s = np.array(results["experiment_3_router_vs_random"]["random_score"])
advantage = np.array(results["experiment_3_router_vs_random"]["advantage"])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

x = np.arange(len(task_c))
w = 0.35

bars1 = ax1.bar(x - w/2, adaptive, w, label='Adaptive Router', color='steelblue')
bars2 = ax1.bar(x + w/2, random_s, w, label='Random Selection', color='coral')
ax1.set_xlabel('Task Complexity', fontsize=12)
ax1.set_ylabel('Performance Score', fontsize=12)
ax1.set_title('Performance vs Task Complexity', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([str(int(t)) for t in task_c])
ax1.legend()
ax1.grid(alpha=0.3, axis='y')

colors2 = ['#4daf4a' if a > 0 else '#e41a1c' for a in advantage]
bars3 = ax2.bar(x, advantage, color=colors2, edgecolor='black', linewidth=0.5)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_xlabel('Task Complexity', fontsize=12)
ax2.set_ylabel('Advantage (Adaptive - Random)', fontsize=12)
ax2.set_title('Adaptive Routing Advantage', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([str(int(t)) for t in task_c])
ax2.grid(alpha=0.3, axis='y')

# Add value labels on bars
for bar, val in zip(bars3, advantage):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
             f'{val:.3f}', ha='center', va='bottom', fontsize=8)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "Fig03-router-vs-random.png"), dpi=150)
plt.close(fig)

# ============================================================================
# Fig 4: Boltzmann vs Best-Response
# ============================================================================

exp4 = results["experiment_4_boltzmann_vs_best_response"]
betas4 = exp4["betas"]
boltzmann = exp4["boltzmann_scores"]
best_resp = exp4["best_response_scores"]

fig, ax = plt.subplots(1, 1, figsize=(7, 5))
ax.plot(betas4, boltzmann, 'bo-', linewidth=2, markersize=6, label='Boltzmann Agent ($\\epsilon=0.1$)')
ax.plot(betas4, best_resp, 'rs-', linewidth=2, markersize=6, label='Best-Response Agent')
ax.set_xlabel(r'$\beta$ (complexity penalty)', fontsize=14)
ax.set_ylabel('Performance Score', fontsize=14)
ax.set_title(r'Boltzmann vs Best-Response Agent', fontsize=16, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(alpha=0.3)

# Mark crossover region
cross_idx = None
for i in range(len(betas4)-1):
    if (boltzmann[i] - best_resp[i]) * (boltzmann[i+1] - best_resp[i+1]) < 0:
        cross_idx = i
        break
if cross_idx is not None:
    ax.axvline(x=betas4[cross_idx], color='purple', linestyle='--', alpha=0.5,
               label=r'crossover at $\beta \approx %.1f$' % betas4[cross_idx])
    ax.legend(fontsize=11)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "Fig04-boltzmann-vs-br.png"), dpi=150)
plt.close(fig)

print(f"Figures saved to: {OUT}")
for f in sorted(os.listdir(OUT)):
    path = os.path.join(OUT, f)
    size = os.path.getsize(path)
    print(f"  {f}: {size/1024:.1f} KB")
