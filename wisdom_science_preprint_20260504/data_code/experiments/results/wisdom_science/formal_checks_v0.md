# Wisdom Science Formal Checks v0

| check | passed | interpretation |
| --- | --- | --- |
| `non_regression_boundedness` | True | If final score is between first score and ceiling, WQ lies in [0, 1]. |
| `intelligence_wisdom_separation` | True | First-round competence and after-experience improvement can rank systems differently. |
| `positive_wq_non_identifiability` | True | The same score trace can come from learning or from hidden round scheduling; provenance is required. |
| `task_mix_simpson_trap` | True | Changing task mixtures can reverse rankings; fixed weights and stratified reports are mandatory. |
| `ceiling_sensitivity` | True | Near-ceiling denominators amplify small regressions; report raw deltas and clipped variants. |
| `macro_accounting` | True | A macro is admissible only after paying definition/glossary cost. |
| `evidence_gate_minimum` | True | A leaderboard cell is not admissible when checkpoint/factory provenance is missing. |
