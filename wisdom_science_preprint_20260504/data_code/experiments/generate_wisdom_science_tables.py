"""Generate LaTeX tables for P8/P9 Wisdom Science drafts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"
P8_GEN = ROOT / "papers" / "P8_representation_genesis" / "generated"
P9_GEN = ROOT / "papers" / "P9_embodied_failure_immunity" / "generated"


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def write_seed_terms_table() -> Path:
    macro_path = RESULT_DIR / "macro_registry_v0.json"
    data = json.loads(macro_path.read_text(encoding="utf-8"))
    rows = data["seed_terms"][:12]
    lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Term & Count & Doc. freq. \\",
        r"\midrule",
    ]
    for item in rows:
        lines.append(
            f"{tex_escape(item['term'])} & {item['count']} & {item['document_frequency']} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P8_GEN / "macro_seed_terms_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_claim_registry_table() -> Path:
    claims = json.loads((RESULT_DIR / "claim_registry_v0.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.08\linewidth}p{0.46\linewidth}p{0.18\linewidth}p{0.14\linewidth}}",
        r"\toprule",
        r"ID & Claim & Evidence & Strength \\",
        r"\midrule",
    ]
    for item in claims:
        lines.append(
            f"{tex_escape(item['id'])} & {tex_escape(item['claim'])} & "
            f"{tex_escape(item['evidence'])} & {tex_escape(item['strength'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P8_GEN / "claim_registry_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_claim_registry_compact_table() -> Path:
    claims = json.loads((RESULT_DIR / "claim_registry_v0.json").read_text(encoding="utf-8"))
    object_short = {
        "I vs WQ": "I/WQ",
        "WQ": "WQ",
        "Intelligence-Wisdom Gap": "IWG",
        "W ~ Phi^alpha Psi^beta H^gamma |E|^delta": "SSL",
        "Cognitive Immunity": "CI",
        "I_E, EWQ": "I_E/EWQ",
        "Phi_E, Psi_E, H_E": "Phi_E/Psi_E/H_E",
        "raw logs, trajectories, provenance": "Gate",
        "Representation Genesis": "RG",
        "Embodied Failure Immunity": "EFI",
        "Perspectival Grounding": "PG",
        "Whole-Organism Intelligence": "WOI",
    }
    evidence_short = {
        "P0/P3 definitions": "P0/P3",
        "P1 longitudinal benchmark": "P1",
        "P2/P4/P5-P7 comparisons": "P2/P4-P7",
        "P4 formal law": "P4",
        "P2/P5-P7 failure adaptation": "P2/P5-P7",
        "P5/P6 embodied metrics": "P5/P6",
        "P5/P6 ablations": "P5/P6",
        "WB-E strict gate": "WB-E gate",
        "P8 macro mining/toy search": "P8",
        "P9 failure atlas": "P9",
        "P8 toy lab": "P8",
        "P9 schema": "P9",
    }
    lines = [
        r"\begin{tabular}{lll}",
        r"\toprule",
        r"ID & Object & Evidence \\",
        r"\midrule",
    ]
    for item in claims[:8]:
        lines.append(
            f"{tex_escape(item['id'])} & {tex_escape(object_short.get(item['object'], item['object']))} & "
            f"{tex_escape(evidence_short.get(item['evidence'], item['evidence']))} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P8_GEN / "claim_registry_compact_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_perspectival_grounding_table() -> Path:
    data = json.loads((RESULT_DIR / "perspectival_grounding_v0.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.25\linewidth}p{0.15\linewidth}rrrr}",
        r"\toprule",
        r"Case & Domain & $|\mathcal{H}_0|$ & $H_0$ & Drop & Cost \\",
        r"\midrule",
    ]
    for item in data["case_results"]:
        lines.append(
            f"{tex_escape(item['case_id'].replace('_', ' '))} & {tex_escape(item['domain'])} & "
            f"{item['initial_hypothesis_count']} & {item['initial_entropy_bits']:.2f} & "
            f"{item['ambiguity_reduction_bits']:.2f} & {item['total_disambiguation_cost']:.1f} \\\\"
        )
    agg = data["aggregate"]
    lines.extend(
        [
            r"\midrule",
            f"Mean & -- & -- & {agg['mean_initial_entropy_bits']:.2f} & "
            f"{(agg['mean_initial_entropy_bits'] - agg['mean_final_entropy_bits']):.2f} & -- \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    )
    path = P8_GEN / "perspectival_grounding_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def pretty_failure_class(name: str) -> str:
    return name.replace("_", " ").title()


def write_failure_classes_table() -> Path:
    schema = json.loads((ROOT / "experiments" / "embodied_failure_atlas_schema.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.38\linewidth}p{0.52\linewidth}}",
        r"\toprule",
        r"Failure class & Typical antigen cue \\",
        r"\midrule",
    ]
    cues = {
        "grasp_contact_failure": "missed contact, slip, unstable grasp, collision",
        "placement_spatial_failure": "wrong pose, wrong target, failed insertion",
        "occlusion_visual_grounding_failure": "object hidden, visual aliasing, distractor",
        "perspectival_aliasing_failure": "one projection supports multiple latent states",
        "active_disambiguation_failure": "agent fails to gather next view, touch, or context",
        "instruction_grounding_failure": "wrong object, wrong relation, semantic ambiguity",
        "perturbation_fragility": "lighting, friction, position, or dynamics shift",
        "sensor_pipeline_failure": "sensor stream missing, stale, misrouted, or uncalibrated",
        "actuator_joint_instability": "unstable joint, slip, saturation, or controller lag",
        "metabolic_budget_failure": "battery, latency, GPU, API, or memory budget exhausted",
        "psychological_calibration_failure": "overconfidence, panic loop, refusal collapse",
        "social_norm_grounding_failure": "physical success violates role, norm, or trust boundary",
        "counter_reflexive_game_failure": "missed bluff, feint, recursive belief, or opponent adaptation",
        "recovery_loop_failure": "repeated retry without new recovery behavior",
        "simulator_or_provenance_failure": "missing trajectory, checkpoint, metadata, or seed",
        "unknown": "insufficient evidence for classification",
    }
    for failure_class in schema["failure_classes"]:
        lines.append(
            f"{tex_escape(pretty_failure_class(failure_class))} & "
            f"{tex_escape(cues.get(failure_class, 'to be specified'))} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P9_GEN / "failure_classes_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_whole_organism_table() -> Path:
    data = json.loads((RESULT_DIR / "whole_organism_intelligence_v0.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.18\linewidth}p{0.34\linewidth}p{0.38\linewidth}}",
        r"\toprule",
        r"Layer & Organ analogy & Engineering gate \\",
        r"\midrule",
    ]
    for item in data["layers"]:
        lines.append(
            f"{tex_escape(item['layer_id'].replace('_', ' '))} & "
            f"{tex_escape(item['biological_analogy'])} & "
            f"{tex_escape(item['engineering_substrate'])}; gate: "
            f"{tex_escape(item['evidence_gate'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P9_GEN / "whole_organism_layers_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_whole_organism_evidence_bridge_table() -> Path:
    data = json.loads((RESULT_DIR / "whole_organism_evidence_bridge_v0.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.15\linewidth}p{0.14\linewidth}p{0.28\linewidth}p{0.27\linewidth}}",
        r"\toprule",
        r"Layer & Status & Direct support & Boundary \\",
        r"\midrule",
    ]
    for item in data["layer_bridge"]:
        lines.append(
            f"{tex_escape(item['layer_id'].replace('_', ' '))} & "
            f"{tex_escape(item['support_level'].replace('_', ' '))} & "
            f"{tex_escape(item['table_support'])} & "
            f"{tex_escape(item['current_boundary'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P9_GEN / "whole_organism_evidence_bridge_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_embodied_antigen_summary_table() -> Path:
    data = json.loads((RESULT_DIR / "embodied_antigen_summary_v0.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.28\linewidth}rrp{0.32\linewidth}}",
        r"\toprule",
        r"Failure class & Count & Share & Recovery opportunity \\",
        r"\midrule",
    ]
    for item in data["by_failure_class"][:8]:
        lines.append(
            f"{tex_escape(item['failure_class'].replace('_', ' '))} & "
            f"{item['count']} & {item['share']:.3f} & "
            f"{tex_escape(item['recovery_opportunity'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path = P9_GEN / "embodied_antigen_summary_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_recovery_adapter_plan_table() -> Path:
    data = json.loads((RESULT_DIR / "p9_recovery_adapter_pilot_plan_20260504.json").read_text(encoding="utf-8"))
    lines = [
        r"\begin{tabular}{p{0.22\linewidth}p{0.22\linewidth}rrp{0.24\linewidth}}",
        r"\toprule",
        r"Agent & Profile & Tasks & Cells & Failure classes \\",
        r"\midrule",
    ]
    for item in data["agent_plans"]:
        lines.append(
            f"{tex_escape(item['agent_id'])} & {tex_escape(item['profile'])} & "
            f"{len(item['task_ids'])} & {item['baseline_failure_cells']} & "
            f"{tex_escape(', '.join(item['failure_classes']).replace('_', ' '))} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            f"Expected & {tex_escape(data['minimum_gpu'])} & -- & -- & "
            f"{tex_escape(str(data['expected_wall_time_minutes']) + ' min, no training')} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    )
    path = P9_GEN / "recovery_adapter_pilot_plan_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_recovery_adapter_result_table() -> Path:
    data = json.loads((RESULT_DIR / "p9_recovery_adapter_pilot_analysis_20260504.json").read_text(encoding="utf-8"))
    by_agent: dict[str, dict[str, object]] = {}
    for item in data["matched"]:
        agent = item["agent_id"]
        bucket = by_agent.setdefault(agent, {"cells": 0, "rescued": 0, "tasks": []})
        bucket["cells"] = int(bucket["cells"]) + 1
        if item["adapter_success"] and not item["baseline_success"]:
            bucket["rescued"] = int(bucket["rescued"]) + 1
            bucket["tasks"].append(item["task_id"])
    lines = [
        r"\begin{tabular}{p{0.26\linewidth}rrrp{0.28\linewidth}}",
        r"\toprule",
        r"Agent & Matched & Rescued & Rate & Rescued tasks \\",
        r"\midrule",
    ]
    for agent, bucket in sorted(by_agent.items()):
        cells = int(bucket["cells"])
        rescued = int(bucket["rescued"])
        rate = rescued / cells if cells else 0.0
        tasks = ", ".join(bucket["tasks"]) if bucket["tasks"] else "--"
        lines.append(
            f"{tex_escape(agent)} & {cells} & {rescued} & {rate:.3f} & {tex_escape(tasks)} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            f"Overall & {data['matched_cells']} & {data['rescued_failures']} & "
            f"{float(data['baseline_failure_rescue_rate'] or 0):.3f} & "
            f"{tex_escape('regressions=' + str(data['regressions']) + ', claim_ready=' + str(data['claim_ready']).lower())} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    )
    path = P9_GEN / "recovery_adapter_pilot_result_table.tex"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_manifest(paths: list[Path]) -> None:
    compression_table = P8_GEN / "representation_compression_table.tex"
    if compression_table.exists() and compression_table not in paths:
        paths = [compression_table, *paths]
    manifest = {
        "generated_files": [str(path.relative_to(ROOT)) for path in paths],
        "source_files": [
            str((RESULT_DIR / "macro_registry_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "claim_registry_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "representation_compression_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "perspectival_grounding_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "whole_organism_intelligence_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "whole_organism_evidence_bridge_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "embodied_antigen_summary_v0.json").relative_to(ROOT)),
            str((RESULT_DIR / "p9_recovery_adapter_pilot_plan_20260504.json").relative_to(ROOT)),
            str((RESULT_DIR / "p9_recovery_adapter_pilot_analysis_20260504.json").relative_to(ROOT)),
            "experiments/embodied_failure_atlas_schema.json",
        ],
    }
    (RESULT_DIR / "wisdom_science_tables_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    P8_GEN.mkdir(parents=True, exist_ok=True)
    P9_GEN.mkdir(parents=True, exist_ok=True)
    paths = [
        write_seed_terms_table(),
        write_claim_registry_table(),
        write_claim_registry_compact_table(),
        write_perspectival_grounding_table(),
        write_failure_classes_table(),
        write_whole_organism_table(),
        write_whole_organism_evidence_bridge_table(),
        write_embodied_antigen_summary_table(),
        write_recovery_adapter_plan_table(),
        write_recovery_adapter_result_table(),
    ]
    write_manifest(paths)
    for path in paths:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
