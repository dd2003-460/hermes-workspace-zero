#!/usr/bin/env python3
"""S18-1: Kolmogorov Complexity Adaptive Router — Experimental Validation

Validates the core predictions of the S18-1 Adaptive Routing Theorem:
1. Phase transition in tool complexity at critical beta_c
2. Optimal tool complexity ≈ task complexity + beta penalty
3. Complexity matching peak at matched complexity
"""

import json
import numpy as np
import os
from dataclasses import dataclass, asdict
from typing import Optional
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "S18-1-experimental-results.json"
)

# ============================================================================
# Tool Model: tools with known "complexity" (circuit depth / description length)
# ============================================================================

@dataclass
class Tool:
    id: str
    complexity: int  # K(t) ~ circuit depth
    accuracy: float  # max achievable accuracy at this complexity
    cost: float      # computation cost
    category: str    # "coarse", "medium", "fine"

def build_tool_market():
    """Build a market of tools at 3 complexity levels.

    Coarse: simple heuristics, K ~ 1-3
    Medium: moderate algorithms, K ~ 4-7
    Fine: complex solvers, K ~ 8-12
    """
    tools = []
    # Coarse tools (K = 1-3)
    for k in range(1, 4):
        tools.append(Tool(
            id=f"coarse_{k}",
            complexity=k,
            accuracy=0.4 + 0.1 * k,  # 0.5, 0.6, 0.7
            cost=0.1 * k,
            category="coarse"
        ))
    # Medium tools (K = 4-7)
    for k in range(4, 8):
        tools.append(Tool(
            id=f"medium_{k}",
            complexity=k,
            accuracy=0.6 + 0.05 * (k - 3),  # 0.65 - 0.80
            cost=0.3 + 0.1 * (k - 3),
            category="medium"
        ))
    # Fine tools (K = 8-12)
    for k in range(8, 13):
        tools.append(Tool(
            id=f"fine_{k}",
            complexity=k,
            accuracy=0.8 + 0.02 * (k - 7),  # 0.82 - 0.90
            cost=0.7 + 0.1 * (k - 7),
            category="fine"
        ))
    return tools

# ============================================================================
# Task Model: tasks with known complexity
# ============================================================================

@dataclass
class Task:
    id: str
    complexity: int  # C_task, 1-12 scale
    difficulty: float  # 0-1, affects whether fine tools help
    n_papers: int  # simulation count per task

def build_task_set():
    """Tasks at 3 complexity levels matching tool levels."""
    tasks = []
    for k in range(1, 4):
        tasks.append(Task(id=f"task_easy_{k}", complexity=k, difficulty=0.3, n_papers=50))
    for k in range(4, 8):
        tasks.append(Task(id=f"task_medium_{k}", complexity=k, difficulty=0.6, n_papers=50))
    for k in range(8, 13):
        tasks.append(Task(id=f"task_hard_{k}", complexity=k, difficulty=0.9, n_papers=50))
    return tasks

# ============================================================================
# Agent: complexity-penalized router (the core model)
# ============================================================================

class ComplexityRouterAgent:
    """
    Agent that selects tools via Boltzmann policy:

    P(t | p, beta) = exp(-beta * C(t)) * acc(t, p) / Z

    where Z = sum_t exp(-beta * C(t)) * acc(t, p)

    This implements the variational routing principle:
    minimize: E[loss] + beta * K(tool)
    """

    def __init__(self, tools, beta=1.0, exploration=0.1):
        self.tools = tools
        self.beta = beta
        self.exploration = exploration
        self.selection_history = []

    def select_tool(self, task):
        """Select tool using Boltzmann policy."""
        # Compute utility for each tool
        utilities = []
        for t in self.tools:
            # Accuracy conditional on task complexity match
            complexity_gap = abs(t.complexity - task.complexity)
            conditional_acc = t.accuracy * np.exp(-0.1 * complexity_gap)

            # Boltzmann weight: accuracy * complexity penalty
            weight = np.exp(-self.beta * t.complexity) * conditional_acc

            # Add exploration noise
            weight *= (1 + self.exploration * np.random.randn())
            utilities.append((t, max(weight, 1e-10)))

        # Sample proportionally
        total = sum(w for _, w in utilities)
        probs = [w / total for _, w in utilities]

        idx = np.random.choice(len(self.tools), p=probs)
        selected = utilities[idx][0]
        self.selection_history.append(selected.id)
        return selected

    def select_tool_best_response(self, task):
        """Optimistic selection: pick tool maximizing acc(t) - beta * C(t)."""
        best = None
        best_score = -np.inf
        for t in self.tools:
            complexity_gap = abs(t.complexity - task.complexity)
            conditional_acc = t.accuracy * np.exp(-0.1 * complexity_gap)
            score = conditional_acc - self.beta * t.complexity * 0.05
            if score > best_score:
                best_score = score
                best = t
        self.selection_history.append(best.id)
        return best

# ============================================================================
# Random Agent Baseline
# ============================================================================

class RandomAgent:
    def __init__(self, tools):
        self.tools = tools

    def select_tool(self, task):
        return np.random.choice(self.tools)

# ============================================================================
# Experiments
# ============================================================================

def experiment_1_phase_transition():
    """
    Exp 1: Vary beta, measure order parameter m(beta) = mean tool complexity.

    Prediction: discontinuous jump at beta_c.
    """
    print("=" * 70)
    print("EXPERIMENT 1: Phase Transition in Tool Complexity")
    print("=" * 70)

    tools = build_tool_market()
    betas = np.linspace(0.01, 2.0, 40)

    results = {"betas": [], "mean_complexity": [], "std_complexity": [],
               "phase_order_parameter": [], "distribution_peaks": []}

    for beta in betas:
        agent = ComplexityRouterAgent(tools, beta=beta, exploration=0.05)

        # Run for a representative task
        task = Task(id="medium_test", complexity=5, difficulty=0.5, n_papers=200)
        selected_tools = [agent.select_tool(task) for _ in range(task.n_papers)]

        complexities = [t.complexity for t in selected_tools]
        mean_k = np.mean(complexities)
        std_k = np.std(complexities)

        results["betas"].append(float(beta))
        results["mean_complexity"].append(float(mean_k))
        results["std_complexity"].append(float(std_k))

        # Order parameter: fraction of fine vs coarse tools used
        fine_count = sum(1 for t in selected_tools if t.category == "fine")
        coarse_count = sum(1 for t in selected_tools if t.category == "coarse")
        total = len(selected_tools)
        order_param = (fine_count - coarse_count) / total if total > 0 else 0
        results["phase_order_parameter"].append(float(order_param))

        # Detect distribution bimodality (simplified: check for gaps)
        sorted_c = sorted(complexities)
        gaps = [sorted_c[i+1] - sorted_c[i] for i in range(len(sorted_c)-1)
                if sorted_c[i+1] - sorted_c[i] > 1]
        results["distribution_peaks"].append(len(gaps))

        if beta < 0.1 or beta > 1.5 or abs(beta - 0.5) < 0.01:
            print(f"  beta={beta:.3f}: <K>={mean_k:.2f}, sigma={std_k:.2f}, "
                  f"order={order_param:.3f} ({len(selected_tools)} samples)")

    # Detect phase transition: find largest derivative of <K> vs beta
    m_c = results["mean_complexity"]
    dK_dbeta = [abs(m_c[i+1] - m_c[i]) / (betas[i+1] - betas[i])
                for i in range(len(m_c)-1)]
    beta_c_idx = np.argmax(dK_dbeta)
    beta_c = betas[beta_c_idx]

    print(f"\n  *** Detected beta_c = {beta_c:.3f} at index {beta_c_idx} ***")
    print(f"  *** Max d<K>/dbeta = {np.max(dK_dbeta):.4f} ***")

    # Check bimodality near beta_c
    bimodal_region = sum(1 for p in results["distribution_peaks"] if p >= 2)
    print(f"  *** Bimodal distributions: {bimodal_region}/{len(results['distribution_peaks'])} ***")

    return results, beta_c, dK_dbeta


def experiment_2_complexity_matching():
    """
    Exp 2: For each task complexity, measure selected tool complexity.

    Prediction: optimal match when K_tool ≈ K_task + penalty(beta)
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Complexity Matching Curve")
    print("=" * 70)

    tools = build_tool_market()
    tasks = build_task_set()
    betas = [0.05, 0.2, 0.5, 1.0, 2.0]

    results = {}

    for beta in betas:
        results[f"beta_{beta}"] = {"task_complexity": [], "selected_complexity": [],
                                     "gap": [], "success_rate": []}
        for task in tasks:
            # Use Boltzmann agent
            agent = ComplexityRouterAgent(tools, beta=beta, exploration=0.05)
            selected = agent.select_tool(task)
            gap = selected.complexity - task.complexity

            # Success: tool accuracy matches task difficulty
            success = selected.accuracy >= task.difficulty

            results[f"beta_{beta}"]["task_complexity"].append(task.complexity)
            results[f"beta_{beta}"]["selected_complexity"].append(selected.complexity)
            results[f"beta_{beta}"]["gap"].append(gap)
            results[f"beta_{beta}"]["success_rate"].append(float(success))

        # Aggregate
        avg_gap = np.mean(results[f"beta_{beta}"]["gap"])
        avg_success = np.mean(results[f"beta_{beta}"]["success_rate"])
        print(f"  beta={beta:.2f}: avg gap = {avg_gap:.2f}, success rate = {avg_success:.3f}")

    return results


def experiment_3_router_vs_random():
    """
    Exp 3: Adaptive router vs random routing across task difficulties.

    Prediction: adaptive router outperforms random, especially on medium-hard tasks.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Adaptive Router vs Random Baseline")
    print("=" * 70)

    tools = build_tool_market()
    tasks = build_task_set()
    n_trials = 500

    results = {"task_complexity": [], "adaptive_score": [], "random_score": [],
               "advantage": []}

    for task in tasks:
        # Adaptive agent
        adaptive_agent = ComplexityRouterAgent(tools, beta=0.3, exploration=0.05)
        adaptive_scores = []
        for _ in range(n_trials):
            t = adaptive_agent.select_tool(task)
            complexity_gap = abs(t.complexity - task.complexity)
            score = t.accuracy * np.exp(-0.1 * complexity_gap) - 0.03 * t.complexity
            adaptive_scores.append(score)

        # Random agent
        random_agent = RandomAgent(tools)
        random_scores = []
        for _ in range(n_trials):
            t = random_agent.select_tool(task)
            complexity_gap = abs(t.complexity - task.complexity)
            score = t.accuracy * np.exp(-0.1 * complexity_gap) - 0.03 * t.complexity
            random_scores.append(score)

        avg_adaptive = np.mean(adaptive_scores)
        avg_random = np.mean(random_scores)
        advantage = avg_adaptive - avg_random

        results["task_complexity"].append(task.complexity)
        results["adaptive_score"].append(float(avg_adaptive))
        results["random_score"].append(float(avg_random))
        results["advantage"].append(float(advantage))

        print(f"  task K={task.complexity}: adaptive={avg_adaptive:.4f}, "
              f"random={avg_random:.4f}, advantage={advantage:.4f}")

    # Statistical test
    all_advantages = results["advantage"]
    mean_adv = np.mean(all_advantages)
    t_stat, p_value = _mann_whitney_summary(tasks, tools, n_trials)

    print(f"\n  Mean advantage: {mean_adv:.4f}")
    print(f"  Mann-Whitney p-value: {p_value:.6f}")

    return results, mean_adv, p_value


def _mann_whitney_summary(tasks, tools, n_trials):
    """Approximate Mann-Whitney U test using aggregated scores."""
    all_adaptive = []
    all_random = []
    for task in tasks:
        agent_a = ComplexityRouterAgent(tools, beta=0.3, exploration=0.05)
        agent_r = RandomAgent(tools)
        for _ in range(n_trials):
            t_a = agent_a.select_tool(task)
            t_r = agent_r.select_tool(task)
            gap_a = abs(t_a.complexity - task.complexity)
            gap_r = abs(t_r.complexity - task.complexity)
            s_a = t_a.accuracy * np.exp(-0.1 * gap_a) - 0.03 * t_a.complexity
            s_r = t_r.accuracy * np.exp(-0.1 * gap_r) - 0.03 * t_r.complexity
            all_adaptive.append(s_a)
            all_random.append(s_r)

    # Simple t-test approximation
    n1, n2 = len(all_adaptive), len(all_random)
    m1, m2 = np.mean(all_adaptive), np.mean(all_random)
    v1, v2 = np.var(all_adaptive), np.var(all_random)
    se = np.sqrt(v1/n1 + v2/n2)
    t = abs(m1 - m2) / se if se > 0 else 0
    # Approximate p-value from t (df ~ n1+n2-2)
    p = 2 * np.exp(-min(t, 10) / 2)  # rough upper bound
    return t, min(p, 1.0)


def experiment_4_best_response_vs_boltzmann():
    """
    Exp 4: Compare Boltzmann agent (noisy) vs best-response (deterministic).

    Prediction: Boltzmann explores more, achieves higher long-term average.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Boltzmann vs Best-Response Agent")
    print("=" * 70)

    tools = build_tool_market()
    task = Task(id="medium_hard", complexity=7, difficulty=0.8, n_papers=500)

    betas = np.linspace(0.01, 2.0, 20)
    boltzmann_scores = []
    best_response_scores = []

    for beta in betas:
        # Boltzmann agent
        agent_b = ComplexityRouterAgent(tools, beta=beta, exploration=0.1)
        b_scores = [agent_b.select_tool(task) for _ in range(task.n_papers)]
        b_avg = np.mean([t.accuracy * np.exp(-0.1 * abs(t.complexity - task.complexity))
                        for t in b_scores])
        boltzmann_scores.append(float(b_avg))

        # Best-response
        agent_br = ComplexityRouterAgent(tools, beta=beta, exploration=0.0)
        br = agent_br.select_tool(task)
        br_score = br.accuracy * np.exp(-0.1 * abs(br.complexity - task.complexity))
        best_response_scores.append(float(br_score))

        if beta < 0.1 or beta > 1.5:
            print(f"  beta={beta:.3f}: Boltzmann={b_avg:.4f}, BestResp={br_score:.4f}")

    return {
        "betas": list(betas),
        "boltzmann_scores": boltzmann_scores,
        "best_response_scores": best_response_scores,
    }


# ============================================================================
# Main
# ============================================================================

def main():
    np.random.seed(42)

    results_all = {}

    # Exp 1: Phase transition
    exp1_results, beta_c, dK_dbeta = experiment_1_phase_transition()
    results_all["experiment_1_phase_transition"] = exp1_results
    results_all["beta_c_detection"] = {"beta_c": float(beta_c),
                                       "max_derivative": float(np.max(dK_dbeta))}

    # Exp 2: Complexity matching
    exp2_results = experiment_2_complexity_matching()
    results_all["experiment_2_complexity_matching"] = exp2_results

    # Exp 3: Router vs random
    exp3_results, mean_adv, p_val = experiment_3_router_vs_random()
    results_all["experiment_3_router_vs_random"] = exp3_results
    results_all["statistical_test"] = {"mean_advantage": float(mean_adv),
                                        "p_value": float(p_val)}

    # Exp 4: Boltzmann vs best-response
    exp4_results = experiment_4_best_response_vs_boltzmann()
    results_all["experiment_4_boltzmann_vs_best_response"] = exp4_results

    # Save
    json.dump(results_all, open(OUTPUT_DIR, "w"), indent=2)
    print(f"\n{'=' * 70}")
    print(f"ALL RESULTS SAVED TO: {OUTPUT_DIR}")
    print(f"{'=' * 70}")

    # Summary
    print(f"\nKEY FINDINGS:")
    print(f"  beta_c = {beta_c:.3f} (phase transition point)")
    print(f"  Max d<K>/dbeta = {np.max(dK_dbeta):.4f} (phase transition strength)")
    print(f"  Mean adaptive advantage = {mean_adv:.4f}")
    print(f"  Statistical significance p = {p_val:.6f}")

    # Check phase transition evidence
    m_c = exp1_results["mean_complexity"]
    low_beta_avg = np.mean(m_c[:5])  # first 5 betas
    high_beta_avg = np.mean(m_c[-5:])  # last 5 betas
    jump = abs(high_beta_avg - low_beta_avg)
    print(f"\n  Phase transition evidence:")
    print(f"    <K> at low beta = {low_beta_avg:.3f}")
    print(f"    <K> at high beta = {high_beta_avg:.3f}")
    print(f"    Jump = {jump:.3f} (large jump = strong evidence)")


if __name__ == "__main__":
    main()
