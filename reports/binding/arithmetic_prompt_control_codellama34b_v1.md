# Arithmetic prompt/output semantics control

Adaptive matched discovery on reused program families. Print syntax and wording change token context. Original outcomes and parser remain unchanged; no causal or confirmatory claim.

5,760 exact generated responses; 5,760 prefill attempts.

| Cell | Cases | Accuracy | Invalid |
|---|---:|---:|---:|
| all/bare_i0 | 1152 | 21.441% | 0.000% |
| train/bare_i0 | 864 | 21.875% | 0.000% |
| train/untouched_literal/bare_i0 | 288 | 45.486% | 0.000% |
| train/arithmetic_written/bare_i0 | 576 | 10.069% | 0.000% |
| development/bare_i0 | 288 | 20.139% | 0.000% |
| development/untouched_literal/bare_i0 | 72 | 50.000% | 0.000% |
| development/arithmetic_written/bare_i0 | 216 | 10.185% | 0.000% |
| all/print_i0 | 1152 | 36.024% | 0.000% |
| train/print_i0 | 864 | 37.037% | 0.000% |
| train/untouched_literal/print_i0 | 288 | 88.889% | 0.000% |
| all/bare_i1 | 1152 | 21.788% | 6.510% |
| train/bare_i1 | 864 | 21.528% | 6.829% |
| train/untouched_literal/bare_i1 | 288 | 44.792% | 9.375% |
| all/print_i1 | 1152 | 40.538% | 0.260% |
| train/print_i1 | 864 | 41.204% | 0.231% |
| train/untouched_literal/print_i1 | 288 | 92.014% | 0.000% |
| all/bare_i2 | 1152 | 17.969% | 4.774% |
| train/bare_i2 | 864 | 17.824% | 4.745% |
| train/untouched_literal/bare_i2 | 288 | 34.722% | 9.028% |
| all/print_i2 | 1152 | 35.764% | 3.385% |
| train/print_i2 | 864 | 37.037% | 3.009% |
| train/untouched_literal/print_i2 | 288 | 85.069% | 5.903% |
| train/arithmetic_written/print_i0 | 576 | 11.111% | 0.000% |
| train/arithmetic_written/bare_i1 | 576 | 9.896% | 5.556% |
| train/arithmetic_written/print_i1 | 576 | 15.799% | 0.347% |
| train/arithmetic_written/bare_i2 | 576 | 9.375% | 2.604% |
| train/arithmetic_written/print_i2 | 576 | 13.021% | 1.562% |
| development/print_i0 | 288 | 32.986% | 0.000% |
| development/untouched_literal/print_i0 | 72 | 97.222% | 0.000% |
| development/bare_i1 | 288 | 22.569% | 5.556% |
| development/untouched_literal/bare_i1 | 72 | 38.889% | 5.556% |
| development/print_i1 | 288 | 38.542% | 0.347% |
| development/untouched_literal/print_i1 | 72 | 97.222% | 0.000% |
| development/bare_i2 | 288 | 18.403% | 4.861% |
| development/untouched_literal/bare_i2 | 72 | 29.167% | 9.722% |
| development/print_i2 | 288 | 31.944% | 4.514% |
| development/untouched_literal/print_i2 | 72 | 79.167% | 6.944% |
| development/arithmetic_written/print_i0 | 216 | 11.574% | 0.000% |
| development/arithmetic_written/bare_i1 | 216 | 17.130% | 5.556% |
| development/arithmetic_written/print_i1 | 216 | 18.981% | 0.463% |
| development/arithmetic_written/bare_i2 | 216 | 14.815% | 3.241% |
| development/arithmetic_written/print_i2 | 216 | 16.204% | 3.704% |

Matched DEV prompt contrasts: `{"arithmetic_written:bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.025462962962962965, 0.15972222222222224], "families": 12, "family_macro_difference": 0.061342592592592594, "paired_rows": 216, "row_weighted_difference": 0.06944444444444445}, "arithmetic_written:bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.0474537037037037, 0.12962962962962962], "families": 12, "family_macro_difference": 0.04050925925925925, "paired_rows": 216, "row_weighted_difference": 0.046296296296296294}, "arithmetic_written:print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.011574074074074075, 0.03935185185185185], "families": 12, "family_macro_difference": 0.012731481481481483, "paired_rows": 216, "row_weighted_difference": 0.013888888888888888}, "arithmetic_written:print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [-0.02199074074074074, 0.07060185185185185], "families": 12, "family_macro_difference": 0.024305555555555552, "paired_rows": 216, "row_weighted_difference": 0.018518518518518517}, "arithmetic_written:print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [-0.032407407407407406, 0.07870370370370369], "families": 12, "family_macro_difference": 0.020833333333333332, "paired_rows": 216, "row_weighted_difference": 0.013888888888888888}, "bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.05208333333333334, 0.11805555555555557], "families": 12, "family_macro_difference": 0.024305555555555556, "paired_rows": 288, "row_weighted_difference": 0.024305555555555556}, "bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.08680555555555557, 0.06944444444444443], "families": 12, "family_macro_difference": -0.017361111111111115, "paired_rows": 288, "row_weighted_difference": -0.017361111111111112}, "print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [0.0625, 0.19453124999999957], "families": 12, "family_macro_difference": 0.12847222222222224, "paired_rows": 288, "row_weighted_difference": 0.1284722222222222}, "print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [0.06944444444444443, 0.25], "families": 12, "family_macro_difference": 0.15972222222222224, "paired_rows": 288, "row_weighted_difference": 0.1597222222222222}, "print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [0.052083333333333336, 0.21874999999999997], "families": 12, "family_macro_difference": 0.13541666666666666, "paired_rows": 288, "row_weighted_difference": 0.13541666666666666}, "untouched_literal:bare_i1_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.2222222222222222, 0.05555555555555555], "families": 9, "family_macro_difference": -0.08333333333333331, "paired_rows": 72, "row_weighted_difference": -0.1111111111111111}, "untouched_literal:bare_i2_minus_bare_i0": {"conditional_family_bootstrap_95": [-0.3796296296296296, -0.027777777777777773], "families": 9, "family_macro_difference": -0.2037037037037037, "paired_rows": 72, "row_weighted_difference": -0.20833333333333334}, "untouched_literal:print_i0_minus_bare_i0": {"conditional_family_bootstrap_95": [0.3055555555555555, 0.5925925925925926], "families": 9, "family_macro_difference": 0.4444444444444444, "paired_rows": 72, "row_weighted_difference": 0.4722222222222222}, "untouched_literal:print_i1_minus_bare_i1": {"conditional_family_bootstrap_95": [0.38888888888888884, 0.6576388888888877], "families": 9, "family_macro_difference": 0.5277777777777778, "paired_rows": 72, "row_weighted_difference": 0.5833333333333334}, "untouched_literal:print_i2_minus_bare_i2": {"conditional_family_bootstrap_95": [0.31481481481481477, 0.6296296296296297], "families": 9, "family_macro_difference": 0.4722222222222222, "paired_rows": 72, "row_weighted_difference": 0.5}}`
