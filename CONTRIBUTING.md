# Contributing to WisdomBench

Contributions should make the released benchmark easier to inspect, recompute, compare, or extend without expanding its claims beyond the public evidence.

## Useful Contributions

- Correct a task, category, schema, citation, or documentation error.
- Add a metric test or a public-safe validator.
- Submit an external run card with exact versions, seeds, hashes, methods, and limitations.
- Propose a bounded task extension with a public scoring contract.
- Report a reproducible mismatch between the documented and computed result.

## Before a Pull Request

Run:

```bash
python analysis/compute_iw_gap.py --demo
python evaluation/compute_metrics.py --data results/deepseek_seed42.json
python scripts/validate_run_card.py run_cards/example_run_card.json --check-files
```

State the benchmark commit, files changed, expected output, data rights, and the claim boundary affected by the change.

## Public Boundary

Do not submit API keys, provider account data, private prompts, customer data, restricted outputs, unpublished review material, or claims that depend on evidence that cannot be inspected. An external run is not canonical merely because its run card validates; inclusion requires provenance and result review.

Use the [external run issue form](https://github.com/mmjbds/wisdombench/issues/new?template=external_run.yml) for public-safe run metadata. Use the central [open research Discussions](https://github.com/mmjbds/mianzhang.org/discussions) for questions and early proposals.
