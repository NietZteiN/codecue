# Relationship readouts after recovery debugging

The corrected execution source is frozen and queued. The full binding suite passed **1,537 tests**, with no failures, errors or skips. The fresh native-tokenizer preflight passed **1,944 programs** from that same source. **GPU capture and real readout fitting have not completed; no new relationship-decoding results are available.**

The [recovery findings](relationship_recovery_findings_v1.md) explain the corrected interruption accounting, chunk checksums, atomic publication, partial-completion recovery, training-input validation, output-path checks, scheduler timeouts and workspace auditing. CPU fault-injection fixtures are software checks, not decoding evidence. The [declared scientific plan](relationship_readout_plan_v2.md), model, dataset, target eligibility, shuffled-target recipe and primary comparisons are unchanged.

| Stage | Job | State at requalification review |
|---|---:|---|
| Native tokenizer/layout preflight | 480286 | Completed, exit 0, 225 allocated seconds |
| Shared 8B activation capture | 480292 | Queued: scheduler account job limit |
| Capture checksum/prefix audit | 480293 | Waits for successful capture |
| Structural/algebraic fitting and verification | 480294 | Waits for successful capture audit |
| Readiness refresh | 480295 | Runs after fitting terminates, including failure |

The earlier unstarted chain, 480208/480209/480258/480259, was canceled in reverse dependency order before replacement. Earlier source snapshots, preflight data, protocols, job records and test evidence are retained. Existing training/controller jobs and the VSCode host allocation were preserved, following the user's instruction to keep those jobs running and queue relationship work.

Capture remains eligible for `dev-a30,a30,h100,h200`, with one GPU and a 15-minute minimum backfill allocation under the scheduler's two-hour maximum for that profile. The wait is an actual scheduler constraint; there is no application GPU-hour budget.

Once scheduled, the capture performs **1,944 case prefills**, saving raw block outputs at nine positions and four layers, with zero generated responses. The CPU continuation fits **45 fixed feature-bank/weighting-seed combinations** and checks **87,480 saved-parameter case replays**, then publishes `reports/binding/relationship_readouts_v3.md` and its completion receipts automatically. Source, input and output identities are checked before reuse; verified partial results can finish publication without refitting.

The bank is adaptive copy-routing discovery, with 18 training and nine development components, and reuses the prepared graph families. Parent recovery assumes the known fixed program scaffold. Weighting seeds and correlated relation tasks are not independent replications. Successful relation decoding alone would not establish causal use or a dedicated relational representation.

At submission, **37 tasks are ready, one awaits execution, nine require scientific decisions and three are optional**, across 50 tracked tasks. See the [live readiness inventory](../../artifacts/binding/relationship_readouts/readiness_live_v3.json), [job IDs](../../artifacts/binding/relationship_readouts/jobs_v3.json), [submission handoff](../../artifacts/binding/relationship_readouts/handoff_review_v3.json) and [automatic experiment dashboard](experiment_log.md). The submission handoff pins static evidence separately from mutable execution status.
