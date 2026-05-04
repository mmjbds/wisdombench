# P9 Recovery Adapter Pilot Plan

Generated UTC: 2026-05-04T14:29:39.913908+00:00
Adapter: `p9_recovery_knob_v0`
Training required: `False`
Cloud required for rollout: `True`
Minimum GPU: 1x A800 80GB is enough; 2 GPUs only help parallelism.
Expected wall time: about 28.0 minutes

Boundary: This pilot may support a recovery-adapter improvement claim only after matched rerun rows exist and are compared with baseline failures.

## Agent Plans

| agent | profile | tasks | cells | failure classes |
| --- | --- | ---: | ---: | --- |
| act3d_peract | act3d_supported | 6 | 6 | recovery_loop_failure, simulator_or_provenance_failure |
| diffuser_actor_peract | diffuser_supported | 2 | 2 | recovery_loop_failure, simulator_or_provenance_failure |

## Adapter Environment

| key | value |
| --- | --- |
| `WBE_PUBLIC_FACTORY_ADAPTER_ID` | `p9_recovery_knob_v0` |
| `WBE_PUBLIC_FACTORY_ADAPTER_NOTE` | `antigen-derived non-training recovery pilot` |
| `WBE_PUBLIC_FACTORY_MAX_STEPS` | `50` |
| `WBE_PUBLIC_FACTORY_MAX_TRIES` | `2` |
| `WBE_PUBLIC_FACTORY_STRICT_TIMEOUT_SEC` | `2400` |
| `WBE_ACT3D_DIFFUSION_TIMESTEPS` | `150` |
| `WBE_3DDA_DIFFUSION_TIMESTEPS` | `150` |

## Launch

```bash
WBE_P9_RECOVERY_MODE=run bash experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh
```
