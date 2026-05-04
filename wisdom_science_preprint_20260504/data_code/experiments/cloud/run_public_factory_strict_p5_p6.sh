#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

source /root/autodl-tmp/miniconda3/etc/profile.d/conda.sh
set +u
conda activate "${WBE_RVT_CONDA_ENV:-wbe-rvt}"
set -u

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
export WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC="${WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC:-1200}"
export WBE_3DDA_DIFFUSION_TIMESTEPS="${WBE_3DDA_DIFFUSION_TIMESTEPS:-100}"

LOG_DIR="experiments/results/wbe_real/logs"
mkdir -p "${LOG_DIR}"

MODE="${WBE_PUBLIC_STRICT_MODE:-recommended}"
DIFFUSER_MINI3_TASKS=(reach_and_drag put_item_in_drawer push_buttons)
DIFFUSER_MINI6_TASKS=(reach_and_drag put_item_in_drawer push_buttons close_jar turn_tap slide_block_to_color_target)

run_analyze_pair() {
  local raw="$1"
  local design_p5="$2"
  local design_p6="$3"
  local out_p5="$4"
  local out_p6="$5"
  python experiments/analyze_wbe_real_results.py "${raw}" --design "${design_p5}" --output "${out_p5}"
  python experiments/analyze_wbe_real_results.py "${raw}" --design "${design_p6}" --output "${out_p6}"
}

run_act3d_mini18() {
  local raw="${WBE_ACT3D_STRICT_RAW:-experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl}"
  python experiments/validate_wbe_factory.py \
    --benchmark rlbench \
    --profile act3d_supported \
    --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
    --agent-id act3d_peract \
    --task-id reach_and_drag \
    --task-group rvt2_official \
    --seed 42 \
    --round 1 \
    --perturbation none \
    --output-dir experiments/results/wbe_real/factory_validation/act3d_strict

  python experiments/run_rlbench_wbe.py \
    --adapter real \
    --profile act3d_supported \
    --paper P5 \
    --output "${raw}" \
    --rounds 1 \
    --seeds 42 \
    --resume \
    2>&1 | tee "${LOG_DIR}/p5_p6_act3d_strict_mini18_run.log"

  run_analyze_pair "${raw}" p5_act3d_mini18 p6_act3d_mini18 \
    experiments/results/wbe_real/p5_act3d_strict_mini18 \
    experiments/results/wbe_real/p6_act3d_strict_mini18
}

run_diffuser_panel() {
  local panel="$1"
  shift
  local tasks=("$@")
  local raw="experiments/results/wbe_real/p5_p6_diffuser_strict_${panel}_raw.jsonl"
  local design_p5="p5_diffuser_${panel}"
  local design_p6="p6_diffuser_${panel}"

  python experiments/validate_wbe_factory.py \
    --benchmark rlbench \
    --profile diffuser_supported \
    --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
    --agent-id diffuser_actor_peract \
    --task-id "${tasks[0]}" \
    --task-group rvt2_official \
    --seed 42 \
    --round 1 \
    --perturbation none \
    --output-dir experiments/results/wbe_real/factory_validation/diffuser_strict_${panel}

  python experiments/run_rlbench_wbe.py \
    --adapter real \
    --profile diffuser_supported \
    --paper P5 \
    --output "${raw}" \
    --rounds 1 \
    --seeds 42 \
    --task-ids "${tasks[@]}" \
    --resume \
    2>&1 | tee "${LOG_DIR}/p5_p6_diffuser_strict_${panel}_run.log"

  run_analyze_pair "${raw}" "${design_p5}" "${design_p6}" \
    "experiments/results/wbe_real/p5_diffuser_strict_${panel}" \
    "experiments/results/wbe_real/p6_diffuser_strict_${panel}"
}

case "${MODE}" in
  smoke)
    python experiments/validate_wbe_factory.py \
      --benchmark rlbench \
      --profile act3d_supported \
      --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
      --agent-id act3d_peract \
      --task-id reach_and_drag \
      --task-group rvt2_official \
      --seed 42 \
      --round 1 \
      --perturbation none \
      --output-dir experiments/results/wbe_real/factory_validation/act3d_strict_smoke
    python experiments/validate_wbe_factory.py \
      --benchmark rlbench \
      --profile diffuser_supported \
      --factory "${WBE_RLBENCH_ROLLOUT_FACTORY}" \
      --agent-id diffuser_actor_peract \
      --task-id reach_and_drag \
      --task-group rvt2_official \
      --seed 42 \
      --round 1 \
      --perturbation none \
      --output-dir experiments/results/wbe_real/factory_validation/diffuser_strict_smoke
    ;;
  recommended)
    run_act3d_mini18
    run_diffuser_panel mini3 "${DIFFUSER_MINI3_TASKS[@]}"
    ;;
  mini6)
    run_act3d_mini18
    run_diffuser_panel mini6 "${DIFFUSER_MINI6_TASKS[@]}"
    ;;
  max)
    export WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC="${WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC_MAX:-2400}"
    run_act3d_mini18
    run_diffuser_panel mini18 put_item_in_drawer reach_and_drag turn_tap slide_block_to_color_target open_drawer put_groceries_in_cupboard place_shape_in_shape_sorter put_money_in_safe push_buttons close_jar stack_blocks place_cups place_wine_at_rack_location light_bulb_in sweep_to_dustpan_of_size insert_onto_square_peg meat_off_grill stack_cups
    ;;
  *)
    echo "Unknown WBE_PUBLIC_STRICT_MODE=${MODE}; expected smoke, recommended, mini6, or max" >&2
    exit 2
    ;;
esac

python experiments/summarize_public_factory_strict.py \
  --inputs \
    experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl \
    experiments/results/wbe_real/p5_p6_diffuser_strict_mini3_raw.jsonl \
    experiments/results/wbe_real/p5_p6_diffuser_strict_mini6_raw.jsonl \
    experiments/results/wbe_real/p5_p6_diffuser_strict_mini18_raw.jsonl \
  --output experiments/results/wbe_real/public_factory_strict_summary.json \
  --csv experiments/results/wbe_real/public_factory_strict_agents.csv \
  2>&1 | tee "${LOG_DIR}/public_factory_strict_summary.log"

python - <<'PY'
import json
import os
from pathlib import Path
summary_path = Path("experiments/results/wbe_real/public_factory_strict_summary.json")
status = {
    "protocol": "public_factory_strict_wbe",
    "mode": os.environ.get("WBE_PUBLIC_STRICT_MODE", "recommended"),
    "summary": str(summary_path),
    "summary_exists": summary_path.exists(),
}
if summary_path.exists():
    status["summary_payload"] = json.loads(summary_path.read_text(encoding="utf-8"))
out = Path("experiments/results/wbe_real/public_factory_strict_status.json")
out.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(status, indent=2, ensure_ascii=False))
PY
