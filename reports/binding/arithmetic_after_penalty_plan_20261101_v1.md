# After the penalty check: questions that can change the explanation

Planning document; the saved-score diagnostic below is now completed. New model-fitting and generation experiments are not submitted. The completed penalty-path findings and numerical audit must be read alongside this plan. The original conditional study, its postrun diagnostic and the frozen continuation protocol remain separate records.

Updated November 1, 2026: incorporates the requested execution-state and written-reasoning experiments. Central question: **as a model simulates code execution, what values, variable bindings, assignment versions and relationships are recoverable, and which of them influence its written reasoning and answers?** Accessibility, correctness, behavioral dependence and faithfulness are separate endpoints. Preserved values with disrupted bindings, followed by selective repair, is a possible outcome rather than an assumed paper conclusion.

The [full consolidated checklist](implementation_checklist.md#current-consolidated-checklist) covers the original ten experiments, later exploratory branches and deferred extensions. The following IDs identify the new integrated study; they do not renumber the original experiments or count earlier cohorts as fresh replication.

| ID | Experiment | Current status / dependency |
|---|---|---|
| N1 | Fresh prospective protocol/answer-format calibration | Planned; freezes wordings, grammar, ceilings and competence criteria before new responses. |
| N2 | Same-example temporal values, bindings, versions, written steps and answers | Planned; generated-trace capture and target-visibility instrumentation required. |
| N3 | Value-multiset-preserving binding swaps and equal-value/different-provenance controls | Earlier literal controls completed; integrated computed/CoT study planned. |
| N4 | Current versus obsolete versions; operand versus irrelevant overwrites | Source banks and exploratory calibration pairs completed; formal temporal replication planned. |
| N5 | Shared variable-query and typed dependency/algebraic readouts | Earlier relation heads completed; integrated structured comparison planned. |
| N6 | Internal owner/version interventions with selective downstream predictions | Earlier transfer assays completed; new computed/CoT study gated by an interpretable assay and validated instrumentation. |
| N7 | Written-CoT value edits/removals followed by resumed generation | New planned experiment; separate from activation patching and original unedited trajectories. |
| N8 | Naming × relevant live-variable load × reassignment | Earlier scoped studies completed; new controlled integrated factorial planned. |
| N9 | Independent-family confirmation, frozen failure prediction and mechanism replication | Gated by a selected supported account and frozen scientific registration. |

The eight extended TRAIN selections all kept alpha 10,000. Adding larger penalties therefore changes our confidence in the finite search, rather than the selected predictions. Repeating a wider ridge sweep is no longer the first priority. The next experiments should distinguish an unsuitable numeric loss, a query-dependent readout site, and difficulty retaining old values after overwrites. These explanations can coexist.

## 1. Audit exact-value failure before fitting a new architecture

Completed in the [saved-score diagnostic](arithmetic_exact_value_diagnostic_20261101_v1.md): both joint probes have zero all-four exact recovery; only 24/3,168 computed DEV slots have values absent from that slot's TRAIN support. Zero/computed-family-mode computed exact accuracy is 8.90%, above either joint probe. This rules out unseen numeric labels as an explanation for most errors, not unseen compositions or contexts.

Retain the selected prediction files. Report computed-value rounded exact accuracy, MAE, target frequencies, and out-of-TRAIN-support targets by structural family and variable role. Retain the fixed zero predictor and TRAIN-estimated mode; estimate a separate mode inside each fitting fold if it participates in selection. Distinguish all-four exact recovery from the average of four marginal accuracies. A numeric average near the right value can still be the wrong integer.

Existing categorical, circular and ordinal results remain in the comparison. Any new endpoint-specific classifier must improve on the corresponding TRAIN class prior, not only a rounded regression. Choose its regularization/calibration on TRAIN folds and report unsupported classes. Do not turn nearest-code distances into probabilities without a declared probabilistic model and calibration procedure.

## 2. Fresh prospective behavior calibration, then temporal captures

Create a separate calibration cohort with closed structural components and no overlap with formal evaluation or previously inspected calibration components. Freeze source generation, query scopes, all wording variants, the answer grammar and generation ceilings before collecting responses. Include output-only, intermediate-query and stepwise protocols. A common total token ceiling controls that ceiling; it does not make protocol prompts or internal computation identical.

Score the declared answer grammar, truncation and malformed answers separately. Preserve the earlier failed output-only competence gates. Declare a new prospective competence criterion and report each protocol/checkpoint independently; do not choose the easiest wording after inspection. Use this calibration to decide which formal contrasts are interpretable, rather than retroactively upgrading the old pilot.

Before prefix reuse, compare native-prefix and full-prompt activations numerically on GPU, including padding/batching conditions. For generated traces, record pretrace and preanswer sites and whether the target has already been emitted. Keep generated-trace states separate from gold teacher-forced states. The prepared source-prefill inventory is an efficiency opportunity, not a completed equivalence test.

Formal temporal contrasts should pair operand overwrites with matched irrelevant overwrites while holding the retained target fixed. Replicate the current 36-pair calibration pattern on new closed components. Keep repeated wording/query contexts clustered with their source component, rather than counting them as independent samples.

## 3. A small shared readout comparison after the access contract is fixed

Compare independent scalar heads with one shared variable-query decoder and one controlled interaction/nonlinear comparator. Declare exactly which hidden state, variable identity, source features and mention positions each receives. Query-only and source-plus-query controls are essential: a contextual mention query can carry the answer itself. Fit normalizers and any learned projections on the fitting partition only. Report parameters, feature dimensions, training effort and family learning curves separately.

For dependencies, predict directed operand-typed edges between assignment versions. For algebraic relations, score pair/triple predicates such as ordering and `z = x + y`, including true relations that are not printed assignments and false structural distractors. Evaluate raw outputs before optional symbolic consistency repair; report the repair's contribution separately. Include complete graphs/states, class balance and permutation checks alongside local edge accuracy.

Freeze the small model comparison and selection objective before submission. The current inspected DEV cohort supports exploratory comparisons. A final generalization claim needs untouched program families under a frozen recipe. Causal interventions follow only after the representation and intervention controls are specified; a successful readout alone does not establish natural causal use.

## 4. Same-example temporal state and distinguishable error accounts (N2–N4)

Join each source, interpreter event, generated prefix, native token boundary, probe prediction, written claim and final answer by immutable case/event IDs. Keep source position, execution step, model layer and generated reasoning step as distinct axes. Generated prose can omit, merge or reorder interpreter steps; declare the alignment policy and report unaligned cases rather than forcing a match. Record code truth and any unambiguous model-stated value separately.

At declared pre-write sites, predict variable values, their owner/assignment identities, designated obsolete versions, value multisets with multiplicity, and directed operand-typed dependencies. Record the first appearance of each target value and of an explicit variable–value claim in the generated trace. Report never-emitted, already-emitted and unaligned cases separately. A numeral already visible in source or another trace claim is a copying opportunity even before the relevant target claim. Do not teacher-force the correct reasoning to obtain a natural-generation measurement.

On the SAME cases and sites, cross oracle-correct versus incorrect probe predictions with correct versus incorrect written steps and answers; retain parsing failures and denominators. A correct probe/wrong output cell establishes a scoped dissociation in accessibility and output, not failure to use information by itself. Probe quality must be measured on the fresh regime before interpreting those cells. Earlier cached probes and continuation results use different cohorts and do not supply this joint evidence.

Use matched states with the same value multiset but swapped variable owners, including computed intermediates and noncommutative downstream expressions. Keep semantic-preserving consistent renaming distinct from semantic-changing assignment swaps. When numeric values coincide, value accuracy cannot identify the owner: test assignment provenance, version identity and subsequent dependency-sensitive behavior. Neither equal-value provenance nor a constant slot code is itself evidence of an internally maintained binding.

For an illustrative source, `x=2; y=5; z=x+1; x=9; print(z)`, `3` is correct, `6` is compatible with substituting the earlier `y`, and `10` is compatible with recomputing from the updated `x`. The source generator must verify these alternatives and retain every compatible label when causes collide. An answer matching a candidate is counterfactual-consistent, not proof of its internal cause. Pair operand and irrelevant overwrites while holding the retained target fixed, and include arithmetic-only, copying and no-overwrite controls.

## 5. Selective internal interventions (N6)

Before submission, specify donor/recipient correspondences, variable and version identities, layer/site, patch scope, high-level counterfactual outcomes and descendant/independent targets. Fit any alignment or subspace on TRAIN only; choose sites/parameters in discovery and freeze them for replication. Validate native-token geometry, no-op/self replay and effective perturbation before interpreting effects.

Include reciprocal donors, wrong-owner, wrong-version, unrelated-site, norm-matched/random, unchanged-answer and same-answer/different-state controls where supported. Report actual control coverage and exclusions. Preserve the value multiset when testing ownership, and separate pre-computation patches from post-write patches. Dependency edges indicate use, but functional influence can vanish (for example, subtraction of a value from itself); interpreter counterfactuals must determine which output changes are predicted.

Measure exact predicted counterfactual answers, complete candidate-string likelihood changes where declared, dependent-target effects, unrelated-target stability and collateral damage. A restoration result needs the predicted pattern across quantities, not just higher final-answer accuracy. An activation intervention can create an artificial computation; even selective repair needs held-out controls before a natural-use interpretation. Failure or broad effects leave localization inconclusive. This experiment does not require a new language-model training method.

## 6. Written-CoT interventions and resumed generation (N7)

Save naturally generated prefixes and resume the same checkpoint after a predeclared edit to one intermediate claim. Branch into: unchanged prefix; incorrect value substitution; correct-value substitution when the original claim is wrong; removal of the selected step; and a meaning-preserving paraphrase or matched irrelevant edit. Match token length/position where feasible, record remaining differences, and declare whether the edit changes one claim or all dependent claims. Preserve the original response and scores.

Score the resumed text and answer against BOTH original interpreter truth and the declared edited-prefix counterfactual. Record following, correcting, contradicting or not observably depending on the edit only when outputs distinguish these categories; otherwise mark ambiguous. Separate greedy and sampled runs, and use independent sampling seeds when sampling. Keep all descendants of a source/prefix in the same structural component for fitting and uncertainty.

The edited branches measure dependence on supplied reasoning text. They do not reveal the unedited run's hidden computation or establish that unmentioned information was unused. States after an edited target value has been supplied belong to an explicit edited-prefix condition; they cannot count as pre-value natural decodability. Analyze internal patches and text edits separately before any joint intervention design.

## 7. Factorial explanation, prediction and paper decision (N8–N9)

Cross neutral, informative/clean and misleading names with genuinely output-relevant live-variable competition and reassignment. Preserve naming twins' semantics. Match arithmetic operations, numeric distributions, query shape, distance and surface/token properties where feasible; disclose remaining coupling. Retain all declared wordings. Use diagnostics that distinguish wrong-variable, wrong-version, arithmetic and output/interface alternatives without assigning an internal cause from answer identity alone.

Test clean-to-renamed transfer alongside within-condition decoding to distinguish readout shift from behavioral loss. Keep independent heads, a shared variable-query model and a small declared interaction comparator; retain source/query/position/class-prior controls and family learning curves. Any prequential/MDL analysis needs an actual probability model and prefix-only fitting/selection. It remains a separate planned complexity analysis, not a completed method or a prerequisite for every experiment.

Choose a primary account from binding interference, value computation/accessibility, failure to use an available binding, query-time reconstruction and harmless representational change only after discovery. Freeze counterfactual predictions, permitted measurements, baseline A/B/C predictors, query costs, ambiguity/exclusion rules and uncertainty/multiplicity handling before untouched outcomes. Replicate a supported selective effect on independent structures and a second checkpoint family. New numeric draws, multiple heads, fitting seeds or extra wording variants are not independent structural replication.

The strongest possible paper would explain a reproducible execution failure with selective causal evidence and unfamiliar-program prediction. A controlled descriptive or negative result is another possible outcome, but needs a substantial supported finding. Correctness and faithfulness must not be equated; complete state recovery, binding disruption and binding repair remain unestablished. Final/extrapolation outcomes remain sealed under the original protocol.

## 8. Claim-specific literature follow-up

The prior discussion identified the following primary sources for explicit comparison. The summaries reflect the inspected descriptions/abstracts; full method and overlap review remains a checklist item. Keep the frozen 23-paper review/register unchanged and record later review in a separate addendum.

- [Unveiling Code Pre-Trained Models: Investigating Syntax and Semantics Capacities](https://doi.org/10.1145/3664606): prior code syntax/semantic and dependency probing; generic code probing is not the proposed novelty.
- [Measuring Faithfulness in Chain-of-Thought Reasoning](https://arxiv.org/abs/2307.13702): reasoning-text interventions already have precedent; N7 needs interpreter-grounded, version-specific comparisons.
- [From Concept Alignment to Causal Grounding: An Intervention Test of Chain-of-Thought Faithfulness](https://arxiv.org/abs/2609.23065): internal alignment and causal-ablation precedent; N6 needs a specific execution-state contribution beyond alignment alone.
- [The Mirage of Explainability: A Survey on Chain-of-Thought Faithfulness in Large Language Models](https://aclanthology.org/2026.emnlp-main.614/): broader faithfulness terminology and evidence review before manuscript claims.

These choices implement the existing [23-paper review](probing_literature_review_20261031_v1.md), particularly its conditional controls, shared structured queries, and complexity/learning-effort sections. This is a project-specific design inference, not a claim that a particular architecture is guaranteed to work.

[Penalty-path findings](arithmetic_penalty_path_findings_20261101_v1.md) · [Frozen protocol](arithmetic_penalty_path_plan_20261101_v1.md) · [Original conditional findings](arithmetic_conditional_findings_20261101_v1.md) · [Continuation decisions](arithmetic_continuation_decisions_20261101_v1.md).
