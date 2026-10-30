# Overnight logger timeout follow-up

Completed scientific publication hashes and accounting passed the independent integrity review. Subsequent operational inspection found the logger refresh becoming stale while successor guards remained queued.

Jobs 481719, 481726, and 481730 all requested a two-minute allocation and reached scheduler TIMEOUT. Job 481719 nevertheless printed a complete result and advanced the success timestamp. The next two jobs emitted explicit time-limit cancellations before completing; the timestamp remained 2026-10-29T01:22:37.738579+00:00. Its age at this follow-up was 1258.1 seconds (freshness threshold: 1,200 seconds).

A longer allocation for verified logging workers and a confirmed completed refresh are needed. This issue concerns automatic result indexing; both model measurements, all frozen scientific outputs, and the independent 08:00 morning job remain intact.

Evidence: `artifacts/binding/old_value_overnight/20261028_v1/postrun_logging_timeout_review_v1.json`.
