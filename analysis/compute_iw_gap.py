#!/usr/bin/env python3
"""
Intelligence-Wisdom Gap Analysis
=================================
Reproduces all statistical analyses from:
  "The Intelligence-Wisdom Gap: Why Smarter AI Agents Are Not Wiser Ones"
  (Zhang, 2026)

Usage:
    python compute_iw_gap.py --demo           # Run with bundled data
    python compute_iw_gap.py --data ../results # Point to custom data directory
"""

import json, argparse, math, os
from pathlib import Path

SEEDS = [42, 137, 256]
STRATEGIES = ["No Memory", "Self-Refine", "Reflexion", "Cog. Immunity"]
TASKS = [f"{c}{i}" for c in ["H", "S", "R"] for i in range(1, 6)] + [f"SA{i}" for i in range(1, 6)]
CATEGORIES = {
    "Hallucination": [f"H{i}" for i in range(1, 6)],
    "Sycophancy": [f"S{i}" for i in range(1, 6)],
    "Reasoning": [f"R{i}" for i in range(1, 6)],
    "Safety": [f"SA{i}" for i in range(1, 6)],
}


def load_data(data_dir: str) -> dict:
    """Load all raw score files from data directory."""
    data = {}
    for model, prefix in [("DeepSeek", "deepseek_seed"), ("Qwen", "qwen_seed")]:
        data[model] = {}
        for seed in SEEDS:
            filepath = Path(data_dir) / f"{prefix}{seed}.json"
            if filepath.exists():
                with open(filepath) as f:
                    data[model][seed] = json.load(f)
    return data


def compute_config_metrics(model_data: dict) -> list:
    """Compute I and W for each (model × strategy) configuration."""
    configs = []
    for model, seeds_data in model_data.items():
        for strat in STRATEGIES:
            r1_all, wq_all = [], []
            for seed in SEEDS:
                if seed not in seeds_data:
                    continue
                total_wq = 0
                for task in TASKS:
                    scores = seeds_data[seed][strat][task]
                    r1_all.append(scores[0])
                    if scores[0] < 3:
                        total_wq += (scores[4] - scores[0]) / (3 - scores[0])
                wq_all.append(total_wq / len(TASKS))

            if r1_all:
                I = sum(r1_all) / len(r1_all)
                W = sum(wq_all) / len(wq_all)
                configs.append({"model": model, "strategy": strat, "I": round(I, 3), "W": round(W, 3)})
    return configs


def spearman_rank(x, y):
    """Compute Spearman rank correlation (no scipy dependency)."""
    n = len(x)
    rank_x = [sorted(x).index(v) + 1 for v in x]
    rank_y = [sorted(y).index(v) + 1 for v in y]
    d_sq = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
    rho = 1 - (6 * d_sq) / (n * (n ** 2 - 1))
    # Approximate p-value using t-distribution
    if abs(rho) < 1:
        t = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    else:
        t = float("inf")
    return rho, t, n


def per_category_analysis(model_data: dict, model: str, strategy: str) -> dict:
    """Per-category R1 and R5 means for a given model × strategy."""
    result = {}
    for cat, task_ids in CATEGORIES.items():
        r1s, r5s = [], []
        for seed in SEEDS:
            if seed not in model_data.get(model, {}):
                continue
            for tid in task_ids:
                scores = model_data[model][seed][strategy][tid]
                r1s.append(scores[0])
                r5s.append(scores[4])
        if r1s:
            r1m = sum(r1s) / len(r1s)
            r5m = sum(r5s) / len(r5s)
            result[cat] = {"R1": round(r1m, 2), "R5": round(r5m, 2), "Delta": round(r5m - r1m, 2)}
    return result


def main():
    parser = argparse.ArgumentParser(description="I-W Gap Analysis")
    parser.add_argument("--data", default="../results", help="Path to results directory")
    parser.add_argument("--demo", action="store_true", help="Run with bundled data")
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent / "results" if args.demo else Path(args.data)
    print(f"Loading data from: {data_dir}")

    model_data = load_data(str(data_dir))

    # === Table 1: I-W Matrix ===
    configs = compute_config_metrics(model_data)
    print(f"\n{'='*70}")
    print("TABLE 1: Intelligence (I) vs Wisdom (W) — 8 Configurations")
    print(f"{'='*70}")
    print(f"{'Model':<20} {'Strategy':<20} {'I (R1)':>8} {'W (WQ)':>8}")
    print("-" * 60)
    for c in configs:
        print(f"{c['model']:<20} {c['strategy']:<20} {c['I']:>8.3f} {c['W']:>+8.3f}")

    # === Spearman Correlation ===
    Is = [c["I"] for c in configs]
    Ws = [c["W"] for c in configs]
    rho, t, n = spearman_rank(Is, Ws)
    print(f"\nSpearman rho(I, W) = {rho:.4f} (n={n})")

    # === Per-Category Analysis ===
    print(f"\n{'='*70}")
    print("PER-CATEGORY ANALYSIS (DeepSeek-v4-flash)")
    print(f"{'='*70}")
    for strat in ["No Memory", "Cog. Immunity"]:
        print(f"\n  --- {strat} ---")
        cats = per_category_analysis(model_data, "DeepSeek", strat)
        for cat, vals in cats.items():
            print(f"    {cat:<15}: R1={vals['R1']:.2f}  R5={vals['R5']:.2f}  Delta={vals['Delta']:+.2f}")

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
