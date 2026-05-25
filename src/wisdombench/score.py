"""Minimal longitudinal scorer for public WisdomBench examples.

The scorer intentionally uses a tiny public schema. It is not a substitute for
private evaluation traces or full paper artifacts.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
    return records


def _group_key(record: dict) -> tuple[str, str, int, str]:
    return (
        str(record["agent"]),
        str(record["task_id"]),
        int(record.get("seed", 0)),
        str(record.get("strategy", "unknown")),
    )


def _success(record: dict) -> float:
    value = record.get("success")
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return 1.0 if value > 0 else 0.0
    raise ValueError(f"Record has non-numeric success field: {record!r}")


def score_records(records: Iterable[dict]) -> dict:
    """Compute compact longitudinal metrics.

    Metrics:
    - first_attempt_success: mean success at the earliest round per trajectory.
    - final_round_success: mean success at the latest round per trajectory.
    - wisdom_quotient: final minus first, averaged across trajectories.
    - repeat_failure_rate: share of trajectories that fail every observed round.
    """

    trajectories: dict[tuple[str, str, int, str], list[dict]] = defaultdict(list)
    for record in records:
        for field in ("agent", "task_id", "round", "success"):
            if field not in record:
                raise ValueError(f"Missing required field {field!r}: {record!r}")
        trajectories[_group_key(record)].append(record)

    if not trajectories:
        raise ValueError("No records to score.")

    first_scores: list[float] = []
    final_scores: list[float] = []
    deltas: list[float] = []
    repeat_failures = 0

    for rows in trajectories.values():
        ordered = sorted(rows, key=lambda item: int(item["round"]))
        first = _success(ordered[0])
        final = _success(ordered[-1])
        first_scores.append(first)
        final_scores.append(final)
        deltas.append(final - first)
        if all(_success(row) == 0.0 for row in ordered):
            repeat_failures += 1

    n = len(deltas)
    return {
        "trajectory_count": n,
        "record_count": sum(len(rows) for rows in trajectories.values()),
        "first_attempt_success": round(mean(first_scores), 6),
        "final_round_success": round(mean(final_scores), 6),
        "wisdom_quotient": round(mean(deltas), 6),
        "repeat_failure_rate": round(repeat_failures / n, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score public WisdomBench sample JSONL.")
    parser.add_argument("--sample", required=True, type=Path, help="Path to JSONL records.")
    args = parser.parse_args()
    metrics = score_records(load_jsonl(args.sample))
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

