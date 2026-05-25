# Dataset Card

## Purpose

This sample dataset demonstrates the public WisdomBench JSONL schema and scorer. It is deliberately tiny and synthetic.

## Fields

- `agent`: anonymized model or agent family.
- `task_id`: stable task identifier.
- `strategy`: evaluation condition.
- `seed`: random seed or run id.
- `round`: longitudinal exposure round.
- `success`: binary success indicator.

## Intended Use

- Verify scorer behavior.
- Build adapters for additional public evaluation tasks.
- File reproduction reports that include task-level metrics.

## Out of Scope

- The sample rows are not a leaderboard.
- The sample rows are not private model logs.
- The sample rows do not support deployment-safety claims.
