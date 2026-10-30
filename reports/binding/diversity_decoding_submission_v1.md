# Diversity decoding: submitted execution

Recorded 2026-10-28T19:42:23.225216+00:00. The new adapters and preparations are complete. The 8B capture completed with 5,760 distinct prefills; its CPU readout is running. The 34B capture is queued behind the scheduler account limit. Learned readout outcomes have not been reviewed.

The cohort contains 5,760 programs from 60 new graph families, with 4,320 TRAIN rows / 45 families and 1,440 DEV rows / 15 families. Each family contributes 96 rows. All four assignment-version classes occur in every DEV variable slot. The full source-only preflight checked all 232 target columns, three sites and three control seeds.

Software validation passed all 2,044 tests, including 70 new adapter tests. The 100 exact test source files are archived against their validation hashes. Golden checks retain the prior runner’s default protocol, summary and report bytes.

Execution snapshot: `345f75b01f5c3b33bd0ca6d8`. Code SHA-256: `9cfa6c42fd79ddb9a4f049650ba311bb996dcb9f48afb9f9c31a2cc22254a918`. Source bank SHA-256: `d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1`.

| Stage | Job | State at recording | Dependencies |
|---|---:|---|---|
| codellama34b_capture | 481414 | PENDING; 0s | 481410 |
| codellama34b_prepare | 481410 | COMPLETED; 166s; exit 0:0 | none |
| codellama34b_readouts | 481415 | PENDING; 0s | 481414, 481411 |
| llama8b_capture | 481412 | COMPLETED; 269s; exit 0:0 | 481409 |
| llama8b_prepare | 481409 | COMPLETED; 101s; exit 0:0 | none |
| llama8b_readouts | 481413 | RUNNING; 248s | 481412, 481411 |
| regression | 481411 | COMPLETED; 563s; exit 0:0 | 481409, 481410 |
| review_publication | 481436 | PENDING; 0s | 481413, 481415 |

The fixed capture batches are 256 for 8B and 128 for 34B, compared with reference batches of 128 and 64. Actual prepared prompts are 112 tokens for 8B and 88–92 for 34B. The prospective free-memory requirements are 18,208,040,024 and 71,782,958,696 bytes; these are admission checks rather than measured peaks. Capture stays within the pinned model, source, site, layer and precision settings. Actual scheduler QoS and walltimes apply; cumulative GPU accounting has no project compute cap. No unrelated jobs were cancelled.

The complete study plans 11,520 distinct model prefills, zero generated answers, and 90 joint real/control readout banks across both models. Those banks retain all declared layers, seeds, classes, surface features and TRAIN priors. Completion requires saved-parameter and metric replay, totaling 518,400 case rows if both readouts complete.

The final CPU worker depends on both readouts. It independently checks all seven stage jobs, provenance, receipts, metrics and replay proofs; generates the report, CSV and figure twice with byte-identical verification; refreshes readiness; checks automatic logging; and publishes a pinned handoff. It does not load activations or fitted arrays, fit probes, or query models.

Current readiness uses the separately pinned `readiness_v19.json`: **68 tasks = 54 ready + 2 awaiting execution + 9 scientific decisions + 3 optional extensions**. The v19 metadata selectors distinguish the historical `columns` field from the new `target_columns` field. Frozen v18 and historical outputs remain preserved. Successful completion is expected to move the two execution tasks to ready. Automatic experiment reconciliation remains enabled every 10 minutes with two verified queued guards.

These are adaptive discovery experiments on literal-root copy programs. More training rows, graph families, and class coverage change together. They do not isolate an effect of graph novelty or establish a causal variable-binding mechanism, behavioral reliability, or rescue prior failed qualification gates.

[Prospective plan](diversity_decoding_plan_v1.md) · [Current checklist](implementation_checklist.md) · [Submission handoff](../../artifacts/binding/diversity_decoding/20261028_v1/queue_handoff_review_v1.json)
