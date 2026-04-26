#!/usr/bin/env python3
"""
WisdomBench Metrics Calculator
==============================
Computes Wisdom Quotient (WQ) and Repeat Failure Rate (RFR) from raw score data.

Usage:
    python compute_metrics.py --data results/deepseek_seed42.json
    python compute_metrics.py --data results/ --all    # Process all files in directory
"""

import json, argparse, math
from pathlib import Path


def compute_wq(scores: list, score_max: int = 3) -> float:
    """Compute per-task Wisdom Quotient: (R5 - R1) / (score_max - R1).
    Returns 0 for ceiling tasks where R1 == score_max."""
    if scores[0] >= score_max:
        return 0.0  # Ceiling task — no headroom
    return (scores[-1] - scores[0]) / (score_max - scores[0])


def compute_rfr(scores: list, threshold: int = 2) -> tuple:
    """Compute Repeat Failure Rate contribution.
    Returns (repeat_failures, total_failure_opportunities)."""
    repeats = 0
    opportunities = 0
    for r in range(1, len(scores)):
        if scores[r - 1] < threshold:
            opportunities += 1
            if scores[r] < threshold:
                repeats += 1
    return repeats, opportunities


def analyze_file(filepath: str) -> dict:
    """Analyze a single raw results JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    results = {}
    for strategy, tasks in data.items():
        wq_values = []
        rfr_num, rfr_den = 0, 0
        r1_scores, r5_scores = [], []

        for task_id, scores in tasks.items():
            wq = compute_wq(scores)
            wq_values.append(wq)
            rn, rd = compute_rfr(scores)
            rfr_num += rn
            rfr_den += rd
            r1_scores.append(scores[0])
            r5_scores.append(scores[-1])

        results[strategy] = {
            "WQ": round(sum(wq_values) / len(wq_values), 4),
            "RFR": round(rfr_num / rfr_den, 4) if rfr_den > 0 else 0.0,
            "R1_mean": round(sum(r1_scores) / len(r1_scores), 3),
            "R5_mean": round(sum(r5_scores) / len(r5_scores), 3),
            "n_tasks": len(wq_values),
        }

    return results


def main():
    parser = argparse.ArgumentParser(description="WisdomBench Metrics Calculator")
    parser.add_argument("--data", required=True, help="Path to JSON results file or directory")
    parser.add_argument("--all", action="store_true", help="Process all JSON files in directory")
    args = parser.parse_args()

    path = Path(args.data)
    files = list(path.glob("*.json")) if path.is_dir() and args.all else [path]

    for f in files:
        print(f"\n{'='*60}")
        print(f"File: {f.name}")
        print(f"{'='*60}")
        results = analyze_file(str(f))
        for strat, metrics in results.items():
            print(f"\n  {strat}:")
            for k, v in metrics.items():
                print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
