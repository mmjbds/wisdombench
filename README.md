# WisdomBench: Longitudinal Evaluation of Learning from Failure

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

WisdomBench is a longitudinal benchmark for measuring whether an AI agent changes after repeated exposure to feedback and failure. Capability benchmarks ask what a system can do at one point in time; WisdomBench asks what changes across sequential interactions.

This GitHub repository is a public development mirror. Its namespace, metadata, and commit history are identity-linkable, so it must not be represented or submitted as an anonymous double-blind artifact. When a venue requires anonymity, use only the separate venue-designated anonymous archive and follow that venue's current rules.

## Public Artifact

- 20 tasks across hallucination, sycophancy, reasoning, and safety categories.
- Five sequential rounds per task.
- Three metrics: Wisdom Quotient (WQ), Repeat Failure Rate (RFR), and Generalization Ratio (GR).
- Three random seeds: 42, 137, and 256.
- Public task definitions, scoring code, evaluation runners, aggregate results, and Croissant metadata.

## Quick Start

```bash
python -c "import json; print(json.dumps(json.load(open('tasks/all_tasks.json')), indent=2))"
python analysis/compute_iw_gap.py --demo
python evaluation/run_evaluation.py --api-key YOUR_KEY --model your-model
```

Pass credentials through your own secure runtime. Never commit keys or model-provider account data.

## Reported Result Table

The repository contains 3,600 scored evaluation events for the included model-strategy conditions.

| Model | Strategy | I (R1) | W (WQ) | RFR |
|:------|:---------|:------:|:------:|:---:|
| DeepSeek-v4-flash | No Memory | 1.783 | +0.067 | 0.764 |
| DeepSeek-v4-flash | Self-Refine | 1.733 | +0.100 | 0.803 |
| DeepSeek-v4-flash | Reflexion | 1.750 | **+0.217** | 0.702 |
| DeepSeek-v4-flash | Cog. Immunity | 1.800 | +0.158 | **0.650** |
| Qwen-Plus | No Memory | 2.800 | +0.050 | 0.933 |
| Qwen-Plus | Self-Refine | 2.917 | +0.033 | 0.000 |
| Qwen-Plus | Reflexion | 2.800 | +0.108 | 0.167 |
| Qwen-Plus | Cog. Immunity | 2.850 | +0.092 | 0.500 |
| Qwen-Max | No Memory | 2.483 | +0.033 | 0.786 |
| Qwen-Max | Self-Refine | 2.450 | -0.008 | 0.605 |
| Qwen-Max | Reflexion | 2.450 | +0.269 | 0.000 |
| Qwen-Max | Cog. Immunity | 2.450 | +0.242 | 0.450 |

Across the 12 model-strategy aggregate points, the reported Spearman correlation between initial score and WQ is `rho = -0.389`, `p = 0.212`, `n = 12`. The point estimate is negative, but the reported p-value does not establish a population-level negative relationship. It should be treated as an exploratory signal, not confirmation of a structural law.

RFR can also have small or condition-dependent denominators when few severe-threshold failures occur initially. Interpret each value with the task-level records and metric definition rather than as a standalone safety rate.

## Repository Structure

```text
wisdombench/
|- croissant.json
|- tasks/all_tasks.json
|- evaluation/
|- analysis/
|- results/
|- CITATION.cff
|- CLAIM_BOUNDARY.md
`- LICENSE
```

## Claim Boundary

The artifact supports inspection and recomputation under its documented task, judge, model, and scoring conditions. It does not establish general wisdom, general safety, production readiness, or superiority across untested models and environments. See [CLAIM_BOUNDARY.md](CLAIM_BOUNDARY.md).

## Citation and License

Use [CITATION.cff](CITATION.cff) only in the context allowed by the target venue. Source code intentionally released by this repository is Apache-2.0; benchmark data and metadata use the item-specific terms described in [LICENSE_SCOPE.md](LICENSE_SCOPE.md). A public repository URL does not make this repository an anonymous submission artifact.
