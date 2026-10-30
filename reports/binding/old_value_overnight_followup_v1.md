# Old-value overnight completion and debug follow-up

Recorded 2026-10-28T20:50:50.417312-05:00.

Both measurements and deterministic publication completed. All 40,320 responses, 48 primary cells and independent current/previous AST oracles reconciled exactly. Sixteen original warm-ups are separately accounted; this follow-up used no new model queries or fits. Both checkpoints failed every fixed reliability cell.

| Model | Correct / scored | Accuracy | Invalid | Gates passed | Mean GPU utilization | Generation requests/s |
|---|---:|---:|---:|---:|---:|---:|
| codellama34b | 4,739 / 20,160 | 23.51% | 9,864 | 0 / 24 | 96.0% | 223.9 |
| llama8b | 12,272 / 20,160 | 60.87% | 0 | 0 / 24 | 97.7% | 203.8 |

The request rates cover timed generation blocks, with model loading and warm-up separate. GPU utilization covers recorded samples on the allocated device. Related numeric, lexical and rotation views remain dependent.

CodeLlama produced 9,397 assignment-wrapped integers, 291 fenced integers and 176 other invalid answers. Only 166 outputs reached the fixed token ceiling; 9,698 invalid outputs stopped normally. On Llama’s 7,272 different-value historical questions, 2,859 were correct, 2,577 returned the current value and 1,836 returned another wrong integer. Saved scores, task truth, input IDs and the CodeLlama native boundary match the frozen protocol. These are observed answer failures, not evidence of a causal neural mechanism.

The post-run artifact audit verified 51 distinct publication pins, 215 frozen source files, 258 frozen configs and the 109-file historical test archive. The original full regression passed 2,280 tests. Publication actually ran twice and reproduced identical bytes.

Two operational repairs were validated after the measurements:

- The accumulating log reconciliation exceeded its two-minute allocation. Future workers now request ten minutes; both existing pending guards were extended in place. Forced CPU job 481752 completed successfully in 2:04 and advanced the actual last-success timestamp. Fifty-eight focused logging tests passed, including interruption and durable-successor recovery. The ten-minute cadence remains configured.
- The current checker now flags failed publication or morning jobs in overall execution status and attention. Fourteen cases reproduced the previous omission; all 32 focused checker tests pass. Scientific completion and gate results retain their meaning.

The current live check recorded execution complete, behavioral gate failed, no issues and fresh logging at 2026-10-29T01:49:38.051099+00:00. Three ten-minute suite checks covered execution; cleanup job 481724 stopped the completed suite’s monitor chain. Automatic experiment-log checks continue. Independent morning job 481707 remains scheduled for October 29 at 08:00 America/Chicago with no dependency. Scheduler capacity may delay its actual start.

These repairs change only the current operational scheduler/checker and their tests. The S7 scientific source, all model outputs, gate results and eight pinned pipeline helpers remain unchanged. The queued morning snapshot retains its original frozen S7 identity; this follow-up independently verifies publication success and logging recovery. No causal experiment, optional training, parser relaxation or completed scientific rerun follows automatically.

The current inventory records 74 tasks: 62 ready, nine needing scientific decisions and three deferred optional tasks.

[Complete findings](old_value_overnight_findings_v1.md) · [Response diagnostics](old_value_postrun_response_diagnostics_v1.md) · [Live status](old_value_overnight_status_v1.md) · [Original plan](old_value_overnight_plan_v1.md)
