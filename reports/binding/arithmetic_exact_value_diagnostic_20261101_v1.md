# Exact-value diagnostic of the audited penalty path

Postrun exploratory diagnostic on the inspected DEV cohort. No new probe fits, model calls, feature loads or sealed-final access. Modes are estimated on full TRAIN only and are diagnostic comparators; they do not participate in the frozen TRAIN-fold selection. Each displayed metric averages fitting seeds after taking structural-family means. All-four exact requires every variable to be correct in the same case.

| Cell/predictor | Computed MAE | Computed exact | Untouched exact | All-four exact |
|---|---:|---:|---:|---:|
| zero | 5.3308 | 8.90% | 6.52% | 0.00% |
| all_slot_mode | 5.3640 | 8.35% | 7.07% | 0.00% |
| computed_family_mode | 5.3308 | 8.90% | 6.52% | 0.00% |
| source/source1024 | 5.1647 | 5.30% | 12.34% | 0.00% |
| source/source2048 | 5.1790 | 5.37% | 12.54% | 0.00% |
| llama8b/hidden | 5.0060 | 6.42% | 11.78% | 0.03% |
| llama8b/joint | 4.9863 | 6.68% | 12.85% | 0.00% |
| llama8b/shuffled_joint | 5.1703 | 5.67% | 12.29% | 0.00% |
| codellama34b/hidden | 4.9726 | 5.90% | 13.43% | 0.03% |
| codellama34b/joint | 4.9444 | 6.00% | 13.18% | 0.00% |
| codellama34b/shuffled_joint | 5.1830 | 5.89% | 12.54% | 0.00% |

## Target support

| Slot | Distinct TRAIN values | Distinct TRAIN computed values | DEV computed slots | Unseen in TRAIN slot | Unseen in TRAIN computed slot |
|---|---:|---:|---:|---:|---:|
| 0 | 58 | 58 | 846 | 6 | 6 |
| 1 | 56 | 56 | 792 | 10 | 10 |
| 2 | 60 | 60 | 774 | 6 | 6 |
| 3 | 58 | 58 | 756 | 2 | 2 |

Support is an exact numeric-value check, not a generalization guarantee. The JSON contains per-slot TRAIN supports, TRAIN mode vectors and the DEV computed-target histogram (observation counts include repeated lexical/query relatives). No predictor is selected using this histogram. Mode tie-breaking uses the smallest integer. Computed modes use family-normalized computed-slot weights; unsupported heads fall back to the all-slot TRAIN mode.
