# Probe improvement: implementation and launch, October 30

Implemented the [archived-feature revision](arithmetic_probe_improvement_plan_v1.md) and the [new local-dependency protocol](arithmetic_local_probe_plan_v1.md). Original results and frozen sources remain intact. New results remain discovery findings; existing DEV is not fresh confirmation.

The archived analysis compares four layers, three regularization settings and three principal-component ranks using three grouped TRAIN folds and three family-weighting seeds. Separate TRAIN objectives select dependency, algebraic-relation and continuous-value readouts. All90 CV banks completed across both checkpoints, covering810 candidate observations. The first workers stopped at a protected output filename before publishing selected models. The repaired version passed exact cache/configuration/source checks and preserves both sets of locked choices without repeating CV. The [repair review](../../artifacts/binding/arithmetic_probe_selection/20261030_v1/publication_guard_review_v1.json) and [cache verification](../../artifacts/binding/arithmetic_probe_selection/20261030_v2/cache_verification_review_v1.json) retain the history.

The first frozen software validation passed2,378 tests. The focused new-method tests passed48 tests, followed by five repair/controller checks (overlapping cases; these are not additive counts). A second full frozen regression pass gates the repaired analyses and new captures.

| Work | Job | State at launch |
|---|---:|---|
| Second frozen software validation | 484973 | Running |
| Llama native local-span preparation | 484974 | Queued |
| CodeLlama native local-span preparation | 484975 | Queued |
| Llama selected-model publication/recovery | 484976 | Queued after successful validation |
| CodeLlama selected-model publication/recovery | 484977 | Queued after successful validation |
| Local experiment supervisor | 484972 | Scheduled; installs recurring successors |

The new source bank has216 TRAIN and72 development structures, six times the original structure counts, plus six calibration structures. There are5,292 prompts per checkpoint: three numeric seeds, three sampling strata and two lexical forms across depths1/2/4/6. Assignment values and surface answers passed independent Python checks. Every original canonical structure is excluded; all new structural relatives stay in their split. One-update calibration is excluded from probe fits.

After software/native validation, the supervised DAG releases10,584 local capture prefills and11,016 one/two-update printed-answer queries across both checkpoints. CPU readouts compare local/global hidden features and a source comparator through shared linear, rank16 bilinear and width32 MLP scorers. TRAIN-only architecture selection, matched random-family controls and nested54/108/216-structure learning curves are implemented. Exact source name/recency tracking remains a100% oracle ceiling, so recovered edges alone cannot establish source superiority or causal use.

The supervisor preserves other work, counts actual attempts and retries only eligible scheduler interruptions. New completion receipts, results and reviews enter the existing automatic experiment logger. [Submitted DAG snapshot](../../artifacts/binding/arithmetic_local/20261030_v1/suite/submission_review_v1.json) · [Frozen configuration](../../configs/binding/arithmetic_local_20261030_v1/suite.json) · [Reproduction and publication](../../reproducibility/arithmetic_probe_20261030_README.md).
