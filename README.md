# WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents

This is the anonymous artifact repository for a NeurIPS 2026 Evaluations and Datasets Track submission.

WisdomBench is a longitudinal benchmark for measuring whether AI agents improve after repeated exposure to failure-inducing tasks with feedback. Standard capability benchmarks measure first-attempt performance; WisdomBench measures learning trajectories.

## Contents

```text
wisdombench/
|- croissant.json
|- tasks/
|  `- all_tasks.json
|- evaluation/
|  |- judge_prompt.txt
|  |- run_evaluation.py
|  `- compute_metrics.py
|- analysis/
|  |- compute_iw_gap.py
|  `- sensitivity_analysis.py
|- results/
|  |- deepseek_seed42.json
|  |- deepseek_seed137.json
|  |- deepseek_seed256.json
|  |- qwen_seed42.json
|  |- qwen_seed137.json
|  |- qwen_seed256.json
|  |- qwenmax_seed42.json
|  |- qwenmax_seed137.json
|  |- qwenmax_seed256.json
|  `- correlations_triple_model.json
|- LICENSE
`- README.md
```

## Benchmark Design

- 20 tasks across four failure categories: hallucination, sycophancy, reasoning, and safety.
- Five sequential rounds per task.
- Inter-round feedback for longitudinal learning strategies.
- Three reported metrics: Wisdom Quotient (WQ), Generalization Ratio (GR), and Repeat Failure Rate (RFR).
- Three random seeds: 42, 137, and 256.

## Evaluation Scope

The submitted result files report 3 model families x 4 learning strategies x 20 tasks x 5 rounds x 3 seeds = 3,600 evaluations.

The benchmark is intended for studying longitudinal learning from failure. It is not a complete measure of general intelligence, alignment, safety, or deployment readiness.

## Anonymous Use

This repository is intentionally anonymized for double-blind review. It should not include author names, public DOI links, public GitHub usernames, public Hugging Face usernames, emails, cloud credentials, or non-anonymous project links.

## Croissant Metadata

The `croissant.json` file includes:

- Standard Croissant context with `@language: en`.
- Anonymous repository URL.
- File-level SHA256 hashes.
- One validated `recordSet`.
- Required Responsible AI fields:
  - `rai:dataLimitations`
  - `rai:dataBiases`
  - `rai:personalSensitiveInformation`
  - `rai:dataUseCases`
  - `rai:dataSocialImpact`
  - `rai:hasSyntheticData`

Local validation:

```text
mlcroissant validation OK
name: WisdomBench
distribution: 11
record_sets: 1
```

## Citation

```bibtex
@article{anonymous2026wisdombench,
  title={WisdomBench: A Longitudinal Benchmark for Measuring Wisdom Acquisition in AI Agents},
  author={Anonymous Authors},
  year={2026},
  note={NeurIPS 2026 Evaluations and Datasets Track submission}
}
```

## License

The benchmark artifacts are released for academic review and reproducibility under the repository license.
