# Reference tokenizer audit and correction

The user authorized the proposed ten-experiment program after the earlier pilot stopped. Experiment 1 compared the cached files and tokenizer against public primary references. The results are separate from the earlier pilot in `artifacts/binding/phase2/`.

All nine audited files, including both weight shards and the tokenizer artifacts, match the public metadata for the exact pinned checkpoint revision. The audit uses streaming SHA-256 for LFS files and Git object SHA-1 for ordinary files. No model weights were downloaded or modified.

The native serialized prompt begins with `<s>[INST]`. Under the installed tokenizer, the opening bracket after BOS is token 29961. Meta's [single-turn renderer and encoder](https://github.com/meta-llama/codellama/blob/1af62e1f43db1fa5140fa43cb828465a603a48f3/llama/generation.py#L335) prepend BOS to raw SentencePiece encoding, which produces token 518 at that position. The [reference tokenizer](https://github.com/meta-llama/codellama/blob/1af62e1f43db1fa5140fa43cb828465a603a48f3/llama/tokenizer.py#L36) defines that encoding boundary.

Earlier tests compared our generation and layout tokenizer paths with each other; they missed this reference mismatch. The new audit closes that gap. An explicit space between serialized BOS and `[INST]` makes the complete input IDs match the raw SentencePiece reference. Both existing printed readouts matched on every fixed audited case. Every saved prompt from the fresh arithmetic and arithmetic-free diagnostics also passed the complete token-ID audit.

The live adapter now uses the correction by default for CodeLlama and validates complete prompt IDs against cached SentencePiece before inference. New experiment configurations also name `codellama_official_boundary_v1` explicitly. `tokenization_mode: native` remains an explicit reproduction control. Historical source snapshots preserve the earlier implementation and recorded outputs; they are not silently rewritten or pooled with corrected-input runs.

A paired same-GPU experiment runs native and corrected inputs on the same fixed fixtures, precision and batch sizes. The primitive accuracy is unchanged. Thus, correcting this integration mismatch is necessary for reference fidelity but does not explain away the observed primitive failures. The fresh diagnostics still fail the saved elementary-performance selection rule.

The new program report lists experiments 4–10 as unexecuted because their scientific prerequisites are unmet. The user authorized the second model family, but no stable selective effect exists to replicate under experiment 10's stated rule. No extra checkpoint was loaded, no mechanism or C feature was invented, and final model outcomes remain sealed.

The arithmetic-free diagnostics distinguish a shallow copy success from unreliable overwrites and deeper copies. These are descriptive observations on consumed diagnostic data. A future redesign could study that contrast with a new plan and fresh validation; the current gate is not lowered after observing outcomes.

Software preparation also adds a syntax-assisted distributed readout: latest visible definition-ending vectors are projected to one hidden width using fixed slot-specific signed permutations. Surface controls receive the same slot/position assistance. It supports the existing ridge, majority and randomized-label comparisons without using execution labels to choose positions. Synthetic tests and the tiny-network preflight validate the implementation; no empirical experiment 7 result is claimed.

Artifacts include `checkpoint_audit.json`, `tokenizer_boundary_audit.json`, `boundary_validation/comparison.json`, `all_prompt_token_audit.json`, both diagnostic run manifests and the machine-readable `program_status.json`. See the generated [experiment program report](experiment_program.md) for complete cell counts and stage status.
