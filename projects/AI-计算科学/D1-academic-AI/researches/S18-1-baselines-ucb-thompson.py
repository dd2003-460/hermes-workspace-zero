#!/usr/bin/env python3
"""S18-1: UCB and Thompson Sampling Baselines for Kolmogorov Complexity Routing

Compares adaptive Boltzmann routing against standard bandit baselines:
- UCB1 (Auer et al. 2002): Upper Confidence Bound
- Thompson Sampling (Thompson 1933): Bayesian posterior sampling
- Random: uniform selection
- Best Response: deterministic greedy selection

Tests 3 environments: easy/medium/hard task complexity.
Measures: cumulative reward, complexity matching error, exploration efficiency.
"""

import json
import numpy as np
import os
from dataclasses import dataclass
from typing import List, Tuple
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "S18-1-baselines-results.json"
)

# ============================================================================
# Shared Models (reuse S18-1 framework)
# ============================================================================

@dataclass
class Tool:
    id: str
    complexity: int
    accuracy: float
    cost: float
    category: str

@dataclass
class Task:
    id: str
    complexity: int
    difficulty: float
    n_rounds: int = 200

def build_tools():
    tools = []
    for k in range(1, 4):
        tools.append(Tool(id=f"coarse_{k}", complexity=k, accuracy=0.4+0.1*k,
                          cost=0.1*k, category="coarse"))
    for k in range(4, 8):
        tools.append(Tool(id=f"medium_{k}", complexity=k, accuracy=0.6+0.05*(k-3),
                          cost=0.3+0.1*(k-3), category="medium"))
    for k in range(8, 13):
        tools.append(Tool(id=f"fine_{k}", complexity=k, accuracy=0.8+0.02*(k-7),
                          cost=0.7+0.1*(k-7), category="fine"))
    return tools

def compute_reward(tool: Tool, task: Task) -> float:
    """Reward = accuracy * complexity_match * (1 - cost_weight)."""
    gap = abs(tool.complexity - task.complexity)
    accuracy_cond = tool.accuracy * np.exp(-0.1 * gap)
    cost_penalty = 0.03 * tool.complexity
    return accuracy_cond - cost_penalty

# ============================================================================
# Agent Implementations
# ============================================================================

class BoltzmannAgent:
    """Boltzmann policy: P(t) ~ exp(-beta*K(t)) * acc(t)."""
    def __init__(self, tools: List[Tool], beta: float = 0.3):
        self.tools = tools
        self.beta = beta

    def select(self, task: Task) -> Tuple[Tool, int]:
        weights = []
        for t in self.tools:
            gap = abs(t.complexity - task.complexity)
            acc_cond = t.accuracy * np.exp(-0.1 * gap)
            w = np.exp(-self.beta * t.complexity) * acc_cond
            weights.append(max(w, 1e-10))
        total = sum(weights)
        probs = [w / total for w in weights]
        idx = int(np.random.choice(len(self.tools), p=probs))
        return self.tools[idx], idx


class UCB1Agent:
    """UCB1: P(t) = argmax Q(t) + c * sqrt(log(t_total) / N(t))."""
    def __init__(self, tools: List[Tool], c: float = 1.0):
        self.tools = tools
        self.c = c
        self.n_total = 0
        self.q_values = np.zeros(len(tools))
        self.n_selects = np.ones(len(tools))  # Laplace smoothing

    def select(self, task: Task) -> Tuple[Tool, float]:
        # Select each tool at least once before UCB kicks in
        if self.n_total < len(self.tools):
            idx = self.n_total
        else:
            ucb_values = self.q_values + self.c * np.sqrt(
                np.log(self.n_total) / self.n_selects
            )
            idx = int(np.argmax(ucb_values))
        return self.tools[idx], idx

    def update(self, idx: int, reward: float):
        self.n_total += 1
        self.n_selects[idx] += 1
        # Incremental mean update
        n = self.n_selects[idx]
        self.q_values[idx] += (reward - self.q_values[idx]) / n


class ThompsonAgent:
    """Thompson Sampling with Beta(alpha, beta) posterior for each tool."""
    def __init__(self, tools: List[Tool], alpha_init: float = 1.0, beta_init: float = 1.0):
        self.tools = tools
        self.alpha = np.full(len(tools), alpha_init)
        self.beta_param = np.full(len(tools), beta_init)

    def select(self, task: Task) -> Tuple[Tool, int]:
        # Sample from posterior for each tool
        samples = []
        for i, t in enumerate(self.tools):
            # Adjust posterior based on task compatibility
            gap = abs(t.complexity - task.complexity)
            # Scale mean reward estimate by task match
            compat = t.accuracy * np.exp(-0.1 * gap)
            samples.append(np.random.beta(self.alpha[i] * compat, self.beta_param[i] * (1 - compat + 1e-10)))
        idx = int(np.argmax(samples))
        return self.tools[idx], idx

    def update(self, idx: int, reward: float):
        # Reward ~ Bernoulli-like: scale to [0,1] for Beta posterior
        success = reward > 0.4  # threshold for "useful" tool
        self.alpha[idx] += success
        self.beta_param[idx] += (1 - success)


class RandomAgent:
    """Uniform random selection."""
    def __init__(self, tools: List[Tool]):
        self.tools = tools

    def select(self, task: Task) -> Tuple[Tool, int]:
        idx = int(np.random.randint(len(self.tools)))
        return self.tools[idx], idx


class BestResponseAgent:
    """Greedy: pick tool maximizing conditional accuracy - beta*cost."""
    def __init__(self, tools: List[Tool], beta: float = 0.3):
        self.tools = tools
        self.beta = beta

    def select(self, task: Task) -> Tuple[Tool, int]:
        best = 0
        best_score = -np.inf
        for i, t in enumerate(self.tools):
            gap = abs(t.complexity - task.complexity)
            acc_cond = t.accuracy * np.exp(-0.1 * gap)
            score = acc_cond - self.beta * t.complexity * 0.05
            if score > best_score:
                best_score = score
                best = i
        return self.tools[best], best


# ============================================================================
# Experiment Protocol
# ============================================================================

def run_rounds(agent, tools, task, n_rounds: int, use_ucb_update: bool = False,
               ucb_agent: UCB1Agent = None):
    """Run sequential rounds. Returns (rewards, complexities, accs)."""
    rewards = []
    complexities = []
    accuracies = []

    for round_idx in range(n_rounds):
        selected, idx = agent.select(task)
        reward = compute_reward(selected, task)
        complexities.append(selected.complexity)
        accuracies.append(selected.accuracy)
        rewards.append(reward)

        if use_ucb_update and ucb_agent is not None:
            ucb_agent.update(idx, reward)

    return rewards, complexities, accuracies


def evaluate_all_agents(tools, task, n_rounds=200, n_seeds=5):
    """Evaluate all agents on one task, averaged over seeds."""
    agents = {
        "boltzmann": lambda: BoltzmannAgent(tools, beta=0.3),
        "ucb1_c0.5": lambda: UCB1Agent(tools, c=0.5),
        "ucb1_c1.0": lambda: UCB1Agent(tools, c=1.0),
        "ucb1_c2.0": lambda: UCB1Agent(tools, c=2.0),
        "thompson": lambda: ThompsonAgent(tools),
        "random": lambda: RandomAgent(tools),
        "best_response": lambda: BestResponseAgent(tools, beta=0.3),
    }

    results = {name: {"rewards": [], "complexities": [], "accuracies": []}
               for name in agents}

    for seed in range(n_seeds):
        for name, factory in agents.items():
            agent = factory()
            r, c, a = run_rounds(agent, tools, task, n_rounds)
            results[name]["rewards"].extend(r)
            results[name]["complexities"].extend(c)
            results[name]["accuracies"].extend(a)

    # Average over seeds
    for name in results:
        for key in ["rewards", "complexities", "accuracies"]:
            results[name][key] = np.mean(results[name][key])

    return results


# ============================================================================
# Experiments
# ============================================================================

def experiment_1_easy_task():
    """Easy task (complexity=3) — should select coarse/medium tools."""
    print("=" * 70)
    print("EXPERIMENT 1: Easy Task (K=3)")
    print("=" * 70)

    tools = build_tools()
    task = Task(id="easy", complexity=3, difficulty=0.3, n_rounds=200)
    results = evaluate_all_agents(tools, task, n_rounds=200, n_seeds=10)

    summary = {}
    for name, data in results.items():
        mean_reward = np.mean(data["rewards"])
        mean_complexity = np.mean(data["complexities"])
        mean_acc = np.mean(data["accuracies"])
        print(f"  {name:20s}: reward={mean_reward:.4f}, K={mean_complexity:.2f}, acc={mean_acc:.4f}")
        summary[name] = {
            "mean_reward": float(mean_reward),
            "mean_complexity": float(mean_complexity),
            "mean_accuracy": float(mean_acc),
        }
    return summary


def experiment_2_medium_task():
    """Medium task (complexity=7) — should select medium tools."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Medium Task (K=7)")
    print("=" * 70)

    tools = build_tools()
    task = Task(id="medium", complexity=7, difficulty=0.6, n_rounds=200)
    results = evaluate_all_agents(tools, task, n_rounds=200, n_seeds=10)

    summary = {}
    for name, data in results.items():
        mean_reward = np.mean(data["rewards"])
        mean_complexity = np.mean(data["complexities"])
        mean_acc = np.mean(data["accuracies"])
        print(f"  {name:20s}: reward={mean_reward:.4f}, K={mean_complexity:.2f}, acc={mean_acc:.4f}")
        summary[name] = {
            "mean_reward": float(mean_reward),
            "mean_complexity": float(mean_complexity),
            "mean_accuracy": float(mean_acc),
        }
    return summary


def experiment_3_hard_task():
    """Hard task (complexity=11) — should select fine tools."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Hard Task (K=11)")
    print("=" * 70)

    tools = build_tools()
    task = Task(id="hard", complexity=11, difficulty=0.9, n_rounds=200)
    results = evaluate_all_agents(tools, task, n_rounds=200, n_seeds=10)

    summary = {}
    for name, data in results.items():
        mean_reward = np.mean(data["rewards"])
        mean_complexity = np.mean(data["complexities"])
        mean_acc = np.mean(data["accuracies"])
        print(f"  {name:20s}: reward={mean_reward:.4f}, K={mean_complexity:.2f}, acc={mean_acc:.4f}")
        summary[name] = {
            "mean_reward": float(mean_reward),
            "mean_complexity": float(mean_complexity),
            "mean_accuracy": float(mean_acc),
        }
    return summary


def experiment_4_learning_curves():
    """
    Exp 4: Learning curves — cumulative reward over rounds.
    Tests whether UCB/Thompson learn faster than Boltzmann.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Learning Curves (Medium Task)")
    print("=" * 70)

    tools = build_tools()
    task = Task(id="medium", complexity=7, difficulty=0.6, n_rounds=500)

    agents = {
        "boltzmann": BoltzmannAgent(tools, beta=0.3),
        "ucb1_c1.0": UCB1Agent(tools, c=1.0),
        "thompson": ThompsonAgent(tools),
        "random": RandomAgent(tools),
    }

    learning = {name: {"cumulative_reward": [0.0], "running_avg": []}
                for name in agents}

    for t in range(500):
        for name, agent in agents.items():
            selected, idx = agent.select(task)
            reward = compute_reward(selected, task)

            # Update UCB/Thompson agents
            if isinstance(agent, UCB1Agent):
                agent.update(idx, reward)
            elif isinstance(agent, ThompsonAgent):
                agent.update(idx, reward)

            # Track learning
            learning[name]["cumulative_reward"].append(
                learning[name]["cumulative_reward"][-1] + reward
            )
            learning[name]["running_avg"].append(
                learning[name]["cumulative_reward"][-1] / (t + 1)
            )

    # Extract learning data
    result = {}
    for name in agents:
        cum = np.array(learning[name]["cumulative_reward"])
        avg = np.array(learning[name]["running_avg"])
        result[name] = {
            "final_cumulative_reward": float(cum[-1]),
            "final_avg_reward": float(avg[-1]),
            "reward_at_50": float(cum[50]),
            "reward_at_100": float(cum[100]),
            "reward_at_200": float(cum[200]),
            "reward_at_500": float(cum[-1]),
            "learning_rate": float((cum[200] - cum[50]) / 150),
        }
        print(f"  {name:20s}: final_cum={cum[-1]:.4f}, final_avg={avg[-1]:.4f}, "
              f"learn_rate={result[name]['learning_rate']:.4f}")

    return result


def experiment_5_ucb_vs_boltzmann_sweep():
    """
    Exp 5: Sweep UCB c and Boltzmann beta.
    Tests robustness across hyperparameter choices.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: Hyperparameter Sweep")
    print("=" * 70)

    tools = build_tools()
    task = Task(id="medium", complexity=7, difficulty=0.6, n_rounds=300)

    ucb_cs = [0.1, 0.5, 1.0, 2.0, 5.0]
    beta_betas = [0.1, 0.3, 0.5, 1.0, 2.0]

    results = {"ucb_sweep": {}, "boltzmann_sweep": {}, "comparison": []}

    for c in ucb_cs:
        agent = UCB1Agent(tools, c=c)
        rewards, _, _ = run_rounds(agent, tools, task, 300, use_ucb_update=True, ucb_agent=agent)
        mean_r = np.mean(rewards)
        results["ucb_sweep"][f"c={c}"] = float(mean_r)
        print(f"  UCB c={c:.1f}: mean_reward={mean_r:.4f}")

    for beta in beta_betas:
        agent = BoltzmannAgent(tools, beta=beta)
        rewards, _, _ = run_rounds(agent, tools, task, 300)
        mean_r = np.mean(rewards)
        results["boltzmann_sweep"][f"beta={beta}"] = float(mean_r)
        print(f"  Boltzmann beta={beta:.1f}: mean_reward={mean_r:.4f}")

    # Direct comparison: best UCB vs best Boltzmann
    best_ucb_c = max(results["ucb_sweep"], key=results["ucb_sweep"].get)
    best_boltz = max(results["boltzmann_sweep"], key=results["boltzmann_sweep"].get)
    results["comparison"] = {
        "best_ucb": {f"{best_ucb_c}": results["ucb_sweep"][best_ucb_c]},
        "best_boltzmann": {f"{best_boltz}": results["boltzmann_sweep"][best_boltz]},
    }
    print(f"\n  Best UCB: {best_ucb_c} -> {results['ucb_sweep'][best_ucb_c]:.4f}")
    print(f"  Best Boltzmann: {best_boltz} -> {results['boltzmann_sweep'][best_boltz]:.4f}")

    return results


# ============================================================================
# Main
# ============================================================================

def main():
    np.random.seed(42)

    all_results = {}

    # Exp 1-3: Three environments
    all_results["experiment_1_easy"] = experiment_1_easy_task()
    all_results["experiment_2_medium"] = experiment_2_medium_task()
    all_results["experiment_3_hard"] = experiment_3_hard_task()

    # Exp 4: Learning curves
    all_results["experiment_4_learning"] = experiment_4_learning_curves()

    # Exp 5: Hyperparameter sweep
    all_results["experiment_5_sweep"] = experiment_5_ucb_vs_boltzmann_sweep()

    # Statistical summary
    easy_avg = {k: v["mean_reward"] for k, v in all_results["experiment_1_easy"].items()}
    medium_avg = {k: v["mean_reward"] for k, v in all_results["experiment_2_medium"].items()}
    hard_avg = {k: v["mean_reward"] for k, v in all_results["experiment_3_hard"].items()}

    all_results["summary"] = {
        "easy_task": easy_avg,
        "medium_task": medium_avg,
        "hard_task": hard_avg,
        "rankings": {
            "easy": sorted(easy_avg.items(), key=lambda x: x[1], reverse=True)[:3],
            "medium": sorted(medium_avg.items(), key=lambda x: x[1], reverse=True)[:3],
            "hard": sorted(hard_avg.items(), key=lambda x: x[1], reverse=True)[:3],
        }
    }

    json.dump(all_results, open(OUTPUT_DIR, "w"), indent=2)
    print(f"\n{'=' * 70}")
    print(f"ALL RESULTS SAVED TO: {OUTPUT_DIR}")
    print(f"{'=' * 70}")

    # Key findings
    print(f"\nKEY FINDINGS:")
    for env_name in ["easy", "medium", "hard"]:
        ranking = all_results["summary"]["rankings"][env_name]
        print(f"\n  {env_name.upper()} TASK Top-3:")
        for i, (name, score) in enumerate(ranking):
            print(f"    {i+1}. {name}: {score:.4f}")


if __name__ == "__main__":
    main()
