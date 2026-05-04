"""Toy perspectival-grounding lab for Representation Genesis.

The lab models a simple but important failure mode: one observation can be a
projection of several possible latent states. A wiser representation keeps the
hypothesis set open and chooses the next view/action that reduces ambiguity per
unit cost.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "experiments" / "results" / "wisdom_science"


@dataclass(frozen=True)
class View:
    view_id: str
    cost: float
    description: str


def entropy(count: int) -> float:
    if count <= 1:
        return 0.0
    return math.log2(count)


def compatible_hypotheses(case: dict[str, Any], observed_views: list[str]) -> list[dict[str, Any]]:
    truth = next(item for item in case["hypotheses"] if item["id"] == case["truth"])
    truth_obs = truth["observations"]
    compatible = []
    for hypothesis in case["hypotheses"]:
        observations = hypothesis["observations"]
        if all(observations.get(view_id) == truth_obs.get(view_id) for view_id in observed_views):
            compatible.append(hypothesis)
    return compatible


def choose_next_view(case: dict[str, Any], observed_views: list[str]) -> tuple[str | None, float]:
    current_count = len(compatible_hypotheses(case, observed_views))
    current_entropy = entropy(current_count)
    best_view = None
    best_efficiency = 0.0
    for view in case["views"]:
        view_id = view["view_id"]
        if view_id in observed_views:
            continue
        next_count = len(compatible_hypotheses(case, [*observed_views, view_id]))
        gain = current_entropy - entropy(next_count)
        efficiency = gain / max(float(view["cost"]), 1e-9)
        if efficiency > best_efficiency:
            best_view = view_id
            best_efficiency = efficiency
    return best_view, best_efficiency


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    observed_views = [case["initial_view"]]
    initial_count = len(compatible_hypotheses(case, observed_views))
    initial_entropy = entropy(initial_count)
    selected = []
    total_cost = 0.0

    while len(compatible_hypotheses(case, observed_views)) > 1:
        next_view, efficiency = choose_next_view(case, observed_views)
        if next_view is None:
            break
        view = next(item for item in case["views"] if item["view_id"] == next_view)
        observed_views.append(next_view)
        total_cost += float(view["cost"])
        selected.append(
            {
                "view_id": next_view,
                "description": view["description"],
                "cost": view["cost"],
                "information_gain_per_cost": efficiency,
                "remaining_hypotheses": len(compatible_hypotheses(case, observed_views)),
            }
        )

    final_count = len(compatible_hypotheses(case, observed_views))
    final_entropy = entropy(final_count)
    return {
        "case_id": case["case_id"],
        "domain": case["domain"],
        "phenomenon": case["phenomenon"],
        "truth": case["truth"],
        "initial_view": case["initial_view"],
        "initial_hypothesis_count": initial_count,
        "initial_entropy_bits": round(initial_entropy, 4),
        "naive_collapse_risk": round((initial_count - 1) / initial_count, 4) if initial_count else 0.0,
        "selected_views": selected,
        "total_disambiguation_cost": round(total_cost, 4),
        "final_hypothesis_count": final_count,
        "final_entropy_bits": round(final_entropy, 4),
        "ambiguity_reduction_bits": round(initial_entropy - final_entropy, 4),
        "resolved": final_count == 1,
    }


def cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "rotated_16_91",
            "domain": "glyph",
            "phenomenon": "A glyph that looks like 16 can also be a rotated 91 or a different writing system cue.",
            "truth": "sixteen_upright",
            "initial_view": "glyph_only",
            "views": [
                {"view_id": "glyph_only", "cost": 0.0, "description": "single cropped glyph"},
                {"view_id": "baseline_marker", "cost": 1.0, "description": "text baseline and page orientation"},
                {"view_id": "neighbor_context", "cost": 1.5, "description": "adjacent symbols and script context"},
                {"view_id": "rotate_90", "cost": 1.0, "description": "side view / 90-degree rotation"},
            ],
            "hypotheses": [
                {
                    "id": "sixteen_upright",
                    "observations": {
                        "glyph_only": "16",
                        "baseline_marker": "upright_baseline",
                        "neighbor_context": "arabic_number_context",
                        "rotate_90": "sideways_digits",
                    },
                },
                {
                    "id": "ninetyone_rotated",
                    "observations": {
                        "glyph_only": "16",
                        "baseline_marker": "inverted_baseline",
                        "neighbor_context": "arabic_number_context",
                        "rotate_90": "sideways_digits",
                    },
                },
                {
                    "id": "nonlatin_symbol",
                    "observations": {
                        "glyph_only": "16",
                        "baseline_marker": "no_digit_baseline",
                        "neighbor_context": "nonlatin_script_context",
                        "rotate_90": "syllable_like_shape",
                    },
                },
            ],
        },
        {
            "case_id": "six_nine_orientation",
            "domain": "glyph",
            "phenomenon": "A 6/9-like mark cannot be grounded without orientation evidence.",
            "truth": "six",
            "initial_view": "isolated_mark",
            "views": [
                {"view_id": "isolated_mark", "cost": 0.0, "description": "isolated mark"},
                {"view_id": "page_arrow", "cost": 0.5, "description": "orientation arrow or gravity cue"},
                {"view_id": "neighbor_number", "cost": 1.0, "description": "neighboring ordered number"},
            ],
            "hypotheses": [
                {
                    "id": "six",
                    "observations": {
                        "isolated_mark": "loop_with_tail",
                        "page_arrow": "tail_down",
                        "neighbor_number": "5_6_7",
                    },
                },
                {
                    "id": "nine",
                    "observations": {
                        "isolated_mark": "loop_with_tail",
                        "page_arrow": "tail_up",
                        "neighbor_number": "8_9_10",
                    },
                },
            ],
        },
        {
            "case_id": "polysemous_chinese_xing",
            "domain": "language",
            "phenomenon": "The Chinese character xing carries multiple senses until collocation and discourse context are observed.",
            "truth": "bank_sense",
            "initial_view": "character_only",
            "views": [
                {"view_id": "character_only", "cost": 0.0, "description": "single character"},
                {"view_id": "left_neighbor", "cost": 0.5, "description": "previous character"},
                {"view_id": "sentence_goal", "cost": 1.0, "description": "sentence-level goal"},
                {"view_id": "speaker_intent", "cost": 1.5, "description": "speaker intent"},
            ],
            "hypotheses": [
                {
                    "id": "walk_sense",
                    "observations": {
                        "character_only": "xing",
                        "left_neighbor": "bu",
                        "sentence_goal": "movement",
                        "speaker_intent": "action_instruction",
                    },
                },
                {
                    "id": "line_sense",
                    "observations": {
                        "character_only": "xing",
                        "left_neighbor": "yi",
                        "sentence_goal": "ordering",
                        "speaker_intent": "layout_instruction",
                    },
                },
                {
                    "id": "bank_sense",
                    "observations": {
                        "character_only": "xing",
                        "left_neighbor": "yin",
                        "sentence_goal": "finance",
                        "speaker_intent": "transaction",
                    },
                },
                {
                    "id": "profession_sense",
                    "observations": {
                        "character_only": "xing",
                        "left_neighbor": "hang",
                        "sentence_goal": "industry",
                        "speaker_intent": "classification",
                    },
                },
            ],
        },
        {
            "case_id": "occluded_mug_can_bowl",
            "domain": "robotics",
            "phenomenon": "A front silhouette under occlusion aliases several manipulation affordances.",
            "truth": "mug_with_hidden_handle",
            "initial_view": "front_silhouette",
            "views": [
                {"view_id": "front_silhouette", "cost": 0.0, "description": "front RGB crop"},
                {"view_id": "side_view", "cost": 1.5, "description": "side camera movement"},
                {"view_id": "top_view", "cost": 1.2, "description": "top-down view"},
                {"view_id": "tactile_probe", "cost": 2.0, "description": "low-force contact probe"},
            ],
            "hypotheses": [
                {
                    "id": "mug_with_hidden_handle",
                    "observations": {
                        "front_silhouette": "vertical_cylinder",
                        "side_view": "handle_visible",
                        "top_view": "open_cavity",
                        "tactile_probe": "handle_contact",
                    },
                },
                {
                    "id": "can",
                    "observations": {
                        "front_silhouette": "vertical_cylinder",
                        "side_view": "no_handle",
                        "top_view": "closed_top",
                        "tactile_probe": "smooth_wall",
                    },
                },
                {
                    "id": "bowl",
                    "observations": {
                        "front_silhouette": "vertical_cylinder",
                        "side_view": "wide_rim",
                        "top_view": "open_cavity",
                        "tactile_probe": "rim_contact",
                    },
                },
            ],
        },
        {
            "case_id": "deictic_instruction",
            "domain": "social_robotics",
            "phenomenon": "The command 'put it there' is unresolved without gaze, pointing, history, and norm context.",
            "truth": "red_block_to_tray",
            "initial_view": "utterance_only",
            "views": [
                {"view_id": "utterance_only", "cost": 0.0, "description": "raw utterance"},
                {"view_id": "speaker_gaze", "cost": 0.8, "description": "gaze direction"},
                {"view_id": "pointing_vector", "cost": 0.8, "description": "hand pointing vector"},
                {"view_id": "task_history", "cost": 1.0, "description": "dialogue and task history"},
                {"view_id": "social_norm", "cost": 1.2, "description": "role and safety norm"},
            ],
            "hypotheses": [
                {
                    "id": "red_block_to_tray",
                    "observations": {
                        "utterance_only": "put_it_there",
                        "speaker_gaze": "red_block",
                        "pointing_vector": "tray",
                        "task_history": "sorting_blocks",
                        "social_norm": "allowed",
                    },
                },
                {
                    "id": "blue_cup_to_shelf",
                    "observations": {
                        "utterance_only": "put_it_there",
                        "speaker_gaze": "blue_cup",
                        "pointing_vector": "shelf",
                        "task_history": "clearing_table",
                        "social_norm": "allowed",
                    },
                },
                {
                    "id": "knife_to_human",
                    "observations": {
                        "utterance_only": "put_it_there",
                        "speaker_gaze": "knife",
                        "pointing_vector": "human_hand",
                        "task_history": "handover",
                        "social_norm": "blocked",
                    },
                },
            ],
        },
        {
            "case_id": "counter_reflexive_game",
            "domain": "social_game",
            "phenomenon": "An agent observes a signal, predicts that another agent observes its prediction, and must avoid collapsing a recursive game into a single literal reading.",
            "truth": "second_order_feint",
            "initial_view": "surface_signal",
            "views": [
                {"view_id": "surface_signal", "cost": 0.0, "description": "announced action or visible cue"},
                {"view_id": "opponent_incentive", "cost": 1.0, "description": "payoff and incentive model"},
                {"view_id": "belief_model", "cost": 1.5, "description": "what the opponent believes the agent will infer"},
                {"view_id": "commitment_trace", "cost": 1.2, "description": "costly commitment or cheap-talk evidence"},
            ],
            "hypotheses": [
                {
                    "id": "literal_signal",
                    "observations": {
                        "surface_signal": "move_A_announced",
                        "opponent_incentive": "move_A_payoff_high",
                        "belief_model": "opponent_expects_literal_acceptance",
                        "commitment_trace": "costly_commitment_to_A",
                    },
                },
                {
                    "id": "first_order_bluff",
                    "observations": {
                        "surface_signal": "move_A_announced",
                        "opponent_incentive": "move_B_payoff_high",
                        "belief_model": "opponent_expects_suspicion",
                        "commitment_trace": "cheap_talk_only",
                    },
                },
                {
                    "id": "second_order_feint",
                    "observations": {
                        "surface_signal": "move_A_announced",
                        "opponent_incentive": "move_A_payoff_high",
                        "belief_model": "opponent_expects_agent_to_call_bluff",
                        "commitment_trace": "partial_costly_commitment",
                    },
                },
            ],
        },
    ]


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Perspectival Grounding Lab v0",
        "",
        f"Generated UTC: {payload['generated_utc']}",
        "",
        "| case | domain | initial hypotheses | first selected view | entropy drop | resolved |",
        "| --- | --- | ---: | --- | ---: | --- |",
    ]
    for item in payload["case_results"]:
        first = item["selected_views"][0]["view_id"] if item["selected_views"] else "none"
        lines.append(
            f"| {item['case_id']} | {item['domain']} | {item['initial_hypothesis_count']} | "
            f"{first} | {item['ambiguity_reduction_bits']} | {item['resolved']} |"
        )
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- Cases: {payload['aggregate']['case_count']}",
            f"- Mean initial entropy: {payload['aggregate']['mean_initial_entropy_bits']}",
            f"- Mean final entropy: {payload['aggregate']['mean_final_entropy_bits']}",
            f"- Mean naive collapse risk: {payload['aggregate']['mean_naive_collapse_risk']}",
            f"- All resolved: {payload['aggregate']['all_resolved']}",
            "",
        ]
    )
    (RESULT_DIR / "perspectival_grounding_v0.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    case_results = [run_case(case) for case in cases()]
    aggregate = {
        "case_count": len(case_results),
        "mean_initial_entropy_bits": round(
            sum(item["initial_entropy_bits"] for item in case_results) / len(case_results),
            4,
        ),
        "mean_final_entropy_bits": round(
            sum(item["final_entropy_bits"] for item in case_results) / len(case_results),
            4,
        ),
        "total_ambiguity_reduction_bits": round(
            sum(item["ambiguity_reduction_bits"] for item in case_results),
            4,
        ),
        "mean_naive_collapse_risk": round(
            sum(item["naive_collapse_risk"] for item in case_results) / len(case_results),
            4,
        ),
        "all_resolved": all(item["resolved"] for item in case_results),
    }
    payload = {
        "schema": "perspectival_grounding_lab_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "definition": "An observation is a projection; wisdom requires preserving hypotheses and selecting evidence-gathering views that reduce ambiguity.",
        "case_results": case_results,
        "aggregate": aggregate,
    }
    (RESULT_DIR / "perspectival_grounding_v0.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(payload)
    print(json.dumps(aggregate, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
