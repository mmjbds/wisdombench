#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

LOG_DIR="experiments/results/wbe_real/logs"
mkdir -p "${LOG_DIR}"

source /root/autodl-tmp/miniconda3/etc/profile.d/conda.sh
set +u
conda activate "${WBE_RVT_CONDA_ENV:-wbe-rvt}"
set -u

echo "== P9 recovery adapter pilot: static checks =="
python -m py_compile \
  experiments/embodied_antigen_labeler.py \
  experiments/prepare_p9_recovery_adapter_pilot.py \
  experiments/analyze_p9_recovery_adapter_pilot.py \
  experiments/run_rlbench_wbe.py \
  experiments/validate_wbe_factory.py \
  experiments/adapters/public_rlbench_factory.py

python experiments/embodied_antigen_labeler.py
python experiments/prepare_p9_recovery_adapter_pilot.py

MODE="${WBE_P9_RECOVERY_MODE:-verify}"
if [[ "${MODE}" == "verify" ]]; then
  echo "== verify mode: cloud prerequisites checked; no paid rollout launched =="
  python experiments/analyze_p9_recovery_adapter_pilot.py
  exit 0
fi
if [[ "${MODE}" != "run" ]]; then
  echo "Unknown WBE_P9_RECOVERY_MODE=${MODE}; expected verify or run." >&2
  exit 2
fi

export DISPLAY_ID="${DISPLAY_ID:-:2}"
export WBE_NVIDIA_XORG_GPU_INDEX="${WBE_NVIDIA_XORG_GPU_INDEX:-0}"
source experiments/cloud/start_rlbench_nvidia_display.sh

if [[ "${WBE_PUBLIC_STRICT_PREPARE:-0}" == "1" ]]; then
  bash experiments/cloud/prepare_public_runnable_factories.sh
fi

export WBE_RLBENCH_ROLLOUT_FACTORY=experiments.adapters.public_rlbench_factory:rollout
export WBE_VLA_SOURCE_ROOT="${WBE_VLA_SOURCE_ROOT:-/root/autodl-tmp/vla_sources}"
export WBE_PUBLIC_POLICY_DIR="${WBE_PUBLIC_POLICY_DIR:-/root/autodl-tmp/models/rlbench_public}"
export COPPELIASIM_ROOT="${COPPELIASIM_ROOT:-/root/autodl-tmp/CoppeliaSim}"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}:${COPPELIASIM_ROOT}"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_QPA_PLATFORM_PLUGIN_PATH:-${COPPELIASIM_ROOT}}"

export WBE_PUBLIC_FACTORY_ADAPTER_ID="${WBE_PUBLIC_FACTORY_ADAPTER_ID:-p9_recovery_knob_v0}"
export WBE_PUBLIC_FACTORY_ADAPTER_NOTE="${WBE_PUBLIC_FACTORY_ADAPTER_NOTE:-antigen-derived non-training recovery pilot}"
export WBE_PUBLIC_FACTORY_MAX_STEPS="${WBE_PUBLIC_FACTORY_MAX_STEPS:-50}"
export WBE_PUBLIC_FACTORY_MAX_TRIES="${WBE_PUBLIC_FACTORY_MAX_TRIES:-2}"
export WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC="${WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC:-2400}"
export WBE_ACT3D_DIFFUSION_TIMESTEPS="${WBE_ACT3D_DIFFUSION_TIMESTEPS:-150}"
export WBE_3DDA_DIFFUSION_TIMESTEPS="${WBE_3DDA_DIFFUSION_TIMESTEPS:-150}"

PLAN_JSON="experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.json"
RAW_OUT="${WBE_P9_RECOVERY_RAW:-experiments/results/wbe_real/p9_recovery_adapter_public_factory_raw.jsonl}"

readarray -t ACT3D_TASKS < <(python - <<'PY'
import json
from pathlib import Path
plan = json.loads(Path("experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.json").read_text(encoding="utf-8"))
for item in plan.get("agent_plans", []):
    if item.get("agent_id") == "act3d_peract":
        for task in item.get("task_ids", []):
            print(task)
PY
)

readarray -t DIFFUSER_TASKS < <(python - <<'PY'
import json
from pathlib import Path
plan = json.loads(Path("experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.json").read_text(encoding="utf-8"))
for item in plan.get("agent_plans", []):
    if item.get("agent_id") == "diffuser_actor_peract":
        for task in item.get("task_ids", []):
            print(task)
PY
)

echo "== P9 recovery adapter plan =="
cat "${PLAN_JSON}"

if (( ${#ACT3D_TASKS[@]} > 0 )); then
  echo "== running Act3D recovery cells: ${ACT3D_TASKS[*]} =="
  python experiments/validate_wbe_factory.py \
    --benchmark rlbench \
    --profile act3d_supported \
    --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
    --agent-id act3d_peract \
    --task-id "${ACT3D_TASKS[0]}" \
    --task-group rvt2_official \
    --seed 42 \
    --round 1 \
    --perturbation none \
    --output-dir experiments/results/wbe_real/factory_validation/p9_recovery_act3d

  python experiments/run_rlbench_wbe.py \
    --adapter real \
    --profile act3d_supported \
    --paper P5 \
    --agent-ids act3d_peract \
    --task-ids "${ACT3D_TASKS[@]}" \
    --rounds 1 \
    --seeds 42 \
    --output "${RAW_OUT}" \
    --resume \
    2>&1 | tee "${LOG_DIR}/p9_recovery_act3d_run.log"
fi

if (( ${#DIFFUSER_TASKS[@]} > 0 )); then
  echo "== running 3D Diffuser recovery cells: ${DIFFUSER_TASKS[*]} =="
  python experiments/validate_wbe_factory.py \
    --benchmark rlbench \
    --profile diffuser_supported \
    --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
    --agent-id diffuser_actor_peract \
    --task-id "${DIFFUSER_TASKS[0]}" \
    --task-group rvt2_official \
    --seed 42 \
    --round 1 \
    --perturbation none \
    --output-dir experiments/results/wbe_real/factory_validation/p9_recovery_diffuser

  python experiments/run_rlbench_wbe.py \
    --adapter real \
    --profile diffuser_supported \
    --paper P5 \
    --agent-ids diffuser_actor_peract \
    --task-ids "${DIFFUSER_TASKS[@]}" \
    --rounds 1 \
    --seeds 42 \
    --output "${RAW_OUT}" \
    --resume \
    2>&1 | tee "${LOG_DIR}/p9_recovery_diffuser_run.log"
fi

python experiments/analyze_p9_recovery_adapter_pilot.py --adapter-raw "${RAW_OUT}"
python experiments/embodied_antigen_labeler.py
python experiments/prepare_p9_recovery_adapter_pilot.py
python experiments/wisdom_science_evidence_index.py

echo "== P9 recovery adapter pilot complete =="
