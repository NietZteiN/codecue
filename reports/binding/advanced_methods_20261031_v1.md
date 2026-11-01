# From descriptive probes to discriminating mechanisms

Follow-up: the [October 31 probing literature search](probing_literature_review_20261031_v1.md)
adds 23 annotated primary papers and six ranked experiment proposals. It makes
alternative-semantic controls and conditional probing explicit additions, and
revisits the original binding paper's evidence for query-dependent routing.
No new experiment is submitted by the literature review.

October 31, 2026. The current linear, low-rank and shallow nonlinear readouts
are useful baselines. Their main limitation is inferential: a decoder can learn
a calculation from information in a state, while an unsuccessful decoder can
miss the model's code. Neither outcome identifies how the model works.

## Competing explanations to separate

| Explanation | Distinguishing prediction | Critical control |
|---|---|---|
| Numbers use a smooth/modular code | Natural circular targets transfer better than permuted geometry | Same dimension, input features, folds and regularization grid; source comparator |
| Multiple bindings share reusable slots | One shared variable-conditioned readout transfers across names, order and slot count | Leave names/order/count out; permutation tests; query-only and source-only controls |
| State is distributed across tokens | Multi-site readout beats one final-query vector | Match capacity and visible source; avoid oracle routing in the primary test |
| States update after writes | Values emerge after computation and overwritten values become obsolete | Native token alignment, operand-mutation pairs, unrelated writes and equal-value overwrites |
| Relations are available without absolute values | Direct relation readout transfers where reconstructed values fail | Class balance, joint confusion, algebraic closure and unseen-family evaluation |
| A rich decoder learns an interpreter | Accuracy rises mainly with decoder/data complexity and also with source features | Sample efficiency, calibrated grouped MDL, capacity-matched source model |
| Readout tracks the answer the model will give | Decoded model-implied value predicts errors beyond task difficulty | Separate correct vs generated-answer labels; out-of-family behavior prediction |

These are hypotheses, not established mutually exclusive architectures. Query
format can change when computation occurs, and several mechanisms may coexist.

## Ordered methods and evidence requirements

**1. Geometry-aware readouts — implemented in the new discovery wave.**
Our one-hot digit baseline did not test circular digit targets. The
[controlled protocol](arithmetic_numeric_geometry_plan_v1.md) compares signed
decimal circles, coprime residue circles, dimension-matched permuted circles
and ordinal thresholds on the same cached definition states. The
[digit-representation paper](https://arxiv.org/abs/2410.11781) motivates this
comparison; its numerical task and decoding rule differ from this adaptation.
An improvement motivates transfer tests, rather than establishing a neural
arithmetic mechanism. Existing simple baselines remain the reference.

**2. Shared variable-conditioned and permutation-equivariant readouts — proposed.**
Instead of a separate unconstrained head per variable, learn a shared map from
a state plus an explicitly specified variable query into a binding/value slot.
Compare bilinear/low-rank slot models with matched independent-head and source
models. A set-valued version should change outputs consistently under variable
permutations. Hold out names, declaration positions and eventually numbers of
variables, not merely random rows. Declare whether the query uses lexical
features, mention activations or privileged oracle identity. Query-only
predictors test how much information the query itself exposes.

[Feng and Steinhardt's binding work](https://arxiv.org/abs/2310.17191) studies binding
IDs in a different setting. The April 2026
[Slot Machines preprint](https://arxiv.org/abs/2604.21139) motivates shared-slot
tests and distinguishes decodability from retrieval use. Applying either
mechanism to versioned assignments is our hypothesis. Do not interpret useful
slots as literal neural registers, or allow gold parent pointers in the primary
global-state test. First extract and test the pure final-query vector.

**3. Temporal transfer and counterfactual state geometry — planned.**
Measure cross-position/layer transfer: fit after one write, test at later use,
after distractors, after overwrite and before answer generation. Keep native
RHS/newline/query token identities explicit; coincident tokens do not constitute
separate time steps. Paired programs differ in one operand or write, with
canonical structural closure keeping relatives together. Ask whether predicted
changes track the changed variable, downstream dependents and relations while
leaving unrelated variables stable. Representational similarity can compare
versioned graph/state models, but pairwise distances are not independent samples;
infer over held-out structural families. The
[existing next-run plan](arithmetic_next_runs_20261031_plan_v1.md) specifies the
data, timing and query-scope preparation. New geometry is an addendum.

**4. Complexity-aware evaluation — proposed after calibrated outputs.**
Report learning curves and proper scoring rules as well as exact accuracy.
[MDL probing](https://aclanthology.org/2020.emnlp-main.14/) measures how readily
a decoder learns a property, rather than ranking representations by accuracy
alone. Implement grouped prequential code length only after TRAIN-only
probability calibration. Every prefix must select hyperparameters using its
own labels; full-TRAIN selection would leak future blocks. Repeated lexical
and numerical relatives do not provide independent coding evidence. Our current
nearest-template energies are not probabilities, and we have not implemented
MDL or measured calibrated uncertainty in this new wave.

**5. Distributed causal alignment — gated future experiment.**
[Distributed Alignment Search](https://proceedings.mlr.press/v236/geiger24a.html)
learns an alignment using high-level interchange interventions. For our task,
swap a candidate variable-version subspace between naturally occurring,
token-aligned donor programs and test the exact counterfactual downstream
answer. Compare equal-value donors, unrelated variables, random subspaces and
unmodified activations; reserve structural families for transfer. First verify
the model's behavioral competence and stable readout/localization. A successful
steering operation alone does not establish natural causal use. Backbone
weights remain frozen and existing intervention gates remain in force.

**6. Correct state versus model-implied state — planned behavior analysis.**
Separate a decoder trained on oracle values from one predicting the model's
generated answer. Test whether their disagreement predicts errors beyond
source-only difficulty, output confidence and majority priors. This follows
the distinction in [Probing for Arithmetic Errors in Language Models](https://arxiv.org/abs/2507.12379),
whose arithmetic tasks differ from these versioned-variable programs. New
family separation and calibration are needed before making an error-prediction
claim. Do not reuse inspected DEV as independent confirmation.

## What will count as progress

A strong result narrows the competing explanations: for example, a reusable
readout that transfers to unseen names and positions, changes only the correct
version after a controlled write, and predicts the corresponding counterfactual
effect. Merely finding a larger decoder with better DEV accuracy is a discovery
lead. The immediate wave tests geometry and prepares global vectors; it does
not implement slot models, MDL, new behavioral evaluations or causal alignment.
