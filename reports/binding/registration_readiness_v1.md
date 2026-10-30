# Forecast registration metadata readiness

State: draft; metadata eligibility ready: False.

Metadata readiness does not verify scientific support, forecast contents, first-access ordering or primary-ID coverage. It does not authorize or execute final collection, scoring, pooling or model inference.

Missing scientific choices: hypothesis, competing_explanations, primary_intervention_endpoint, intervention_controls, model_revision, layers_and_sites, frozen_fitting_procedure, structural_predictions, ambiguity_and_exclusion_rules, multiplicity_and_uncertainty, feature_information_contract, additional_query_budgets, code_source_sha256, dataset_sha256, registered_utc

| Check | Passed | Detail |
|---|---|---|
| required_fields | False | missing or placeholder fields: hypothesis, competing_explanations, primary_intervention_endpoint, intervention_controls, model_revision, layers_and_sites, frozen_fitting_procedure, structural_predictions, ambiguity_and_exclusion_rules, multiplicity_and_uncertainty, feature_information_contract, additional_query_budgets, code_source_sha256, dataset_sha256, registered_utc |
| required_field_types | True | scientific choices must be explicit text or structured metadata:  |
| frozen_status | False | status must explicitly be frozen; draft never passes |
| supported_account | False | supported_account must explicitly be true; this utility does not establish a mechanism |
| run_config | False | run_config metadata is required to check evaluator bindings |
| model_revision_pinned | False | model_revision must be an immutable 40- or 64-character hexadecimal revision |
| code_source_sha256 | False | registration code digest must match current analysis source identity |
| dataset_manifest_metadata | False | dataset manifest metadata must declare a SHA-256 and evaluation_role; dataset body is not read |
| dataset_sha256 | False | registration dataset digest must match declared dataset manifest metadata |
| behavioral_endpoint | True | existing heldout evaluator implements incorrect_including_invalid |
| registered_utc | False | registered_utc must be an explicit UTC timestamp |
| fit_manifest_digest | False | forecasting requires a pinned fit_manifest_sha256; fitted model contents are not read |
| feature_information_contract | False | 'NoneType' object is not iterable |
| query_budget_declarations | False | declare nonnegative per-target additional-query budgets for all four predictors |

Dry-run ordering: registration → frozen measurements/forecasts → new heldout responses → scoring.
No prerequisite node was executed. No model, dataset body, forecast content or outcome was read.
