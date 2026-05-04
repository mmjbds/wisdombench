"""Generate the Whole-Organism Intelligence schema.

The schema makes a deliberately non-brain-centric embodied-AI claim auditable:
robot intelligence is distributed across sensing, routing, metabolism/cost,
actuation, immunity, psychological regulation, and social grounding.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"


LAYERS: list[dict[str, Any]] = [
    {
        "layer_id": "brain_policy",
        "biological_analogy": "brain",
        "engineering_substrate": "VLA policy, planner, world model, reasoning loop",
        "typical_failure": "brain-centric overcommitment without enough sensory or provenance evidence",
        "evidence_gate": "checkpoint identity, prompt/action trace, policy version, decision log",
        "wisdom_metric": "I_E / EWQ / WQ",
    },
    {
        "layer_id": "senses_active_perception",
        "biological_analogy": "eyes, touch, proprioception, hearing",
        "engineering_substrate": "camera views, tactile probes, proprioceptive state, language input",
        "typical_failure": "single-view aliasing, occlusion, symbol ambiguity, missing context",
        "evidence_gate": "sensor coverage, active-view trace, ambiguity set, observation hashes",
        "wisdom_metric": "perspectival entropy reduction",
    },
    {
        "layer_id": "nervous_routing",
        "biological_analogy": "nerves and meridians",
        "engineering_substrate": "message passing, context routing, control pipeline, attention budget",
        "typical_failure": "dropped signals, stale context, wrong module receives the evidence",
        "evidence_gate": "timestamped pipeline trace, routing decision, context budget log",
        "wisdom_metric": "routing recall and latency",
    },
    {
        "layer_id": "blood_metabolism",
        "biological_analogy": "blood, energy, metabolism",
        "engineering_substrate": "GPU budget, battery, latency, memory, API spend, data flow",
        "typical_failure": "apparently wise behavior that is too slow, too costly, or unsustainable",
        "evidence_gate": "wall-clock, GPU, energy, API, memory, and storage telemetry",
        "wisdom_metric": "wisdom efficiency per unit cost",
    },
    {
        "layer_id": "joints_muscles",
        "biological_analogy": "joints, muscles, reflex arcs",
        "engineering_substrate": "controllers, action primitives, skill APIs, low-level servo loops",
        "typical_failure": "valid plan with unstable execution, joint-limit collision, slip, or latency",
        "evidence_gate": "action trace, joint state, contact state, controller version, recovery trace",
        "wisdom_metric": "trajectory stability / Phi_E",
    },
    {
        "layer_id": "immune_system",
        "biological_analogy": "immune memory",
        "engineering_substrate": "failure atlas, antigens, antibodies, recovery adapters",
        "typical_failure": "same failure repeats because no transferable antibody was retained",
        "evidence_gate": "antigen ID, antibody payload, activation condition, transfer result",
        "wisdom_metric": "repeat-failure reduction / Psi_E",
    },
    {
        "layer_id": "psychological_regulation",
        "biological_analogy": "confidence, affect, attention, self-regulation",
        "engineering_substrate": "uncertainty calibration, refusal threshold, evidence pressure, attention control",
        "typical_failure": "overconfidence, panic loops, refusal collapse, or hallucinated certainty",
        "evidence_gate": "confidence trace, uncertainty estimate, evidence-pressure record, intervention log",
        "wisdom_metric": "calibration and homeostasis H_E",
    },
    {
        "layer_id": "social_body",
        "biological_analogy": "social norms, roles, institutions",
        "engineering_substrate": "human feedback, role constraints, team protocols, norm memory",
        "typical_failure": "instruction succeeds physically but violates role, norm, consent, or trust boundary",
        "evidence_gate": "human instruction log, norm check, role state, approval or override provenance",
        "wisdom_metric": "social grounding robustness",
    },
    {
        "layer_id": "game_theoretic_mind",
        "biological_analogy": "theory of mind and strategic social cognition",
        "engineering_substrate": "opponent model, recursive belief model, commitment detector, multi-agent debate",
        "typical_failure": "agent treats a strategic signal as literal and misses bluff, feint, or reflexive adaptation",
        "evidence_gate": "payoff model, belief-depth trace, opponent-action log, commitment evidence",
        "wisdom_metric": "counter-reflexive regret reduction",
    },
]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Whole-Organism Intelligence Schema v0",
        "",
        f"Generated UTC: {payload['generated_utc']}",
        "",
        "| layer | biological analogy | engineering substrate | evidence gate |",
        "| --- | --- | --- | --- |",
    ]
    for item in payload["layers"]:
        lines.append(
            f"| {item['layer_id']} | {item['biological_analogy']} | "
            f"{item['engineering_substrate']} | {item['evidence_gate']} |"
        )
    lines.append("")
    (RESULT_DIR / "whole_organism_intelligence_v0.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "whole_organism_intelligence_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "definition": "Embodied intelligence is a whole-organism property distributed across policy, sensors, routing, metabolism, action, immunity, psychological regulation, and social grounding.",
        "layer_count": len(LAYERS),
        "layers": LAYERS,
    }
    (RESULT_DIR / "whole_organism_intelligence_v0.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(payload)
    print(json.dumps({"layer_count": len(LAYERS)}, indent=2))


if __name__ == "__main__":
    main()
