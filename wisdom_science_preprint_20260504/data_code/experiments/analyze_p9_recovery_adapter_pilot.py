"""Analyze matched baseline vs P9 recovery-adapter pilot rows."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"

BASELINE_RAW = [
    "experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl",
    "experiments/results/wbe_real/p5_p6_diffuser_strict_mini18_raw.jsonl",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def resolve_input_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def cell_key(row: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(row.get("agent_id")),
        str(row.get("task_id")),
        int(row.get("seed", 0)),
        int(row.get("round", 0)),
    )


def build_analysis(adapter_raw: Path) -> dict[str, Any]:
    adapter_raw = resolve_input_path(adapter_raw)
    baseline_rows = []
    for rel in BASELINE_RAW:
        baseline_rows.extend(read_jsonl(ROOT / rel))
    adapter_rows = read_jsonl(adapter_raw)
    baseline = {cell_key(row): row for row in baseline_rows}

    matched = []
    rescued = []
    regressions = []
    for row in adapter_rows:
        key = cell_key(row)
        before = baseline.get(key)
        if before is None:
            continue
        item = {
            "agent_id": key[0],
            "task_id": key[1],
            "seed": key[2],
            "round": key[3],
            "baseline_success": bool(before.get("success")),
            "adapter_success": bool(row.get("success")),
            "baseline_score": before.get("score"),
            "adapter_score": row.get("score"),
            "adapter_metadata": {
                "recovery_adapter": (row.get("metadata") or {}).get("recovery_adapter", {}),
                "evidence_mode": row.get("evidence_mode"),
                "trajectory_path": row.get("trajectory_path", ""),
            },
        }
        matched.append(item)
        if not item["baseline_success"] and item["adapter_success"]:
            rescued.append(item)
        if item["baseline_success"] and not item["adapter_success"]:
            regressions.append(item)

    baseline_failures = [item for item in matched if not item["baseline_success"]]
    return {
        "schema": "p9_recovery_adapter_pilot_analysis_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "adapter_raw": display_path(adapter_raw),
        "adapter_raw_exists": adapter_raw.exists(),
        "matched_cells": len(matched),
        "matched_baseline_failures": len(baseline_failures),
        "rescued_failures": len(rescued),
        "regressions": len(regressions),
        "baseline_failure_rescue_rate": round(len(rescued) / len(baseline_failures), 6) if baseline_failures else None,
        "claim_ready": adapter_raw.exists() and len(matched) > 0,
        "claim_boundary": (
            "If rescued_failures > 0, this supports a small matched recovery-adapter pilot, "
            "not a full public leaderboard or trained-policy claim."
        ),
        "matched": matched,
        "rescued": rescued,
        "regressions_detail": regressions,
    }


def write_markdown(analysis: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# P9 Recovery Adapter Pilot Analysis",
        "",
        f"Generated UTC: {analysis['generated_utc']}",
        f"Adapter raw exists: `{analysis['adapter_raw_exists']}`",
        f"Matched cells: {analysis['matched_cells']}",
        f"Matched baseline failures: {analysis['matched_baseline_failures']}",
        f"Rescued failures: {analysis['rescued_failures']}",
        f"Regressions: {analysis['regressions']}",
        f"Baseline failure rescue rate: {analysis['baseline_failure_rescue_rate']}",
        "",
        f"Boundary: {analysis['claim_boundary']}",
        "",
        "| agent | task | seed | round | baseline | adapter |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in analysis["matched"]:
        lines.append(
            f"| {item['agent_id']} | {item['task_id']} | {item['seed']} | {item['round']} | "
            f"{item['baseline_success']} / {item['baseline_score']} | "
            f"{item['adapter_success']} / {item['adapter_score']} |"
        )
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze P9 recovery-adapter matched pilot.")
    parser.add_argument(
        "--adapter-raw",
        type=Path,
        default=ROOT / "experiments" / "results" / "wbe_real" / "p9_recovery_adapter_public_factory_raw.jsonl",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RESULT_DIR / "p9_recovery_adapter_pilot_analysis_20260504.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RESULT_DIR / "p9_recovery_adapter_pilot_analysis_20260504.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    analysis = build_analysis(args.adapter_raw)
    args.output_json.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(analysis, args.output_md)
    print(
        json.dumps(
            {
                "matched_cells": analysis["matched_cells"],
                "rescued_failures": analysis["rescued_failures"],
                "claim_ready": analysis["claim_ready"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
