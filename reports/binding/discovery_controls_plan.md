# Capacity and oracle-access controls for discovery prediction

Specified on 2026-10-26 before fitting this sensitivity. All inputs and failure labels come from the previously consumed discovery cohort. This is an exploratory, prospectively fixed analysis of existing data, not untouched final validation.

## Why this follows the first baseline

The [first discovery baseline](discovery_prediction_decision.md) used an additive input model. It found little Brier improvement from raw neutral responses and a larger gain when the reference response was scored against its oracle. Two uncertainties remain: the source-only baseline may miss known factorial interactions, and the scored tier mixes oracle access with an engineered nonlinear comparison.

For a valid neutral response, `neutral_failure` is exactly whether the neutral prediction differs from the program oracle answer; invalid responses also count as failures. Once the neutral prediction, validity and oracle answer are supplied, this indicator contains no additional observation. A gain from supplying it explicitly then reflects representation/model capacity, not a new measurement or a mechanism.

## Cohort, grouping and immutability

Reuse the exact pinned feature tables from `discovery_prediction/*_v1`, with 6,144 transformed targets and 3,072 distinct neutral references per checkpoint. Target IDs, labels, reference IDs, source configurations and original response hashes remain unchanged. There are 24 structural components. Preserve the original six outer folds, five inner folds, seeds 17/29/43, L2 grid `[0.1,1,10,100]`, inner Brier selection, training-only normalization, single-class prior fallback and conditional template bootstrap (2,000 draws, seed 117).

New feature collection reads the validated generated source programs and existing feature payloads. It does not request new model outputs or read original reserved outcomes. Verify the reconstructed oracle relation exactly against every existing neutral-failure feature. No case, component or seed may be dropped after seeing a score.

## Fixed feature transforms

Retain the 19 original source-only features. Define five design bits: `u=(updates-1)/2`, `c=(available_bindings-2)/2`, `m=misleading`, `q=query_saved`, and `t=tail_after`. Append all ten pairwise products, all ten three-way products of those five bits, and query-definition distance multiplied by each bit. These 25 pointwise terms give 44 source features. They cover the original naming/load/update/query/timing questions without choosing terms using new fit results. The transform has no fitted vocabulary, centering, feature selection or outcome access.

For explicitly oracle-assisted tiers, independently execute the validated program and append its integer answer value, absolute value and negative-sign indicator. These are source-program oracle features, not the target language model's answer or eventual correctness. The original oracle-free source tier continues to exclude them.

## Eight fixed predictor tiers

| Predictor | Features | Prediction-time observation contract |
|---|---|---|
| `prior` | Smoothed outer-training failure rate. | No query or oracle. |
| `A_input` | Original 19 additive source features. | No query or oracle; reproduction anchor. |
| `A_interactions` | 44 source features including the fixed interactions. | No query or oracle. |
| `A_interactions_neutral_raw` | Interaction inputs plus five raw neutral-response features. | At most one neutral query; no reference correctness. |
| `A_interactions_neutral_scored` | The preceding features plus neutral failure. | One neutral query and reference-oracle scoring. |
| `A_interactions_oracle` | Interaction inputs plus three source-oracle descriptors. | Source oracle, no language-model query. |
| `A_interactions_oracle_neutral_raw` | Interaction/oracle inputs plus raw neutral properties. | Source oracle plus one neutral query. |
| `A_interactions_oracle_neutral_scored` | The preceding features plus the deterministic neutral-failure indicator. | Exactly the same observations as the preceding tier. |

The raw-reference columns and original failure indicator are reused unchanged. Each final payload has 53 features across all access tiers, with explicit per-tier column lists. Target model outputs, validity and correctness remain excluded from feature construction. The scored reference and oracle input share the target semantic answer, so these tiers must never be described as oracle-free predictors.

## Scoring and decisions

Reuse the same grouped nested logistic procedure. Report Brier loss, log loss and fixed-bin calibration for every tier, each of the three partition seeds and the mean-probability OOF ensemble. Preserve all condition/query/load/original-split cells, inner selection curves, normalizers, weights and OOF records.

Report all seven prior-to-tier comparisons plus nine fixed comparisons: additive to interaction input; interaction input to raw neutral, scored neutral and oracle input; oracle input to oracle-plus-raw; oracle-plus-raw to its explicit-scored encoding; raw neutral to scored neutral; raw neutral to oracle-plus-raw; and scored neutral to oracle-plus-scored. Positive loss differences favor the right tier. All 16 comparisons remain visible with conditional, unadjusted template-bootstrap intervals; they do not refit the fitting pipeline.

Check that the reproduced prior and original additive input predictions, fold assignments and selected penalties match the original analysis, allowing only declared floating-point tolerance. Original results remain immutable. An improved interaction baseline would show that additive model capacity limited the first comparison. An oracle-only gain would identify an access difference. An explicit-score gain after supplying oracle and raw reference properties would identify useful deterministic encoding under the same information, not an additional observation. Null and adverse increments are valid outcomes.

This sensitivity does not exhaust flexible source-only prediction. It does not collect confidence, fit a mechanism C model, establish causal binding, train a language-model checkpoint or open final/extrapolation outcomes. The original vocabulary boundary remains crossed within consumed-data CV, and conditional intervals omit refitting/selection uncertainty. Frozen unfamiliar-program validation remains unfinished.

## Execution

Use the existing entry point `scripts/120_binding_discovery_prediction.py`: `collect_controls`, `run`, and `compare`, with `feature_profile=capacity_oracle_v1`. Collection and fitting receive separate frozen source/configuration pointers under `artifacts/binding/discovery_controls/`; lifecycle/result writers and SLURM wrappers update the [automatic log](experiment_log.md). All new fitting runs on CPUs using cached model behavior.
