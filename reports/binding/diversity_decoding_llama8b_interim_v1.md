# Llama 3.1 8B diversity decoding: audited interim result

**Llama 3.1 8B only.** Its readout worker completed with exit 0:0 and the actual saved-parameter/scientific-metric/control-marginal replay proof passed. CodeLlama 34B is incomplete and is not included or ranked here.

The fixed primary is layer 24 at the final-assignment site 7, averaged over weighting seeds 17, 29 and 43. All 45 banks and the full class inventories remain retained; no favorable layer or subset replaces the primary.

| Whole task | Hidden direct | Exact-prefix text | TRAIN prior | Hidden prefix-sham |
|---|---:|---:|---:|---:|
| Four current defining statements | 56.389% | 6.296% | 0.000% | 0.093% |
| Four current version numbers | 22.870% | 9.630% | 0.000% | 0.370% |
| Four copy-parent statements | 30.370% | 7.963% | 1.111% | 0.278% |

These are joint four-head accuracies over 1,440 DEV rows in 15 families. Every family contributes 96 rows, so row and equal-family whole-task means agree to rounding. The sham column scores a different source-keyed task with different marginals; it is not a matched chance estimate for the real graph task.

The hidden decoder exceeds the text feature map and prior on all three fixed whole tasks, but whole current-version recovery is only 22.870%. This is evidence of partial accessibility on the declared bank, not reliable whole-state recovery. Full source syntax determines these targets; a hidden-over-character advantage does not imply information absent from source.

All four version classes now have actual DEV examples in every slot: 600/360/360/120 rows for versions 1/2/3/4 per slot. Their TRAIN graph supports are 45/30/30/15, and DEV graph supports are 15/10/10/5. Unlike the earlier restricted bank, version 3 is tested and no final version head is constant. Coverage is broader, while class frequencies remain unequal.

| Fixed slot | Hidden version head | Version 1 | Version 2 | Version 3 | Version 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 76.204% | 92.444% | 71.481% | 62.222% | 51.111% |
| 1 | 68.889% | 74.222% | 59.630% | 60.741% | 94.444% |
| 2 | 70.278% | 78.444% | 58.148% | 69.630% | 67.778% |
| 3 | 61.019% | 79.111% | 37.407% | 51.481% | 70.000% |

Each class entry averages the three fixed weighting seeds on the same actual class rows. These are individual supplied-slot heads, not whole-state success rates or independent replications. Strongly uneven class/slot performance remains despite complete source support. The TRAIN prior gets version 1 right and versions 2–4 wrong, yielding 41.667% per-slot accuracy but zero joint four-version accuracy.

Individual parent heads have different difficulty. Their hidden accuracies are 80.185%, 60.093%, 64.722%, 100.000%. The last head refers to the immediately preceding copy at this capture site; its perfect score does not establish general read-time binding or version recovery. Parent and current-definition predictions are statement indices. Translating them to natural variable@version labels would use an oracle source map and must remain explicitly assisted.

This run repairs missing slot/version support in the source bank and makes real errors on versions 3/4 measurable. It does not establish causal state tracking, computed-program reliability or unfamiliar-program prediction. Relative to the earlier study, graph sampling, overwrite profiles, slot rotations, class frequencies, TRAIN size and effective fixed-alpha fitting changed together. Cross-study score differences do not isolate the effect of novelty or coverage.

Probe features are selected hidden vectors or signed character n-grams of the exact visible prefix; source graph/profile/rotation metadata supplies validation and labels only. The data remain restricted literal-root/copy programs with supplied variable slots and fixed initialization order. Fifteen DEV families, repeated lexical/numeric/query relatives and three dependent weighting seeds support a descriptive discovery result; no new confidence interval is claimed.

The 8B capture used 5,760 distinct prefills with no retries or generated answers. The readout/replay grid completed 45 factorizations and 259,200 parameter-replay case rows. This review read only checksum-pinned JSON/report metadata, not arrays, coefficients or models, and did not rerun fitting or audits.

Full original results remain in [the audited 8B report](diversity_decoding_llama8b_v1.md). The new [interim metadata review](../../artifacts/binding/diversity_decoding/20261028_v1/interim_llama8b_review_v1.json) records exact values, class counts, input pins and the contemporaneous 34B scheduler state. Existing published paths and helper sources remain unchanged.
