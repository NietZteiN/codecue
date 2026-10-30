# Project-priority cached-checkpoint suites

The user explicitly removed the inherited aggregate compute restriction and stated that this is the only active project. The authorization and accounting policy are recorded in `artifacts/binding/resource_policy_20261025.json`. New work uses an uncapped usage ledger with per-job walltimes and checkpoint identities. The historical ledger remains intact for earlier frozen runs. No capacity is reserved for other projects.

The repeated instruction to remove every artificial GPU/compute limit is implemented in the common runner: legacy `max_gpu_seconds`, stage budgets and profiler timeout settings no longer stop current-source runs. The ledger only accounts for completed work and active jobs. Submission supports configurable GPU counts, configurable tensor parallelism and the scheduler's actual 48-hour GPU allocation maximum. Scientific token ceilings, identity checks and validity gates continue to define each experiment.

The pending 3B job was replaced with the uncapped runner, 95% VRAM target and hardware-adaptive concurrency. The fully cached Llama-3.1-8B-Instruct checkpoint (`0e9e39f249a16976918f6564b8830bc894c89659`) adds another complete 5,038-request native-chat feasibility baseline. The four-model program now totals 20,152 planned predictions. Completed 13B outputs and the already-running 34B job retain their original captured source; they are not restarted. The 13B audit passed all 5,038 saved responses and measured 99.2% mean GPU utilization.

Current queue/source pointers are `artifacts/binding/capacity/jobs_v2.json` and `source_v2.json`. The combined report re-audits each model against its own exact registered tokenizer/source identity, so preserved earlier runs and new uncapped runs remain distinguishable. Refresh current status with `configs/binding/capacity/status_v2.json`; the older v1 queue includes explicitly cancelled pending work and is historical.

The 34B suite is now also complete and audited, averaging 99.5% allocated-device utilization. The uncapped runner passed all 181 binding regression tests. Both pending instruction-model suites passed complete 5,038-prompt preflight checks and are eligible on all suitable GPU partitions. They request the actual 48-hour scheduler maximum and allow a 15-minute minimum backfill allocation; only SLURM chooses and enforces the granted walltime. No application deadline stops these finite, resumable workloads. The source plan `../dependvar.txt` now reflects the explicit user override; its previous text is archived under `artifacts/binding/policies/`.

Run the following fully cached checkpoints as exploratory feasibility/capacity comparisons. The two larger CodeLlama models test capacity within the existing model family. The smaller general instruction model can use A30 hardware and supplies a separate architecture/protocol comparison. No weights are downloaded. Missing Qwen weights were detected before scheduling; that checkpoint is not included.

| Checkpoint | Pinned revision | Eligible GPU partition |
|---|---|---|
| CodeLlama-13b-Instruct-hf | `745795438019e47e4dad1347a0093e11deee4c68` | H100 or H200 |
| CodeLlama-34b-Instruct-hf | `d4c1c474abcacd32d2a6eda45f9811d38c83e93d` | H200 |
| Llama-3.2-3B-Instruct | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | A30 |

Each checkpoint has 5,038 predeclared requests, totaling 15,114:

| Section | Requests per checkpoint | Purpose |
|---|---:|---|
| CRUXEval-O direct and CoT | 1,600 | Complete published output-prediction baseline |
| BBH tracking sizes 3, 5 and 7 | 750 | Complete published arithmetic-free object tracking |
| Arithmetic forms, two readouts | 384 | Computation/readout feasibility |
| Arithmetic-free diagnostics, two readouts | 768 | Copy/overwrite feasibility |
| Fresh counterbalanced pairs, two readouts | 1,536 | Remove the earlier magnitude/distractor design confound |

CodeLlama CRUXEval uses the independently audited released completion boundary; its prompt token IDs are checked against raw SentencePiece. The smaller Llama model uses native chat around the same released content, so that comparison changes checkpoint and serialization. BBH and generated calibration use native chat templates. All generations are BF16, greedy, one completion per request, with unchanged per-task/readout token ceilings. CRUXEval scoring remains literal equality without code execution, not official sampled execution pass@k.

An actual-tokenizer CPU preflight builds content-hashed, complete prompt-token caches and independently rechecks the generated programs against Python. Downloaded benchmark programs and model output are never executed. GPU inference consumes those exact input IDs using one persistent vLLM engine per checkpoint, continuous batching, prefix caching, chunked prefill and request backlogs of 1,024. Completed chunks are saved for resumption. Engine initialization is amortized over every section. Device UUID telemetry, output token IDs, exact responses and recomputable scores accompany each run.

Scientific interpretation remains exploratory. Apply the previously stated elementary training-cell gate (at least 24 examples per cell, at least 90% correct and at most 5% invalid), preferring direct before trace. Test the training choice on numeric validation without falling back after a failure. These familiar structures are not confirmatory structural generalization. Preserve the original seven-billion-parameter results and failed gates; these are additional feasibility results, not the conditional mechanism-replication experiment. Generated final-test and extrapolation outcomes stay sealed.

Report counterbalanced effects as complete paired descriptive counts, keeping both readouts and every pair. Adding a dead statement also changes context and length; do not treat an observed difference as proof of a binding mechanism. Do not choose checkpoints or protocols using final outcomes.

Real scheduler limits apply. Observed `juno` permits four active jobs, including normal CPU, A30 and H200 allocations; `juno-dev` permits one. Independent tokenizer preparation can use ordinary CPU nodes while the regression suite uses dev. Jobs with failed prerequisites are cancelled, allowing their audits and final status checks to terminate visibly. The 34B job requests sufficient host RAM and an H200 rather than risking a too-small accelerator. There is no project-wide GPU-hour ceiling.

Source/configuration is immutable under `artifacts/binding/capacity/source_v1.json`; submitted jobs are in `jobs_v1.json` in the same directory. All complete suites are re-audited before the combined report and pair/gate summaries are exported. [Live status](capacity_status.md) records actual queued/running/completed states. Refresh it without inference:

```bash
PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/101_binding_experiment_status.py configs/binding/capacity/status_v1.json
```

The completed seven-billion-parameter [throughput validation](throughput_results.md) reached approximately 40 requests/s and 99% average GPU utilization on an H200 with the full request backlog. New kernel/batch outputs remain separately identified; that report records answer agreement and the H100/H200 hardware difference in its baseline timing comparison.
