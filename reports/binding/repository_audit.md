# Repository and resource audit

Inspected October 24, 2026 (America/Chicago). Requirement source: `../../../dependvar.txt`, version 2026-10-25. This is a new study implementation, not a result from the existing manuscript.

## Existing assets and scientific difference

The workspace contains several independent Git repositories. Work belongs in `codecue/`, whose starting revision is `39c9e6600feb14a45d473395a5efc848ac37c47f`. The working tree was clean before this task. No AGENTS.md was found in the ancestor chain or project. Read `CLAUDE.md`, inherited cluster guidance in `../probing/CLAUDE.md`, README, model/compute configuration, model runner, span layout, cache, probes, patching, statistics, and the existing manuscript and `paper/ARGUMENT.md`.

The existing paper, *Misleading Identifiers Change What Code Traces Write*, studies length-versus-sum name conflicts, recoverable correct digits on erroneous trace writes, span interventions, and demonstrated expression formats. It documents that original probes had program overlap and uses disjoint follow-ups. Its evidence is not imported into this dataset or presented as evidence for binding interference.

The proposed addition is a restricted integer execution environment with several current bindings, explicit assignment versions, output-relevant competition, computed value-multiset controls, functional counterfactual labels, and structurally grouped prediction tests. Whether any model error is explained by a binding mechanism remains open. No prior empirical table or paper text was changed.

Reuse: `codecue.models.generate_free`, `codecue.layout.Span/spans_to_tokens`, `codecue.patching.decoder_layers`, `codecue.stats.bootstrap_ci`, and the existing SLURM submission/environment tools. New code is a subpackage, `src/codecue/binding/`, invoked as `python -m codecue.binding`; it is not a separate project or model-training framework. The new loader pins revisions and captures raw decoder block outputs, avoiding ambiguity about the final normalized hidden state.

## Checkpoint and dependencies

Use the repository's established default, `codellama/CodeLlama-7b-Instruct-hf`, with model and tokenizer commit `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`. The checkpoint and tokenizer are in the existing shared Hugging Face cache. Loading is local-files-only; no checkpoint downloads or paid resources are requested.

Existing environment: `../envs/probe-cu129/bin/python`, Python 3.12.14, torch 2.11.0+cu129, transformers 5.14.1, numpy 2.3.5, pytest and PyYAML already installed. No dependency installation or lock changes were necessary. Generation and independent validation use Python's standard library; measurement/statistics use the existing numpy/torch stack.

## Hardware and budget

The current CPU node has no visible CUDA device; `nvidia-smi` fails and `torch.cuda.is_available()` is false. SLURM is available. GPU partitions exist but their GPUs were allocated during inspection. The initial H100 smoke request was pending with reason `Resources`, with a scheduler estimate on October 25, not immediate capacity. The CPU `dev` preflight can run without reserving a GPU.

GPU work uses sbatch, one cached checkpoint, one GPU, and a shared four-hour ledger (`artifacts/binding/gpu_budget.json`). The pipeline profiles a balanced smoke before estimating the larger discovery run. It has a 13,800-second internal limit and a 3:55:00 SLURM wall limit. A balanced subset is selected if the estimated complete discovery pilot exceeds the remaining budget. The final holdout is not scheduled automatically. Activation extraction checks storage against 64 GiB and writes one bounded sample chunk at a time; no activation experiment has run at audit time.

See `handoff.md` and the current job manifests for final validation and queue status. Queue estimates are advisory, not promises of a start time.
