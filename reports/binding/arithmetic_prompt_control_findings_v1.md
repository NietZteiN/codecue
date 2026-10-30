# Matched print/query semantics control: findings

Adaptive discovery on reused families. Changed syntax and wording also change token context. Parser and original scores unchanged; no mechanism or untouched-confirmation claim.

11,520 new generated responses and2,304 cached baseline responses cover two source forms × three instructions for both models. Original bare/I0 answers were not recollected.

| Model | Arm | Arithmetic DEV accuracy | Invalid | Literal DEV accuracy | Invalid |
|---|---|---:|---:|---:|---:|
| llama8b | bare_i0 | 10.19% | 2.31% | 44.44% | 4.17% |
| llama8b | print_i0 | 11.11% | 0.93% | 95.83% | 0.00% |
| llama8b | bare_i1 | 5.56% | 0.00% | 13.89% | 0.00% |
| llama8b | print_i1 | 15.74% | 5.09% | 93.06% | 0.00% |
| llama8b | bare_i2 | 2.31% | 37.50% | 16.67% | 29.17% |
| llama8b | print_i2 | 0.00% | 78.70% | 15.28% | 79.17% |
| codellama34b | bare_i0 | 10.19% | 0.00% | 50.00% | 0.00% |
| codellama34b | print_i0 | 11.57% | 0.00% | 97.22% | 0.00% |
| codellama34b | bare_i1 | 17.13% | 5.56% | 38.89% | 5.56% |
| codellama34b | print_i1 | 18.98% | 0.46% | 97.22% | 0.00% |
| codellama34b | bare_i2 | 14.81% | 3.24% | 29.17% | 9.72% |
| codellama34b | print_i2 | 16.20% | 3.70% | 79.17% | 6.94% |

The figure uses the prospectively fixed original instruction I0. I1 and I2 are the two clarified instructions, all retained above. Printing raises untouched-literal accuracy substantially in I0 while leaving arithmetic-written accuracy low. Clear wording does not produce a reliable arithmetic regime; I2 also produces many invalid Llama responses. These are prompt-specific results, not evidence that the hidden representation lacks values or relationships.

| Model | DEV stratum | Paired contrast | Row difference (pp) | Family-macro difference (pp) | Conditional family95% interval (pp) | Families |
|---|---|---|---:|---:|---|---:|
| llama8b | arithmetic_written | print_i0 − bare_i0 | 0.93 | 2.43 | [-3.82, 9.14] | 12 |
| llama8b | untouched_literal | print_i0 − bare_i0 | 51.39 | 45.37 | [31.46, 59.26] | 9 |
| codellama34b | arithmetic_written | print_i0 − bare_i0 | 1.39 | 1.27 | [-1.16, 3.94] | 12 |
| codellama34b | untouched_literal | print_i0 − bare_i0 | 47.22 | 44.44 | [30.56, 59.26] | 9 |

Each contrast pairs the exact same original case. Intervals resample whole families, conditional on these outcomes, with no refits or multiplicity correction. Arithmetic comparisons use12 families; literal comparisons use the9 families with untouched queried variables. All other predeclared contrasts are retained in the machine-readable summaries.

Decision: use explicit printed queries for the next discovery calibration, retain all wording results, and establish a reliable shorter arithmetic regime before causal patching. Preserve the original bare-query scores and the graph-readout TRAIN/DEV gap. This control diagnoses an interface effect on literal reporting; it does not rescue arithmetic performance.

[Original overnight findings](arithmetic_graph_overnight_findings_v1.md) · [Morning replay audit](arithmetic_graph_morning_review_v2.md) · [Control plan](arithmetic_prompt_control_plan_v1.md)
