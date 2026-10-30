# Discovery replication preparation

Generated discovery/calibration source preparation only; no model inference, final outcomes, training or confirmatory claim. Distinct generation seeds are not independent structural replications. Cross-bank template/base ID namespaces cannot be pooled without content checks. Alpha-skeleton sharing is expected in numeric calibration but invalidates treating rows as new independent structures. No automatic pooling, resplitting or final opening is authorized by a passed source audit.

Prepared/audited 30,960 generated source rows in 9 banks. No model outcome was collected.

| Bank | Kind | Rows | Unique source hashes | Canonical ASTs | Alpha skeletons | Train/dev shared skeletons |
|---|---|---:|---:|---:|---:|---:|
| competition_cohort1 | competition | 2496 | 2496 | 480 | 200 | 0 |
| live_load_cohort1 | live_load | 4752 | 4752 | 912 | 386 | 0 |
| arithmetic_readout_cohort1 | arithmetic_readout | 3072 | 2424 | 2424 | 8 | 8 |
| competition_cohort2 | competition | 2496 | 2496 | 480 | 199 | 0 |
| live_load_cohort2 | live_load | 4752 | 4752 | 912 | 386 | 0 |
| arithmetic_readout_cohort2 | arithmetic_readout | 3072 | 2420 | 2420 | 8 | 8 |
| competition_cohort3 | competition | 2496 | 2496 | 480 | 200 | 0 |
| live_load_cohort3 | live_load | 4752 | 4752 | 912 | 386 | 0 |
| arithmetic_readout_cohort3 | arithmetic_readout | 3072 | 2412 | 2412 | 8 | 8 |

## Cross-bank overlap

| Left | Right | Shared row IDs | Shared source hashes | Shared canonical ASTs | Shared alpha skeletons | Cross-bank train/dev skeletons |
|---|---|---:|---:|---:|---:|---:|
| arithmetic_readout_cohort1 | arithmetic_readout_cohort2 | 64 | 650 | 650 | 8 | 8 |
| arithmetic_readout_cohort1 | arithmetic_readout_cohort3 | 80 | 612 | 612 | 8 | 8 |
| arithmetic_readout_cohort1 | competition_cohort1 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort1 | competition_cohort2 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort1 | competition_cohort3 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort1 | live_load_cohort1 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort1 | live_load_cohort2 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort1 | live_load_cohort3 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort2 | arithmetic_readout_cohort3 | 48 | 644 | 644 | 8 | 8 |
| arithmetic_readout_cohort2 | competition_cohort1 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort2 | competition_cohort2 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort2 | competition_cohort3 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort2 | live_load_cohort1 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort2 | live_load_cohort2 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort2 | live_load_cohort3 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort3 | competition_cohort1 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort3 | competition_cohort2 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort3 | competition_cohort3 | 0 | 0 | 0 | 0 | 0 |
| arithmetic_readout_cohort3 | live_load_cohort1 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort3 | live_load_cohort2 | 0 | 0 | 0 | 1 | 0 |
| arithmetic_readout_cohort3 | live_load_cohort3 | 0 | 0 | 0 | 1 | 0 |
| competition_cohort1 | competition_cohort2 | 0 | 0 | 0 | 103 | 48 |
| competition_cohort1 | competition_cohort3 | 0 | 0 | 0 | 104 | 48 |
| competition_cohort1 | live_load_cohort1 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort1 | live_load_cohort2 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort1 | live_load_cohort3 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort2 | competition_cohort3 | 0 | 0 | 0 | 103 | 48 |
| competition_cohort2 | live_load_cohort1 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort2 | live_load_cohort2 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort2 | live_load_cohort3 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort3 | live_load_cohort1 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort3 | live_load_cohort2 | 0 | 0 | 0 | 0 | 0 |
| competition_cohort3 | live_load_cohort3 | 0 | 0 | 0 | 0 | 0 |
| live_load_cohort1 | live_load_cohort2 | 6 | 6 | 6 | 386 | 0 |
| live_load_cohort1 | live_load_cohort3 | 18 | 18 | 18 | 386 | 0 |
| live_load_cohort2 | live_load_cohort3 | 6 | 6 | 6 | 386 | 0 |

## Content and declared identities

Content-based relation components: 51; 10 contain both training and development rows. This can be intentional numeric calibration, but it does not create independent structural validation.

Declared template IDs reused across banks with different content sets: 25. Declared base IDs reused with different canonical content: 120. Row IDs reused for different sources: 0.

Source preparation opportunities: 6 bank pairs share exact source prompts; 18 share structures with different canonical variant sets. These are potential discovery comparisons requiring an explicit plan, not new independent replications.

The full machine-readable review retains collision identities, all pairwise counts and content components. The fingerprint JSONL indexes every row by source/canonical/alpha hashes and its content relation component. Bank-local labels are not used as cross-bank identities.

All original bank splits and artifacts are preserved. A passed preparation audit neither chooses a scientific hypothesis nor authorizes pooling, new final outcomes or a confirmatory model run.
