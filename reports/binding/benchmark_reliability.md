# Benchmark continuation reliability

The working implementation now preserves completed published-benchmark runs when revisited. Previously, the completed-response branch rebuilt the summary from accuracy counts, dropping its response checksum and peak-memory fields. It also registered another attempt and GPU-budget lease even though no inference was necessary. The later scientific audit requires those metadata fields, so this could damage an otherwise complete result's auditability.

`registry.begin(..., reuse_complete=True)` validates the exact source/config/data/environment identity and returns an existing complete manifest without changing attempts, timestamps or the budget ledger. The benchmark runner validates all saved responses, coverage, aggregate counts and checksums, then returns the original summary with all resource/custom metadata intact. Corrupt completed artifacts are rejected rather than silently rewritten. Other stages retain the registry's previous default behavior.

If a process saved its final response batch but stopped before finalizing the run, the runner can finish bookkeeping without loading a model. It records the response checksum and explicitly marks unavailable peak-memory data as unknown. The review formats that missing measurement explicitly instead of inventing a value or crashing. Tests cover immutable repeated reads, reuse after the GPU budget is exhausted, incompatible identities, corrupted metadata and final-batch recovery without model loading.

The currently running scientific experiment and its queued audit retain their original frozen sources. These fixes apply to newly frozen software; historical source snapshots are not rewritten. Inspect historical completed results through the read-only status/audit tools instead of rerunning their archived inference command. A new inference attempt requires distinct output/preflight paths and fresh source/configuration freezing.

The new status command reads SLURM accounting, queue reasons, stage manifests, atomic summaries, append-only response progress and the shared budget. It distinguishes failed dependencies, missing scheduler confirmation, incomplete final JSONL writes and inconsistent completed coverage/checksums. It never repairs response files, cancels jobs or clears budget reservations. It writes only its dedicated status JSON and Markdown report; it does not replace the full scientific audit.

```bash
PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/101_binding_experiment_status.py configs/binding/serialization/status_v1.json
```

Scientific inference source: `artifacts/binding/serialization/source_v1.json`. Original controller/audit source: `analysis_source_v1.json` in that directory. Updated maintenance software: `maintenance_source_v1.json`. Regression results are recorded in `maintenance_regression_v1.xml`; focused recovery/status/snapshot checks are in `continuation_tests_v1.xml`.
