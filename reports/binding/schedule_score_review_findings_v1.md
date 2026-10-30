# Posthoc saved-score and fixed-target query diagnostics

All 90 completed parameter banks were read only through their saved identity and score arrays. Original metrics reproduce exactly; no parameters were applied or fitted.

The table retains layer24 for both models and the matched surface baseline. Site7 precedes the query; site8 observes it. Effects hold each target slot fixed across the four queries on an identical assignment body.

| Model | Backend | Site | Method | Current-definition effect (pp) | Equal-graph effect (pp) | Current-version effect (pp) | Equal-graph effect (pp) |
|---|---|---:|---|---:|---:|---:|---:|
| llama8b | hidden | 7 | direct | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | hidden | 7 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | hidden | 7 | random_prefix_control | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | hidden | 8 | direct | 3.975 | -1.335 | 0.782 | 2.747 |
| llama8b | hidden | 8 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | hidden | 8 | random_prefix_control | -0.399 | -0.847 | 0.080 | -2.170 |
| llama8b | surface | 7 | direct | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | surface | 7 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | surface | 7 | random_prefix_control | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | surface | 8 | direct | -0.383 | -0.880 | 0.000 | 0.000 |
| llama8b | surface | 8 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| llama8b | surface | 8 | random_prefix_control | 0.367 | 0.679 | 0.383 | -0.557 |
| codellama34b | hidden | 7 | direct | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | hidden | 7 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | hidden | 7 | random_prefix_control | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | hidden | 8 | direct | 3.991 | 2.604 | 1.102 | 4.167 |
| codellama34b | hidden | 8 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | hidden | 8 | random_prefix_control | -0.830 | -1.655 | -0.447 | 1.096 |
| codellama34b | surface | 7 | direct | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | surface | 7 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | surface | 7 | random_prefix_control | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | surface | 8 | direct | -0.351 | -0.039 | 0.000 | 0.000 |
| codellama34b | surface | 8 | training_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| codellama34b | surface | 8 | random_prefix_control | 0.335 | 0.378 | 0.639 | 0.149 |

Every layer, seed, site, fixed target slot, confusion matrix, joint-correctness mass, pre-query prediction disagreement and graph denominator remains in results_v1.json. Prediction-only DEV banks retain aligned case IDs, truths, decisions and uncalibrated margins.

- Posthoc discovery analysis after examining the original aggregate results; this is neither an untouched test nor a reliability-gate rescue.
- Five unequal DEV graph families are the structural units. Numeric, lexical, body-query and weighting-seed relatives are dependent; no new confidence interval is claimed.
- Every fixed target slot is compared with itself across the four queries on an identical assignment body. Query effects do not compare different queried targets.
- Site7 is a pre-query placebo; site8 observes the explicit query. Any site7 disagreement or margin difference is retained, including numerical or padding effects.
- Joint scalar-version/definition/parent correctness describes different decoder tasks; correct version integers do not establish correct bindings or a causal state-tracking algorithm.
- Random-prefix controls are separate sham tasks with different class marginals and potentially unlawful joint graphs. Their diagnostic results do not establish matched task difficulty.
- Scores are uncalibrated ridge outputs; margins and top scores are descriptive. No threshold, layer, seed, class or subgroup is selected using this analysis.
- No model/tokenizer/activation/coefficient arrays are loaded, no parameters are reapplied, and no model or probe is fitted.
