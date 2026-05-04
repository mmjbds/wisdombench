# Whole-Organism Evidence Bridge v0

Generated UTC: 2026-05-04T13:23:14.436050+00:00

## Readiness

- Current paper claims ready: `True`
- Large training required now: `False`
- Cloud required now: `False`
- Boundary: P9 is a mechanism/evidence-contract paper; new robot performance-improvement claims require adapter re-evaluation.

## Portfolio Counts

| item | count |
| --- | ---: |
| real_embodied_rows | 8076 |
| real_embodied_successes | 1820 |
| public_checkpoint_supported_rows | 540 |
| public_factory_strict_rows | 36 |
| self_trained_lowdim_rows | 6300 |
| libero_supported_rows | 1200 |
| api_panel_rows | 48 |
| perspectival_cases | 6 |
| whole_organism_layers | 9 |

## Layer Bridge

| layer | support level | direct support | boundary |
| --- | --- | --- | --- |
| brain_policy | real_rollout | 8076 embodied rows; 1820 successes | Not a 12-policy public VLA/SOTA 6,300 leaderboard. |
| senses_active_perception | toy_plus_trace_proxy | 6 perspectival cases; 9.34 bits reduced | Real rollouts store trajectories but do not yet log active view/tactile queries. |
| nervous_routing | system_artifact | routing modules plus API panel | Routing exists as a system artifact; robot-side module routing traces are not yet complete. |
| blood_metabolism | real_telemetry | 8076 rows with wall-clock telemetry | Energy and API-cost counters are not yet normalized into one cross-platform unit. |
| joints_muscles | real_trajectory_paths | 8076 rows with trajectory paths | Trajectory paths certify action traces; low-level force/contact introspection is still sparse. |
| immune_system | longitudinal_evidence | failure atlas plus repeated rounds | Existing rows support failure mining; new antibody-caused robot improvement needs re-evaluation. |
| psychological_regulation | protocol_ready | confidence gate defined | No strong claim about affective or confidence regulation improvement yet. |
| social_body | toy_plus_api_protocol | deictic/social case plus API panel | No human-subject or live institution-governance evidence is claimed. |
| game_theoretic_mind | toy_protocol | counter-reflexive toy case | No live multi-agent rollout is claimed. |

## Recommended Upgrades

| priority | name | cloud | training | description |
| ---: | --- | --- | --- | --- |
| 1 | offline_antigen_labeling | False | False | Label existing failures by organ layer, causal cue, recovery opportunity, and transfer group. |
| 2 | p8_perspectival_api_panel | False | False | Run six API models on perspectival/counter-reflexive cases with no-memory vs active-disambiguation strategies. |
| 3 | p9_recovery_adapter_re_evaluation | True | optional | Evaluate whether labeled antigens produce transferable robot improvement. Start with rule/prompt/recovery adapters before full training. |
