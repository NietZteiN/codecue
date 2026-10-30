# Overnight arithmetic suite: debug pass and release

Revision3 passed all2,315 archived regression tests with no errors, failures or skips. Both cached checkpoint tokenizers passed native preparation for every4,608-row cohort. The supervisor can now release model collectors; this is execution readiness, not a scientific result.

| Revision | Tests | Failures | Collection errors | Status |
|---|---:|---:|---:|---|
| 1 | 6 | 0 | 6 | failed |
| 2 | 2315 | 3 | 0 | failed |
| 3 | 2315 | 0 | 0 | passed |

The first failure came from pytest importlib mode preventing sibling test helper imports. Prepend mode resolved collection. The second run found three guard fixtures that intentionally expect an unfrozen checkout; importing the real frozen package violated that fixture condition. The current launcher verifies every mirrored code/config byte against its immutable manifest, then runs the unchanged tests against that source mirror. No test assertion, scientific guard, parser or cohort was relaxed.

Earlier sources, QA XML, failed records and tokenizer preparations remain preserved. Their model/readout submission lists are empty. Only superseded supervisor and morning jobs were canceled; unrelated training jobs were preserved.

Current source snapshot: `e71af09e675ea7a66cf5c8f1`. Dataset SHA256: `120f96e58dae52aab319d8a13a06eca7c01d584f55201e55deead7dd59f8329f`. Llama native prompts span101–111 tokens; CodeLlama prompts are87 tokens. Prospective weight-plus-prefill requirements are18.21GB and71.78GB respectively; the actual GPU workers retain their device/free-memory guards.

The durable supervisor checks roughly every10 minutes, records submission intents, preserves committed chunks, and retries only eligible scheduler interruptions. The existing experiment logger remains enabled. Independent morning job483450 has no upstream dependency and requests08:00 America/Chicago on October30. Scheduler capacity may delay actual starts.

Source-only review: DEV behavior contains216 queries of arithmetic-written slots and72 queries of untouched literals. These query types must be separated when interpreting answer accuracy. All48 relation cells have supported TRAIN classes and both DEV classes at every site; some numeric value classes are absent from TRAIN, as recorded in the readiness report.

[Plan](arithmetic_graph_overnight_20261029_plan_v3.md) · [Live status](arithmetic_graph_overnight_20261029_status_v3.md) · [Source readiness](arithmetic_graph_source_readiness_v1.md) · [Reproduction](../../reproducibility/arithmetic_graph_20261029_README.md)
