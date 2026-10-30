# Matched arithmetic output/query semantics control, October30

The completed48-family arithmetic study has weak generated answers and poor
held-out graph recovery. Its prompt says “Execute this Python program and return
only its final integer output,” but the source ends with a bare variable. A Python
script prints nothing for that expression. This is a plausible interface
ambiguity, not an established explanation of the failures.

Run a matched2×3 discovery control on the original numeric_draw0 cases:

- Final source line: bare variable versus explicit `print(variable)`.
- Instruction0: the exact original wording. Instructions1 and2 explicitly ask
  for the final variable's value, whether named directly or inside print.
- Preserve every assignment, query identity, neutral name, numeric value,
  checkpoint revision and TRAIN/DEV family split. Validate printed output with
  ordinary Python and retain the original query-value oracle.

Each checkpoint has1,152 cases in each of six arms. Reuse all original bare/I0
responses; assert native prompt text and token IDs match those cached inputs
exactly. Generate only the other five arms:5,760 new responses per model,
11,520 total new model prefills, plus2,304 cached responses in the comparison.
These are relatives of48 existing families, not independent structural replication.

Both cached checkpoints retain their native boundaries, BF16 greedy generation,
batch64, logits_to_keep1,12-token ceiling and full-response signed-integer parser.
Do not credit assignment wrappers or fenced responses, alter earlier scores,
refit probes, run causal interventions, or open sealed outcomes.

The primary interface contrast is printed-minus-bare under original instruction0.
Retain both corresponding print contrasts under instructions1 and2, and both
clarified-bare versus original-bare contrasts. Evaluate arithmetic-written DEV
queries as the primary task stratum; report untouched-literal and pooled queries
separately. Report every arm and invalid rate;
do not select the best wording as a confirmatory result. All contrasts are paired
within the same original case. Conditional intervals resample the12 whole DEV
families after within-family averaging; report row-weighted and family-macro
differences separately. These discovery intervals are not multiplicity-adjusted.

Printing changes syntax, token count and context; instruction changes also alter
context. A gain would support an interface effect under these prompts, not a
binding mechanism. Failure across clear variants would strengthen the case for
finding a shorter reliable computed regime before causal work.

Use a newly frozen implementation and configs. Require matching software proof
before GPU collection. CPU preparation must verify every transformed oracle and
all cached baseline prompt/token identities. GPU jobs depend on their preparation;
collectors retain durable response prefixes, attempt accounting, memory checks,
checksums and automatic experiment logging. Existing jobs remain untouched.
