# Why the component heads are score marginals

This mathematical clarification was written before the direct-identity study was fitted. It changes no endpoint, data, split, feature, layer, alpha, control label or fitting rule in the [study plan](direct_identity_plan_v1.md). It qualifies interpretation of joint versus component predictions.

For one event, let Y_J contain the sixteen joint owner/version one-hot labels. Let M_O sum joint classes sharing each owner, and M_V sum classes sharing each version. The coherent targets satisfy Y_O = Y_J M_O and Y_V = Y_J M_V, for both real labels and the locally coherent sham task.

The [existing weighted ridge](../../src/codecue/binding/weighted_ridge.py) standardizes TRAIN features, performs weighted centering and fits every output through the same regularized Gram system. It does not standardize each target separately. With identical features, masks, positive weights, alpha and intercept handling, its prediction operator is linear in the target matrix. Therefore the fitted score matrices satisfy:

- S_O = S_J M_O
- S_V = S_J M_V

These equalities hold mathematically; floating point roundoff can create small residuals. The new diagnostics record those residuals wherever all involved scores are finite. They do not impose a new scientific threshold or select a favorable subset. The result applies separately within every feature/site/weight-seed bank; no claim is made about models with different losses or normalization.

Joint prediction selects the largest individual joint score. Factorized prediction selects the owner with the largest owner-score marginal and the version with the largest version-score marginal. Those argmax decisions can differ even when their scores obey the exact linear identities. A difference in exact accuracy compares decision rules on a joint score table and its marginals. It is not independent evidence for separate internal representations or a binding-association mechanism. Ridge scores are uncalibrated and can be negative, so “score marginal” does not mean a calibrated posterior probability.

The joint head has sixteen output coefficient columns; the two component heads have eight combined. That nominal parameter count remains worth reporting. Under this coherent-label/shared-linear-estimator recipe, however, the fitted component columns are projections of the joint columns; they are not an independent learned representation. Successful direct joint identity decoding still differs from the previous per-program source-map conversion: its predicted identity comes from the fixed global codebook alone.

The source-owner/weighted-TRAIN-version-prior comparator has one parsed owner and a conditional version distribution. Its joint and factorized argmax identities must agree by construction, including the fixed tie rule. That is a software sanity check, not a model finding. The first assignment/parent versions remain constants, and the sparse final-parent version-4 support remains unchanged.

All scope limits remain: adaptive discovery, supplied event positions and canonical slots, explicit owner syntax, fifteen dependent DEV graph families, no causal-use qualification and no untouched unfamiliar-program evaluation.
