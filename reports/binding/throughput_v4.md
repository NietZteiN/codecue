# GPU throughput optimization

Same pinned CodeLlama checkpoint, BF16, greedy decoding, published prompt-token IDs and per-task ceilings. Performance replay is separate from the recorded scientific experiments. Selection uses requests/second, not answer accuracy. Numerical and answer changes are recorded rather than silently pooled.

| Backend / setting | Cases | Generation seconds | Requests/s | Output tokens/s | GPU utilization | Valid | Correct |
|---|---:|---:|---:|---:|---:|---:|---:|
| vllm {'chunk_size': 64, 'gpu_memory_utilization': 0.9, 'max_num_batched_tokens': 16384, 'max_num_seqs': 256} | 512 | 32.99 | 15.52 | 2486.3 | 98.2% | 496 | 188 |
| vllm {'chunk_size': 128, 'gpu_memory_utilization': 0.9, 'max_num_batched_tokens': 16384, 'max_num_seqs': 256} | 512 | 22.42 | 22.84 | 3616.4 | 99.6% | 495 | 191 |
| vllm {'chunk_size': 256, 'gpu_memory_utilization': 0.9, 'max_num_batched_tokens': 16384, 'max_num_seqs': 256} | 512 | 15.70 | 32.62 | 5222.0 | 99.7% | 495 | 191 |

Selected: `vllm` / `{'chunk_size': 256, 'gpu_memory_utilization': 0.9, 'max_num_batched_tokens': 16384, 'max_num_seqs': 256}`.
Original baseline did not complete.
Full-backlog validation: `complete`.

Useful output token counts exclude EOS-valued padding. Generation timing includes decode/stopping overhead and GPU synchronization; model loading, warmup and compilation are reported separately per worker. GPU utilization/memory/power samples come only from the allocated device. Larger batching and attention kernels can change numerical outputs; quality agreement and raw responses accompany every trial.

The old scientific reports are unchanged. See `artifacts/binding/throughput/` for profiles, worker logs, GPU telemetry and the selected execution settings.
