# Conditional readouts: postrun numerical audit

All eight cells passed a no-refit audit. Training input hashes/IDs/weights and family/donor partitions match. Independent TRAIN normalization and ridge normal-equation/intercept checks pass. Explicit saved-parameter multiplication reproduces CV/selected predictions, including fixed-block ablations. Independent family-first metrics and TRAIN-only alpha selection match.

- CV banks: **216**; selected banks: **24**.
- Prediction coordinates replayed: **2,135,808**.
- Maximum absolute prediction difference: **0**.
- Maximum relative ridge normal-equation residual: **1.16e-11** (limit1e-7).
- Maximum weighted-intercept residual: **2.07e-14** (limit1e-7).

Prediction replay allows rtol/atol1e-10 across CPU kernels; metric checks allow1e-12 and normalization checks1e-10. This numerical audit does not turn adaptive DEV findings into confirmation or establish causal use. No new model calls, parameter fits, layer/wording selection or sealed-final access.
