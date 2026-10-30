# Training-only prompt calibration

The original short-answer protocol is near floor on the main discovery cohort. Primitive checks reproduce arithmetic failures in FP32, so changing precision does not by itself make the task usable. This continuation compares two predefined readouts on the existing checkpoint; it does not replace earlier results or open final-test behavior.

`print_direct_v3` wraps the final expression in `print(...)`, asks for the printed integer, and continues an assistant `Output:` prefix. It uses at most 16 new tokens and the strict integer parser. `print_trace_v1` uses the same printed program, allows at most 256 new tokens of explanation, and requires an explicit final `Answer: <integer>` line. Its parser accepts only that final nonempty line; it never extracts an arbitrary number from the explanation. Blank lines stop the direct format but do not truncate the trace format.

The print wrapper leaves preceding assignments and the final expression AST unchanged. Shadowing the `print` builtin is rejected. Canonical program answers and assignment traces are independently checked in Python. The readout is a change in task syntax, and explicit reasoning changes computation. Neither is pooled with the original short-answer experiment. Original probes and causal results cannot be carried across automatically.

The first suite uses the same eight primitive fixtures and first four training neutral programs as the previous interface diagnostics. Both new variants run regardless of which performs better. Before opening their outcomes, the follow-up gate was fixed: a variant must parse all twelve outputs and answer at least seven primitive fixtures and two training programs correctly. If both pass, the direct format is preferred for continuity with short-answer measurement. This gate permits only a further training check, not a scientific mechanism claim.

Neither initial format passed. The explicit trace format answered most primitives but all four longer responses ended without the required final line. A separate `print_trace_long_v1` sensitivity holds prompts, cases and FP32 settings fixed and raises only the generation cap to 512. The gate is unchanged. Earlier results remain intact; this is one bounded token-budget check and does not silently reclassify truncated responses as semantic mistakes or successes.

The generated bank contains eight difficulty families: literal reads, addition, subtraction, overwrites, updates, two-binding outputs, copy dependencies and interleaved updates. Each family has equal negative, zero and positive answer counts. Literal zero cases vary the single queried variable name to avoid duplicate programs. All records have role `prompt_calibration_only` and split `train`. Structures repeat within families, and these records are not confirmatory data. The manifest records the seed, rejection proposals, counts, Python checks and content hash.

The conditional pipeline checks completion and the checkpoint identity before selecting a variant. It saves the selector summary hash, upstream run identity, immutable decision and effective configuration before collecting bank outcomes. Observed trace throughput motivated a declared balanced first subset: one program per family and answer sign, chosen by stable ID, for 24 model queries from the 96-record bank. This selection was specified before opening bank model outcomes. No qualifying variant means no bank-model inference. The one-hour CPU stage cap and job wall limit bound the bank check; an incomplete run remains explicitly incomplete.

```bash
python -m codecue.binding build-calibration-bank --output artifacts/binding/prompt_calibration_bank.jsonl
python -m codecue.binding calibrate-protocol --config configs/binding/protocol_calibration_fp32.json
python scripts/93_binding_calibration_pipeline.py configs/binding/protocol_training_bank_fp32.json
```

Use the immutable source launcher for scheduled runs. The submitted jobs and snapshot pointers are in `protocol_calibration_jobs.json`, `calibration_bank_jobs.json` and `long_calibration_jobs.json` under `artifacts/binding`; do not submit duplicates. These calibration stages completed, and both conditional bank decisions skipped inference because no variant passed. Raw responses, exact prompts, rendered source, token IDs, generation budgets and observed parameter dtype are retained. Passing a future training calibration would still require a separately frozen discovery run before any return to mechanism or final-prediction claims.
