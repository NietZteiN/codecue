# October30 morning audit and saved-parameter review

The scheduled08:00 Chicago snapshot completed at08:00:04, with every arithmetic
suite stage complete and no scheduler errors. This follow-up preserves all
earlier sources, parameters, gates and scores. It performs no fitting or language
model/tokenizer loading, and does not open original sealed outcomes.

Reconstruct the exact nominated-layer hidden inputs and visible-prefix source
features for both models and all three sites. Verify the training feature,
target, weighting and ordered-case hashes against each saved ridge fit. Restore
all36 parameter banks and replay all4,608 rows per bank. Floating-point scores
may differ by at most1e-10 relative/absolute tolerance across CPU kernels;
binary and categorical decisions must agree exactly with the original DEV
scores. Record any mismatch rather than replacing historical results.

Report TRAIN/DEV individual-parent and complete-graph accuracy, TRAIN priors,
coherent-shuffle comparisons, per-head confusion/collapse, value-class support,
and queried versus other-value readout accuracy. Retain every site/backend/seed.
The figure uses answer preparation at the original nominated layers, not a
posthoc best layer. Training success diagnoses interpolation, not generalization.

For generated DEV answers, distinguish invalid responses, correct answers,
numeric matches to obsolete queried values, matches to another current variable,
their overlap, and neither. These signatures are numeric coincidences; they do
not identify causal ownership/version failures. Do not relax the integer parser.

The separate a27p training failures are outside this suite. Their logs report
`Saved production conditioning/target does not replay` after training. Preserve
their outputs and leave their jobs/dependencies unchanged during this review.

If training graphs decode well but DEV graphs do not, prioritize family transfer
and position-conditioned/source-parser controls. If arithmetic execution remains
poor, first identify a reliable shorter computed regime. Do not initiate causal
patching from weak behavioral performance or claim absence from a failed probe.
