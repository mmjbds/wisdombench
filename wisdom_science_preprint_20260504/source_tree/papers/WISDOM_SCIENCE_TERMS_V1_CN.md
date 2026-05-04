# Wisdom Science 术语表 v1

日期：2026-05-04

来源：`experiments/results/wisdom_science/macro_registry_v0.md`、P0-P7、P8/P9 题纲、15 条 Zenodo 记录。

## 核心术语

| 术语 | 短定义 | 对应论文 | 角色 |
| --- | --- | --- | --- |
| Wisdom Science | 研究系统经历失败、反馈、扰动和迁移后是否变得更好的科学框架 | 总框架 | 领域名 |
| Intelligence | first-round performance；第一次尝试的能力 | P2/P3/P6/P7 | 横轴 |
| Wisdom | experience-conditioned improvement；经历后的改进能力 | P2/P3/P4 | 纵轴 |
| Wisdom Quotient (`WQ`) | 文本/agent 场景的归一化跨轮次学习增益 | P1/P2/P3/P4 | 核心指标 |
| Embodied Wisdom Quotient (`EWQ`) | 具身场景中最后一轮与第一轮表现差 | P5/P6/P7 | 核心指标 |
| Intelligence-Wisdom Gap | 高 first-round intelligence 不保证高 wisdom 的结构性差距 | P3 | 理论问题 |
| Second Scaling Law | 智慧随架构属性和经验缩放，而非只随参数缩放 | P4/P5 | 主定律 |
| Cognitive Immunity | 从失败中抽取抗原并形成可迁移抗体的机制 | P1/P0 | 机制 |
| Cognitive Entropy | 描述认知系统不确定性、漂移和失稳的统一度量 | P0 | 理论底座 |
| Plasticity (`Φ`) | 架构在经验后改变有效映射的能力 | P4 | 架构轴 |
| Immunity (`Ψ`) | 从失败中抽取可迁移规则的能力 | P1/P4 | 架构轴 |
| Homeostasis (`H`) | 扰动下维持稳定改进的能力 | P4 | 架构轴 |
| Embodied Plasticity (`Φ_E`) | 轨迹级行为随经验变化的程度 | P5/P6 | 具身轴 |
| Embodied Immunity (`Ψ_E`) | 失败经验能否提升相关任务 | P5/P6/P9 | 具身轴 |
| Embodied Homeostasis (`H_E`) | nominal/perturbed 分布下 EWQ 的稳定性 | P5/P6 | 具身轴 |
| WisdomBench | 文本/agent 纵向智慧评测 | P2 | benchmark |
| WisdomBench-Embodied (`WB-E`) | 机器人/VLA 纵向智慧评测协议 | P6 | benchmark |
| Evidence Gate | 只有 raw logs/provenance/trajectory 完整时才允许声称结果 | P7 | 证据纪律 |
| Representation Genesis | 生成能压缩未来问题的新表示法 | P8 | 下一层理论 |
| Embodied Failure Immunity | 把机器人失败轨迹转成可迁移抗原/抗体 | P9 | 具身下一层 |
| Failure Antigen | 从失败事件中抽取的可复用失败模式 | P1/P9 | 数据结构 |
| Failure Antibody | 从 failure antigen 生成的规则、记忆、约束或 adapter | P1/P9 | 干预结构 |
| Failure Atlas | 机器人失败类型、原因和迁移关系图谱 | P9 | 数据资产 |
| Observer Depth | 模型在观察者-参与者环境中识别反身层级的能力 | early-2 | 前史术语 |
| Ouroboros | 循环认知/反思/场景模拟机制 | early-4/P0 | 系统机制 |

## 三个公式的标准口径

### `WQ`

标准短句：

> Wisdom is normalized improvement under repeated experience.

禁止升级：

> WQ 不是哲学智慧，也不是安全性或价值对齐的充分指标。

### Second Scaling Law

标准短句：

> Wisdom scales with plasticity, transferable failure immunity, homeostasis, and experience.

禁止升级：

> 当前不能写成已证明普适指数；应写成可检验框架与初步证据。

### `EWQ`

标准短句：

> Embodied wisdom is auditable improvement across repeated physical trials.

禁止升级：

> Positive EWQ 本身不等于真实在线学习；必须结合机制和 provenance。

## 术语治理规则

1. 论文中统一使用 `Wisdom` 指跨轮次经验改进能力。
2. `Intelligence` 统一指 first-round competence，不泛指全部智能。
3. P5-P7 使用 `I_E` / `EWQ`，不混写成普通 `I` / `WQ`。
4. `Cognitive Immunity` 用于文本/agent 和系统机制；具身扩展写作 `Embodied Failure Immunity`。
5. `Evidence Gate` 必须和具体 artifact 绑定：raw logs、trajectory、metadata、checkpoint、commit。
6. `Representation Genesis` 不抢“compression=math/intelligence”首创，只写“wisdom-oriented representation governance”。

## 当前最强概念核

按 corpus count 和 document frequency，当前最强概念核是：

1. Cognitive Immunity / immunity。
2. WisdomBench。
3. Ouroboros。
4. Plasticity-Immunity-Homeostasis 三轴。
5. Wisdom Quotient / Second Scaling Law。
6. Evidence Gate。
7. Representation Genesis / Embodied Failure Immunity。

这说明我们的体系已经从单个想法变成了可压缩、可复用的研究语言。
