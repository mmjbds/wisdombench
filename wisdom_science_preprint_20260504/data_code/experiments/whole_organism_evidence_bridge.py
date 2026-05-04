"""Bridge Whole-Organism Intelligence layers to existing evidence artifacts.

This script is intentionally conservative. It does not turn schema-only layers
into performance claims; it records which layers already have real rollout/API
support and which layers still need richer instrumentation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"


RAW_SOURCES = [
    {
        "source_id": "self_trained_lowdim_rlbench_6300",
        "path": "experiments/results/wbe_real/p5_p6_lowdim_rlbench_6300_raw.jsonl",
        "description": "Self-trained low-dimensional RLBench imitation baseline.",
    },
    {
        "source_id": "rvt2_public_checkpoint_supported",
        "path": "experiments/results/wbe_real/p5_p6_rvt2_supported_raw.jsonl",
        "description": "RVT-2 official/public checkpoint supported-set validation.",
    },
    {
        "source_id": "peract_public_checkpoint_supported",
        "path": "experiments/results/wbe_real/p5_p6_peract_official_supported_raw.jsonl",
        "description": "PerAct official/public checkpoint supported-set validation.",
    },
    {
        "source_id": "act3d_public_factory_strict",
        "path": "experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl",
        "description": "Act3D public-factory strict sidecar.",
    },
    {
        "source_id": "diffuser_public_factory_strict",
        "path": "experiments/results/wbe_real/p5_p6_diffuser_strict_mini18_raw.jsonl",
        "description": "3D Diffuser Actor public-factory strict sidecar.",
    },
    {
        "source_id": "unifolm_vla_libero_supported",
        "path": "experiments/results/wbe_real/p7_libero_raw.jsonl",
        "description": "UnifoLM-VLA LIBERO supported validation.",
    },
]


def read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {"exists": False, "path": rel_path}
    return {"exists": True, "path": rel_path, "payload": json.loads(path.read_text(encoding="utf-8"))}


def summarize_jsonl(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    summary: dict[str, Any] = {
        "path": rel_path,
        "exists": path.exists(),
        "rows": 0,
        "successes": 0,
        "failures": 0,
        "json_errors": 0,
        "trajectory_path_rows": 0,
        "wall_time_rows": 0,
        "environment_rows": 0,
        "git_commit_rows": 0,
        "checkpoint_path_rows": 0,
        "duplicate_cell_count": 0,
    }
    if not path.exists():
        return summary

    agents: set[str] = set()
    architectures: set[str] = set()
    tasks: set[str] = set()
    seeds: set[str] = set()
    rounds: set[str] = set()
    benchmarks: set[str] = set()
    evidence_modes: set[str] = set()
    cell_keys: set[tuple[Any, ...]] = set()
    wall_times: list[float] = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                summary["json_errors"] += 1
                continue

            summary["rows"] += 1
            if bool(record.get("success")):
                summary["successes"] += 1
            else:
                summary["failures"] += 1

            if record.get("trajectory_path"):
                summary["trajectory_path_rows"] += 1
            if record.get("environment"):
                summary["environment_rows"] += 1
            if record.get("git_commit"):
                summary["git_commit_rows"] += 1
            metadata = record.get("metadata") or {}
            if metadata.get("checkpoint_path"):
                summary["checkpoint_path_rows"] += 1

            wall_time = record.get("wall_time_s")
            if isinstance(wall_time, (int, float)):
                summary["wall_time_rows"] += 1
                wall_times.append(float(wall_time))

            for target, key in (
                (agents, "agent_id"),
                (architectures, "architecture"),
                (tasks, "task_id"),
                (seeds, "seed"),
                (rounds, "round"),
                (benchmarks, "benchmark"),
                (evidence_modes, "evidence_mode"),
            ):
                value = record.get(key)
                if value is not None:
                    target.add(str(value))

            cell_keys.add(
                (
                    record.get("paper"),
                    record.get("benchmark"),
                    record.get("task_id"),
                    record.get("agent_id"),
                    record.get("seed"),
                    record.get("round"),
                    record.get("perturbation"),
                    record.get("evidence_mode"),
                )
            )

    summary.update(
        {
            "success_rate": round(summary["successes"] / summary["rows"], 6) if summary["rows"] else 0.0,
            "agent_count": len(agents),
            "architecture_count": len(architectures),
            "task_count": len(tasks),
            "seed_count": len(seeds),
            "round_count": len(rounds),
            "benchmark_count": len(benchmarks),
            "evidence_modes": sorted(evidence_modes),
            "agents": sorted(agents)[:24],
            "architectures": sorted(architectures)[:24],
            "benchmarks": sorted(benchmarks),
            "mean_wall_time_s": round(mean(wall_times), 4) if wall_times else None,
            "duplicate_cell_count": max(0, summary["rows"] - len(cell_keys)),
        }
    )
    return summary


def count_rows(*summaries: dict[str, Any]) -> int:
    return sum(int(item.get("rows", 0)) for item in summaries)


def count_successes(*summaries: dict[str, Any]) -> int:
    return sum(int(item.get("successes", 0)) for item in summaries)


def support(*items: str) -> list[str]:
    return [item for item in items if item]


def build_bridge() -> dict[str, Any]:
    raw_summaries = {
        item["source_id"]: {
            **summarize_jsonl(item["path"]),
            "source_id": item["source_id"],
            "description": item["description"],
        }
        for item in RAW_SOURCES
    }
    lowdim = raw_summaries["self_trained_lowdim_rlbench_6300"]
    rvt2 = raw_summaries["rvt2_public_checkpoint_supported"]
    peract = raw_summaries["peract_public_checkpoint_supported"]
    act3d = raw_summaries["act3d_public_factory_strict"]
    diffuser = raw_summaries["diffuser_public_factory_strict"]
    libero = raw_summaries["unifolm_vla_libero_supported"]

    api_panel = read_json(
        "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.json"
    )
    perspectival = read_json("experiments/results/wisdom_science/perspectival_grounding_v0.json")
    organism = read_json("experiments/results/wisdom_science/whole_organism_intelligence_v0.json")
    public_checkpoint_status = read_json(
        "experiments/results/wbe_real/public_checkpoint_panel_next_status.json"
    )
    public_factory_status = read_json("experiments/results/wbe_real/public_factory_strict_status.json")

    api_rows = int(api_panel.get("payload", {}).get("row_count", 0)) if api_panel["exists"] else 0
    p8_cases = (
        int(perspectival.get("payload", {}).get("aggregate", {}).get("case_count", 0))
        if perspectival["exists"]
        else 0
    )
    p8_reduction = (
        float(perspectival.get("payload", {}).get("aggregate", {}).get("total_ambiguity_reduction_bits", 0.0))
        if perspectival["exists"]
        else 0.0
    )
    layer_count = int(organism.get("payload", {}).get("layer_count", 0)) if organism["exists"] else 0
    real_rollout_rows = count_rows(lowdim, rvt2, peract, act3d, diffuser, libero)
    real_rollout_successes = count_successes(lowdim, rvt2, peract, act3d, diffuser, libero)
    trajectory_rows = sum(int(item.get("trajectory_path_rows", 0)) for item in raw_summaries.values())
    wall_time_rows = sum(int(item.get("wall_time_rows", 0)) for item in raw_summaries.values())

    layer_bridge = [
        {
            "layer_id": "brain_policy",
            "support_level": "real_rollout",
            "table_support": f"{real_rollout_rows} embodied rows; {real_rollout_successes} successes",
            "primary_artifacts": [
                "experiments/results/wbe_real/public_checkpoint_panel_next_status.json",
                "experiments/results/wbe_real/public_checkpoint_strong_panel_summary_20260504.json",
                "experiments/results/wbe_real/public_factory_strict_status.json",
            ],
            "measured_support": support(
                f"RVT-2 + PerAct public checkpoint supported rows: {count_rows(rvt2, peract)}",
                f"Self-trained lowdim rows: {lowdim['rows']}",
                f"LIBERO UnifoLM-VLA rows: {libero['rows']}",
                f"Act3D/3D Diffuser strict sidecar rows: {count_rows(act3d, diffuser)}",
            ),
            "current_boundary": "Not a 12-policy public VLA/SOTA 6,300 leaderboard.",
            "next_upgrade": "Add more runnable public factories only when the checkpoint/evaluator path is fixed.",
        },
        {
            "layer_id": "senses_active_perception",
            "support_level": "toy_plus_trace_proxy",
            "table_support": f"{p8_cases} perspectival cases; {p8_reduction:.2f} bits reduced",
            "primary_artifacts": ["experiments/results/wisdom_science/perspectival_grounding_v0.json"],
            "measured_support": support(
                f"P8 cases resolved: {p8_cases}",
                f"Total ambiguity reduction: {p8_reduction:.2f} bits",
                f"Trajectory-path rows available as embodied observation proxies: {trajectory_rows}",
            ),
            "current_boundary": "Real rollouts store trajectories but do not yet log active view/tactile queries.",
            "next_upgrade": "Instrument active disambiguation actions before claiming perception-driven improvement.",
        },
        {
            "layer_id": "nervous_routing",
            "support_level": "system_artifact",
            "table_support": "routing modules plus API panel",
            "primary_artifacts": [
                "sovereign_core/context_packer.py",
                "engines/predictive_context.py",
                "engines/spreading_activation.py",
                "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.json",
            ],
            "measured_support": support(
                "Context packing, predictive context, and spreading activation are implemented artifacts.",
                f"API longitudinal rows exercising strategy routing: {api_rows}",
            ),
            "current_boundary": "Routing exists as a system artifact; robot-side module routing traces are not yet complete.",
            "next_upgrade": "Attach timestamped module-route logs to WB-E episodes.",
        },
        {
            "layer_id": "blood_metabolism",
            "support_level": "real_telemetry",
            "table_support": f"{wall_time_rows} rows with wall-clock telemetry",
            "primary_artifacts": [
                "experiments/results/wbe_real/p5_p6_lowdim_rlbench_6300_raw.jsonl",
                "experiments/results/wbe_real/p5_p6_rvt2_supported_raw.jsonl",
                "experiments/results/wbe_real/p7_libero_raw.jsonl",
            ],
            "measured_support": support(
                f"Rows with wall_time_s: {wall_time_rows}",
                f"Rows with environment/GPU metadata: {sum(int(item.get('environment_rows', 0)) for item in raw_summaries.values())}",
            ),
            "current_boundary": "Energy and API-cost counters are not yet normalized into one cross-platform unit.",
            "next_upgrade": "Add energy/API/memory counters to the evidence gate.",
        },
        {
            "layer_id": "joints_muscles",
            "support_level": "real_trajectory_paths",
            "table_support": f"{trajectory_rows} rows with trajectory paths",
            "primary_artifacts": [item["path"] for item in RAW_SOURCES],
            "measured_support": support(
                f"Rows with trajectory paths: {trajectory_rows}",
                f"Rows with checkpoint paths: {sum(int(item.get('checkpoint_path_rows', 0)) for item in raw_summaries.values())}",
            ),
            "current_boundary": "Trajectory paths certify action traces; low-level force/contact introspection is still sparse.",
            "next_upgrade": "Add contact-state and joint-limit summaries to antigen labels.",
        },
        {
            "layer_id": "immune_system",
            "support_level": "longitudinal_evidence",
            "table_support": "failure atlas plus repeated rounds",
            "primary_artifacts": [
                "experiments/embodied_failure_atlas_schema.json",
                "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.json",
                "experiments/results/wbe_real/p5_p6_lowdim_rlbench_6300_raw.jsonl",
            ],
            "measured_support": support(
                f"Lowdim longitudinal rows: {lowdim['rows']}",
                f"API cognitive-immunity panel rows: {api_rows}",
                f"Real embodied failures available for antigen labeling: {sum(int(item.get('failures', 0)) for item in raw_summaries.values())}",
            ),
            "current_boundary": "Existing rows support failure mining; new antibody-caused robot improvement needs re-evaluation.",
            "next_upgrade": "Offline-label antigens first, then run a small adapter re-evaluation.",
        },
        {
            "layer_id": "psychological_regulation",
            "support_level": "protocol_ready",
            "table_support": "confidence gate defined",
            "primary_artifacts": ["experiments/results/wisdom_science/whole_organism_intelligence_v0.json"],
            "measured_support": support(
                "Confidence, uncertainty, evidence pressure, and intervention logs are defined gates.",
                "API panel can host calibration prompts, but robot rollouts lack confidence traces.",
            ),
            "current_boundary": "No strong claim about affective or confidence regulation improvement yet.",
            "next_upgrade": "Add confidence/evidence-pressure fields to API and robot raw rows.",
        },
        {
            "layer_id": "social_body",
            "support_level": "toy_plus_api_protocol",
            "table_support": "deictic/social case plus API panel",
            "primary_artifacts": [
                "experiments/results/wisdom_science/perspectival_grounding_v0.json",
                "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.json",
            ],
            "measured_support": support(
                "P8 includes a deictic instruction case with context disambiguation.",
                f"API rows available for social/norm tasks: {api_rows}",
            ),
            "current_boundary": "No human-subject or live institution-governance evidence is claimed.",
            "next_upgrade": "Add explicit role, norm, approval, and override provenance to social tasks.",
        },
        {
            "layer_id": "game_theoretic_mind",
            "support_level": "toy_protocol",
            "table_support": "counter-reflexive toy case",
            "primary_artifacts": [
                "experiments/results/wisdom_science/perspectival_grounding_v0.json",
                "experiments/embodied_failure_atlas_schema.json",
            ],
            "measured_support": support(
                "P8 includes a counter-reflexive game case.",
                "P9 failure atlas includes counter_reflexive_game_failure.",
            ),
            "current_boundary": "No live multi-agent rollout is claimed.",
            "next_upgrade": "Run a small recursive-belief API panel before any embodied strategic claim.",
        },
    ]

    return {
        "schema": "whole_organism_evidence_bridge_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "readiness_judgment": {
            "current_paper_claims_ready": True,
            "large_training_required_now": False,
            "cloud_required_now": False,
            "data_completion_required_for_current_claims": False,
            "highest_roi_missing_work": "offline failure-antigen labeling over existing real rollout rows",
            "claim_boundary": "P9 is a mechanism/evidence-contract paper; new robot performance-improvement claims require adapter re-evaluation.",
        },
        "portfolio_counts": {
            "real_embodied_rows": real_rollout_rows,
            "real_embodied_successes": real_rollout_successes,
            "public_checkpoint_supported_rows": count_rows(rvt2, peract),
            "public_factory_strict_rows": count_rows(act3d, diffuser),
            "self_trained_lowdim_rows": lowdim["rows"],
            "libero_supported_rows": libero["rows"],
            "api_panel_rows": api_rows,
            "perspectival_cases": p8_cases,
            "whole_organism_layers": layer_count,
        },
        "raw_evidence_summary": raw_summaries,
        "external_status_artifacts": {
            "public_checkpoint_status": public_checkpoint_status,
            "public_factory_status": public_factory_status,
        },
        "layer_bridge": layer_bridge,
        "recommended_upgrades": [
            {
                "priority": 1,
                "name": "offline_antigen_labeling",
                "requires_cloud": False,
                "requires_training": False,
                "description": "Label existing failures by organ layer, causal cue, recovery opportunity, and transfer group.",
            },
            {
                "priority": 2,
                "name": "p8_perspectival_api_panel",
                "requires_cloud": False,
                "requires_training": False,
                "description": "Run six API models on perspectival/counter-reflexive cases with no-memory vs active-disambiguation strategies.",
            },
            {
                "priority": 3,
                "name": "p9_recovery_adapter_re_evaluation",
                "requires_cloud": True,
                "requires_training": "optional",
                "description": "Evaluate whether labeled antigens produce transferable robot improvement. Start with rule/prompt/recovery adapters before full training.",
            },
        ],
    }


def write_markdown(payload: dict[str, Any]) -> None:
    counts = payload["portfolio_counts"]
    lines = [
        "# Whole-Organism Evidence Bridge v0",
        "",
        f"Generated UTC: {payload['generated_utc']}",
        "",
        "## Readiness",
        "",
        f"- Current paper claims ready: `{payload['readiness_judgment']['current_paper_claims_ready']}`",
        f"- Large training required now: `{payload['readiness_judgment']['large_training_required_now']}`",
        f"- Cloud required now: `{payload['readiness_judgment']['cloud_required_now']}`",
        f"- Boundary: {payload['readiness_judgment']['claim_boundary']}",
        "",
        "## Portfolio Counts",
        "",
        "| item | count |",
        "| --- | ---: |",
    ]
    for key, value in counts.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Layer Bridge",
            "",
            "| layer | support level | direct support | boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in payload["layer_bridge"]:
        lines.append(
            f"| {item['layer_id']} | {item['support_level']} | "
            f"{item['table_support']} | {item['current_boundary']} |"
        )

    lines.extend(["", "## Recommended Upgrades", "", "| priority | name | cloud | training | description |", "| ---: | --- | --- | --- | --- |"])
    for item in payload["recommended_upgrades"]:
        lines.append(
            f"| {item['priority']} | {item['name']} | {item['requires_cloud']} | "
            f"{item['requires_training']} | {item['description']} |"
        )
    lines.append("")
    (RESULT_DIR / "whole_organism_evidence_bridge_v0.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_bridge()
    (RESULT_DIR / "whole_organism_evidence_bridge_v0.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(payload)
    print(json.dumps(payload["readiness_judgment"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
