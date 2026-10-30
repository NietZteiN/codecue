# Computation, context and copy readout calibration

This is a fresh discovery calibration prompted by the completed overnight relationship study. It changes the queried root's arithmetic and readout context while preserving its target value. It does not reopen earlier failed reliability gates, select a causal mechanism, train a language model, download a checkpoint or open sealed final outcomes.

Use the cached Llama3.1 8B Instruct and CodeLlama34B Instruct revisions already used in the project. Three fixed direct-output instructions are `routing_output_v1`, `routing_execute_v1` and `routing_value_v1`; preserve every instruction separately. All request a signed integer, use the same assistant-output prefix, greedy decoding,16-token ceiling and blank-line stop. Score the entire ASCII signed integer after whitespace trimming. Invalid, truncated and valid-wrong outputs remain visible, together with raw text and generated token IDs.

## Paired source design

Initialize four distinct roots. The queried source is initialized first; all24 root-initialization orders balance its actual variable slot. Four new copy variables leave the original roots available. Three declared copy graphs put the final copied leaf at depth1,2 or4 while retaining four copy assignments. They are fixed calibration constructions, not three independently discovered mechanisms.

For each numeric base, retain three forms: a literal queried-root value, a compact one-operation expression, and a larger cancellation expression. Only the queried root RHS changes; the other three roots remain literal. Both computed forms share the operator and operand-sign pattern and yield exactly the same root states and answer. Target magnitudes are1–8, compact operand magnitudes are at most16, and larger operands are13–32; the ranges partly overlap. Both computed forms can require cancellation. These are declared operand-regime packages, not a pure operation-count or magnitude intervention. The queried magnitude is absent from the computed operands and other roots' literals.

Retain all four question conditions:

- `arithmetic_only`: a single queried-root assignment followed by its readout. This is an isolated assigned-root calculation, not a naked expression or a proof that assignment context is absent.
- `roots_only`: all four initializations, then the preserved queried root.
- `full_root`: all initializations and copies, then the preserved queried root.
- `full_leaf`: the identical full program body, then the copied leaf with the same correct value.

The first two conditions are shared across copy topologies. The full-leaf minus full-root comparison holds the body and answer fixed; queried variable and definition recency still differ. Full-root minus roots-only measures a context/copy-body survival package. Arithmetic-only versus roots-only adds other assignments and distance. None of these behavioral comparisons directly observes an internal computation or proves a binding-specific causal effect.

Use numeric seeds401,503,607, two sign-mirrored draws and two lexical forms. The maximum logical grid is6,912 rows before source deduplication. There are72 root-order×topology units but only24 root-order clusters; all topology, numeric, sign, lexical, form, question and instruction relatives follow the same root-order TRAIN/DEV allocation,12 clusters per split. This is a familiar restricted-program calibration, not unfamiliar-structure confirmation.

Generate each unique source once per instruction and retain explicit mappings to all logical memberships. Nonzero isolated calculations must be source-disjoint across TRAIN and DEV. Shared literal isolated controls are explicitly allowed, reused, excluded from qualification and never counted as independent numeric generalization. Report logical rows, unique sources, unique prompts, overlap with prior source banks and every reuse count. Reject non-control source overlap required by the builder's exclusion contract; preserve prior scientific artifacts.

## Qualification and comparisons

Before any responses, fix the new gate to at least24 evaluated and24 unique prompts per required cell, accuracy at least90%, and invalid rate at most5%. Assess each instruction independently on TRAIN, then its separate numeric DEV cells. Cells are form×question×operator×answer-sign, pooling the prospectively balanced queried-slot, topology and lexical factors. All queried-slot/topology sensitivity cells remain visible descriptively. Exclude only literal `arithmetic_only` controls. A pass applies only to the declared balanced calibration population; no favorable instruction, topology, sign or form may rescue another failed cell or replace a historical gate.

The primary behavioral contrast is full-leaf minus full-root accuracy, separately for instruction, form, operator, answer sign and copy depth. Require exact paired membership, identical full bodies and equal expected answers. Bootstrap whole root-order clusters on DEV,2,000 draws, seed913, conditional on these fixed numeric/program templates and without multiplicity correction. Preserve all pairs; subsets conditioned on correct answers are not primary evidence. Do not attach independent-trial binomial intervals to reused control views. All short-context comparisons remain descriptive if shared controls prevent independent cluster attribution.

## Execution and provenance

Freeze generation and execution sources/configurations. Independently compare source traces and answers with ordinary Python before model work. Both native tokenizer/preparation jobs run through CPU SLURM, including CodeLlama's previously audited released BOS/SentencePiece boundary. The shared continuously batched vLLM BF16 CUDA12.9 runner uses exact prepared token IDs, prefix caching and hardware-appropriate batching. GPU execution depends on preparation and full software validation. Keep actual scheduler limits, uncapped usage accounting and resumable outputs.

Record scored unique cases separately from the backend's eight generation warm-up requests per successful invocation. Interrupted attempts retain conservative query bounds rather than claiming exact unjournaled request counts. Resumes require source/config/environment identity; orphan responses are rejected and interrupted tails are preserved before repair. Complete-backend publication recovery must not generate again.

Publish per-model audited cells, all fixed gates, prompt/response geometry, contrasts, unique/logical counts, runtime/cost accounting and a combined decision. A failed gate is a valid result. A successful narrower regime can motivate a later specified assay, but does not itself authorize computed causal interventions, a mechanism-C predictor, optional training or final-evaluation access.
