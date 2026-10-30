# Relationship pipeline recovery checks

The debugging review found reproducible recovery and validation problems before the relationship model capture or real probe fitting had started. The fixes preserve the model, dataset, target eligibility, layers/sites, ridge objective, weighting seeds, shuffled-target recipe and primary comparisons in the [declared study plan](relationship_readout_plan_v2.md).

| Failure | Corrected behavior |
|---|---|
| A killed capture leaves its final attempt unfinished | Resume retains durable counters and records the interrupted attempt before continuing. |
| A partial capture file changes before the final completion receipt exists | The expected checksum is journaled before chunk publication; resume rejects a changed or unowned committed chunk. |
| Capture stops between saving its summary and completing its manifest | Resume verifies the saved summary, source identity and chunks, then finishes metadata without another prefill. |
| A prepared-layout or capture metadata write stops partway through publication | Metadata is published atomically; output publication rejects symbolic links. |
| A saved probe is reused with changed training membership or input metadata | Resume verifies ordered training IDs, feature/target/weight hashes and donor IDs before accepting the saved fit. |
| A report path aliases another generated artifact or capture source | Validation rejects the configuration before capture payload access or fitting. |
| Fitting stops after saving results, report or audit but before its completion receipt | Exact parameter replay and matching scientific payload allow completion to resume; original runtime is preserved and the completing worker is recorded separately. |
| SLURM accounting or queue queries stall | Each query has a 15-second timeout. Other observations and explicit scheduler errors are retained. |
| A manual pipeline audit is invoked from the ordinary workspace | Audit verifies the recorded original frozen source and exact template before reading capture completion metadata. Fitting still requires a frozen sbatch worker. |

These checks use CPU fixtures, fault injection and source metadata. They are software validation, not relationship-decoding evidence. No model activations or sealed final outcomes were used to choose these fixes.

The old unstarted chain, jobs 480208, 480209, 480258 and 480259, was canceled in reverse dependency order for replacement. The completed tokenizer preflight, its frozen source and all prior submission records are retained. Existing training jobs 480139 and 480148 and the VSCode host allocation were left untouched, following the user's instruction to keep those jobs running and queue relationship work.

The replacement uses `capture_v2.json`, `readouts_pipeline_v3.json` and `readiness_v11.json`, with fresh output directories. Final test counts, source checksums, submission state and new job IDs belong in the replacement submission handoff; the earlier handoffs retain their original meaning.
