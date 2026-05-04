"""Export the Wisdom Science claim registry to machine-readable artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"


CLAIMS = [
    {
        "id": "C1",
        "claim": "Wisdom should be distinguished from first-round intelligence.",
        "object": "I vs WQ",
        "evidence": "P2, P3",
        "strength": "strong",
        "limitation": "WQ measures observable cross-round improvement, not philosophical wisdom.",
    },
    {
        "id": "C2",
        "claim": "Wisdom can be operationalized as normalized cross-round learning gain.",
        "object": "WQ",
        "evidence": "P1, P2",
        "strength": "strong",
        "limitation": "Ceiling tasks must be handled explicitly.",
    },
    {
        "id": "C3",
        "claim": "Higher first-round intelligence does not guarantee higher wisdom.",
        "object": "Intelligence-Wisdom Gap",
        "evidence": "P3, P4",
        "strength": "medium-strong",
        "limitation": "Current evidence is limited to a finite model/strategy panel.",
    },
    {
        "id": "C4",
        "claim": "Wisdom scales with architectural qualities and experience, not only parameters.",
        "object": "W ~ Phi^alpha Psi^beta H^gamma |E|^delta",
        "evidence": "P4",
        "strength": "medium",
        "limitation": "Exponent universality requires larger architecture sweeps.",
    },
    {
        "id": "C5",
        "claim": "Failures can be converted into transferable immunity signals.",
        "object": "Cognitive Immunity",
        "evidence": "P1",
        "strength": "medium-strong",
        "limitation": "Must separate transfer from memorization.",
    },
    {
        "id": "C6",
        "claim": "Embodied agents should report longitudinal learning ability.",
        "object": "I_E, EWQ",
        "evidence": "P5, P6, P7",
        "strength": "strong",
        "limitation": "Real rollout claims require complete provenance.",
    },
    {
        "id": "C7",
        "claim": "Robot learning ability can be described by embodied plasticity, immunity, and homeostasis.",
        "object": "Phi_E, Psi_E, H_E",
        "evidence": "P5, P6",
        "strength": "medium",
        "limitation": "Current evidence is not yet a full multi-architecture exponent fit.",
    },
    {
        "id": "C8",
        "claim": "Evidence gates are necessary for embodied wisdom claims.",
        "object": "raw logs, trajectories, provenance",
        "evidence": "P7",
        "strength": "strong",
        "limitation": "Evidence gates do not replace policy capability.",
    },
    {
        "id": "C9",
        "claim": "Representation search is the next layer of wisdom-oriented systems.",
        "object": "Representation Genesis",
        "evidence": "P8 draft",
        "strength": "new",
        "limitation": "Needs toy-to-real evidence.",
    },
    {
        "id": "C10",
        "claim": "Embodied failure trajectories can become transferable antigens.",
        "object": "Embodied Failure Immunity",
        "evidence": "P9 draft",
        "strength": "new",
        "limitation": "Needs real or strict supported-set re-evaluation.",
    },
    {
        "id": "C11",
        "claim": "A single observation should be treated as a projection rather than the latent world.",
        "object": "Perspectival Grounding",
        "evidence": "P8 toy lab",
        "strength": "new",
        "limitation": "Toy cases must be extended to multimodal perception and social-game logs.",
    },
    {
        "id": "C12",
        "claim": "Embodied wisdom is distributed across organ-like subsystems, not only a brain policy.",
        "object": "Whole-Organism Intelligence",
        "evidence": "P9 schema",
        "strength": "new",
        "limitation": "A systems evidence contract, not an exhaustive biological theory.",
    },
]


def write_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CLAIMS[0].keys()))
        writer.writeheader()
        writer.writerows(CLAIMS)


def write_markdown(path: Path) -> None:
    headers = list(CLAIMS[0].keys())
    lines = [
        "# Wisdom Science Claim Registry v0",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for claim in CLAIMS:
        lines.append("| " + " | ".join(str(claim[h]).replace("|", "/") for h in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "claim_registry_v0.json").write_text(
        json.dumps(CLAIMS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(RESULT_DIR / "claim_registry_v0.csv")
    write_markdown(RESULT_DIR / "claim_registry_v0.md")
    print(f"wrote {len(CLAIMS)} claims to {RESULT_DIR}")


if __name__ == "__main__":
    main()
