# Overnight debug pass

All 2,280 binding tests passed, with the exact 109-file test archive verified. The new source/runner/checker modules passed 89 focused tests; the recurring monitor passed 23 synthetic checks and publication passed 14. Both native preparations passed all 20,160 prompts per model without model inference.

The live check verified the frozen source/configuration identities and immutable scientific baseline. It found a 35-minute-old logging reconciliation despite two queued guards. An actual forced reconciliation completed; the recurring monitor now invokes the real tick and verifies the persisted timestamp instead of inferring freshness from guard health.

The first monitor tick completed without issues and prequeued successor 481709. Checks run every 10 minutes while work/publication remain active; running behavior with no committed progress for 30 minutes is flagged. Queued work and expected partial response tails remain distinct from execution failures. The independent morning job 481707 is scheduled for October 29 at 08:00 America/Chicago, with no dependency on measurement success.

See the [plan](old_value_overnight_plan_v1.md), [live status](old_value_overnight_status_v1.md) and [machine debug review](../../artifacts/binding/old_value_overnight/20261028_v1/debug_pass_review_v1.json). Measurement results remain pending; no causal study automatically follows the gates.
