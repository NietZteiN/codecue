# Prepared counterbalanced diagnostic data

The [post-hoc review](diagnostic_review.md) found that the consumed arithmetic-free dataset tied trailing distractors to replicate parity. For nonzero answers, parity also determined magnitude. This prevents attribution of between-stratum accuracy differences to the distractor alone. It does not alter the completed cell counts or selection decision.

The continuation prepares a fresh numeric dataset with 384 matched pairs and 768 programs. It retains the original copy-depth/overwrite families, depths or update counts of one, two, four and eight, two or four initial literal bindings, and negative/zero/positive answer groups. Each base appears both with and without one dead trailing copy assignment. The assignment prefix and queried answer are identical within a pair, and both variants remain in the same numeric train/validation partition. Both distractor levels now occur at every answer magnitude.

The numeric seed is 2026102505. Prefixes and queries are deduplicated against the earlier prompt bank, difficulty ladder, arithmetic-form diagnostics and arithmetic-free diagnostics, including removal of previously present trailing distractors for the exclusion check. This prevents reuse of a previously consumed prefix/query under the other distractor condition. All 768 complete traces agree with ordinary Python execution.

These are unqueried future calibration candidates. They reuse task structures, provide no heldout structural confirmation and have no model accuracy results. Adding the trailing assignment changes length, query position and context; this is not a pure memory-delay intervention. Available-binding count also differs from the number of simultaneously output-relevant variables.

The inherited `available_bindings` field counts initial literal bindings. Fresh-copy chains introduce additional names, and the trailing statement introduces another. In two-initial-binding overwrite cases, the trailing copy repeats the queried value. Thus the paired intervention includes the effect of that value repetition; semantic irrelevance of the added assignment does not imply irrelevance to the model. Copy and overwrite families should not be treated as matched competition manipulations.

The final records have role `counterbalanced_followup_only`. This preparation does not lower the failed elementary-performance gate or execute experiments 4–10. Any subsequent analysis must retain pairing, distinguish readout protocols and use a separately specified inference/selection procedure. The previously consumed numeric-validation outcomes cannot serve as new confirmation.

Artifacts:

- `artifacts/binding/phase2/counterbalanced_followup.jsonl`
- `artifacts/binding/phase2/counterbalanced_followup.manifest.json`
- `artifacts/binding/phase2/counterbalanced_base.jsonl` and its generation manifest
- `artifacts/binding/phase2/diagnostic_review.json`, including exact paired outcome counts and input hashes
- `artifacts/binding/phase2_review_source.json`, the immutable generation/analysis source pointer

The generation command is CPU-only; it performs no tokenizer loading or model inference:

```bash
python scripts/96_binding_program.py build-counterbalanced configs/binding/phase2/counterbalanced_followup.json
```

Existing outputs refuse overwrites. Reproduction should use the saved source launcher and distinct output paths, retaining the exclusion manifests.

The accompanying distributed-readout checks now reject ambiguous slot maps, mismatched record IDs, duplicate cache sites, invalid layer indices, nonfinite activations and inconsistent canonical/surface renaming. Positions come from visible syntax; executed values do not choose them. Synthetic recovery and the tiny-network preflight test software behavior. They establish no empirical state-recovery or natural-use result.
