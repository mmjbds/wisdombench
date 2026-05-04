#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

LOG_DIR="experiments/results/wbe_real/logs"
mkdir -p "${LOG_DIR}"

echo "== final public rollout gate: static checks =="
python -m py_compile \
  experiments/audit_public_rlbench_checkpoints.py \
  experiments/run_rlbench_wbe.py \
  experiments/validate_wbe_factory.py \
  experiments/analyze_wbe_real_results.py \
  experiments/summarize_public_factory_strict.py \
  experiments/adapters/rvt_rlbench_factory.py \
  experiments/adapters/public_rlbench_factory.py

print_gate_status() {
  python - <<'PY'
import json
from pathlib import Path

root = Path("experiments/results/wbe_real")
checks = {
    "public_checkpoint_panel_next": root / "public_checkpoint_panel_next_status.json",
    "public_checkpoint_strong_panel": root / "public_checkpoint_strong_panel_summary_20260504.json",
    "public_factory_strict": root / "public_factory_strict_status.json",
    "p5_peract_supported": root / "p5_peract_supported" / "statistics.json",
    "p6_peract_supported": root / "p6_peract_supported" / "statistics.json",
    "p5_rvt2_supported": root / "p5_rvt2_supported" / "statistics.json",
    "p6_rvt2_supported": root / "p6_rvt2_supported" / "statistics.json",
}

status = {}
for name, path in checks.items():
    item = {"exists": path.exists(), "path": str(path)}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            audit = data.get("audit", {})
            if audit:
                item.update({
                    "complete": audit.get("complete"),
                    "observed_episodes": audit.get("observed_episodes"),
                    "expected_episodes": audit.get("expected_episodes"),
                    "real_evidence_ok": audit.get("real_evidence_ok"),
                    "provenance_ok": audit.get("provenance_ok"),
                })
            if "total_episodes" in data:
                item["total_episodes"] = data.get("total_episodes")
                item["overall_success_rate"] = data.get("overall_success_rate")
            if "items" in data:
                item["items"] = data["items"]
            if "summary_payload" in data:
                item["summary_payload_present"] = True
        except Exception as exc:
            item["parse_error"] = repr(exc)
    status[name] = item

out = {
    "protocol": "public_rollout_final_20260504_gate",
    "mode": "status_only",
    "status": status,
}
Path("experiments/results/wbe_real/public_rollout_final_20260504_gate.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps(out, indent=2, ensure_ascii=False))
PY
}

echo "== final public rollout gate: current status =="
print_gate_status | tee "${LOG_DIR}/public_rollout_final_gate_before.log"

MODE="${WBE_FINAL_ROLLOUT_MODE:-verify}"
case "${MODE}" in
  verify)
    echo "== verify mode: no paid rollout launched =="
    ;;
  peract_supported)
    echo "== running public checkpoint supported panel =="
    WBE_PUBLIC_PANEL_MODE="${WBE_PUBLIC_PANEL_MODE:-supported}" \
      bash experiments/cloud/run_public_checkpoint_panel_next_p5_p6.sh \
      2>&1 | tee "${LOG_DIR}/public_rollout_final_peract_supported.log"
    ;;
  public_factory_strict)
    echo "== running public factory strict panel =="
    WBE_PUBLIC_STRICT_MODE="${WBE_PUBLIC_STRICT_MODE:-max}" \
      bash experiments/cloud/run_public_factory_strict_p5_p6.sh \
      2>&1 | tee "${LOG_DIR}/public_rollout_final_public_factory_strict.log"
    ;;
  all)
    echo "== running public checkpoint supported panel, then public factory strict panel =="
    WBE_PUBLIC_PANEL_MODE="${WBE_PUBLIC_PANEL_MODE:-supported}" \
      bash experiments/cloud/run_public_checkpoint_panel_next_p5_p6.sh \
      2>&1 | tee "${LOG_DIR}/public_rollout_final_peract_supported.log"
    WBE_PUBLIC_STRICT_MODE="${WBE_PUBLIC_STRICT_MODE:-max}" \
      bash experiments/cloud/run_public_factory_strict_p5_p6.sh \
      2>&1 | tee "${LOG_DIR}/public_rollout_final_public_factory_strict.log"
    ;;
  *)
    echo "Unknown WBE_FINAL_ROLLOUT_MODE=${MODE}; use verify, peract_supported, public_factory_strict, or all." >&2
    exit 2
    ;;
esac

echo "== final public rollout gate: after status =="
print_gate_status | tee "${LOG_DIR}/public_rollout_final_gate_after.log"
