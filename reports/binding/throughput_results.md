# Validated GPU throughput

Selected `vllm` with `{'backend': 'vllm', 'chunk_sizes': [1600], 'first_n_per_task': None, 'gpu_memory_utilization': 0.9, 'max_num_batched_tokens': 16384, 'max_num_seqs': 256, 'timeout_seconds': 1680}` on NVIDIA H200 NVL.

The matched 512-request profile improved from 1.55 to 32.62 requests/s (21.01×).
Baseline hardware: NVIDIA H100 80GB HBM3; candidate hardware: NVIDIA H200 NVL. This ratio combines hardware and execution changes; it does not isolate a software speedup.

Full workload: 1600 requests in 39.78 generation seconds, 40.22 requests/s and 6642 useful output tokens/s.
Allocated-device utilization averaged 98.61111111111111%; peak device memory was 132555.0 MiB. Device memory includes model weights, reserved KV cache and allocator reservations.
The engine worker lifetime was 598.73 seconds (shared engine lifetime including profiling; no second model load, including loading/compilation/warmup and cleanup).

Full validation quality: 575 correct, 1537 parseable; the saved reference has 585 correct. Correctness decisions agree on 1528/1600; raw strings agree on 1142/1600. Parsed values agree on 1325/1524 cases where both are valid.

The fastest setting was selected by work completed per second, not by favorable answer scores. Different batching and numerical kernels can change answers; this is an explicit new execution profile. Old scientific scores and snapshots are unchanged.

The audit rechecked all 3 completed profile trials and all 1600 validation prompt sequences, response scores, token ceilings and throughput calculations. Raw responses, GPU telemetry summaries, memory use, failures and timing are retained in the run directory.

Reusable preset: `artifacts/binding/throughput/selected_execution_v4.json`. Measured settings and per-candidate utilization are in [the profiling report](throughput_v4.md). See [the fixed plan](throughput_plan.md).
