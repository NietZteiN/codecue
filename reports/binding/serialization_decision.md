# Decision after the serialization comparison

The follow-up completed all 1,600 predictions and its full score/token/provenance audit. The [comparison report](serialization_comparison.md) preserves both predeclared metrics and all paired outcomes.

Direct released-postprocessing literal correctness changed from 3/800 to 295/800 (+36.50 percentage points). Answer-block literal correctness changed from 290/800 to 295/800 (+0.625 points). Python-section echoes changed from 786/800 to 0/800. The large released-parser gap primarily reflects the interface/format mismatch; it is not evidence of a comparable gain in underlying reasoning.

For CoT, both scoring methods agree: native chat solved 298/800 and completion solved 290/800 (-1.00 percentage points). Changing serialization also changes some individual answers, not just their parseability. Direct literal decisions overlap on 254 questions, with 36 chat-only and 41 completion-only correct. These observed counts do not establish a binding mechanism or resolve the earlier synthetic calibration failures.

All three recorded device models—old chat, native replay and new completion—were NVIDIA H100 80GB HBM3. The scheduler accepted H100/H200 candidates, but the anticipated cross-device-model fallback did not occur. All 16 replay input and output token sequences matched exactly. Every full-run prompt matched the independently audited single-BOS/SentencePiece preflight.

Use the released completion serialization for CRUXEval because it preserves the intended completion boundary and makes its released postprocessing applicable. Keep the native-chat results as an explicitly different protocol. Retain literal-only scoring labels: no model output was executed and these are not sampled execution pass@k reproduction scores. This follow-up was designed after the previous formatting result and is not an independent confirmatory dataset.

The next research step is a separately planned paired-variant study grounded in the published programs, with explicit scope/renaming eligibility, separate derivative IDs and independently validated semantics. Do not rename arbitrary Python without resolving scopes or send downloaded programs through the original generated-program execution oracle. The existing generated final-test and extrapolation model outcomes remain sealed, and conditional mechanism/forecast/replication stages retain their previous prerequisites.

Engineering fixes were completed alongside the run. Reusing a completed benchmark now preserves its resource/checksum metadata and does not register another attempt or reserve GPU time. A final saved response batch can be finalized without loading a model, while missing peak-memory measurements remain explicitly unknown. A read-only health command replaces the stale queued status with actual job states, progress, checksum/coverage issues and budget information. Historical scientific snapshots remain unchanged; see [benchmark_reliability.md](benchmark_reliability.md).

Validation: 156 full regression tests passed, plus 17 focused recovery/status/snapshot checks. The shared ledger now records 62.87 of 240 registered GPU-stage minutes, with no active reservations. Exact model, source, response and job identities are recorded in `artifacts/binding/serialization/handoff_v2.json`.
