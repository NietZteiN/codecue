# Overnight relationship behavior

Adaptive discovery on reused structural components. No causal mechanism or confirmatory claim. Literal/computed formats also differ in tokens and operations.

7,290 exact generated responses; 7,290 prefill attempts.

| Cell | Cases | Accuracy | Invalid |
|---|---:|---:|---:|
| overall | 7290 | 43.964% | 1.948% |
| source_form/literal | 5832 | 52.709% | 0.617% |
| query/literal/0 | 1458 | 54.527% | 0.617% |
| split/development/literal | 1944 | 51.543% | 0.360% |
| numeric_seed/101/literal | 1944 | 51.235% | 0.874% |
| source_form/computed | 1458 | 8.985% | 7.270% |
| query/computed/0 | 1458 | 8.985% | 7.270% |
| split/development/computed | 486 | 11.728% | 6.173% |
| numeric_seed/101/computed | 486 | 7.407% | 8.025% |
| query/literal/1 | 1458 | 52.881% | 1.783% |
| query/literal/2 | 1458 | 52.401% | 0.069% |
| query/literal/3 | 1458 | 51.029% | 0.000% |
| split/train/literal | 3888 | 53.292% | 0.746% |
| split/train/computed | 972 | 7.613% | 7.819% |
| numeric_seed/211/literal | 1944 | 50.669% | 0.669% |
| numeric_seed/211/computed | 486 | 6.996% | 8.230% |
| numeric_seed/307/literal | 1944 | 56.224% | 0.309% |
| numeric_seed/307/computed | 486 | 12.551% | 5.556% |

Computed-minus-literal DEV comparison: `{"bootstrap_seed": 117, "conditional_group_bootstrap_95": [-0.4588477366255144, -0.28189300411522633], "contrast": "computed_minus_literal", "development_components": ["relationship-routing:000", "relationship-routing:012", "relationship-routing:021", "relationship-routing:102", "relationship-routing:111", "relationship-routing:120", "relationship-routing:201", "relationship-routing:210", "relationship-routing:222"], "draws": 2000, "matched_pairs": 486, "mean": -0.368312757201646, "multiplicity_adjusted": false, "refits": 0}`
