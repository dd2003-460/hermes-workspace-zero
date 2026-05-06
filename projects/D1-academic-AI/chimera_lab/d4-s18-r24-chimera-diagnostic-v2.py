#!/usr/bin/env python3
"""D4-S18-r24: Chimera 诊断实验"""
import numpy as np
import json
from pathlib import Path

def compute_sync_profile(theta, N=256, n_seg=4):
    x = np.arange(N, dtype=np.float64) * 6.28318530718 / N
    segs = np.linspace(0.0, 6.28318530718, n_seg + 1)
    profile = np.zeros(n_seg)
    for s in range(n_seg):
        mask = (x >= segs[s]) & (x < segs[s + 1])
        seg = theta[mask]
        if len(seg) > 0:
            profile[s] = np.abs(np.mean(np.exp(1j * seg)))
    return profile

def run_chimera(N, K, sigma_frac, omega_mag, warmup, measure, dt):
    rng = np.random.RandomState(42)
    theta = rng.uniform(0.0, 6.28318530718, N).astype(np.float64)
    sigma = sigma_frac * 6.28318530718
    omega = omega_mag * np.sin(np.arange(N).astype(np.float64) * 2 * 3.14159265359 / N)
    sync = np.zeros(4)
    steps_done = 0
    for t in range(warmup + measure):
        dphi = theta.reshape(-1, 1) - theta.reshape(1, -1)
        dphi = (dphi + np.pi) % (2 * np.pi) - np.pi
        x = np.arange(N, dtype=np.float64)
        dx = np.abs(x[:, None] - x[None, :])
        dist = np.minimum(dx, N - dx) * 6.28318530718 / N
        k_local = np.exp(-dist ** 2 / (2 * sigma ** 2))
        local = np.sum(k_local * np.sin(dphi), axis=1)
        theta += dt * (omega + K * local / N)
        if t >= warmup:
            steps_done += 1
            profile = compute_sync_profile(theta, N)
            sync += profile
    return sync / max(1, steps_done)

def run_global(N, K, omega_mag, g, warmup, measure, dt):
    rng = np.random.RandomState(42)
    theta = rng.uniform(0.0, 6.28318530718, N).astype(np.float64)
    omega = omega_mag * np.sin(np.arange(N).astype(np.float64) * 2 * 3.14159265359 / N)
    c = np.ones(N)
    if g > 0:
        c = 1.0 + g * np.cos(np.arange(N).astype(np.float64) * 2 * 3.14159265359 / N)
    sync = np.zeros(4)
    steps_done = 0
    for t in range(warmup + measure):
        r = np.mean(np.exp(1j * theta))
        theta += dt * (omega + K * c * r.imag)
        if t >= warmup:
            steps_done += 1
            profile = compute_sync_profile(theta, N)
            sync += profile
    return sync / max(1, steps_done)

def classify(sp):
    ci = np.std(sp) / (np.mean(sp) + 1e-10)
    if np.mean(sp) > 0.95:
        return "global_sync", ci
    elif ci < 0.15:
        return "gradient_locking", ci
    elif ci > 0.3:
        return "chimera_mixed", ci
    else:
        return "mixed", ci

def main():
    N = 256
    results = {}
    modes = [
        ("true_chimera",   "chimera",   1.5, 0.3, 0.0, "非局部高斯耦合 (Abrams-Strogatz)"),
        ("freq_gradient",  "global",    1.0, 0.0, 0.5, "频率梯度锁相"),
        ("global_uniform", "global",    1.0, 0.0, 0.0, "纯均匀耦合"),
        ("mixed_chimera",  "chimera",   1.5, 0.3, 0.3, "混合 chimera + 频率梯度"),
    ]
    for name, mode, K, sigma_f, omega_m, desc in modes:
        tw = 3000 if mode == "chimera" else 20000
        tm = 15000 if mode == "chimera" else 30000
        if mode == "chimera":
            sp = run_chimera(N, K, sigma_f, omega_m, tw, tm, 0.01)
        else:
            sp = run_global(N, K, omega_m, sigma_f, tw, tm, 0.01)
        phase, ci = classify(sp)
        tag = {"chimera_mixed": "CHIMERA", "global_sync": "GLOBAL",
               "gradient_locking": "GRADLOCK", "mixed": "MIXED"}.get(phase, phase)
        print(f"\n{name} ({desc}): {tag} | K={K} SCI={ci:.4f}")
        print(f"  同步率: {[round(s, 4) for s in sp]}")
        results[name] = {
            "phase": phase, "ci": round(float(ci), 6),
            "sync": [round(float(s), 4) for s in sp],
            "desc": desc,
        }
    summary = {}
    for r in results.values():
        k = r["phase"].split("_")[0]
        summary[k] = summary.get(k, 0) + 1
    results["_summary"] = summary
    out = Path(__file__).parent / "r24-diagnostic-results.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n汇总: {summary}")
    print(f"结果: {out}")

if __name__ == "__main__":
    main()
