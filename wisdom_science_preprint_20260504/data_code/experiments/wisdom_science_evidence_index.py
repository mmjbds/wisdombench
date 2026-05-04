"""Build a reproducible evidence index for the Wisdom Science package."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"


ARTIFACTS = [
    ("framework", "papers/WISDOM_SCIENCE_MASTER_FRAMEWORK_20260504_CN.md"),
    ("execution_status", "papers/WISDOM_SCIENCE_EXECUTION_STATUS_20260504_CN.md"),
    ("terms", "papers/WISDOM_SCIENCE_TERMS_V1_CN.md"),
    ("claim_registry_doc", "papers/WISDOM_SCIENCE_CLAIM_REGISTRY_20260504_CN.md"),
    ("zenodo_inventory", "papers/ZENODO_REPO_ARTICLE_INVENTORY_20260504_CN.md"),
    ("zenodo_bibtex", "papers/wisdom_science_zenodo.bib"),
    ("collision_audit", "papers/REPRESENTATION_LAB_COLLISION_AUDIT_20260504_CN.md"),
    ("package_readme", "papers/WISDOM_SCIENCE_README_CN.md"),
    ("release_runbook", "papers/WISDOM_SCIENCE_RELEASE_RUNBOOK_CN.md"),
    ("submission_checklist", "papers/WISDOM_SCIENCE_SUBMISSION_CHECKLIST_20260504_CN.md"),
    ("cloud_public_rollout_final_launch", "experiments/CLOUD_PUBLIC_ROLLOUT_FINAL_LAUNCH_20260504_CN.md"),
    ("cloud_public_rollout_final_script", "experiments/cloud/run_public_rollout_final_20260504.sh"),
    ("p9_recovery_adapter_cloud_launch", "experiments/P9_RECOVERY_ADAPTER_CLOUD_LAUNCH_20260504_CN.md"),
    ("p9_recovery_adapter_cloud_script", "experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh"),
    ("p8_tex", "papers/P8_representation_genesis/main.tex"),
    ("p8_pdf", "papers/P8_representation_genesis/main.pdf"),
    ("p8_log", "papers/P8_representation_genesis/main.log"),
    ("p8_readme", "papers/P8_representation_genesis/README_CN.md"),
    ("p8_seed_terms_table", "papers/P8_representation_genesis/generated/macro_seed_terms_table.tex"),
    ("p8_compression_table", "papers/P8_representation_genesis/generated/representation_compression_table.tex"),
    ("p8_perspectival_grounding_table", "papers/P8_representation_genesis/generated/perspectival_grounding_table.tex"),
    ("p8_claim_registry_table", "papers/P8_representation_genesis/generated/claim_registry_table.tex"),
    ("p8_claim_registry_compact_table", "papers/P8_representation_genesis/generated/claim_registry_compact_table.tex"),
    ("p9_tex", "papers/P9_embodied_failure_immunity/main.tex"),
    ("p9_pdf", "papers/P9_embodied_failure_immunity/main.pdf"),
    ("p9_log", "papers/P9_embodied_failure_immunity/main.log"),
    ("p9_readme", "papers/P9_embodied_failure_immunity/README_CN.md"),
    ("p9_failure_classes_table", "papers/P9_embodied_failure_immunity/generated/failure_classes_table.tex"),
    ("p9_whole_organism_layers_table", "papers/P9_embodied_failure_immunity/generated/whole_organism_layers_table.tex"),
    (
        "p9_whole_organism_evidence_bridge_table",
        "papers/P9_embodied_failure_immunity/generated/whole_organism_evidence_bridge_table.tex",
    ),
    ("p9_embodied_antigen_summary_table", "papers/P9_embodied_failure_immunity/generated/embodied_antigen_summary_table.tex"),
    ("p9_recovery_adapter_pilot_plan_table", "papers/P9_embodied_failure_immunity/generated/recovery_adapter_pilot_plan_table.tex"),
    ("p9_recovery_adapter_pilot_result_table", "papers/P9_embodied_failure_immunity/generated/recovery_adapter_pilot_result_table.tex"),
    ("formal_core_tex", "papers/WISDOM_SCIENCE_FORMAL_CORE/main.tex"),
    ("formal_core_pdf", "papers/WISDOM_SCIENCE_FORMAL_CORE/main.pdf"),
    ("formal_core_log", "papers/WISDOM_SCIENCE_FORMAL_CORE/main.log"),
    ("formal_checks_table", "papers/WISDOM_SCIENCE_FORMAL_CORE/generated/formal_checks_table.tex"),
    ("physics_engineering_tex", "papers/WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE/main.tex"),
    ("physics_engineering_pdf", "papers/WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE/main.pdf"),
    ("physics_engineering_log", "papers/WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE/main.log"),
    (
        "physics_engineering_checks_table",
        "papers/WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE/generated/physics_engineering_checks_table.tex",
    ),
    ("foundation_tex", "papers/WISDOM_SCIENCE_FOUNDATION/main.tex"),
    ("foundation_pdf", "papers/WISDOM_SCIENCE_FOUNDATION/main.pdf"),
    ("foundation_log", "papers/WISDOM_SCIENCE_FOUNDATION/main.log"),
    ("api_panel_tex", "papers/WISDOM_SCIENCE_API_PANEL/main.tex"),
    ("api_panel_pdf", "papers/WISDOM_SCIENCE_API_PANEL/main.pdf"),
    ("api_panel_log", "papers/WISDOM_SCIENCE_API_PANEL/main.log"),
    ("api_panel_readme", "papers/WISDOM_SCIENCE_API_PANEL/README_CN.md"),
    ("api_panel_table", "papers/WISDOM_SCIENCE_API_PANEL/generated/api_wisdombench_panel_table.tex"),
    ("api_panel_config_template", "experiments/configs/api_wisdombench_six_model_panel.template.json"),
    ("api_panel_runner", "experiments/api_wisdombench_longitudinal_panel.py"),
    (
        "api_panel_readiness",
        "experiments/results/wisdom_science/api_wisdombench_panel/api_wisdombench_panel_readiness.json",
    ),
    ("api_panel_dryrun_raw", "experiments/results/wisdom_science/api_wisdombench_panel/dryrun_raw.jsonl"),
    (
        "api_panel_dryrun_summary_json",
        "experiments/results/wisdom_science/api_wisdombench_panel/dryrun_summary.json",
    ),
    (
        "api_panel_dryrun_summary_csv",
        "experiments/results/wisdom_science/api_wisdombench_panel/dryrun_summary.csv",
    ),
    ("api_panel_smoke_raw", "experiments/results/wisdom_science/api_wisdombench_panel/smoke6_raw.jsonl"),
    (
        "api_panel_smoke_summary_json",
        "experiments/results/wisdom_science/api_wisdombench_panel/smoke6_summary.json",
    ),
    (
        "api_panel_smoke_summary_csv",
        "experiments/results/wisdom_science/api_wisdombench_panel/smoke6_summary.csv",
    ),
    ("api_panel_pilot_raw", "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_raw.jsonl"),
    (
        "api_panel_pilot_summary_json",
        "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.json",
    ),
    (
        "api_panel_pilot_summary_csv",
        "experiments/results/wisdom_science/api_wisdombench_panel/pilot6x2x2_summary.csv",
    ),
    ("claim_registry_json", "experiments/results/wisdom_science/claim_registry_v0.json"),
    ("macro_registry_json", "experiments/results/wisdom_science/macro_registry_v0.json"),
    ("representation_compression_json", "experiments/results/wisdom_science/representation_compression_v0.json"),
    ("perspectival_grounding_json", "experiments/results/wisdom_science/perspectival_grounding_v0.json"),
    ("perspectival_grounding_md", "experiments/results/wisdom_science/perspectival_grounding_v0.md"),
    ("whole_organism_intelligence_json", "experiments/results/wisdom_science/whole_organism_intelligence_v0.json"),
    ("whole_organism_intelligence_md", "experiments/results/wisdom_science/whole_organism_intelligence_v0.md"),
    ("whole_organism_evidence_bridge_json", "experiments/results/wisdom_science/whole_organism_evidence_bridge_v0.json"),
    ("whole_organism_evidence_bridge_md", "experiments/results/wisdom_science/whole_organism_evidence_bridge_v0.md"),
    ("embodied_antigen_labels_jsonl", "experiments/results/wisdom_science/embodied_antigen_labels_v0.jsonl"),
    ("embodied_antigen_summary_json", "experiments/results/wisdom_science/embodied_antigen_summary_v0.json"),
    ("embodied_antigen_summary_md", "experiments/results/wisdom_science/embodied_antigen_summary_v0.md"),
    (
        "p9_recovery_adapter_pilot_plan_json",
        "experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.json",
    ),
    (
        "p9_recovery_adapter_pilot_plan_md",
        "experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.md",
    ),
    (
        "p9_recovery_adapter_pilot_analysis_json",
        "experiments/results/wisdom_science/p9_recovery_adapter_pilot_analysis_20260504.json",
    ),
    (
        "p9_recovery_adapter_pilot_analysis_md",
        "experiments/results/wisdom_science/p9_recovery_adapter_pilot_analysis_20260504.md",
    ),
    (
        "p9_recovery_adapter_public_factory_raw",
        "experiments/results/wbe_real/p9_recovery_adapter_public_factory_raw.jsonl",
    ),
    (
        "p9_recovery_adapter_cloud_log",
        "experiments/results/wbe_real/logs/p9_recovery_adapter_cloud_20260504_214938.log",
    ),
    (
        "p9_recovery_adapter_artifact_manifest",
        "experiments/results/wbe_real/p9_recovery_adapter_artifacts_20260504/manifest.json",
    ),
    ("formal_checks_json", "experiments/results/wisdom_science/formal_checks_v0.json"),
    ("formal_checks_md", "experiments/results/wisdom_science/formal_checks_v0.md"),
    ("physics_engineering_checks_json", "experiments/results/wisdom_science/physics_engineering_checks_v0.json"),
    ("physics_engineering_checks_md", "experiments/results/wisdom_science/physics_engineering_checks_v0.md"),
    ("tables_manifest", "experiments/results/wisdom_science/wisdom_science_tables_manifest.json"),
    ("failure_schema", "experiments/embodied_failure_atlas_schema.json"),
    ("leaderboard_schema", "experiments/wisdom_science_leaderboard_schema.json"),
    ("macro_mining_script", "experiments/wisdom_science_macro_mining.py"),
    ("claim_registry_script", "experiments/wisdom_science_claim_registry.py"),
    ("compression_script", "experiments/wisdom_science_representation_compression.py"),
    ("perspectival_grounding_script", "experiments/perspectival_grounding_lab.py"),
    ("whole_organism_intelligence_script", "experiments/whole_organism_intelligence_schema.py"),
    ("whole_organism_evidence_bridge_script", "experiments/whole_organism_evidence_bridge.py"),
    ("embodied_antigen_labeler_script", "experiments/embodied_antigen_labeler.py"),
    ("p9_recovery_adapter_pilot_plan_script", "experiments/prepare_p9_recovery_adapter_pilot.py"),
    ("p9_recovery_adapter_pilot_analysis_script", "experiments/analyze_p9_recovery_adapter_pilot.py"),
    ("formal_checks_script", "experiments/wisdom_science_formal_checks.py"),
    ("physics_engineering_checks_script", "experiments/wisdom_science_physics_engineering_checks.py"),
    ("table_generator_script", "experiments/generate_wisdom_science_tables.py"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_index() -> dict[str, object]:
    artifacts = []
    missing = []
    for role, rel in ARTIFACTS:
        path = ROOT / rel
        if not path.exists():
            missing.append({"role": role, "path": rel})
            continue
        artifacts.append(
            {
                "role": role,
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            }
        )
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(artifacts),
        "missing_count": len(missing),
        "artifacts": artifacts,
        "missing": missing,
    }


def write_markdown(index: dict[str, object]) -> None:
    lines = [
        "# Wisdom Science Evidence Index v0",
        "",
        f"Generated UTC: {index['generated_utc']}",
        f"Artifacts: {index['artifact_count']}",
        f"Missing: {index['missing_count']}",
        "",
        "| role | path | bytes | sha256 |",
        "| --- | --- | ---: | --- |",
    ]
    for item in index["artifacts"]:
        lines.append(
            f"| {item['role']} | `{item['path']}` | {item['bytes']} | `{str(item['sha256'])[:16]}...` |"
        )
    if index["missing"]:
        lines.extend(["", "## Missing", "", "| role | path |", "| --- | --- |"])
        for item in index["missing"]:
            lines.append(f"| {item['role']} | `{item['path']}` |")
    lines.append("")
    (RESULT_DIR / "evidence_index_v0.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    index = build_index()
    (RESULT_DIR / "evidence_index_v0.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(index)
    print(json.dumps({"artifacts": index["artifact_count"], "missing": index["missing_count"]}, indent=2))


if __name__ == "__main__":
    main()
