# Cached-state follow-up, October30 evening

[Completed local results](../reports/binding/arithmetic_local_completion_snapshot_v1.md) · [Active protocol](../reports/binding/arithmetic_state_followup_plan_v2.md).

The original local suite is complete. New CPU-only work audits its results and reuses the archived activations for current binding lookup, role-conditioned numeric values and composed algebraic relationships. No new backbone inference or training is part of this follow-up. The source interpreter remains a100% ceiling, and every scientific result remains adaptive discovery.

The initial follow-up source `06e1b8ee6730629c94b814de` was stopped during software validation, before any state audit or readout worker began. A saved behavioral summary used an exact floating equality check that rejected two TRAIN means changing only at5.55e-17/2.78e-17 when batch traversal order changed. Revision2 uses at most1e-12 roundoff only for two rate fields; counts, cell identities, parsing and correctness remain exact. Responses and scientific summaries were preserved. The active source is **`82aa60555d1e9b67df97b706`**, with source SHA `bbc601d34d9d423808e74b7e7e1a08d43bdab11ec66265fbed72e0b87a147334`.

The [source catalog](frozen_sources.json) stores normalized archives. Restore sources and regression mirrors from a repository checkout:

```bash
python scripts/export_binding_repository.py restore-sources --match 82aa60555d1e9b67df97b706
tar -xzf reproducibility/arithmetic_state_regression_20261030_v2.tar.gz
```

Inspect the active supervised suite:

```bash
../envs/probe-cu129/bin/python scripts/91_binding_frozen_run.py \
  artifacts/binding/sources/82aa60555d1e9b67df97b706 \
  scripts/186_binding_state_suite.py status \
  configs/binding/arithmetic_state_followup_20261030_v2/suite.json
```

`submit` is for a fresh run directory; existing suites use `watch`/`status`. The source-only setup entrypoint is script187 with `--edition 2` from the live checkout. Scientific workers require SLURM and frozen software validation. Audits preserve all four layers' fixed seed-specific projections. Learned readouts and composition only consume caches with matching immutable receipts and row identities.

The active DAG is in `configs/binding/arithmetic_state_followup_20261030_v2/suite.json`. Its controller checks about every ten minutes and stops after all stages are terminal. Source/model/score errors require review; only resumable scheduler interruptions are retried. Existing model jobs and the editor allocation are preserved. Every completed bank and review enters automatic experiment logging.

Raw activations, projected arrays, model parameters and score arrays remain local under the existing repository policy. Metadata, regression mirrors and frozen source are published; JSONL is losslessly compressed through `compressed_artifacts.csv`. A clean clone requires the original local activation payloads to rebuild projections. Publication snapshots can precede queued-job completion; later evidence receives a new publication edition. Superseded first-edition files and stopped-job evidence remain preserved rather than being rewritten.
