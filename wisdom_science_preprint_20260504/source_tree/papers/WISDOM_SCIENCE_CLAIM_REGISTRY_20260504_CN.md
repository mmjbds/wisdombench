# Wisdom Science 核心主张登记表

日期：2026-05-04

用途：把所有核心主张、公式、证据和限制条件登记清楚，防止过度声称、内部冲突和外部撞车。

## Claim Registry

| ID | 主张 | 公式/对象 | 证据来源 | 当前强度 | 限制条件 |
| --- | --- | --- | --- | --- | --- |
| C1 | 智慧应与一次性智能区分 | `I` vs `WQ` | P2, P3 | 强 | WQ 只测可观察跨轮次改进，不等于哲学智慧 |
| C2 | 智慧可定义为跨轮次归一化学习增益 | `WQ` | P1, P2 | 强 | ceiling tasks 需置零，避免分母问题 |
| C3 | 更高 first-round intelligence 不必然带来更高 wisdom | Intelligence-Wisdom Gap | P3, P4 | 中强 | 当前实证基于有限模型/策略组合 |
| C4 | 智慧随架构属性缩放，而不只随参数量缩放 | `W ∝ Φ^αΨ^βH^γ|E|^δ` | P4 | 中 | 指数估计仍需更大样本，定律应写为 hypothesis/framework + preliminary evidence |
| C5 | 失败可作为免疫抗原被抽取和复用 | Cognitive Immunity | P1 | 中强 | 需要区分 memorization 与 true transfer |
| C6 | 具身智能也应报告纵向学习能力 | `I_E`, `EWQ` | P5, P6, P7 | 强 | 真实 rollout 需完整 provenance |
| C7 | 机器人学习能力可由 embodied plasticity/immunity/homeostasis 描述 | `Φ_E`, `Ψ_E`, `H_E` | P5, P6 | 中 | 当前还不是全量多架构指数拟合 |
| C8 | Evidence gate 是具身智慧论文的必要纪律 | raw logs, trajectories, provenance | P7 | 强 | gate 不能替代真实策略能力 |
| C9 | 表示法搜索是智慧系统的下一层能力 | Representation Genesis | P8 draft | 新主张 | 需要 toy-to-real 证据链 |
| C10 | 失败轨迹可转成 embodied antigens 并提升跨任务表现 | Embodied Failure Immunity | P9 draft | 新主张 | 需要真实或严格 supported-set re-eval |

## 三个同行短版公式

1. Wisdom Quotient:

```tex
\mathrm{WQ}
= \frac{1}{N}\sum_{i=1}^{N} w_i,\quad
w_i =
\begin{cases}
\frac{s_i^{(R)}-s_i^{(1)}}{s_{\max}-s_i^{(1)}} & s_i^{(1)}<s_{\max}\\
0 & s_i^{(1)}=s_{\max}
\end{cases}
```

2. Second Scaling Law:

```tex
\mathbb{E}_{\mathcal{T}}[W(M)]
= C_{\mathcal{T}}\Phi(\mathcal{A})^{\alpha}
\Psi(\mathcal{A})^{\beta}
H(\mathcal{A})^{\gamma}
|\mathcal{E}|^{\delta}
```

3. Embodied Wisdom:

```tex
\mathrm{EWQ}(M)=\frac{1}{K}\sum_{t=1}^{K}[s_R(t)-s_1(t)],
\qquad
W_E \propto \Phi_E^{\alpha}\Psi_E^{\beta}H_E^{\gamma}
```

## 禁止升级的说法

| 不应写 | 应改成 |
| --- | --- |
| 我们证明了智慧的终极定律 | 我们提出一个可检验的智慧缩放框架 |
| 参数对智慧完全无用 | 参数提升 first-round competence，但不保证 longitudinal wisdom |
| EWQ 证明机器人真正学习 | EWQ 是跨轮次表现变化；需结合机制和 provenance 判断学习来源 |
| 压缩就是智慧 | 表示法压缩可能是智慧系统的一种上游机制 |
| 失败免疫一定提升所有任务 | 失败免疫应通过 `Ψ/Ψ_E` 检验跨任务迁移 |

## 当前最该补强的证据

1. P4：更多模型/架构组合，收紧 exponent 口径。
2. P5/P6：更多 public runnable factory，但不必盲目烧全量。
3. P7：把 negative EWQ 解释得更清楚，强调 inference-only baseline。
4. P8：论文/代码宏挖掘真实统计。
5. P9：failure atlas 与 embodied antigen schema。
