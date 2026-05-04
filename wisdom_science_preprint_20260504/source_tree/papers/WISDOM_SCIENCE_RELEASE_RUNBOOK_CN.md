# Wisdom Science 发布 Runbook

日期：2026-05-04

## 发布目标

把 Wisdom Science 作为一个完整研究包对外呈现，而不是散落的若干篇论文。

最小发布单元：

1. Foundation whitepaper。
2. Wisdom Science Formal Core。
3. Wisdom Science Physics/Engineering Core。
4. Six-Model API Longitudinal Panel。
5. P8 Representation Genesis + Perspectival Grounding。
6. P9 Embodied Failure Immunity + Whole-Organism Intelligence。
7. Claim registry。
8. Terms v1。
9. Zenodo BibTeX。
10. Evidence index。
11. Submission checklist。
12. Macro/representation/formal/physics/API reproducibility scripts。

## 发布前检查

| 项 | 标准 |
| --- | --- |
| 论文编译 | Foundation/Formal/Physics/API Panel/P8/P9 PDF 全部可生成 |
| 证据索引 | `artifact_count = 99` 且 `missing_count = 0` |
| 术语一致 | 使用 `WISDOM_SCIENCE_TERMS_V1_CN.md` |
| DOI 引用 | 使用 `wisdom_science_zenodo.bib`，P4 优先新版 `10.5281/zenodo.19895990` |
| Formal Core | 7/7 formal checks 通过，且不把正 WQ/EWQ 偷换成学习机制证明 |
| Physics Core | 7/7 physics/engineering checks 通过，且所有物理类比都有可测量定义 |
| API Panel | 48-row pilot 全部 `ok`，且明确不是具身 rollout 或 VLA checkpoint 证据 |
| P8 口径 | 不声称 compression/intelligence/macro discovery/active perception/symbol grounding 首创 |
| P9 口径 | 只声称 8-cell matched recovery-adapter pilot 中 3/8 rescue、0 regression；不写成 public SOTA leaderboard、训练策略或通用机器人自愈 |
| 云端口径 | 不声称未跑过的 rollout / checkpoint / seed |

## 对外短口径

中文：

> Wisdom Science 研究 AI 在经历失败、反馈和扰动之后，是否真的变得更好。它把评价从“第一次多聪明”推进到“能不能从经验中变智慧”。

英文：

> Wisdom Science studies whether AI systems become better, more stable, and more transferable after failure, feedback, and perturbation.

## 三个公式短版

```tex
I = \text{first-round competence}
```

```tex
\mathrm{WQ} = \frac{1}{N}\sum_i
\frac{s_i^{(R)}-s_i^{(1)}}{s_{\max}-s_i^{(1)}}
```

```tex
\mathbb{E}[W] = C_{\mathcal{T}}\Phi^\alpha\Psi^\beta H^\gamma|\mathcal{E}|^\delta
```

```tex
\mathrm{EWQ} = \frac{1}{K}\sum_t[s_R(t)-s_1(t)]
```

## 后续云端开机条件

满足以下任意一项再开云端：

1. 已确定 runnable RLBench/LIBERO checkpoint。
2. 已写好 re-evaluation matrix。
3. 已确认 raw logs / trajectory / metadata / checkpoint provenance 保存路径。
4. 需要把 P9 小型 matched recovery-adapter pilot 扩展为更多 seed/task/policy 的真实 rollout。
5. 要生成 public leaderboard 的新增真实行。

开机后先跑零浪费核验：

```bash
cd /root/autodl-tmp/order-architect-factory
WBE_FINAL_ROLLOUT_MODE=verify bash experiments/cloud/run_public_rollout_final_20260504.sh
```

只有核验显示结果缺失或确实要加厚 public-factory strict sidecar，才切换到 `peract_supported`、`public_factory_strict` 或 `all`。

## 不开云端也能继续推进

- Foundation/Formal/Physics whitepaper 打磨。
- P8/P9 正文扩写和 related work 精修。
- 术语表和 claim registry v1。
- 官网/README/图示。
- 本地 API 扩大六模型 WisdomBench longitudinal panel 或做 macro-rewriting 对比。
