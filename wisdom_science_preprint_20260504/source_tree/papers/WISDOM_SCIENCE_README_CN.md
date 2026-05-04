# Wisdom Science 研究包 README

日期：2026-05-04

## 核心定义

Wisdom Science 研究系统在经历失败、反馈、扰动和迁移之后，能否变得更好、更稳、更可复用。

它把 AI 评价从单点成功率推进到纵向学习能力：

- `I` / `I_E`：第一次尝试有多强。
- `WQ` / `EWQ`：经历后提升多少。
- `Φ` / `Φ_E`：是否可塑。
- `Ψ` / `Ψ_E`：失败经验能否迁移。
- `H` / `H_E`：扰动下是否稳定。

## 当前成品结构

| 层级 | 产物 |
| --- | --- |
| 总框架 | `papers/WISDOM_SCIENCE_MASTER_FRAMEWORK_20260504_CN.md` |
| 成品白皮书 | `papers/WISDOM_SCIENCE_FOUNDATION/main.tex` |
| 数学骨架 | `papers/WISDOM_SCIENCE_FORMAL_CORE/main.tex` |
| 物理/工程骨架 | `papers/WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE/main.tex` |
| 六模型 API panel | `papers/WISDOM_SCIENCE_API_PANEL/main.tex` |
| P8 | `papers/P8_representation_genesis/main.tex` |
| P9 | `papers/P9_embodied_failure_immunity/main.tex` |
| 主张登记 | `papers/WISDOM_SCIENCE_CLAIM_REGISTRY_20260504_CN.md` |
| 术语表 | `papers/WISDOM_SCIENCE_TERMS_V1_CN.md` |
| Zenodo BibTeX | `papers/wisdom_science_zenodo.bib` |
| 证据索引 | `experiments/results/wisdom_science/evidence_index_v0.md` |
| 投稿预检表 | `papers/WISDOM_SCIENCE_SUBMISSION_CHECKLIST_20260504_CN.md` |
| 宏挖掘 | `experiments/results/wisdom_science/macro_registry_v0.md` |
| 表示法压缩 | `experiments/results/wisdom_science/representation_compression_v0.md` |
| 失败图谱 schema | `experiments/embodied_failure_atlas_schema.json` |
| leaderboard schema | `experiments/wisdom_science_leaderboard_schema.json` |

## 快速复现

```powershell
python experiments\wisdom_science_claim_registry.py
python experiments\wisdom_science_macro_mining.py
python experiments\wisdom_science_representation_compression.py
python experiments\wisdom_science_formal_checks.py
python experiments\wisdom_science_physics_engineering_checks.py
python experiments\generate_wisdom_science_tables.py
python experiments\wisdom_science_evidence_index.py
```

六模型 API panel（需要本地环境变量，不写入密钥）：

```powershell
python experiments\api_wisdombench_longitudinal_panel.py --check-only --max-tasks 2
python experiments\api_wisdombench_longitudinal_panel.py --max-tasks 2 --rounds 2 --strategies no_memory,cognitive_immunity --seeds 42 --run-id apiwb_pilot6x2x2_20260504 --output experiments\results\wisdom_science\api_wisdombench_panel\pilot6x2x2_raw.jsonl --summary-json experiments\results\wisdom_science\api_wisdombench_panel\pilot6x2x2_summary.json --summary-csv experiments\results\wisdom_science\api_wisdombench_panel\pilot6x2x2_summary.csv --table-tex papers\WISDOM_SCIENCE_API_PANEL\generated\api_wisdombench_panel_table.tex --resume
```

编译论文：

```powershell
cd papers\P8_representation_genesis
pdflatex -interaction=nonstopmode main.tex

cd ..\P9_embodied_failure_immunity
pdflatex -interaction=nonstopmode main.tex

cd ..\WISDOM_SCIENCE_FOUNDATION
pdflatex -interaction=nonstopmode main.tex

cd ..\WISDOM_SCIENCE_FORMAL_CORE
pdflatex -interaction=nonstopmode main.tex

cd ..\WISDOM_SCIENCE_PHYSICS_ENGINEERING_CORE
pdflatex -interaction=nonstopmode main.tex

cd ..\WISDOM_SCIENCE_API_PANEL
pdflatex -interaction=nonstopmode main.tex
```

## 当前验证快照

- Claim registry：12 条核心主张。
- Macro mining：130 个论文/代码源文件。
- Representation compression：12 个核心源文件、13 个标准宏、净节省 3079 bytes、压缩比 1.0126。
- Perspectival Grounding：6 个 glyph/language/robotics/social/game toy cases，平均初始歧义 1.56 bits，主动补证据后全部消歧。
- Whole-Organism Intelligence：9 个 organ-like engineering layers，覆盖 policy、senses、routing、metabolism、joints、immunity、psychological regulation、social grounding、game-theoretic mind。
- Formal checks：7/7 通过。
- Physics/engineering checks：7/7 通过。
- 六模型 API panel pilot：6 个模型端点 × 2 个任务 × 2 个策略 × 2 轮 × 1 seed = 48 个真实 API rows，全部 `ok`；这是 text-agent evidence，不是具身 rollout。
- PDF：Foundation、Formal Core、Physics/Engineering Core、API Panel、P8、P9 均可编译。
- Evidence index：77 个 artifact，missing_count=0。

## 数学、物理、工程三层落地

- 数学：Formal Core 区分定义、定理、假设和经验主张，证明 I/WQ 可分离、正 WQ 不可单独识别学习机制、任务混合会造成排名反转。
- 物理：Physics/Engineering Core 把 plasticity 写成经验响应，把 homeostasis 写成扰动阻尼，把 failure immunity 写成重复失败衰减。
- 工程：每个强结果必须通过 metric、stability、provenance、cost、duplicate-cell gates。
- 视角：P8 的 Perspectival Grounding 把“看到的只是投影”落成 hypothesis set、viewpoint、evidence cost 和 counter-reflexive belief。
- 机体：P9 的 Whole-Organism Intelligence 把具身智能从单脑模型扩展成器官集群，每层都有 substrate 和 evidence gate。

## 当前证据边界

- P8 的表示法压缩实验是语料压缩证据，不等于证明“压缩就是智慧”。
- P9 当前是 schema + protocol + evidence discipline + 小型 matched recovery-adapter pilot：8 个 public-factory baseline failures 中恢复 3 个，0 个 regression；不声称 public SOTA leaderboard 或训练策略。
- 六模型 API panel 支持跨模型纵向认知口径，但不能写成 VLA、机器人、public checkpoint 或 RLBench rollout 证据。
- P5-P7 的真实具身证据仍按各自 evidence gate 口径解释。
- 云端只在需要真实 RLBench/LIBERO rollout、failure re-eval、VLA checkpoint 证据门时开启。
