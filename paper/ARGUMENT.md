# Misleading Identifiers Change What Code Traces Write

Updated 2026-10-08 to match the completed follow-ups and revised manuscript.

The contribution separates the correct value recoverable from internal activations from
the incorrect value written in a trace. That separation motivates changing the worked
examples: showing the operation reduces incorrect writes while holding the program and
model fixed. The implication concerns both reading and improving traces: the value written
is a separate measurement from the value recovered by a probe, and the demonstrated format
can change that write.

The paper follows one conflict: a variable is computed as a length but named like a sum.
A terse trace can write the sum. The revised probes train on disjoint programs and report readouts
and name controls under all three demonstration sets. The correct digit is decodable
before actual name errors, with the generated prefixes verified against the cached states;
five-fold layer selection keeps each test computation out of its neutral selection pool.
Decodability does not establish use. Showing the expression in demonstrations sharply
reduces the effect. Neutral annotations preserve a large effect, while numeric elaboration
reduces part of it.
An independent replication on fresh computations with names passing the original meaning
gate confirms the format contrast, while preserving the original selection-rule deviation.

The introduction starts with the 2-versus-8 trace, then asks how names and worked examples
affect the value written. Define a linear probe as a predictor of the correct digit from
internal activations: recovering 2 while the model writes 8 establishes recoverable
information, not its use by the model.

## Order of the evidence

1. **Show an actual trace.** The same program receives different traces when worked examples
   show values alone or expressions with values.
2. **Measure the naming effect.** Establish excess name errors against matched neutral
   twins and distinguish it from the models' ordinary length-step errors.
3. **Test sensitivity with patches.** Report name-site and decision-site interventions.
   Report the validated disjoint probe readouts on actual name errors and their
   controls, with independent layer selection and demonstration-set repeats. Decodability does not establish that the
   model uses the decoded digit.
4. **Change the demonstrated format.** Hold the program and example identities fixed.
   Compare expressions with neutral annotations of the same token length and numeric
   elaborations. Report the remaining OLMo effect, then use REPL, comments, scale and
   natural code to bound the finding.
5. **Replicate with independently screened names.** Freeze names using the original
   seven-model meaning gate before collecting behavior on fresh computations. Report
   trace and expression effects in the three affected models and the CodeGemma control.

The main evidence table reports error-conditioned probe intervals and independent computation
counts alongside the replication with independently screened names. Its panels explicitly
separate the original-name readouts from the fresh behavioral cohort. The full model panel
remains in the appendix. This evidence extends known identifier sensitivity by testing
correct-digit availability immediately before actual wrong writes and a controlled change
to the demonstrated format.

The prompt-end versus pre-write comparison is queued, not a completed finding. Its fixed
design is in `../docs/PROMPT_PROBE_COMPARISON.md`. Once validated, report both positions on
the same observed errors; do not infer causal use from their difference.

The appendix holds task levels, identifier-meaning checks, the operation matrix, format
intervals, probe and patch details, scope checks and statistical conventions.

## Limits that affect the argument

- The original probes reused test programs in training. Reported replacement runs pass
  the split audit; retain the original caches as an audit trail.
- Decodability does not prove that computation is intact or that the model uses the decoded
  value. The name-identity controls have low selectivity.
- Patches replace mixed features. The alternative-name control has no distinct source value
  in the main sum-family cell, and the affected Llama-3.1-8B name lacks aligned neutral twins.
- Expression-bearing examples reduce the effect; they do not eliminate it in every model.
  Length-matched neutral annotations and numeric elaborations test narrower format accounts.
- Generated-prefix audits cover all 2,565 code evaluation generations across the three
  affected models and three demonstration sets. Error-conditioned readouts show available
  computed digits, but do not establish their causal use.
- The CodeLlama-34B maximum-step interval crosses the equivalence margin. A small estimate
  does not establish equivalence.
- CRUXEval direct-answer and prose tests do not test the synthetic few-shot trace format.
- The companion arithmetic paper studies a different task. The two findings do not establish
  a shared causal mechanism.
- None of the three main identifiers passes the planned 80% panel meaning gate, so its
  filtered estimate is unavailable. Model-specific and per-name sensitivities are
  exploratory and do not repair that deviation. Avoid assuming each model interprets
  every retained name according to the operational name table.
- The independent screened-name replication supports the format contrast, while leaving
  the original selection-rule deviation disclosed. Names and computations change, so
  cross-experiment effect magnitudes are descriptive. Probes and patches concern only
  the original identifiers.

## Writing conventions

Keep final-answer accuracy distinct from accuracy of intermediate value writes. The main
probe result pools three demonstration sets with cross-fitted layer selection; the appendix's
layer curves and name-identity controls use the separate full-neutral analysis. Explain controls
through the task they predict and report accuracy as a percentage. Caption the direction
of paired changes and identify each table's comparison and denominator.

Figure 1 explains the task and length-versus-sum conflict, then shows every actual
assignment and final answer from the same program under the two example formats. Template
labels explain what the examples demonstrate without introducing another numeric task.
Figure 2 tells the two central aggregate findings: error-conditioned correct-digit readouts
on original names, and the independently screened-name format replication on fresh programs.
Its panels explicitly identify separate cohorts and define the added-error measure.
Technical layer curves remain in the appendix, with distinct outcome axes and denominators.
Removal of a sum write does not itself establish recovery of the correct value. Methods and appendix retain the design-rule disclosures;
the Limitations section contains the Scope and Internal measurements bullets.

For readers outside this project, keep the abstract's result–evidence–implication order
but explain the task and comparison in ordinary words. Define the requested calculation
or reported variable values before using technical labels. Avoid unexplained equivalence,
matched-pair, activation and trace terminology; keep the central numbers and precise scope.

Follow the problem through the evidence. Keep headings concrete, paragraphs short and
interpretations beside the measurements that support them. Avoid contribution lists and
repeated scope statements. Use generated `\NUM{}` macros for measured quantities and state
the interval convention actually used by the analysis.

The abstract states the main finding first: a wrong trace value can coexist with a
recoverable correct digit. Summarize the matched-program design, the error-conditioned
probe result and the demonstration intervention, then state their implications for
interpreting and improving traces. Keep concrete examples in the introduction and
auxiliary experiments in the body.
End the introduction with what we show about predicted digits, wrong writes and the
effect of showing the operation. Keep causal-use and generalization caveats with the
results and limitations that support them.

Terminology: a name-suggested value is the incorrect digit implied by the misleading name.
A name error writes that digit; excess name errors subtract the matched neutral twin's
rate of writing the same digit. Probe predictions of that value are a separate readout.
