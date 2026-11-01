# Next readout wave: regularization and loss-appropriate priors

Planning only; not submitted. The completed conditional study found modest computed-value MAE gains from case-matched hidden features, while all eight cells selected alpha 10,000, the upper end of the declared grid. Postrun TRAIN-only diagnostics show that joint MAE beats constant mean/median/zero baselines, but exact rounded accuracy is BELOW the zero baseline. These are different endpoints; a lower numeric error does not establish exact value recovery.

## First experiment: continue the penalty path without repeating old fits

Freeze a new source/configuration edition before running. Keep the same archived cases, source/hidden feature blocks, layers, weights, structural folds, fitting seeds and computed-value selection objective. Add only alpha 100,000 / 1,000,000 / 10,000,000. Reuse the old 216 CV banks by immutable references rather than refitting their 1/100/10,000 grid. Require exact old recipe/cache/ID/input/weight matches, with original source and configuration identities preserved in every reuse wrapper.

The eight cells and nine fold/seed combinations imply **216 new CV fits**. Reuse an old selected refit when the extended TRAIN selection keeps its old alpha. Otherwise fit only the newly selected full-TRAIN model, at most 24 additional ridge fits. Report new and reused fits separately; do not silently count reused banks as new training.

Include the analytic ridge alpha→infinity limit (TRAIN weighted-mean intercept with zero feature coefficients) as a reference point. Compute the fixed zero, all-slot median and computed-family median on EACH TRAIN fitting fold before validation. These require only prior-statistic estimation, not additional ridge factorizations. Report all priors and choose any predictor class or penalty using TRAIN folds only, never DEV. Preserve the original conditional study and its postrun diagnostic; the new selection remains adaptive discovery on an inspected DEV cohort.

Require the selected penalty to lie inside the finite grid, or explicitly report a remaining boundary/constant preference rather than calling the learned model optimized. Reapply saved parameters, verify TRAIN-only normalization/input hashes/donors and check ridge normal equations as in the completed audit. Keep nominal-width source and independently optimized shuffled-hidden controls.

## Endpoint-specific follow-ups

For numerical proximity, compare the selected ridge path against loss-appropriate constant priors before adding robust Huber/LAD alternatives. A robust-loss branch would need its own prospectively frozen fitting/convergence/selection rules and matched controls.

For exact value recovery, evaluate discrete/categorical or ordinal readouts against TRAIN-estimated class priors and the zero-mode baseline. The scalar MAE result does not license an exact-state claim. Any class-prior mixing or probability calibration must use held-out TRAIN folds, with complete class-support reporting; existing linear relation scores are not calibrated probabilities.

Do not open a broad architecture/layer/width grid until the penalty boundary and endpoint baselines are settled. Shared-slot or source/hidden interaction models remain a separate hypothesis, since adding source to hidden-only improved MAE by just 0.020 / 0.028 with descriptive intervals crossing zero.

## Parallel data work

The completed longer-generation calibration motivates a fresh prospective protocol calibration, not a retroactive pass of the old output-only gate. Keep both intermediate-query and stepwise candidates, all wordings, explicit generation ceilings and an answer grammar fixed before collection. Then audit prefix/full-prompt numerical equivalence and implement generated-trace boundary/value-visibility flags before formal paired temporal capture. The retained-target overwrite patterns from 36 calibration pairs need formal-family replication. No causal-use or complete-state claim is ready.

[Conditional findings](arithmetic_conditional_findings_20261101_v1.md) · [Prior/boundary diagnostics](arithmetic_conditional_prior_diagnostics_20261101_v1.md) · [Numerical audit](arithmetic_conditional_postrun_review_20261101_v1.md) · [Continuation decisions](arithmetic_continuation_decisions_20261101_v1.md).
