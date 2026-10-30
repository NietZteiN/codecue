# Structural and algebraic relationship discovery readouts

Prospective fixed readout recipe on an adaptive discovery bank, not final confirmation, natural causal use or mechanism C. Sites 3, 7 and 8 alone are fitted; other captured sites are reserved for later work. Raw 4096-dimensional hidden coordinates and matched 4096 character-ngram features have train-only float64 normalization and fixed alpha 100. Independent relation columns and value columns share a Gram factorization without output coupling. Primary algebraic comparisons use relations derived from four independent 32-class categorical value heads; rounded/clipped scalar-value derivation is secondary. Whole-pipeline parameter counts differ, so this is not an equal-total-capacity comparison. Numeric values, graph/stratum IDs and oracle relations never enter readout features. Binary ridge outputs are uncalibrated scores, with threshold 0.5. Undefined and constant tasks are retained and reported, not claimed as relationship learning. Primary eligibility uses only training group class support; all fixed eligible development cells must contain both classes. Components, not numeric/lexical relatives, are uncertainty units. Three seeds change component weights and coherent shuffle tasks, not independent experiments. Component derangements move initialization-prefix base blocks, with copy-parent permutations inside each base and lexical ties retained. This preserves unweighted target marginals, not necessarily weighted marginals. Conditional intervals resample nine development components without refitting or multiplicity adjustment. Successful relation decoding alone does not establish a dedicated relational representation or an identified algorithm.

1,944 source cases: 1,296 training rows in 18 components; 648 development rows in nine components. Fitted sites are 3, 7 and 8; other captured sites are not fitted.

45 shared weighted-ridge factorizations; 87,480 exact saved-parameter row replays. Real and coherent-shuffle target columns are independent right-hand sides. Four 32-way categorical value heads are the primary value-derived comparator; scalar-value rounding is secondary.

The direct primary algebraic task has 18 scalar outputs; the categorical value pipeline has 128 outputs. Both use the same feature bank, training normalization and per-column ridge objective, with different total parameter counts.

## Fixed primary algebraic comparison

Interval status: qualified_conditional_interval.

| Method | Four-family macro balanced accuracy |
|---|---:|
| direct | 0.850191 |
| categorical_value_derived | 0.687791 |
| scalar_value_derived | 0.619313 |
| structural_position_prior | 0.500000 |
| surface | 0.587333 |

| Contrast | Increment | Conditional group 95% |
|---|---:|---|
| direct_minus_categorical_value_derived | +0.162400 | [0.1256236471955241, 0.2116434530425705] |
| direct_minus_scalar_value_derived | +0.230878 | [0.19554562273254267, 0.2669158522624155] |
| direct_minus_structural_position_prior | +0.350191 | [0.31854489602088204, 0.37691505109575285] |
| direct_minus_surface | +0.262858 | [0.22683047136321446, 0.2968393032840617] |

## Fixed primary structural comparison

Four three-way parent heads reconstruct the whole eight-definition graph under a known fixed roots/version scaffold. This is compositional parent recovery, not learned node/version discovery.

| Method | Whole-parent-graph accuracy |
|---|---:|
| direct | 0.834877 |
| structural_position_prior | 0.024691 |
| surface | 0.019033 |

| Contrast | Increment | Conditional group 95% |
|---|---:|---|
| direct_minus_structural_position_prior | +0.810185 | [0.6110853909465022, 0.934670781893004] |
| direct_minus_surface | +0.815844 | [0.6152006172839506, 0.9439429012345678] |

All fitted layers, sites, weighting seeds, pooled per-cell metrics, class-support and constant/undefined-cell descriptions remain in results_v1.json. Component-level primary uncertainty is computed from saved row correctness; full per-cell/per-group AP tables are not duplicated.

Coherent shuffle heads are trained and evaluated against separately shuffled TRAIN/DEV targets. Component derangements move initialization-prefix base blocks, then permute copy-parent variants within each base, keeping lexical relatives tied. One donor mapping applies across every target and site. Unweighted marginals are preserved; reported weighted-marginal differences are retained. Shuffle metrics describe the control task and are not averaged into the original-label primary contrast.

Fitting performs zero additional model queries. The source capture separately records 1,944 case prefills and zero generated responses.
