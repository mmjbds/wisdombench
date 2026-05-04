# 本地仓库与 Zenodo 文章清单审阅

日期：2026-05-04

## 结论

已根据用户提供的 15 条 Zenodo record URL 通过公开 Zenodo API 逐条复核。此前“本地 P0-P7 可能还未发 Zenodo”的判断需要更新：P0-P7 主线已经在 Zenodo 上有公开 preprint 记录；另外，早期 paper1-6 也已有独立 Zenodo 记录。

当前情况是三条谱系：

1. early paper1-6：反身智能、Observer Depth、GRPO 冲突、Ouroboros、认知生命周期、奖励拓扑。
2. P0-P4：SOVEREIGN、Cognitive Immunity、WisdomBench、Intelligence-Wisdom Gap、Second Scaling Law。
3. P5-P7：具身第二缩放律、WisdomBench-Embodied、LIBERO/VLA 实践证据。

这不是冲突，而是一个可整理成“总理论谱系”的连续推进：从反身决策与观察者深度，到智慧评测与架构缩放律，再到具身机器人/VLA 的可审计实验。

## 用户提供的 15 条 Zenodo 记录

| 序号 | Record | DOI | 标题 | 日期 | 文件 | 归类 |
| --- | --- | --- | --- | --- | --- | --- |
| Z1 | https://zenodo.org/records/19557261 | `10.5281/zenodo.19557261` | Reflexive Intelligence: Decision-Making in Observer-Participant Environments | 2026-04-13 | `paper1_reflexive_intelligence.pdf` | early-1 |
| Z2 | https://zenodo.org/records/19627242 | `10.5281/zenodo.19627242` | Observer Depth: Quantifying Reflexive Intelligence in LLMs via Phase Transition Analysis | 2026-04-17 | `paper2_reflexbench_arxiv.zip`, `paper2_reflexbench.pdf` | early-2 |
| Z3 | https://zenodo.org/records/19665969 | `10.5281/zenodo.19665969` | When Rewards Collide: Structural Interference and Phase Transitions in Multi-Objective GRPO | 2026-04-20 | PDF | early-3 |
| Z4 | https://zenodo.org/records/19666786 | `10.5281/zenodo.19666786` | Ouroboros V22: Bayesian Scenario Simulation and Recurrent Depth Cognition for Autonomous Financial Decision-Making | 2026-04-20 | PDF | early-4 |
| Z5 | https://zenodo.org/records/19666806 | `10.5281/zenodo.19666806` | The Cognitive Lifecycle: How AI Systems Learn to Remember, Forget, and Evolve in Non-Stationary Environments | 2026-04-20 | PDF | early-5 |
| Z6 | https://zenodo.org/records/19666829 | `10.5281/zenodo.19666829` | Cognitive Reward Topology: A Nine-Tier Architecture for Measuring and Shaping Intelligence via Multi-Reward GRPO | 2026-04-20 | `paper6_cognitive_reward_topology.pdf` | early-6 |
| Z7 | https://zenodo.org/records/19791688 | `10.5281/zenodo.19791688` | Cognitive Immunity: Anti-Fragile Reasoning through Bio-Inspired Failure Learning in AI Agents | 2026-04-26 | PDF | P1 |
| Z8 | https://zenodo.org/records/19793098 | `10.5281/zenodo.19793098` | WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents | 2026-04-26 | PDF | P2 |
| Z9 | https://zenodo.org/records/19793250 | `10.5281/zenodo.19793250` | SOVEREIGN: A Cognitive Operating System for Self-Evolving AI Agents ... Cognitive Entropy Theory | 2026-04-26 | `SOVEREIGN_A_Cognitive_Operating_System_for_Self-Evolving_AI_Agents.pdf` | P0 |
| Z10 | https://zenodo.org/records/19793366 | `10.5281/zenodo.19793366` | The Intelligence-Wisdom Gap: Why Smarter AI Agents Are Not Wiser Ones ... | 2026-04-26 | PDF | P3 |
| Z11 | https://zenodo.org/records/19793489 | `10.5281/zenodo.19793489` | The Second Scaling Law: Intelligence Scales with Parameters, Wisdom Scales with Architecture | 2026-04-26 | PDF | P4 old |
| Z12 | https://zenodo.org/records/19895990 | `10.5281/zenodo.19895990` | The Second Scaling Law: Intelligence Scales with Parameters, Wisdom Scales with Architecture | 2026-04-29 | PDF | P4 newer |
| Z13 | https://zenodo.org/records/19987012 | `10.5281/zenodo.19987012` | The Second Scaling Law in Physical Worlds: Why Architecture Determines Robot Learning Ability | 2026-05-02 | `Ouroboros_P5_Embodied_Scaling_Law_Preprint.pdf` | P5 |
| Z14 | https://zenodo.org/records/19988002 | `10.5281/zenodo.19988002` | WisdomBench-Embodied: A Longitudinal Benchmark for Measuring Learning Ability in Physical Agents | 2026-05-02 | `Ouroboros_P6_WisdomBench_Embodied_Protocol.pdf` | P6 |
| Z15 | https://zenodo.org/records/19988080 | `10.5281/zenodo.19988080` | WisdomBench-Embodied in Practice: Measuring Learning Ability in Vision-Language-Action Agents on LIBERO | 2026-05-02 | `Ouroboros_P7_WBE_Practice_on_LIBERO.pdf` | P7 |

## Zenodo 元数据问题

| 问题 | 影响 | 建议 |
| --- | --- | --- |
| P4 有两个 Zenodo records：`19793489` 和 `19895990` | 读者可能引用旧版 | 对外统一引用新版 `10.5281/zenodo.19895990`，旧版标为 previous version |
| 作者字段不统一：`Zhang, Mian` 与 `Mian, Zhang` 混用 | BibTeX/Google Scholar 可能拆成两个人 | 后续所有记录统一为 `Zhang, Mian` 或作者本人指定格式 |
| P0/P3 标题元数据出现异常字符 `бк` | 影响专业观感 | 在 Zenodo metadata 中改成冒号或 em dash |
| 多数记录 `version` 为空 | 版本管理不够清晰 | 后续统一填 `v1.0`, `v1.1` 等 |
| early paper1-6 与 P0-P7 命名体系未显式连接 | 总谱系不够清楚 | 建一个 `Ouroboros / SOVEREIGN Research Portfolio` 总 README |

## 三个公式：给学术同行看的简短版

这三条应作为“短版核心命题”，用于同行快速理解，不作为夸张宣传语。

### 1. Wisdom Quotient

用途：把“智慧”定义为跨轮次的可测学习增益，而不是一次性正确率。

```tex
\mathrm{WQ}
= \frac{1}{N}\sum_{i=1}^{N} w_i,\quad
w_i =
\begin{cases}
\frac{s_i^{(R)}-s_i^{(1)}}{s_{\max}-s_i^{(1)}} & s_i^{(1)}<s_{\max}\\
0 & s_i^{(1)}=s_{\max}
\end{cases}
```

同行短句：

> Intelligence is first-round performance; wisdom is normalized improvement under repeated experience.

### 2. Second Scaling Law

用途：把“智慧增长”从参数/数据规模转向架构属性。

```tex
\mathbb{E}_{\mathcal{T}}[W(M)]
= C_{\mathcal{T}}\,
\Phi(\mathcal{A})^{\alpha}
\Psi(\mathcal{A})^{\beta}
H(\mathcal{A})^{\gamma}
|\mathcal{E}|^{\delta}.
```

其中：

- `\Phi` = plasticity，经验后能否改变有效映射；
- `\Psi` = immunity，能否从失败中抽取可迁移规则；
- `H` = homeostasis，分布扰动下是否稳定；
- `|\mathcal{E}|` = 交互经验量。

同行短句：

> Wisdom scales with plasticity, transferable failure immunity, and homeostasis, not merely with parameter count.

### 3. Embodied Wisdom Extension

用途：把第二缩放律落到机器人/VLA 轨迹级证据。

```tex
\mathrm{EWQ}(M)
= \frac{1}{K}\sum_{t=1}^{K}\left[s_R(t)-s_1(t)\right],
\qquad
W_E \propto \Phi_E^{\alpha}\Psi_E^{\beta}H_E^{\gamma}.
```

其中：

- `\Phi_E` = 轨迹级 plasticity，例如 round 1 与 round R 的 DTW 差异；
- `\Psi_E` = 失败后的跨任务成功提升；
- `H_E` = nominal/perturbed 分布下 EWQ 的稳定性。

同行短句：

> For physical agents, wisdom is not first-attempt success; it is auditable improvement across repeated embodied trials.

## 当前最适合的总叙事

1. Z1-Z6 是前史：反身性、观察者深度、奖励冲突、循环认知、生命周期、奖励拓扑。
2. P0-Z9 是系统框架：SOVEREIGN 把这些前史汇聚成认知操作系统。
3. P1/P2/P3/P4 是理论核心：认知免疫、WisdomBench、智能-智慧差距、第二缩放律。
4. P5/P6/P7 是具身落地：把智慧缩放律与 WB-E 测量接到 RLBench/LIBERO/VLA 证据门。
5. Representation Lab 是下一层：不只优化答案和策略，而是优化表示法、宏、证明路线和任务接口。

## 本地仓库已见论文线

从 `papers/` 目录已见：

| 本地线 | 文件/目录线索 | 定位 |
| --- | --- | --- |
| P0 | `P0_sovereign_system`, `SOVEREIGN_A_Cognitive_Operating_System_for_Self-Evolving_AI_Agents.tex/pdf` | SOVEREIGN 认知操作系统 |
| P1 | `P1_cognitive_immunity`, `Cognitive_Immunity_Anti-Fragile_Reasoning...tex/pdf` | 失败学习、认知免疫 |
| P2 | `P2_wisdombench`, `WisdomBench_A_Longitudinal_Benchmark...tex/pdf` | 智慧获取 benchmark |
| P3 | `P3_intelligence_wisdom_gap`, `The_Intelligence-Wisdom_Gap...tex/pdf` | 智能-智慧差距 |
| P4 | `P4_second_scaling_law`, `The_Second_Scaling_Law...tex/pdf` | 第二缩放律 / 架构智慧 |
| P5 | `P5_embodied_wisdom` | 具身智慧 |
| P6 | `P6_wisdombench_embodied` | WisdomBench Embodied |
| P7 | `P7_wbe_in_practice` | WB-E 实践与证据纪律 |
| early-1 | `paper1_reflexive_intelligence.*` | 反身智能早期稿 |
| early-2 | `paper2_reflexbench.*` | ReflexBench 早期稿 |
| early-3 | `paper3_multi_reward_grpo.*` | 多奖励 GRPO 早期稿 |
| early-4 | `paper4_ouroboros_v22.*` | Ouroboros v22 早期稿 |
| early-5 | `paper5_cognitive_lifecycle.*` | 认知生命周期早期稿 |
| early-6 | `paper6_cognitive_reward_topology.*` | 认知奖励拓扑早期稿 |

本地精确标题在 Zenodo 公开搜索中暂未命中，说明 P0-P7 这批很可能还没有正式发布到 Zenodo，或未被公开索引。

## Zenodo 公开索引到的相关记录

以下是按公开搜索结果归纳出的可见记录；不是 Zenodo API 全量导出，因此后续如有账号权限或作者主页链接，应再做一次最终核对。

### AI / 认知系统 / SOVEREIGN 可吸收资产

| 标题 | DOI / 链接 | 与当前论文关系 |
| --- | --- | --- |
| Functional Self-Consciousness in Frontier AI Agents: A Case Study of OpenClaw from the Perspective of Confidence-Modulated State Separation | https://doi.org/10.5281/zenodo.18641234 | 可作为 P0/P3/P4 的思想前史，但顶会稿要避免“证明 AI 有意识”的强口径 |
| Toward a Cognitive Operating System: Theoretical Architecture, Layered Principles, and Meta-Theoretical Transformation | https://doi.org/10.5281/zenodo.17507208 | 与 P0 SOVEREIGN 强相关；可作为 COS 到 SOVEREIGN 的理论前身 |
| Field Theory of Knowledge (FTK): A Dynamical Systems Formalization of Concepts, Associations, and Creative Recombination | https://doi.org/10.5281/zenodo.17882333 | 与 spreading activation、Representation Lab、知识场/语义动力学相关 |
| Dynamic Fold Gradient Descent (DFGD): New AI Algorithm methodology | https://doi.org/10.5281/zenodo.17119051 | 可作为算法思想资产；若进顶会稿，需要严格实验与基线 |
| AI Zero-Cost Multiplier Effect on White-Collar Labor: An Economic Analysis | https://doi.org/10.5281/zenodo.18437448 | 与产品化/社会影响相关，不适合塞入 P0-P7 技术主线 |

### 数学 / 哲学 / 元方法资产

| 标题 | DOI / 链接 | 与当前论文关系 |
| --- | --- | --- |
| Mathematical Certainty and the Psychology of Proof: When Formal Rigour Amplifies Experiential Uncertainty | https://doi.org/10.5281/zenodo.18216803 | 可支持“形式证明与人类认知成本”的背景，适合 Representation Lab 引言 |
| Contextual Structural Logic and Interpretation Moduli in Algebraic Geometry | https://doi.org/10.5281/zenodo.17610142 | 与表示法、解释模空间、数学语义多样性相关；可进入 Representation Lab 背景 |
| The Epistemology of Simulated Evaluation: Toward a Reflexive Method of Theoretical Validation Beyond Mathematics | https://doi.org/10.5281/zenodo.17345875 | 与 P7 证据纪律、反身评估、simulated evaluation 相关 |
| The Formal Genesis of Philosophy: Theory-Internal Meaning, Conceptual Abstraction, and the Interface between Philosophy and Non-Philosophy | https://doi.org/10.5281/zenodo.17384556 | 可作为抽象生成理论前史，但不宜进入技术核心 |
| Post-Evental Epistemology: Consciousness, Temporality, and the Ontology of the Already-Ended | https://doi.org/10.5281/zenodo.17365397 | 与记忆、时间性、反思有弱关联；建议只放入总谱系，不进主论文 |
| From Rebellion to Play: The Sublimation of 'Enjoying the Absurd' in Absurdist Philosophy | https://doi.org/10.5281/zenodo.17219433 | 哲学资产，与当前 AI 顶会线关系弱 |
| Dynamical System of Folding Convergence Criterion Is Isomorphic to Euclidean Algorithm | https://doi.org/10.5281/zenodo.16737094 | 与 DFGD/FCC 数学资产相关；若要使用需重新审计数学严谨性 |

### 需要复核的引用线索

| 线索 | 状态 |
| --- | --- |
| Folding Convergence Criterion and Its Implications for Algorithm Optimization, DOI `10.5281/zenodo.17115298` | 在 DFGD 记录中被引用，但本次公开搜索未直接打开到该记录 |
| `Dynamical System of Folding Convergence Criterion...` 的 restricted/ResearchGate DOI 版本 | 存在一个 restricted 文件记录和 RG DOI 版本，可能是重复/旧版本 |
| Zenodo 作者页全量列表 | 本次未完成 API/账号级全量导出，只完成公开搜索索引审阅 |

## 与当前 P0-P7 的整合建议

1. P0 SOVEREIGN 可以吸收 `Toward a Cognitive Operating System`，但要写成“概念前身”，不要让 P0 看起来只是 COS 改名。
2. P3/P4 可以吸收 OpenClaw functional self-consciousness 的“confidence-modulated state separation”思想，但要降成架构机制，不要写意识哲学强结论。
3. Representation Lab 最适合吸收 FTK、数学确定性、CSL/IMO、SAV：它们共同指向“表示、解释、验证、认知成本”。
4. DFGD/FCC 如果要进入主技术线，必须单独做数学审稿和实验复现；不能直接作为已证算法收益。
5. 哲学类论文可作为 intellectual lineage，不建议塞进 NeurIPS/CoRL 主文，只能精炼为背景动机或 appendix。

## 风险

| 风险 | 处理方式 |
| --- | --- |
| 旧 Zenodo 论文表述过宏大，影响顶会审稿信任 | 主论文采用冷静、可检验、可复现口径 |
| COS 与 SOVEREIGN 名称过近 | 明确 COS 是理论框架，SOVEREIGN 是工程系统和实验论文 |
| OpenClaw 自意识口径容易引发争议 | 顶会稿只使用 metacognition/self-model/state-separation，不主张现象意识 |
| DFGD/FCC 数学严格性需复核 | 单独成线，不混入 P0-P7 的核心证据 |
| Zenodo 全量记录可能未完全检索 | 后续需要用 Zenodo API 或账号导出做最终 bib/DOI 清单 |

## 下一步

建议立即做三件事：

1. 建一个统一 bibliography：把 Zenodo 可用资产分为 `core lineage`、`supporting philosophy`、`do-not-cite-in-main` 三类。
2. 给 P0-P7 写一段统一祖先叙事：COS -> SOVEREIGN -> WisdomBench -> Embodied Wisdom -> Representation Lab。
3. 如果要对外发布，先补 Zenodo/DOI 元数据一致性，避免标题、作者格式、版本号、DOI 引用混乱。
