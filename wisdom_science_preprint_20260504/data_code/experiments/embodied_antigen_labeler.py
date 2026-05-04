"""Offline failure-antigen labeling for WB-E evidence rows.

The labeler is deliberately evidence-preserving: it only reads existing raw
rollout rows, labels failed episodes, and writes antigen/antibody drafts. It
does not modify success rates or claim that the antibodies improved a robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"

DEFAULT_INPUTS = [
    "experiments/results/wbe_real/p5_p6_lowdim_rlbench_6300_raw.jsonl",
    "experiments/results/wbe_real/p5_p6_rvt2_supported_raw.jsonl",
    "experiments/results/wbe_real/p5_p6_peract_official_supported_raw.jsonl",
    "experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl",
    "experiments/results/wbe_real/p5_p6_diffuser_strict_mini18_raw.jsonl",
    "experiments/results/wbe_real/p7_libero_raw.jsonl",
]

PLACEMENT_TERMS = (
    "place",
    "put",
    "insert",
    "stack",
    "close_jar",
    "light_bulb",
    "drawer",
    "safe",
    "cupboard",
    "rack",
    "sorter",
    "peg",
)
GRASP_TERMS = ("grasp", "pick", "lift", "take", "meat_off", "reach_target")
ACTUATOR_TERMS = ("turn_tap", "sweep", "push_buttons", "reach_and_drag", "slide_block")
GROUNDING_TERMS = ("color", "shape", "numbered", "money", "groceries", "wine", "bulb")


ANTIBODY_TEMPLATES: dict[str, dict[str, Any]] = {
    "grasp_contact_failure": {
        "type": "recovery_primitive",
        "rule": "retry with slower approach, contact verification, and post-grasp lift check",
    },
    "placement_spatial_failure": {
        "type": "constraint",
        "rule": "add target-frame verification, insertion clearance, and final pose correction",
    },
    "occlusion_visual_grounding_failure": {
        "type": "attention_cue",
        "rule": "request side/front view agreement before committing to affordance",
    },
    "instruction_grounding_failure": {
        "type": "prompt_adapter",
        "rule": "bind object, relation, and target slot before action selection",
    },
    "actuator_joint_instability": {
        "type": "recovery_primitive",
        "rule": "increase step budget, smooth motion, and add joint-limit/contact checks",
    },
    "metabolic_budget_failure": {
        "type": "constraint",
        "rule": "stop or simplify when latency, retries, or simulator budget exceeds gate",
    },
    "recovery_loop_failure": {
        "type": "memory_rule",
        "rule": "do not repeat the same failed recovery without new sensory evidence",
    },
    "simulator_or_provenance_failure": {
        "type": "none",
        "rule": "repair missing trajectory, checkpoint, metadata, or simulator state before scoring",
    },
    "unknown": {
        "type": "memory_rule",
        "rule": "preserve failure for human review; do not infer unsupported mechanism",
    },
}


def stable_episode_id(row: dict[str, Any], raw_path: str) -> str:
    parts = [
        raw_path,
        str(row.get("paper", "")),
        str(row.get("benchmark", "")),
        str(row.get("agent_id", "")),
        str(row.get("task_id", "")),
        str(row.get("seed", "")),
        str(row.get("round", "")),
        str(row.get("perturbation", "")),
        str(row.get("evidence_mode", "")),
    ]
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"antigen_{digest}"


def task_contains(task_id: str, terms: tuple[str, ...]) -> bool:
    return any(term in task_id for term in terms)


def classify_failure(row: dict[str, Any]) -> tuple[str, str]:
    task_id = str(row.get("task_id", "")).lower()
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    trace_stats = metadata.get("trace_stats") if isinstance(metadata.get("trace_stats"), dict) else {}
    trajectory_path = str(row.get("trajectory_path", "")).strip()
    checkpoint_path = str(metadata.get("checkpoint_path", "")).strip()
    evidence_mode = str(row.get("evidence_mode", ""))

    if not trajectory_path or not evidence_mode:
        return "simulator_or_provenance_failure", "missing trajectory path or evidence mode"
    if "real_" in evidence_mode and not checkpoint_path:
        return "simulator_or_provenance_failure", "missing checkpoint path for real-evidence row"
    if bool(metadata.get("timed_out")):
        return "metabolic_budget_failure", "rollout timed out before a valid recovery"

    returncode = metadata.get("returncode")
    if isinstance(returncode, int) and returncode not in {0, 124}:
        return "simulator_or_provenance_failure", f"official evaluator returned code {returncode}"

    wall_time = row.get("wall_time_s")
    if isinstance(wall_time, (int, float)) and wall_time > 900:
        return "metabolic_budget_failure", f"very high wall time ({wall_time:.1f}s)"

    step_count = trace_stats.get("step_count")
    max_reward = trace_stats.get("max_reward")
    if isinstance(step_count, int) and step_count >= 25 and (max_reward in {0, 0.0, None}):
        return "recovery_loop_failure", "long trace ended without reward improvement"

    if task_contains(task_id, ACTUATOR_TERMS):
        return "actuator_joint_instability", f"task '{task_id}' stresses motion/control stability"
    if task_contains(task_id, GROUNDING_TERMS):
        return "instruction_grounding_failure", f"task '{task_id}' requires semantic target binding"
    if task_contains(task_id, PLACEMENT_TERMS):
        return "placement_spatial_failure", f"task '{task_id}' requires precise target placement"
    if task_contains(task_id, GRASP_TERMS):
        return "grasp_contact_failure", f"task '{task_id}' requires contact acquisition"
    if "occlusion" in task_id or "behind" in str(metadata).lower():
        return "occlusion_visual_grounding_failure", "metadata suggests hidden or ambiguous object state"
    return "unknown", "no stronger class can be inferred from task/trace metadata"


def transfer_group(row: dict[str, Any], failure_class: str) -> str:
    task_group = str(row.get("task_group", "") or "ungrouped")
    benchmark = str(row.get("benchmark", "") or "unknown")
    return f"{benchmark}:{task_group}:{failure_class}"


def recovery_opportunity(failure_class: str) -> str:
    return str(ANTIBODY_TEMPLATES.get(failure_class, ANTIBODY_TEMPLATES["unknown"])["rule"])


def build_antibody(row: dict[str, Any], failure_class: str, cue: str, raw_path: str) -> dict[str, Any]:
    template = ANTIBODY_TEMPLATES.get(failure_class, ANTIBODY_TEMPLATES["unknown"])
    return {
        "type": template["type"],
        "payload": {
            "rule": template["rule"],
            "task_id": row.get("task_id"),
            "agent_id": row.get("agent_id"),
            "causal_cue": cue,
        },
        "activation_condition": f"same transfer_group and failure_class={failure_class}",
        "provenance": raw_path,
    }


def row_to_antigen(row: dict[str, Any], raw_path: str) -> dict[str, Any]:
    failure_class, cue = classify_failure(row)
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    score = row.get("score")
    return {
        "episode_id": stable_episode_id(row, raw_path),
        "task": row.get("task_id"),
        "benchmark": row.get("benchmark"),
        "policy": row.get("agent_id"),
        "architecture": row.get("architecture"),
        "round": row.get("round"),
        "seed": row.get("seed"),
        "success": bool(row.get("success")),
        "score": score if isinstance(score, (int, float)) else None,
        "failure_class": failure_class,
        "causal_cue": cue,
        "recovery_opportunity": recovery_opportunity(failure_class),
        "transfer_group": transfer_group(row, failure_class),
        "evidence": {
            "trajectory_path": row.get("trajectory_path", ""),
            "metadata_path": "",
            "checkpoint_path": metadata.get("checkpoint_path", ""),
            "video_path": row.get("video_path") or None,
            "raw_log_path": raw_path,
            "git_commit": row.get("git_commit"),
            "evidence_mode": row.get("evidence_mode"),
        },
        "antibody": build_antibody(row, failure_class, cue, raw_path),
        "metrics": {
            "I_E": None,
            "EWQ": None,
            "Phi_E": None,
            "Psi_E": None,
            "H_E": None,
        },
    }


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def summarize(antigens: list[dict[str, Any]], source_stats: list[dict[str, Any]]) -> dict[str, Any]:
    by_class = Counter(item["failure_class"] for item in antigens)
    by_policy = Counter(str(item["policy"]) for item in antigens)
    by_benchmark = Counter(str(item["benchmark"]) for item in antigens)
    by_transfer = Counter(str(item["transfer_group"]) for item in antigens)
    class_policy: dict[str, Counter[str]] = defaultdict(Counter)
    for item in antigens:
        class_policy[item["failure_class"]][str(item["policy"])] += 1

    failure_classes = []
    for failure_class, count in by_class.most_common():
        policies = class_policy[failure_class].most_common(4)
        failure_classes.append(
            {
                "failure_class": failure_class,
                "count": count,
                "share": round(count / len(antigens), 6) if antigens else 0.0,
                "top_policies": [{"policy": key, "count": value} for key, value in policies],
                "recovery_opportunity": recovery_opportunity(failure_class),
            }
        )

    return {
        "schema": "embodied_antigen_labels_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_stats": source_stats,
        "antigen_count": len(antigens),
        "failure_class_count": len(by_class),
        "by_failure_class": failure_classes,
        "by_policy": [{"policy": key, "count": value} for key, value in by_policy.most_common()],
        "by_benchmark": [{"benchmark": key, "count": value} for key, value in by_benchmark.most_common()],
        "top_transfer_groups": [
            {"transfer_group": key, "count": value} for key, value in by_transfer.most_common(20)
        ],
        "claim_boundary": "Offline labels over existing failures only; no robot improvement is claimed.",
    }


def write_markdown(summary: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Embodied Antigen Labels v0",
        "",
        f"Generated UTC: {summary['generated_utc']}",
        f"Antigens: {summary['antigen_count']}",
        f"Failure classes: {summary['failure_class_count']}",
        "",
        "Boundary: offline labels over existing failures only; no robot improvement is claimed.",
        "",
        "## Failure Classes",
        "",
        "| failure class | count | share | top policies | recovery opportunity |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for item in summary["by_failure_class"]:
        top = ", ".join(f"{p['policy']}:{p['count']}" for p in item["top_policies"])
        lines.append(
            f"| {item['failure_class']} | {item['count']} | {item['share']:.3f} | "
            f"{top} | {item['recovery_opportunity']} |"
        )
    lines.extend(["", "## Sources", "", "| path | rows | failures | antigens |", "| --- | ---: | ---: | ---: |"])
    for item in summary["source_stats"]:
        lines.append(f"| `{item['path']}` | {item['rows']} | {item['failures']} | {item['antigens']} |")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label WB-E failed episodes as embodied antigens.")
    parser.add_argument("--inputs", nargs="*", default=DEFAULT_INPUTS)
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=RESULT_DIR / "embodied_antigen_labels_v0.jsonl",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=RESULT_DIR / "embodied_antigen_summary_v0.json",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=RESULT_DIR / "embodied_antigen_summary_v0.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    antigens: list[dict[str, Any]] = []
    source_stats = []

    for rel in args.inputs:
        path = ROOT / rel
        rows = read_rows(path)
        failures = [row for row in rows if not bool(row.get("success"))]
        source_antigens = [row_to_antigen(row, rel) for row in failures]
        antigens.extend(source_antigens)
        source_stats.append(
            {
                "path": rel,
                "exists": path.exists(),
                "rows": len(rows),
                "failures": len(failures),
                "antigens": len(source_antigens),
            }
        )

    with args.output_jsonl.open("w", encoding="utf-8") as handle:
        for antigen in antigens:
            handle.write(json.dumps(antigen, ensure_ascii=False, sort_keys=True) + "\n")

    summary = summarize(antigens, source_stats)
    args.summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.summary_md)
    print(json.dumps({"antigens": len(antigens), "failure_classes": summary["failure_class_count"]}, indent=2))


if __name__ == "__main__":
    main()
