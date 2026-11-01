# Conditional readouts: median-prior and regularization diagnostics

Exploratory follow-up after observing that the declared ridge grid selected its upper endpoint. All prior constants below use TRAIN only; all methods are reported, with no best-prior selection on DEV. The original 240 fits and their source/hidden contrasts remain unchanged. No new ridge fits or language-model calls; nine four-slot prior-statistic vectors were estimated.

| Prior | Computed MAE | Computed rounded exact |
|---|---:|---:|
| all_slot_mean | 5.3348 | 8.90% |
| all_slot_median | 5.3308 | 8.90% |
| computed_family_median | 5.3308 | 8.90% |
| zero | 5.3308 | 8.90% |

The computed-family median estimates one constant per output slot from TRAIN computed observations, weighting each family by its original fitting-seed weight divided by its total computed observations. It minimizes the corresponding constant-predictor absolute-loss objective. Oracle computed masks are TRAIN/evaluation annotations only, not per-example prediction inputs. All-slot mean/median and fixed zero give simpler reference points. Medians are verified against brute-force candidate absolute losses.

## Joint minus prior computed-value MAE

| Joint cell | Prior | Difference | Descriptive 95% family interval |
|---|---|---:|---|
| llama8b/joint | all_slot_median | -0.3445 | [-0.5925, -0.1107] |
| llama8b/joint | computed_family_median | -0.3445 | [-0.5925, -0.1107] |
| llama8b/joint | zero | -0.3445 | [-0.5925, -0.1107] |
| codellama34b/joint | all_slot_median | -0.3863 | [-0.6530, -0.1352] |
| codellama34b/joint | computed_family_median | -0.3863 | [-0.6530, -0.1352] |
| codellama34b/joint | zero | -0.3863 | [-0.6530, -0.1352] |

## TRAIN regularization boundary

| Cell | Selected alpha | Upper boundary | TRAIN CV loss at 1 / 100 / 10000 |
|---|---:|---|---|
| source/source1024 | 10000 | True | 5.7039 / 5.6093 / 5.3289 |
| source/source2048 | 10000 | True | 5.7056 / 5.6358 / 5.3340 |
| llama8b/hidden | 10000 | True | 7.0372 / 5.5574 / 5.1831 |
| llama8b/joint | 10000 | True | 7.6403 / 5.7687 / 5.1154 |
| llama8b/shuffled_joint | 10000 | True | 8.2875 / 6.1765 / 5.3707 |
| codellama34b/hidden | 10000 | True | 7.0020 / 5.4040 / 5.1076 |
| codellama34b/joint | 10000 | True | 7.7095 / 5.6224 / 5.0690 |
| codellama34b/shuffled_joint | 10000 | True | 8.6967 / 6.2626 / 5.3657 |

Upper-boundary selection motivates a new, prospectively frozen TRAIN-only penalty continuation and stronger robust-loss/constant baselines before treating the current learned models as optimized. These diagnostics were added after the ridge results were inspected: intervals remain descriptive, non-simultaneous and adaptive, not confirmation. A joint gain against finite learned source features does not by itself show an improvement over a loss-appropriate constant predictor or a maintained numeric state.
