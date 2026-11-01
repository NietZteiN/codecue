# Probing literature: methods we can test next

Reviewed October 31, 2026, America/Chicago. This is a targeted methods search
for CodeCue's variables, assignment versions, dependencies, numerical values
and algebraic relationships. It extends the [October 27 source reviews](source_review_r1_r4.md)
and [earlier methods roadmap](advanced_methods_20261031_v1.md). It is not an
exhaustive systematic review or a novelty claim. Primary papers support the
method descriptions below; proposed CodeCue adaptations are our inferences.
Reading depth and access limitations are recorded in the
[source register](../../artifacts/binding/literature/probing_methods_20261031_review_v1.json).

## The main methodological decision

Specify the question before choosing a probe:

| Question | Appropriate evidence | Insufficient evidence |
|---|---|---|
| Is information recoverable? | A decoder that transfers to independent program families; compare several decoder classes | One unsuccessful linear readout |
| Is information readily accessible? | A restricted decoder, learning curves, controls and probabilistic code length | The best accuracy after an unrestricted search |
| Does the model use it? | Specific counterfactual effects, selective ablations and behavioral transfer | Decodability or changing the probe's prediction alone |

These questions explain the apparent disagreement between P01's selectivity
criterion and P02's preference for a strong decoder: the papers operationalize
different aspects of representation quality. We should keep a simple readout
as an accessibility reference and a controlled nonlinear readout as an
availability test. Neither directly identifies natural computation.

## Annotated primary-source reading list

Every application or priority in the last column is our proposed adaptation.
The source register distinguishes selected full-text reading from abstract-only
screening; no paper's code or empirical result was independently reproduced.

| ID and paper | What the paper contributes | Application and limit for CodeCue |
|---|---|---|
| **P01. Hewitt & Liang, EMNLP 2019 — [Designing and Interpreting Probes with Control Tasks](https://aclanthology.org/D19-1275/) [abstract/introduction]** | Compare task performance with randomized type-level control labels; probe expressivity affects selectivity. | Retain coherent-family controls and add stable name/version controls where identifiable. Our family derangement is an adaptation, not their word-type control. Random-label chance does not establish causal use. |
| **P02. Pimentel et al., ACL 2020 — [Information-Theoretic Probing for Linguistic Structure](https://aclanthology.org/2020.acl-main.420/) [abstract/introduction]** | Under their mutual-information objective, a better predictive probe provides a tighter estimate, including when nonlinear. | Add one prespecified nonlinear availability comparator. Computational accessibility and causal use remain separate; a deterministic representation cannot create Shannon information absent from the source. |
| **P03. Voita & Titov, EMNLP 2020 — [Information-Theoretic Probing with Minimum Description Length](https://aclanthology.org/2020.emnlp-main.14/) [§2 and online-code method]** | Evaluate label code length, accounting for predictive quality and learning effort; online coding trains on growing prefixes. | Grouped learning curves first, then prequential probabilistic coding. Keep relatives in the same block and prohibit using later-block labels for hyperparameters. Exact accuracy is not code length. |
| **P04. Hewitt et al., EMNLP 2021 — [Conditional probing: measuring usable information beyond a baseline](https://aclanthology.org/2021.emnlp-main.122/) [§2]** | Compare a probe on baseline plus representation with one on baseline plus a constant, rather than subtracting two standalone accuracies. | Test what hidden states contribute beyond public source/position features. Fix the function class and input access. This estimates usable prediction beyond a baseline, not newly created information. |
| **P05. Ravichander, Belinkov & Hovy, EACL 2021 — [Probing the Probing Paradigm](https://aclanthology.org/2021.eacl-main.295/) [abstract]** | Properties can be decodable even when unnecessary for a model's task. | Include live and dead variables and vary query relevance. A dead variable being decodable does not show it participates in execution. |
| **P06. Hewitt & Manning, NAACL 2019 — [A Structural Probe for Finding Syntax in Word Representations](https://aclanthology.org/N19-1419/) [abstract/§2 setup]** | Learn a transformation whose squared distances and norms reflect tree distances and depths. | Add graph-geometry diagnostics alongside directed edge readouts. Our versioned dependency graphs are DAGs with multiple parents, not syntax trees; symmetric distances cannot recover direction or operand role by themselves. |
| **P07. Troshin & Chirkova, BlackboxNLP 2022 — [Probing Pretrained Models of Source Codes](https://aclanthology.org/2022.blackboxnlp-1.31/) [abstract]** | Diagnostic tasks separate code structure, identifiers/namespaces and harder semantic properties. | Preserve separate binding, dependency and arithmetic endpoints. Success on identifier or structural tasks cannot substitute for semantic-state recovery. |
| **P08. Jin & Rinard, ICML 2024 — [Emergent Representations of Program Semantics](https://proceedings.mlr.press/v235/jin24e.html) [arXiv v3, §§3–4]** | Hold captured states fixed, re-execute programs under changed operation meanings, and train probes for the alternate traces. Their grid-world experiments distinguish original semantics from alternatives. | **High priority:** original versus alternative-semantics targets on the same cached states. Match label difficulty and test several operation permutations. This changes target semantics, not numerical code geometry or model activations. |
| **P09. Jin & Rinard, 2024 — [Latent Causal Probing](https://arxiv.org/html/2407.13765v2) [§§2–4]** | Formalize latent program states using causal models of the data, bound/free outcomes and validity conditions on alternate baselines. | Use our executor to define explicit competing target dynamics. We do not know the pretrained LMs' complete training-data causal model, so their identification result does not automatically apply to our generator. |
| **P10. Wu, Geiger & Millière, ICML 2025 — [How Do Transformers Learn Variable Binding in Symbolic Programs?](https://proceedings.mlr.press/v267/wu25j.html) [§3; Appendix J revisited]** | Their task-trained model supports causal routing through assignment chains despite weak single-vector linear decoding of complete program state. | **High priority:** test global state against query-dependent, distributed retrieval. The paper was already in our original review. Its constant/copy programs and small trained model do not establish the mechanism in our arithmetic/overwrite tasks. |
| **P11. Feng & Steinhardt, ICLR 2024 — [How do Language Models Bind Entities in Context?](https://arxiv.org/html/2310.17191v2) [abstract/§§3–4 structure]** | Study binding-ID representations and entity–attribute association. | Compare lexical identity, declaration position, assignment version and current value as distinct targets. Binding IDs are a hypothesis to test, not an established explanation of our versioned variables. |
| **P12. Bogdan & Lindsey, 2026 preprint — [Slot Machines](https://arxiv.org/html/2604.21139v1) [§2.1]** | Use shared slot classifiers and entity-specific routing; distinguish decodable entity information from retrieval use. | Shared variable-conditioned decoding is promising. Their per-entity routers are not a demonstrated name-invariant mechanism; our shared query encoder and name/order/count transfer tests would be additional work. |
| **P13. Lepori, Serre & Pavlick, COLM 2024 — [Uncovering Intermediate Variables using Circuit Probing](https://arxiv.org/html/2311.04354v3) [§§2–4; Appendices H–I/Q]** | Optimize sparse masks over frozen weights to find component updates associated with hypothesized intermediates; evaluate by classification and targeted ablation. Some probe-targeted embedding edits fail to produce correct counterfactual behavior. | Later, compare alternative arithmetic intermediates, including algebraically equivalent decompositions. Requires new masked forwards and intervention controls; it cannot run from residual caches alone. |
| **P14. Geiger et al., CLeaR 2024 — [Distributed Alignment Search](https://proceedings.mlr.press/v236/geiger24a.html) [publisher abstract/method summary]** | Learn distributed alignments to high-level causal variables using interchange interventions. | Gated comparison of variable-version or relation subspaces. Held-out donor/recipient families, natural donors, unrelated variables and exact counterfactual answers are required. Steering success alone is weaker than natural-use evidence. |
| **P15. Elazar et al., TACL 2021 — [Amnesic Probing](https://aclanthology.org/2021.tacl-1.10/) [abstract/§2 controls]** | Remove recoverable information and measure behavioral change, including random-removal and label-restoration controls. | A complementary necessity test after localization. Collateral removal, distribution shift and redundant encodings complicate both positive and negative outcomes. |
| **P16. Belrose et al., NeurIPS 2023 — [LEACE](https://arxiv.org/html/2306.03819v4) [abstract/§7]** | Closed-form erasure prevents linear classification of a specified concept under the paper's conditions while minimizing specified distortion. | Prefer as a controlled linear-erasure baseline over repeatedly projecting away classifier directions. Linear removal does not guarantee nonlinear removal or property-specific causal isolation. |
| **P17. Dobrzeniecka et al., Findings ACL 2025 — [Improving Causal Interventions in Amnesic Probing](https://aclanthology.org/2025.findings-acl.674/) [abstract/§2]** | Compare INLP with mean projection and LEACE; targeted removal and restoration controls improve interpretation in their tested settings. | Retain random-rank/removal and rescue controls. These results do not guarantee selective erasure of one assignment version in our models. |
| **P18. Levy & Geva, NAACL 2025 — [Language Models Encode Numbers Using Digit Representations in Base 10](https://arxiv.org/html/2410.11781v2) [§3]** | Probe individual digit circles and test interventions in their numerical setting. | Our circular-code wave already adapts this idea. Signed computed values, bounded joint template decoding and our controls differ from their literal-number assay; do not label it a direct replication. |
| **P19. Sun, Stolfo & Sachan, EMNLP 2025 — [Probing for Arithmetic Errors](https://aclanthology.org/2025.emnlp-main.411/) [§2.2/abstract]** | Decode correct and model-predicted arithmetic outputs separately; compare circular, linear, logistic and nonlinear readouts and use internal signals for error detection. | Separate oracle state from model-implied state. Match activation site and answer-token availability; test behavior prediction beyond source difficulty and output confidence on new families. |
| **P20. Gurnee et al., TMLR 2023 — [Finding Neurons in a Haystack](https://arxiv.org/html/2305.01610) [§3; Appendix B.3–B.4]** | Vary the number of selected neuron coordinates with sparse linear probes and compare feature-selection methods. | Add sparse-coordinate/rank curves as a localization diagnostic. Residual coordinates are not automatically individual neurons or monosemantic features. Do not prioritize an expensive exact subset solver before cheaper methods show value. |
| **P21. Klubička & Kelleher, BlackboxNLP 2022 — [Probing with Noise](https://aclanthology.org/2022.blackboxnlp-1.34/) [abstract/limitations]** | Perturb geometric properties to separate information carried by vector norm and direction in their embedding experiments. | A cheap norm-only, direction-only and matched-noise control on cached vectors. Such perturbations diagnose a readout; they do not by themselves identify neural causal mechanisms. |
| **P22. Barin-Pacela et al., UAI 2026 — [Stop Probing, Start Coding](https://proceedings.mlr.press/v337/barin-pacela26a.html) [publisher abstract only]** | In their superposition benchmarks, iterative sparse inference improves compositional transfer relative to linear and amortized SAE inference. | A conditional follow-up if our transfer results suggest superposition. We have not established sparse-factor ground truth in these states. The publisher-linked PDF was not retrievable through the browser, so implementation details remain unreviewed. |

**Early-stage radar, P23:** Yoo & Skapars, 2026 preprint,
[Probe Generalization as Subspace Selection](https://arxiv.org/html/2609.02893),
§§3–5. In a single-model deception setting they compare PCA-subspace selection,
including target-informed oracle analyses and source-only interpretation-based
selection. Our possible adaptation is TRAIN-only PCA/stability selection against
full and random subspaces. Never select components using confirmation labels;
their target-informed results are oracle diagnostics. This is neither a causal
result nor demonstrated arithmetic transfer. The landing record's submitted
month and identifier prefix are inconsistent; this review uses the displayed
year only and does not infer a month or verified venue.

## Ranked experiments for this project

The following are proposals, not newly executed experiments. The current
geometry wave and previously planned global-state baseline remain intact.
Each item needs an executable frozen protocol before launch.

### E1. Alternative-semantic controls on fixed cached states

**Question:** does a readout preferentially recover the program's normal
semantics, or can it learn equally well to calculate arbitrary alternate traces?

Start with a declarative swap of the meanings of existing binary operators,
while keeping the program text, initial values, captures and family splits
unchanged. Execute both semantics independently to make labels. This differs
from our circular-label permutations: those change the output code for the same
true value; here the trace itself changes.

Run the same readout families on normal and alternate values/relations; compare
paired family differences and matched source comparators. Audit target entropy,
sign, magnitude, depth, literal copying and class support. Changing operators
can leave the current bounded domain: do not clip, wrap or discard rows after
looking at performance. Use a predeclared scalar target or a cohort/domain
valid under every selected semantics, with acceptance counts reported. An
alternate semantic baseline must be comparably learnable; a harder target
distribution is not evidence of model semantics. Multiple operator maps and a
positive control that exposes the input program are needed before inference.

**Interpretation:** a robust preference for ordinary semantics would narrow a
source-record/learned-interpreter explanation. It would not independently
identify a causal neural circuit or meet P09's pretraining-SCM assumptions.
This is the highest-priority addition because labels can be prepared without
new LM forward passes.

### E2. Global state versus query-dependent retrieval

**Question:** is the model maintaining all current values, routing only the
queried value, or combining these strategies?

Finish the already planned cached final-query-vector comparison as a baseline.
Then use paired single-variable queries, all-variable queries and unrelated
queries on the same program. Compare a pure final vector, independently
specified earlier token sites and a capacity-matched multi-site readout.
Record readout access explicitly: a state plus several mention activations is
a different assay from a single-vector global-state claim.

Probe before the query, after the query and at native answer preparation;
include latest and superseded assignment versions, dead variables, distractors
and unrelated writes. Preserve token alignment rather than treating identical
RHS/newline token positions as different times. Label relevance changes must
not masquerade as a newly computed value. Query-specific improvement alongside
weak complete-state recovery would be consistent with retrieval, not proof of
the exact routing mechanism. P10 motivates this contrast; its broader-model
transfer is our hypothesis, and it was already in the original bibliography.

### E3. Conditional probing beyond source and position cues

**Question:** what extra prediction becomes accessible when hidden states are
added to a public baseline?

Fit matched predictive models on `[baseline, hidden]` and `[baseline, zero]`.
Use fixed input widths and the same selection procedure; also retain baseline
alone and hidden alone. Begin with statement/declaration position, lexical
identity features and source-hash features, never oracle parent pointers or
true values in the primary assay. For probabilistic targets compare held-out
cross-entropy (in bits), with accuracy as a second endpoint. An observed
negative gain is reported, not truncated away.

This is the conditional-usable-information adaptation of P04. It does not claim
new Shannon information beyond a complete deterministic program. Joint access
may simply make its semantics easier for the selected function class. Include
matched noise/random-feature additions to diagnose finite-sample capacity
effects, and family-held-out calibration before describing NLL as uncertainty.

### E4. Shared queries and structured relationship heads

**Question:** do names, versions, values and relationships admit a reusable
representation, rather than independent memorized output heads?

Compare independent heads with a shared low-rank/bilinear query-conditioned
decoder. A query encoder specifies which variable is requested; a shared bank
predicts values. An optional routed-slot model follows P12, but replacing its
per-entity routers with a shared encoder is our extension. Report query-only,
position-only, source-only and independent-head controls. A contextual mention
query may itself contain the value, so declare that access and test it alone.

For dependency targets use directed, operand-typed edges between assignment
versions. A metric-distance probe inspired by P06 is auxiliary, since our
graphs have multiple parents. For semantic relationships use shared pair and
triple queries: ordering/equality for `(x,y)` and predicates such as `z=x+y`
for `(x,y,z)`. Ensure semantic relations are not synonymous with the printed
assignment pattern: include relations that hold without being explicitly
written, and structural distractors. Train/evaluate raw relation heads before
any consistency repair or symbolic solver, whose contribution must be reported
separately. Report class balance, exact whole-graph/state recovery and
consistency, not only per-edge or per-class averages.

Hold out names, declaration orders, query roles, program families and eventually
variable counts. Mask non-existent slots. Keep all relatives and all queries
for a program in one canonical component. Equivariance is an architectural
property to verify under permutations, not a label to attach to any multihead
network. This item is the main architectural upgrade, but requires a clean
target/access contract before implementation.

### E5. Complexity, geometry and learning-effort comparisons

**Question:** are failures caused by decoder mismatch, limited sample size,
compression, or absent transferable signal?

Use a small declared comparison of linear, bilinear and shallow nonlinear
readouts; sparse-coordinate, rank/PCA and random-projection controls; and
norm-only/direction-only ablations. Select features and all preprocessing inside
TRAIN folds. A PCA fit using DEV is transductive access even without its labels.
Weight sharing and parameter counts should be explicit rather than assuming
equal hidden widths imply equal capacity. Current circular/ordinal fits remain
useful existing panels; the literature does not justify repeated unrestricted
architecture sweeps until one improves familiar DEV.

Use stratified structural-family learning curves, then prequential codes on
growing TRAIN blocks. NLL requires actual probability models: our nearest-code
energies are not calibrated probabilities. Fix or select hyperparameters and
calibration using only each available prefix. Lexical repetitions do not make
independent evidence; report code length per family and per scored target with
within-family dependence explicit. MDL is a coding criterion, not a causal
test, and manual parameter count alone is not its implementation.

P22 motivates considering iterative sparse inference only after evidence of
compositional superposition and review of its full method. Training a large SAE
is not the first recommended response to weak value probes.

### E6. Causal arithmetic model comparison, after the existing gates

**Question:** which of several algebraically valid intermediates is used in
the model's computation?

An example contrast is `a*a - b*b` versus `(a+b)*(a-b)`: the mathematical result
agrees but the intermediate variables differ. P13 provides a close precedent;
identifying these alternatives is not a new general method. Compare native
component update vectors as well as residual streams. A difference between
adjacent residual layers is only a coarse block update; it does not separately
identify attention and MLP contributions without additional capture hooks.

Only after behavioral competence and stable localization, test natural donor
interchanges and DAS-style alignments, with new-family transfer and exact
counterfactual effects. Circuit probing would require optimizing masks and new
model forwards, not retraining backbone weights. A complementary LEACE/mean
projection test needs collateral-damage, matched-removal and rescue controls.
Do not treat an edit that changes the probe's label as a successful model
intervention. These methods remain gated and are not launched by this review.

## What changes in the plan

1. Add E1 as the next inexpensive label/control preparation task.
2. Make E2's query-dependent retrieval explanation an explicit peer of global
   state. Wider global probes remain a baseline, not our sole model of cognition.
3. Add E3 to the next controlled readout suite, then E4 as the main new decoder
   architecture. Both preserve source/query access tiers and canonical splits.
4. Add E5's learning-effort and preprocessing controls to that suite, with a
   finite selection recipe. Causal use requires E6 and existing gates.

The scientific target is a pattern that distinguishes hypotheses: the readout
transfers to new names/structures, changes the correct assignment version after
a controlled write, and predicts a specific downstream consequence. This
review proposes those comparisons; it does not establish those results.
