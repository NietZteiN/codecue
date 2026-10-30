# Morning review of the arithmetic relationship suite

Adaptive postrun diagnostics. Numeric match categories are coincidences, not causal error labels. Training scores measure interpolation. No selected layer, decoder refit, causal patch or untouched evaluation.

| Model | Site | Features | TRAIN parent | DEV parent | TRAIN whole graph | DEV whole graph | DEV parent prior |
|---|---|---|---:|---:|---:|---:|---:|
| codellama34b | 1 | hidden | 100.00% | 29.08% | 100.00% | 0.00% | 25.69% |
| codellama34b | 1 | source | 100.00% | 21.05% | 100.00% | 0.00% | 25.69% |
| codellama34b | 2 | hidden | 100.00% | 29.39% | 100.00% | 0.00% | 25.69% |
| codellama34b | 2 | source | 100.00% | 22.29% | 100.00% | 0.00% | 25.69% |
| llama8b | 1 | hidden | 100.00% | 29.76% | 100.00% | 0.00% | 25.69% |
| llama8b | 1 | source | 100.00% | 19.99% | 100.00% | 0.00% | 25.69% |
| llama8b | 2 | hidden | 100.00% | 24.34% | 99.99% | 0.00% | 25.69% |
| llama8b | 2 | source | 100.00% | 22.16% | 100.00% | 0.00% | 25.69% |

codellama34b DEV numeric match signatures: `{"arithmetic_written": {"correct": 22, "neither": 112, "other_current_only": 35, "stale_and_other_current": 12, "stale_only": 35}, "untouched_literal": {"correct": 36, "neither": 27, "other_current_only": 9}}`


llama8b DEV numeric match signatures: `{"arithmetic_written": {"correct": 22, "invalid": 5, "neither": 133, "other_current_only": 18, "stale_and_other_current": 3, "stale_only": 35}, "untouched_literal": {"correct": 32, "invalid": 3, "neither": 33, "other_current_only": 4}}`


TRAIN/DEV comparisons use the same frozen parameters. Every reconstructed training input is hash-checked against its saved fit. DEV numerical replay permits only1e-10 floating-point tolerance; categorical and binary decisions must match exactly. All sites/backends remain in the JSON, including priors, coherent shuffles, value-class coverage and queried/unqueried accuracy.

