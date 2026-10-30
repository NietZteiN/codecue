# Automatic experiment logging

Experiments, analyses, datasets and SLURM jobs now share a local metadata log. Original manifests and result artifacts remain authoritative; the log connects them by run identity, configuration/source/data hashes, model revision, job ID, timestamps, status, compact metrics and artifact links. Retired and superseded protocols retain their provenance.

Enabled and backfilled on 2026-10-26: **367 records** covering **59 runs, 32 analyses, 38 dataset manifests and 238 job records**, with no indexing issues. Six legacy submission manifests have no recoverable scheduler identity and are explicitly `unknown`. The remaining job outcomes are reconciled with accounting. The reconciler is enabled under account `tnguyen`; its live status command below reports the current guards.

Every event is written atomically to a uniquely named JSON file before indexing. Changed records also receive durable snapshots. SQLite, CSV and the dashboard are rebuildable views; concurrent writes use a filesystem lock and SQLite rollback journaling on the shared filesystem.

| Location | Purpose |
|---|---|
| `artifacts/binding/experiment_log/events/*.json` | Durable lifecycle events and record snapshots |
| `artifacts/binding/experiment_log/index.sqlite3` | Searchable current records and indexed event history |
| `artifacts/binding/experiment_log/experiments.csv` | Complete current record export |
| `artifacts/binding/experiment_log/index_summary.json` | Counts, last refresh and indexing issues |
| [experiment_log.md](experiment_log.md) | Generated dashboard with result links |

Registry start/finish/failure hooks publish stage events. Dataset/result metadata writers publish recognized manifests, registrations, summaries, audits and reviews. SLURM submission and start/finish stamping publish job events; completion also indexes the job's declared run and review paths. The mutable workspace stamp covers older frozen entrypoints that lack the new hooks. Periodic scans discover other local analyses and use `sacct` to catch cancellations before a job starts, timeouts and node failures.

Execution, audit and scientific qualification remain separate fields. A job can finish successfully and pass its artifact audit while failing its reliability gate. Canceled, interrupted, failed, retired and superseded records are retained instead of being counted as successful experiments.

The indexer reads bounded JSON metadata only. It does not open prediction JSONL, activation NPZ, model weights or frozen source snapshots. Sealed final/holdout/extrapolation outcomes are excluded; where permitted, only their manifest identity and artifact link are recorded. Logging neither runs models nor changes experiment resume identities.

The 2026-10-27 maintenance update keeps the 8 MiB JSON read limit and records oversized permitted reviews as links with size metadata and explicit `unknown` status. Their contents are not read or hashed. CSV `notices_json`, index-summary `notices`, and dashboard links expose this limitation separately from indexing errors. The compact model and pipeline reviews retain their independently indexed completion evidence. When a review becomes small enough, the same record is parsed and its notice clears. Malformed metadata, permission failures and oversized manifests still require attention. All 62 focused logging, scheduler and job checks passed, including 11 new bounded-read and recovery cases; a real refresh returned `ok` with no indexing errors.

Run these commands from the project root; each explicitly selects this workspace:

```bash
../envs/probe-cu129/bin/python scripts/117_binding_experiment_log.py refresh --scheduler --root "$PWD"
../envs/probe-cu129/bin/python scripts/117_binding_experiment_log.py list --kind run --root "$PWD"
../envs/probe-cu129/bin/python scripts/117_binding_experiment_log.py show RECORD_ID --root "$PWD"
```

The durable reconciler uses short CPU jobs on `dev`: one CPU, 1 GB, two-minute limit, requeue enabled, and a ten-minute default interval. It keeps two future guarded workers queued and replenishes them **before** indexing. A failed refresh or a worker lost before Python starts therefore has a successor. Singleton dependencies, file locks and a due-time check suppress duplicate indexing. Actual start times depend on SLURM availability. This survives terminal/VSCode closure, requests no GPUs and holds no permanent running slot on `normal`.

```bash
../envs/probe-cu129/bin/python scripts/118_binding_log_scheduler.py enable --root "$PWD" --account tnguyen
../envs/probe-cu129/bin/python scripts/118_binding_log_scheduler.py status --root "$PWD"
../envs/probe-cu129/bin/python scripts/118_binding_log_scheduler.py disable --root "$PWD"
```

Scheduler state, locks, journal and worker stdout live under `artifacts/binding/experiment_log/` (`scheduler_state.json`, `scheduler_journal.jsonl`, `scheduler_jobs/`). Ordinary logging repairs missing guards only when this service is already enabled; it never installs or re-enables a disabled service. Disable marks it disabled first and cancels only recorded housekeeping IDs whose current job name, account and owner match this workspace. It does not cancel unrelated experiments.

Indexing failures produce diagnostics and preserve the experiment's exit status. An event already spooled survives an index failure and is replayed on refresh; scheduler failures remain visible in its status/journal. Inspect the dashboard's indexing issues, `index_summary.json`, scheduler status and worker stdout when investigating missing records. Keep the durable event directory when rebuilding derived views.

Deployment checks: CPU job **478377** wrote a software-check result that appeared automatically; intentional-failure job **478378** remained failed with exit **7** in both SLURM and the log. CPU worker **478379** completed real reconciliation with exit **0** while retaining both successor guards. A repeated unchanged refresh produced no additional record snapshots. Software-check artifacts and regression XML are retained in `artifacts/binding/logging_release/`; they are separate from model evidence.

Validation: the final full binding regression passed **293 tests** (`regression_v2.xml`), followed by **55** fixture-isolation checks and **19** scheduler checks, including startup-jitter cases. Earlier focused checks cover writer paths, legacy identity recovery, concurrency, replay and sealed exclusions. [Deployment evidence](../../artifacts/binding/logging_release/deployment_v1.json) retains exact counts, source hashes, scheduler health and CPU-job accounting. Test-only lifecycle isolation keeps temporary software fixtures outside the project research journal; any earlier fixture observations were preserved in the release quarantine directory.
