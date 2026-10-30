# Discovery failure-prediction baselines

Analysis specified on 2026-10-26 before fitting these statistical models. All outcomes come from previously observed arithmetic-free discovery runs. This is an exploratory analysis of consumed data, not a prospective registration on unseen model outcomes or completion of frozen final validation.

## Question and cohort

How well do program input features predict failures on informative/misleading names, and how much does a distinct neutral-name query add? This establishes empirical predictive baselines for the original A/B/C agenda while an evidence-supported mechanism C remains unavailable. It follows the [arithmetic/readout decision](arithmetic_readout_decision.md) without selecting a favorable arithmetic cell or opening reserved outcomes.

Use the completed `competition/discovery_v2.jsonl` runs for the pinned Llama 3.1 8B Instruct and CodeLlama 34B Instruct checkpoints. Restrict targets to the `versions` family's informative/misleading rows: 6,144 target examples per checkpoint, covering 192 numeric bases and 24 structural components. Original training and development examples were both consumed discovery data; retain their original split labels for reporting, not as predictors. Ownership rows have no nonneutral counterpart and are excluded by design.

Each target has exactly one neutral counterpart with the same base, update count, tail placement, query role, ownership status and lexical realization. Require distinct source/prompt IDs, matching semantics, and the same checkpoint, backend and protocol. The 3,072 distinct references per checkpoint are reused across informative/misleading targets. The maximum additional access is one neutral query per prediction, with 0.5 unique cached reference queries per target over the complete cohort. These are already collected queries; the analysis makes no additional model call.

## Information contract

All target features are fixed before target correctness is supplied to the statistical fitter. Input features use source AST topology, input-token/character counts, assignment/copy/literal counts, literal-magnitude summaries, query-definition distance/count/dependency depth, and declared load/update/naming/query/lexical factors. They do not use oracle execution traces, target answer magnitude, target greedy output, target validity or target correctness. Template/base identifiers and the original split are grouping/reporting metadata, not model features.

Compare four predeclared levels:

| Predictor | Permitted information | Extra query/oracle access |
|---|---|---|
| Training prior | Smoothed failure rate in the fitting subset. | None. |
| `A_input` | Fixed input features only. | None. |
| `A_neutral_raw` | Input features plus neutral validity, output-token count, response-character count and parsed neutral prediction value/magnitude. | At most one distinct neutral query; no oracle scoring of that response. |
| `A_neutral_scored` | The preceding features plus the neutral response's failure indicator. | The same neutral query **and reference-program oracle correctness**. |

The last comparator has stronger oracle access and is reported separately. Its reference shares the target's semantic answer, but its response is a distinct query. No predictor observes the target model's own answer, validity, correctness or target–reference agreement. No confidence scores, hidden activations, probe outputs or mechanism C measurements are introduced. This baseline analysis does not use the legacy fitter's four-model interface to manufacture a C feature.

## Fitting and evaluation

Fit checkpoints separately. Keep each structural component, every numeric/lexical/naming/query relative and its reference in the same outer and inner group. Recompute the canonical-skeleton grouping to verify the declared components before fitting.

Use three fixed group-partition seeds: 17, 29 and 43. Each partition has six outer folds, balanced by available-binding level: four structural components per outer validation fold, two from each level. Split the remaining 20 training components into five balanced inner folds. Fold assignment uses component identities and load strata, never outcome labels.

Reuse the existing regularized logistic fitter with train-only standardization and an unpenalized intercept. Select L2 from `[0.1, 1, 10, 100]` by the pooled inner out-of-fold Brier score; ties use the first declared value. Refit the selected model on the outer training subset only. A single-class fitting subset uses the predeclared Jeffreys-smoothed training prior `(failures+0.5)/(n+1)` and records the fallback. Nonconvergence is a visible failure. No fold, target or component is dropped after inspecting results.

Retain every fold's fitting identities, inner selection curve, weights, normalizers and out-of-fold probabilities. Report every partition seed and a predeclared mean-probability ensemble across the three partitions; partition seeds are sensitivity analyses, not independent scientific replications. Score Brier loss, log loss and fixed-bin calibration. Retain complete naming/query/load/original-split cells and invalid-target counts. Report paired improvements relative to the training prior, input-only baseline and raw-reference baseline as applicable.

Intervals resample the 24 structural components together for all predictors (2,000 bootstrap draws, seed 117). They condition on the fitted out-of-fold probabilities and do not refit the training pipeline in each draw. They therefore omit some model-selection/training uncertainty; the same consumed discovery cohort and shared source forms do not establish confirmatory unfamiliar-program prediction. Retain null and adverse increments. No positive-effect criterion determines software completion.

## Validation, provenance and next decision

Reject reserved roles/paths, incompatible dataset/checkpoint/configuration hashes, incomplete runs and incompatible feature manifests before reading outcome payloads. Validate the original source and structural relationships before invoking an audit that opens responses. Re-score all selected cached outputs under their original parsing contract. Changing only outer validation labels must leave probabilities, chosen penalties and training normalizers unchanged; changing a target response must not alter its feature vector.

Feature collection and statistical fitting have separate immutable configuration/source pointers. Input feature tables and manifests, fold artifacts, probabilities, summaries, reports and source identities will live under `artifacts/binding/discovery_prediction/`. The ordinary metadata writers and SLURM wrappers maintain the [automatic experiment log](experiment_log.md). All statistical work is CPU-based; original model runs and reserved final/extrapolation outcomes remain unchanged.

This completes an exploratory baseline comparison only. Supported mechanism selection, confidence collection, C-model features, prospectively frozen forecasts and final scoring remain separate unfinished tasks.
