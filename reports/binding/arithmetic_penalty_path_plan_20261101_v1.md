# Extended conditional penalty path and fold-local priors

November 1, 2026. This executes the [declared next-wave design](arithmetic_conditional_next_wave_20261101_v1.md) after every original conditional cell selected the upper penalty boundary. Existing original results, the numerical audit and the postrun prior diagnostic remain immutable. The study is adaptive discovery on the already inspected cohort, not confirmation.

## Fixed inputs and new fits

Keep all eight original cells, the archived 5,292-case cohort, source/hidden feature definitions, layers 24/36, projection/fitting seeds 11/29/47, structural TRAIN folds, family weights, scalar targets and computed-slot family-macro MAE selection objective. Pin each original worker config and the numerical audit that covered its exact result. No new model calls or layer/wording/feature-width search.

Extend the ridge candidates from 1/100/10,000 to **1/100/10,000/100,000/1,000,000/10,000,000**. Reuse all **216 original CV banks** through immutable references. Validate original ownership/configuration, ordered fitting IDs and exact feature/target/weight/donor fingerprints. Retain original source and configuration under each reuse wrapper; do not relabel original coefficients as newly trained. Fit only the **216 new CV models** at the three added penalties. Selected full-TRAIN ridge models are reused if their original selected penalty remains best; otherwise fit at most 24 new selected models. New fits and reused banks must be reported separately.

## Fold-local constant controls and selection

Prepare shared fixed-zero, weighted-mean, weighted-median and computed-family-median constants inside EACH TRAIN fitting fold. The mean is the analytic alpha→infinity intercept-only ridge limit. For the computed-family median, each fitting observation receives its original seed weight divided by that family's total computed observations; unsupported computed heads explicitly fall back to their all-slot TRAIN median. Values, masks, weights, ID order and support are pinned. All-slot medians use the original fitting weights. Ties choose the lower weighted median. These estimators never see their validation targets.

Nine seed/fold combinations plus three full-TRAIN fits require **36 estimated four-slot prior-statistic vectors** across three nonzero prior methods. Zero is fixed. Full-TRAIN constants are stored without DEV evaluation during preparation. Every worker checks the shared cohort/target identity and fitting-partition fingerprints before using priors.

After all 54 ridge CV banks and nine shared prior CV records are available, lock two TRAIN-only selections: (a) best ridge penalty; (b) best predictor when all four constant classes compete with ridge. Average the nine structural fold/seed computed-MAE losses. Larger ridge penalties win exact ridge ties. Constants win exact ties with ridge, with fixed priority zero, mean, median, computed-median. No DEV selection. A selected constant needs no new ridge fit; still report the independently selected ridge outcome so shrinkage and constant preference remain explicit.

Store whether the ridge optimum is interior, at the lower boundary or at the upper boundary of this finite grid. A remaining boundary is an unresolved range, not optimization success. Preserve exact-integer metrics alongside MAE; a proximity gain does not establish exact value recovery.

## Evaluations, audit and scope

Only after the selection lock evaluate selected ridge, selected overall predictor and all four priors on TRAIN/DEV/calibration. Save coefficients, original/reused references, score arrays and fixed-coefficient TRAIN-mean block ablations. Calibration is excluded from fitting and selection.

A no-refit numerical audit gates reporting: verify all 432 CV banks and 24 selected ridge banks, original fit provenance, exact TRAIN input/target/weight hashes, family/donor boundaries, independent normalization, ridge normal equations/intercept stationarity, saved-parameter prediction replay, family-first metrics, fold-local priors and TRAIN selection. Prediction rtol/atol is 1e-10, normalization tolerance 1e-10, metric tolerance 1e-12 and ridge/intercept stationarity limit 1e-7. Every prior's fit/validation IDs must match its exact TRAIN fold. Scientific errors stop downstream reporting.

Report selected overall joint-minus-comparator computed-MAE contrasts against independently selected source 1024/source 2048, hidden-only, shuffled-hidden and constant priors. Also report the extended-versus-original selected ridge change for each cell. Average fitting seeds within DEV families before 2,000 paired bootstrap replicates. Intervals are descriptive, non-simultaneous and adaptive on inspected DEV; seeds are not independent datasets. Nominal feature count does not match effective rank/inductive bias. Conditional predictive gain is relative to finite feature/readout classes: the complete source determines program outputs. No exact/global-state or natural causal-use claim follows.

## Execution and records

Freeze source/configuration and pass full binding regression before priors/fitting. Use CPU `dev,normal` allocations and scratch-first arrays/banks with work links. Durable ten-minute controllers preserve committed prefixes on scheduler retries and stop at terminal completion. Existing jobs, sealed final outcomes and old artifacts are preserved. There is no cumulative compute allowance. Pin the 23-paper review/register, log automatically, publish source/configuration/compressed immutable text and inventory raw arrays without placing them in Git.
