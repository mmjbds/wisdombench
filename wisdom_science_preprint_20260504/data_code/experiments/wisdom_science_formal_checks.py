"""Formal sanity checks for Wisdom Science metrics and evidence gates.

The script is deliberately dependency-free. It does not prove the theory by
itself; it records executable counterexamples and invariants that the papers
must respect.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"
FORMAL_GEN = ROOT / "papers" / "WISDOM_SCIENCE_FORMAL_CORE" / "generated"


def wq(first: float, final: float, score_max: float = 1.0) -> float:
    if first >= score_max:
        return 0.0
    return (final - first) / (score_max - first)


def clipped_wq(first: float, final: float, score_max: float = 1.0) -> float:
    return max(-1.0, min(1.0, wq(first, final, score_max)))


def weighted_mean(values: list[float], weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        raise ValueError("weights must have positive total")
    return sum(value * weight for value, weight in zip(values, weights)) / total


def boundedness_check() -> dict[str, object]:
    samples = []
    for i in range(101):
        first = i / 100
        final = first + (1.0 - first) * 0.37
        value = wq(first, final)
        samples.append(value)
    return {
        "name": "non_regression_boundedness",
        "passed": all(0.0 <= value <= 1.0 for value in samples),
        "min": min(samples),
        "max": max(samples),
        "interpretation": "If final score is between first score and ceiling, WQ lies in [0, 1].",
    }


def separation_check() -> dict[str, object]:
    high_i_stagnant = {"I": 0.92, "WQ": wq(0.92, 0.92)}
    low_i_learning = {"I": 0.20, "WQ": wq(0.20, 0.76)}
    return {
        "name": "intelligence_wisdom_separation",
        "passed": high_i_stagnant["I"] > low_i_learning["I"]
        and high_i_stagnant["WQ"] < low_i_learning["WQ"],
        "high_i_stagnant": high_i_stagnant,
        "low_i_learning": low_i_learning,
        "interpretation": "First-round competence and after-experience improvement can rank systems differently.",
    }


def non_identifiability_check() -> dict[str, object]:
    learning_agent_scores = [0.20, 0.35, 0.50, 0.64, 0.76]
    scheduled_agent_scores = [0.20, 0.35, 0.50, 0.64, 0.76]
    return {
        "name": "positive_wq_non_identifiability",
        "passed": learning_agent_scores == scheduled_agent_scores
        and math.isclose(wq(learning_agent_scores[0], learning_agent_scores[-1]), 0.70),
        "learning_agent_scores": learning_agent_scores,
        "scheduled_agent_scores": scheduled_agent_scores,
        "observed_wq": wq(learning_agent_scores[0], learning_agent_scores[-1]),
        "interpretation": "The same score trace can come from learning or from hidden round scheduling; provenance is required.",
    }


def simpson_check() -> dict[str, object]:
    strata = ["easy", "hard"]
    system_a = [0.90, 0.40]
    system_b = [0.80, 0.30]
    fixed_weights = [0.50, 0.50]
    biased_a_weights = [0.10, 0.90]
    biased_b_weights = [0.90, 0.10]
    return {
        "name": "task_mix_simpson_trap",
        "passed": all(a > b for a, b in zip(system_a, system_b))
        and weighted_mean(system_a, biased_a_weights) < weighted_mean(system_b, biased_b_weights)
        and weighted_mean(system_a, fixed_weights) > weighted_mean(system_b, fixed_weights),
        "strata": strata,
        "system_a_by_stratum": system_a,
        "system_b_by_stratum": system_b,
        "fixed_mix": {
            "A": weighted_mean(system_a, fixed_weights),
            "B": weighted_mean(system_b, fixed_weights),
        },
        "biased_mix": {
            "A": weighted_mean(system_a, biased_a_weights),
            "B": weighted_mean(system_b, biased_b_weights),
        },
        "interpretation": "Changing task mixtures can reverse rankings; fixed weights and stratified reports are mandatory.",
    }


def ceiling_sensitivity_check() -> dict[str, object]:
    near_ceiling = {"first": 0.99, "final": 0.98, "WQ": wq(0.99, 0.98), "cWQ": clipped_wq(0.99, 0.98)}
    mid_range = {"first": 0.50, "final": 0.49, "WQ": wq(0.50, 0.49), "cWQ": clipped_wq(0.50, 0.49)}
    return {
        "name": "ceiling_sensitivity",
        "passed": abs(near_ceiling["WQ"]) > abs(mid_range["WQ"]),
        "near_ceiling": near_ceiling,
        "mid_range": mid_range,
        "interpretation": "Near-ceiling denominators amplify small regressions; report raw deltas and clipped variants.",
    }


def compression_accounting_check() -> dict[str, object]:
    corpus_bytes = 10_000
    honest_replacement_gain = 650
    glossary_cost = 210
    fake_replacement_gain = 120
    honest_net = honest_replacement_gain - glossary_cost
    fake_net = fake_replacement_gain - glossary_cost
    return {
        "name": "macro_accounting",
        "passed": honest_net > 0 and fake_net <= 0,
        "honest_net_gain": honest_net,
        "fake_net_gain": fake_net,
        "honest_ratio": corpus_bytes / (corpus_bytes - honest_replacement_gain + glossary_cost),
        "fake_ratio": corpus_bytes / (corpus_bytes - fake_replacement_gain + glossary_cost),
        "interpretation": "A macro is admissible only after paying definition/glossary cost.",
    }


def evidence_gate_check() -> dict[str, object]:
    required = {"raw_logs", "seeds", "rounds", "task_ids", "checkpoint", "metadata", "hash"}
    complete = {
        "raw_logs": "logs.jsonl",
        "seeds": [42, 137, 256],
        "rounds": [1, 2, 3, 4, 5],
        "task_ids": ["open_drawer", "stack_blocks"],
        "checkpoint": "policy.ckpt",
        "metadata": "simulator.json",
        "hash": "abc123",
    }
    incomplete = dict(complete)
    incomplete.pop("checkpoint")
    return {
        "name": "evidence_gate_minimum",
        "passed": required.issubset(complete) and not required.issubset(incomplete),
        "required_fields": sorted(required),
        "complete_passes": required.issubset(complete),
        "incomplete_passes": required.issubset(incomplete),
        "interpretation": "A leaderboard cell is not admissible when checkpoint/factory provenance is missing.",
    }


def run_checks() -> list[dict[str, object]]:
    return [
        boundedness_check(),
        separation_check(),
        non_identifiability_check(),
        simpson_check(),
        ceiling_sensitivity_check(),
        compression_accounting_check(),
        evidence_gate_check(),
    ]


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


def write_markdown(checks: list[dict[str, object]]) -> None:
    lines = [
        "# Wisdom Science Formal Checks v0",
        "",
        "| check | passed | interpretation |",
        "| --- | --- | --- |",
    ]
    for item in checks:
        lines.append(
            f"| `{item['name']}` | {item['passed']} | {item['interpretation']} |"
        )
    lines.append("")
    (RESULT_DIR / "formal_checks_v0.md").write_text("\n".join(lines), encoding="utf-8")


def write_latex_table(checks: list[dict[str, object]]) -> Path:
    lines = [
        r"\begin{tabular}{p{0.27\linewidth}p{0.12\linewidth}p{0.50\linewidth}}",
        r"\toprule",
        r"Check & Pass & What it guards against \\",
        r"\midrule",
    ]
    for item in checks:
        status = "yes" if item["passed"] else "no"
        lines.append(
            f"{tex_escape(item['name'])} & {status} & {tex_escape(item['interpretation'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = FORMAL_GEN / "formal_checks_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    FORMAL_GEN.mkdir(parents=True, exist_ok=True)
    checks = run_checks()
    summary = {
        "check_count": len(checks),
        "passed_count": sum(1 for item in checks if item["passed"]),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    (RESULT_DIR / "formal_checks_v0.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(checks)
    table = write_latex_table(checks)
    print(json.dumps({k: summary[k] for k in ("check_count", "passed_count", "all_passed")}, indent=2))
    print(table.relative_to(ROOT))


if __name__ == "__main__":
    main()
