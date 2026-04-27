# WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19699756.svg)](https://doi.org/10.5281/zenodo.19699756)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![HuggingFace Dataset](https://img.shields.io/badge/🤗-Dataset-yellow)](https://huggingface.co/datasets/MMJBDS/wisdombench-data)

**WisdomBench** is the first longitudinal benchmark for measuring *wisdom acquisition* — an AI agent's ability to learn from failure across sequential interactions.

Unlike capability benchmarks (GAIA, SWE-bench, WebArena) that measure what an agent *can do* at a single point in time, WisdomBench measures what an agent *has learned from doing* through repeated exposure.

## Key Features

- **20 Tasks × 4 Categories**: Hallucination, Sycophancy, Reasoning, Safety
- **5 Sequential Rounds**: Each task is attempted 5 times with feedback
- **Deliberate Traps**: Each task contains a failure mode that wise agents learn to avoid
- **3 Metrics**: Wisdom Quotient (WQ), Repeat Failure Rate (RFR), Generalization Ratio (GR)
- **Multi-Seed Evaluation**: 3 random seeds (42, 137, 256) for statistical robustness

## Quick Start

```bash
# Clone the repo
git clone https://github.com/mmjbds/wisdombench.git
cd wisdombench

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

**Key Finding**: Intelligence and Wisdom are negatively correlated (Spearman ρ = −0.389, p = 0.212, n=12). Higher-capability models hit a *ceiling effect* that leaves no headroom for learning. The triple-model evaluation confirms this as a structural phenomenon, not a statistical artifact.

## Repository Structure

```
wisdombench/
├── tasks/
│   └── all_tasks.json          # 20 tasks with prompts, traps, and rubrics
├── evaluation/
│   ├── judge_prompt.txt         # LLM-as-judge prompt + scoring rubric
│   ├── run_evaluation.py        # Evaluation runner (bring your own API key)
│   └── compute_metrics.py       # WQ, RFR, GR calculation
├── analysis/
│   ├── compute_iw_gap.py        # Intelligence-Wisdom Gap analysis
│   └── sensitivity_analysis.py  # Robustness checks (K, category exclusion)
├── results/
│   ├── deepseek_seed42.json     # Raw evaluation scores
│   ├── deepseek_seed137.json
│   ├── deepseek_seed256.json
│   ├── qwen_seed42.json
│   ├── qwen_seed137.json
│   ├── qwen_seed256.json
│   ├── qwenmax_seed42.json
│   ├── qwenmax_seed137.json
│   ├── qwenmax_seed256.json
│   └── correlations_triple_model.json  # Cross-model correlation analysis
├── LICENSE
└── README.md
```

## Citation

If you use WisdomBench in your research, please cite:

```bibtex
@article{zhang2026wisdombench,
  title={WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents},
  author={Zhang, Mian},
  year={2026},
  note={Preprint}
}

@article{zhang2026sovereign,
  title={SOVEREIGN: A Cognitive Operating System for Self-Evolving AI Agents},
  author={Zhang, Mian},
  year={2026},
  doi={10.5281/zenodo.19699756}
}

@article{zhang2026iwgap,
  title={The Intelligence-Wisdom Gap: Why Smarter AI Agents Are Not Wiser Ones},
  author={Zhang, Mian},
  year={2026},
  note={Preprint}
}
```

## Related Papers

This benchmark is part of the **Ouroboros Research Program**:

| Paper | DOI |
|:------|:----|
| SOVEREIGN: Cognitive Operating System | [10.5281/zenodo.19699756](https://doi.org/10.5281/zenodo.19699756) |
| Reflexive Intelligence | [10.5281/zenodo.19557261](https://doi.org/10.5281/zenodo.19557261) |
| ReflexBench / Observer Depth | [10.5281/zenodo.19627242](https://doi.org/10.5281/zenodo.19627242) |
| When Rewards Collide (Multi-GRPO) | [10.5281/zenodo.19665969](https://doi.org/10.5281/zenodo.19665969) |
| Ouroboros V22 | [10.5281/zenodo.19666786](https://doi.org/10.5281/zenodo.19666786) |
| Cognitive Lifecycle | [10.5281/zenodo.19666806](https://doi.org/10.5281/zenodo.19666806) |
| Cognitive Reward Topology | [10.5281/zenodo.19666829](https://doi.org/10.5281/zenodo.19666829) |

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

## Contact

Mian Zhang — 373743743@qq.com — [Ouroboros Project](https://github.com/mmjbds)
