# Posthoc relationship decoding and answer behavior

Posthoc adaptive discovery on the same nine familiar structural components. Decoded correctness is an external readout measurement, not evidence that the model naturally uses that information or that it causes an answer. Conditional associations do not validate an unfamiliar-program predictor. Computed/literal formats also change operations, tokens and positions. Weighting seeds, lexical twins, numeric draws and query siblings are not independent replications. Other slots can be answer ancestors. Query is future text at sites3/7, so slot/recency differences are not query effects. Intervals condition on saved fits, omit refitting and multiplicity correction.

All rows below are DEV, joined by exact ID. Conditional probabilities use fit-averaged joint masses. Undefined graph checkpoints are omitted.

| Model | Form | Backend / site | Answer correct | Graph correct | Value correct | Graph correct and answer wrong |
|---|---|---|---:|---:|---:|---:|
| llama8b | literal | hidden/site3 | 51.543% | undefined | 54.167% | undefined |
| llama8b | literal | surface/site3 | 51.543% | undefined | 88.940% | undefined |
| llama8b | literal | hidden/site7 | 51.543% | 74.966% | 10.562% | 34.928% |
| llama8b | literal | surface/site7 | 51.543% | 3.635% | 14.060% | 1.663% |
| llama8b | literal | hidden/site8 | 51.543% | 49.108% | 22.565% | 23.457% |
| llama8b | literal | surface/site8 | 51.543% | 1.800% | 13.289% | 0.857% |
| llama8b | computed | hidden/site3 | 11.728% | undefined | 5.761% | undefined |
| llama8b | computed | surface/site3 | 11.728% | undefined | 9.053% | undefined |
| llama8b | computed | hidden/site7 | 11.728% | 94.719% | 7.133% | 83.265% |
| llama8b | computed | surface/site7 | 11.728% | 2.675% | 6.584% | 1.989% |
| llama8b | computed | hidden/site8 | 11.728% | 58.642% | 8.230% | 50.892% |
| llama8b | computed | surface/site8 | 11.728% | 1.372% | 5.556% | 0.823% |
| codellama34b | literal | hidden/site3 | 53.961% | undefined | 53.035% | undefined |
| codellama34b | literal | surface/site3 | 53.961% | undefined | 90.484% | undefined |
| codellama34b | literal | hidden/site7 | 53.961% | 93.004% | 16.049% | 42.524% |
| codellama34b | literal | surface/site7 | 53.961% | 8.505% | 17.318% | 3.789% |
| codellama34b | literal | hidden/site8 | 53.961% | 64.849% | 27.058% | 29.492% |
| codellama34b | literal | surface/site8 | 53.961% | 2.486% | 15.844% | 0.977% |
| codellama34b | computed | hidden/site3 | 2.881% | undefined | 6.996% | undefined |
| codellama34b | computed | surface/site3 | 2.881% | undefined | 8.230% | undefined |
| codellama34b | computed | hidden/site7 | 2.881% | 92.730% | 6.241% | 89.849% |
| codellama34b | computed | surface/site7 | 2.881% | 1.372% | 9.739% | 1.372% |
| codellama34b | computed | hidden/site8 | 2.881% | 58.093% | 5.761% | 56.310% |
| codellama34b | computed | surface/site8 | 2.881% | 0.343% | 7.750% | 0.343% |

Queried value means its current checkpoint value. At site3 this is the initialization value, not necessarily the final answer.

| Model | Backend | Site7 placebo | Site8 query effect | Site8 minus7 |
|---|---|---:|---:|---:|
| llama8b | hidden | 0.000 pp | 0.857 pp | 0.857 pp |
| llama8b | surface | 0.000 pp | -0.063 pp | -0.063 pp |
| codellama34b | hidden | 0.000 pp | -0.400 pp | -0.400 pp |
| codellama34b | surface | 0.000 pp | 0.297 pp | 0.297 pp |

The machine result retains every query/numeric-seed/validity cell, support, conditional denominator and valid/invalid bootstrap count, plus the full4×4 within-body query tables and fixed-slot contrasts. Invalid responses remain wrong. Other slots can be answer ancestors.

No new model queries, fits, parameter predictions or hidden-state array reads were performed. Original score banks and generated responses remain unchanged.
