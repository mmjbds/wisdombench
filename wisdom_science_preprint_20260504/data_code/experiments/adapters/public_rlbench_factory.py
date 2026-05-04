# -*- coding: utf-8 -*-
"""WB-E factory for public Act3D / 3D Diffuser RLBench official evaluators."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np


SUPPORTED_AGENT_IDS = {"act3d_peract", "diffuser_actor_peract"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _source_root() -> Path:
    return Path(os.environ.get("WBE_VLA_SOURCE_ROOT", "/root/autodl-tmp/vla_sources")).resolve()


def _asset_root() -> Path:
    return Path(os.environ.get("WBE_PUBLIC_POLICY_DIR", "/root/autodl-tmp/models/rlbench_public")).resolve()


def _dda_repo() -> Path:
    return Path(os.environ.get("WBE_3DDA_REPO", str(_source_root() / "3d_diffuser_actor"))).resolve()


def _instructions_path(repo: Path) -> Path:
    return Path(os.environ.get("WBE_3DDA_INSTRUCTIONS", str(repo / "instructions" / "peract" / "instructions.pkl"))).resolve()


def _data_dir(repo: Path) -> Path:
    return Path(os.environ.get("WBE_3DDA_DATA_DIR", str(repo / "data" / "peract" / "raw" / "test"))).resolve()


def _manifest_agent(agent_id: str) -> Dict[str, Any]:
    manifest_path = _repo_root() / "experiments" / "configs" / "rlbench_public_policy_panel.downloaded.json"
    if not manifest_path.exists():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    for row in manifest.get("agents", []):
        if row.get("agent_id") == agent_id:
            return row
    return {}


def _candidate_config(agent_id: str) -> Dict[str, Any]:
    repo = _dda_repo()
    asset_root = _asset_root()
    if agent_id == "act3d_peract":
        return {
            "agent_id": agent_id,
            "test_model": "act3d",
            "checkpoint": asset_root / "3d_diffuser_actor" / "act3d_peract.pth",
            "repo": repo,
            "entry": repo / "online_evaluation_rlbench" / "evaluate_policy.py",
            "rotation_parametrization": "quat_from_query",
            "predict_trajectory": "0",
            "num_history": "1",
            "quaternion_format": "xyzw",
            "diffusion_timesteps": os.environ.get("WBE_ACT3D_DIFFUSION_TIMESTEPS", "100"),
            "extra": {},
            "evidence_mode": "real_act3d_official_rlbench",
        }
    if agent_id == "diffuser_actor_peract":
        return {
            "agent_id": agent_id,
            "test_model": "3d_diffuser_actor",
            "checkpoint": asset_root / "3d_diffuser_actor" / "diffuser_actor_peract.pth",
            "repo": repo,
            "entry": repo / "online_evaluation_rlbench" / "evaluate_policy.py",
            "rotation_parametrization": "6D",
            "predict_trajectory": "1",
            "num_history": "3",
            "quaternion_format": "wxyz",
            "diffusion_timesteps": os.environ.get("WBE_3DDA_DIFFUSION_TIMESTEPS", "100"),
            "extra": {
                "fps_subsampling_factor": "5",
                "lang_enhanced": "0",
                "relative_action": "0",
            },
            "evidence_mode": "real_3d_diffuser_actor_official_rlbench",
        }
    raise ValueError(f"unsupported public RLBench agent_id: {agent_id}")


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)


def _base_official_args(cfg: Dict[str, Any], task_id: str, seed: int, output_file: Path) -> list[str]:
    repo = cfg["repo"]
    args = [
        "--checkpoint",
        str(cfg["checkpoint"]),
        "--tasks",
        task_id,
        "--seed",
        str(seed),
        "--num_episodes",
        str(int(os.environ.get("WBE_PUBLIC_FACTORY_NUM_EPISODES", "1"))),
        "--variations",
        str(int(os.environ.get("WBE_PUBLIC_FACTORY_VARIATION", "0"))),
        "--data_dir",
        str(_data_dir(repo)),
        "--instructions",
        str(_instructions_path(repo)),
        "--output_file",
        str(output_file),
        "--device",
        os.environ.get("WBE_PUBLIC_FACTORY_DEVICE", "cuda"),
        "--headless",
        os.environ.get("WBE_PUBLIC_FACTORY_HEADLESS", "0"),
        "--max_steps",
        os.environ.get("WBE_PUBLIC_FACTORY_MAX_STEPS", "25"),
        "--max_tries",
        os.environ.get("WBE_PUBLIC_FACTORY_MAX_TRIES", "1"),
        "--test_model",
        str(cfg["test_model"]),
        "--cameras",
        os.environ.get("WBE_PUBLIC_FACTORY_CAMERAS", "left_shoulder,right_shoulder,wrist,front"),
        "--action_dim",
        "8",
        "--collision_checking",
        "0",
        "--embedding_dim",
        "120",
        "--rotation_parametrization",
        str(cfg["rotation_parametrization"]),
        "--single_task_gripper_loc_bounds",
        "0",
        "--use_instruction",
        "1",
        "--predict_trajectory",
        str(cfg["predict_trajectory"]),
        "--num_history",
        str(cfg["num_history"]),
        "--gripper_loc_bounds_file",
        "tasks/18_peract_tasks_location_bounds.json",
        "--gripper_loc_bounds_buffer",
        "0.04",
        "--dense_interpolation",
        "1",
        "--interpolation_length",
        "2",
        "--quaternion_format",
        str(cfg["quaternion_format"]),
        "--verbose",
        os.environ.get("WBE_PUBLIC_FACTORY_VERBOSE", "0"),
        "--diffusion_timesteps",
        str(cfg["diffusion_timesteps"]),
    ]
    for key, value in cfg["extra"].items():
        args.extend([f"--{key}", str(value)])
    return args


def _pad_rows(rows: Iterable[Any]) -> np.ndarray:
    arrays = [np.asarray(row, dtype=float).reshape(-1) for row in rows if row is not None]
    if not arrays:
        return np.empty((0, 0), dtype=float)
    width = max(arr.shape[0] for arr in arrays)
    out = np.full((len(arrays), width), np.nan, dtype=float)
    for idx, arr in enumerate(arrays):
        out[idx, : arr.shape[0]] = arr
    return out


def _load_trace_arrays(trace_jsonl: Path) -> tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    actions = []
    positions = []
    rewards = []
    terminations = []
    if trace_jsonl.exists():
        with trace_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("type") != "step":
                    continue
                actions.append(row.get("action"))
                low_dim = row.get("low_dim")
                if isinstance(low_dim, dict) and "error" in low_dim:
                    low_dim = None
                positions.append(low_dim)
                reward = row.get("reward")
                if isinstance(reward, (int, float)):
                    rewards.append(float(reward))
                terminations.append(bool(row.get("terminate", False)))
    action_arr = _pad_rows(actions)
    position_arr = _pad_rows(positions)
    trace_stats = {
        "step_count": int(action_arr.shape[0]),
        "position_count": int(position_arr.shape[0]),
        "reward_count": len(rewards),
        "max_reward": max(rewards) if rewards else None,
        "last_reward": rewards[-1] if rewards else None,
        "termination_count": sum(1 for item in terminations if item),
    }
    return position_arr, action_arr, trace_stats


def _parse_official_output(path: Path, task_id: str) -> Dict[str, Any]:
    if not path.exists():
        return {"available": False}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    task_result = parsed.get(task_id, {})
    mean = task_result.get("mean") if isinstance(task_result, dict) else None
    success_count = None
    if isinstance(task_result, dict):
        success_count = task_result["0"] if "0" in task_result else task_result.get(0)
    return {
        "available": True,
        "raw": parsed,
        "mean": float(mean) if isinstance(mean, (int, float)) else None,
        "success_count": int(success_count) if isinstance(success_count, (int, float)) else None,
    }


def _git_revision(path: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return "unknown"


def rollout(
    *,
    benchmark: str,
    paper: str,
    agent_config: Dict[str, Any],
    task_id: str,
    task_group: str,
    seed: int,
    round_idx: int,
    perturbation: str,
    output_dir: str,
) -> Dict[str, Any]:
    if benchmark != "rlbench":
        raise ValueError(f"public RLBench factory only supports rlbench, got {benchmark}")
    if perturbation != "none":
        raise ValueError("public Act3D/3D Diffuser factory currently supports perturbation=none only")

    agent_id = str(agent_config.get("agent_id", ""))
    if agent_id not in SUPPORTED_AGENT_IDS:
        raise ValueError(f"unsupported agent_id for public RLBench factory: {agent_id}")

    cfg = _candidate_config(agent_id)
    for key in ("repo", "entry", "checkpoint"):
        if not Path(cfg[key]).exists():
            raise RuntimeError(f"{key} does not exist: {cfg[key]}")
    if not _instructions_path(cfg["repo"]).exists():
        raise RuntimeError(f"instructions cache does not exist: {_instructions_path(cfg['repo'])}")
    if not _data_dir(cfg["repo"]).exists():
        raise RuntimeError(f"data dir does not exist: {_data_dir(cfg['repo'])}")

    started = time.time()
    base = Path(output_dir).resolve() / "public_factory_strict" / _safe_name(agent_id)
    episode_dir = base / f"{_safe_name(task_id)}_s{seed}_r{round_idx}"
    episode_dir.mkdir(parents=True, exist_ok=True)
    official_output = episode_dir / "official_output.json"
    trace_jsonl = episode_dir / "trace_steps.jsonl"
    trace_summary = episode_dir / "trace_summary.json"
    stdout_path = episode_dir / "stdout.log"
    stderr_path = episode_dir / "stderr.log"

    wrapper = _repo_root() / "experiments" / "run_official_eval_with_trace.py"
    official_args = _base_official_args(cfg, task_id, seed, official_output)
    cmd = [
        sys.executable,
        str(wrapper),
        "--official-entry",
        str(cfg["entry"]),
        "--trace-jsonl",
        str(trace_jsonl),
        "--trace-summary",
        str(trace_summary),
        "--",
        *official_args,
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{_repo_root()}:{cfg['repo']}:{env.get('PYTHONPATH', '')}"
    timeout_sec = int(os.environ.get("WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC", "900"))
    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cfg["repo"]),
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
        stderr = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
        stderr += f"\nTIMEOUT after {timeout_sec}s"

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    positions, actions, trace_stats = _load_trace_arrays(trace_jsonl)
    official = _parse_official_output(official_output, task_id)
    mean_score = official.get("mean")
    score = float(mean_score) if isinstance(mean_score, (int, float)) else (float(trace_stats["max_reward"]) if trace_stats["max_reward"] is not None else 0.0)
    success = bool(returncode == 0 and score >= 0.5)
    manifest = _manifest_agent(agent_id)

    metadata = {
        "factory": "experiments.adapters.public_rlbench_factory:rollout",
        "candidate": agent_id,
        "checkpoint_path": str(cfg["checkpoint"]),
        "checkpoint_sha256": manifest.get("sha256", ""),
        "policy_repo": manifest.get("policy_repo", "https://github.com/nickgkan/3d_diffuser_actor"),
        "weight_source": manifest.get("weight_source", "https://huggingface.co/katefgroup/3d_diffuser_actor"),
        "official_repo": str(cfg["repo"]),
        "official_repo_git": _git_revision(cfg["repo"]),
        "official_entry": str(cfg["entry"]),
        "official_output_path": str(official_output),
        "trace_jsonl_path": str(trace_jsonl),
        "trace_summary_path": str(trace_summary),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "official_output": official,
        "trace_stats": trace_stats,
        "returncode": returncode,
        "timed_out": timed_out,
        "timeout_sec": timeout_sec,
        "command": cmd,
        "task_group": task_group,
        "elapsed_sec_factory": round(time.time() - started, 3),
    }
    adapter_id = os.environ.get("WBE_PUBLIC_FACTORY_ADAPTER_ID", "").strip()
    if adapter_id:
        metadata["recovery_adapter"] = {
            "adapter_id": adapter_id,
            "note": os.environ.get("WBE_PUBLIC_FACTORY_ADAPTER_NOTE", ""),
            "max_steps": os.environ.get("WBE_PUBLIC_FACTORY_MAX_STEPS", ""),
            "max_tries": os.environ.get("WBE_PUBLIC_FACTORY_MAX_TRIES", ""),
            "act3d_diffusion_timesteps": os.environ.get("WBE_ACT3D_DIFFUSION_TIMESTEPS", ""),
            "diffuser_diffusion_timesteps": os.environ.get("WBE_3DDA_DIFFUSION_TIMESTEPS", ""),
        }
    return {
        "success": success,
        "score": score,
        "positions": positions,
        "actions": actions,
        "evidence_mode": cfg["evidence_mode"],
        "environment": {
            "official_repo": str(cfg["repo"]),
            "official_repo_git": metadata["official_repo_git"],
            "public_policy_candidate": agent_id,
            "trace_wrapper": str(wrapper),
        },
        "metadata": metadata,
    }
