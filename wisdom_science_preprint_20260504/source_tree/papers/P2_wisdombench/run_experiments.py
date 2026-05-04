# -*- coding: utf-8 -*-
"""
WisdomBench Live Evaluator — 多模型多策略全矩阵实验
======================================================
Usage:
    python run_experiments.py --seed 42
    python run_experiments.py --model deepseek --strategy immunity --rounds 5

Runs the full experiment matrix required for NeurIPS 2026 submission:
  3 models × 4 strategies × 20 tasks × 5 rounds × 3 seeds = 3,600 calls

Results saved to: results/<timestamp>_<model>_<strategy>_<seed>.json
"""

import os
import sys
import json
import time
import random
import argparse
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Import WisdomBench framework
sys.path.insert(0, os.path.dirname(__file__))
from wisdombench import (
    ALL_TASKS, WisdomTask, FailureCategory,
    NoMemoryStrategy, SelfRefineStrategy, ReflexionStrategy,
    CognitiveImmunityStrategy, LearningStrategy,
    TaskResult, RoundResult, BenchmarkResult,
    compute_wq, compute_rfr, compute_per_category_wq,
    generate_feedback,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("wisdombench_live")

# ═══════════════════════════════════════════════════════════════════════════
# MODEL CONFIGS — 三个模型 API
# ═══════════════════════════════════════════════════════════════════════════

MODEL_CONFIGS = {
    "claude-opus": {
        "api_key_env": "CLAUDE_KEY",
        "api_url": "https://lanyiapi.com/v1/chat/completions",
        "model_id": "claude-opus-4-7",
        "display_name": "Claude Opus",
    },
    "deepseek-chat": {
        "api_key_env": "DEEPSEEK_KEY",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "model_id": "deepseek-chat",
        "display_name": "DeepSeek-V3",
    },
    "qwen-plus": {
        "api_key_env": "QWEN_KEY",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model_id": "qwen-plus",
        "display_name": "Qwen-Plus",
    },
}


def load_api_keys():
    """从 .secrets.ps1 加载 API keys 到环境变量"""
    secrets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".secrets.ps1"
    )
    if not os.path.exists(secrets_path):
        # Fallback absolute path
        secrets_path = r"e:\order-architect-factory\.secrets.ps1"
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('$') or '=' not in line:
                    continue
                parts = line.split('=', 1)
                key = parts[0].strip().lstrip('$').strip()
                val = parts[1].strip().strip('"').strip("'")
                # Map PowerShell var names to env var names
                key_map = {
                    'KEY': 'CLAUDE_KEY',
                    'DEEPSEEK_KEY': 'DEEPSEEK_KEY',
                    'QWEN_KEY': 'QWEN_KEY',
                }
                env_name = key_map.get(key, key)
                os.environ[env_name] = val
        logger.info("Loaded API keys from .secrets.ps1")


# ═══════════════════════════════════════════════════════════════════════════
# LLM CALLER — 统一 OpenAI-compatible 调用
# ═══════════════════════════════════════════════════════════════════════════

def call_llm(model_config: dict, prompt: str, system: str = "",
             temperature: float = 0.0, max_tokens: int = 2000,
             max_retries: int = 3) -> str:
    """
    统一 LLM 调用 — OpenAI-compatible API。
    支持 Claude (via lanyiapi), DeepSeek, Qwen (dashscope)。
    """
    import urllib.request
    import urllib.error

    api_key = os.environ.get(model_config["api_key_env"], "")
    if not api_key:
        raise ValueError(f"API key not found: {model_config['api_key_env']}")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_config["model_id"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                model_config["api_url"],
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"].strip()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logger.warning(f"API call failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1) + random.random() * 2
                logger.info(f"Retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                raise


# ═══════════════════════════════════════════════════════════════════════════
# LLM-AS-JUDGE — 评分器
# ═══════════════════════════════════════════════════════════════════════════

JUDGE_SYSTEM = """You are a strict evaluator for WisdomBench, an AI benchmark.
You must score the response on a 0-3 scale according to the rubric provided.
Output ONLY a JSON object: {"score": <0-3>, "reason": "<one sentence>"}
No other text."""


def judge_response(model_config: dict, task: WisdomTask,
                   response: str) -> tuple:
    """
    LLM-as-judge scoring.
    Returns: (score: int, reason: str)
    """
    rubric_text = "\n".join(
        f"  {score}: {desc}" for score, desc in task.scoring_rubric.items()
    )

    prompt = f"""Task: {task.prompt}

Ground Truth: {task.ground_truth}

Scoring Rubric:
{rubric_text}

Agent Response:
{response}

Score this response according to the rubric. Output JSON only: {{"score": <0-3>, "reason": "..."}}"""

    try:
        raw = call_llm(model_config, prompt, system=JUDGE_SYSTEM,
                       temperature=0.0, max_tokens=200)
        # Parse score
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        score = int(data.get("score", 1))
        score = max(0, min(3, score))
        reason = data.get("reason", "")
        return score, reason
    except Exception as e:
        logger.warning(f"Judge parse error: {e}, raw={raw[:100] if 'raw' in dir() else '?'}")
        return 1, f"Parse error: {e}"


# ═══════════════════════════════════════════════════════════════════════════
# LIVE EVALUATOR
# ═══════════════════════════════════════════════════════════════════════════

def run_live_evaluation(
    model_name: str,
    strategy: LearningStrategy,
    judge_model: str = "deepseek-chat",
    rounds: int = 5,
    tasks: List[WisdomTask] = None,
    seed: int = 42,
    output_dir: str = "results",
) -> BenchmarkResult:
    """
    Run live WisdomBench evaluation with real API calls.

    Args:
        model_name: Key in MODEL_CONFIGS
        strategy: Learning strategy instance
        judge_model: Model used for judging (cheaper model preferred)
        rounds: Number of evaluation rounds
        tasks: Task list (default: ALL_TASKS)
        seed: Random seed for reproducibility
        output_dir: Where to save results
    """
    random.seed(seed)

    if tasks is None:
        tasks = ALL_TASKS

    model_config = MODEL_CONFIGS[model_name]
    judge_config = MODEL_CONFIGS[judge_model]

    logger.info(f"Starting: {model_config['display_name']} × {strategy.name} "
                f"× {len(tasks)} tasks × {rounds} rounds (seed={seed})")

    start_time = time.time()
    round_results: List[RoundResult] = []
    round_scores: Dict[str, List[int]] = {t.task_id: [] for t in tasks}
    task_categories = {t.task_id: t.category.value for t in tasks}
    all_responses: Dict[str, List[dict]] = {t.task_id: [] for t in tasks}

    for r in range(1, rounds + 1):
        logger.info(f"=== Round {r}/{rounds} ===")
        task_results = []

        for task in tasks:
            # T-Cell: modify prompt
            modified_prompt = strategy.pre_query(task)

            # Call target model
            try:
                response = call_llm(
                    model_config, modified_prompt,
                    temperature=0.0, max_tokens=1500,
                )
            except Exception as e:
                logger.error(f"Model call failed for {task.task_id}: {e}")
                response = f"[ERROR: {e}]"

            # Judge
            try:
                score, reason = judge_response(judge_config, task, response)
            except Exception as e:
                logger.error(f"Judge failed for {task.task_id}: {e}")
                score, reason = 1, f"Judge error: {e}"

            # Rate limit
            time.sleep(0.5)

            # Generate feedback
            feedback = generate_feedback(task, score, response) if r < rounds else ""

            result = TaskResult(
                task_id=task.task_id,
                round_num=r,
                score=score,
                response=response[:500],  # Truncate for storage
                feedback=feedback,
            )
            task_results.append(result)
            round_scores[task.task_id].append(score)

            # Store full response
            all_responses[task.task_id].append({
                "round": r, "score": score, "reason": reason,
                "response": response[:1000],
            })

            # B-Cell: learn from feedback
            if r < rounds:
                strategy.post_feedback(task, score, feedback)

            status = "✓" if score >= 2 else "✗"
            logger.info(f"  {status} {task.task_id} ({task.category.value}): "
                       f"score={score}/3 — {reason[:60]}")

        # Round aggregates
        mean_score = sum(tr.score for tr in task_results) / len(task_results)
        cat_scores = {}
        for cat in FailureCategory:
            cat_results = [tr for tr in task_results
                          if task_categories[tr.task_id] == cat.value]
            if cat_results:
                cat_scores[cat.value] = sum(tr.score for tr in cat_results) / len(cat_results)

        round_results.append(RoundResult(
            round_num=r,
            task_results=task_results,
            mean_score=mean_score,
            category_scores=cat_scores,
        ))

        logger.info(f"  Round {r} mean: {mean_score:.2f}/3")

    # Final metrics
    wq = compute_wq(round_scores)
    rfr = compute_rfr(round_scores)
    per_cat_wq = compute_per_category_wq(round_scores, task_categories)
    elapsed = time.time() - start_time

    result = BenchmarkResult(
        model_name=model_config['display_name'],
        strategy=strategy.name,
        rounds=round_results,
        wq=wq,
        gr=0.0,  # Will compute with variant tasks
        overfitting_ratio=1.0,
        per_category_wq=per_cat_wq,
        repeat_failure_rate=rfr,
        total_time_seconds=elapsed,
    )

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{model_name}_{strategy.name}_s{seed}.json"
    filepath = os.path.join(output_dir, filename)

    save_data = {
        "meta": {
            "model": model_name,
            "model_display": model_config['display_name'],
            "strategy": strategy.name,
            "rounds": rounds,
            "tasks": len(tasks),
            "seed": seed,
            "judge_model": judge_model,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
        },
        "metrics": {
            "wq": wq,
            "rfr": rfr,
            "per_category_wq": per_cat_wq,
        },
        "round_scores": {tid: scores for tid, scores in round_scores.items()},
        "responses": all_responses,
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Results saved to {filepath}")
    logger.info(f"WQ={wq:.3f}, RFR={rfr:.3f}, Time={elapsed:.0f}s")

    return result


# ═══════════════════════════════════════════════════════════════════════════
# FULL MATRIX RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_full_matrix(seeds: List[int] = None, rounds: int = 5,
                    output_dir: str = "results"):
    """
    Run full experiment matrix: 3 models × 4 strategies × 3 seeds.
    """
    if seeds is None:
        seeds = [42, 123, 456]

    models = ["claude-opus", "deepseek-chat", "qwen-plus"]
    strategy_factories = {
        "no_memory": NoMemoryStrategy,
        "self_refine": SelfRefineStrategy,
        "reflexion": ReflexionStrategy,
        "immunity": CognitiveImmunityStrategy,
    }

    total = len(models) * len(strategy_factories) * len(seeds)
    done = 0

    all_results = {}

    for model in models:
        for strat_name, strat_cls in strategy_factories.items():
            for seed in seeds:
                done += 1
                logger.info(f"\n{'#'*60}")
                logger.info(f"  [{done}/{total}] {model} × {strat_name} × seed={seed}")
                logger.info(f"{'#'*60}")

                try:
                    strategy = strat_cls()
                    result = run_live_evaluation(
                        model_name=model,
                        strategy=strategy,
                        judge_model="deepseek-chat",  # cheapest judge
                        rounds=rounds,
                        seed=seed,
                        output_dir=output_dir,
                    )
                    key = f"{model}_{strat_name}_s{seed}"
                    all_results[key] = {
                        "wq": result.wq,
                        "rfr": result.repeat_failure_rate,
                        "per_cat_wq": result.per_category_wq,
                    }
                except Exception as e:
                    logger.error(f"FAILED: {model} × {strat_name} × s{seed}: {e}")

    # Save aggregated results
    agg_path = os.path.join(output_dir, "aggregated_results.json")
    with open(agg_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logger.info(f"\nAggregated results saved to {agg_path}")

    return all_results


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WisdomBench Live Evaluator")
    parser.add_argument("--model", default="all",
                        choices=list(MODEL_CONFIGS.keys()) + ["all"],
                        help="Model to evaluate")
    parser.add_argument("--strategy", default="all",
                        choices=["no_memory", "self_refine", "reflexion",
                                 "immunity", "all"],
                        help="Learning strategy")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seeds", type=str, default="42,123,456",
                        help="Comma-separated seeds for full matrix")
    parser.add_argument("--judge", default="deepseek-chat",
                        choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--full-matrix", action="store_true",
                        help="Run complete 3×4×3 experiment matrix")
    args = parser.parse_args()

    # Load keys
    load_api_keys()

    if args.full_matrix:
        seeds = [int(s) for s in args.seeds.split(",")]
        run_full_matrix(seeds=seeds, rounds=args.rounds,
                        output_dir=args.output_dir)
    elif args.model != "all" and args.strategy != "all":
        # Single run
        strategies = {
            "no_memory": NoMemoryStrategy(),
            "self_refine": SelfRefineStrategy(),
            "reflexion": ReflexionStrategy(),
            "immunity": CognitiveImmunityStrategy(),
        }
        run_live_evaluation(
            model_name=args.model,
            strategy=strategies[args.strategy],
            judge_model=args.judge,
            rounds=args.rounds,
            seed=args.seed,
            output_dir=args.output_dir,
        )
    else:
        # Default: run full matrix
        seeds = [int(s) for s in args.seeds.split(",")]
        run_full_matrix(seeds=seeds, rounds=args.rounds,
                        output_dir=args.output_dir)
