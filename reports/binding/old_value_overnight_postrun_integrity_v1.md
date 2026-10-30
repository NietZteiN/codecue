# Old-value overnight post-run integrity check

Recorded 2026-10-28T20:42:26.948856-05:00. Status: **passed**.

The two measurements and publication completed successfully. Both scientific reliability gates failed; operational completion does not qualify a causal follow-on.

Verified 51 distinct metadata/data pins by streaming bytes, plus 215 frozen source files and 258 frozen configs. No model calls, fitting, array loading, or response/source/prepared-record parsing occurred.

- Full regression: 2,280 passed, zero failures/errors/skips; all 109 archived and current test sources match.
- Both native preparations passed for 20,160 cases each without model inference.
- Scored responses: 40,320; warm-ups: 16; total original model queries: 40,336. Each model used one completed backend attempt.
- Publication job 481706 actually produced `published` and `byte_identical_reproduction` in sequence and completed with exit 0.
- Three periodic checks ran about ten minutes apart. Final cleanup tick 481724 stopped with `terminal_no_successor`; no further suite-monitor successor remains.
- Independent morning job 481707 remains queued for October 29 at 08:00 America/Chicago (UTC−05:00), with no dependency.
- Logging last succeeded 2026-10-29T01:22:37.738579+00:00; age at check 1189.2 seconds, within the 20-minute threshold. 3 logger guards are queued.

The readiness inventory records 74 tasks: 62 ready, nine requiring scientific decisions, and three optional deferred tasks.

Evidence: `artifacts/binding/old_value_overnight/20261028_v1/postrun_integrity_review_v1.json`.
