# Variable binding, updating and relationships: master research report

> **October 31 methods upgrade:** [Competing mechanisms and advanced methods](../../reports/binding/advanced_methods_20261031_v1.md) · [Submitted geometry wave](../../reports/binding/arithmetic_numeric_geometry_launch_v1.md) · [Controlled protocol](../../reports/binding/arithmetic_numeric_geometry_plan_v1.md). The new assay tests circular numeric geometry with matched permutations and prepares final-query vectors. Shared-slot models, calibrated MDL and causal alignment remain proposed follow-ups.

> **October 31 next-run planning:** [Latest results snapshot](../../reports/binding/arithmetic_results_for_next_runs_v1.md) · [Ordered run plan](../../reports/binding/arithmetic_next_runs_20261031_plan_v1.md). Cached full-width global decoding of all four values/direct relations comes first, alongside paired timing/overwrite/retention dataset preparation. No new run is submitted by this planning step.

> **October 31 completed compression/encoding wave:** [Audited review and figure](../../reports/binding/arithmetic_numeric_postrun_review_v1.md) · [Full findings](../../reports/binding/arithmetic_numeric_exploration_findings_v1.md). All workers and the report finished, with successful independent bank/selection/parameter/metric checks. Wider hidden features help within the fixed-layer assay; exact computed-value recovery remains weak. These are exploratory results.

> **October 31 storage recovery:** Numeric exploration passed2,467 tests and all cache stages before a `/work` quota failure. [Verified relocation and resume](../../reports/binding/arithmetic_numeric_storage_recovery_20261031_v1.md) moved large data and future readout outputs to scratch, preserved66 saved/recovered banks and restored the controller. The first restarted worker is making new progress.

> **October 31, next wave:** [Compression and numeric encoding submitted](../../reports/binding/arithmetic_numeric_exploration_launch_v1.md). Fixed-layer role-specific probes compare 64/256/1024/uncompressed features and numeric component encodings with shared source controls. Full frozen regression gates the CPU experiment DAG. [Live status](../../reports/binding/arithmetic_numeric_exploration_status_v1.md).

> **October 31:** The [completed current-state follow-up](../../reports/binding/arithmetic_current_state_findings_v1.md) finds weak computed-value recovery and near-chance derived relationships. The [exploratory roadmap](../../reports/binding/arithmetic_exploration_20261031_plan_v1.md) tests compression, numeric encoding, timing, binding/arithmetic, direct relations and behavior prediction before gated causal work. Its [completed first diagnostic](../../reports/binding/arithmetic_measurement_diagnostics_v2.md) reports structural-family uncertainty, positive hidden/source dependency contrasts and weak numeric states even with oracle routing.

> **October 30 evening:** [Audited local-dependency results and figure](../../reports/binding/arithmetic_local_dependency_findings_v1.md) show 86.72% / 83.43% parent accuracy and 41.46% / 34.54% complete graphs. All 108 saved readouts passed exact replay. The [validated follow-up release](../../reports/binding/arithmetic_state_followup_launch_v2.md) queues capacity controls and current-binding/numeric/algebraic decoding. Complete numeric-state recovery and causal use remain unestablished.

> **October30 probe revision:** [Implementation and submitted experiments](../../reports/binding/arithmetic_probe_improvement_launch_v1.md). TRAIN-only layer/regularization/rank selection, a larger structural dataset and shared local dependency scorers are implemented. Original negative findings remain preserved.

> **Completed archived-feature comparison:** [Results and figure](../../reports/binding/arithmetic_probe_selection_findings_v2.md). Complete-graph recovery remains zero; numeric error improves modestly. The new local experiment passed 2,408 software tests and both native layout checks before capture submission.

> **October30 operations:** [Debug pass and scheduled monitoring](../../reports/binding/operations_debug_20261030_v1.md). Saved readout and prompt-control artifacts passed their audits; logger freshness detection was fixed and verified with 54 tests.

> **October30 morning review:** [Audit and next decisions](../../reports/binding/arithmetic_graph_morning_decision_v1.md) · [New TRAIN/DEV figure](../../reports/binding/figures/arithmetic_graph_train_dev_review_v2.png) · [Printed-query control results](../../reports/binding/arithmetic_prompt_control_findings_v1.md). Exact replay confirms the generalization gap. Explicit printing improves literal reporting but arithmetic remains unreliable.

> **New completed follow-up, October29–30:** [Arithmetic dependency/relationship findings](../../reports/binding/arithmetic_graph_overnight_findings_v1.md) · [plan](../../reports/binding/arithmetic_graph_overnight_20261029_plan_v3.md). The first suite completed: 9,216 captures, 2,304 generated answers and 36 readout fits. Answer-preparation relation balanced accuracy is 54.61% / 54.04% (8B / 34B), with zero complete eight-parent graphs recovered. Arithmetic-written DEV answers are 22/216 correct for each model. These are exploratory negative findings under the tested readouts, not evidence of representational absence.

> **GitHub edition.** This is the repository-relative edition of the October 29 master report. All scientific results are unchanged. For the interactive walkthrough, download the [self-contained HTML edition](../../reports/binding/master_research_report_v4.html) and open it in a browser. Large evidence files are losslessly compressed; see the [artifact catalog and restore commands](../../reproducibility/README.md). The [original plan](dependvar_20261025.txt) is included in this repository.

**Status as of October 29, 2026.** This is the master record for the study proposed in `dependvar.txt`, including the subsequent user-requested dependency and algebraic relationship work. It summarizes completed work, preserves negative findings, and gives a concrete next plan. It is a research status report, not an empirical paper abstract or a claim that the original scientific objective is finished.

## The idea in one figure

![Master conceptual figure: code enters a language model; one hidden-state tap feeds readouts for all variable bindings, versions, dependencies and algebraic relations.](../../reports/binding/figures/variable_binding_master_v1.png)

*Master figure. The proposed readout suite asks whether a checkpoint supports a structured view of all current bindings, previous assignment versions, directed dependencies and algebraic relationships. Displayed values and edges are Python ground truth, not observed probe predictions.*

[PNG](../../reports/binding/figures/variable_binding_master_v1.png) · [Editable SVG](../../reports/binding/figures/variable_binding_master_v1.svg) · [Vector PDF](../../reports/binding/figures/variable_binding_master_v1.pdf)

## Start here: the idea in pictures

A variable name can keep appearing while the value it refers to changes. The research asks whether a model keeps the right value attached to the right name and assignment, and whether that helps explain its answers.

![A tiny worked example of binding and overwriting. The final subtraction should use current x = 7 and copied y = 2, giving z = 5. The diagrams show exact Python ground truth, not a known neural storage mechanism.](../../reports/binding/figures/concept_binding_timeline_v1.png)

*Figure 1. A tiny worked example of binding and overwriting. The final subtraction should use current x = 7 and copied y = 2, giving z = 5. The diagrams show exact Python ground truth, not a known neural storage mechanism.*

The old value of `x` and the current value of `y` happen to be the same number here. That does not make them the same binding: they have different names and assignment histories. At the final subtraction, using obsolete `x` gives 0; exchanging the two inputs gives −5. These are illustrative possible errors, not measured error frequencies.

[Open the interactive assignment walkthrough in the HTML edition](../../reports/binding/master_research_report_v4.html#binding-stepper). Use Next, Previous or the slider to see the state after each line.

<!-- BINDING_STEPPER -->

![Binding asks who owns a value; dependency asks which assignment supplied it; an algebraic relation asks how current numbers relate. The arrows describe the program's data flow. Decoding one kind of relationship does not automatically establish the others.](../../reports/binding/figures/concept_relationship_types_v1.png)

*Figure 2. Binding asks who owns a value; dependency asks which assignment supplied it; an algebraic relation asks how current numbers relate. The arrows describe the program's data flow. Decoding one kind of relationship does not automatically establish the others.*

![The evidence ladder: recover information with a probe, test selective causal use with controlled interventions, then predict errors on unfamiliar programs. These are different scientific requirements; high probe accuracy alone does not complete the chain.](../../reports/binding/figures/concept_evidence_ladder_v1.png)

*Figure 3. The evidence ladder: recover information with a probe, test selective causal use with controlled interventions, then predict errors on unfamiliar programs. These are different scientific requirements; high probe accuracy alone does not complete the chain.*

These illustrations introduce the concepts. The plots and tables below report actual experiments and retain their original limitations.

## 1. Where we stand

**The infrastructure and a large discovery program are complete. The central causal explanation and untouched unfamiliar-program validation are not.** We have working semantic datasets, two main model families, behavior and representation measurements, several intervention assays, strong error-prediction comparators, and audited results. We have not established that a selective binding/version mechanism explains the errors and predicts them on new program families.

The strongest findings are:

- **Structure can be decoded without reliable execution.** Copy-parent graphs are often recovered well under a supplied scaffold, including computed-root programs whose numeric readouts and generated answers are poor.
- **Query-dependent accessibility is large in one controlled readout.** Queried and unqueried values differ strongly at the saved answer-preparation site. This concerns the tested decoders, not proof that unqueried values were erased.
- **Source-only controls substantially change the interpretation.** Deriving relations from source-predicted values beats direct hidden algebraic decoding on literal programs. Explicit source owners and external counters can reconstruct assignment identities perfectly in the grammar diagnostic.
- **The intervention evidence is narrow or inconclusive.** Literal-site transfers affect answers in a small interface family, but fresh ownership controls do not establish selective transport. An initial query-timing gap becomes much smaller when the final cue is held constant.
- **Cheap confidence is a serious prediction baseline.** CodeLlama has useful discovery gains from next-token confidence; combining confidence bundles sometimes helps further. There is no frozen mechanism-based predictor or untouched final comparison.
- **Latest historical-value calibration failed.** Current and previous values are not reliably distinguished across the fixed cells. CodeLlama also has substantial formatting failures, but formatting alone cannot explain the failed gates.

| Latest old/current calibration | Llama 8B | CodeLlama 34B |
|---|---:|---:|
| Scored responses | 20,160 | 20,160 |
| Overall exact accuracy | 60.87% | 23.51% |
| Invalid responses | 0 | 9,864 |
| Primary reliability cells passed | 0 / 24 | 0 / 24 |

**Read the task count correctly:** **74 tracked tasks: 62 ready, 9 requiring scientific decisions, 3 optional/deferred**. “Ready” combines implemented tools and completed scoped work; it does not mean that the scientific claim is supported. The last full binding regression passed 2,280 tests for the frozen overnight source. Later operational fixes passed 90 focused tests; these are overlapping checks, not another 90 independent scientific experiments or a new full-suite total.

## 2. The original question and how this differs from CodeCue

The original question was: **What determines whether transformers correctly update and use variable bindings, and can the identified mechanism predict failures on unfamiliar programs?** A binding includes a variable, its assignment version and its value. Updating, recovering information, using it for an answer, and predicting future errors are separate requirements.

The existing CodeCue manuscript, *Misleading Identifiers Change What Code Traces Write*, concerns length/sum identifier conflicts, erroneous trace writes, recoverable digits, span interventions and expression formats. The new study adds controlled multi-variable integer programs, explicit old/current versions, value-ownership and dependency controls, and the intended causal-to-predictive validation chain. Existing manuscript results are not imported as new binding-study evidence. [Repository/manuscript audit](../../reports/binding/repository_audit.md).

The competing explanations from the original plan remain live:

| Hypothesis | Current evidence | What would distinguish it |
|---|---|---|
| H1: binding/version interference | Obsolete/current-compatible errors and incomplete identity recovery occur. | Selective owner/version changes with matched numeric multisets and wrong-owner/wrong-version controls. |
| H2: value computation/accessibility failure | Computed programs and numeric readouts are weak; algebraic scores fall on computed roots. | A reliable arithmetic/readout baseline, matched decoder capacity, and an assay separating computation from selection. |
| H3: failure to use an accessible binding | Some task-specific quantities are decodable while behavior is weak. | Same-case correct binding recovery plus selective intervention and downstream specificity. Existing results do not establish this conjunction. |
| H4: reconstruction during answering | Query/site effects are substantial; final-cue control reduces the timing effect. | Matched prefix/full-history tasks and timing-coupled route controls that do not change the answer interface. |
| H5: harmless representational change | Alignment helps some individual-slot readouts. | Strong within-condition controls and equivalent selective causal effects after alignment; improved decoding alone is insufficient. |

No single H1–H5 account has been selected as established. The current best-supported description is **decoder- and protocol-dependent accessibility, with reliable causal ownership and computed execution unresolved**.

## 3. The whole plan: milestones and current acceptance

![The original milestones and current evidence status. Engineering completion does not imply causal or confirmatory qualification.](../../reports/binding/figures/master_plan_20261029_v2.png)

*Figure 4. The original milestones and current evidence status. Engineering completion does not imply causal or confirmatory qualification.*

| Original milestone | Engineering / execution | Scientific acceptance | Remaining work |
|---|---|---|---|
| M0: repository/resource audit | Done: repository, manuscript, tokenizer, checkpoint, runtime and scheduler audits. | Scope is explicit. | Update novelty/version review around the eventual claim before submission. |
| M1: generator and oracle | Done: three core families, AST execution, renaming, versions, dependencies, liveness, counterfactuals, grouped manifests; later copy/relationship banks. | Semantic checks pass for the recorded cohorts. | New families and prospective independent structures remain separate design choices. |
| M2: behavioral smoke/pilot | Done: original pilot, published benchmarks, arithmetic-free discovery and several computed/history calibrations. | Mixed: some literal/copy assays qualified; computed and latest old-value gates failed. | Find a tractable regime for the intended explanatory assay without retrospectively rescuing failed gates. |
| M3: representations and controls | Done: values, previous versions, multisets, queried/unqueried, alignment/rank, dependencies, algebraic relations, direct identities and grammar diagnostics. | Scoped accessibility findings supported. | Full bindings, strong out-of-family transfer and natural causal use remain unestablished. |
| M4: focused intervention | Several assays completed, with no-op, self, donor, wrong-owner/version and pathway controls. | Partial/inconclusive for a general binding mechanism. | A reproducible selective effect with matched ownership/version controls and independent quantities. |
| M5: frozen unfamiliar-program prediction | Interfaces, discovery predictors, confidence comparators and structural source banks built. | Not reached. | Select supported mechanism C; freeze genuine registration and forecasts; then authorized untouched scoring. |
| M6: paper decision | Reports and decision memos exist; this master document consolidates them. | Main proposed contribution is not yet supported. | Decide whether to pursue a narrower measurement result or invest in a better calibrated causal assay. |

The original pilot target was 600 bases × six naming/lexical renderings = 3,600 rendered programs, before separate arithmetic controls. Actual consumed cohorts and units are recorded per study rather than being treated as that target or pooled into one sample.

## 4. What has been built

**Semantic and data system.** Restricted straight-line scalar-integer Python; parallel chains, saved snapshots/overwrites, interleaved accumulators; bounded values; informative/neutral/misleading bijective renaming; relevant-load and update factors; per-statement values, versions, direct/transitive def-use, liveness and counterfactual outputs. Generated restricted programs are checked independently against ordinary Python. Syntactic dependency is kept distinct from functional influence.

**Measurement system.** Greedy full-response behavior, strict parsers with invalid outputs retained, complete signed-integer candidate/EOS event scoring, exact prompt/token identities, statement/final/query/answer positions, residual capture, capacity-controlled readouts, source/prior/shuffle controls, train-only normalization and alignment, donor interventions and counterfactual output scoring.

**Prediction and statistics.** Structurally grouped nested cross-validation; input-only, raw neutral query, oracle-scored neutral, next-token confidence, candidate-event and joint confidence tiers; Brier/log loss/calibration; conditional group bootstrap intervals; exact replay of saved probabilities and fitted parameters. A source oracle is a stronger access contract, not an ordinary cheap feature.

**Operations.** Local cached checkpoints, pinned revisions, immutable source/config snapshots, resumable chunked outputs, model-query/warm-up/retry accounting, semantic/tokenizer preflights, SLURM dependency chains, actual device telemetry, automatic SQLite/CSV/Markdown experiment logging and independent checks. Compute has no application GPU-hour cap under the user's override; hardware/scheduler limits and scientific gates still apply.

### Main checkpoints

| Checkpoint | Role | Recorded revision |
|---|---|---|
| CodeLlama 7B Instruct | Original feasibility pilot and published benchmark/interface work. | `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed` |
| Llama 3.1 8B Instruct | Main behavioral, representation and prediction discovery. | `0e9e39f249a16976918f6564b8830bc894c89659` |
| CodeLlama 34B Instruct | Main second-family behavioral, representation and prediction comparison. | `d4c1c474abcacd32d2a6eda45f9811d38c83e93d` |

Use each original run manifest for its actual precision, backend and prompt contract. In particular, candidate-event measurements use a qualified FP32 contract; their probabilities must not be described as the same BF16 next-token measurement.

### Datasets and independent units

| Bank / collection | Size / grouping | Status and interpretation |
|---|---|---|
| Original generated families | Main and smoke banks plus explicit arithmetic controls. | Consumed discovery subsets; preserve grouped canonical structures. |
| Published CRUXEval-O and BBH tracking | 800 CRUXEval examples; 250 each of three/five/seven-object BBH. | Evaluated on early CodeLlama 7B. Direct and CoT are separate protocols on reused examples. |
| Computed retention frontier | 38,016 prompts/model; 24 initialization-order components. | Fully evaluated; both reliability gates failed. |
| Failure-prediction targets | 6,144/checkpoint; 24 structural groups/checkpoint. | Reused across nested analyses; partition seeds are not new datasets. |
| Prepared replication/precision portfolio | Nine discovery banks, 30,960 source records; 240 conditional planning scenarios. | Oracle/overlap checked. Structural sharing prevents automatic pooling or a claim of independent confirmation. |
| First routing/relations banks | 1,296 routing programs; 1,944 relation programs; 81 graphs in 27 components. | Learned analyses complete; fixed four-root/four-copy scaffold. |
| Literal/computed/query overnight union | 16,038 union rows; panels share rows; 18 TRAIN/nine DEV components. | Both model captures and six readout panels complete. |
| Varied overwrite schedules | 2,016 rows/model; ten TRAIN/five DEV canonical families. | Actual assignment versions; class support was uneven. |
| Slot-complete diversity | 5,760 rows/model; 45 TRAIN/15 DEV families, 96 dependent relatives/family. | Versions 1–4 in every slot; broadens the same literal/copy program language. |
| Historical/current questions | 6,720 rows; 3,360 pairs; 1,440 bodies from those 60 families. | Three instructions → 20,160 responses/model. New numbers are not new structural families. |
| Reserved structural extrapolation | Depth, distance, competition and combined source banks. | Prepared/validated; original final/extrapolation outcomes remain sealed. |

Published datasets provide external behavioral references. Controlled synthetic banks provide exact intermediate state, ownership and intervention truth that those benchmarks do not directly supply. Downloading a cited dataset alone does not answer the causal binding question. [Published dataset review](../../reports/binding/published_datasets.md), [overlap/replication audit](../../reports/binding/replication_preparation_v1.md), [precision planning](../../reports/binding/precision_planning_v1.md).

## 5. Behavioral results and calibration

### Original computed pilot

| Task | Responses | Exact accuracy | Cluster bootstrap 95% interval |
|---|---:|---:|---|
| arithmetic_control | 360 | 3.1% | [0.0, 0.07895455852746616] |
| primary | 360 | 2.5% | [0.0, 0.06780624036979964] |

This early CodeLlama 7B subset contains 720 responses over 60 bases and 38 parent-template clusters. Its near-floor accuracy made the intended computed-mechanism interpretation infeasible. Compatible competing-variable/obsolete answers overlap and are not proven internal causes. Later literal/copy improvements do not repair this original result. [Pilot and interface diagnostics](../../reports/binding/pilot_report.md).

### Published benchmarks and interface lessons

| Evaluation | Correct / questions | Literal / letter accuracy | Invalid | Token limit | Upstream postprocessing + literal correct |
|---|---:|---:|---:|---:|---:|
| cruxeval_o_direct | 290 / 800 | 36.25% | 25 | 8 | 3 |
| bbh_tracking_3 | 90 / 250 | 36.00% | 0 | 0 | — |
| bbh_tracking_5 | 63 / 250 | 25.20% | 1 | 0 | — |
| bbh_tracking_7 | 39 / 250 | 15.60% | 8 | 0 | — |
| cruxeval_o_cot | 298 / 800 | 37.25% | 48 | 27 | 298 |

These are the report's separately defined literal/letter scores. The initial direct CRUXEval released-postprocessor score was 3/800 because the output structure did not match that processing path; this is not interchangeable with 290/800 answer-block literal scoring. A subsequent controlled completion serialization yielded 295/800 direct. CoT remains a different protocol. [Benchmark audit](../../reports/binding/published_baseline_review.md), [serialization comparison](../../reports/binding/serialization_comparison.md).

### Literal binding discovery versus computed execution

Arithmetic-free discovery qualified the main two checkpoints for scoped literal/copy work. Update count and trailing copies affected current answers, and naming effects depended on model/query. Available competing variables were not all output-relevant, so that bank is not a clean manipulation of functional live load. The explicit computed-retention design later held all variables defined while varying functional relevance; reliability remained poor:

| Task | Llama 3.1 8B | CodeLlama 34B |
|---|---:|---:|
| Direct-literal three-subtraction control | 130/384 (33.85%) | 44/384 (11.46%) |
| Decomposed arithmetic control | 65/768 (8.46%) | 22/768 (2.86%) |
| Full retention-frontier program cohort | 2,883/36,864 (7.82%) | 2,163/36,864 (5.87%) |
| Entire evaluated cohort | 3,078/38,016 | 2,229/38,016 |
| Invalid responses | 0 | 16 |
| Fixed reliability gate | Failed | Failed |

The separate arithmetic/readout study collected 12,288 responses and failed all four fixed model/protocol gates. The later computation/context/copy study collected 40,200 responses and qualified 0/6 prospective gates. Changing arithmetic form, context and wording strongly changes performance, but these comparisons do not isolate binding interference.

![Computed retention results for Llama 8B. All fixed contrasts remain exploratory after the failed clean/arithmetic gate.](../../reports/binding/live_load_llama31_8b_v2.png)

*Figure 5. Computed retention results for Llama 8B. All fixed contrasts remain exploratory after the failed clean/arithmetic gate.*
![Matched computation, context and copy calibration. Root-format and context effects cannot alone identify whether arithmetic, routing or selection failed.](../../reports/binding/figures/computation_routing_v1.png)

*Figure 6. Matched computation, context and copy calibration. Root-format and context effects cannot alone identify whether arithmetic, routing or selection failed.*

Sources: [competition](../../reports/binding/competition_results.md), [computed retention](../../reports/binding/live_load_decision.md), [arithmetic/readout](../../reports/binding/arithmetic_readout_decision.md), [computation routing](../../reports/binding/computation_routing_findings_v1.md).

## 6. Representation accessibility, previous values and alignment

The original computed probes fitted training states very well but generalized weakly. Corrected analyses centered masked labels correctly and matched surface features to the visible prefix; regularization and increased numeric diversity were tested. Poor readout does not show that the information is absent.

Frequency-matched grouped controls preserved label frequencies/entropy. The later query-selectivity study used equally sized independent categorical heads on the same coordinates. At the fixed neutral block-24 saved `pre_answer` site, queried accuracy was 88.89%, unqueried 9.4184%, a 79.4705-point gap with conditional group interval [75.8670, 83.5069]. This was an earlier saved formatting boundary, not the later corrected digit boundary.

![All fixed query-selectivity curves. The large queried/unqueried difference establishes decoder-specific accessibility on consumed structures, not disposal, ownership or natural causal use.](../../reports/binding/query_selectivity_curves_v1.png)

*Figure 7. All fixed query-selectivity curves. The large queried/unqueried difference establishes decoder-specific accessibility on consumed structures, not disposal, ownership or natural causal use.*

Train-only reduced-rank/Procrustes work completed 336 readout fits. At the earlier answer-preparation site, misleading-current accuracy improved from 19.01% to 25.39%, saved-value accuracy from 30.34% to 35.68%, but both-values recovery only from 0.78% to 1.56%. Alignment is a useful sensitivity analysis; it does not demonstrate equivalent computation or full-state recovery. [Matched controls](../../reports/binding/matched_probe_controls_decision.md), [query accessibility](../../reports/binding/query_selectivity_findings.md), [alignment/rank findings](../../reports/binding/continuation_followup.md).

## 7. Interventions and tracking versus reconstruction

### Literal value transfer

The corrected literal assay had 392/432 correct full baselines and 20,160 intervention forwards. Raw block-0 transfer changed affected digit outcomes on 144/144 queries with 0/144 replacements on unchanged-answer controls. This supports a narrow literal-site causal contribution. Ownership was less specific on the full cohort: 118/144 affected replacements and 27/144 unchanged-answer replacements. Conditioning on already-correct baselines is secondary and does not replace the full-cohort result.

The first run patched a formatting space rather than the digit; its apparent zero transfer is not valid answer-transfer evidence. The correction used the same fixed space for every input and preserved the original artifact. [Boundary correction](../../reports/binding/value_transfer_boundary_correction.md), [corrected decision](../../reports/binding/value_transfer_decision.md).

![Corrected literal transfer. Use the corrected digit-boundary figure; the earlier figure is historical, not an alternative valid zero-effect result.](../../reports/binding/value_transfer_effects_v2.png)

*Figure 8. Corrected literal transfer. Use the corrected digit-boundary figure; the earlier figure is historical, not an alternative valid zero-effect result.*

### Earlier-copy routes, ownership and timing controls

Earlier-copy/reordering/renaming studies ran 90,720 interventions. Effects differed by quantity and direction: improving one queried value could harm another. Fresh numeric ownership controls then ran 96,768 intervention forwards plus 7,776 baselines; nominated copy-site effects were weak or nonselective.

| Block-8 intervention | Target correct before | Target correct after | Cases |
|---|---:|---:|---:|
| First-copy substitution | 758 | 763 | 1,728 |
| Second-copy substitution | 970 | 971 | 1,728 |
| Both-copy substitution / donor answer | 270 | 289 | 1,728 |
| Wrong-version directional control | 1,026 | 1,019 | 1,728 |

The original explicit timing study found higher late-query accuracy. A matched common-final-query control substantially reduced that gap:

| Prompt condition | Early correct | Late correct | Late minus early |
|---|---:|---:|---:|
| Original timing cues, replayed | 1,030/1,296 | 1,199/1,296 | +13.04 percentage points |
| Identical final query in both | 1,191/1,296 | 1,213/1,296 | +1.70 percentage points |

![A common final cue shrinks the early/late timing gap. Query timing by itself therefore does not distinguish maintained state from reconstruction.](../../reports/binding/cue_control_effects_v1.png)

*Figure 9. A common final cue shrinks the early/late timing gap. Query timing by itself therefore does not distinguish maintained state from reconstruction.*

No general selective ownership/version/pathway mechanism follows from these assays. [Timing/copy decision](../../reports/binding/timing_and_copy_decision.md), [fresh ownership and final-cue decision](../../reports/binding/mechanism_followup_decision.md).

## 8. Error predictors: what was actually trained

These are **small supervised predictors of language-model failure**, not language-model training and not an established causal mechanism. Targets are saved response correctness. Source groups stay together across nested folds; scaling and regularization fit training data only. The same consumed discovery examples recur across analyses, so fit totals must not be added as if they were independent experiments.

The comparison hierarchy is:

1. A training prior and source properties: length, operations, structure and fixed interactions.
2. A distinct neutral-query response, either raw or separately oracle-scored.
3. Label-free next-token confidence statistics.
4. Complete finite signed-integer/EOS candidate events, or both confidence bundles together.
5. An additional assignment-cue generation under its explicit query-cost contract.
6. Intended future mechanism C features — **not yet qualified, fitted or validated**.

### Input and neutral-query baselines

| Checkpoint | Targets | Failures | Predictor | Brier | Log loss |
|---|---:|---:|---|---:|---:|
| Llama 3.1 8B | 6144 | 430 | prior | 0.065153 | 0.254100 |
| Llama 3.1 8B | 6144 | 430 | A_input | 0.039731 | 0.138343 |
| Llama 3.1 8B | 6144 | 430 | A_neutral_raw | 0.040188 | 0.139721 |
| Llama 3.1 8B | 6144 | 430 | A_neutral_scored | 0.036727 | 0.130138 |
| CodeLlama 34B | 6144 | 1454 | prior | 0.180960 | 0.548053 |
| CodeLlama 34B | 6144 | 1454 | A_input | 0.132585 | 0.408816 |
| CodeLlama 34B | 6144 | 1454 | A_neutral_raw | 0.132397 | 0.408188 |
| CodeLlama 34B | 6144 | 1454 | A_neutral_scored | 0.101568 | 0.316216 |

Raw neutral behavior adds no clear Brier gain over input features in either checkpoint. Scoring the neutral response with an oracle helps under its stronger information contract. Capacity/access controls preserve original predictions and expose deterministic feature-encoding effects. [Original prediction decision](../../reports/binding/discovery_prediction_decision.md), [capacity/access controls](../../reports/binding/discovery_controls_decision.md).

### Next-token confidence

| Checkpoint | Baseline | Baseline Brier | + confidence Brier | Improvement [conditional 95%] | Baseline log loss | + confidence log loss |
|---|---|---:|---:|---|---:|---:|
| CodeLlama 34B | Source + interactions | 0.123574 | 0.116641 | +0.006933 [0.002194, 0.011878] | 0.380577 | 0.361757 |
| Llama 3.1 8B | Source + interactions | 0.039673 | 0.039430 | +0.000243 [−0.000755, 0.001285] | 0.137222 | 0.133126 |
| CodeLlama 34B | Interactions + source oracle + raw neutral | 0.091608 | 0.087942 | +0.003666 [0.001484, 0.005842] | 0.293049 | 0.283594 |
| Llama 3.1 8B | Interactions + source oracle + raw neutral | 0.037215 | 0.035738 | +0.001477 [0.000134, 0.002940] | 0.131400 | 0.124886 |

CodeLlama benefits beyond strong input interactions. Llama's corresponding Brier interval crosses zero, though its log loss improves. Cross-model absolute Brier values do not rank language-model quality because failure prevalence differs.

![Discovery confidence increments with the corrected source comparison. Intervals condition on saved out-of-fold predictions and are not final unfamiliar-program validation.](../../reports/binding/discovery_confidence_increments_v2.png)

*Figure 10. Discovery confidence increments with the corrected source comparison. Intervals condition on saved out-of-fold predictions and are not final unfamiliar-program validation.*

### Complete-answer events, joint confidence and an extra query

The qualified full-answer banks contain 12,288 prompts across both checkpoints, 33 numeral candidates and declared EOS events. FP32 parity smokes, complete-prefix boundaries and immutable audits passed. Candidate-event statistics alone show no clear Brier advantage over next-token confidence in any of ten matched comparisons:

| Checkpoint | Shared source context | Next-token Brier | Candidate-event Brier | Improvement [conditional 95%] |
|---|---|---:|---:|---|
| CodeLlama 34B | Source + interactions | 0.116641 | 0.116667 | −0.000026 [−0.002814, 0.002933] |
| Llama 3.1 8B | Source + interactions | 0.039430 | 0.039524 | −0.000094 [−0.001131, 0.000858] |

Combining both bundles is a different comparison. CodeLlama source-interaction Brier improves from 0.116641 to 0.113499, increment 0.003142 [0.000158, 0.006277]; all five Llama conditional intervals cross zero. The extra instructed query gives context-dependent gains, with no clear Brier advantage over joint confidence in any of ten fixed comparisons.

![Complementarity of the two saved confidence bundles across all fixed contexts; this does not revise the earlier alternative-bundle null result.](../../reports/binding/joint_confidence_increments_v1.png)

*Figure 11. Complementarity of the two saved confidence bundles across all fixed contexts; this does not revise the earlier alternative-bundle null result.*
![Corrected extra-query comparator. Additional observations and oracle access are distinct contracts, not free mechanistic features.](../../reports/binding/stress_prediction_increments_v2.png)

*Figure 12. Corrected extra-query comparator. Additional observations and oracle access are distinct contracts, not free mechanistic features.*

These conditional bootstrap intervals resample structural groups without refitting or multiplicity adjustment. They do not establish an independent generalization gain. [Candidate events](../../reports/binding/candidate_prediction_findings.md), [joint confidence](../../reports/binding/joint_confidence_findings.md), [extra-query comparator](../../reports/binding/stress_comparator_findings.md).

## 9. Dependency and algebraic relationships

This branch covers **both** user-requested relationship types: directed data dependencies/assignment versions and algebraic relationships such as equality, ordering, signed differences and sum/subtraction triples.

### First balanced relationship bank

| Declared comparison | Hidden direct | Comparator | Difference and conditional group 95% |
|---|---:|---:|---|
| Algebraic relations, layer 24 / initialization site 3 | 85.019% | 68.779% from hidden categorical values | +16.240 pp [+12.562, +21.164] |
| Complete parent graph, layer 24 / last-assignment site 7 | 83.488% | 1.903% from direct source-text heads | +81.584 pp [+61.520, +94.394] |

The stronger source-predicted-values → relations pipeline reached 98.108%, exceeding direct hidden algebraic decoding. Hidden first-parent recovery distinguished equal-numeric-state provenance pairs at 96.759%, but the texts explicitly differ in copy-source syntax. These findings concern accessible information under the supplied scaffold, not a special neural relation store or causal use.

![Relationship controls: include the stronger source-value pipeline and equal-state/different-provenance comparisons, not only weak direct text heads.](../../reports/binding/figures/relationship_controls_v1.png)

*Figure 13. Relationship controls: include the stronger source-value pipeline and equal-state/different-provenance comparisons, not only weak direct text heads.*

### Literal versus computed roots across both checkpoints

| Model | Root format | Hidden direct | Hidden values → relations | Source values → relations |
|---|---|---:|---:|---:|
| Llama 3.1 8B | literal | 88.109% | 77.346% | 96.476% |
| Llama 3.1 8B | computed | 54.842% | 51.428% | 50.962% |
| CodeLlama 34B | literal | 84.192% | 83.857% | 95.869% |
| CodeLlama 34B | computed | 56.897% | 53.034% | 51.568% |

| Model | Format | Last assignment | Final prompt |
|---|---|---:|---:|
| Llama 3.1 8B | literal | 85.665% | 23.422% |
| Llama 3.1 8B | computed | 93.124% | 59.739% |
| CodeLlama 34B | literal | 95.628% | 57.305% |
| CodeLlama 34B | computed | 91.855% | 57.493% |

Algebraic and numeric decoding weakens on computed roots while graph recovery remains high. At the computed final prompt, queried numeric values score 7.493%/6.927% for 8B/34B, versus a 6.173% TRAIN prior. The matched generated-answer contrast is:

| Model | Matched literal accuracy | Computed accuracy | Computed minus literal, conditional95% | Literal invalid | Computed invalid |
|---|---:|---:|---|---:|---:|
| Llama 3.1 8B | 48.560% | 11.728% | -36.831 pp [-45.885, -28.189] | 0.412% | 6.173% |
| CodeLlama 34B | 45.062% | 2.881% | -42.181 pp [-54.938, -30.864] | 0.000% | 0.000% |

The suite completed 32,076 capture prefills, 14,580 generated answers, 270 ridge factorizations, 1,574,640 saved-parameter row checks and 524,880 frozen literal-to-computed applications. Shared panel rows and fit seeds are dependent reuse. Strong graph recovery does not show that the model knows all numeric values and merely fails to use them.

![Two-model literal/computed results, transfer and generated behavior. The graphs use supplied node/scaffold identities; root formats also change arithmetic and token context.](../../reports/binding/figures/overnight_relationships_v1.png)

*Figure 14. Two-model literal/computed results, transfer and generated behavior. The graphs use supplied node/scaffold identities; root formats also change arithmetic and token context.*

[Complete first-bank findings](../../reports/binding/relationship_results_findings_v1.md), [overnight findings](../../reports/binding/overnight_20261027_findings_v1.md), [posthoc exact-case/query analysis](../../reports/binding/overnight_score_behavior_findings_v1.md).

## 10. Actual versions, direct identities and grammar decoding

### Varied schedules and repaired class coverage

The first varied-schedule study used actual assignment versions. Its apparent 89.655% row-weighted version score fell to 53.333% under equal-family weighting, while the source-text baseline scored 100%. Uneven class/family coverage limited interpretation.

The slot-complete bank then ensured versions 1–4 occurred in every slot across 60 canonical families. Its fixed layer-24/site-7 **whole-task** direct hidden results are:

| Model | Backend | Method | Current definitions | Current versions | Copy parents |
|---|---|---|---:|---:|---:|
| Llama 3.1 8B | hidden | direct | 56.389% | 22.870% | 30.370% |
| CodeLlama 34B | hidden | direct | 69.815% | 35.093% | 37.222% |

![Slot-complete current-definition/version/parent recovery. Whole-task rates require every head correct; they are not pooled per-slot accuracies.](../../reports/binding/figures/diversity_decoding_v1.png)

*Figure 15. Slot-complete current-definition/version/parent recovery. Whole-task rates require every head correct; they are not pooled per-slot accuracies.*

### Source-assisted taxonomy versus direct joint identities

The source-assisted analysis mapped fixed statement predictions to owners/versions using source truth; parent identities were evaluated at the moment of consumption, even when obsolete later. Pooled owner accuracy is high, but the owner TRAIN prior is already 100%. This is assisted interpretation, not a learned complete binding decoder.

Direct joint owner/version heads removed the per-program identity map after prediction. Whole-write recovery is 28.519%/35.463% for 8B/34B; whole-parent recovery 24.630%/30.093%, below a stronger source-owner/TRAIN-version comparator's 40%. All-eight recovery is 6.019%/13.056%. First-event constant versions and rare version-4 classes remain explicit limitations. Joint and factorized component scores are linearly related; differing argmax rules are not independent representational evidence.

![Direct identity readouts and stronger source priors across every fixed layer. Parent recovery does not beat the stronger source comparator.](../../reports/binding/figures/direct_identity_v1.png)

*Figure 16. Direct identity readouts and stronger source priors across every fixed layer. Parent recovery does not beat the stronger source comparator.*

### Constrained grammar diagnostic

| Decision rule | Llama 8B | CodeLlama 34B |
|---|---:|---:|
| Original free joint | 6.019% | 13.056% |
| Original free marginal | 8.796% | 27.778% |
| Broad joint-score grammar | 16.204% | 25.093% |
| No-self joint-score grammar (secondary) | 20.648% | 31.944% |
| Broad owner-only grammar | 25.556% | 46.204% |
| No-self owner-only grammar (secondary) | 28.333% | 49.352% |
| Source-owner/TRAIN-version prior + broad joint grammar | 62.222% | 62.222% |
| Source-owner scores + broad owner-only grammar | 100.000% | 100.000% |

Grammar constraints improve free-joint recovery, but CodeLlama joint grammar is below its free marginal reference. Owner-only grammar supplies versions externally; visible source owners plus counting give 100% without neural version scores. This is decoder-assisted reconstruction. It does not establish maintained state, obsolete numeric retrieval, causal use or unfamiliar-program prediction.

![All fixed grammar comparisons. Read source-owner and owner-only controls alongside hidden joint scores.](../../reports/binding/figures/identity_grammar_v1.png)

*Figure 17. All fixed grammar comparisons. Read source-owner and owner-only controls alongside hidden joint scores.*

[Varied schedules](../../reports/binding/schedule_decoding_findings_v1.md), [slot-complete results](../../reports/binding/diversity_decoding_findings_v1.md), [assisted taxonomy](../../reports/binding/diversity_identity_review_findings_v1.md), [direct identities](../../reports/binding/direct_identity_findings_v1.md), [linearity clarification](../../reports/binding/direct_identity_linearity_note_v1.md), [grammar interpretation](../../reports/binding/identity_grammar_interpretation_v1.md).

## 11. Latest study: previous versus current numeric values

This addresses a missing part of the original plan: the old numeric value itself, rather than the identity/version label. Four literal roots and four copies create full-history questions about a queried owner's current value or its value immediately before its last assignment. Previous-value truth is independently checked from that prefix; every model prompt still shows the full body.

The cohort uses fresh numeric seeds on the existing 60 graph families, both neutral lexical forms and four rotations. Equal old/current answers are controls; the primary strata distinguish old values absent from all current slots versus retained in another slot. Three fixed instructions are retained, with strict complete-response signed-integer scoring and a 16-token maximum.

| Model | Question | Correct / n | Accuracy | Invalid |
|---|---|---:|---:|---:|
| llama8b | current | 8,047 / 10,080 | 79.83% | 0 |
| llama8b | previous | 4,225 / 10,080 | 41.91% | 0 |
| codellama34b | current | 2,085 / 10,080 | 20.68% | 6,587 |
| codellama34b | previous | 2,654 / 10,080 | 26.33% | 3,277 |

![New synthesis from the pinned saved reviews. Current/previous rates pool all three instructions and equality controls descriptively; primary reliability remains cell-by-cell. Optimistic ceiling credits every invalid answer while keeping already-valid integer answers unchanged.](../../reports/binding/figures/master_old_value_20261029_v1.png)

*Figure 18. New synthesis from the pinned saved reviews. Current/previous rates pool all three instructions and equality controls descriptively; primary reliability remains cell-by-cell. Optimistic ceiling credits every invalid answer while keeping already-valid integer answers unchanged.*

| Model | Fixed primary cells | Still below 90% even with every invalid answer correct |
|---|---:|---:|
| codellama34b | 24 | 16 |
| llama8b | 24 | 24 |

CodeLlama invalid outputs include 9,397 assignment-wrapped integers, 291 fenced integers and 176 other forms. Only 166 outputs hit the token ceiling; 9,698 invalid outputs stopped normally. On Llama's 7,272 distinct-value historical questions, 2,859 were correct, 2,577 returned the current value and 1,836 returned another wrong integer.

All 40,320 strict scores, 48 primary cells, native input IDs and independent historical/current oracles reconciled. No parser, cohort or gate was relaxed. The formatting ceiling is an optimistic bound on saved outputs, not a capability ceiling for new prompts. Full source history remains visible, so successful answers could still come from rereading.

[Fixed plan](../../reports/binding/old_value_overnight_plan_v1.md), [all results](../../reports/binding/old_value_overnight_findings_v1.md), [response diagnostics](../../reports/binding/old_value_postrun_response_diagnostics_v1.md), [formatting bound](../../reports/binding/old_value_format_ceiling_v1.md).

## 12. Coverage of every original research branch

| Idea from the original document | Current status | What remains |
|---|---|---|
| Controlled integer programs: parallel chains, snapshots/overwrites and interleaved accumulators (§3) | Implemented and independently validated; initial behavioral pilots run | A reliable computed-program regime supporting the full explanatory study. Later successful literal/copy assays do not replace the original computed task. |
| Computed intermediates absent from literals, noncommutative outputs and arithmetic controls (§3–4) | Implemented; several behavioral/calibration studies run, including the new computed bank | Computed-family gates failed. No qualified computed-transfer intervention result is claimed. |
| Naming × genuinely relevant live-variable competition × reassignment (§4, §6) | Partial | Factorial generator and discovery contrasts exist. The later arithmetic-free bank measures naming/updates/distance, but additional available variables include irrelevant competitors and are not a pure live-output-load manipulation. The new [computed-retention study](../../reports/binding/live_load_decision.md) verifies 2/3/4 functional live bindings with all eight variables defined and completed 76,032 audited predictions. Both models failed reliability gates; scheduling/distances remain an explicit design limitation. A robust computed factorial explanation remains unfinished. |
| Same-value-multiset/different-owner pairs, including computed analogues (§4, §8) | Fresh numeric-pair ownership controls completed and audited | Separate and joint copy-site patches preserve the donor value multiset but show weak/nonselective effects at the nominated site. Selective ownership repair and computed generalization remain unresolved. |
| Counterfactual error taxonomy (§6) | Behavioral taxonomy implemented and used; source-oracle-assisted owner/version diagnostic completed and audited | Existing behavioral labels retain ambiguity. The new saved-score analysis separates owner errors, obsolete versions, scalar-version correctness and jointly wrong agreement, with parent referents evaluated at read time. Its saved-score analysis/audit is complete; internal causes remain unidentified. |
| Current-state, previous-version and value-multiset decoding (§7) | Original readouts and matched queried/unqueried accessibility study complete; new 60-family diversity study completed both model readouts and their full audits | Versions 1–4 are now tested in every slot; 8B joint version recovery remains limited. The completed source-oracle-assisted owner/version taxonomy interprets existing statement heads rather than learning full bindings. Other-value disposal, natural causal use and unfamiliar-structure generalization remain unresolved. Failed probes do not establish absence. |
| Probe controls and clean-to-transformed transfer (§7) | Frequency-matched grouped controls completed; broader transfer partial | 75 new CPU fits preserve class frequencies/entropies and reproduce every original value prediction. Queried-value recovery exceeds the shuffled control at answer preparation, with site/proximity and naming limitations. Matching all task complexity, robust lexical/structural transfer and natural causal use remain unresolved. |
| Low-rank/conditioned decoders and train-only representational alignment (§7) | Fixed 336-fit real-data projection/rank/alignment study complete; later queried/unqueried comparison uses all 4,096 coordinates without PCA, alignment or gating | Alignment partly helps some readouts, with projection and whole-state limits retained; no harmless-change equivalence or causal ownership mechanism is established. See the [preparation portfolio](../../reports/binding/preparation_portfolio.md). |
| Ground-truth dependencies and learned directed dependency recovery (§3, §7) | Oracle graphs and earlier fixed-scaffold learned controls complete; actual-schedule adapters and 60 novel graph families now measured | Audited current-definition/version/parent readouts on both models broaden schedule and class coverage; the oracle-assisted error follow-up is complete with its source-map limitation. Statement-index targets use supplied slots and source maps. General node/version discovery, learned full bindings and causal use remain unestablished; retain the [earlier findings](../../reports/binding/relationship_results_findings_v1.md) and [new interim result](../../reports/binding/diversity_decoding_llama8b_interim_v1.md). |
| Algebraic relationship decoding (user-prioritized extension) | Prefix-visible equality, ordering, signed-difference and additive/subtractive targets plus a balanced 1,944-row numeric bank are prepared and audited | Relation heads and value-derived controls are complete. Source-value decoding exceeds hidden direct relations on this literal-initialization bank; arithmetic execution and independent confirmation remain open. See the [findings](../../reports/binding/relationship_results_findings_v1.md). |
| Tracking versus reconstruction during answering (§7 optional study) | Explicit timing/capture phase completed; mechanism unresolved | A 2,592-prompt early/late cue study now holds token multisets, lengths and capture positions fixed across three instructions. Paired prefix checks and full behavior are audited. The common-final-query control is now complete: the late advantage shrinks from 13.04 to 1.70 percentage points. Timing-coupled selective pathway tests remain necessary to distinguish strategies. |
| Value, owner, assignment-version and relevant/irrelevant pathway interventions (§8) | Partial scientific coverage | Literal transfers, late-reference controls and 90,720 earlier-copy interventions under equivalent reordering/renaming ran. Both quantity queries and reciprocal transfers reveal tradeoffs. A further 96,768 fresh-pair single/joint interventions produced weak, nonselective effects at the nominated block. A selective causal binding explanation and pathway specificity are not established. |
| Frozen prediction beyond input features, confidence and cheap behavioral stress tests (§9) | Interfaces, empirical discovery baselines and capacity/access controls completed; frozen final validation unrun | Input/neutral/oracle-assisted tiers completed nested grouped CV on 12,288 consumed targets. Fixed source interactions and same-information encoding controls clarify the baseline comparison. Confidence input preparation and the resumable exact-prompt collector are implemented, with both full GPU runs completed/audited; supported mechanism C, genuine final registration, frozen forecasts and untouched scoring remain. |
| Greater depth/distance, higher competition and unfamiliar combinations (§5, §9) | Four structural extrapolation banks generated and independently validated | Model outcomes remain sealed. No confirmatory prediction/generalization result exists. |
| At least one genuinely new program family (§5) | Scientific extension decision remains open | Sixty new canonical overwrite graphs are prepared and measured within the existing literal/copy language. Novel graph families are not automatically a genuinely new program family. The original plan conditions that extension on a stable core result; numeric variants alone do not satisfy it. |
| Independent generation/fitting replications, precision/power planning and confirmatory registration (§9) | Some seeds, three instruction variants, grouped resampling and infrastructure implemented | Nine new discovery source cohorts and 240 conditional precision scenarios are prepared. Their overlap audit shows structural sharing and prohibits automatic pooling. Completed exploratory intervals, new numeric draws and fit-weighting seeds do not constitute independent structural replication. A final scientific registration and confirmatory study size remain unset. |
| Second-model-family replication (§11 and authorized program) | Two-family behavioral comparisons completed | A selected causal mechanism has not been replicated across families. Benchmarking several cached checkpoints does not satisfy this claim. |
| Literature/novelty comparison with existing CodeCue and closest papers (§13) | Repository/manuscript audit and targeted comparison of four closest sources written | Complete the broader source/version review and reassess novelty around the eventual supported claim. No submission-level novelty claim is established. |
| New binding-study manuscript and predictive figure (§14) | Pilot reports, decision memos and behavioral/probe/intervention figures exist | The existing CodeCue manuscript addresses a different question. A complete manuscript supporting the new central contribution, including unfamiliar-program prediction, is unfinished. |

### The ten authorized experiments, reconciled with later work

| Experiment | Current broader coverage |
|---|---|
| 1. Checkpoint and official prompt audit | Completed, including tokenizer/serialization corrections and cross-backend checks. |
| 2. Arithmetic versus program execution | Behavioral studies completed; no reliable original computed regime qualified. |
| 3. Arithmetic-free binding | Completed across cached checkpoints; CodeLlama 34B and Llama 3.1 8B qualified for scoped discovery. |
| 4. Binding and version competition | Arithmetic-free discovery and broader overwrite-source coverage completed; both diversity model readouts and source-assisted diagnostics completed; direct joint event-identity probes are now complete and audited; computed generalization remains unresolved. |
| 5. Naming by competition by updates | Scoped naming/version/distance contrasts and a computed 2/3/4-live-binding scheduling factorial completed. Both new models failed reliability gates; computation timing/distance remain coupled. The original general interaction claim is unestablished. |
| 6. Tracking versus query-time reconstruction | Explicit timing and common-final-query controls completed with three instructions. The late advantage shrinks from 13.04 to 1.70 points with the final cue; an underlying algorithm and causal-route discrimination remain unresolved. |
| 7. Distributed-state probe diagnostics | Earlier probes, matched controls and queried/unqueried studies complete. New diversity captures cover all-slot versions 1–4; both model readouts and the oracle-assisted taxonomy are audited. Direct joint event-identity probes are now complete on saved features, with source-prior advantages on the parent endpoint retained. General state representation, full learned bindings and natural causal use remain unresolved. |
| 8. Value, ownership and pathway interventions | Several controlled assays run, including earlier-copy transfers under equivalent source transformations; selective ownership/pathway explanation unfinished. |
| 9. Frozen failure prediction | Interfaces and empirical discovery baselines built/run; registered final forecasts, mechanism C and untouched comparisons not run. |
| 10. Second-family replication | Behavioral comparison done; causal-mechanism replication not run. |

The initial experiment-program table recorded early failed prerequisites. Later scoped studies expanded coverage; they did not retroactively pass the computed-program gates. The current coverage table above supersedes old execution status, while original results remain unchanged.

### Deferred extensions

| Proposed branch | Original idea | Status |
|---|---|---|
| Targeted language-model training (§12A) | Compare ordinary training, obfuscation augmentation and binding-targeted training at matched tokens/updates; include shuffled/mismatched supervision controls and unfamiliar combinations. | Not started. No model fine-tuning or binding-specific training ran. The original prerequisite is a reproducible mechanism motivating a specific intervention. |
| Separate explanation-transfer paper (§12B) | Test whether explanations transfer across semantically equivalent inputs: consistent renaming, independent-statement reordering and larger rewrites with explicit correspondences. Calibrate shared/different computation and inconclusive alignment; use semantic-change controls and held-out transformations. | Core precursor experiments now include consistent temporary renaming and independent-statement reordering with local copy-site transfers. A dedicated calibrated equivalence method, held-out transformation test and independent paper contribution remain unstarted. |
| Unlearning (§12C) | Controlled fictional API mappings, matched forget/retain performance, retain-only adaptation reference and prediction of unseen retained-task failures beyond cheap behavior. | Not started. Original rule defers it until the core diagnostic is reliable. |
| Human experiments and broad multilingual evaluation (§1) | Larger external extensions. | Not started; outside the initial pilot. The associative-learning reference is a motivation, not a completed human experiment. |
| Large model sweeps/new checkpoint downloads (§1, execution policy) | Broader scale beyond the initial pilot. | Limited cached-checkpoint comparisons ran after authorization. A large download/training campaign has not begun. |

No targeted language-model training, unlearning or separate explanation-transfer project has been launched by this binding program. Logistic predictors and linear probes are small measurement models, not language-model fine-tuning. Cached two-family comparisons do not constitute causal-mechanism replication.

## 13. What is established, and what is not

| Supported within the recorded discovery scope | Still unresolved |
|---|---|
| Exact source semantics, grouping and independent oracle validation for the generated banks. | A single reliable computed-program assay for the original causal claim. |
| Strong decoding of certain copy-parent relations under supplied scaffolds. | General node discovery, full variable/value/version recovery and natural use. |
| Query/site-dependent numeric accessibility under matched readout capacity. | Whether unqueried information is absent, discarded, reconstructed or encoded differently. |
| Narrow literal-site causal effects and significant interface/timing sensitivity. | Selective owner/version repair that survives wrong-variable/version, same-answer and independent-path controls. |
| Useful discovery error-prediction baselines, including confidence gains in specific contexts. | Mechanistic predictive benefit on genuinely untouched unfamiliar structures. |
| High-throughput reproducible execution with complete failed-gate reporting. | Submission-level novelty or a finished paper supporting the original contribution. |

Group intervals are conditional on consumed structures and often fixed saved fits. Numeric draws, rotations, lexical forms, instruction variants, bootstrap draws and weighting seeds are not independent structural replications. Source-derived maps, literal exposure and externally supplied counters can make an apparently strong decoder score easier to obtain. These qualifications belong beside each result, not only in a final disclaimer.

The primary-source/novelty review exists, but this master report does not reverify the latest external paper versions. Revisit the closest work around the actual final claim before submission. [Recorded source/version review](../../reports/binding/submission_novelty_review.md).

## 14. What next: an ordered experimental plan

**Recommended next priority: isolate historical-value selection in a tractable arithmetic-free assay, before more broad probe sweeps or causal-mechanism claims.** This is a prospective recommendation based on the completed failures, not an experiment already run or a frozen confirmatory registration.

| Order | Task / question | Concrete design and output | Advance condition |
|---|---|---|---|
| 1 | Separate historical query selection from difficulty of reading the relevant prefix. | Fresh grouped discovery sources; pair full-body current, full-body previous and truncated-prefix current questions with identical target truth where appropriate. Include direct-literal/copy controls, all fixed instructions, matched numeric distributions and explicit context-length differences. | Independently validated semantics and sufficient distinct structural support in every cell; report all cells and invalids. |
| 2 | Check answer interface separately from numeric selection. | Prospective bare-integer compliance controls and, if useful, complete finite candidate-string likelihoods under a pinned boundary. Keep greedy accuracy separate; do not rescore the failed cohort with a permissive parser. | A separately documented measurement contract; successful tokenizer/parity QA; no best-wording rescue after validation. |
| 3 | Find the smallest reliable difficulty level. | Vary overwrite count, copy depth, relevant competing owners and distance in a balanced ladder, avoiding the earlier live-load/distance coupling where possible. Preserve a held-back fresh numeric calibration stage. | At least 90% accuracy, at most 5% invalids, adequate support in every fixed prerequisite cell, and independent calibration success before an intervention claim. |
| 4 | Test one error account on exact same cases. | Compare current/old/other-owner/value-multiset accessibility at the same checkpoint with capacity- and label-matched hidden and strong source controls. Predeclare sites from discovery; distinguish answer-compatible aliases. | Evidence that distinguishes one H1–H5 account beyond source reconstruction and query effects. A failed decoder remains inconclusive about absence. |
| 5 | Run a focused selective intervention. | Matched donor/recipient value multisets; explicit owner/version change; reciprocal direction; no-op, self, random, wrong-owner, wrong-version, same-answer/different-state and independent-path controls. | Interpretable effects on dependent quantities with specificity and reliable baseline behavior; otherwise report inconclusive localization. |
| 6 | Freeze mechanism C and compare costs fairly. | Keep source interactions, next-token/joint confidence, raw/oracle-access distinctions and the extra-query comparator. Freeze feature access, model fits, exclusions and forecasts. | A genuine scientific registration tied to immutable forecasts and a supported intervention account. |
| 7 | Perform unfamiliar-program confirmation. | Choose independent structural units, new-family criteria and sample size from conditional precision planning. Score only after the final protocol authorizes opening untouched outcomes. | A defensible incremental predictive result with proper scores, grouping, costs and uncertainty; absence of gain is a reportable result. |
| 8 | Make the paper decision. | Reassess novelty; choose causal/predictive contribution if supported, or a narrower controlled measurement/negative-result report if that is what survives. | Claims match the actual evidence. Mechanism replication, targeted training and transfer/unlearning remain conditional extensions. |

If the tractable calibration still fails, the next decision should be about the task/model/interface rather than another large unqualified causal sweep. More compute can expand evidence; it cannot remove a failed prerequisite by itself.

### Nine open scientific decisions

| Task | Category | Readiness | Prerequisite |
|---|---|---|---|
| Genuinely new structural program family | datasets | needs_scientific_decision | Select a stable core claim and a useful genuinely new family before extension. |
| Choose independent confirmatory structural cohort size | statistics | needs_scientific_decision | Requires a supported claim, independent structural units and a frozen sampling/uncertainty plan. |
| Learned dependency-recovery study | representations | needs_scientific_decision | Only run if the selected explanation requires directed dependency recovery. |
| Supported explanatory mechanism and selective intervention | science | needs_scientific_decision | Select and support an account that predicts selective effects and distinguishes the competing explanations. |
| Independent-structure and second-family causal replication | science | needs_scientific_decision | A selected reproducible causal mechanism must precede causal-mechanism replication; new numeric variants are insufficient. |
| Complete and freeze genuine scientific registration | registration | needs_scientific_decision | Fill hypotheses, intervention/behavior endpoints, feature/access contract, fitting, sites, exclusions and uncertainty before confirmation. |
| Freeze A/B/C/stress-test forecasts before outcomes | prediction | needs_scientific_decision | Requires qualified measurements and immutable model fits/forecasts; original final outcomes remain sealed. |
| Score untouched unfamiliar-program outcomes | science | needs_scientific_decision | Only after genuine registration and forecast freezing with explicit final-evaluation authorization from the study protocol. |
| New study manuscript and predictive figure | writing | needs_scientific_decision | Requires the final supported claim, complete prediction comparison and limitations; current pilot reports are available. |

## 15. Operations, debugging and reproducibility

The latest overnight study passed the 2,280-test frozen-source regression and archived 109 exact test sources. Post-run logging/checker repairs passed 58 and 32 focused tests. The response diagnostic added 23 synthetic guard checks and reproduced its saved report bytes. These totals describe their own checkpoints and overlap; they are not additive counts of unique current tests.

Recorded corrections include tokenizer/official-boundary handling; literal digit versus formatting-space patching; masked-probe centering and prefix-visible surface controls; generated-text-only stop checking; a candidate-event boundary/EOS contract and qualified FP32 parity; a predictor numerical iteration correction; a ten-minute CPU log-worker allocation replacing repeated two-minute timeouts; and failure propagation for auxiliary publication/morning jobs. Original failures and superseded artifacts are retained, with the valid replacement identified explicitly.

The independent October 29 morning check completed at 08:00. The daytime audit verified all seven suite stages, 51 distinct publication/diagnostic pins, 215 frozen source files, 258 configs and the 161-artifact scientific baseline. It observed 89 actual successful reconciliations and one normal not-due worker after the repair, with no failed worker in that window and a maximum successful-export gap of 11 minutes 22 seconds. This is a timestamped audit, not a promise about future scheduler availability. [Daytime verification](../../reports/binding/old_value_overnight_daytime_check_20261029_v1.md).

The latest behavior runs recorded mean GPU utilization of 97.7%/96.0% and timed-generation request rates of 203.8/223.9 per second for 8B/34B. Those rates exclude model loading and warm-up; they are not whole-study throughput. Candidate-event collection also retained separate precision-specific telemetry. Resource ledgers account for work without imposing a cumulative project budget.

Safe metadata-only verification from the repository root:

```bash
PYTHONPATH=src /work/jvl210002/migration/envs/probe-cu129/bin/python \
  scripts/166_binding_old_value_overnight.py check \
  configs/binding/old_value_overnight_20261028_v1/check.json --deep

/work/jvl210002/migration/envs/probe-cu129/bin/python \
  scripts/118_binding_log_scheduler.py status \
  --root /work/jvl210002/migration/codecue
```

Use original source pointers and manifests for historical numerical reproduction; do not rerun completed inference merely to regenerate a report. All model/tokenizer loads go through SLURM. [Current inventory](../../reports/binding/preparation_readiness.md), [automatic log](../../reports/binding/experiment_log.md), [logging guide](../../reports/binding/experiment_logging.md), [implementation checklist](../../reports/binding/implementation_checklist.md).

## 16. Reading guide and complete archive

This document replaces the need to infer current status from the chronological README. Earlier reports remain valuable historical checkpoints and may accurately say “not run” at their recorded dates. The linked current findings, completed receipts and this milestone map resolve those differences.

- **Original plan:** [full unchanged dependvar.txt](dependvar_20261025.txt) from the repository root's parent; the HTML edition also includes an expandable full copy.
- **Current task detail:** [implementation checklist](../../reports/binding/implementation_checklist.md) and [research backlog](../../reports/binding/research_backlog.md).
- **Machine evidence:** the master-report publication review records source/report/figure hashes and the exact data used for the new synthesis figure.
- **Archive:** [report archive CSV](../../reports/binding/master_report_archive_20261029_v3.csv) and [figure archive CSV](../../reports/binding/master_figure_archive_20261029_v4.csv). All locally available report documents and PNG figure revisions are indexed; a historical or superseded figure is not automatically valid evidence for a current claim.

### Complete figure index

| Figure | Context |
|---|---|
| [arithmetic_readout_results_v1.png](../../reports/binding/arithmetic_readout_results_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [calibration_readouts.png](../../reports/binding/calibration_readouts.png) | See originating report for endpoint, cohort and qualifications. |
| [candidate_prediction_alternatives_v1.png](../../reports/binding/candidate_prediction_alternatives_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [competition_effects.png](../../reports/binding/competition_effects.png) | See originating report for endpoint, cohort and qualifications. |
| [copy_path_effects_v1.png](../../reports/binding/copy_path_effects_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [cue_control_effects_v1.png](../../reports/binding/cue_control_effects_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [difficulty_ladder.png](../../reports/binding/difficulty_ladder.png) | See originating report for endpoint, cohort and qualifications. |
| [discovery_confidence_increments_v1.png](../../reports/binding/discovery_confidence_increments_v1.png) | Earlier comparison; corrected v2 is current. |
| [discovery_confidence_increments_v2.png](../../reports/binding/discovery_confidence_increments_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [discovery_controls_results_v1.png](../../reports/binding/discovery_controls_results_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [discovery_prediction_results_v1.png](../../reports/binding/discovery_prediction_results_v1.png) | Earlier figure revision; v2 is current. |
| [discovery_prediction_results_v2.png](../../reports/binding/discovery_prediction_results_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [experiment_program.png](../../reports/binding/experiment_program.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/computation_routing_v1.png](../../reports/binding/figures/computation_routing_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/concept_binding_timeline_v1.png](../../reports/binding/figures/concept_binding_timeline_v1.png) | Conceptual illustration, not an experimental result. |
| [figures/concept_evidence_ladder_v1.png](../../reports/binding/figures/concept_evidence_ladder_v1.png) | Conceptual illustration, not an experimental result. |
| [figures/concept_relationship_types_v1.png](../../reports/binding/figures/concept_relationship_types_v1.png) | Conceptual illustration, not an experimental result. |
| [figures/direct_identity_v1.png](../../reports/binding/figures/direct_identity_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/diversity_decoding_v1.png](../../reports/binding/figures/diversity_decoding_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/identity_grammar_v1.png](../../reports/binding/figures/identity_grammar_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/master_old_value_20261029_v1.png](../../reports/binding/figures/master_old_value_20261029_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/master_plan_20261029_v1.png](../../reports/binding/figures/master_plan_20261029_v1.png) | Retired draft diagram with an incorrect wraparound connector; use master_plan_20261029_v2.png. |
| [figures/master_plan_20261029_v2.png](../../reports/binding/figures/master_plan_20261029_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/overnight_relationships_v1.png](../../reports/binding/figures/overnight_relationships_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/relationship_controls_v1.png](../../reports/binding/figures/relationship_controls_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/schedule_decoding_v1.png](../../reports/binding/figures/schedule_decoding_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/schedule_score_review_v1.png](../../reports/binding/figures/schedule_score_review_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [joint_confidence_increments_v1.png](../../reports/binding/joint_confidence_increments_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [live_load_codellama34b_v2.png](../../reports/binding/live_load_codellama34b_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [live_load_llama31_8b_v2.png](../../reports/binding/live_load_llama31_8b_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [matched_probe_all_slots_v1.png](../../reports/binding/matched_probe_all_slots_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [matched_probe_queried_value_v1.png](../../reports/binding/matched_probe_queried_value_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [probe_curves.png](../../reports/binding/probe_curves.png) | See originating report for endpoint, cohort and qualifications. |
| [query_selectivity_curves_v1.png](../../reports/binding/query_selectivity_curves_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [query_timing_effects_v1.png](../../reports/binding/query_timing_effects_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [stress_prediction_increments_v2.png](../../reports/binding/stress_prediction_increments_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [swap_reset_effects_v2.png](../../reports/binding/swap_reset_effects_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [value_owner_effects_v1.png](../../reports/binding/value_owner_effects_v1.png) | See originating report for endpoint, cohort and qualifications. |
| [value_transfer_effects.png](../../reports/binding/value_transfer_effects.png) | Superseded formatting-space transfer; use value_transfer_effects_v2.png. |
| [value_transfer_effects_v2.png](../../reports/binding/value_transfer_effects_v2.png) | See originating report for endpoint, cohort and qualifications. |
| [figures/variable_binding_master_v1.png](../../reports/binding/figures/variable_binding_master_v1.png) | Master conceptual framework; oracle target values, not experimental predictions. |

### Additional figures from completed and historical studies

The main sections show the central figures. The following gallery preserves the other figure revisions. Earlier/superseded outputs are labeled and do not replace corrected results.

<details markdown="1">
<summary>arithmetic_readout_results_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/arithmetic_readout_results_v1.png)

</details>

<details markdown="1">
<summary>calibration_readouts.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/calibration_readouts.png)

</details>

<details markdown="1">
<summary>candidate_prediction_alternatives_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/candidate_prediction_alternatives_v1.png)

</details>

<details markdown="1">
<summary>competition_effects.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/competition_effects.png)

</details>

<details markdown="1">
<summary>copy_path_effects_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/copy_path_effects_v1.png)

</details>

<details markdown="1">
<summary>difficulty_ladder.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/difficulty_ladder.png)

</details>

<details markdown="1">
<summary>discovery_confidence_increments_v1.png — Earlier comparison; corrected v2 is current.</summary>

![Earlier comparison; corrected v2 is current.](../../reports/binding/discovery_confidence_increments_v1.png)

</details>

<details markdown="1">
<summary>discovery_controls_results_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/discovery_controls_results_v1.png)

</details>

<details markdown="1">
<summary>discovery_prediction_results_v1.png — Earlier figure revision; v2 is current.</summary>

![Earlier figure revision; v2 is current.](../../reports/binding/discovery_prediction_results_v1.png)

</details>

<details markdown="1">
<summary>discovery_prediction_results_v2.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/discovery_prediction_results_v2.png)

</details>

<details markdown="1">
<summary>experiment_program.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/experiment_program.png)

</details>

<details markdown="1">
<summary>figures/master_plan_20261029_v1.png — Retired draft diagram with an incorrect wraparound connector; use master_plan_20261029_v2.png.</summary>

![Retired draft diagram with an incorrect wraparound connector; use master_plan_20261029_v2.png.](../../reports/binding/figures/master_plan_20261029_v1.png)

</details>

<details markdown="1">
<summary>figures/schedule_decoding_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/figures/schedule_decoding_v1.png)

</details>

<details markdown="1">
<summary>figures/schedule_score_review_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/figures/schedule_score_review_v1.png)

</details>

<details markdown="1">
<summary>live_load_codellama34b_v2.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/live_load_codellama34b_v2.png)

</details>

<details markdown="1">
<summary>matched_probe_all_slots_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/matched_probe_all_slots_v1.png)

</details>

<details markdown="1">
<summary>matched_probe_queried_value_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/matched_probe_queried_value_v1.png)

</details>

<details markdown="1">
<summary>probe_curves.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/probe_curves.png)

</details>

<details markdown="1">
<summary>query_timing_effects_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/query_timing_effects_v1.png)

</details>

<details markdown="1">
<summary>swap_reset_effects_v2.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/swap_reset_effects_v2.png)

</details>

<details markdown="1">
<summary>value_owner_effects_v1.png — See originating report for endpoint, cohort and qualifications.</summary>

![See originating report for endpoint, cohort and qualifications.](../../reports/binding/value_owner_effects_v1.png)

</details>

<details markdown="1">
<summary>value_transfer_effects.png — Superseded formatting-space transfer; use value_transfer_effects_v2.png.</summary>

![Superseded formatting-space transfer; use value_transfer_effects_v2.png.](../../reports/binding/value_transfer_effects.png)

</details>

