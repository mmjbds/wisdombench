# P9 Recovery Adapter 云端启动说明

日期：2026-05-04

## 当前状态

本地准备已完成：

- `experiments/embodied_antigen_labeler.py`
- `experiments/prepare_p9_recovery_adapter_pilot.py`
- `experiments/analyze_p9_recovery_adapter_pilot.py`
- `experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh`
- `experiments/results/wisdom_science/embodied_antigen_labels_v0.jsonl`
- `experiments/results/wisdom_science/embodied_antigen_summary_v0.json`
- `experiments/results/wisdom_science/p9_recovery_adapter_pilot_plan_20260504.json`

本地标注结果：

- 失败 antigen：6,256
- failure classes：7
- public-factory recovery pilot：8 个 matched failed cells
- 训练需求：不需要
- 最低云端：1 张 A800 80GB 足够
- 预计时间：约 28 分钟，实际可能因 CoppeliaSim 和 official evaluator 波动

## 云端启动命令

在云端仓库根目录运行：

```bash
WBE_P9_RECOVERY_MODE=run bash experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh
```

只检查不烧实验：

```bash
WBE_P9_RECOVERY_MODE=verify bash experiments/cloud/run_p9_recovery_adapter_pilot_20260504.sh
```

## 这次会做什么

脚本会：

1. 编译检查 P9 标注、计划、分析和 public factory adapter。
2. 重新生成 antigen labels 和 recovery plan。
3. 启动 RLBench/CoppeliaSim display。
4. 对 strict public-factory 已失败的 Act3D/3D Diffuser cells 进行 matched rerun。
5. 写出 `experiments/results/wbe_real/p9_recovery_adapter_public_factory_raw.jsonl`。
6. 生成 `experiments/results/wisdom_science/p9_recovery_adapter_pilot_analysis_20260504.json/md`。

## 论文口径

运行前只能说：

> We prepared an antigen-derived, non-training recovery-adapter pilot over matched public-factory failures.

运行后如果有 rescued failures，只能说：

> The pilot rescued X/Y matched public-factory failures under a non-training recovery adapter.

不能说：

> We trained a new policy.

不能说：

> We completed a full public VLA/SOTA leaderboard.

不能说：

> P9 proves general robot self-healing.

## 成功标准

最低成功：

- 脚本完成，analysis JSON 存在。
- matched cells 大于 0。
- 所有 adapter rows 有 trajectory、metadata、checkpoint、git commit、recovery_adapter 字段。

强成功：

- `rescued_failures > 0`
- `baseline_failure_rescue_rate > 0`

若 `rescued_failures = 0`，仍然可写为 negative pilot：当前 knob adapter 不足，需要更强 recovery primitive 或 learned adapter。
