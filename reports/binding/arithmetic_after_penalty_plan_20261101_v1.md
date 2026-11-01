# After the penalty check: questions that can change the explanation

Planning document; the saved-score diagnostic below is now completed. New model-fitting and generation experiments are not submitted. The completed penalty-path findings and numerical audit must be read alongside this plan. The original conditional study, its postrun diagnostic and the frozen continuation protocol remain separate records.

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

These choices implement the existing [23-paper review](probing_literature_review_20261031_v1.md), particularly its conditional controls, shared structured queries, and complexity/learning-effort sections. This is a project-specific design inference, not a claim that a particular architecture is guaranteed to work.

[Penalty-path findings](arithmetic_penalty_path_findings_20261101_v1.md) · [Frozen protocol](arithmetic_penalty_path_plan_20261101_v1.md) · [Original conditional findings](arithmetic_conditional_findings_20261101_v1.md) · [Continuation decisions](arithmetic_continuation_decisions_20261101_v1.md).
