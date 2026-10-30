# Overnight discovery: arithmetic dependencies and relationships, October 29–30

This suite measures the gap between the master conceptual figure and earlier
copy-only dependency probes. Both cached checkpoints receive programs containing
four literal roots and four two-input addition/subtraction assignments. The
question is whether hidden states expose current values, actual assignment
versions, and both operand definitions alongside algebraic relationships.

This is adaptive TRAIN/DEV discovery, not untouched confirmation. Existing
computed-task failures remain valid. There is no optional language-model
training, download, causal intervention or sealed final evaluation in this run.
The user's instruction is to queue useful overnight work while preserving the
other running training jobs and their pending successors.

## Fixed source cohort

- 48 ordered program families: 16 addition-only, 16 subtraction-only, 16 mixed.
- Within each operator family, 12 structures go to TRAIN and four to DEV:
  36 TRAIN / 12 DEV structural units, fixed before model outcomes.
- Three numeric seeds (1103,1201,1301), four draws, two lexical forms and four
  queried slots produce **4,608 rows per checkpoint**, 3,456 TRAIN / 1,152 DEV.
- Each draw has four roots in [-6,6]; one draw enforces equal independent roots
  and another enforces an additive root triple. These sampling strata are not
  measured truth labels: all relations are recomputed at each visible prefix.
- Rejection enforces unique initial states across the 576 numeric bodies. This
  source-only condition prevents identical initialization prefixes from receiving
  conflicting shuffled labels. Rejection attempts are recorded, not hidden.
- Canonical grouping quotients all 24 slot permutations, retaining operator,
  operand order and assignment order. Numeric, lexical and query relatives stay
  together. It does not quotient every commuting schedule or semantic identity.
- AST evaluation computes read-time definition parents before updating a
  destination. Ordinary Python independently checks all values; the existing
  interpreter also checks renamed programs and answers. Overlapping values never
  imply a dependency edge. Syntactic def-use is not functional causal influence.

## Measurements and controls

Capture at initialization end (statement3), last assignment (statement7), and
answer preparation using the audited resumable BF16 SDPA prefill engine. Native
token boundaries, padding, identical prefixes, committed chunks, checksums and
attempt counts retain their existing guards. Llama3.1 8B captures blocks8,16,24,31;
CodeLlama34B blocks12,24,36,47. Nominated readout layers are24 and36 respectively,
fixed before outcomes. Other captured layers remain available for a separately
declared follow-up; no best-layer selection occurs here.

For each model, fit 18 banks: three prefix sites × hidden/source features ×
three fixed weighting seeds (11,29,47). Source features are exact visible-prefix
character3–8-grams hashed to the model's hidden width. Every fit uses neutral
TRAIN only, alpha100, train-only normalization and the same independent
multioutput ridge objective. The direct relationship pipeline and categorical
value pipeline have different numbers of scalar outputs; their contrast is
accessibility under these readouts, not an information-content comparison.

Targets and reported scores:

1. **Dependency/assignment targets:** both ordered read-time parents for each of
   four arithmetic writes; four current definition IDs and four current versions.
   Report per-head accuracy, all-eight-parent accuracy, unordered whole-graph
   accuracy and the fraction containing no future-definition predictions.
   Initialization fits exclude future parent labels. Nodes and statement order
   are supplied: this does not establish arbitrary graph/node discovery.
2. **Algebraic targets:** six equality cells, six oriented less-than cells,
   12 distinct-slot addition cells and24 ordered subtraction cells. Retain every
   cell's support. Macro balanced accuracy averages cells within families and
   then families; eligible cells require at least12 positive and12 negative
   unique TRAIN numeric bodies. DEV cells with a missing class remain explicitly
   undefined. This support rule is prospective but the task remains discovery.
3. **Values:** independent fixed193-class heads for each slot, covering [-96,96].
   Calculate algebraic relations from their argmax values and compare with direct
   relation heads. Also retain whole-state accuracy and six signed-difference
   regression MAEs. No oracle values enter representation features.
4. **Controls:** TRAIN-weighted priors; source direct and source-value-derived
   predictions; a whole-family derangement within each split with all relative
   coordinates tied. Shuffled heads are scored against their shuffled truths.
   A source AST parser recovers syntactic parents/versions perfectly; executing
   the source supplies a100% numeric oracle ceiling. Character probes are not
   the strongest possible source algorithms and cannot establish hidden advantage
   over source information. All predictions and ridge parameters are saved and
   reloaded for exact replay before completion.
5. **Behavior:** greedy answers for every numeric_draw0 row, **1,152 responses
   per model**, four query slots and both lexical forms. Use the exact prepared
   capture prompt, max12 tokens, batch64, and the full-response signed-integer
   parser. Assignment wrappers and fenced answers remain invalid. Report invalid
   rate separately. No parser relaxation or post-hoc reliability rescue.

Total planned work is **9,216 case captures, 2,304 generated answers and36 ridge
factorizations** including controls in shared right-hand sides. Retries and model
loads are separately accounted. Raw four-layer activation storage is about2.53GiB.
Conditional95% intervals resample12 whole DEV families after averaging weighting
seeds; they are provided for answer accuracy and fixed hidden-minus-source graph
and value metrics. Per-relation scores/support are descriptive, without a
confirmatory significance claim or multiplicity correction. No readout failure
establishes absence; readout success does not establish natural causal use.

## Unattended execution and checks

Before GPU work, a frozen test archive must pass regression under the same source
snapshot. Both tokenizer/preparation jobs verify every native prefix. GPU workers
depend on software validation and their corresponding preparation; readouts wait
until the GPU phase is terminal. Each collector audits its artifacts before
returning success. Readouts resume only checksum-verified completed banks.

The durable supervisor checks about every10 minutes and installs its successor
before acting. It retries resumable TIMEOUT/PREEMPTED/NODE_FAIL/BOOT_FAIL jobs;
two interruptions without committed progress stop automatic retries. Scientific,
format, integrity and memory failures require review. No unrelated job is
canceled. The existing ten-minute experiment logger remains enabled.

8B uses dev-a30/a30/h100/h200 (actual mixed-profile maximum2h,15min backfill
minimum);34B uses h100/h200 (48h scheduler maximum,30min minimum). These are
scheduler bounds, not project compute allowances. CPU fits request16 CPUs/64GiB;
software/native preparation uses eligible dev/normal CPU queues.

A separate no-dependency **08:00 America/Chicago, October30** job records actual
morning status and any completed results, even if upstream work is delayed or
failed. Scheduler pressure can delay its start. Terminal suites stop their own
supervisor chain; experiment logging continues. No external messages are sent.

Morning review: inspect execution failures and accounting first, then source and
shuffle controls, whole graph/version/value scores, direct-versus-derived
relations, and generated-answer errors. Decide the next scientific experiment
from those measurements; do not automatically initiate patching after a weak
computed-behavior result.

Live status: [suite status](arithmetic_graph_overnight_20261029_status_v3.md).
Artifacts: `artifacts/binding/arithmetic_graph/20261029_v3/`.

## Operational revision2

The first frozen revision stopped at regression collection: importlib mode could not resolve six existing sibling test-helper imports. No scientific model collection was released. Revision2 uses pytest prepend mode for the archived tests, with unchanged cohort, targets, scientific controls and planned measurements. The failed revision1 source, QA report, logs and completed tokenizer preparations remain preserved.

## Operational revision3

The full revision2 regression exposed guard fixtures that intentionally require an unfrozen checkout. The launcher had imported the real frozen package into those fixtures. Revision3 verifies every source/config byte against the frozen manifest, then imports that exact source from its isolated regression mirror (without a frozen_manifest.json). Test assertions and scientific guards are unchanged. CPU readouts use the actual allocated thread count. Source programs, targets, models, readout recipe and cohort are unchanged. Prior revision artifacts remain preserved; no model collector was released by either failed software gate.

Morning interpretation must separate queries of untouched literal roots from queries of arithmetic-written variables, and report TRAIN/DEV value-class support before interpreting low categorical accuracy. Whole-state scores include every slot; the current generated-answer summary pools query types, so its overall accuracy cannot qualify a reliable computed-only regime.
