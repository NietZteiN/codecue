# Overnight suite: morning and daytime verification

Verified 2026-10-29T11:51:09.920473-05:00.

The independent morning check started at **08:00:04 America/Chicago on October 29**, saved its snapshot at 08:00:07 and completed at **08:00:16**, exit 0. All seven suite stages now have confirmed successful scheduler exits. The snapshot recorded its own job as running because it was written before that job exited; the current live check correctly records completion.

The repaired logging workers held overnight: **90 workers completed successfully**, including **89 actual reconciliations** and **1 normal not-due exit**. All had ten-minute allocations. The longest worker ran 162 seconds; 33 workers exceeded the previous two-minute limit. No failed worker appears in this audited post-repair window. The longest gap between successful export completions was **11 minutes 22 seconds**.

Current logging last succeeded at 2026-10-29T16:48:08.964194+00:00 and was 181.0 seconds old at verification. Both the live check and morning check report no issues, no scheduler errors and fresh logging. Automatic reconciliation continues.

Integrity checks matched **51 distinct publication/diagnostic input and output pins**, all **215 frozen source files**, **258 frozen configurations**, and the **161-artifact scientific baseline**. The completed study still contains 40,320 scored responses plus 16 separately counted warm-ups. This verification makes no model calls or fits and does not rerun completed measurements.

Execution success remains separate from scientific qualification. Llama 8B scored 60.9% overall and CodeLlama 34B scored 23.5%; both failed all 24 fixed reliability cells. The saved-output optimistic bound still leaves 16/24 CodeLlama and 24/24 Llama cells below 90%, including every historical-question cell. No causal follow-on qualifies from this calibration.

The implementation checklist, research backlog and README now record the morning check as complete. Historical snapshots and earlier timestamped reports retain their original contents. The 74-task inventory remains 62 ready / nine scientific decisions / three optional tasks.

[Morning snapshot](old_value_overnight_morning_v1.md) · [Live status](old_value_overnight_status_v1.md) · [Complete findings](old_value_overnight_findings_v1.md) · [Formatting bound](old_value_format_ceiling_v1.md)
