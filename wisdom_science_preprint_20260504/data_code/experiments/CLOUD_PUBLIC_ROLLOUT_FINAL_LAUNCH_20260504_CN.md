# 云端 public checkpoint / real rollout 最终启动包

日期：2026-05-04

## 当前结论

本地六模型 API panel 已完成 pilot，并已纳入 evidence index。
真实 rollout / public checkpoint 证据当前不是空白：仓库中已经有可审计结果。

已落袋证据：

| 证据层 | 状态 | 口径 |
| --- | --- | --- |
| RVT-2 official supported | 270 episodes，gate 全过 | 官方 RLBench checkpoint 主证据 |
| PerAct official supported | 270 episodes，gate 全过 | public checkpoint supported-set validation |
| Act3D + 3D Diffuser strict sidecar | 36 unique episodes，gate 全过 | official-evaluator trajectory/provenance sidecar |
| self-trained lowdim | 6,300 episodes，gate 全过 | self-trained low-dimensional imitation baseline |
| UnifoLM-VLA LIBERO | 1,200 episodes，gate 全过 | official UnifoLM-VLA supported-set case study |

因此，下一次开云端的目标不是补“有没有”，而是做最终核验、同步、或加厚 public-factory strict evidence。

## 开机后第一条命令

先跑零浪费核验，不启动付费 rollout：

```bash
cd /root/autodl-tmp/order-architect-factory
WBE_FINAL_ROLLOUT_MODE=verify bash experiments/cloud/run_public_rollout_final_20260504.sh
```

若 gate 显示 public checkpoint 文件缺失，跑 PerAct supported：

```bash
cd /root/autodl-tmp/order-architect-factory
WBE_FINAL_ROLLOUT_MODE=peract_supported bash experiments/cloud/run_public_rollout_final_20260504.sh
```

若要继续加厚 Act3D / 3D Diffuser strict sidecar，跑最强 public-factory 模式：

```bash
cd /root/autodl-tmp/order-architect-factory
WBE_FINAL_ROLLOUT_MODE=public_factory_strict WBE_PUBLIC_STRICT_MODE=max bash experiments/cloud/run_public_rollout_final_20260504.sh
```

若云端目录完全没有结果，又确定要一次性补齐：

```bash
cd /root/autodl-tmp/order-architect-factory
WBE_FINAL_ROLLOUT_MODE=all WBE_PUBLIC_STRICT_MODE=max bash experiments/cloud/run_public_rollout_final_20260504.sh
```

## 时间预估

| 模式 | 预估 | 说明 |
| --- | ---: | --- |
| verify | 1-5 分钟 | 只查文件、gate 和 py_compile |
| peract_supported | 3-8 小时 | 270 RLBench episodes，主要吃 simulator wall-clock |
| public_factory_strict max | 6-12 小时 | Act3D + 3D Diffuser official evaluator strict sidecar |
| all | 9-20 小时 | 只在云端结果缺失时使用 |

## 最低云端配置

- 最低：1 张 A800 80G 或同级 NVIDIA GPU；24GB 显存也可尝试，但 A800 更稳。
- 推荐：1 张 A800 80G。这个任务主要受 RLBench/CoppeliaSim wall-clock 限制，不需要 4 张卡。
- 2 张卡：只有并行开多个 simulator 队列时才明显有用。
- 驱动/CUDA：以现有 `wbe-rvt` conda 环境为准；先看 `nvidia-smi` 和 `check_wbe_cloud.py`。
- 磁盘：至少 80GB 空余，最好 150GB。

## 停机标准

满足以下条件即可停机：

- `experiments/results/wbe_real/public_rollout_final_20260504_gate.json` 已生成；
- `p5_peract_supported` 和 `p6_peract_supported` 为 `complete=true`；
- `real_evidence_ok=true`；
- `provenance_ok=true`；
- public-factory strict summary 存在，且没有缺 trajectory/environment/git commit。

超过时间应止损：

- PerAct supported 超过 8 小时仍无新 episode；
- Diffuser strict 单 task 超过 40 分钟且 trace step 不增长；
- `nvidia-smi` / CPU 无目标进程但云端仍计费。

## 论文口径

可以写：

> We report a layered real-evidence stack: RVT-2 and PerAct official RLBench supported-set rollouts, Act3D/3D Diffuser official-evaluator strict sidecars, a self-trained low-dimensional 6,300-episode baseline, and UnifoLM-VLA LIBERO supported-set evidence.

不能写：

> We completed a 12-policy public VLA/SOTA 6,300 leaderboard.

除非后续真的拿到足够 public runnable checkpoints / factories，并对每个 policy 完成相同 task/seed/round gate。
