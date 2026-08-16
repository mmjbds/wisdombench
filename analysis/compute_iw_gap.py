#!/usr/bin/env python3
"""
Intelligence-Wisdom Gap Analysis
=================================
Reproduces all statistical analyses from:
  "The Intelligence-Wisdom Gap: Why Smarter AI Agents Are Not Wiser Ones"
  (Anonymous submission, 2026)

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
    for model, prefix in [
        ("DeepSeek", "deepseek_seed"),
        ("Qwen", "qwen_seed"),
        ("Qwen-Max", "qwenmax_seed"),
    ]:
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
                configs.append({"model": model, "strategy": strat, "I": I, "W": W})
    return configs


def average_ranks(values):
    """Return one-based average ranks, including correct handling of ties."""
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(indexed):
        end = start + 1
        while end < len(indexed) and indexed[end][1] == indexed[start][1]:
            end += 1
        average_rank = ((start + 1) + end) / 2
        for position in range(start, end):
            ranks[indexed[position][0]] = average_rank
        start = end
    return ranks


def pearson_correlation(x, y):
    """Compute Pearson correlation for equal-length numeric sequences."""
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    x_ss = sum((a - x_mean) ** 2 for a in x)
    y_ss = sum((b - y_mean) ** 2 for b in y)
    return numerator / math.sqrt(x_ss * y_ss)


def _beta_continued_fraction(a, b, x):
    """Continued fraction for the regularized incomplete beta function."""
    max_iterations = 200
    epsilon = 3e-14
    floor = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < floor:
        d = floor
    d = 1.0 / d
    result = d
    for iteration in range(1, max_iterations + 1):
        even = 2 * iteration
        coefficient = iteration * (b - iteration) * x / ((qam + even) * (a + even))
        d = 1.0 + coefficient * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + coefficient / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        result *= d * c
        coefficient = -(a + iteration) * (qab + iteration) * x / ((a + even) * (qap + even))
        d = 1.0 + coefficient * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + coefficient / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        delta = d * c
        result *= delta
        if abs(delta - 1.0) < epsilon:
            return result
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def regularized_incomplete_beta(a, b, x):
    """Regularized incomplete beta I_x(a, b), using a stable continued fraction."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b


def spearman_rank(x, y):
    """Compute tie-corrected Spearman rho and the standard asymptotic p-value."""
    n = len(x)
    if n != len(y) or n < 3:
        raise ValueError("Spearman correlation requires equal-length inputs with n >= 3")
    rho = pearson_correlation(average_ranks(x), average_ranks(y))
    if abs(rho) >= 1:
        p_value = 0.0
    else:
        degrees_of_freedom = n - 2
        t_squared = rho * rho * degrees_of_freedom / (1 - rho * rho)
        p_value = regularized_incomplete_beta(
            degrees_of_freedom / 2,
            0.5,
            degrees_of_freedom / (degrees_of_freedom + t_squared),
        )
    return rho, p_value, n


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
    print(f"TABLE 1: Intelligence (I) vs Wisdom (W) — {len(configs)} Configurations")
    print(f"{'='*70}")
    print(f"{'Model':<20} {'Strategy':<20} {'I (R1)':>8} {'W (WQ)':>8}")
    print("-" * 60)
    for c in configs:
        print(f"{c['model']:<20} {c['strategy']:<20} {c['I']:>8.3f} {c['W']:>+8.3f}")

    # === Spearman Correlation ===
    Is = [c["I"] for c in configs]
    Ws = [c["W"] for c in configs]
    rho, p_value, n = spearman_rank(Is, Ws)
    print(f"\nSpearman rho(I, W) = {rho:.4f}, p = {p_value:.4f} (n={n})")

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
