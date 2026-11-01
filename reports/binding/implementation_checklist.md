# Implementation checklist

**Current checklist: November 1, 2026.** [Full consolidated status](#current-consolidated-checklist) · [New N1–N9 experiments](arithmetic_after_penalty_plan_20261101_v1.md). The entries preceding the consolidated checklist below preserve historical execution notes and their original counts.

**Start here: [Master research report — plan, results, figures and next steps](../../docs/binding/MASTER_REPORT.md)** ([Markdown version](master_research_report_v4.md)). Updated October 29, 2026; includes the full original plan, 19 main figures, including four conceptual illustrations, the complete figure archive, every research branch and an ordered next-experiment plan.

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

Updated **November 1, 2026**. Checked means that the stated implementation or experiment completed, including negative or inconclusive results. An unchecked claim is still open even when related software and pilots exist. New N1–N9 experiments are planned or gated, not submitted by this documentation update. Earlier task/test totals describe historical checkpoints, not this checklist.

Current consolidated inventory: **84 items — 42 completed, 37 open/partial core items and five optional/deferred items.** These grouped work items are not a percentage estimate of scientific completion and do not replace the historical per-study readiness inventories.

[Detailed new experiment plan and N1–N9 designs](arithmetic_after_penalty_plan_20261101_v1.md) · [Latest audited results](arithmetic_penalty_path_postrun_20261101_v1.md) · [Full master report](../../docs/binding/MASTER_REPORT.md) · [Original unchanged plan](../../docs/binding/dependvar_20261025.txt).

The current evidence includes strong scoped local dependency decoding and modest computed-value MAE gains. The latest joint probes have 6.68% / 6.00% computed exact accuracy versus zero's 8.90%, and 0.00% all-four exact recovery. No general preserved-value/disrupted-binding account, selective binding repair or faithfulness claim is established.

### The ten original authorized experiments

| Original experiment | Reconciled status |
|---|---|
| 1. Checkpoint and official prompt audit | Completed, including serialization/tokenizer/backend corrections. |
| 2. Arithmetic versus program execution | Behavioral studies completed; original computed reliability gates failed. Fresh N1 calibration remains planned. |
| 3. Arithmetic-free binding | Completed across cached checkpoints with scoped discovery qualification. |
| 4. Binding and version competition | Multiple measured banks and identity readouts completed; integrated computed/CoT binding/version account remains open (N2–N4). |
| 5. Naming × competition × updates | Scoped factorials completed with failed computed gates and timing/distance limitations; N8 controls remain planned. |
| 6. Tracking versus reconstruction | Timing and common-query controls completed; causal route identification and temporal N2/N4 tests remain open. |
| 7. Distributed-state probe diagnostics | Value/version/multiset, geometry, global-state, relationship and conditional/penalty studies completed; general full-state recovery remains unestablished. |
| 8. Value, ownership and pathway interventions | Several audited transfer studies completed; selective owner/version/descendant effects remain unestablished (N6). |
| 9. Frozen failure prediction | Discovery predictors, confidence/stress baselines and software completed; mechanism C, final registration/forecasts and untouched scoring remain gated (N9). |
| 10. Second-family replication | Behavioral/readout comparisons completed; replication of a supported causal mechanism remains gated (N9). |

### A. Infrastructure and reproducibility

- [x] Audit CodeCue, the existing manuscript, environments, cached checkpoints, native prompts and scheduler constraints.
- [x] Implement immutable dataset/configuration/source identities, grouped splits, compatible resumes and checksum verification.
- [x] Record raw generations, invalid outputs, seeds, native token sites, model revisions and actual resource use.
- [x] Implement automatic experiment/result logging, scheduler reconciliation and publication inventories.
- [x] Remove artificial project compute caps; retain actual scheduler limits, finite jobs and separate activation-storage policy.
- [x] Complete the latest frozen 2,697-test experiment regression and repair logging lock contention with 77 targeted checks.
- [x] Publish source, metadata, reports and figures to CodeCue; retain raw arrays on scratch and keep final/extrapolation outcomes sealed.

### B. Datasets, semantic ground truth and controls

- [x] Build parallel-chain, snapshot/overwrite and interleaved-accumulator generators and validate restricted-AST execution independently against Python.
- [x] Label values, assignment versions, directed/transitive dependencies, liveness and lawful counterfactual outputs.
- [x] Build neutral/informative/misleading naming twins, computed-value controls and same-value-multiset/different-owner examples.
- [x] Build literal/copy, varied-schedule, numeric relationship and computed-retention banks with structural grouping and overlap audits.
- [x] Retrieve/pin cited CRUXEval and BBH datasets and run benchmark/interface evaluations.
- [x] Prepare the 27,864-row paired source bank and validate both checkpoints' 45,360 native layouts; inventory potential prefix reuse.
- [ ] Generate fresh closed calibration components for N1 without overlap with prior calibration or formal evaluation.
- [ ] Generate integrated computed binding-swap, equal-value provenance and version/overwrite controls for N3/N4; earlier literal controls remain completed evidence.

### C. Behavior, naming and calibration

- [x] Complete original pilots, arithmetic/readout controls, capacity comparisons and arithmetic-free binding studies.
- [x] Complete relevant-live-load, computation/context/copy and historical-value studies; retain every failed competence gate.
- [x] Complete timing/common-final-query and equivalent-source behavior controls; retain wording and formatting sensitivity.
- [x] Complete paired protocol calibration and 941 continuations; audit all 2,592 merged responses with no remaining truncation.
- [x] Complete the exploratory 36-pair operand-versus-irrelevant overwrite review; retain correlated-context and finite-candidate limitations.
- [ ] Freeze and run N1: answer grammar, generation ceilings, wordings, protocols, parse/truncation reporting and prospective competence criteria.
- [ ] Run N8 naming × genuinely relevant live-variable load × reassignment with arithmetic/distance/surface controls in an interpretable regime.

### D. Values, bindings, versions and state recovery

- [x] Measure current/previous values, whole states, multisets and queried/unqueried accessibility with source/prior/shuffle controls.
- [x] Complete varied-schedule owner/version and direct joint identity studies; preserve supplied-slot, source-map and rare-class limitations.
- [x] Complete source-assisted taxonomy and saved-score grammar diagnostics; report symbolic assistance separately.
- [x] Complete local dependency, current-state and global all-four scalar/categorical studies with saved-parameter audits.
- [x] Audit exact-value failures and TRAIN mode/zero baselines: only 24/3,168 computed DEV slots have unseen slot values; both latest joint all-four scores are zero.
- [ ] Run N2 same-example temporal values/bindings/versions, written-step and answer measurements at declared pre-value sites.
- [ ] Distinguish numeric-value recovery from owner/version identity, including equal values with different provenance (N3/N4).
- [ ] Establish robust value/binding/version recovery or a well-supported failure pattern on independent structures; failed decoding alone cannot establish absence.

### E. Directed dependencies and algebraic relationships

- [x] Implement prefix-safe directed/operand-typed versioned def-use, ancestry and assignment-succession targets.
- [x] Implement equality, ordering, signed difference and additive/subtractive pair/triple targets with support masks.
- [x] Complete fixed-scaffold structural/algebraic readouts, equal-state provenance controls and stronger source/value-derived comparisons.
- [x] Complete computed/global direct-versus-derived relation studies; preserve weak relation scores and supplied-candidate limitations.
- [ ] Run N5 shared variable/pair/triple readouts with matched source/query/position/class-prior controls and complete graph/state metrics.
- [ ] Test unprinted true algebraic relations and false structural distractors on the integrated fresh cohort.
- [ ] Separate syntactic dependency from functional influence using interpreter-verified counterfactuals; evaluate optional consistency repair separately.

### F. Probe methods and competing explanations

- [x] Complete frequency/entropy-matched grouped controls and projection/rank/alignment studies.
- [x] Complete TRAIN-selected layer/rank/readout improvements and scalar/categorical/circular/ordinal geometry comparisons.
- [x] Complete alternative-semantic controls on fixed states and source/hidden/joint/independently selected shuffled-hidden comparisons.
- [x] Complete the penalty extension: 216 new CV fits, 240 reused banks, all eight selections still alpha 10,000; audit 3,763,584 coordinates exactly.
- [ ] Compare independent heads, a shared variable-query decoder and one declared interaction/nonlinear comparator under TRAIN-only selection (N5).
- [ ] Run endpoint-specific exact/probabilistic readout comparisons against TRAIN class priors with class-support and calibration reporting.
- [ ] Run independent-family learning curves and, if pursued, valid prequential/MDL comparisons with prefix-only fitting and an actual probability model.
- [ ] Distinguish binding interference, computation/accessibility, failure to use, query-time reconstruction and harmless readout/representation shift (N2–N9).

### G. Temporal capture and same-case measurement

- [x] Validate causal source prefixes and distinguish source position, model layer, execution step and query site in existing captures.
- [x] Prepare paired compute/overwrite/delay/later-use sources with matched earlier prefixes and distinct RHS/newline native sites.
- [x] Complete the metadata-only prefix inventory: 165,888 requested site rows map to 50,688 unique prefixes per model; reuse remains a potential optimization.
- [ ] Audit full-prompt versus prefix-truncated activations numerically on GPU, including padding/batching conditions, before reuse.
- [ ] Implement generated-trace capture with exact token boundaries, first target-value/claim occurrence, visibility flags and an explicit alignment policy.
- [ ] Join interpreter truth, generated prefixes, probe predictions, written claims and final answers on identical case/event IDs (N2).
- [ ] Collect pre-write/pretrace/preanswer states from natural generation; report already-visible, copied, omitted and unaligned targets separately.
- [ ] Cross correct/incorrect probe predictions with written-step/answer correctness and formal operand/irrelevant-overwrite contrasts on the same cases (N2/N4).

### H. Internal interventions and selective use

- [x] Complete literal value transfers, computed/late-reference follow-ups and their sanity/control audits.
- [x] Complete equivalent-source copy-site and fresh ownership single/joint patch studies with reciprocal and wrong-owner/version controls.
- [x] Preserve weak/nonselective ownership results and the reduced timing gap under a common final query.
- [ ] Freeze N6 donor/recipient correspondences, variable/version identity, sites, patch scope and interpreter-predicted counterfactuals.
- [ ] Validate token geometry, no-op/self replay, effective perturbation and matched negative controls before causal interpretation.
- [ ] Measure predicted descendant changes, unrelated-target stability, exact counterfactual answers and collateral damage.
- [ ] Test selective binding/version restoration where the assay supports it; an accuracy gain or a decodable patched value alone is insufficient.
- [ ] Replicate a supported selective effect on independent structures and a second checkpoint family; otherwise report inconclusive localization (N9).

### I. Written reasoning interventions — newly added N7

- [ ] Save natural CoT prefixes and construct unchanged, wrong-value, corrective-value, removed-step and matched paraphrase/irrelevant-edit branches.
- [ ] Resume the same model with declared greedy/sampling settings; preserve original trajectories and record token/length differences.
- [ ] Score both original program truth and edited-prefix counterfactuals, retaining ambiguous follows/corrects/ignores classifications.
- [ ] Compare effects on downstream dependent and unrelated quantities with all branches grouped by source/prefix.
- [ ] Keep edited-prefix dependence separate from claims about the original run's computation, pre-value decodability and faithfulness.

### J. Prediction, confirmation and replication

- [x] Implement frozen registrations/forecasts, access guards, proper scores, calibration and clustered uncertainty; prepare four reserved extrapolation banks.
- [x] Complete discovery input/neutral/oracle-access predictors, capacity controls and exact-prompt confidence comparisons.
- [x] Complete the discovery assignment-cue extra-query/stress comparator with explicit information and query-cost contracts.
- [ ] Select an evidence-supported primary account and freeze N9 hypotheses, measurements, layers/sites, exclusions, ambiguity and multiplicity rules.
- [ ] Freeze unfamiliar-program A input-only, B confidence/behavior and C internal-measurement predictors plus the cheap behavioral comparator and immutable forecasts.
- [ ] Choose independent structural cohort size and precision/power targets; new numeric draws and fitting seeds do not substitute for structural replication.
- [ ] Score authorized untouched depth/distance/competition/transformation outcomes only after registration and forecasts; report incremental proper scores, calibration, uncertainty and cost.
- [ ] Add a genuinely new program family once the core assay/claim is stable and replicate the selected effect across model families.

### K. Literature, paper and final handoff

- [x] Inspect the original CodeCue paper, document the proposed extension and maintain evidence-linked master reports/figures.
- [x] Complete the pinned 23-paper probing review plus prior primary-source/version checks; preserve their stated reading limits.
- [ ] Fully review the newly identified code-structure and CoT text/internal-intervention sources; write an addendum without changing the frozen review/register.
- [ ] Choose a supported causal/predictive or descriptive/negative-result contribution and verify claim-specific novelty.
- [ ] Write the new manuscript and predictive figure after the relevant empirical evidence exists; complete reproducibility and submission review.

### L. Optional or deferred branches

These original branches remain listed. Adding them to the checklist does not launch them.

- [ ] Targeted language-model training: matched ordinary, obfuscation and binding-targeted training plus shuffled-supervision controls, after a reproducible mechanism motivates it.
- [ ] Separate explanation-transfer study: calibrated shared/different/inconclusive mechanisms, explicit correspondences and held-out semantic-preserving/changing transformations.
- [ ] Unlearning: controlled fictional API mappings, forget/retain controls and prediction beyond cheap behavior, after the core diagnostic is reliable.
- [ ] Human experiments and broad multilingual evaluation: outside the initial pilot.
- [ ] Large new-checkpoint download/model-sweep campaign: deferred; existing cached-checkpoint comparisons remain completed.

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
