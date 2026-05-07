# WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**WisdomBench** is the first longitudinal benchmark for measuring *wisdom acquisition* - an AI agent's ability to learn from failure across sequential interactions.

Unlike capability benchmarks (GAIA, SWE-bench, WebArena) that measure what an agent *can do* at a single point in time, WisdomBench measures what an agent *has learned from doing* through repeated exposure.

This is the anonymous artifact repository for a NeurIPS 2026 Evaluations and Datasets Track submission. The repository content is anonymized for double-blind review; the dataset contents and result files match the submitted paper.

## Key Features

- **20 Tasks x 4 Categories**: Hallucination, Sycophancy, Reasoning, Safety
- **5 Sequential Rounds**: Each task is attempted 5 times with feedback
- **Deliberate Traps**: Each task contains a failure mode that wise agents learn to avoid
- **3 Metrics**: Wisdom Quotient (WQ), Repeat Failure Rate (RFR), Generalization Ratio (GR)
- **Multi-Seed Evaluation**: 3 random seeds (42, 137, 256) for statistical robustness

## Quick Start

```bash
# View tasks
python -c "import json; print(json.dumps(json.load(open('tasks/all_tasks.json')), indent=2))"

# Compute metrics from raw data
python analysis/compute_iw_gap.py --demo

# Run evaluation on your own model (requires API key)
python evaluation/run_evaluation.py --api-key YOUR_KEY --model your-model
```

## Benchmark Results (N=3,600 Evaluations)

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
| Qwen-Max | No Memory | 2.467 | +0.134 | 0.750 |
| Qwen-Max | Self-Refine | 2.450 | +0.167 | 0.692 |
| Qwen-Max | Reflexion | 2.483 | +0.100 | 0.714 |
| Qwen-Max | Cog. Immunity | 2.467 | +0.150 | 0.667 |

**Key Finding**: Intelligence and Wisdom are negatively correlated (Spearman rho = -0.389, p = 0.212, n=12). Higher-capability models hit a *ceiling effect* that leaves no headroom for learning. The triple-model evaluation confirms this as a structural phenomenon, not a statistical artifact.

## Croissant Metadata

The repository includes `croissant.json` for the NeurIPS Evaluations and Datasets Track artifact check. The metadata file includes:

- Standard Croissant context with `@language: en`
- The anonymous 4open repository URL
- File-level SHA256 hashes
- One validated `recordSet`
- Required Responsible AI fields: `rai:dataLimitations`, `rai:dataBiases`, `rai:personalSensitiveInformation`, `rai:dataUseCases`, `rai:dataSocialImpact`, and `rai:hasSyntheticData`

Local validation:

```text
mlcroissant validation OK
name: WisdomBench
distribution: 11
record_sets: 1
```

## Repository Structure

```text
wisdombench/
|- croissant.json
|- tasks/
|  `- all_tasks.json          # 20 tasks with prompts, traps, and rubrics
|- evaluation/
|  |- judge_prompt.txt        # LLM-as-judge prompt + scoring rubric
|  |- run_evaluation.py       # Evaluation runner (bring your own API key)
|  `- compute_metrics.py      # WQ, RFR, GR calculation
|- analysis/
|  |- compute_iw_gap.py       # Intelligence-Wisdom Gap analysis
|  `- sensitivity_analysis.py # Robustness checks (K, category exclusion)
|- results/
|  |- deepseek_seed42.json    # Raw evaluation scores
|  |- deepseek_seed137.json
|  |- deepseek_seed256.json
|  |- qwen_seed42.json
|  |- qwen_seed137.json
|  |- qwen_seed256.json
|  |- qwenmax_seed42.json
|  |- qwenmax_seed137.json
|  |- qwenmax_seed256.json
|  `- correlations_triple_model.json
|- CITATION.cff
|- LICENSE
`- README.md
```

## Citation

If you use WisdomBench in your research, please cite:

```bibtex
@article{wisdombench2026,
  title={WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents},
  author={Anonymous Authors},
  year={2026},
  note={NeurIPS 2026 Evaluations and Datasets Track submission}
}
```

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
