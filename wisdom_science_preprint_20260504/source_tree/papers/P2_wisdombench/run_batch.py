# -*- coding: utf-8 -*-
"""
Batch runner: execute all remaining experiment combinations.
Runs sequentially to avoid API rate limiting.
"""
import sys, os, time, json, logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_experiments import (
    load_api_keys, run_live_evaluation, MODEL_CONFIGS,
    NoMemoryStrategy, SelfRefineStrategy,
    ReflexionStrategy, CognitiveImmunityStrategy,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

def get_done_keys():
    """Scan results dir for already completed runs."""
    done = set()
    if os.path.exists(RESULTS_DIR):
        for f in os.listdir(RESULTS_DIR):
            if not f.endswith(".json") or f in ("aggregated_results.json", "summary.json"):
                continue
            path = os.path.join(RESULTS_DIR, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                meta = data.get("meta", {})
                model = meta.get("model", "")
                strategy = meta.get("strategy", "")
                seed = meta.get("seed", "")
                if model and strategy:
                    done.add(f"{model}_{strategy}_s{seed}")
            except Exception:
                pass
    return done

def main():
    load_api_keys()

    models = ["deepseek-chat", "qwen-plus", "claude-opus"]
    strategy_factories = [
        ("no_memory", NoMemoryStrategy),
        ("self_refine", SelfRefineStrategy),
        ("reflexion", ReflexionStrategy),
        ("cognitive_immunity", CognitiveImmunityStrategy),
    ]
    seed = 42
    rounds = 5

    done = get_done_keys()
    total_pairs = [(m, sn, sc) for m in models for sn, sc in strategy_factories]
    remaining = [(m, sn, sc) for m, sn, sc in total_pairs
                 if f"{m}_{sn}_s{seed}" not in done]

    logger.info(f"Total combinations: {len(total_pairs)}, Already done: {len(done)}, "
                f"Remaining: {len(remaining)}")

    for i, (model, strat_name, strat_cls) in enumerate(remaining, 1):
        logger.info(f"\n{'#'*60}")
        logger.info(f"  [{i}/{len(remaining)}] {model} x {strat_name} (seed={seed})")
        logger.info(f"{'#'*60}")

        try:
            strategy = strat_cls()
            result = run_live_evaluation(
                model_name=model,
                strategy=strategy,
                judge_model="deepseek-chat",
                rounds=rounds,
                seed=seed,
                output_dir=RESULTS_DIR,
            )
            logger.info(f"  DONE: WQ={result.wq:.3f}, RFR={result.repeat_failure_rate:.3f}")
        except Exception as e:
            logger.error(f"  FAILED: {e}")
            import traceback
            traceback.print_exc()

        # Cool-down between runs
        time.sleep(5)

    logger.info("\n" + "="*60)
    logger.info("ALL EXPERIMENTS COMPLETE")
    logger.info("="*60)

    # Aggregate
    aggregate_results()

def aggregate_results():
    """Compile all individual results into a summary table."""
    summary = {}
    for f in sorted(os.listdir(RESULTS_DIR)):
        if not f.endswith(".json") or f == "aggregated_results.json" or f == "summary.json":
            continue
        path = os.path.join(RESULTS_DIR, f)
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        meta = data.get("meta", {})
        metrics = data.get("metrics", {})
        key = f"{meta.get('model','?')}_{meta.get('strategy','?')}"
        summary[key] = {
            "model": meta.get("model_display", meta.get("model", "?")),
            "strategy": meta.get("strategy", "?"),
            "wq": metrics.get("wq", 0),
            "rfr": metrics.get("rfr", 0),
            "per_category_wq": metrics.get("per_category_wq", {}),
            "round_scores": data.get("round_scores", {}),
        }

    out = os.path.join(RESULTS_DIR, "summary.json")
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    logger.info(f"Summary saved to {out}")

    # Print table
    print(f"\n{'Model':<20} {'Strategy':<22} {'WQ':>8} {'RFR':>8}")
    print("-"*60)
    for k, v in sorted(summary.items()):
        print(f"{v['model']:<20} {v['strategy']:<22} {v['wq']:>8.3f} {v['rfr']:>8.3f}")

if __name__ == "__main__":
    main()
