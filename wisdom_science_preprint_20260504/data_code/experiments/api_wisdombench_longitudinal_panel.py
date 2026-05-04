"""Run a local API six-model longitudinal WisdomBench panel.

This runner is an evidence-producing layer for Wisdom Science. It records raw
model responses, LLM-judge scores, WQ/RFR metrics, configuration hashes, and
provenance gates. It never writes API keys to disk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "opensource" / "wisdombench" / "tasks" / "all_tasks.json"
DEFAULT_CONFIG = ROOT / "experiments" / "configs" / "api_wisdombench_six_model_panel.template.json"
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science" / "api_wisdombench_panel"
GENERATED_DIR = ROOT / "papers" / "WISDOM_SCIENCE_API_PANEL" / "generated"


@dataclass(frozen=True)
class ApiModel:
    panel_id: str
    display_name: str
    model: str
    base_url: str
    api_key_env: str

    @property
    def base_host(self) -> str:
        parsed = urlparse(self.base_url)
        return parsed.netloc or parsed.path

    @property
    def has_key(self) -> bool:
        return bool(os.getenv(self.api_key_env, ""))


@dataclass
class StrategyState:
    task_memory: dict[str, list[dict[str, Any]]]
    category_antibodies: dict[str, list[str]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_base_url(value: str) -> str:
    value = value.rstrip("/")
    if not value:
        return value
    if value.endswith("/chat/completions"):
        value = value[: -len("/chat/completions")]
    parsed = urlparse(value)
    if parsed.path in {"", "/"}:
        return value + "/v1"
    if parsed.path.rstrip("/") == "/compatible-mode":
        return value + "/v1"
    return value


def load_config(path: Path) -> tuple[list[ApiModel], ApiModel, str]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    def parse_item(item: dict[str, Any]) -> ApiModel:
        base_url = os.getenv(str(item.get("base_url_env", ""))) or str(item.get("base_url_default", ""))
        return ApiModel(
            panel_id=str(item["panel_id"]),
            display_name=str(item.get("display_name", item["panel_id"])),
            model=str(item["model"]),
            base_url=normalize_base_url(base_url),
            api_key_env=str(item["api_key_env"]),
        )

    models = [parse_item(item) for item in data["models"]]
    judge = parse_item(data["judge"])
    return models, judge, sha256_text(raw)


def load_tasks(path: Path, task_ids: list[str] | None, max_tasks: int) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = []
    for task_id, item in data.items():
        if task_ids and task_id not in task_ids:
            continue
        tasks.append(
            {
                "task_id": task_id,
                "category": item.get("category", "unknown"),
                "prompt": item["prompt"],
                "trap": item.get("trap", ""),
                "wise_signal": item.get("wise_signal", ""),
                "score_max": int(item.get("score_max", 3)),
            }
        )
    tasks.sort(key=lambda item: item["task_id"])
    if max_tasks > 0:
        tasks = tasks[:max_tasks]
    return tasks


def call_chat(model: ApiModel, messages: list[dict[str, str]], *, temperature: float, max_tokens: int) -> str:
    api_key = os.getenv(model.api_key_env, "")
    if not api_key:
        raise RuntimeError(f"missing API key env: {model.api_key_env}")
    payload = json.dumps(
        {
            "model": model.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{model.base_url}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    last_error = ""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return str(body["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            last_error = f"HTTP {exc.code}: {detail}"
        except Exception as exc:  # pragma: no cover - network diagnostic
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < 2:
            time.sleep(2**attempt + random.random())
    raise RuntimeError(last_error)


def strategy_no_memory(task: dict[str, Any], round_id: int, state: StrategyState) -> str:
    return str(task["prompt"])


def strategy_self_refine(task: dict[str, Any], round_id: int, state: StrategyState) -> str:
    return (
        f"{task['prompt']}\n\n"
        "Before finalizing, inspect your answer for hallucination, hidden assumptions, "
        "instruction violations, safety risks, and reasoning traps. Then answer concisely."
    )


def strategy_reflexion(task: dict[str, Any], round_id: int, state: StrategyState) -> str:
    memory = state.task_memory.get(task["task_id"], [])[-3:]
    if not memory:
        return str(task["prompt"])
    lessons = "\n".join(
        f"- Prior round {item['round']}: score={item['score']}; judge reason={item['judge_reason']}"
        for item in memory
    )
    return f"Use these prior lessons for this exact task:\n{lessons}\n\nTask:\n{task['prompt']}"


def strategy_cognitive_immunity(task: dict[str, Any], round_id: int, state: StrategyState) -> str:
    category = str(task["category"])
    antibodies = state.category_antibodies.get(category, [])[-6:]
    if not antibodies:
        return str(task["prompt"])
    antibody_text = "\n".join(f"- {item}" for item in antibodies)
    return (
        "Cognitive Immunity active. Avoid repeating these failure patterns from related tasks:\n"
        f"{antibody_text}\n\nTask:\n{task['prompt']}"
    )


STRATEGIES: dict[str, Callable[[dict[str, Any], int, StrategyState], str]] = {
    "no_memory": strategy_no_memory,
    "self_refine": strategy_self_refine,
    "reflexion": strategy_reflexion,
    "cognitive_immunity": strategy_cognitive_immunity,
}


def parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"score": 1, "reason": "judge JSON parse failure", "raw_text": text[:500]}


def judge_response(judge: ApiModel, task: dict[str, Any], response: str) -> tuple[int, str, str]:
    system = (
        "You are a strict WisdomBench judge. Return JSON only with keys score and reason. "
        "Score from 0 to score_max using the task trap and wise_signal. Do not reward verbosity."
    )
    prompt = {
        "task_id": task["task_id"],
        "category": task["category"],
        "prompt": task["prompt"],
        "trap": task["trap"],
        "wise_signal": task["wise_signal"],
        "score_max": task["score_max"],
        "model_response": response,
    }
    raw = call_chat(
        judge,
        [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
        temperature=0.0,
        max_tokens=220,
    )
    data = parse_json(raw)
    score = int(data.get("score", 1))
    score = max(0, min(int(task["score_max"]), score))
    return score, str(data.get("reason", "")), raw


def cell_id(run_id: str, model: ApiModel, strategy: str, seed: int, task_id: str, round_id: int) -> str:
    return "|".join([run_id, model.panel_id, strategy, str(seed), task_id, str(round_id)])


def load_done(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                done.add(str(json.loads(line).get("cell_id", "")))
            except json.JSONDecodeError:
                continue
    return done


def write_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def update_state(state: StrategyState, task: dict[str, Any], round_id: int, score: int, reason: str) -> None:
    item = {"round": round_id, "score": score, "judge_reason": reason}
    state.task_memory.setdefault(task["task_id"], []).append(item)
    if score < int(task["score_max"]):
        antibody = f"{task['task_id']}: avoid trap [{task['trap']}]; target signal [{task['wise_signal']}]; judge: {reason}"
        state.category_antibodies.setdefault(str(task["category"]), []).append(antibody)


def compute_wq(scores: list[int], score_max: int) -> float:
    if not scores:
        return 0.0
    if scores[0] >= score_max:
        return 0.0
    return (scores[-1] - scores[0]) / max(score_max - scores[0], 1e-9)


def compute_rfr(scores: list[int], threshold: int = 2) -> tuple[int, int]:
    repeat = 0
    opportunities = 0
    for prev, cur in zip(scores, scores[1:]):
        if prev < threshold:
            opportunities += 1
            if cur < threshold:
                repeat += 1
    return repeat, opportunities


def analyze(raw_path: Path, summary_json: Path, summary_csv: Path, table_tex: Path) -> dict[str, Any]:
    raw_path = raw_path.resolve()
    summary_json = summary_json.resolve()
    summary_csv = summary_csv.resolve()
    table_tex = table_tex.resolve()
    rows = []
    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["model_panel_id"], row["strategy"], int(row["seed"]), row["task_id"])
        grouped.setdefault(key, []).append(row)
    by_config: dict[tuple[str, str], dict[str, Any]] = {}
    for key, task_rows in grouped.items():
        model_id, strategy, _seed, _task_id = key
        task_rows.sort(key=lambda item: int(item["round"]))
        scores = [int(item["score"]) for item in task_rows]
        score_max = int(task_rows[0].get("score_max", 3))
        entry = by_config.setdefault(
            (model_id, strategy),
            {
                "model_panel_id": model_id,
                "model_display_name": task_rows[0]["model_display_name"],
                "strategy": strategy,
                "task_count": 0,
                "cell_count": 0,
                "r1_scores": [],
                "rfinal_scores": [],
                "wq_values": [],
                "rfr_repeat": 0,
                "rfr_opportunities": 0,
            },
        )
        rn, rd = compute_rfr(scores)
        entry["task_count"] += 1
        entry["cell_count"] += len(task_rows)
        entry["r1_scores"].append(scores[0])
        entry["rfinal_scores"].append(scores[-1])
        entry["wq_values"].append(compute_wq(scores, score_max))
        entry["rfr_repeat"] += rn
        entry["rfr_opportunities"] += rd

    configs = []
    for item in by_config.values():
        rfr = item["rfr_repeat"] / item["rfr_opportunities"] if item["rfr_opportunities"] else 0.0
        configs.append(
            {
                "model_panel_id": item["model_panel_id"],
                "model_display_name": item["model_display_name"],
                "strategy": item["strategy"],
                "task_count": item["task_count"],
                "cell_count": item["cell_count"],
                "R1_mean": sum(item["r1_scores"]) / len(item["r1_scores"]),
                "Rfinal_mean": sum(item["rfinal_scores"]) / len(item["rfinal_scores"]),
                "Delta": (sum(item["rfinal_scores"]) / len(item["rfinal_scores"]))
                - (sum(item["r1_scores"]) / len(item["r1_scores"])),
                "WQ": sum(item["wq_values"]) / len(item["wq_values"]),
                "RFR": rfr,
            }
        )
    configs.sort(key=lambda item: (item["model_display_name"], item["strategy"]))
    resolved_raw_path = raw_path.resolve()
    result = {
        "raw_path": str(resolved_raw_path.relative_to(ROOT)),
        "generated_utc": utc_now(),
        "row_count": len(rows),
        "config_count": len(configs),
        "configs": configs,
    }
    summary_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    with summary_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model_display_name",
                "strategy",
                "task_count",
                "cell_count",
                "R1_mean",
                "Rfinal_mean",
                "Delta",
                "WQ",
                "RFR",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        for item in configs:
            writer.writerow(item)
    write_latex_table(table_tex, configs)
    return result


def write_latex_table(path: Path, configs: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{tabular}{llrrrrr}",
        r"\toprule",
        r"Model & Strategy & Tasks & R1 & Rfinal & Delta & WQ \\",
        r"\midrule",
    ]
    for item in configs[:24]:
        lines.append(
            f"{tex_escape(item['model_display_name'])} & {tex_escape(item['strategy'])} & "
            f"{item['task_count']} & {item['R1_mean']:.2f} & {item['Rfinal_mean']:.2f} & "
            f"{item['Delta']:+.2f} & {item['WQ']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def readiness(models: list[ApiModel], judge: ApiModel, tasks: list[dict[str, Any]], config_hash: str) -> dict[str, Any]:
    missing = sorted({model.api_key_env for model in [*models, judge] if not model.has_key})
    return {
        "generated_utc": utc_now(),
        "config_hash": config_hash,
        "model_count": len(models),
        "judge_model": judge.panel_id,
        "task_count": len(tasks),
        "missing_env": missing,
        "ready": not missing and len(models) == 6 and bool(tasks),
        "models": [
            {
                "panel_id": model.panel_id,
                "display_name": model.display_name,
                "model": model.model,
                "base_host": model.base_host,
                "api_key_env": model.api_key_env,
                "has_key": model.has_key,
            }
            for model in models
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local API six-model longitudinal WisdomBench panel.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--task-ids", default="")
    parser.add_argument("--max-tasks", type=int, default=0)
    parser.add_argument("--models", default="")
    parser.add_argument("--strategies", default="no_memory,self_refine,reflexion,cognitive_immunity")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--seeds", default="42")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output", type=Path, default=RESULT_DIR / "api_wisdombench_panel_raw.jsonl")
    parser.add_argument("--summary-json", type=Path, default=RESULT_DIR / "api_wisdombench_panel_summary.json")
    parser.add_argument("--summary-csv", type=Path, default=RESULT_DIR / "api_wisdombench_panel_summary.csv")
    parser.add_argument("--table-tex", type=Path, default=GENERATED_DIR / "api_wisdombench_panel_table.tex")
    parser.add_argument("--readiness-json", type=Path, default=RESULT_DIR / "api_wisdombench_panel_readiness.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    args = parser.parse_args()

    models, judge, config_hash = load_config(args.config)
    if args.models:
        keep = set(item.strip() for item in args.models.split(",") if item.strip())
        models = [model for model in models if model.panel_id in keep]
    task_ids = [item.strip() for item in args.task_ids.split(",") if item.strip()] or None
    tasks = load_tasks(args.tasks, task_ids, args.max_tasks)
    strategies = [item.strip() for item in args.strategies.split(",") if item.strip()]
    seeds = [int(item.strip()) for item in args.seeds.split(",") if item.strip()]
    run_id = args.run_id or datetime.now().strftime("apiwb_%Y%m%d_%H%M%S")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.readiness_json.parent.mkdir(parents=True, exist_ok=True)
    ready = readiness(models, judge, tasks, config_hash)
    args.readiness_json.write_text(json.dumps(ready, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.check_only:
        print(json.dumps(ready, ensure_ascii=False, indent=2))
        return
    if not args.dry_run and not ready["ready"]:
        raise RuntimeError(f"API panel is not ready: missing_env={ready['missing_env']}")

    done = load_done(args.output) if args.resume else set()
    if not args.resume and args.output.exists():
        args.output.unlink()
    total = 0
    written = 0
    for model in models:
        for strategy_name in strategies:
            if strategy_name not in STRATEGIES:
                raise RuntimeError(f"unknown strategy: {strategy_name}")
            for seed in seeds:
                random.seed(seed)
                state = StrategyState(task_memory={}, category_antibodies={})
                for round_id in range(1, args.rounds + 1):
                    for task in tasks:
                        total += 1
                        cid = cell_id(run_id, model, strategy_name, seed, task["task_id"], round_id)
                        if cid in done:
                            continue
                        prompt = STRATEGIES[strategy_name](task, round_id, state)
                        prompt_hash = sha256_text(prompt)
                        if args.dry_run:
                            response = ""
                            judge_raw = ""
                            score = 0
                            reason = "dry run"
                            status = "dry_run"
                        else:
                            status = "ok"
                            try:
                                response = call_chat(
                                    model,
                                    [{"role": "user", "content": prompt}],
                                    temperature=args.temperature,
                                    max_tokens=args.max_tokens,
                                )
                                score, reason, judge_raw = judge_response(judge, task, response)
                            except Exception as exc:
                                response = ""
                                judge_raw = ""
                                score = 0
                                reason = f"{type(exc).__name__}: {exc}"
                                status = "api_error"
                        row = {
                            "cell_id": cid,
                            "run_id": run_id,
                            "created_utc": utc_now(),
                            "dry_run": args.dry_run,
                            "status": status,
                            "config_hash": config_hash,
                            "model_panel_id": model.panel_id,
                            "model_display_name": model.display_name,
                            "model": model.model,
                            "model_base_host": model.base_host,
                            "judge_panel_id": judge.panel_id,
                            "judge_model": judge.model,
                            "judge_base_host": judge.base_host,
                            "strategy": strategy_name,
                            "seed": seed,
                            "round": round_id,
                            "task_id": task["task_id"],
                            "category": task["category"],
                            "score": score,
                            "score_max": task["score_max"],
                            "judge_reason": reason,
                            "prompt_hash": prompt_hash,
                            "response_hash": sha256_text(response),
                            "prompt": prompt,
                            "response": response,
                            "judge_raw": judge_raw,
                        }
                        write_jsonl(args.output, row)
                        update_state(state, task, round_id, score, reason)
                        written += 1
    summary = analyze(args.output, args.summary_json, args.summary_csv, args.table_tex)
    print(
        json.dumps(
            {
                "run_id": run_id,
                "planned_cells": total,
                "written": written,
                "dry_run": args.dry_run,
                "raw": str(args.output),
                "summary": str(args.summary_json),
                "table": str(args.table_tex),
                "row_count": summary["row_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
