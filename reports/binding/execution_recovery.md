# Execution and reporting recovery

The VS Code execution worker previously exited with SIGTRAP; subsequent tool calls failed before shell execution. The available extension log records the signal and closed stdout but does not establish the underlying crash cause. Execution recovered with the current extension process and new SLURM allocation. This is separate from the experiment-code bug below.

The current-node process audit found one Codex application server and its child execution worker, both belonging to this conversation. No extra Codex process was available to terminate. The old interactive allocation completed. Saved conversation history was not deleted, and unrelated VS Code/Copilot processes were preserved. Exact observations and timestamps are in `artifacts/binding/execution_recovery.json`.

Codex app-server can manage several threads within one server, so operating-system process counts do not enumerate saved conversations. The official [OpenAI Docs on app-server lifecycle](https://learn.chatgpt.com/docs/app-server#track-thread-status-changes) distinguish loaded-thread status, interruption and unsubscribing. This inspection found no redundant application-server process on the current node; it does not claim to have deleted or archived other conversations.

All scheduled CPU behavior, extraction, probe, audit and software-check jobs completed successfully. The final aggregation job failed because `92_binding_progress_report.py` derived its output root from its own location inside the immutable source snapshot. It consequently looked for data there and attempted to write a report there.

The fix resolves the writable workspace from the verified snapshot manifest and creates the report directory there. A regression test launches the frozen report against a temporary workspace, verifies the resulting report and evidence file, and confirms no report directory is created inside the source snapshot. The replacement frozen aggregation job completed successfully. The original failed job and its logs remain available.

The refreshed [pilot report](pilot_report.md) includes the completed larger CPU cohorts. Their near-floor accuracy and weak decoder generalization are experimental outcomes, not repaired by the report fix. Full GPU expansion was cancelled before allocation while a separate, bounded arithmetic/interface calibration compares batch sizes and CPU precisions. All final-test model outcomes remain sealed.

During subsequent calibration-bank subset preparation, the original conditional job had already completed and skipped inference. A redundant submission then hit the immutable-decision guard and exited without loading a model or changing the saved decision. The original completed job was restored as authoritative, and the duplicate job/log remains recorded. No bank outputs were discarded or relabelled. The later 512-token sensitivity uses a separate output directory and decision file.
