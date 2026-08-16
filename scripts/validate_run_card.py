from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEX_COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(card: dict[str, object], check_files: bool) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "benchmark_commit",
        "model",
        "strategies",
        "seeds",
        "task_count",
        "round_count",
        "artifacts",
        "summary",
        "boundary",
    }
    missing = sorted(required - card.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
        return errors
    if card["schema_version"] != "wisdombench_run_card_v1":
        errors.append("schema_version must be wisdombench_run_card_v1")
    if not HEX_COMMIT.fullmatch(str(card["benchmark_commit"])):
        errors.append("benchmark_commit must be a 7-40 character lowercase Git commit")
    if not isinstance(card["strategies"], list) or not card["strategies"]:
        errors.append("strategies must be a non-empty list")
    if not isinstance(card["seeds"], list) or not card["seeds"]:
        errors.append("seeds must be a non-empty list")
    if not isinstance(card["task_count"], int) or card["task_count"] < 1:
        errors.append("task_count must be a positive integer")
    if not isinstance(card["round_count"], int) or card["round_count"] < 2:
        errors.append("round_count must be an integer of at least 2")
    if not isinstance(card["boundary"], str) or len(card["boundary"].strip()) < 20:
        errors.append("boundary must be a substantive string")

    artifacts = card["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty list")
        return errors
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifacts[{index}] must be an object")
            continue
        path_value = artifact.get("path")
        hash_value = artifact.get("sha256")
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"artifacts[{index}].path is required")
        if hash_value == "TO_BE_REPLACED_BY_AUDIT" and not check_files:
            continue
        if not isinstance(hash_value, str) or not HEX_SHA256.fullmatch(hash_value):
            errors.append(f"artifacts[{index}].sha256 must be 64 hexadecimal characters")
            continue
        if check_files and isinstance(path_value, str):
            target = (ROOT / path_value).resolve()
            if ROOT not in target.parents:
                errors.append(f"artifacts[{index}].path escapes repository root")
            elif not target.is_file():
                errors.append(f"artifacts[{index}].path does not exist: {path_value}")
            elif sha256(target).lower() != hash_value.lower():
                errors.append(f"artifacts[{index}].sha256 does not match {path_value}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a WisdomBench external run card")
    parser.add_argument("card", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    card = json.loads(args.card.read_text(encoding="utf-8"))
    errors = validate(card, args.check_files)
    if errors:
        print("Run card validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Run card validation passed: {args.card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
