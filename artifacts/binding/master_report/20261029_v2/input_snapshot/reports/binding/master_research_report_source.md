# Variable binding, updating and relationships: master research report

**Status as of October 29, 2026.** This is the master record for the study proposed in `dependvar.txt`, including the subsequent user-requested dependency and algebraic relationship work. It summarizes completed work, preserves negative findings, and gives a concrete next plan. It is a research status report, not an empirical paper abstract or a claim that the original scientific objective is finished.

## 1. Where we stand

**The infrastructure and a large discovery program are complete. The central causal explanation and untouched unfamiliar-program validation are not.** We have working semantic datasets, two main model families, behavior and representation measurements, several intervention assays, strong error-prediction comparators, and audited results. We have not established that a selective binding/version mechanism explains the errors and predicts them on new program families.

The strongest findings are:

- **Structure can be decoded without reliable execution.** Copy-parent graphs are often recovered well under a supplied scaffold, including computed-root programs whose numeric readouts and generated answers are poor.
- **Query-dependent accessibility is large in one controlled readout.** Queried and unqueried values differ strongly at the saved answer-preparation site. This concerns the tested decoders, not proof that unqueried values were erased.
- **Source-only controls substantially change the interpretation.** Deriving relations from source-predicted values beats direct hidden algebraic decoding on literal programs. Explicit source owners and external counters can reconstruct assignment identities perfectly in the grammar diagnostic.
- **The intervention evidence is narrow or inconclusive.** Literal-site transfers affect answers in a small interface family, but fresh ownership controls do not establish selective transport. An initial query-timing gap becomes much smaller when the final cue is held constant.
- **Cheap confidence is a serious prediction baseline.** CodeLlama has useful discovery gains from next-token confidence; combining confidence bundles sometimes helps further. There is no frozen mechanism-based predictor or untouched final comparison.
- **Latest historical-value calibration failed.** Current and previous values are not reliably distinguished across the fixed cells. CodeLlama also has substantial formatting failures, but formatting alone cannot explain the failed gates.

{{latest_summary}}

**Read the task count correctly:** {{readiness_summary}}. “Ready” combines implemented tools and completed scoped work; it does not mean that the scientific claim is supported. The last full binding regression passed 2,280 tests for the frozen overnight source. Later operational fixes passed 90 focused tests; these are overlapping checks, not another 90 independent scientific experiments or a new full-suite total.

## 2. The original question and how this differs from CodeCue

The original question was: **What determines whether transformers correctly update and use variable bindings, and can the identified mechanism predict failures on unfamiliar programs?** A binding includes a variable, its assignment version and its value. Updating, recovering information, using it for an answer, and predicting future errors are separate requirements.

The existing CodeCue manuscript, *Misleading Identifiers Change What Code Traces Write*, concerns length/sum identifier conflicts, erroneous trace writes, recoverable digits, span interventions and expression formats. The new study adds controlled multi-variable integer programs, explicit old/current versions, value-ownership and dependency controls, and the intended causal-to-predictive validation chain. Existing manuscript results are not imported as new binding-study evidence. [Repository/manuscript audit](repository_audit.md).

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

{{milestone_figure}}

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

Published datasets provide external behavioral references. Controlled synthetic banks provide exact intermediate state, ownership and intervention truth that those benchmarks do not directly supply. Downloading a cited dataset alone does not answer the causal binding question. [Published dataset review](published_datasets.md), [overlap/replication audit](replication_preparation_v1.md), [precision planning](precision_planning_v1.md).

## 5. Behavioral results and calibration

### Original computed pilot

{{table:pilot_report.md:0}}

This early CodeLlama 7B subset contains 720 responses over 60 bases and 38 parent-template clusters. Its near-floor accuracy made the intended computed-mechanism interpretation infeasible. Compatible competing-variable/obsolete answers overlap and are not proven internal causes. Later literal/copy improvements do not repair this original result. [Pilot and interface diagnostics](pilot_report.md).

### Published benchmarks and interface lessons

{{table:published_baseline_review.md:0}}

These are the report's separately defined literal/letter scores. The initial direct CRUXEval released-postprocessor score was 3/800 because the output structure did not match that processing path; this is not interchangeable with 290/800 answer-block literal scoring. A subsequent controlled completion serialization yielded 295/800 direct. CoT remains a different protocol. [Benchmark audit](published_baseline_review.md), [serialization comparison](serialization_comparison.md).

### Literal binding discovery versus computed execution

Arithmetic-free discovery qualified the main two checkpoints for scoped literal/copy work. Update count and trailing copies affected current answers, and naming effects depended on model/query. Available competing variables were not all output-relevant, so that bank is not a clean manipulation of functional live load. The explicit computed-retention design later held all variables defined while varying functional relevance; reliability remained poor:

{{table:live_load_decision.md:0}}

The separate arithmetic/readout study collected 12,288 responses and failed all four fixed model/protocol gates. The later computation/context/copy study collected 40,200 responses and qualified 0/6 prospective gates. Changing arithmetic form, context and wording strongly changes performance, but these comparisons do not isolate binding interference.

{{figure:live_load_llama31_8b_v2.png|Computed retention results for Llama 8B. All fixed contrasts remain exploratory after the failed clean/arithmetic gate.}}
{{figure:figures/computation_routing_v1.png|Matched computation, context and copy calibration. Root-format and context effects cannot alone identify whether arithmetic, routing or selection failed.}}

Sources: [competition](competition_results.md), [computed retention](live_load_decision.md), [arithmetic/readout](arithmetic_readout_decision.md), [computation routing](computation_routing_findings_v1.md).

## 6. Representation accessibility, previous values and alignment

The original computed probes fitted training states very well but generalized weakly. Corrected analyses centered masked labels correctly and matched surface features to the visible prefix; regularization and increased numeric diversity were tested. Poor readout does not show that the information is absent.

Frequency-matched grouped controls preserved label frequencies/entropy. The later query-selectivity study used equally sized independent categorical heads on the same coordinates. At the fixed neutral block-24 saved `pre_answer` site, queried accuracy was 88.89%, unqueried 9.4184%, a 79.4705-point gap with conditional group interval [75.8670, 83.5069]. This was an earlier saved formatting boundary, not the later corrected digit boundary.

{{figure:query_selectivity_curves_v1.png|All fixed query-selectivity curves. The large queried/unqueried difference establishes decoder-specific accessibility on consumed structures, not disposal, ownership or natural causal use.}}

Train-only reduced-rank/Procrustes work completed 336 readout fits. At the earlier answer-preparation site, misleading-current accuracy improved from 19.01% to 25.39%, saved-value accuracy from 30.34% to 35.68%, but both-values recovery only from 0.78% to 1.56%. Alignment is a useful sensitivity analysis; it does not demonstrate equivalent computation or full-state recovery. [Matched controls](matched_probe_controls_decision.md), [query accessibility](query_selectivity_findings.md), [alignment/rank findings](continuation_followup.md).

## 7. Interventions and tracking versus reconstruction

### Literal value transfer

The corrected literal assay had 392/432 correct full baselines and 20,160 intervention forwards. Raw block-0 transfer changed affected digit outcomes on 144/144 queries with 0/144 replacements on unchanged-answer controls. This supports a narrow literal-site causal contribution. Ownership was less specific on the full cohort: 118/144 affected replacements and 27/144 unchanged-answer replacements. Conditioning on already-correct baselines is secondary and does not replace the full-cohort result.

The first run patched a formatting space rather than the digit; its apparent zero transfer is not valid answer-transfer evidence. The correction used the same fixed space for every input and preserved the original artifact. [Boundary correction](value_transfer_boundary_correction.md), [corrected decision](value_transfer_decision.md).

{{figure:value_transfer_effects_v2.png|Corrected literal transfer. Use the corrected digit-boundary figure; the earlier figure is historical, not an alternative valid zero-effect result.}}

### Earlier-copy routes, ownership and timing controls

Earlier-copy/reordering/renaming studies ran 90,720 interventions. Effects differed by quantity and direction: improving one queried value could harm another. Fresh numeric ownership controls then ran 96,768 intervention forwards plus 7,776 baselines; nominated copy-site effects were weak or nonselective.

{{table:mechanism_followup_decision.md:0}}

The original explicit timing study found higher late-query accuracy. A matched common-final-query control substantially reduced that gap:

{{table:mechanism_followup_decision.md:1}}

{{figure:cue_control_effects_v1.png|A common final cue shrinks the early/late timing gap. Query timing by itself therefore does not distinguish maintained state from reconstruction.}}

No general selective ownership/version/pathway mechanism follows from these assays. [Timing/copy decision](timing_and_copy_decision.md), [fresh ownership and final-cue decision](mechanism_followup_decision.md).

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

{{table:discovery_prediction_decision.md:0}}

Raw neutral behavior adds no clear Brier gain over input features in either checkpoint. Scoring the neutral response with an oracle helps under its stronger information contract. Capacity/access controls preserve original predictions and expose deterministic feature-encoding effects. [Original prediction decision](discovery_prediction_decision.md), [capacity/access controls](discovery_controls_decision.md).

### Next-token confidence

{{table:discovery_confidence_decision.md:0}}

CodeLlama benefits beyond strong input interactions. Llama's corresponding Brier interval crosses zero, though its log loss improves. Cross-model absolute Brier values do not rank language-model quality because failure prevalence differs.

{{figure:discovery_confidence_increments_v2.png|Discovery confidence increments with the corrected source comparison. Intervals condition on saved out-of-fold predictions and are not final unfamiliar-program validation.}}

### Complete-answer events, joint confidence and an extra query

The qualified full-answer banks contain 12,288 prompts across both checkpoints, 33 numeral candidates and declared EOS events. FP32 parity smokes, complete-prefix boundaries and immutable audits passed. Candidate-event statistics alone show no clear Brier advantage over next-token confidence in any of ten matched comparisons:

{{table:candidate_prediction_findings.md:0}}

Combining both bundles is a different comparison. CodeLlama source-interaction Brier improves from 0.116641 to 0.113499, increment 0.003142 [0.000158, 0.006277]; all five Llama conditional intervals cross zero. The extra instructed query gives context-dependent gains, with no clear Brier advantage over joint confidence in any of ten fixed comparisons.

{{figure:joint_confidence_increments_v1.png|Complementarity of the two saved confidence bundles across all fixed contexts; this does not revise the earlier alternative-bundle null result.}}
{{figure:stress_prediction_increments_v2.png|Corrected extra-query comparator. Additional observations and oracle access are distinct contracts, not free mechanistic features.}}

These conditional bootstrap intervals resample structural groups without refitting or multiplicity adjustment. They do not establish an independent generalization gain. [Candidate events](candidate_prediction_findings.md), [joint confidence](joint_confidence_findings.md), [extra-query comparator](stress_comparator_findings.md).

## 9. Dependency and algebraic relationships

This branch covers **both** user-requested relationship types: directed data dependencies/assignment versions and algebraic relationships such as equality, ordering, signed differences and sum/subtraction triples.

### First balanced relationship bank

{{table:relationship_results_findings_v1.md:0}}

The stronger source-predicted-values → relations pipeline reached 98.108%, exceeding direct hidden algebraic decoding. Hidden first-parent recovery distinguished equal-numeric-state provenance pairs at 96.759%, but the texts explicitly differ in copy-source syntax. These findings concern accessible information under the supplied scaffold, not a special neural relation store or causal use.

{{figure:figures/relationship_controls_v1.png|Relationship controls: include the stronger source-value pipeline and equal-state/different-provenance comparisons, not only weak direct text heads.}}

### Literal versus computed roots across both checkpoints

{{table:overnight_20261027_findings_v1.md:0}}

{{table:overnight_20261027_findings_v1.md:2}}

Algebraic and numeric decoding weakens on computed roots while graph recovery remains high. At the computed final prompt, queried numeric values score 7.493%/6.927% for 8B/34B, versus a 6.173% TRAIN prior. The matched generated-answer contrast is:

{{table:overnight_20261027_findings_v1.md:5}}

The suite completed 32,076 capture prefills, 14,580 generated answers, 270 ridge factorizations, 1,574,640 saved-parameter row checks and 524,880 frozen literal-to-computed applications. Shared panel rows and fit seeds are dependent reuse. Strong graph recovery does not show that the model knows all numeric values and merely fails to use them.

{{figure:figures/overnight_relationships_v1.png|Two-model literal/computed results, transfer and generated behavior. The graphs use supplied node/scaffold identities; root formats also change arithmetic and token context.}}

[Complete first-bank findings](relationship_results_findings_v1.md), [overnight findings](overnight_20261027_findings_v1.md), [posthoc exact-case/query analysis](overnight_score_behavior_findings_v1.md).

## 10. Actual versions, direct identities and grammar decoding

### Varied schedules and repaired class coverage

The first varied-schedule study used actual assignment versions. Its apparent 89.655% row-weighted version score fell to 53.333% under equal-family weighting, while the source-text baseline scored 100%. Uneven class/family coverage limited interpretation.

The slot-complete bank then ensured versions 1–4 occurred in every slot across 60 canonical families. Its fixed layer-24/site-7 **whole-task** direct hidden results are:

{{diversity_table}}

{{figure:figures/diversity_decoding_v1.png|Slot-complete current-definition/version/parent recovery. Whole-task rates require every head correct; they are not pooled per-slot accuracies.}}

### Source-assisted taxonomy versus direct joint identities

The source-assisted analysis mapped fixed statement predictions to owners/versions using source truth; parent identities were evaluated at the moment of consumption, even when obsolete later. Pooled owner accuracy is high, but the owner TRAIN prior is already 100%. This is assisted interpretation, not a learned complete binding decoder.

Direct joint owner/version heads removed the per-program identity map after prediction. Whole-write recovery is 28.519%/35.463% for 8B/34B; whole-parent recovery 24.630%/30.093%, below a stronger source-owner/TRAIN-version comparator's 40%. All-eight recovery is 6.019%/13.056%. First-event constant versions and rare version-4 classes remain explicit limitations. Joint and factorized component scores are linearly related; differing argmax rules are not independent representational evidence.

{{figure:figures/direct_identity_v1.png|Direct identity readouts and stronger source priors across every fixed layer. Parent recovery does not beat the stronger source comparator.}}

### Constrained grammar diagnostic

{{table:identity_grammar_interpretation_v1.md:0}}

Grammar constraints improve free-joint recovery, but CodeLlama joint grammar is below its free marginal reference. Owner-only grammar supplies versions externally; visible source owners plus counting give 100% without neural version scores. This is decoder-assisted reconstruction. It does not establish maintained state, obsolete numeric retrieval, causal use or unfamiliar-program prediction.

{{figure:figures/identity_grammar_v1.png|All fixed grammar comparisons. Read source-owner and owner-only controls alongside hidden joint scores.}}

[Varied schedules](schedule_decoding_findings_v1.md), [slot-complete results](diversity_decoding_findings_v1.md), [assisted taxonomy](diversity_identity_review_findings_v1.md), [direct identities](direct_identity_findings_v1.md), [linearity clarification](direct_identity_linearity_note_v1.md), [grammar interpretation](identity_grammar_interpretation_v1.md).

## 11. Latest study: previous versus current numeric values

This addresses a missing part of the original plan: the old numeric value itself, rather than the identity/version label. Four literal roots and four copies create full-history questions about a queried owner's current value or its value immediately before its last assignment. Previous-value truth is independently checked from that prefix; every model prompt still shows the full body.

The cohort uses fresh numeric seeds on the existing 60 graph families, both neutral lexical forms and four rotations. Equal old/current answers are controls; the primary strata distinguish old values absent from all current slots versus retained in another slot. Three fixed instructions are retained, with strict complete-response signed-integer scoring and a 16-token maximum.

{{old_value_table}}

{{figure:figures/master_old_value_20261029_v1.png|New synthesis from the pinned saved reviews. Current/previous rates pool all three instructions and equality controls descriptively; primary reliability remains cell-by-cell. Optimistic ceiling credits every invalid answer while keeping already-valid integer answers unchanged.}}

{{format_table}}

CodeLlama invalid outputs include 9,397 assignment-wrapped integers, 291 fenced integers and 176 other forms. Only 166 outputs hit the token ceiling; 9,698 invalid outputs stopped normally. On Llama's 7,272 distinct-value historical questions, 2,859 were correct, 2,577 returned the current value and 1,836 returned another wrong integer.

All 40,320 strict scores, 48 primary cells, native input IDs and independent historical/current oracles reconciled. No parser, cohort or gate was relaxed. The formatting ceiling is an optimistic bound on saved outputs, not a capability ceiling for new prompts. Full source history remains visible, so successful answers could still come from rereading.

[Fixed plan](old_value_overnight_plan_v1.md), [all results](old_value_overnight_findings_v1.md), [response diagnostics](old_value_postrun_response_diagnostics_v1.md), [formatting bound](old_value_format_ceiling_v1.md).

## 12. Coverage of every original research branch

{{original_branch_table}}

### The ten authorized experiments, reconciled with later work

{{experiment_coverage_table}}

The initial experiment-program table recorded early failed prerequisites. Later scoped studies expanded coverage; they did not retroactively pass the computed-program gates. The current coverage table above supersedes old execution status, while original results remain unchanged.

### Deferred extensions

{{extension_table}}

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

The primary-source/novelty review exists, but this master report does not reverify the latest external paper versions. Revisit the closest work around the actual final claim before submission. [Recorded source/version review](submission_novelty_review.md).

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

{{open_decisions_table}}

## 15. Operations, debugging and reproducibility

The latest overnight study passed the 2,280-test frozen-source regression and archived 109 exact test sources. Post-run logging/checker repairs passed 58 and 32 focused tests. The response diagnostic added 23 synthetic guard checks and reproduced its saved report bytes. These totals describe their own checkpoints and overlap; they are not additive counts of unique current tests.

Recorded corrections include tokenizer/official-boundary handling; literal digit versus formatting-space patching; masked-probe centering and prefix-visible surface controls; generated-text-only stop checking; a candidate-event boundary/EOS contract and qualified FP32 parity; a predictor numerical iteration correction; a ten-minute CPU log-worker allocation replacing repeated two-minute timeouts; and failure propagation for auxiliary publication/morning jobs. Original failures and superseded artifacts are retained, with the valid replacement identified explicitly.

The independent October 29 morning check completed at 08:00. The daytime audit verified all seven suite stages, 51 distinct publication/diagnostic pins, 215 frozen source files, 258 configs and the 161-artifact scientific baseline. It observed 89 actual successful reconciliations and one normal not-due worker after the repair, with no failed worker in that window and a maximum successful-export gap of 11 minutes 22 seconds. This is a timestamped audit, not a promise about future scheduler availability. [Daytime verification](old_value_overnight_daytime_check_20261029_v1.md).

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

Use original source pointers and manifests for historical numerical reproduction; do not rerun completed inference merely to regenerate a report. All model/tokenizer loads go through SLURM. [Current inventory](preparation_readiness.md), [automatic log](experiment_log.md), [logging guide](experiment_logging.md), [implementation checklist](implementation_checklist.md).

## 16. Reading guide and complete archive

This document replaces the need to infer current status from the chronological README. Earlier reports remain valuable historical checkpoints and may accurately say “not run” at their recorded dates. The linked current findings, completed receipts and this milestone map resolve those differences.

- **Original plan:** [full unchanged dependvar.txt](../../../dependvar.txt) from the repository root's parent; the HTML edition also includes an expandable full copy.
- **Current task detail:** [implementation checklist](implementation_checklist.md) and [research backlog](research_backlog.md).
- **Machine evidence:** the master-report publication review records source/report/figure hashes and the exact data used for the new synthesis figure.
- **Archive:** {{archive_links}}. All locally available report documents and PNG figure revisions are indexed; a historical or superseded figure is not automatically valid evidence for a current claim.

{{figure_catalog}}
