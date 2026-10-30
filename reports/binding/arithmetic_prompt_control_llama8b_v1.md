# Arithmetic prompt/output semantics control

Adaptive matched discovery on reused program families. Print syntax and wording change token context. Original outcomes and parser remain unchanged; no causal or confirmatory claim.

5,760 exact generated responses; 5,760 prefill attempts.

| Cell | Cases | Accuracy | Invalid |
|---|---:|---:|---:|
| all/bare_i0 | 1152 | 17.882% | 3.385% |
| train/bare_i0 | 864 | 17.593% | 3.588% |
| train/untouched_literal/bare_i0 | 288 | 37.847% | 4.514% |
| train/arithmetic_written/bare_i0 | 576 | 7.465% | 3.125% |
| development/bare_i0 | 288 | 18.750% | 2.778% |
| development/untouched_literal/bare_i0 | 72 | 44.444% | 4.167% |
| development/arithmetic_written/bare_i0 | 216 | 10.185% | 2.315% |
| all/print_i0 | 1152 | 37.934% | 0.868% |
| train/print_i0 | 864 | 39.815% | 0.926% |
| train/untouched_literal/print_i0 | 288 | 92.361% | 0.347% |
| all/bare_i1 | 1152 | 12.500% | 0.260% |
| train/bare_i1 | 864 | 14.120% | 0.347% |
| train/untouched_literal/bare_i1 | 288 | 25.000% | 0.347% |
| all/print_i1 | 1152 | 38.455% | 3.646% |
| train/print_i1 | 864 | 39.583% | 3.588% |
| train/untouched_literal/print_i1 | 288 | 91.319% | 3.819% |
| all/bare_i2 | 1152 | 8.681% | 33.767% |
| train/bare_i2 | 864 | 9.606% | 33.218% |
| train/untouched_literal/bare_i2 | 288 | 21.181% | 34.375% |
| all/print_i2 | 1152 | 9.115% | 74.566% |
| train/print_i2 | 864 | 10.880% | 73.148% |
| train/untouched_literal/print_i2 | 288 | 27.431% | 70.486% |
| train/arithmetic_written/print_i0 | 576 | 13.542% | 1.215% |
| train/arithmetic_written/bare_i1 | 576 | 8.681% | 0.347% |
| train/arithmetic_written/print_i1 | 576 | 13.715% | 3.472% |
| train/arithmetic_written/bare_i2 | 576 | 3.819% | 32.639% |
| train/arithmetic_written/print_i2 | 576 | 2.604% | 74.479% |
| development/print_i0 | 288 | 32.292% | 0.694% |
| development/untouched_literal/print_i0 | 72 | 95.833% | 0.000% |
| development/bare_i1 | 288 | 7.639% | 0.000% |
| development/untouched_literal/bare_i1 | 72 | 13.889% | 0.000% |
| development/print_i1 | 288 | 35.069% | 3.819% |
| development/untouched_literal/print_i1 | 72 | 93.056% | 0.000% |
| development/bare_i2 | 288 | 5.903% | 35.417% |
| development/untouched_literal/bare_i2 | 72 | 16.667% | 29.167% |
| development/print_i2 | 288 | 3.819% | 78.819% |
| development/untouched_literal/print_i2 | 72 | 15.278% | 79.167% |
| development/arithmetic_written/print_i0 | 216 | 11.111% | 0.926% |
| development/arithmetic_written/bare_i1 | 216 | 5.556% | 0.000% |
| development/arithmetic_written/print_i1 | 216 | 15.741% | 5.093% |
| development/arithmetic_written/bare_i2 | 216 | 2.315% | 37.500% |
| development/arithmetic_written/print_i2 | 216 | 0.000% | 78.704% |

Matched DEV prompt contrasts: `{"arithmetic_written:bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.10766782407407406, 0.016203703703703703], "families": 12, "family_macro_difference": -0.03935185185185185, "paired_rows": 216, "row_weighted_difference": -0.046296296296296294}, "arithmetic_written:bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.13310185185185183, -0.006944444444444445], "families": 12, "family_macro_difference": -0.06597222222222221, "paired_rows": 216, "row_weighted_difference": -0.0787037037037037}, "arithmetic_written:print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.03819444444444445, 0.09143518518518517], "families": 12, "family_macro_difference": 0.024305555555555552, "paired_rows": 216, "row_weighted_difference": 0.009259259259259259}, "arithmetic_written:print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [0.04973958333333334, 0.14351851851851852], "families": 12, "family_macro_difference": 0.0949074074074074, "paired_rows": 216, "row_weighted_difference": 0.10185185185185185}, "arithmetic_written:print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [-0.04282407407407407, -0.003472222222222222], "families": 12, "family_macro_difference": -0.020833333333333332, "paired_rows": 216, "row_weighted_difference": -0.023148148148148147}, "bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.16319444444444445, -0.05902777777777777], "families": 12, "family_macro_difference": -0.1111111111111111, "paired_rows": 288, "row_weighted_difference": -0.1111111111111111}, "bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.1770833333333333, -0.08680555555555557], "families": 12, "family_macro_difference": -0.1284722222222222, "paired_rows": 288, "row_weighted_difference": -0.1284722222222222}, "print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [0.03125000000000001, 0.2396701388888884], "families": 12, "family_macro_difference": 0.13541666666666666, "paired_rows": 288, "row_weighted_difference": 0.13541666666666666}, "print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [0.19097222222222224, 0.3611111111111111], "families": 12, "family_macro_difference": 0.2743055555555555, "paired_rows": 288, "row_weighted_difference": 0.2743055555555556}, "print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [-0.05208333333333332, 0.006944444444444444], "families": 12, "family_macro_difference": -0.020833333333333332, "paired_rows": 288, "row_weighted_difference": -0.020833333333333332}, "untouched_literal:bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.4351851851851852, -0.23148148148148145], "families": 9, "family_macro_difference": -0.32407407407407407, "paired_rows": 72, "row_weighted_difference": -0.3055555555555556}, "untouched_literal:bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.3888888888888889, -0.23148148148148145], "families": 9, "family_macro_difference": -0.3055555555555556, "paired_rows": 72, "row_weighted_difference": -0.2777777777777778}, "untouched_literal:print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [0.3145833333333333, 0.5925925925925926], "families": 9, "family_macro_difference": 0.45370370370370366, "paired_rows": 72, "row_weighted_difference": 0.5138888888888888}, "untouched_literal:print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [0.6111111111111112, 0.8703703703703705], "families": 9, "family_macro_difference": 0.7407407407407407, "paired_rows": 72, "row_weighted_difference": 0.7916666666666666}, "untouched_literal:print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [-0.16666666666666669, 0.07407407407407407], "families": 9, "family_macro_difference": -0.03703703703703704, "paired_rows": 72, "row_weighted_difference": -0.013888888888888888}}`
