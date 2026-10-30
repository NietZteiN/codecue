# Implementation checklist

**Start here: [Master research report — plan, results, figures and next steps](../../docs/binding/MASTER_REPORT.md)** ([Markdown version](master_research_report_v3.md)). Updated October 29, 2026; includes the full original plan, 18 main figures, including three conceptual illustrations, the complete figure archive, every research branch and an ordered next-experiment plan.

The [October 28–29 old-value suite](old_value_overnight_findings_v1.md) completed **40,320 audited responses**. Llama 8B scored **60.9%** overall and CodeLlama 34B **23.5%**; both failed all 24 fixed reliability cells. The [response diagnostics](old_value_postrun_response_diagnostics_v1.md) reconcile every score and oracle, identify CodeLlama’s formatting errors, and quantify Llama’s current-value answers on historical questions.

The [post-run debug follow-up](old_value_overnight_followup_v1.md) records the **2,280-test** completed-run regression, **90 focused operational tests**, repaired logging timeouts and auxiliary-job failure reporting. Three checks covered the running suite; its monitor stopped after completion. Automatic logging continues. The [October 29 morning/daytime verification](old_value_overnight_daytime_check_20261029_v1.md) confirms that the independent snapshot **completed at 08:00**, and all seven suite stages exited successfully. The [74-task inventory](preparation_readiness.md) has **62 ready / 9 scientific / 3 optional** items. See [live status](old_value_overnight_status_v1.md).

The [format-only repair bound](old_value_format_ceiling_v1.md) shows that even making every invalid saved answer correct leaves **16/24 CodeLlama** and **24/24 Llama** primary cells below 90% accuracy. Every historical-question cell remains below threshold. This is a bound on saved responses, not a limit on what changed prompts could achieve; original scores and gates stay fixed.

The [bounded saved-score grammar diagnostic](identity_grammar_interpretation_v1.md) is complete and audited across **60 banks and 86,400 DEV bank-case rows**, with **zero new model calls, fits or parameter applications**. All **2,191 tests** and the exact **106-file source archive** passed. Owner-only grammar gives **25.556% / 46.204%** all-eight recovery for 8B / 34B; explicit source owners plus counters give **100%**. Joint grammar improves free joint but falls below the original marginal rule on 34B. These are decoder-assisted reconstruction results, with natural causal use unresolved. The [updated inventory](preparation_readiness.md) records **71 tasks: 59 ready / 9 scientific / 3 optional**. Earlier completed studies below retain their historical counts.

The completed [direct owner/version identity study](direct_identity_findings_v1.md) has a mixed comparison with the stronger source-owner plus weighted TRAIN-version-prior baseline. At fixed layer 24/site 7, hidden whole-write joint recovery exceeds the prior, while whole-parent joint recovery falls below it. Each task requires all listed event identities correct; points average the three fixed weighting seeds.

| Whole joint task | Llama 8B | CodeLlama 34B | Source-owner / TRAIN-version prior |
|---|---:|---:|---:|
| Four writes | 28.519% | 35.463% | 11.111% |
| Four parents | 24.630% | 30.093% | 40.000% |
| All eight | 6.019% | 13.056% | 2.222% |

Factorized-parent recovery is **28.889% / 45.093%** for 8B / 34B, a secondary marginal-argmax result. Joint heads have 16 nominal outputs versus 8 component outputs; shared linear ridge makes the component scores joint-score marginal sums, so this does not compare independent representations or provide a clean capacity test. See the [linearity clarification](direct_identity_linearity_note_v1.md). All **192 targets** use a fixed global owner/version codebook without a per-program source map after prediction. Rare final-parent version-4 classes remain evaluated with only **two TRAIN graph families**. These adaptive accessibility results do not establish causal binding; see the [decision](direct_identity_decision_v1.md) and [plan](direct_identity_plan_v1.md).

All four jobs completed successfully, retaining **60 banks, 60 factorizations and 345,600 exact parameter-row replays**, with **zero additional GPU allocations or model queries**. All **2,129 binding tests** and the exact **104-file source archive** passed. Publication passed **35 synthetic checks**, retained **1,440 cells** and reproduced identical bytes twice. The final [105-pin handoff](../../artifacts/binding/direct_identity/20261028_v1/handoff_review_v1.json) and refreshed [inventory](preparation_readiness.md) record **70 tasks: 58 ready / 9 scientific / 3 optional**. All nine scientific decisions remain open.

### Saved-score grammar continuation (October 28)

- [x] Build the exact score-only copy/version DP with broad and no-self grammars and joint/owner-only evidence.
- [x] Pass 62 focused checks and independent source/synthetic review.
- [x] Freeze source, pass all 2,191 regression tests and verify the exact 106-file source archive.
- [x] Reproduce original metrics for all 60 banks and preserve all 86,400 DEV bank-case rows.
- [x] Independently replay every prediction, exact objective and metric from retained scores without reopening original score banks.
- [x] Pass 14 publication checks, retain all 960 rule cells and reproduce publication bytes.
- [x] Verify all artifact pins, inspect the chart, log completion and refresh readiness to 59 ready out of 71.


### Direct identity continuation (October 28)

- [x] Build 192 categorical target columns and 24 heads for assignment/parent joint identities and separate owner/version components; preserve the fixed global codebook and parent read-time reference.
- [x] Validate all 5,760 source records, prefix-consistent coherent sham targets, all class/group support and source-only baseline checks; retain rare final-parent version-4 classes with two TRAIN families.
- [x] Verify initialization site 3 has no defined event targets and fit only sites 7/8 through the original capture axes; preserve earlier source snapshots and outputs.
- [x] Pass 41 new focused tests and the 42-test combined readout/compatibility suite (13 new and 29 existing cases), including historical default-byte checks and synthetic saved-parameter replay.
- [x] Freeze the source, plan and configurations; submit regression and both dependent CPU readout workers without new model queries or GPU captures.
- [x] Document the source-owner/TRAIN-version baseline and the linear ridge score-marginal relationship before fitting.
- [x] Complete the 2,129-test full regression and exact 104-file test-source archive check (job 481539 passed).
- [x] Complete and audit all 60 fitted banks, 60 factorizations and 345,600 parameter-row replays across both models; both CPU workers completed successfully.
- [x] Pass 35 publication synthetic checks, retain all 1,440 cells and reproduce publication bytes twice; complete independent review and the 105-pin final handoff.
- [x] Complete automatic closure and refresh readiness to 70 tasks: 58 ready, nine scientific and three optional; all four jobs completed successfully and the nine scientific decisions remain open.

The preceding completed [source-oracle-assisted identity review](diversity_identity_review_findings_v1.md) retains an important baseline: choosing fixed roots gives the current-definition TRAIN prior **100% owner accuracy**, but only **41.667% exact-definition and source-mapped version accuracy**. Owner accuracy alone does not establish learned binding. Source maps provide the semantic interpretation. At the fixed layer 24/site 7 endpoint, pooled four-head decisions give exact definitions **86.782% / 91.227%** and exact parents **76.250% / 81.898%** for Llama 8B / CodeLlama 34B. These rates pool individual decisions; whole-state recovery requires all four to be correct. See the [decision](diversity_identity_review_decision_v1.md) and [plan](diversity_identity_review_plan_v1.md).

All three review jobs completed and audited **90 saved-score banks, 518,400 score-case rows checked and 129,600 DEV prediction rows**, with **zero new model calls, fits or parameter applications**. All **2,088 binding tests** and the exact 102-file test-source archive passed. That checkpoint's final [readiness](preparation_readiness.md) was **69 tasks: 57 ready / 9 scientific / 3 optional**. All nine scientific claims remain open.

The preceding [diversity decoding study](diversity_decoding_findings_v1.md) completed all eight jobs: **11,520 distinct and actual prefills, no generated answers or retries, 90 readout banks and 518,400 exact parameter-row replays**. Fixed layer-24/site7 whole current-definition/version/copy-parent recovery is **56.389% / 22.870% / 30.370%** for Llama 8B and **69.815% / 35.093% / 37.222%** for CodeLlama 34B. Source baselines are lower; decoder accessibility does not establish natural causal binding or version tracking. Its frozen source passed **2,044 binding tests**. See the [decision](diversity_decoding_decision_v1.md) and [plan](diversity_decoding_plan_v1.md).

### Diversity decoding continuation (October 28)

- [x] Implement isolated target, capture and readout adapters for the published 5,760-row bank, preserving the existing 232 target tasks and earlier frozen science.
- [x] Validate all capture-whitelisted source records at all three sites and control seeds 17/29/43; retain masks, prefix consistency, changed control marginals and all-slot version support.
- [x] Pass 70 new focused checks and all 2,044 binding tests; complete both 5,760-case native preparations.
- [x] Freeze the plan/configurations and submit both GPU captures and dependent readout/audit workers for the full cohort.
- [x] Complete and audit 11,520 distinct and actual prefills, preserving prefix checks; no retries or answers were generated.
- [x] Complete and audit all 90 readout banks and 518,400 parameter-row replays, retaining all baselines, layers, seeds and classes.
- [x] Complete independent review, reproducible publication, readiness refresh and the 47-pin final handoff; all eight jobs exited successfully.

### Source-oracle-assisted identity continuation (October 28)

- [x] Implement capture-checkpoint versus consumer-read-time owner/version diagnostics; pass 29 core and 15 runner checks without new model calls, fits or parameter applications.
- [x] Validate oracle-truth predictions on all 1,440 DEV cases at three sites, including 1,248 correct parent labels per final site that become obsolete by capture time.
- [x] Freeze the posthoc plan/source and queue full regression and the dependent saved-score analysis.
- [x] Complete and certify all 2,088 binding tests and the exact 102-file test-source archive.
- [x] Complete and audit the 90-bank source-assisted diagnostics: check 518,400 saved-score case rows and preserve 129,600 DEV prediction rows, scalar-version heads and the separate original sham task; add no model calls, fits or parameter applications.
- [x] Complete the automatic metadata-only finish worker, publication, final 69-task readiness refresh and the 211-pin handoff; all three jobs exited successfully.
- [x] Preserve the fixed-root TRAIN-prior owner baseline, explicit source-oracle assistance and pooled-head versus whole-state distinction; leave the nine scientific claims open.

The preceding [posthoc saved-score review](schedule_score_review_summary_v1.md) completed all **90 banks and 540 query-effect cells** without new model calls or fits. Fixed-target query effects vary across five graph families; the equal-graph primary definition effects are **−1.335 / +2.604 percentage points**, with zero pre-query prediction changes. Its [source-only overwrite preparation](relationship_schedule_diversity_preparation_v1.md) produced **5,760 programs, 60 new canonical graph families, versions 1–4 in every slot and 8,640 independent Python trace checks**. That checkpoint passed **1,974 binding tests** and recorded **53 ready / 9 scientific / 3 optional** items in its 65-task inventory.

### Saved-score diagnostics and broader overwrite preparation (October 28)

- [x] Reproduce original metrics from all 90 saved score banks; preserve DEV class confusions, joint correctness masses, all baselines and numerical score differences.
- [x] Audit same-body, fixed-target comparisons over 174 DEV query quads and 696 dependent body/target units; retain every site, layer and weighting seed, including pre-query placebos.
- [x] Independently verify 540 query-effect cells, publish reproducible tables and four-panel figures, and preserve heterogeneous graph effects without a causal claim.
- [x] Prepare 60 canonical overwrite families absent from both named prior banks, with 45 TRAIN / 15 DEV families, four slot rotations and all-slot version coverage.
- [x] Document why the initially proposed fully updated profile was exhausted by the earlier routing universe; validate the revised profiles without weakening graph novelty.
- [x] Validate all 5,760 sources and 8,640 ordinary-Python traces; pass the full 1,974-test regression and maintain automatic logging.

That checkpoint established source/oracle preparation. Its completed learned study and audited source-assisted postmetrics are tracked above; general owner/version and causal-mechanism work remains open.

### Dynamic schedule decoding continuation (October 28)

- [x] Implement source-derived 232-column targets for actual current definitions, versions, direct/transitive dependencies and final-query ancestry; retain rare and constant classes.
- [x] Validate all 2,016 rows, TRAIN-only support and prefix-consistent random-task controls; pass 79 focused checks and the complete 1,922-test regression.
- [x] Freeze the source and configurations, and complete both native tokenizer preparations without model calls.
- [x] Queue both GPU captures, both dependent readout/audit workers, and automatic independent review, reproducible tables/figures and a completed handoff.
- [x] Complete the two 2,016-case GPU captures; preserve actual retry counts and source-prefix audits. There were no retries and no generated responses.
- [x] Complete and audit all 90 fixed readout banks, comparing hidden, surface, TRAIN-prior and source-keyed control tasks without claiming a causal mechanism.

The preceding [computation/context/copy calibration](computation_routing_findings_v1.md) completed **40,200 scored responses** with **0/6 prospective reliability gates qualified**. Its completed negative results remain preserved.

### Computation and schedule continuation (October 28)

- [x] Build and independently validate 6,700 unique computation/context/copy sources representing 6,912 matched views, with explicit control reuse and at least 30 unique sources per prospective gate cell.
- [x] Complete both native preparations, 40,200 scored responses, 16 separately counted warm-ups, all audits and the complete six-gate decision. All gates failed; no fallback or causal qualification is selected.
- [x] Build and independently validate 2,016 varied-schedule sources with actual SSA/read-from/current/obsolete labels through version 4; preserve all canonical-family splits and explicit incompatibility with the old learned targets.

The existing general owner/version, mechanism and unfamiliar-program tasks remain open.

Earlier checkpoints below retain their historical task and test counts.

Overnight continuation, October 27–28: **all 14 stages completed** on both cached checkpoints, with **32,076 captures, 14,580 generated responses, 270 probe fits, 1,574,640 exact row replays and 524,880 literal-to-computed parameter applications**. See the [consolidated findings](overnight_20261027_findings_v1.md) and [completed stage status](overnight_20261027_status.md). The [posthoc score/answer and fixed-target matched-query analysis](overnight_score_behavior_findings_v1.md) is complete and audited on 4,860 DEV rows without new model calls or fits. All **1,766 binding tests pass**. The [current 57-task inventory](preparation_readiness.md) has **45 ready / 9 scientific / 3 optional** items; completion does not establish natural causal use or general version recovery.

Structural and algebraic relationship readouts and posthoc controls are complete: **83.488% whole-graph recovery**, **85.019% algebraic balanced accuracy**, and **96.759% both-first-parent recovery on equal-state pairs**. The stronger source-value pipeline scores **98.108%**, exceeding hidden direct algebraic decoding. See the [findings](relationship_results_findings_v1.md) and [figure](figures/relationship_controls_v1.png). All seven execution jobs completed and all **1,602 binding tests pass**. Current readiness: **39 ready / 9 scientific / 3 optional**, 51 tasks. These remain discovery results under a fixed program scaffold; broader causal/version and final-prediction work remains open.

Both relationship branches are now active: prefix-safe **dependency/version targets** and **algebraic targets** for equality, ordering, signed differences and sum/subtraction triples. The balanced numeric-control bank has **1,944 source programs** and supports both target families on the same examples. It reuses the earlier routing bank’s 81 graphs and 27 components, so it is not independent structural replication. See the [broader relationship plan](relationship_decoding_plan_v2.md) and [combined preparation findings](relationship_preparation_findings_v2.md). **Learned relationship decoders remain untrained**; source/target validation is complete. The full suite passes **1,370 tests**, and the [current inventory](preparation_readiness.md) records **36 ready tasks out of 48**, nine scientific decisions and three optional deferred tasks. The [combined handoff](../../artifacts/binding/relationships/handoff_review_v2.json) retains source, target, test and logging identities.

Earlier dependency/version preparation, 2026-10-27: versioned def-use, transitive ancestry, assignment succession and explicitly visible output ancestry now have prefix-safe labels. A new copy-routing bank contains **1,296 source programs, 81 directed graphs and 432 equal-value/different-provenance pairs**, with full graphs separated across 18 training and nine development components. The old banks were largely fixed by family/update schedule. See the [relationship plan](relationship_decoding_plan.md) and [preparation findings](relationship_preparation_findings.md). **Learned relationship decoding remains unfinished**; oracle targets and source preparation do not count as recovered model representations. The full suite passes **1,302 tests**; the [current readiness inventory](preparation_readiness.md) records **35 ready tasks out of 47**, nine scientific decisions and three optional deferred tasks.

Completed queried/unqueried accessibility follow-up, 2026-10-27: **45 weighted-ridge factorizations**, **180 independent matched-capacity heads** and **414,720 exact saved-model row replays** on an existing 9,216-row capture bank. At the fixed neutral block-24 `pre_answer` cell, queried-value accuracy is **88.89%**, versus **9.4184%** for the unqueried value: **79.4705 percentage points**, with conditional group interval **[75.8670, 83.5069]**. See the [findings](query_selectivity_findings.md), [PNG curves](query_selectivity_curves_v1.png) and [SVG curves](query_selectivity_curves_v1.svg). This is decoder-specific accessibility on consumed structures; value disposal, natural causal use, ownership, tracking/reconstruction and mechanism C remain unestablished. No new language-model calls were made. The [46-task readiness report](preparation_readiness.md) has **34 ready**, nine scientific decisions and three optional deferred tasks. The full binding regression suite passes **1,191 tests**; the compact completion manifest fixes audit/reuse of large scientific results while preserving every original fit artifact. Exact source, artifact, test and job identities are retained in the [machine-readable handoff](../../artifacts/binding/query_selectivity/handoff_review_v2.json).

Earlier assignment-cue behavioral comparator checkpoint, 2026-10-27: **12,288 full responses**, 256 qualification responses, **20,412 corrected-analysis logistic fits** and **1,024 passing tests**. Gains are context-dependent, with no clear Brier advantage over joint confidence in any of ten matched contexts. All 847,872 parent probabilities replay exactly; a documented iteration-allowance correction resolved one initial fit failure. See the [findings](stress_comparator_findings.md), [all comparisons](stress_prediction_decision_v2.md), [numerical correction](stress_comparator_numerics_v2.md), and [current readiness report](preparation_readiness.md). That earlier checkpoint had 33 ready tasks, nine scientific decisions and three optional deferred tasks. Automatic logging retains the failed/canceled first attempts alongside completed runs.

Earlier joint-confidence and representation checkpoint, 2026-10-27: **16,632 logistic fits**, **336 readout fits**, exact replay and **932 passing tests**. Combining confidence bundles improves CodeLlama in two fixed contexts; alignment helps some individual-slot readouts without establishing whole-state recovery or a mechanism. See the [joint/representation findings](continuation_followup.md), [joint table](joint_confidence_decision.md), [representation report](representation_sensitivity_v1.md), and [current readiness report](preparation_readiness.md). That earlier checkpoint had 32 ready tasks, nine scientific decisions and three optional deferred tasks. All six new SLURM jobs completed successfully. Automatic result logging is enabled, with bounded large-file notices separated from errors.

Earlier confidence checkpoint, 2026-10-27: both candidate-event collections and the 18-tier/37-contrast comparison are complete. Across the two new analyses, 21,924 logistic fits passed exact baseline replay checks. CodeLlama benefits from next-token confidence beyond strong source features, but the more costly candidate-event alternatives show no clear Brier improvement over next-token confidence in any of the ten fixed contexts. See the [findings](candidate_prediction_findings.md), [all results](candidate_prediction_decision.md), and [current readiness report](preparation_readiness.md). The full suite passed **852 tests**; all qualified collection/prediction jobs completed, with automatic aggregation and logging. That checkpoint had 30 ready tasks, 10 scientific decisions and three optional deferred tasks. Source hashes, validation and scheduler accounting are in the [machine-readable handoff](../../artifacts/binding/discovery_confidence/handoff_review_v1.json).

Confidence follow-up, 2026-10-27: the [13-tier discovery comparison](discovery_confidence_decision.md) completed 9,072 logistic fits with every original baseline reproduced exactly. Confidence lowers CodeLlama Brier from 0.123574 to 0.116641 beyond source interactions; Llama's Brier increment is smaller and uncertain, while log loss improves. The [fixed-contrast figure](discovery_confidence_increments_v2.svg), all scores and source/access contracts are retained. The earlier 13-tier checkpoint passed **796 tests**. Both whole-bank candidate tokenizer QAs and FP32 parity smokes passed; both 6,144-row full-answer banks subsequently completed and passed audit, as recorded above. The [primary-source review](submission_novelty_review.md) covers the original twelve reference identifiers plus two confidence papers, with version flags and explicit claim limits.

Expanded preparation update, 2026-10-26: see the [preparation portfolio](preparation_portfolio.md) and [current 46-task readiness inventory](preparation_readiness.md). Nine new discovery banks (30,960 source records), complete content-overlap audits and 240 precision scenarios are built; both exact-prompt confidence collections completed and passed audit (12,288 prefill measurements). Candidate-answer scoring, train-only alignment/reduced-rank helpers and registration-readiness tools are implemented. The inventory distinguishes built software from executed measurements and scientific qualification.

The [full research agenda](research_backlog.md) tracks the original hypotheses, ten experiments, representation/pathway studies and explicit training, explanation-transfer and unlearning extensions. The milestones below alone do not represent completion of that larger agenda.

Current status, 2026-10-27, mapped to the original milestones in `dependvar.txt` §11:

| Original milestone | Current status | Evidence or remaining work |
|---|---|---|
| M0: repository and resource audit | Complete | Existing CodeCue assets, model/cache access, instrumentation, environment and scheduler resources inspected. |
| M1: generator and semantic oracle | Complete | Three restricted-program families, semantic renaming, version/def-use labels, grouped splits, independent Python checks and counterfactual validation implemented. Later discovery banks have separate manifests and scope. |
| M2: behavioral smoke and pilot | Complete, with mixed feasibility | Original CodeLlama 7B pilot and calibration completed; later cached-checkpoint and published-benchmark suites completed. Arithmetic-free discovery qualified on CodeLlama 34B and Llama 3.1 8B. The original arithmetic gates and newer computed-family gates failed and remain recorded. |
| M3: representation diagnostics | Implemented and run; interpretation limited | Original probes plus two 9,216-case capture banks and three later readout suites completed. Recovery depends on site and literal proximity. A 75-fit frequency-matched grouped-shuffle follow-up repairs the earlier identifier-control label mismatch, with exact original-value prediction replay. The newer 45-factorization/180-head query-selectivity study matches class marginals and per-head capacity and retains every layer/site/naming cell; its large queried/unqueried gap is decoder-specific accessibility. No general state-tracking, information-disposal or selective binding-code conclusion is established. |
| M4: focused intervention study | Exploratory assays completed; mechanism unresolved | Digit-aligned literal, late-reference and 96,768 fresh-pair single/joint copy-site interventions passed their software/norm controls. The nominated block-8 ownership effects are weak and nonselective. Local literal effects are supported; owner specificity is mixed and late reset changes did not repair swap errors. Computed interventions were skipped after their registered behavioral gate failed. |
| M5: frozen prediction on unfamiliar programs | Discovery baselines and capacity/access controls run; frozen final validation not run | Source-only, neutral-query and explicitly oracle-assisted tiers completed exploratory grouped CV on 12,288 consumed targets. Fixed interactions and identical-information encoding controls clarify the earlier gain; original baselines reproduce exactly. No supported explanatory account, empirical mechanism C or confirmatory comparison has been registered. Final/extrapolation outcomes remain sealed. |
| M6: paper decision | Decision memos complete; scientific contribution unresolved | Current memos distinguish local findings, negative results and unresolved claims. A general causal binding explanation and incremental unfamiliar-program prediction are not established. |

Negative or inconclusive results are valid completed experiments; they do not require a positive mechanism claim. The central outstanding scientific objective is an explanation that survives specific counterfactual tests and improves prediction beyond behavioral/input baselines on unfamiliar programs.

Latest completed evidence includes the [source-oracle-assisted identity diagnostics](diversity_identity_review_findings_v1.md), [60-family diversity decoding study](diversity_decoding_findings_v1.md), [fixed-target saved-score review](schedule_score_review_summary_v1.md), [varied-schedule decoding](schedule_decoding_findings_v1.md), the [computation and routing calibration](computation_routing_findings_v1.md), [capacity/oracle-access controls](discovery_controls_decision.md), [discovery failure baselines](discovery_prediction_decision.md), [arithmetic/readout discovery](arithmetic_readout_decision.md), and [ownership/cue controls](mechanism_followup_decision.md). The completed diversity source passed **2,044 tests**; the identity extension passed 44 focused checks and the latest **2,088-test full regression**, with its 102-file test-source archive verified. The computed-retention and arithmetic/readout reliability failures remain preserved. Discovery-only prediction completed 2,268 initial logistic fits and 5,292 capacity/access sensitivity fits on the same 12,288 cached transformed targets. Original baselines reproduce exactly. All diversity execution/publication jobs and all three source-assisted review jobs completed and passed audit. Automatic logging is enabled. No language-model training was performed.

## Current consolidated checklist

Checked means the specified implementation or experiment was completed, including negative or inconclusive experiments. Unchecked means the work or claim remains unfinished. The original failed gates are preserved; final/extrapolation model outcomes remain sealed.

### Infrastructure, datasets and reproducibility

- [x] Audit the existing CodeCue repository, manuscript, environment, model cache and scheduler.
- [x] Implement the three original generator families: parallel chains, snapshots/overwrites and interleaved accumulators.
- [x] Implement restricted-AST execution, versioned bindings, direct/transitive dependencies, liveness and diagnostic distractors.
- [x] Validate rendered execution traces and lawful counterfactuals against independent Python execution.
- [x] Implement semantic renaming, computed-value controls, noncommutative outputs and same-value-multiset/different-owner pairs.
- [x] Build the 38,016-prompt computed-retention bank: fixed eight defined variables, 2/3/4 functional live bindings, matched schedules and independently checked checkpoint interventions.
- [x] Implement structural splits, grouped relatives, stable identities, deduplication, manifests and identifier-vocabulary audits.
- [x] Record raw generations, invalid outputs, ambiguous counterfactual-consistent error labels and per-cell counts.
- [x] Correct tokenizer/serialization and answer-boundary errors; preserve the original erroneous or historical runs separately.
- [x] Validate hooks, causal prefixes, fixed token geometry, replay identity and effective BF16 perturbation norms.
- [x] Freeze source/configuration snapshots and enforce compatible resumes and artifact checksums.
- [x] Automatically journal experiment/job lifecycles and result metadata; backfill historical runs and export a [dashboard and complete CSV](experiment_log.md), with periodic CPU scheduler reconciliation and sealed-outcome exclusions. See the [logging guide](experiment_logging.md).
- [x] Remove project GPU-hour/stage/checkpoint/concurrency caps; retain usage accounting and actual scheduler constraints.
- [x] Profile GPU throughput, use larger validated batches, and run independent finite jobs on eligible hardware.
- [x] Keep activation storage under its separate policy and preserve sealed final/extrapolation outcomes.
- [x] Pass the frozen diversity study's 2,044-test full regression suite, earlier focused maintenance checks and completed experiment audits.
- [x] Certify the new identity extension's latest 2,088-test full regression and exact test-source archive.

### The ten authorized experiments

| Experiment | Updated completion status |
|---|---|
| 1. Checkpoint and official prompt audit | Complete, including tokenizer, serialization and backend corrections. |
| 2. Arithmetic versus program execution | Behavioral studies complete; the original computed-program reliability gates failed. |
| 3. Arithmetic-free binding | Complete across cached checkpoints; CodeLlama 34B and Llama 3.1 8B qualified for scoped discovery. |
| 4. Binding and version competition | Arithmetic-free discovery and the computed-retention behavioral study complete; computed reliability/generalization unresolved. |
| 5. Naming × competition × updates | Scoped naming/version/distance experiments complete; a computed 2/3/4-live-binding scheduling factorial also completed, but failed reliability gates and remains coupled to computation timing/distance; the original explanatory claim is unfinished. |
| 6. Tracking versus reconstruction | Timing and common-final-query controls complete; an identified algorithm and selective causal route remain unresolved. |
| 7. Distributed-state probe diagnostics | Capture banks, readouts, 75 frequency-matched control fits and the 45-factorization/180-head queried/unqueried comparison complete. Decoder-specific accessibility is measured; general state representation and natural causal use remain unresolved. |
| 8. Value, ownership and pathway interventions | Multiple audited assays complete; selective ownership/version/pathway mechanism unresolved. |
| 9. Frozen failure prediction | Software and reserved datasets ready; empirical input/neutral-query discovery baselines completed. Mechanism C, genuine final registration and untouched scoring not run. |
| 10. Second-family replication | Behavioral comparison complete; causal-mechanism replication not run. |

### Behavioral studies and external datasets

- [x] Complete the original pilot, prompt calibration, arithmetic controls, difficulty ladder and failed-gate decisions.
- [x] Complete the four-checkpoint capacity program: 20,152 predictions.
- [x] Retrieve and pin published CRUXEval/BBH data; complete published-benchmark and serialization/interface evaluations.
- [x] Complete two-family arithmetic-free competition discovery: 19,968 responses.
- [x] Complete three-instruction timing/equivalent-copy studies: 4,536 baselines and 90,720 intervention forwards.
- [x] Complete fresh ownership/common-final-query studies: 7,776 baselines and 96,768 intervention forwards.
- [x] Complete and audit both computed-retention model runs: 76,032 predictions, all registered contrasts and both failed reliability gates preserved.
- [x] Complete corrected 396-case-per-model backend replays and 24 uncached arithmetic controls; fix and archive the diagnostic prompt/completion stop-boundary error.
- [x] Register and independently validate the fresh 3,072-program [arithmetic/readout bank](arithmetic_readout_plan.md): eight matched-answer 0/1/3-operation forms, six signed strata, disjoint nonzero prompts and explicit repeated zero-operation controls; pass both tokenizer preflights and 322 regression tests.
- [x] Revalidate 768 existing two-operation calibration responses and retain every form/operator/sign/split cell as [context](arithmetic_readout_prior_context.md).
- [x] Complete and audit the fresh arithmetic/readout study on both cached models: 12,288 responses, separate direct/trace gates, automatic comparison and figure export; all four reliability gates failed. See the [decision](arithmetic_readout_decision.md).
- [ ] Establish a reliable computed-program regime for the full original explanatory study.
- [ ] Isolate genuinely output-relevant live-variable load from irrelevant competitors, with matched arithmetic and surface controls.
- [ ] Complete the original naming × relevant load × reassignment interaction study in that regime.

### Representation diagnostics

- [x] Implement and measure current, previous-version, whole-state and value-multiset recovery in the original pilot.
- [x] Complete two 9,216-case discovery capture banks and the original three later readout suites.
- [x] Fit neutral-training probes with train-only preprocessing, fixed regularization, surface/prior controls and naming-transfer evaluation.
- [x] Complete the fixed regularization sensitivity and saved-weight replay checks.
- [x] Audit the old identifier control and identify its two-label versus value-label difficulty mismatch.
- [x] Complete 75 grouped shuffled-label fits with exact class-frequency/entropy matching and all original value predictions reproduced.
- [x] Report complete layer/site/naming curves, label support, literal-proximity effects and measurement-boundary limitations.
- [x] Complete the [queried/unqueried accessibility study](query_selectivity_findings.md): retain reciprocal query twins, all four 32-class heads, matched grouped-shuffle controls, raw 4,096-dimensional hidden/surface features and all 45 fixed layer/site/backend/seed fits; replay 414,720 saved-model rows exactly.
- [x] Report the fixed block-24 neutral `pre_answer` gap and six-component conditional interval alongside every naming condition and layer/site curve; preserve the limits on information absence, natural causal use, ownership and tracking/reconstruction.
- [ ] Establish robust value/owner/version recovery beyond literal proximity and query preparation on unfamiliar structures.
- [ ] Resolve lexical/structural transfer failures with appropriately matched controls.
- [x] Complete the declared 336-fit projection/rank/alignment sensitivity; preserve its projection limits and distinguish it from the later full-dimensional queried/unqueried accessibility study.
- [x] Build prefix-safe versioned relationship labels, audit historical graph variation, and validate a 1,296-row/81-graph copy-routing bank with 432 value-matched provenance controls. See the [preparation findings](relationship_preparation_findings.md).
- [x] Build algebraic equality/order/difference and sum/subtraction targets, validate the balanced 1,944-row numeric-control bank, and audit both target families on the same examples.
- [x] Build the shared native-token capture, fixed readout/metric controls and automatic capture→audit→fit→refresh continuation; pass the full regression and real tokenizer preflight.
- [x] Train and evaluate structural and algebraic relationship decoders on the fixed discovery bank, including surface/prior/coherent-shuffle controls and relations derived from independently decoded values; complete all 45 fits and 87,480 replays. Preserve the stronger source-value baseline, literal/scaffold limitations and position sensitivity in the [findings](relationship_results_findings_v1.md). General causal owner/version claims remain open.
- [x] Complete the posthoc stronger-source, equal-state provenance-pair and unconstrained graph-validity controls on 18 pinned saved-score banks; preserve all original primaries and add zero model queries or fits.

### Overnight relationship continuation (October 27–28)

- [x] Build the shared 16,038-row discovery union, three 5,832-row views, matched computed twins and independent ordinary-Python/target-support checks.
- [x] Freeze the two-model plan and execution source; submit durable preparation and supervision jobs; pass both native-tokenizer preparations and all 1,733 regression tests.
- [x] Complete both frozen GPU captures and 14,580 greedy full-answer evaluations.
- [x] Complete six readout panels, all 270 declared factorizations, saved-parameter replays and literal-to-computed transfer applications.
- [x] Review the automatically aggregated morning results, including source-value controls, query strata and familiar-scaffold limitations; publish checksum-pinned summary JSON/CSV, report and inspected PNG/SVG.
- [x] Complete and audit the [posthoc exact-ID score/answer and fixed-target query analysis](overnight_score_behavior_findings_v1.md), preserving fit-averaged joint masses and conditional denominator checks.

### Interventions, timing and explanation specificity

- [x] Complete digit-aligned literal routing: 432 baselines and 20,160 intervention forwards, plus reciprocal/unchanged-answer controls.
- [x] Complete computed/late-reference follow-ups: computed gates failed; the eligible reset assay and its controls completed.
- [x] Test independent-statement reordering and consistent scratch renaming with earlier-copy transfers.
- [x] Test fresh value pairings with separate/joint copy patches, both quantity queries, spatial/wrong-version/random/sham controls and analytic final-layer checks.
- [x] Cross early/late queries with an identical final query and audit exact original-input replay differences.
- [x] Report null/mixed effects: nominated ownership-site effects are weak/nonselective; the late-query advantage shrinks from 13.04 to 1.70 percentage points with the final cue.
- [ ] Identify a reproducible account distinguishing binding interference, computation/accessibility, failure to use information, reconstruction and harmless representational change.
- [ ] Demonstrate selective owner/version effects on predicted descendants while preserving unrelated quantities.
- [ ] Distinguish tracking from reconstruction using selective causal-route tests, beyond cue-placement behavior alone.
- [ ] Replicate a selected causal effect on an independently generated structural cohort and a second model family.

### Frozen prediction and unfamiliar programs

- [x] Complete discovery confidence prediction with 13 tiers, 9,072 logistic fits and 24 fixed contrasts; reproduce all 294,912 baseline probabilities exactly and retain train-only preprocessing, proper scores and calibration outputs.

- [x] Implement nested predictor fitting, train-only normalization, development selection, immutable registration/forecasts, calibration and clustered scoring.
- [x] Reject declared sealed or mismatched forecasting inputs before opening outcomes; retain legacy discovery support and strict response-ID checks, with 44 focused fitting/measurement checks passing.
- [x] Complete exploratory source-only versus distinct-neutral-query failure baselines on both checkpoints: 12,288 cached targets, six outer/five inner structural folds, three fixed partition seeds, 2,268 logistic fits, raw versus oracle-scored access and all proper-score/calibration outputs preserved. See the [decision](discovery_prediction_decision.md).
- [x] Complete 5,292 further logistic fits across eight fixed capacity/access tiers; preserve original baseline probabilities, folds and fitted parameters exactly. Distinguish oracle access from deterministic score encoding and retain all 16 registered contrasts. See the [control decision](discovery_controls_decision.md).
- [x] Collect pinned source/neutral/oracle-control discovery feature tables with explicit access contracts and no target model outcome features.
- [x] Generate and independently validate four reserved structural-extrapolation banks; keep their model outcomes sealed.
- [ ] Select an evidence-supported explanatory account and define its permissible measurements.
- [ ] Register hypotheses, features, layers/sites, exclusions, ambiguity rules, query access/costs and multiplicity handling.
- [ ] Collect additional permitted confidence/internal prediction measurements under a frozen contract, without target-correctness leakage; existing source/neutral/oracle-control discovery features are complete.
- [ ] Freeze and validate model A for final unfamiliar-program prediction; exploratory input-only discovery CV is complete.
- [ ] Freeze and validate model B with its declared confidence/clean-behavior access for final prediction; distinct-neutral-query discovery baselines are complete, exact-prompt next-token confidence collection is now complete (12,288 measurements), and discovery predictor fitting is complete; final validation remains unrun.
- [ ] Fit and validate model C: the same features plus frozen internal measurements.
- [x] Complete the discovery assignment-cue behavioral comparator: 12,288 full responses plus 256 qualification responses, five ungraded extra-query features, 28 fixed tiers and 70 contrasts, 20,412 corrected-analysis logistic fits and exact 23-tier replay. The declared extra-query allowance is a scientific access control; final confirmation remains unrun.
- [ ] Freeze all forecasts before collecting/scoring final correctness outcomes.
- [ ] Evaluate greater depth/distance, higher competition and unfamiliar transformation combinations with grouped uncertainty and cost reporting.
- [ ] Add a genuinely new program family once the core result is stable; new numeric pairs do not count as a new family.
- [ ] Complete independent generation/fitting replications and precision/power planning for a confirmatory study.
- [ ] Report incremental log-loss/Brier/calibration performance, including a null result if internal measurements do not help.

### Literature, manuscript and final handoff

- [x] Inspect the existing CodeCue paper and document how this proposed study differs.
- [x] Read and compare four closest primary sources; record versions and provenance.
- [x] Produce pilot reports, decision memos, scientific figures, resource records, reproduction commands and machine-readable handoffs.
- [x] Review the original twelve primary-source identifiers and two confidence/calibration sources; record version/title/authorship discrepancies and reading limits.
- [ ] Recheck versions and claim-specific novelty before submission; the current bounded review does not establish exhaustive novelty.
- [ ] Establish the eventual supported claim's distinction from prior work; implementation differences alone do not establish novelty.
- [ ] Produce a complete binding-study manuscript grounded in the supported claim.
- [ ] Produce the unfamiliar-program predictive comparison/figure after real frozen validation exists.
- [ ] Complete submission-level reproducibility and manuscript review.

### Optional or deferred extensions

These remain subject to the original decision rules; their presence here does not launch them.

- [ ] Targeted language-model training: matched ordinary/obfuscation/binding-targeted training and shuffled-supervision controls, after a reproducible mechanism motivates it.
- [ ] Dedicated explanation-transfer project: calibrated equivalence/difference/inconclusive controls, explicit correspondences, semantic-change controls and held-out transformations. Core renaming/reordering precursors are already complete.
- [ ] Unlearning: fictional API mappings, forgetting/retention controls, retain-only adaptation reference and unseen retained-task failure prediction, after the core diagnostic is reliable.
- [ ] Human experiments or broad multilingual evaluation: outside the initial pilot.
- [ ] A large new-checkpoint download/model-sweep campaign: not started; existing cached-checkpoint evaluations are complete.

## Historical pilot record

The detailed boxes below preserve the original pilot record and precede the later checkpoint/routing studies. References there to bounded runs and a shared GPU budget describe historical execution. The user subsequently removed the project compute quota; current usage accounting is uncapped, with actual scheduler/hardware constraints still applicable.

- [x] M0: inspect existing project, scientific scope, checkpoint, dependencies and SLURM resources.
- [x] M1: three generators; AST-safe names; versioned oracle, uses, dependencies and liveness.
- [x] M1: independent Python checks of full rendered traces and counterfactual downstream states.
- [x] M1: six renderings, computed multiset swaps, arithmetic controls, stable IDs and manifests.
- [x] M1: structural/relative grouping, actual control-skeleton checks, heldout identifier-string audit.
- [x] M2 implementation: deterministic inference, raw/invalid outputs, compatible diagnostic sets, resume identity checks.
- [x] M2 implementation: balanced smoke profiling, bounded discovery pilot/subset and shared GPU budget.
- [x] M2 empirical feasibility: real CPU BF16 balanced smoke completed with parseable outputs; raw responses and descriptive report retained.
- [x] M2 broader CPU discovery: magnitude-matched subset completed; near-floor performance triggers calibration review before expansion.
- [x] Training calibration: printed short answers and separately labeled 256/512-token traces completed; no format passes the predeclared main-program gate.
- [x] Calibration data/pipeline: independently validated balanced-sign bank and conditional inference gate; inference is skipped after failed calibration.
- [x] Backend consistency: CPU FP32/BF16 and GPU BF16 compared on identical fixed training prompts, with oracle and score verification.
- [x] Generation implementation check: uncached full-prefix argmax exactly reproduces all saved GPU batch-one responses; tiny-model preflight and shared GPU accounting completed.
- [x] Difficulty ladder implementation: matched assignment/value paths, sign-balanced training data, independent Python checks and a predeclared whole-suite selection gate.
- [x] Difficulty ladder empirical calibration: both existing readouts completed, every cell reported and the declared stopping rule applied; no regime qualifies.
- [x] M3 implementation: bounded prefix-aligned extraction, shared linear decoders, baselines and development curves.
- [x] M3 empirical calibration: real CPU activations for the complete smaller discovery cohort and all development curves; saved-weight training recovery checked without refitting.
- [x] M3 main-data supplement: neutral training and all development naming conditions completed; generalization remains weak.
- [ ] M3 empirical acceptance: actual activation caches, reproducible probe controls, layer/site selection on development.
- [x] M3 analysis corrections: masked-label intercept, prefix-matched surface baseline, explicit earlier-cache pinning and separate analysis artifacts.
- [x] M3 sensitivity: full fixed regularization grid completed; alpha-one saved predictions exactly replicated.
- [x] Behavioral diagnostic prior: paired-vector shuffle reference completed without treating compatible errors as identified causes.
- [x] M4 assay implementation: computed donors, full residual transfer, negative controls, late dependent/independent quantity queries and ownership-matched donor mode.
- [ ] M4 scientific acceptance: diagnostic binding ownership intervention, dependent/independent quantities and path specificity.
- [x] M4 value-transfer calibration: all controls and late quantity queries completed; no final-answer repair established.
- [x] M5 scorer: frozen registration checks, fixed-forecast scoring, calibration and clustered improvement intervals.
- [x] M5 fitting interface: nested logistic models, train-only normalization, development penalty selection, immutable fits and registered forecast generation.
- [x] M5 data preparation: four reserved structural extrapolation cohorts generated and independently validated, with outcomes sealed.
- [ ] M5 scientific acceptance: freeze a supported explanation, fit nested predictors, fresh unfamiliar structures, confirmatory run.
- [x] Reproducibility: immutable source/config snapshots protect queued experiments; version 5 regeneration remains byte-identical.
- [x] M6 pilot decision: stop full expansion at floor; current evidence does not justify a binding-mechanism paper claim. Confirmatory prediction remains unfinished.

## Additional preparation and tooling

- [x] Inventory 50 setup, dataset, analysis, measurement, prediction and writing tasks with evidence/dependencies and scientific gates.
- [x] Build nine immutable discovery source banks totaling 30,960 rows and audit exact/canonical/structural overlap across seeds and splits.
- [x] Report reused template/base labels and conservative content components; prevent automatic pooling/confirmation claims.
- [x] Complete 240 conditional structural-group precision/detection scenarios from both checkpoints' existing discovery OOF predictions.
- [x] Build exact-saved-prompt label-free confidence collection with resumable chunks and strict scalar/provenance audit.
- [x] Prepare full 6,144-example and 128-example software-smoke confidence inputs per checkpoint.
- [x] Complete both full next-token confidence collections and audits: 12,288 total prompt measurements.
- [x] Build complete integer-plus-EOS teacher-forcing helpers with prefix and finite-support checks.
- [x] Validate all 12,288 candidate-event inputs using real pinned tokenizers; qualify cached scoring with per-event/scalar FP32 parity after recording the BF16 and joint-boundary failures.
- [x] Complete both full finite-candidate likelihood collections and aggregate audit: 12,288 prompts; no generated answers or correctness features.
- [x] Complete the 18-tier/37-contrast candidate-event prediction comparison, 12,852 logistic fits and exact 13-tier replay; preserve the null Brier comparison against next-token confidence.
- [x] Build train-only Procrustes and mathematically constrained reduced-rank ridge helpers with synthetic objective/split checks.
- [x] Complete the fixed real-data alignment/rank sensitivity: 336 readout fits, training-only PCA/alignment, all rank/surface/shuffle controls and 2,322,432 exact parameter-row replays; retain projection and causal limits.
- [x] Complete the 23-tier/55-contrast nested joint-confidence study: 16,632 logistic fits and 663,552 exact parent probability replays; preserve all contexts and conditional intervals.
- [x] Build metadata-only registration lint and an inert final-evaluation prerequisite DAG; retain an unfilled ineligible draft.
- [ ] Select a supported account, finish genuine scientific registration and perform untouched final evaluation.

- [x] Correct numerical non-convergence with a fixed 1,000-iteration allowance for the five new stress tiers; preserve the original solver objective/tolerance and all 23 parent tiers at 100, with failed attempts retained.

See the preparation portfolio for exact interfaces, source pointers, accepted job IDs and limitations.
