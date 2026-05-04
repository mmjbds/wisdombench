# -*- coding: utf-8 -*-
"""Analyze completed experiment results."""
import json, os

RESULTS_DIR = r"e:\order-architect-factory\papers\P2_wisdombench\results"

for f in sorted(os.listdir(RESULTS_DIR)):
    if not f.endswith(".json") or f in ("aggregated_results.json", "summary.json", "batch_log.txt"):
        continue
    path = os.path.join(RESULTS_DIR, f)
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            d = json.load(fh)
        meta = d.get("meta")
        if not meta:
            continue
        print(f"=== {meta['model_display']} x {meta['strategy']} (seed={meta.get('seed',42)}) ===")
        metrics = d["metrics"]
        print(f"  WQ={metrics['wq']:.3f}  RFR={metrics['rfr']:.3f}")
        print(f"  Per-cat WQ: {metrics.get('per_category_wq', {})}")
        print(f"  Task trajectories:")
        for tid, scores in sorted(d["round_scores"].items()):
            marker = " ***" if 0 in scores else ""
            print(f"    {tid}: {' -> '.join(map(str,scores))}{marker}")
        # Round means
        n_tasks = len(d["round_scores"])
        for r in range(5):
            rnd_scores = [scores[r] for scores in d["round_scores"].values() if r < len(scores)]
            mean = sum(rnd_scores) / len(rnd_scores) if rnd_scores else 0
            print(f"    R{r+1} mean: {mean:.2f}")
        print()
    except Exception as e:
        print(f"Error reading {f}: {e}")
