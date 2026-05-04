"""Prepare a cloud-ready P9 recovery-adapter pilot plan.

The pilot is intentionally small and falsifiable. It selects failed Act3D and
3D Diffuser public-factory cells that already have baseline evidence, then
prepares a non-training recovery adapter based on safer evaluator knobs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"

DEFAULT_ANTIGENS = RESULT_DIR / "embodied_antigen_labels_v0.jsonl"
DEFAULT_PLAN_JSON = RESULT_DIR / "p9_recovery_adapter_pilot_plan_20260504.json"
DEFAULT_PLAN_MD = RESULT_DIR / "p9_recovery_adapter_pilot_plan_20260504.md"

PUBLIC_FACTORY_MODES = {
    "real_act3d_official_rlbench",
    "real_3d_diffuser_actor_official_rlbench",
}

AGENT_PROFILE = {
    "act3d_peract": "act3d_supported",
    "diffuser_actor_peract": "diffuser_supported",
}

ADAPTER_ENV = {
    "WBE_PUBLIC_FACTORY_ADAPTER_ID": "p9_recovery_knob_v0",
    "WBE_PUBLIC_FACTORY_ADAPTER_NOTE": "antigen-derived non-training recovery pilot",
    "WBE_PUBLIC_FACTORY_MAX_STEPS": "50",
    "WBE_PUBLIC_FACTORY_MAX_TRIES": "2",
    "WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC": "2400",
    "WBE_ACT3D_DIFFUSION_TIMESTEPS": "150",
    "WBE_3DDA_DIFFUSION_TIMESTEPS": "150",
}


def load_antigens(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def select_public_factory_failures(antigens: list[dict[str, Any]], max_cells: int) -> list[dict[str, Any]]:
    candidates = []
    for item in antigens:
        evidence = item.get("evidence") if isinstance(item.get("evidence"), dict) else {}
        mode = str(evidence.get("evidence_mode", ""))
        policy = str(item.get("policy", ""))
        if mode not in PUBLIC_FACTORY_MODES or policy not in AGENT_PROFILE:
            continue
        if bool(item.get("success")):
            continue
        candidates.append(item)

    class_rank = {
        "recovery_loop_failure": 0,
        "actuator_joint_instability": 1,
        "placement_spatial_failure": 2,
        "instruction_grounding_failure": 3,
        "grasp_contact_failure": 4,
    }
    candidates.sort(
        key=lambda item: (
            class_rank.get(str(item.get("failure_class")), 9),
            str(item.get("policy")),
            str(item.get("task")),
        )
    )
    return candidates[:max_cells]


def build_plan(selected: list[dict[str, Any]]) -> dict[str, Any]:
    by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in selected:
        by_agent[str(item["policy"])].append(item)

    agent_plans = []
    for agent_id, rows in sorted(by_agent.items()):
        task_ids = sorted({str(item["task"]) for item in rows})
        seeds = sorted({int(item["seed"]) for item in rows if item.get("seed") is not None})
        rounds = sorted({int(item["round"]) for item in rows if item.get("round") is not None})
        agent_plans.append(
            {
                "agent_id": agent_id,
                "profile": AGENT_PROFILE[agent_id],
                "task_ids": task_ids,
                "seeds": seeds or [42],
                "rounds": rounds or [1],
                "baseline_failure_cells": len(rows),
                "failure_classes": sorted({str(item["failure_class"]) for item in rows}),
            }
        )

    task_count = sum(len(item["task_ids"]) for item in agent_plans)
    expected_minutes = round(max(8.0, task_count * 3.5), 1)
    return {
        "schema": "p9_recovery_adapter_pilot_plan_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "adapter_id": ADAPTER_ENV["WBE_PUBLIC_FACTORY_ADAPTER_ID"],
        "training_required": False,
        "cloud_required_for_rollout": True,
        "minimum_gpu": "1x A800 80GB is enough; 2 GPUs only help parallelism.",
        "expected_wall_time_minutes": expected_minutes,
        "claim_boundary": (
            "This pilot may support a recovery-adapter improvement claim only after "
            "matched rerun rows exist and are compared with baseline failures."
        ),
        "adapter_env": ADAPTER_ENV,
        "input_antigen_count": len(selected),
        "agent_plans": agent_plans,
        "selected_antigens": selected,
        "output_raw": "experiments/results/wbe_real/p9_recovery_adapter_public_factory_raw.jsonl",
        "analysis_json": "experiments/results/wisdom_science/p9_recovery_adapter_pilot_analysis_20260504.json",
        "analysis_md": "experiments/results/wisdom_science/p9_recovery_adapter_pilot_analysis_20260504.md",
    }


def write_markdown(plan: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# P9 Recovery Adapter Pilot Plan",
        "",
        f"Generated UTC: {plan['generated_utc']}",
        f"Adapter: `{plan['adapter_id']}`",
        f"Training required: `{plan['training_required']}`",
        f"Cloud required for rollout: `{plan['cloud_required_for_rollout']}`",
        f"Minimum GPU: {plan['minimum_gpu']}",
        f"Expected wall time: about {plan['expected_wall_time_minutes']} minutes",
        "",
        f"Boundary: {plan['claim_boundary']}",
        "",
        "## Agent Plans",
        "",
        "| agent | profile | tasks | cells | failure classes |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for item in plan["agent_plans"]:
        lines.append(
            f"| {item['agent_id']} | {item['profile']} | {len(item['task_ids'])} | "
            f"{item['baseline_failure_cells']} | {', '.join(item['failure_classes'])} |"
        )
    lines.extend(["", "## Adapter Environment", "", "| key | value |", "| --- | --- |"])
    for key, value in plan["adapter_env"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Launch", "", "```bash", "WBE_P9_RECOVERY_MODE=run bash experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh", "```", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare P9 recovery-adapter cloud pilot.")
    parser.add_argument("--antigens", type=Path, default=DEFAULT_ANTIGENS)
    parser.add_argument("--max-cells", type=int, default=12)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_PLAN_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    antigens = load_antigens(args.antigens)
    selected = select_public_factory_failures(antigens, args.max_cells)
    plan = build_plan(selected)
    args.output_json.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(plan, args.output_md)
    print(
        json.dumps(
            {
                "selected_antigens": plan["input_antigen_count"],
                "agent_plans": len(plan["agent_plans"]),
                "expected_wall_time_minutes": plan["expected_wall_time_minutes"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
