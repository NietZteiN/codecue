# Versioned variable-binding study

**Start here: [Master research report — plan, results, figures and next steps](../../docs/binding/MASTER_REPORT.md)** ([Markdown version](master_research_report_v4.md)). Updated October 29, 2026; includes the full original plan, 19 main figures, including four conceptual illustrations, the complete figure archive, every research branch and an ordered next-experiment plan. The handoffs below retain their historical checkpoints; use the master report for current status.

Structural and algebraic relationship readouts and posthoc controls are complete: **83.488% whole-graph recovery**, **85.019% algebraic balanced accuracy**, and **96.759% both-first-parent recovery on equal-state pairs**. The stronger source-value pipeline scores **98.108%**, exceeding hidden direct algebraic decoding. See the [findings](relationship_results_findings_v1.md) and [figure](figures/relationship_controls_v1.png). All seven execution jobs completed and all **1,602 binding tests pass**. Current readiness: **39 ready / 9 scientific / 3 optional**, 51 tasks. These remain discovery results under a fixed program scaffold; broader causal/version and final-prediction work remains open.

Both relationship branches are now active: prefix-safe **dependency/version targets** and **algebraic targets** for equality, ordering, signed differences and sum/subtraction triples. The balanced numeric-control bank has **1,944 source programs** and supports both target families on the same examples. It reuses the earlier routing bank’s 81 graphs and 27 components, so it is not independent structural replication. See the [broader relationship plan](relationship_decoding_plan_v2.md) and [combined preparation findings](relationship_preparation_findings_v2.md). **Learned relationship decoders remain untrained**; source/target validation is complete. The full suite passes **1,370 tests**, and the [current inventory](preparation_readiness.md) records **36 ready tasks out of 48**, nine scientific decisions and three optional deferred tasks. The [combined handoff](../../artifacts/binding/relationships/handoff_review_v2.json) retains source, target, test and logging identities.

Earlier dependency/version preparation, 2026-10-27: versioned def-use, transitive ancestry, assignment succession and explicitly visible output ancestry now have prefix-safe labels. A new copy-routing bank contains **1,296 source programs, 81 directed graphs and 432 equal-value/different-provenance pairs**, with full graphs separated across 18 training and nine development components. The old banks were largely fixed by family/update schedule. See the [relationship plan](relationship_decoding_plan.md) and [preparation findings](relationship_preparation_findings.md). **Learned relationship decoding remains unfinished**; oracle targets and source preparation do not count as recovered model representations. The full suite passes **1,302 tests**; the [current readiness inventory](preparation_readiness.md) records **35 ready tasks out of 47**, nine scientific decisions and three optional deferred tasks.

Completed queried/unqueried accessibility follow-up, 2026-10-27: **45 weighted-ridge factorizations**, **180 independent matched-capacity heads** and **414,720 exact saved-model row replays** on an existing 9,216-row capture bank. At the fixed neutral block-24 `pre_answer` cell, queried-value accuracy is **88.89%**, versus **9.4184%** for the unqueried value: **79.4705 percentage points**, with conditional group interval **[75.8670, 83.5069]**. See the [findings](query_selectivity_findings.md), [PNG curves](query_selectivity_curves_v1.png) and [SVG curves](query_selectivity_curves_v1.svg). This is decoder-specific accessibility on consumed structures; value disposal, natural causal use, ownership, tracking/reconstruction and mechanism C remain unestablished. No new language-model calls were made. The [46-task readiness report](preparation_readiness.md) has **34 ready**, nine scientific decisions and three optional deferred tasks. The full binding regression suite passes **1,191 tests**; the compact completion manifest fixes audit/reuse of large scientific results while preserving every original fit artifact. Exact source, artifact, test and job identities are retained in the [machine-readable handoff](../../artifacts/binding/query_selectivity/handoff_review_v2.json).


Current reproduction uses the frozen verification/figure source in `artifacts/binding/query_selectivity/source_release_v2.json`; the original numerical fit source is separately retained in `source_v1.json`. From the repository root, these commands audit the sealed results and reproduce the immutable figure without loading a language model or refitting:

```bash
PYTHONPATH=artifacts/binding/sources/c8983e113aafcad5ab23f89b/src ../envs/probe-cu129/bin/python artifacts/binding/sources/c8983e113aafcad5ab23f89b/scripts/137_binding_query_selectivity.py audit configs/binding/query_selectivity/llama31_8b_v1.json
PYTHONPATH=artifacts/binding/sources/c8983e113aafcad5ab23f89b/src ../envs/probe-cu129/bin/python artifacts/binding/sources/c8983e113aafcad5ab23f89b/scripts/138_binding_query_selectivity_review.py configs/binding/query_selectivity/review_v1.json
```

The [completion receipt](../../artifacts/binding/query_selectivity/llama31_8b_v1/completion_manifest_v2.json) and [seal review](../../artifacts/binding/query_selectivity/seal_review_v2.json) preserve all 50 scientific artifact hashes. The [regression record](../../artifacts/binding/query_selectivity/regression_v2.xml) records 1,191 passing tests; [SLURM accounting](../../artifacts/binding/query_selectivity/job_accounting_v2.json) records successful completion of both study jobs and all 38 current-stage jobs.

Earlier assignment-cue behavioral comparator checkpoint, 2026-10-27: **12,288 full responses**, 256 qualification responses, **20,412 corrected-analysis logistic fits** and **1,024 passing tests**. Gains are context-dependent, with no clear Brier advantage over joint confidence in any of ten matched contexts. All 847,872 parent probabilities replay exactly; a documented iteration-allowance correction resolved one initial fit failure. See the [findings](stress_comparator_findings.md), [all comparisons](stress_prediction_decision_v2.md), [numerical correction](stress_comparator_numerics_v2.md), and [current readiness report](preparation_readiness.md). That earlier checkpoint had 33 ready tasks, nine scientific decisions and three optional deferred tasks. Automatic logging retains the failed/canceled first attempts alongside completed runs.

Earlier joint-confidence and representation checkpoint, 2026-10-27: **16,632 logistic fits**, **336 readout fits**, exact replay and **932 passing tests**. Combining confidence bundles improves CodeLlama in two fixed contexts; alignment helps some individual-slot readouts without establishing whole-state recovery or a mechanism. See the [joint/representation findings](continuation_followup.md), [joint table](joint_confidence_decision.md), [representation report](representation_sensitivity_v1.md), and [current readiness report](preparation_readiness.md). That earlier checkpoint had 32 ready tasks, nine scientific decisions and three optional deferred tasks. All six new SLURM jobs completed successfully. Automatic result logging is enabled, with bounded large-file notices separated from errors.

Earlier confidence checkpoint, 2026-10-27: both candidate-event collections and the 18-tier/37-contrast comparison are complete. Across the two new analyses, 21,924 logistic fits passed exact baseline replay checks. CodeLlama benefits from next-token confidence beyond strong source features, but the more costly candidate-event alternatives show no clear Brier improvement over next-token confidence in any of the ten fixed contexts. See the [findings](candidate_prediction_findings.md), [all results](candidate_prediction_decision.md), and [current readiness report](preparation_readiness.md). The full suite passed **852 tests**; all qualified collection/prediction jobs completed, with automatic aggregation and logging. That checkpoint had 30 ready tasks, 10 scientific decisions and three optional deferred tasks. Source hashes, validation and scheduler accounting are in the [machine-readable handoff](../../artifacts/binding/discovery_confidence/handoff_review_v1.json).

Confidence follow-up, 2026-10-27: the [13-tier discovery comparison](discovery_confidence_decision.md) completed 9,072 logistic fits with every original baseline reproduced exactly. Confidence lowers CodeLlama Brier from 0.123574 to 0.116641 beyond source interactions; Llama's Brier increment is smaller and uncertain, while log loss improves. The [fixed-contrast figure](discovery_confidence_increments_v2.svg), all scores and source/access contracts are retained. The earlier 13-tier checkpoint passed **796 tests**. Both whole-bank candidate tokenizer QAs and FP32 parity smokes passed; both 6,144-row full-answer banks subsequently completed and passed audit, as recorded above. The [primary-source review](submission_novelty_review.md) covers the original twelve reference identifiers plus two confidence papers, with version flags and explicit claim limits.

Expanded preparation update, 2026-10-26: see the [preparation portfolio](preparation_portfolio.md) and [current 46-task readiness inventory](preparation_readiness.md). Nine new discovery banks (30,960 source records), complete content-overlap audits and 240 precision scenarios are built; both exact-prompt confidence collections completed and passed audit (12,288 prefill measurements). Candidate-answer scoring, train-only alignment/reduced-rank helpers and registration-readiness tools are implemented. The inventory distinguishes built software from executed measurements and scientific qualification.

The [capacity/oracle-access sensitivity](discovery_controls_decision.md) is complete: **5,292 additional logistic fits**, eight fixed tiers and **421 passing tests** on the same discovery cohort. Original baseline predictions, folds, penalties and fitted parameters reproduce exactly. Fixed source interactions help CodeLlama; raw neutral behavior still has no clear oracle-free Brier gain. Oracle-matched controls retain a CodeLlama neutral-query increment, while an explicit failure flag can help without adding any observation. [All scores](discovery_controls_results_v1.md) and the [figure](discovery_controls_results_v1.svg) distinguish capacity, oracle access and deterministic encoding. This remains exploratory, with its later confidence follow-up reported above; mechanism C and frozen final validation remain unfinished.

The [empirical discovery failure baselines](discovery_prediction_decision.md) are complete: 12,288 cached target examples, 24 structural groups per checkpoint, and 2,268 regularized logistic fits. Input features improve over training-prior predictions; raw neutral-query properties add no clear Brier gain, while a separately labeled oracle-scored neutral query helps. [All scores](discovery_prediction_results_v1.md) and the [figure](discovery_prediction_results_v2.svg) retain both access contracts and every fixed partition seed. All six CPU jobs and **385 regression tests** passed. This is exploratory cross-validation on consumed discovery data; mechanism C and frozen final validation remain unfinished.

The [arithmetic/readout diagnostic](arithmetic_readout_decision.md) is complete: **12,288 audited responses**, eight same-answer 0/1/3-operation forms and separate direct/trace protocols on both cached models. All four fixed reliability gates failed. Source form and trace prompting strongly change the scores; a reliable computed regime and causal account remain unresolved. The [full comparison](arithmetic_readout_results_v1.md), [figure](arithmetic_readout_results_v1.svg) and [completed status](arithmetic_readout_status_v1.md) retain every result. Both tokenizer preflights and **322 full regression tests** passed; the subsequent forecasting-access guard passed **44 focused checks**. The [prior two-operation context](arithmetic_readout_prior_context.md) reproduces 768 existing scores without new model queries. Earlier failed gates and sealed outcomes remain unchanged.

The [automatic experiment dashboard](experiment_log.md) indexes run/result identities, metrics, audits, scientific gates, datasets and job outcomes. [Logging and periodic CPU reconciliation](experiment_logging.md) run automatically, including for frozen entrypoints; the complete CSV and durable event history are under `artifacts/binding/experiment_log/`.

Logging maintenance passed the **293-test full regression suite** plus focused checks. Successful-result and intentional-failure CPU jobs verified the real hooks; a real reconciler worker and an automatically replenished guard verified background operation. This maintenance adds no model inference or scientific evidence.

The [computed retention-frontier study](live_load_decision.md) is complete: 76,032 audited predictions across two cached models. Both failed the fixed arithmetic/clean-program reliability gate. The revised bank has genuinely 2/3/4 live bindings at fixed eight defined variables and reproduces byte for byte. Independent backend/cache checks also completed after correcting a prompt/completion stop-boundary bug; switching backend did not materially improve accuracy in the selected groups. All 247 tests pass. A reliable computed regime and a selective binding mechanism remain unresolved.

The [frequency-matched probe-control continuation](matched_probe_controls_decision.md) is complete: 75 CPU fits, exact class-frequency/entropy matching, and both full audits. All 967,680 original value-head predictions reproduced exactly. Queried-value recovery at the recorded block-31 answer-preparation site is 87.89% versus 2.78% shuffled. All 234 tests pass; causal use and a general binding mechanism remain unresolved.

The [fresh ownership and common-final-query continuation](mechanism_followup_decision.md) is complete and audited: 7,776 baseline responses and 96,768 intervention forwards. The primary copy-site patches show small, nonselective effects. Repeating the final query reduces the late-query advantage from 13.04 to 1.70 percentage points. All 234 tests pass; a tracking/reconstruction algorithm and selective binding mechanism remain unestablished.

The [explicit query-timing and earlier-copy studies](timing_and_copy_decision.md) are complete: 4,536 audited baseline responses and 90,720 intervention forwards across three instruction variants. Late-query accuracy was 1201/1296 versus 1022/1296 early, with cell-specific reversals. Reordering improved joint paired-query correctness (34/162 to 78/162), while producing ownership swaps and other-query tradeoffs. All 223 tests pass. These findings advance query timing and semantic-transformation tests; no general binding mechanism or explanation-transfer method is established.

The [full research agenda and backlog](research_backlog.md) maps every original research branch, the ten authorized experiments and the proposed training, explanation-transfer and unlearning extensions to its current status. The [M0–M6 checklist](implementation_checklist.md) is the shorter milestone view.

The [computed-expression and late-reference continuation](routing_extension_decision.md) is complete: 1,008 audited baseline responses and 15,120 next-token intervention forwards. Neither computed family passed its accuracy gate. Changing the unused reset reference did not repair the swap failure (15/54 versus 9/54 in the nominated cell), and reference-vector transfers showed no consistent advantage over matched controls. All 217 regression tests passed; the larger A30 batches and scheduler eligibility changes are recorded. These results do not establish a general binding mechanism.

The corrected [literal-value routing assay](value_transfer_decision.md) is complete: 432 baselines, 20,160 intervention forwards and all output/control audits passed. At block 0, version-query transfer is 144/144 on affected queries and 0/144 on unchanged-answer controls. Ownership transfer is less specific across the full cohort (81.94% versus 18.75%). The initial formatting-boundary error is preserved and [documented](value_transfer_boundary_correction.md). All 213 regression tests pass. This is evidence about local literal routing; a general binding mechanism and held-out error prediction remain unestablished.

Both 9,216-case discovery capture banks and all three readout suites are complete and audited. At block 31, queried-value recovery rises from 6.4% at the query-line boundary to 87.9% at answer preparation. Earlier current-value recovery depends strongly on literal proximity; identifier controls have easier targets and cannot settle selectivity. See [the completed measurement review](readout_protocol.md) and `artifacts/binding/continuation/handoff_v1.json`. The latest regression suite passed 213 tests. These results do not yet support a causal mechanism or a frozen final-test forecast.

The latest [continuation decision](continuation_decision.md) records completed [binding-competition discovery](competition_results.md) and [Llama completion-interface follow-ups](llama_serialization_results.md). All 19,968 competition predictions and 3,200 new completion predictions are audited. A 128-case cross-backend/hook check passed for Llama 3.1 8B, enabling [discovery state/query captures](state_capture_plan.md); their source and jobs are in `artifacts/binding/state_capture/`. The resulting probe measurements are reported below; no causal mechanism or generated final-test result is claimed.

The four-model capacity program is complete: [all 20,152 predictions are audited](capacity_results.md). CodeLlama 34B and Llama 3.1 8B passed the elementary arithmetic-free gate, enabling a separately scoped [binding-competition discovery study](competition_plan.md) with matched ownership/version/query-distance controls. Its CPU preflight caught and corrected a generated-only asset-loading bug before GPU inference; current jobs/source are in `artifacts/binding/continuation/jobs_v2.json` and `source_v2.json`. [Live continuation status](continuation_status.md) tracks the new work. The [Llama completion-interface follow-up](llama_serialization_results.md) is also complete: its separately recorded raw-completion runs resolve much of the earlier native-chat formatting failure. Historical scores and generated final outcomes remain unchanged.

The user's latest resource instruction makes this the sole active project and removes cumulative GPU-hour limits, stage time budgets, profiler cutoffs and the single-checkpoint restriction from the current runner. GPU counts and tensor parallelism are configurable; scheduler/hardware limits still apply. The completed [throughput validation](throughput_results.md) reached 40.2 requests/s with 98.6% average utilization on an H200. Independent [cached-checkpoint suites](capacity_plan.md) cover 20,152 predictions across CodeLlama 13B/34B and Llama 3.2 3B/3.1 8B; all four suites have completed with full audits; the 13B and 34B suites achieved 99.2% and 99.5% generation utilization. Check [live suite status](capacity_status.md) and `artifacts/binding/capacity/jobs_v2.json` before submitting duplicate work. Refresh with `python scripts/101_binding_experiment_status.py configs/binding/capacity/status_v2.json`.

Following the user's dataset search request, [published benchmark candidates](published_datasets.md) are now recorded. Official CRUXEval and BBH object-tracking data are downloaded with pinned commits and hashes; CRUXEval-O is the recommended next external baseline. The subsequent published baseline and completion-interface evaluations are complete, as recorded above and below.

The user subsequently authorized the [ten-experiment program](experiment_program.md). Its [reference-tokenizer audit and correction](tokenizer_boundary_correction.md), fresh diagnostics, source snapshots and per-experiment prerequisites are separate from the earlier pilot below. The current adapter verifies CodeLlama input IDs against the official tokenizer by default; historical native-tokenization experiments reproduce through their frozen sources.

The subsequent [diagnostic review](diagnostic_review.md) identifies the trailing-distractor/magnitude confound in the consumed data. A [fresh paired follow-up dataset](counterbalanced_followup.md) is generated and independently validated, with no model inference. Its preparation preserves the earlier gate and sealed final outcomes.

Read the generated [pilot report](pilot_report.md), [repository audit](repository_audit.md), [research decisions](research_decisions.md), [implementation checklist](implementation_checklist.md), and [handoff](handoff.md). Work remains in the existing CodeCue project; no optional training or second-paper extension runs automatically.

The continuation includes [training-only prompt calibration](prompt_calibration.md), [additional measurement controls](measurement_controls.md), matched CPU/GPU diagnostics and an independent uncached decoding check. The conditional arithmetic/update bank skipped inference after the fixed gate failed. The main short-answer cohort is near floor, so full GPU expansion was stopped. The [fixed difficulty ladder](difficulty_ladder_plan.md) has now completed both readouts; no regime passed its saved gate, so its stopping rule ends this checkpoint/protocol feasibility pilot. Read the [scientific decision memo](decision_memo.md) and [closest-work comparison](related_work_comparison.md) for interpretation. Final-test model outcomes remain sealed.

The published-dataset continuation completed all 2,350 predictions on 1,550 released questions: see the [audited results](published_baseline_review.md), [decision memo](published_decision.md), [fixed evaluation plan](published_evaluation_plan.md) and [dataset/source manifest guide](published_datasets.md). Its 1,600-prediction serialization follow-up is also complete and audited: see the [comparison](serialization_comparison.md) and [current decision](serialization_decision.md). Refresh [live status](serialization_status.md) with `python scripts/101_binding_experiment_status.py configs/binding/serialization/status_v1.json`; inspect `artifacts/binding/serialization/jobs_v1.json` before submitting duplicate work. The [reliability note](benchmark_reliability.md) describes completed-run metadata preservation and the new read-only health checks. The latest handoff is `artifacts/binding/serialization/handoff_v2.json`.

GPU throughput tuning has a separate [plan](throughput_plan.md) and [live status](throughput_status.md). Its completed Transformers trials are audited in `artifacts/binding/throughput/partial_hf_trials_audit.json`; these initial performance profiles preceded the completed full-workload validation linked above. The CUDA 12.9 vLLM runtime is isolated from the shared environment. The completed one-GPU sweep used continuous batching, CUDA graphs, prefix caching, up to 256 active sequences and a 90% GPU-memory target; it reuses the same engine for full-workload validation. Inspect `artifacts/binding/throughput/jobs_v4.json` before resubmitting. Successful post-run auditing automatically exports `artifacts/binding/throughput/selected_execution_v4.json` and `reports/binding/throughput_results.md`; a final CPU job refreshes status even if the GPU run or audit fails. Refresh it manually without model inference:

```bash
PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/101_binding_experiment_status.py configs/binding/throughput/status_v4.json
```

The throughput source pointer is `artifacts/binding/throughput/source_v4.json`; the status-tool source pointer is `status_source_v4.json` in the same directory. Every attempt, including failed startup and cancelled profiling time, charges the existing shared GPU ledger. Changed batching/kernels are recorded as a new execution profile with answer-agreement checks; old scientific scores remain unchanged.

The completed baseline evaluates CRUXEval-O and BBH Tracking Shuffled Objects independently of the earlier synthetic mechanism gates, using direct and CoT CRUXEval prompts and the released BBH CoT demonstrations. Inspect `artifacts/binding/published_jobs_v2.json` and `artifacts/binding/published/continuation_handoff.json` before submitting anything. Inference source is frozen by `published_source_v2.json`; audit source is frozen by `published_review_source_v3.json`. Both pointers are under `artifacts/binding/`.

```bash
# CPU data wrapping only; idempotent, verifies exact upstream source hashes.
python scripts/97_binding_published_benchmarks.py build configs/binding/published/full_v1.json
# Tokenizer QA and model inference must be submitted through SLURM.
# Use the snapshot path from published_source_v2.json as SNAPSHOT.
python scripts/slurm/submit.py --name published_qa --partition dev --time 00:10:00 -- python SNAPSHOT/scripts/91_binding_frozen_run.py SNAPSHOT scripts/97_binding_published_benchmarks.py preflight SNAPSHOT/configs/binding/published/full_v2.json
python scripts/slurm/submit.py --name published_full --partition h100 --time 02:55:00 -- python SNAPSHOT/scripts/91_binding_frozen_run.py SNAPSHOT scripts/97_binding_published_benchmarks.py run SNAPSHOT/configs/binding/published/full_v2.json
```

The CRUXEval metric is literal equality without code execution; it differs from the official execution scorer. The checkpoint's native chat wrapper is an explicit adaptation around unchanged released prompt content. Raw responses, token IDs, invalid/truncated counts, source hashes and runtime details are retained. Public benchmark scores do not open the generated final-test or structural-extrapolation outcomes.

From `/work/jvl210002/migration/codecue`:

```bash
export PYTHONPATH="$PWD/src"
export PATH="$PWD/../envs/probe-cu129/bin:$PATH"
python -m pytest tests -q
python -m codecue.binding generate --config configs/binding/smoke.json
python -m codecue.binding validate --config configs/binding/smoke.json
python -m codecue.binding generate --config configs/binding/pilot.json
python -m codecue.binding validate --config configs/binding/pilot.json
```

Tokenizer and hook preflight is a CPU software test. It also exercises behavior, extraction, probe fitting and the intervention assay in a temporary directory using the random network. It loads the pinned tokenizer and a tiny random network, and produces no model experiment result:

```bash
python scripts/slurm/submit.py --name binding_preflight --partition dev --time 00:10:00 -- python scripts/87_binding_preflight.py configs/binding/smoke.json
```

The current protocol is `short_answer_prefill_v2`, which starts the assistant response with `Answer:`. The older `short_answer_chat_v1` configs are retained for provenance: an actual CPU run produced explanations rather than parseable integers and was interrupted. Do not pool those outputs with v2.

Standalone smoke (one base from each of the twelve cells, all six naming renderings, primary and arithmetic controls = 144 responses):

```bash
python scripts/slurm/submit.py --name binding_smoke --partition h100 --time 00:10:00 -- python -m codecue.binding run-behavior --config configs/binding/smoke_prefill_v2.json
python -m codecue.binding report --run artifacts/binding/smoke_behavior_prefill_v2
```

The profiled pipeline includes that same smoke and then a full or balanced-subset discovery pilot, keeping final test sealed. Submit it only once; the handoff records the already submitted job. It writes the measured estimate, effective configuration and run manifests, and stops for development redesign if the smoke is near floor or ceiling.

```bash
python scripts/slurm/submit.py --name binding_pilot --partition h100 --time 03:55:00 -- python scripts/88_binding_pipeline.py configs/binding/smoke_prefill_v2.json configs/binding/pilot_prefill_v2.json
```

Run manifests include the exact configuration, code revision plus dirty source hashes, dataset manifest, pinned model/tokenizer commits, seeds, environment, elapsed time and artifact locations. Re-running with changed identities is refused. To resume the pipeline's pilot directly, use its generated `effective_config.json`; its balanced subset, if any, has its own directory. Never replace it silently with the nominal full configuration.

Actual CPU behavior is now recorded under `artifacts/binding/cpu_smoke_bf16_prefill_v2`. CPU activation extraction, probe fitting and a focused development assay have their own configs and job manifests. The handoff records completion status; do not submit duplicates. GPU equivalents remain available:

```bash
python scripts/slurm/submit.py --name binding_extract --partition h100 --time 01:00:00 -- python -m codecue.binding extract --config configs/binding/representations_prefill_v2.json
python scripts/slurm/submit.py --name binding_probes --partition dev --time 01:00:00 -- python -m codecue.binding fit-probes --config configs/binding/representations_prefill_v2.json
python scripts/slurm/submit.py --name binding_assay --partition h100 --time 00:30:00 -- python -m codecue.binding intervene --config configs/binding/development_assay_prefill_v2.json
```

The historical four-hour GPU quota has been removed at the user’s request. Current accounting uses `artifacts/binding/gpu_usage_uncapped.json` without admission limits; the old ledger is retained for provenance. Scheduler walltimes and cluster QoS still apply. A failed activation/intervention attempt must be inspected before trying a new run directory. Layer 16 in the development assay is a fixed software-assay site, not a discovered primary mechanism.

The completed CPU continuation uses `cpu_discovery_subset_prefill_v2.json` for a larger balanced behavioral cohort, and `cpu_representations_main_neutral_prefill_v2.json` for neutral training with all three development naming conditions on the main dataset. The original smaller probe cohort has one numeric instance per template and a large training/development gap; the supplement has five numeric instances per template and preserves the same layers and penalty. Its neutral-only training does not replace the separate within-condition fits from the smaller cohort. Selection plans, CPU wall caps, dependency chains and immutable source pointers are recorded in `artifacts/binding/*jobs.json` and the adjacent plan manifests.

The fixed interface suites cover the same eight primitive and four training programs at batch sizes one and four. `compare-backends` reads saved outcomes, verifies the inference contract and recomputes scores; it performs no model inference. `check-generation` runs an uncached full-prefix argmax reference on that same suite and is submitted through SLURM. The latter charges the shared GPU ledger. Its tiny random-model preflight is a software test. The actual submitted jobs are in `generation_reference_jobs.json`; inspect their state before any resubmission.

```bash
python -m codecue.binding compare-backends --config configs/binding/backend_comparison.json
python scripts/slurm/submit.py --name binding_generation_reference --partition a30 --time 00:10:00 -- python -m codecue.binding check-generation --config configs/binding/gpu_generation_reference.json
```

Both outputs are immutable; the first command refuses to overwrite the existing comparison. Exact reproduction uses the source pointer `artifacts/binding/backend_reference_source.json` and the verified snapshot launcher, with distinct output paths for a new attempt. All chosen token IDs, stop reasons, top-two logit margins, generation settings and baseline hashes are preserved by the reference run.

`evaluate-heldout --config ...` requires a genuinely frozen analysis registration and hashed forecast file. The configuration must pin both `registration_sha256` and `frozen_predictions_sha256`. Required registration fields are listed in `src/codecue/binding/heldout.py`; there is no valid scientific registration yet. Predictions must cover every primary test ID exactly once with probabilities for `A_input`, `B_behavior`, `C_measurements`, and `cheap_stress_test`. The evaluator refuses implicit exclusions and reports invalid observed outputs separately. The new `fit-forecasters` and `write-forecasts` interfaces implement nested logistic fitting and registered forecast generation; see [the exact contracts](predictors.md). There is no empirical C predictor without discovery evidence.

For queued experiments, freeze source and configuration before submission. The verified launcher runs that copy even when the working tree changes:

```bash
python -m codecue.binding freeze-source
# Use the returned absolute snapshot path for SNAPSHOT below.
python SNAPSHOT/scripts/91_binding_frozen_run.py SNAPSHOT module run-behavior --config SNAPSHOT/configs/binding/cpu_smoke_prefill_v2.json
python -m codecue.binding verify-source --run SNAPSHOT
```

`cpu_probes_centered_v3.json` explicitly pins the extraction source hash when reusing an earlier immutable cache for corrected analysis. It writes a separate stage and records the upstream cache identity and index hash; capture-affecting config changes are refused. The correction centers masked training rows per output and gives surface baselines only the source prefix visible at each site.

Generate and validate each reserved structural cohort using its `configs/binding/extrapolation_{depth,distance,competition,combined}_full.json` configuration. They use test-only generator version 6, while version 5 remains byte-identical. All full cohorts and the separate smaller structural smoke fixtures have passed semantic validation. Their model outcomes remain sealed. No new-family cohort exists yet.

Regenerate the discovery report from available artifacts without running inference or opening heldout outcomes:

```bash
python scripts/92_binding_progress_report.py
```

Current baseline datasets are `smoke_matched.*` and `pilot_matched.*`; reserved structures are `extrapolation_*.*`. Earlier `*_v*` and `*_final.*` files were development fixtures and are excluded from analysis. JSONL datasets and immutable source copies remain locally available but are ignored by Git. No unrelated artifacts were removed.
