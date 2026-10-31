# Next runs after the audited numeric sweep

October 31, 2026. Status: planned, not submitted. This is the next implementation plan, not an executable scheduler configuration or a registration made before the existing DEV results. The [results snapshot](arithmetic_results_for_next_runs_v1.md) is generated from hash-pinned audited files; the [completed review and figure](arithmetic_numeric_postrun_review_v1.md) retain the full measurement context.

## What the results change

Compression is a measurement limitation in the tested role-specific assay: wider features improve computed-value error and categorical accuracy. Full-width literal decoding works extremely well, while exact computed values remain weak. Sign and magnitude are more accessible than precise digits. Current data do not decide whether arithmetic is unfinished at the sampled token, values are encoded differently later, bindings are lost, or computation fails. Failed decoding is specific to a tested readout; successful decoding does not establish natural causal use.

The next priority is a shared-checkpoint test of all four current variables and direct relations, followed by temporal and matched-mechanism experiments. Another broad search over decoder architectures is deferred until those questions are measured.

## Run 1: full-width global state and direct relationships, CPU only

**Question:** Can one answer-preparation state support all current variables and their relationships, even when local computed-definition readouts are weak?

- Reuse the existing 5,292-row local cohort and immutable raw captures. Stream each model's chunks once and cache all four archived layers' actual answer-point vectors. The answer point is `point_count - 1`, never the fixed padded index22. No model/tokenizer call is needed for extraction.
- Primary layers remain24 for Llama8B and36 for CodeLlama34B. Other archived layers are cached for separately declared sensitivities; no DEV-selected best layer is reported.
- Primary input is one final hidden vector, with an intercept. No candidate history, true binding pointer, gold value, dependency edge or additional depth/slot feature enters the representation. Four output slots are a canonical measurement convention, not a claim about neural registers.
- New hidden widths:1024 and full4096/8192. Use model-independent whole-source character features at widths1024/4096/8192 as shared controls, fitting each matching source width once. Reuse the existing fixed-alpha64-wide global scalar/relation banks as an explicitly historical reference; do not refit those completed banks. The new within-protocol width comparison is1024 versus full. Source formatting and tuning differ from the historical reference, so that reference cannot isolate a pure rank effect.
- Independently fit four scalar outputs, four193-class integer heads, and48 direct relation outputs: six equalities, six orderings, twelve sums and twenty-four ordered differences. There are824 real-target columns. Joint factorization is a computational convenience; heads remain independent. Add coherent-family-shuffled targets at selected refit only.
- Compare direct relation predictions with relations derived externally from the four decoded values. Oracle current-state values provide labels only. Report per-variable exact/MAE, all-four-values accuracy, and relation-type macro balanced accuracy. Separate queried/unqueried slots, computed/untouched values and relations involving computed values. These evaluation strata use gold annotations only for reporting.
- Use three structural TRAIN folds, weighting seeds11/29/47 and alphas1/100/10000. Fit normalization only on fitting rows. Select one alpha per output group: scalar group by TRAIN family-macro MAE, categorical group by TRAIN family-macro per-slot exact, direct-relation group by TRAIN relation-type macro balanced accuracy. Ties choose stronger regularization. For relation decisions, use the fitting subset's weighted prevalence as the threshold; a constant fitting prior then has balanced accuracy50% on supported cells. Do not describe ridge outputs as calibrated probabilities without separate TRAIN-only calibration.
- Determine relation eligibility from each fold's fitting data, and from all TRAIN for final evaluation: at least12 positive and12 negative unique numeric bodies; preserve lexical deduplication, class/family support and undefined evaluation cells. Shuffled controls are evaluated against their own coherent shuffled truth.
- Four hidden cells and three shared-source cells require189 CV factorizations and at most63 selected factorizations. These are finite workload counts, not a compute allowance. Save/replay coefficients and all planned panels. Existing DEV remains discovery.

This run tests the original all-variable objective more directly than a decoder that receives the correct current-definition node. A positive direct-relation result with poor absolute values would motivate a relational representation assay; source controls and later causal tests are still needed.

The archived prompts request one printed value. Interpret a negative all-variable readout in that task context: it would not rule out a different representation when all values are requested. The new query-scope control below addresses that possibility.

## Runs 2–3: paired dataset preparation, then temporal captures

**Questions:** When does a computed value become accessible, and which operation causes errors?

Prepare matched families covering literal/copy controls, arithmetic with minimal overwrite, copies/overwrites without arithmetic, and the combined task. Vary delay over0/4/12 intervening statements. Compare irrelevant-variable writes with mutations of an earlier operand after a result has been assigned. Keep the requested value unchanged under the delay/mutation manipulation when intended; verify that with two independent interpreters.

An illustrative diagnostic is:

```python
a = 2
b = 5
x = a + b
a = 9
print(x)  # 7; recomputing with the updated a would give 14
```

The explanatory comment in this illustration is documentation only; it must not appear in model prompts. Keep oracle traces, expected answers, versions, split IDs and evaluator annotations separate from model input. The matched control writes the9 to an unrelated variable. Answer14 is consistent with recomputation from the updated operand; it is not proof of that internal mechanism. Enumerate all compatible error labels and mark collisions/ambiguities. Add semantic-preserving renamings/root-order changes and same-value-multiset/different-binding twins with fixed query text. Group every relative together.

**Structural grouping is a pre-inference gate.** Target96 TRAIN and32 DEV components for the nontrivial bank, plus separate calibration components. These counts are unvalidated design targets, not a generated dataset. Compute canonical keys over all relatives and take connected components when variants share a canonical skeleton. Literalization or copy controls may collapse many nominal templates into one component; never count them as independent families. The finite one-hop/literal skeletons may need to remain calibration-only. Record actual feasible counts and revise the plan before model calls if the closure is too small. Numeric seeds, lexical variants and filler lengths do not manufacture independent structural families. Prevent overlap with the old structural cohorts where new-family claims are intended.

Use distinct numeric-generation seeds20261101/20261102/20261103 and fitting seeds11/29/47. Numeric/lexical relatives remain in the same structural split. Balance target values and relevant difficulty within feasible matched strata, report retained frequencies, and separate computed values present/absent as literals. Literal and arithmetic programs differ in value visibility by construction; matching output magnitude does not make their input information equivalent. Categorical heads are closed-set measurements: unseen TRAIN value classes need explicit support labels; scalar heads are the appropriate primary range-transfer assay.

After AST/oracle/counterfactual/split checks, run native tokenizer preflight in CPU allocations. Sample at RHS end, assignment newline/delimiter, a later use and the answer boundary. A newline may share its native token with the RHS; record collapsed sites, and use distinct positions for temporal contrasts. Do not silently claim an extra computation step for an identical token. Preserve per-model site coverage and matched-case denominators. Check every capture prefix for future-source exposure and target-value leakage.

Then use the cached, revision-pinned8B/34B checkpoints for GPU inference. Retain all four archived layers, raw full-width states and a1024-wide sensitivity. Primary analyses are within-site scalar/categorical readouts with TRAIN-only tuning; cross-site decoder transfer separately tests stability. Low transfer with good within-site decoding indicates an encoding change rather than absence of information.

## Run 4: query and behavior protocols

Use output-only, explicit intermediate-query and model-generated stepwise protocols as separate conditions. Keep three instruction variants and every invalid/truncated response. Use the original deterministic generation/parser where compatible; freeze any new trace parser before inference, selecting the last `Answer:` as required by the repository rules.

Within the explicit-query condition, compare one requested variable with all four current variables. Validate a separate ordered four-value parser, retain per-slot and joint accuracy, and mark values already emitted in the generated answer when studying later states. The all-variable task changes the requested computation; task-dependent decodability is informative without establishing a task-independent register representation.

For an explicit query appended after a code prefix, verify that supposedly matched earlier token prefixes really are identical. Stepwise instructions change the prompt and computation; interpret that as a protocol intervention. Never teacher-force a correct intermediate into the main measurement. A gold-intermediate condition is a separately labeled copying control. Mark when the target appeared in the source or generated trace, and separate value-visible cases from latent readout claims. Capture pre-answer states before the final answer token.

Calibration first checks oracle/parser/native sites, copying controls, model arithmetic competence and memory/batching. Keep calibration templates outside probe fits. Reuse byte-identical historical generations when applicable; only new prompts/sites require new inference. Do not choose a wording because its DEV accuracy is best. If protocol changes are needed, preserve the pilot and freeze a new edition before collecting the formal bank.

## Run 5 and confirmation

On matched cases/instructions, relate output errors to binding pointers, coarse numeric properties and exact-value errors. Train error predictors using grouped TRAIN cross-fitting. Compare input-difficulty features, output uncertainty and added probe features using held-out log loss/Brier score, calibration and family-cluster intervals. Keep invalid outputs in denominators. Correct probe/wrong answer cases are informative only with the same prompt/site protocol and without answer-token leakage.

After discovery, freeze a primary measurement and a few scientific contrasts before generating/opening independent confirmation families. Choose the confirmation sample size from a useful effect and structural-family variance, not repeated deterministic fitting seeds. Existing sealed final outcomes remain untouched. Natural-donor interventions remain gated on robust readouts, behavioral positive controls, functional counterfactuals and exact native layout matching; no causal patching or backbone training is scheduled by this plan.

## Execution order and storage

Run1 CPU implementation and Runs2–3 dataset preparation can proceed in parallel. Data/oracle/group/storage tests precede tokenizer preflight; calibration and a frozen protocol precede the larger GPU capture/behavior jobs. The actual scheduler determines concurrency. Preserve other authorized jobs and the editor allocation. Use measured hardware-compatible batches and the scheduler's finite walltimes/backfill options, with no cumulative project compute allowance.

All large caches, scores and parameters must be created on scratch from the outset, with original paths linked and hash-pinned where needed. Check write+fsync, expected space and path ownership before submission. Keep metadata/status/logging small on work, and retain lossless public metadata export. Every stage records its immutable source/config/data hashes, attempted/returned counts, parameters, failures and receipts through the existing automatic logger. Supervisors retry reviewed scheduler interruptions only; scientific failures stop for inspection.

The [machine-readable plan](../../configs/binding/arithmetic_next_runs_20261031_v1.json) records dependencies, model revisions, input hashes and unvalidated dataset targets. It is intentionally marked non-launchable until implementation and preflight are complete.

## Related methodological context

[Hewitt and Liang](https://aclanthology.org/D19-1275/) motivate distinguishing probe capacity from representation signal with controls. Our coherent-family controls are an adaptation, not a replication of their word-type control task. [Linear numeric decoding](https://arxiv.org/abs/2401.03735) and [digit-position arithmetic circuits](https://aclanthology.org/2025.findings-ijcnlp.86/) provide related hypotheses from different settings; they do not establish what these multi-assignment programs encode.
