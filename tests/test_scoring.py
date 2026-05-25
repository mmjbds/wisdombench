import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wisdombench.score import score_records  # noqa: E402


def test_score_records_computes_longitudinal_metrics():
    records = [
        {"agent": "a", "task_id": "t1", "strategy": "s", "seed": 1, "round": 1, "success": 0},
        {"agent": "a", "task_id": "t1", "strategy": "s", "seed": 1, "round": 2, "success": 1},
        {"agent": "a", "task_id": "t2", "strategy": "s", "seed": 1, "round": 1, "success": 0},
        {"agent": "a", "task_id": "t2", "strategy": "s", "seed": 1, "round": 2, "success": 0},
    ]

    metrics = score_records(records)

    assert metrics["trajectory_count"] == 2
    assert metrics["record_count"] == 4
    assert metrics["first_attempt_success"] == 0.0
    assert metrics["final_round_success"] == 0.5
    assert metrics["wisdom_quotient"] == 0.5
    assert metrics["repeat_failure_rate"] == 0.5
