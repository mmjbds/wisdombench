# WB-E 真实结果 Schema

这个 schema 是 P5、P6、P7 的证据契约。只有当论文表格、图和统计结果都能从符合该契约的文件重新生成时，相关主张才算达到投稿门槛。

## Raw Episode Log

使用 JSONL。每一行代表一个环境 episode：

```json
{
  "paper": "P5",
  "benchmark": "rlbench",
  "task_id": "stack_cube2",
  "task_group": "stack",
  "agent_id": "cog_immunity_small",
  "architecture": "Cog. Immunity",
  "model_capacity": "small",
  "backbone": "unifolm-vla-libero",
  "seed": 42,
  "round": 1,
  "perturbation": "none",
  "success": true,
  "score": 1.0,
  "trajectory_path": "trajectories/P5/cog_immunity_small/stack_cube2_s42_r1.npz",
  "video_path": "videos/P5/cog_immunity_small/stack_cube2_s42_r1.mp4",
  "wall_time_s": 14.2,
  "git_commit": "abc1234",
  "environment": {
    "simulator": "RLBench",
    "simulator_version": "x.y.z",
    "cuda": "12.4",
    "gpu": "A100-80G"
  }
}
```

必填字段：

- `paper`：`P5`、`P6` 或 `P7`。
- `benchmark`：`rlbench`、`libero` 或具名 real-robot benchmark。
- `task_id`、`task_group`。
- `agent_id`、`architecture`、`model_capacity`、`backbone`。
- `seed`、`round`、`perturbation`。
- `success`：用于计算 I_E 与 EWQ 的 boolean success signal。
- `trajectory_path`：如果主张 Phi_E/plasticity，必须保存 trajectory。
- `git_commit` 与 `environment`：复现所需信息。

## 最低证据数量

P5/P6 RLBench 主张：

```text
12 configs x 35 tasks x 5 rounds x 3 seeds = 6,300 nominal episodes
```

如果 `H_E` homeostasis 来自 perturbation robustness 主张，需要增加 matched perturbed run；否则必须明确说明 `H_E` 是 architecture-coded，而不是测量结果。

P7 LIBERO 主张：

```text
6 agents x 130 tasks x 5 rounds x 3 seeds = 11,700 nominal episodes
+ 11,700 perturbation episodes = 23,400 total episodes
```

## 重新生成规则

以下输出必须由脚本生成，不能手工编辑：

- P5/P6：12 configurations 表格、axiom table、two-way ANOVA、power-law fit。
- P7：main LIBERO table、learning curves、I_E/EWQ scatter、axiom radar、ablation table、perturbation/homeostasis statistics。
- Audit manifest：按 config、task group、seed、round、perturbation condition 统计的精确 episode count 和 missing-cell report。
