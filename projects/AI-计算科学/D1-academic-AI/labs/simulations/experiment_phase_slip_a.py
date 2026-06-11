#!/usr/bin/env python3
"""
Protocol A: Long-time chimera integration — lifetime distribution.

Three M1 chimera seeds (run_idx 42, 43, 44) run for T_total = 500,000 steps.
Phase-slip tracking every 10 steps (Reviewer-5 Note 3).
State saved every 500 steps (1,000 snapshots per run).

Output: collapse_times, slip events, survival function data, sector coherence histories.
"""

import sys

sys.path.insert(0, ".")

import numpy as np
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

from experiment_chimera_spatial_coupling import (
    simulate_kuramoto_ring,
    piecewise_k,
    detect_chimera_in_domain,
)
from phase_slip_tracker import PhaseSlipTracker, PhaseSlipAnalyzer

# ---------------------------------------------------------------------------
# Protocol A constants
# ---------------------------------------------------------------------------

N_TOTAL = 1500
N_PER_DOMAIN = N_TOTAL // 2
DT = 0.02
DOMAIN_BOUNDARIES = [0.4, 0.5, 0.9]
EPS_A = 0.6
EPS_B = 0.6
DELTA = 0.15
K_TRANSITION = 0.3
N_SECTORS = 8

# Protocol A parameters
T_TRANSIENT = 50_000  # Same as M1 — chimera must already be formed
T_TOTAL = 500_000  # 10x M1 measure window
SAVE_INTERVAL = 500  # State snapshot interval
SLIP_CHECK_INTERVAL = 10  # Phase-slip check every 10 steps (Reviewer-5 Note 3)

# Chimera seeds — M1 confirmed these are chimera-producing (SEED_BASE + run_idx)
SEED_BASE = 42
CHIMERA_SEEDS = [SEED_BASE, SEED_BASE + 1, SEED_BASE + 2]  # 42, 43, 44

# Domain definitions for phase_slip_tracker
# Domain A: pos [0, 0.4), Domain B: pos [0.5, 0.9)
# Pre-compute per-sector masks for both domains


def _build_domain_masks():
    """Pre-compute position arrays and sector masks for slip tracking."""
    pos = np.linspace(0, 1, N_TOTAL, endpoint=False)
    b1, b2, b3 = DOMAIN_BOUNDARIES

    domain_a_mask = (pos >= 0) & (pos < b1)
    domain_b_mask = (pos >= b2) & (pos < b3)

    a_sectors = []
    b_sectors = []

    # Domain A: N_A = int(b1 * N_TOTAL) oscillators
    N_a = int(b1 * N_TOTAL)
    bin_size_a = N_a // N_SECTORS
    for s in range(N_SECTORS):
        start = s * bin_size_a
        end = (s + 1) * bin_size_a if s < N_SECTORS - 1 else N_a
        a_sectors.append(domain_a_mask & (np.arange(N_TOTAL) >= start) & (np.arange(N_TOTAL) < end))

    # Domain B
    N_b = int((b3 - b2) * N_TOTAL)
    bin_size_b = N_b // N_SECTORS
    global_offset = int(b2 * N_TOTAL)
    for s in range(N_SECTORS):
        start = global_offset + s * bin_size_b
        end = global_offset + (s + 1) * bin_size_b if s < N_SECTORS - 1 else int(b3 * N_TOTAL)
        b_sectors.append(domain_b_mask & (np.arange(N_TOTAL) >= start) & (np.arange(N_TOTAL) < end))

    return a_sectors, b_sectors


# ---------------------------------------------------------------------------
# Protocol A implementation
# ---------------------------------------------------------------------------


def run_protocol_a(
    output_dir: str = "labs/simulations/results",
    seeds: Optional[List[int]] = None,
    t_total: int = T_TOTAL,
) -> Dict:
    """
    Protocol A: long-time integration for 3 chimera seeds.

    Each run:
      1. Integrate T_transient steps from random IC
      2. Integrate t_total steps with slip tracking
      3. Record collapse times, slip events, sector histories
    """
    if seeds is None:
        seeds = CHIMERA_SEEDS

    seeds = sorted(set(seeds))
    a_sectors, b_sectors = _build_domain_masks()

    print(f"\n{'#' * 70}")
    print(f"# Protocol A: Long-Time Chimera Lifetime Study")
    print(f"# N={N_TOTAL}, T_transient={T_TRANSIENT}, T_total={t_total}")
    print(f"# SLIP_CHECK_INTERVAL={SLIP_CHECK_INTERVAL} (Reviewer-5 Note 3)")
    print(f"# SAVE_INTERVAL={SAVE_INTERVAL}")
    print(f"# Sectors: N_SECTORS={N_SECTORS} per domain, 2 domains")
    print(f"# Seeds: {seeds}")
    print(f"{'#' * 70}\n")

    output = {
        "protocol": "A_long_lifetime",
        "parameters": {
            "N_total": N_TOTAL,
            "dt": DT,
            "domain_boundaries": DOMAIN_BOUNDARIES,
            "eps_a": EPS_A,
            "eps_b": EPS_B,
            "delta": DELTA,
            "k_transition": K_TRANSITION,
            "n_sectors": N_SECTORS,
            "t_transient": T_TRANSIENT,
            "t_total": t_total,
            "slip_check_interval": SLIP_CHECK_INTERVAL,
            "save_interval": SAVE_INTERVAL,
        },
        "runs": [],
    }

    total_slips_a = 0
    total_slips_b = 0
    collapse_times = []

    for seed in seeds:
        print(f"{'=' * 50}")
        print(f"  Seed: {seed}")
        print(f"{'=' * 50}")

        rng = np.random.RandomState(seed)
        theta = rng.uniform(0, 2 * np.pi, N_TOTAL)
        pos = np.linspace(0, 1, N_TOTAL, endpoint=False)

        k_weights = piecewise_k(
            pos,
            K0=1.0,
            eps_a=EPS_A,
            eps_b=EPS_B,
            delta=DELTA,
            k_transition=K_TRANSITION,
            domain_boundaries=DOMAIN_BOUNDARIES,
        )

        # --- Slip trackers ---
        tracker_a = PhaseSlipTracker(domain_id=0)
        tracker_b = PhaseSlipTracker(domain_id=1)

        # --- Coherence time series ---
        r_a_series = []
        r_b_series = []
        r_global_series = []
        slip_events_a = []
        slip_events_b = []
        collapse_time: Optional[float] = None

        chimera_surviving = True
        collapsed_a = False
        collapsed_b = False

        snapshot_counter = 0
        step_since_collapse_check = 0

        # Simulate transient (no tracking)
        for t in range(T_TRANSIENT):
            theta = simulate_kuramoto_ring(theta, k_weights, DT)

        # --- Measure window with tracking ---
        for t in range(t_total):
            theta = simulate_kuramoto_ring(theta, k_weights, DT)
            step = T_TRANSIENT + t

            is_slip_check = (t % SLIP_CHECK_INTERVAL == 0)
            is_snapshot = (t % SAVE_INTERVAL == 0)

            if is_slip_check or is_snapshot:
                # Sector coherence + phase variance
                a_r_local = []
                b_r_local = []
                for mask in a_sectors:
                    a_r_local.append(PhaseSlipTracker._compute_sector_r_s(theta, mask))
                for mask in b_sectors:
                    b_r_local.append(PhaseSlipTracker._compute_sector_r_s(theta, mask))

                if is_slip_check:
                    # --- Phase slip detection ---
                    new_a = tracker_a.detect_slips(theta, a_sectors, step)
                    new_b = tracker_b.detect_slips(theta, b_sectors, step)
                    slip_events_a.extend(new_a)
                    slip_events_b.extend(new_b)

                if is_snapshot:
                    r_a_series.append(np.mean(a_r_local))
                    r_b_series.append(np.mean(b_r_local))
                    r_global_series.append(float(abs(np.mean(np.exp(1j * theta)))))
                    snapshot_counter += 1

                    # --- Collapse detection ---
                    if not collapsed_a and np.all(np.array(a_r_local) > 0.8):
                        collapsed_a = True
                    if not collapsed_b and np.all(np.array(b_r_local) > 0.8):
                        collapsed_b = True

                    # A domain is "collapsed" when all sectors have r > 0.7
                    # for 10,000 timesteps (≈ 5% of t_total)
                    if collapsed_a:
                        step_since_collapse_check += 1
                        if step_since_collapse_check >= 10000:
                            # Full chimera collapsed — entire system synchronized
                            collapse_time = float(step - 10000)
                            chimera_surviving = False
                            break
                    else:
                        step_since_collapse_check = 0

            # Fast simulation step (every step, not just check intervals)
            # Already done above at line: theta = simulate_kuramoto_ring(...)

        run_summary = {
            "seed": seed,
            "chimera_survived": chimera_surviving,
            "collapse_time": collapse_time,
            "n_snapshots": snapshot_counter,
            "n_slips_domain_a": tracker_a.slip_count,
            "n_slips_domain_b": tracker_b.slip_count,
            "total_slips": tracker_a.slip_count + tracker_b.slip_count,
            "final_r_a_mean": float(np.mean(a_r_local)) if a_r_local else 0.0,
            "final_r_b_mean": float(np.mean(b_r_local)) if b_r_local else 0.0,
            "final_r_global": float(abs(np.mean(np.exp(1j * theta)))),
        }
        output["runs"].append(run_summary)

        collapse_times.append(collapse_time)
        total_slips_a += tracker_a.slip_count
        total_slips_b += tracker_b.slip_count

        print(f"  Seed {seed}: survived={chimera_surviving}, "
              f"collapse_t={collapse_time}, "
              f"slips_A={tracker_a.slip_count}, slips_B={tracker_b.slip_count}")

    # --- Aggregate analysis ---
    # Survival function
    surv_bins, surv_vals = PhaseSlipAnalyzer.compute_survival_function(
        collapse_times, t_total, bin_width=10_000
    )

    # Metastability classification
    metastability = PhaseSlipAnalyzer.classify_metastability(collapse_times, t_total)

    # Global slip rate
    global_slip_rate = PhaseSlipAnalyzer.compute_slip_rate(
        slip_events_a + slip_events_b,
        (T_TRANSIENT, T_TRANSIENT + t_total),
        N_SECTORS * 2,
    )

    # Sector PSD from coherence histories (for Protocol D)
    sector_psd = {}
    for idx, (r_series, label) in enumerate([
        (r_a_series, "A"), (r_b_series, "B")
    ]):
        if r_series:
            for s in range(N_SECTORS):
                sector_psd[f"{label}_S{s}"] = PhaseSlipAnalyzer.compute_sector_psd(
                    {s: np.array(r_series)}, dt=DT
                )

    output["analysis"] = {
        "metastability_class": metastability,
        "survival_function": {
            "bin_width": 10_000,
            "bin_centers": surv_bins.tolist(),
            "survival_probs": surv_vals.tolist(),
        },
        "global_slip_rate": global_slip_rate,
        "total_slips_domain_a": total_slips_a,
        "total_slips_domain_b": total_slips_b,
        "sector_psd": sector_psd,
        "slip_events": {
            "domain_a": slip_events_a,
            "domain_b": slip_events_b,
        },
    }

    # --- Save output ---
    out_path = Path(output_dir) / "protocol_a_lifetime_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert any float32/64 to Python native for JSON serialization
    def _convert(obj):
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (list, tuple)):
            return [_convert(i) for i in obj]
        return obj

    out_data = _convert(output)
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2)

    # --- Results summary ---
    print(f"\n{'=' * 70}")
    print(f"PROTOCOL A RESULTS")
    print(f"{'=' * 70}")
    print(f"Metastability classification: {metastability}")
    print(f"Global slip rate: {global_slip_rate:.6e} per sector per timestep")
    print(f"Total slips (domain A): {total_slips_a}")
    print(f"Total slips (domain B): {total_slips_b}")

    survived_count = sum(1 for r in output["runs"] if r["chimera_survived"])
    print(f"Chimera survived: {survived_count}/{len(seeds)} runs")

    for run in output["runs"]:
        print(f"  Seed {run['seed']}: "
              f"survived={run['chimera_survived']}, "
              f"collapse_t={run['collapse_time']}, "
              f"slips={run['total_slips']}")

    print(f"\nSurvival function S(T):")
    for bin_c, s_val in zip(surv_bins[:6], surv_vals[:6]):
        print(f"  S({int(bin_c):>8}) = {s_val:.3f}")

    print(f"\nResults saved to: {out_path}")
    print(f"{'=' * 70}\n")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Protocol A: Long-Time Chimera Lifetime")
    parser.add_argument("--output", default="labs/simulations/results",
                        help="Output directory")
    parser.add_argument("--seeds", nargs="+", type=int, default=None,
                        help="Override chimera seeds (default: 42, 43, 44)")
    parser.add_argument("--fast", action="store_true",
                        help="Use T_total=50000 for prototyping")
    args = parser.parse_args()

    t_total_override = 50_000 if args.fast else T_TOTAL
    run_protocol_a(output_dir=args.output, seeds=args.seeds, t_total=t_total_override)
