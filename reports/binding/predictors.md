# Frozen failure-prediction interface

An [empirical discovery-baseline analysis](discovery_prediction_decision.md) now complements this frozen-forecast interface. It fits source-only and distinct-neutral-query baselines with nested structural-group cross-validation on previously observed arithmetic-free data. Raw and oracle-scored reference features have separate access contracts. No empirical mechanism C or untouched final forecast is produced; the interface below still governs genuine final registration and scoring.

The follow-up [capacity/access controls](discovery_controls_decision.md) add fixed source interactions and separately declared source-oracle descriptors. Once neutral prediction, validity and oracle answer are available, the neutral-failure flag is deterministic; a gain from providing it explicitly is an encoding/model-capacity effect, not a new measurement. All eight tiers, unchanged grouping and exact baseline-reproduction checks are retained. The original four-predictor interface remains unchanged by default; `scripts/120_binding_discovery_prediction.py` uses the separate, explicitly named sensitivity profile.

`fit-forecasters` fits small regularized logistic models on complete discovery behavior. This is statistical prediction, separate from optional language-model training. An empirical C model is not fitted until discovery supports choosing its measurement features and query budget.

The configuration contains the ordinary pinned `dataset`, `model_revision`, and `run_dir`, plus a `forecasting` object:

- `discovery_responses`: a completed behavior stage's `responses.jsonl`, with its adjacent manifest.
- `feature_table`: JSONL rows shaped `{"id": "…", "features": {"feature_name": 0.0}}`. Cover every observed primary discovery ID exactly once; arithmetic controls are excluded from the fitting target.
- `features`: four explicit lists under `A_input`, `B_behavior`, `C_measurements`, and `cheap_stress_test`. A must be a strict subset of B, and B of C.
- `l2_grid`: a predeclared positive regularization grid. Development Brier score selects the penalty, with declared ordering breaking ties. Normalization and coefficients use training only; development is never refitted.

The feature collector must honor the declared information contract. A uses input length, assignment distance, arithmetic work, depth and competition; B adds available confidence or clean-program measurements; C adds the frozen mechanism measurements. The cheap stress baseline has its own declared features and additional-query budget. The fitter forbids direct outcome columns, but a column name cannot prove how a feature was collected. Collection provenance and outcome timing must be reviewed before registration. No target correctness, target greedy answer, or feature selected using final labels may enter the forecasts.

Before opening response outcomes, fitting now checks declared dataset/configuration/response roles and splits, reserved response paths, completed behavior provenance, source checksums and checkpoint identity. Mixed legacy source datasets remain valid because program records are not model outcomes. An untyped legacy response manifest cannot attest every response ID in advance, so the fitter also checks every parsed response ID/split before collecting features. The access, fitting and measurement regression checks passed 44 tests; evidence is in `artifacts/binding/arithmetic_readout/forecasting_access_review_v1.json`. This software change fits no empirical predictor and opens no reserved outcomes.

```bash
python -m codecue.binding fit-forecasters --config CONFIG
```

The output `forecasters/fit.json` retains every development curve, selected model weights, training normalizers, feature lists, data/response/feature hashes, behavior identity, source identity and cluster intervals. Discovery behavior must match the dataset and checkpoint; test outcomes, parent-template leakage, missing IDs, single-class training labels and nonconvergent fits are refused. The development scores remain selection scores and are optimistic.

Before generating final forecasts, the genuine scientific registration must include all fields required by `heldout.py`. It additionally binds `frozen_fitting_procedure.fit_manifest_sha256` to the JSON-content hash returned by fitting and sets `feature_information_contract.features` to exactly the fitted lists. Its query budgets must cover confidence, clean behavior, representation, intervention and cheap-stress collection as applicable. Registration also pins the current source, target dataset and checkpoint. Add `forecasting.fitted_model`, `forecasting.target_feature_table`, and `frozen_predictions` to the target config.

```bash
python -m codecue.binding write-forecasts --config TARGET_CONFIG
```

The target feature table must cover every primary test ID exactly once, without labels. This command reads no target model responses and refuses to overwrite an existing forecast file. Pin its returned byte hash as `frozen_predictions_sha256` before invoking heldout behavior. Then use `evaluate-heldout` to score the frozen probabilities against observed outputs, with Brier score, log loss, calibration and clustered incremental comparisons.

Software tests exercise training, normalization, nesting, refusal of test labels, immutable fits and forecast hashes with temporary synthetic data. They are excluded from empirical model results. There is no populated scientific registration or empirical C forecast artifact yet.
