# Embodied Antigen Labels v0

Generated UTC: 2026-05-04T14:29:39.786116+00:00
Antigens: 6256
Failure classes: 7

Boundary: offline labels over existing failures only; no robot improvement is claimed.

## Failure Classes

| failure class | count | share | top policies | recovery opportunity |
| --- | ---: | ---: | --- | --- |
| unknown | 2063 | 0.330 | bc_mlp_large_s1:180, bc_ridge_l2_1e4:180, bc_ridge_l2_1e2:180, bc_mlp_small_s3:179 | preserve failure for human review; do not infer unsupported mechanism |
| placement_spatial_failure | 2012 | 0.322 | bc_mlp_small_s2:165, bc_mlp_base_s1:165, bc_mlp_base_s3:165, bc_ridge_l2_1e4:165 | add target-frame verification, insertion clearance, and final pose correction |
| instruction_grounding_failure | 812 | 0.130 | peract_600k_seed0:67, bc_mlp_small_s1:60, bc_mlp_small_s2:60, bc_mlp_small_s3:60 | bind object, relation, and target slot before action selection |
| actuator_joint_instability | 692 | 0.111 | bc_mlp_small_s1:60, bc_mlp_small_s2:60, bc_mlp_base_s1:60, bc_mlp_base_s2:60 | increase step budget, smooth motion, and add joint-limit/contact checks |
| grasp_contact_failure | 669 | 0.107 | bc_mlp_small_s1:60, bc_mlp_small_s2:60, bc_mlp_small_s3:60, bc_mlp_base_s1:60 | retry with slower approach, contact verification, and post-grasp lift check |
| recovery_loop_failure | 6 | 0.001 | act3d_peract:5, diffuser_actor_peract:1 | do not repeat the same failed recovery without new sensory evidence |
| simulator_or_provenance_failure | 2 | 0.000 | act3d_peract:1, diffuser_actor_peract:1 | repair missing trajectory, checkpoint, metadata, or simulator state before scoring |

## Sources

| path | rows | failures | antigens |
| --- | ---: | ---: | ---: |
| `experiments/results/wbe_real/p5_p6_lowdim_rlbench_6300_raw.jsonl` | 6300 | 5927 | 5927 |
| `experiments/results/wbe_real/p5_p6_rvt2_supported_raw.jsonl` | 270 | 85 | 85 |
| `experiments/results/wbe_real/p5_p6_peract_official_supported_raw.jsonl` | 270 | 212 | 212 |
| `experiments/results/wbe_real/p5_p6_act3d_strict_mini18_raw.jsonl` | 18 | 6 | 6 |
| `experiments/results/wbe_real/p5_p6_diffuser_strict_mini18_raw.jsonl` | 18 | 2 | 2 |
| `experiments/results/wbe_real/p7_libero_raw.jsonl` | 1200 | 24 | 24 |
