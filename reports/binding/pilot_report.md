# Binding-study discovery pilot

This report is generated from recorded artifacts. Results concern one cached CodeLlama checkpoint. No primary explanation among H1–H5 or confirmatory claim has been selected.

## Behavioral feasibility

Model `codellama/CodeLlama-7b-Instruct-hf`, revision `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`; bfloat16, cpu, greedy `short_answer_prefill_v2` with an assistant `Answer:` prefix. The earlier unprefilled protocol produced explanations outside the strict integer parser; its interrupted run is retained separately and excluded here.

The completed balanced discovery subset has 720 responses across 60 bases and 38 parent-template clusters. Invalid outputs: 14. All six naming renderings and both primary/arithmetic tasks are retained.

| Task | Responses | Exact accuracy | Cluster bootstrap 95% interval |
|---|---:|---:|---|
| arithmetic_control | 360 | 3.1% | [0.0, 0.07895455852746616] |
| primary | 360 | 2.5% | [0.0, 0.06780624036979964] |

| Primary naming | Responses | Correct |
|---|---:|---:|
| neutral | 120 | 2 |
| informative | 120 | 3 |
| misleading | 120 | 4 |

Naming contrasts in this discovery sample do not establish equivalence. The larger subset preserves the primary 40/40/20 magnitude-bin mixture within every factorial cell. It overlaps some earlier smoke examples and is not an independent replication. Arithmetic-control performance also leaves arithmetic and output selection as live explanations.

| Compatible error label (nonexclusive) | Responses | Independent bases |
|---|---:|---:|---:|
| arithmetic_add_for_subtract | 12 | 3 |
| competing_variable | 62 | 16 |
| obsolete_assignment | 61 | 13 |

Ambiguous errors: 21. Compatible labels describe answers, not identified internal causes. Lexical relatives are not independent replications.

Behavior wall time: 2137.1 s; CPU forward/generation time: 2106.9 s. Raw responses, prompts, token IDs and exact identities are retained in the behavior directory.

### Prediction-prior control

Complete base prediction vectors are shuffled within family/load/update/split cells, retaining naming, lexical and task pairing. This measures accidental compatibility under the observed output prior. The reference bands are within-cohort permutation ranges, not population confidence intervals or significance tests.

| Task | Compatible label | Observed rate | Shuffled mean | Shuffled 95% reference range |
|---|---|---:|---:|---|
| arithmetic_control | arithmetic_add_for_subtract | 2.2% | 3.8% | 2.2%–5.6% |
| arithmetic_control | competing_variable | 0.0% | 0.0% | 0.0%–0.0% |
| arithmetic_control | obsolete_assignment | 9.2% | 7.6% | 5.0%–10.3% |
| primary | arithmetic_add_for_subtract | 1.1% | 0.4% | 0.0%–1.4% |
| primary | competing_variable | 17.2% | 15.3% | 10.6%–19.5% |
| primary | obsolete_assignment | 7.8% | 7.6% | 5.8%–9.7% |

The control uses 1000 permutations and 53 permutable bases; 7 singleton cells cannot vary. Numeric bases can share structural parents and prompt effects within a cell remain uncontrolled. Counterfactual matches resembling this output-prior reference do not establish binding interference.

## Representation measurements

Extraction completed on 1440 primary train/development renderings (480 bases), using 366,073,920 retained bytes. Probes use fixed-alpha ridge, train-only normalization, integer rounding and separate current/previous/multiset fits. All supplied sites and layers are reported; none is selected as a primary mechanism.

| Site | Block | Task | Hidden train / dev | Dev 95% cluster interval | Surface dev | Mode dev | Random-label dev |
|---|---:|---|---:|---|---:|---:|---:|
| last_assignment | 8 | current | 100.0% / 3.8% | [0.022916666666666665, 0.053125] | 5.5% | 3.5% | 2.6% |
| last_assignment | 8 | previous | 100.0% / 4.0% | [0.025, 0.05375] | 5.4% | 3.0% | 3.4% |
| last_assignment | 8 | multiset | 100.0% / 9.7% | [0.071875, 0.12291666666666666] | 5.7% | 4.2% | 3.3% |
| last_assignment | 16 | current | 100.0% / 5.6% | [0.038515625000000046, 0.07708333333333334] | 5.5% | 3.5% | 3.0% |
| last_assignment | 16 | previous | 100.0% / 6.0% | [0.04736842105263158, 0.07142857142857142] | 5.4% | 3.0% | 3.4% |
| last_assignment | 16 | multiset | 100.0% / 10.5% | [0.08541666666666667, 0.12604166666666666] | 5.7% | 4.2% | 3.7% |
| last_assignment | 24 | current | 100.0% / 5.4% | [0.04268229166666671, 0.065625] | 5.5% | 3.5% | 3.0% |
| last_assignment | 24 | previous | 100.0% / 4.5% | [0.031578947368421054, 0.05952380952380952] | 5.4% | 3.0% | 3.3% |
| last_assignment | 24 | multiset | 100.0% / 9.3% | [0.06875, 0.121875] | 5.7% | 4.2% | 3.4% |
| source_final | 8 | current | 95.9% / 4.2% | [0.025, 0.06356770833333318] | 4.2% | 3.5% | 1.6% |
| source_final | 8 | previous | 98.8% / 3.6% | [0.023748355263157897, 0.04880952380952381] | 5.2% | 3.0% | 1.0% |
| source_final | 8 | multiset | 99.8% / 3.3% | [0.021875, 0.046875] | 4.7% | 4.2% | 1.7% |
| source_final | 16 | current | 100.0% / 4.2% | [0.026041666666666668, 0.057291666666666664] | 4.2% | 3.5% | 2.5% |
| source_final | 16 | previous | 100.0% / 6.8% | [0.05454545454545454, 0.08157894736842106] | 5.2% | 3.0% | 2.7% |
| source_final | 16 | multiset | 100.0% / 5.8% | [0.046875, 0.07291666666666667] | 4.7% | 4.2% | 2.9% |
| source_final | 24 | current | 100.0% / 4.8% | [0.034375, 0.0625] | 4.2% | 3.5% | 2.1% |
| source_final | 24 | previous | 100.0% / 6.2% | [0.04473684210526316, 0.07857142857142857] | 5.2% | 3.0% | 2.5% |
| source_final | 24 | multiset | 100.0% / 5.6% | [0.03854166666666667, 0.07604166666666666] | 4.7% | 4.2% | 3.1% |

The table uses neutral training and neutral development. The complete JSON contains every within-condition fit and cross-condition transfer, MAE, whole-state scores, capacity and label priors. Intervals resample parent-template clusters and are descriptive, without correction for selecting among sites/layers. Random-label accuracy concerns a different target task and is not a paired improvement estimate. The surface baseline uses the same visible source prefix as each hidden site. Training scores are recomputed from saved weights, without refitting. A large train/development gap indicates weak generalization of this estimator on this small cohort; it does not establish an internal tracking failure. These measurements establish neither natural causal use nor information absence when decoding fails.

![All predeclared probe curves and controls](probe_curves.png)

Error bars are descriptive cluster bootstrap intervals for hidden decoding. Random-label control points concern separate tasks. All plotted sites and blocks were fixed before extraction.

### Fixed regularization sensitivity

The following grid changes the ridge penalty while retaining decoder capacity, extraction cache and train-only preprocessing. Every task, site and block is retained. The complete artifact also includes naming transfer, surface and randomized-label controls. This development sensitivity selects no primary site or penalty.

| Site | Block | Task | α=1 accuracy / MAE | α=100 accuracy / MAE | α=10000 accuracy / MAE |
|---|---:|---|---|---|---|
| last_assignment | 8 | current | 3.8% / 6.90 | 5.8% / 6.36 | 5.7% / 5.86 |
| last_assignment | 8 | multiset | 9.7% / 3.85 | 9.4% / 3.67 | 8.9% / 3.84 |
| last_assignment | 8 | previous | 4.0% / 6.89 | 4.5% / 6.63 | 5.1% / 6.03 |
| last_assignment | 16 | current | 5.6% / 5.65 | 5.3% / 5.58 | 6.5% / 5.63 |
| last_assignment | 16 | multiset | 10.5% / 3.53 | 10.1% / 3.48 | 9.7% / 3.82 |
| last_assignment | 16 | previous | 6.0% / 5.62 | 5.2% / 5.46 | 4.8% / 5.91 |
| last_assignment | 24 | current | 5.4% / 5.64 | 4.5% / 5.53 | 5.9% / 5.69 |
| last_assignment | 24 | multiset | 9.3% / 3.47 | 8.1% / 3.52 | 8.4% / 3.94 |
| last_assignment | 24 | previous | 4.5% / 5.91 | 6.5% / 5.68 | 4.8% / 5.98 |
| source_final | 8 | current | 4.2% / 10.25 | 5.0% / 6.54 | 6.5% / 5.43 |
| source_final | 8 | multiset | 3.3% / 6.54 | 8.0% / 3.95 | 10.2% / 3.51 |
| source_final | 8 | previous | 3.6% / 10.16 | 6.6% / 5.54 | 4.1% / 5.71 |
| source_final | 16 | current | 4.2% / 6.35 | 7.0% / 5.60 | 6.9% / 5.09 |
| source_final | 16 | multiset | 5.8% / 4.48 | 8.1% / 4.01 | 7.2% / 3.54 |
| source_final | 16 | previous | 6.8% / 5.54 | 5.8% / 5.22 | 7.4% / 5.18 |
| source_final | 24 | current | 4.8% / 6.69 | 5.6% / 5.68 | 7.7% / 5.15 |
| source_final | 24 | multiset | 5.6% / 4.64 | 8.2% / 4.26 | 7.1% / 3.48 |
| source_final | 24 | previous | 6.2% / 6.32 | 6.6% / 5.08 | 5.9% / 5.27 |

Regularization can improve a measurement estimator without establishing natural state use. The original fixed-penalty results remain the earlier experiment, and final-test outcomes remain sealed.

## Causal assay

This development calibration uses one predeclared block, computed donors and accumulator programs. Recipients were selected by stable ID within factorial cells rather than by successful patching. Late quantity queries can trigger reconstruction; full-residual transfer does not isolate a natural pathway.

| Control | Recipients | Counterfactual output | Dependent quantities | Independent quantities |
|---|---:|---:|---:|---:|
| matched_norm_random_direction | 4 | 0.0% | 25.0% | 16.7% |
| no_op | 4 | 0.0% | 25.0% | 16.7% |
| reciprocal_value_donor | 4 | 0.0% | — | — |
| same_answer_different_state | 4 | 0.0% | 25.0% | 16.7% |
| self_patch | 4 | 0.0% | 25.0% | 16.7% |
| shuffled_donor | 4 | 0.0% | 25.0% | 16.7% |
| value_donor | 4 | 0.0% | 50.0% | 16.7% |
| wrong_variable | 4 | 0.0% | 25.0% | 8.3% |
| wrong_version | 4 | 0.0% | 25.0% | 16.7% |

Complete likelihood margins, bootstrap intervals, baseline-correct counts and raw responses are retained. Self-patch responses exactly matched no-op in 4/4 comparisons. Ownership-matched intervention and path specificity are not established by this calibration.

## Reserved structural data

| Cohort | Bases | Renderings | Independent Python checks | Dataset SHA-256 |
|---|---:|---:|---:|---|
| depth | 300 | 3600 | 13264 | `7b126f69e362f7a6b3841cdac68d7a649942ee108d9310d09686154830ecfb82` |
| distance | 600 | 7200 | 21490 | `093471154d196fa060365adf67e26f6545da3ed1daf984485ef4703fc02c0a8c` |
| competition | 300 | 3600 | 24424 | `69f1bff8fe025624c1a25236b4fedffa2337b12381d5685f373db0c092529c2c` |
| combined | 150 | 1800 | 14714 | `12b696b2b4a6623b99fd84abb8e2667efad3948f8f52427b82e603d531d4334a` |

All these cohorts are test-only. Generator version 6 checks actual primary and control skeletons against the discovery dataset, verifies independent Python traces and downstream counterfactual states, and rejects cross-base duplicate numeric ASTs. Their model outcomes remain unopened. Increased competition uses six variables; distance padding adds arithmetic identities and is not a pure timing manipulation. The smaller structural smoke fixtures are separate from the full cohorts. No new-family extrapolation has been implemented yet.

## Arithmetic and interface calibration: CPU BF16

Eight fixed primitive programs and four training programs selected by ID use the same checkpoint and prompt. Expected values are independently checked in Python. Single-example and padded-batch generation are compared; no heldout outcomes are read.

| Batch size | Primitive correct / 8 | Training correct / 4 |
|---:|---:|---:|
| 1 | 5 | 1 |
| 4 | 5 | 0 |

Exact response agreement across batch sizes: 10/12. Primitive success does not establish competence on the complete task; batch differences require inspection before assigning errors to a mechanism.

## Arithmetic and interface calibration: CPU FP32

Eight fixed primitive programs and four training programs selected by ID use the same checkpoint and prompt. Expected values are independently checked in Python. Single-example and padded-batch generation are compared; no heldout outcomes are read.

| Batch size | Primitive correct / 8 | Training correct / 4 |
|---:|---:|---:|
| 1 | 5 | 0 |
| 4 | 5 | 0 |

Exact response agreement across batch sizes: 12/12. Primitive success does not establish competence on the complete task; batch differences require inspection before assigning errors to a mechanism.

## Arithmetic and interface calibration: GPU BF16

Eight fixed primitive programs and four training programs selected by ID use the same checkpoint and prompt. Expected values are independently checked in Python. Single-example and padded-batch generation are compared; no heldout outcomes are read.

| Batch size | Primitive correct / 8 | Training correct / 4 |
|---:|---:|---:|
| 1 | 5 | 1 |
| 4 | 5 | 0 |

Exact response agreement across batch sizes: 11/12. Primitive success does not establish competence on the complete task; batch differences require inspection before assigning errors to a mechanism.

## Matched backend comparison

The comparison verifies identical case IDs, source, oracle answers, unpadded input tokens, checkpoint, tokenizer, generation cap and inference source files. Scores are recomputed from raw responses. Only batch size, device and precision vary in the comparisons shown. Other captured source files and host environments can differ; this is not a controlled hardware benchmark.

| Left run / batch | Right run / batch | Exact raw matches / n | Parsed matches / n |
|---|---|---:|---:|
| CPU BF16 / 1 | CPU FP32 / 1 | 10/12 | 10/12 |
| CPU BF16 / 4 | CPU FP32 / 4 | 12/12 | 12/12 |
| CPU BF16 / 1 | GPU BF16 / 1 | 11/12 | 11/12 |
| CPU BF16 / 4 | GPU BF16 / 4 | 12/12 | 12/12 |
| CPU FP32 / 1 | GPU BF16 / 1 | 11/12 | 11/12 |
| CPU FP32 / 4 | GPU BF16 / 4 | 12/12 | 12/12 |
| CPU BF16 / 1 | CPU BF16 / 4 | 10/12 | 10/12 |
| CPU FP32 / 1 | CPU FP32 / 4 | 12/12 | 12/12 |
| GPU BF16 / 1 | GPU BF16 / 4 | 11/12 | 11/12 |

Primitive fixtures incorrect in every compared run and batch: `sanity:overwrite`, `sanity:subtraction`, `sanity:two_bindings`.

The observed primitive failures are not confined to CPU inference or BF16. Batch-sensitive longer answers remain visible in the artifact; deterministic greedy outputs are not independent replications. Agreement cannot rule out a shared adapter problem or identify a binding mechanism.

GPU device: NVIDIA A30; peak allocated tensor memory: 12.91 GiB. This excludes non-tensor device allocations.

## Independent generation reference

The same training-only prompts are decoded by direct full-prefix forward passes with `use_cache=False` and raw-logit argmax, without `model.generate` or the production generation wrapper. EOS and blank-line boundaries are explicit; every chosen token and top-two logit margin is saved.

Exact raw response matches with the earlier GPU batch-one run: 12/12; parsed matches: 12/12. This is an implementation sensitivity check on the same checkpoint and prompts, not a new accuracy cohort.

| Case | Expected | Cached baseline | Uncached reference | Stop |
|---|---:|---|---|---|
| `sanity:literal` | 7 | 7 | 7 | eos |
| `sanity:negative_literal` | -4 | -4 | -4 | eos |
| `sanity:addition` | 5 | 5 | 5 | eos |
| `sanity:subtraction` | 5 | -5 | -5 | eos |
| `sanity:overwrite` | 9 | invalid | invalid | blank_line |
| `sanity:update` | 7 | 7 | 7 | eos |
| `sanity:two_bindings` | -2 | -7 | -7 | eos |
| `sanity:copy_dependency` | 7 | 7 | 7 | eos |
| `002b344d1f3e0ed3fb8e6b68:primary:neutral:0` | -9 | -10 | -10 | eos |
| `016fad207d08134a448a48be:primary:neutral:0` | -10 | -1 | -1 | eos |
| `01858fed241f90d05dd9100b:primary:neutral:0` | 5 | -1 | -1 | eos |
| `018c17396acc735cccfd4755:primary:neutral:0` | -10 | -10 | -10 | eos |

Matching primitive failures across these paths narrow the implementation checks; they cannot validate the shared tokenizer, checkpoint or prompt interpretation. Any longer-program differences remain a cache/backend sensitivity and require inspection before causal claims.

## Training-only prompt calibration

The print readout wraps only the final expression. Direct-output and explicitly reasoned protocols are distinct experiments and are not pooled with each other or with the original behavior cohort. Only fixed primitive cases, existing training cases and the separate training-only calibration bank are eligible.

| Cohort | Variant | Responses | Primitive correct / n | Other training correct / n | Invalid |
|---|---|---:|---|---|---:|
| fixed suite | print_direct_v3 | 12 | 5/8 | 0/4 | 0 |
| fixed suite | print_trace_v1 | 12 | 7/8 | 0/4 | 4 |

| fixed suite | print_trace_long_v1 | 12 | 7/8 | 0/4 | 1 |

Passing the predeclared small-suite gate only permits a fresh training-bank check. It does not establish a binding mechanism or qualify final-test evaluation. Reasoning changes the computation; original prefix probes and interventions do not transfer automatically.

![Readout calibration with the same underlying training programs](calibration_readouts.png)

Cell text is the parsed integer; invalid output is shown separately. Token budgets and the use of explicit reasoning differ as labeled, so these are separate protocol measurements.

## Fresh training difficulty ladder

The [fixed plan](difficulty_ladder_plan.md) declares a new training-only calibration with both existing readouts. Within a depth, all three styles share assignment-result values, operation counts and answers. The independent-arithmetic control substitutes preceding values as literals, altering surface cues and functional dependencies. Twelve answer targets repeat across depths; these are not independent confirmatory programs. GPU BF16 results remain separate from earlier CPU FP32 prompt calibration.

Decision: `stop_no_usable_regime`; completed queries 240/240.

| Protocol | Style | Assignments | Correct / n | Invalid | Negative correct / n | Zero correct / n | Positive correct / n |
|---|---|---:|---:|---:|---:|---:|---:|
| print_direct_v3 | computed_baseline | 1 | 5/12 | 0 | 3/4 | 1/4 | 1/4 |
| print_direct_v3 | reassigned_chain | 2 | 1/12 | 0 | 1/4 | 0/4 | 0/4 |
| print_direct_v3 | fresh_chain | 2 | 1/12 | 0 | 0/4 | 0/4 | 1/4 |
| print_direct_v3 | independent_arithmetic | 2 | 6/12 | 0 | 3/4 | 0/4 | 3/4 |
| print_direct_v3 | reassigned_chain | 4 | 1/12 | 0 | 0/4 | 0/4 | 1/4 |
| print_direct_v3 | fresh_chain | 4 | 0/12 | 0 | 0/4 | 0/4 | 0/4 |
| print_direct_v3 | independent_arithmetic | 4 | 4/12 | 0 | 3/4 | 0/4 | 1/4 |
| print_direct_v3 | reassigned_chain | 8 | 1/12 | 0 | 1/4 | 0/4 | 0/4 |
| print_direct_v3 | fresh_chain | 8 | 0/12 | 0 | 0/4 | 0/4 | 0/4 |
| print_direct_v3 | independent_arithmetic | 8 | 4/12 | 0 | 2/4 | 0/4 | 2/4 |
| print_trace_long_v1 | computed_baseline | 1 | 8/12 | 0 | 2/4 | 3/4 | 3/4 |
| print_trace_long_v1 | reassigned_chain | 2 | 6/12 | 0 | 0/4 | 2/4 | 4/4 |
| print_trace_long_v1 | fresh_chain | 2 | 6/12 | 0 | 1/4 | 2/4 | 3/4 |
| print_trace_long_v1 | independent_arithmetic | 2 | 11/12 | 0 | 3/4 | 4/4 | 4/4 |
| print_trace_long_v1 | reassigned_chain | 4 | 4/12 | 0 | 1/4 | 0/4 | 3/4 |
| print_trace_long_v1 | fresh_chain | 4 | 4/12 | 0 | 1/4 | 1/4 | 2/4 |
| print_trace_long_v1 | independent_arithmetic | 4 | 12/12 | 0 | 4/4 | 4/4 | 4/4 |
| print_trace_long_v1 | reassigned_chain | 8 | 0/12 | 0 | 0/4 | 0/4 | 0/4 |
| print_trace_long_v1 | fresh_chain | 8 | 1/12 | 0 | 1/4 | 0/4 | 0/4 |
| print_trace_long_v1 | independent_arithmetic | 8 | 10/12 | 0 | 2/4 | 4/4 | 4/4 |

No regime passes the fixed arithmetic, parsing and nondegenerate chain-accuracy gate. The declared stopping rule ends this checkpoint/protocol feasibility pilot; no further prompt search or automatic intervention expansion follows.

![Training difficulty ladder](difficulty_ladder.png)

The one-assignment baseline is shared across curves. Invalid outputs count as incorrect in exact accuracy and appear separately in the lower panels. No population confidence intervals are inferred from these training cells.

## Decision and remaining work

The larger behavioral cohort is near floor, so full GPU expansion was stopped before allocation. The fixed training difficulty ladder also failed its predeclared gate. End this checkpoint/protocol feasibility pilot and preserve the result. A new scientific plan is needed for further model experiments. Current results do not justify a binding-repair or binding-interference claim. Probe generalization remains weak despite greater numeric diversity. A supported hypothesis, frozen predictor fitting and unfamiliar-program forecasts are still required before opening final model outcomes. No optional training, second checkpoint or empirical paper abstract has been started.

Queued-job identities and immutable source pointers are recorded in the adjacent handoff and artifact manifests. GPU experiment time remains subject to the shared four-hour ledger; CPU results are kept separate from any GPU replication.

## Later authorized experiment program

The user subsequently authorized a [ten-experiment follow-up](experiment_program.md). It audits the cached checkpoint, corrects an instruction-marker tokenization mismatch and runs fresh arithmetic and arithmetic-free diagnostics. That correction restores reference input IDs; it does not resolve the observed primitive failure. These new results remain separate from the native-tokenization pilot above. See the linked stage table for completed and unexecuted experiments.
