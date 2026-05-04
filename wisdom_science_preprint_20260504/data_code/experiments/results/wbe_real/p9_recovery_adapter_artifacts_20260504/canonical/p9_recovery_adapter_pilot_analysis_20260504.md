# P9 Recovery Adapter Pilot Analysis

Generated UTC: 2026-05-04T14:29:39.451809+00:00
Adapter raw exists: `True`
Matched cells: 8
Matched baseline failures: 8
Rescued failures: 3
Regressions: 0
Baseline failure rescue rate: 0.375

Boundary: If rescued_failures > 0, this supports a small matched recovery-adapter pilot, not a full public leaderboard or trained-policy claim.

| agent | task | seed | round | baseline | adapter |
| --- | --- | ---: | ---: | --- | --- |
| act3d_peract | insert_onto_square_peg | 42 | 1 | False / 0.0 | False / 0.0 |
| act3d_peract | open_drawer | 42 | 1 | False / 0.0 | True / 1.0 |
| act3d_peract | place_cups | 42 | 1 | False / 0.0 | False / 0.0 |
| act3d_peract | place_shape_in_shape_sorter | 42 | 1 | False / 0.0 | False / 0.0 |
| act3d_peract | place_wine_at_rack_location | 42 | 1 | False / 0.0 | True / 0.5 |
| act3d_peract | stack_cups | 42 | 1 | False / 0.0 | True / 0.5 |
| diffuser_actor_peract | place_cups | 42 | 1 | False / 0.0 | False / 0.0 |
| diffuser_actor_peract | place_shape_in_shape_sorter | 42 | 1 | False / 0.0 | False / 0.0 |
