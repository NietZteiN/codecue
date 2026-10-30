# Arithmetic and readout feasibility: codellama/CodeLlama-34b-Instruct-hf

All 6,144 registered responses retained: 3,939 correct and 16 invalid across 384 numeric tuples. Execution/audit status: complete and passed.

Fresh numeric calibration on repeated arithmetic structures, not structural generalization or a causal mechanism test. One versus three operations also changes intermediate literal exposure; storage forms change assignments, dependencies and token distances. Trace responses change computation and generation allowance and are never pooled with direct answers. Intervals are exploratory without multiplicity adjustment. Historical failed gates and sealed final/extrapolation outcomes remain unchanged.

Each protocol has its own fixed gate. Every nonzero-operation form × split × sign-stratum cell must reach at least 90% accuracy, at most 5% invalid responses and n ≥ 24. Numeric development qualifies only after training qualification; no alternate protocol is substituted after failure. Zero-operation controls remain visible separately.

| Protocol | Training qualified | Numeric development qualified | Reliability |
|---|---|---|---|
| print_direct_v3 | False | False | failed |
| print_trace_long_v1 | False | False | failed |

## All forms by protocol and split

| Protocol | Form | Split | Correct / n | Unique prompts | Invalid | Accuracy Wilson 95% |
|---|---|---|---:|---:|---:|---|
| print_direct_v3 | bound_one | all | 315/384 | 384 | 0 | [77.9%, 85.5%] |
| print_direct_v3 | bound_one | development | 154/192 | 192 | 0 | [74.0%, 85.2%] |
| print_direct_v3 | bound_one | train | 161/192 | 192 | 0 | [78.0%, 88.4%] |
| print_direct_v3 | bound_three | all | 16/384 | 384 | 6 | [2.6%, 6.7%] |
| print_direct_v3 | bound_three | development | 5/192 | 192 | 3 | [1.1%, 6.0%] |
| print_direct_v3 | bound_three | train | 11/192 | 192 | 3 | [3.2%, 10.0%] |
| print_direct_v3 | literal_one | all | 302/384 | 384 | 0 | [74.3%, 82.5%] |
| print_direct_v3 | literal_one | development | 151/192 | 192 | 0 | [72.3%, 83.9%] |
| print_direct_v3 | literal_one | train | 151/192 | 192 | 0 | [72.3%, 83.9%] |
| print_direct_v3 | literal_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_direct_v3 | literal_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | literal_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | literal_three | all | 25/384 | 384 | 5 | [4.4%, 9.4%] |
| print_direct_v3 | literal_three | development | 8/192 | 192 | 3 | [2.1%, 8.0%] |
| print_direct_v3 | literal_three | train | 17/192 | 192 | 2 | [5.6%, 13.7%] |
| print_direct_v3 | stored_intermediates_three | all | 8/384 | 384 | 0 | [1.1%, 4.1%] |
| print_direct_v3 | stored_intermediates_three | development | 5/192 | 192 | 0 | [1.1%, 6.0%] |
| print_direct_v3 | stored_intermediates_three | train | 3/192 | 192 | 0 | [0.5%, 4.5%] |
| print_direct_v3 | stored_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_direct_v3 | stored_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | stored_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | stored_result_one | all | 298/384 | 384 | 0 | [73.2%, 81.5%] |
| print_direct_v3 | stored_result_one | development | 150/192 | 192 | 0 | [71.8%, 83.4%] |
| print_direct_v3 | stored_result_one | train | 148/192 | 192 | 0 | [70.6%, 82.5%] |
| print_trace_long_v1 | bound_one | all | 297/384 | 384 | 0 | [72.9%, 81.2%] |
| print_trace_long_v1 | bound_one | development | 145/192 | 192 | 0 | [69.0%, 81.1%] |
| print_trace_long_v1 | bound_one | train | 152/192 | 192 | 0 | [72.9%, 84.3%] |
| print_trace_long_v1 | bound_three | all | 16/384 | 384 | 3 | [2.6%, 6.7%] |
| print_trace_long_v1 | bound_three | development | 8/192 | 192 | 2 | [2.1%, 8.0%] |
| print_trace_long_v1 | bound_three | train | 8/192 | 192 | 1 | [2.1%, 8.0%] |
| print_trace_long_v1 | literal_one | all | 276/384 | 384 | 1 | [67.2%, 76.1%] |
| print_trace_long_v1 | literal_one | development | 139/192 | 192 | 0 | [65.7%, 78.2%] |
| print_trace_long_v1 | literal_one | train | 137/192 | 192 | 1 | [64.6%, 77.3%] |
| print_trace_long_v1 | literal_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_trace_long_v1 | literal_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | literal_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | literal_three | all | 238/384 | 384 | 1 | [57.0%, 66.7%] |
| print_trace_long_v1 | literal_three | development | 112/192 | 192 | 1 | [51.3%, 65.1%] |
| print_trace_long_v1 | literal_three | train | 126/192 | 192 | 0 | [58.7%, 72.0%] |
| print_trace_long_v1 | stored_intermediates_three | all | 314/384 | 384 | 0 | [77.6%, 85.3%] |
| print_trace_long_v1 | stored_intermediates_three | development | 156/192 | 192 | 0 | [75.1%, 86.1%] |
| print_trace_long_v1 | stored_intermediates_three | train | 158/192 | 192 | 0 | [76.3%, 87.0%] |
| print_trace_long_v1 | stored_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_trace_long_v1 | stored_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | stored_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | stored_result_one | all | 298/384 | 384 | 0 | [73.2%, 81.5%] |
| print_trace_long_v1 | stored_result_one | development | 147/192 | 192 | 0 | [70.1%, 82.0%] |
| print_trace_long_v1 | stored_result_one | train | 151/192 | 192 | 0 | [72.3%, 83.9%] |

## Complete sign-stratified cells

Cell Wilson intervals are descriptive binomial intervals, not structural-generalization uncertainty. Zero-operation controls repeat exact deterministic prompts, report unique counts, and cannot be treated as independent numeric generalization evidence. Paired contrasts bootstrap whole numeric-relative groups; repeated templates are not independent structural replications.

| Protocol | Form | Split | Signs (r,s,y) | Correct / n | Unique prompts | Invalid | Accuracy Wilson 95% |
|---|---|---|---|---:|---:|---:|---|
| print_direct_v3 | bound_one | development | −,−,− | 27/32 | 32 | 0 | [68.2%, 93.1%] |
| print_direct_v3 | bound_one | development | −,−,+ | 14/32 | 32 | 0 | [28.2%, 60.7%] |
| print_direct_v3 | bound_one | development | −,+,− | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_direct_v3 | bound_one | development | +,−,+ | 18/32 | 32 | 0 | [39.3%, 71.8%] |
| print_direct_v3 | bound_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | −,−,− | 28/32 | 32 | 0 | [71.9%, 95.0%] |
| print_direct_v3 | bound_one | train | −,−,+ | 15/32 | 32 | 0 | [30.9%, 63.6%] |
| print_direct_v3 | bound_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | +,−,+ | 22/32 | 32 | 0 | [51.4%, 82.0%] |
| print_direct_v3 | bound_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_three | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | −,+,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_direct_v3 | bound_three | development | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | +,+,− | 0/32 | 32 | 1 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | +,+,+ | 1/32 | 32 | 2 | [0.6%, 15.7%] |
| print_direct_v3 | bound_three | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | −,+,− | 5/32 | 32 | 0 | [6.9%, 31.8%] |
| print_direct_v3 | bound_three | train | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | +,+,− | 4/32 | 32 | 2 | [5.0%, 28.1%] |
| print_direct_v3 | bound_three | train | +,+,+ | 2/32 | 32 | 1 | [1.7%, 20.1%] |
| print_direct_v3 | literal_one | development | −,−,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | +,−,+ | 23/32 | 32 | 0 | [54.6%, 84.4%] |
| print_direct_v3 | literal_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | −,−,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | +,−,+ | 23/32 | 32 | 0 | [54.6%, 84.4%] |
| print_direct_v3 | literal_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | −,−,− | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | −,−,+ | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | −,+,− | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | +,−,+ | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | +,+,− | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | development | +,+,+ | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | −,−,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | −,−,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | −,+,− | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | +,−,+ | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | +,+,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_output | train | +,+,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_three | development | −,−,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_direct_v3 | literal_three | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | development | −,+,− | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_direct_v3 | literal_three | development | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | development | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | development | +,+,+ | 1/32 | 32 | 3 | [0.6%, 15.7%] |
| print_direct_v3 | literal_three | train | −,−,− | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_direct_v3 | literal_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | train | −,+,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_direct_v3 | literal_three | train | +,−,+ | 1/32 | 32 | 1 | [0.6%, 15.7%] |
| print_direct_v3 | literal_three | train | +,+,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_direct_v3 | literal_three | train | +,+,+ | 0/32 | 32 | 1 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | −,−,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_intermediates_three | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | −,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_intermediates_three | development | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | +,+,− | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_direct_v3 | stored_intermediates_three | development | +,+,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | −,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_intermediates_three | train | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | +,+,− | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_direct_v3 | stored_intermediates_three | train | +,+,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_output | development | −,−,− | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | development | −,−,+ | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | development | −,+,− | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | development | +,−,+ | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | development | +,+,− | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | development | +,+,+ | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | −,−,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | −,−,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | −,+,− | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | +,−,+ | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | +,+,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_output | train | +,+,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | −,−,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | −,−,+ | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_result_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | +,−,+ | 21/32 | 32 | 0 | [48.3%, 79.6%] |
| print_direct_v3 | stored_result_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | −,−,− | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_direct_v3 | stored_result_one | train | −,−,+ | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_result_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | +,−,+ | 20/32 | 32 | 0 | [45.3%, 77.1%] |
| print_direct_v3 | stored_result_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | −,−,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_trace_long_v1 | bound_one | development | −,−,+ | 8/32 | 32 | 0 | [13.3%, 42.1%] |
| print_trace_long_v1 | bound_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | −,−,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_trace_long_v1 | bound_one | train | −,−,+ | 15/32 | 32 | 0 | [30.9%, 63.6%] |
| print_trace_long_v1 | bound_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_trace_long_v1 | bound_three | development | −,−,+ | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_trace_long_v1 | bound_three | development | −,+,− | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_trace_long_v1 | bound_three | development | +,−,+ | 2/32 | 32 | 2 | [1.7%, 20.1%] |
| print_trace_long_v1 | bound_three | development | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_trace_long_v1 | bound_three | development | +,+,+ | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_trace_long_v1 | bound_three | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_trace_long_v1 | bound_three | train | −,−,+ | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_trace_long_v1 | bound_three | train | −,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_trace_long_v1 | bound_three | train | +,−,+ | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_trace_long_v1 | bound_three | train | +,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_trace_long_v1 | bound_three | train | +,+,+ | 2/32 | 32 | 1 | [1.7%, 20.1%] |
| print_trace_long_v1 | literal_one | development | −,−,− | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_trace_long_v1 | literal_one | development | −,−,+ | 14/32 | 32 | 0 | [28.2%, 60.7%] |
| print_trace_long_v1 | literal_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | development | +,−,+ | 19/32 | 32 | 0 | [42.3%, 74.5%] |
| print_trace_long_v1 | literal_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | train | −,−,− | 12/32 | 32 | 0 | [22.9%, 54.7%] |
| print_trace_long_v1 | literal_one | train | −,−,+ | 8/32 | 32 | 0 | [13.3%, 42.1%] |
| print_trace_long_v1 | literal_one | train | −,+,− | 31/32 | 32 | 1 | [84.3%, 99.4%] |
| print_trace_long_v1 | literal_one | train | +,−,+ | 22/32 | 32 | 0 | [51.4%, 82.0%] |
| print_trace_long_v1 | literal_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | −,−,− | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | −,−,+ | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | −,+,− | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | +,−,+ | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | +,+,− | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | development | +,+,+ | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | −,−,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | −,−,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | −,+,− | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | +,−,+ | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | +,+,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_output | train | +,+,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_three | development | −,−,− | 9/32 | 32 | 1 | [15.6%, 45.4%] |
| print_trace_long_v1 | literal_three | development | −,−,+ | 17/32 | 32 | 0 | [36.4%, 69.1%] |
| print_trace_long_v1 | literal_three | development | −,+,− | 22/32 | 32 | 0 | [51.4%, 82.0%] |
| print_trace_long_v1 | literal_three | development | +,−,+ | 6/32 | 32 | 0 | [8.9%, 35.3%] |
| print_trace_long_v1 | literal_three | development | +,+,− | 29/32 | 32 | 0 | [75.8%, 96.8%] |
| print_trace_long_v1 | literal_three | development | +,+,+ | 29/32 | 32 | 0 | [75.8%, 96.8%] |
| print_trace_long_v1 | literal_three | train | −,−,− | 8/32 | 32 | 0 | [13.3%, 42.1%] |
| print_trace_long_v1 | literal_three | train | −,−,+ | 17/32 | 32 | 0 | [36.4%, 69.1%] |
| print_trace_long_v1 | literal_three | train | −,+,− | 24/32 | 32 | 0 | [57.9%, 86.7%] |
| print_trace_long_v1 | literal_three | train | +,−,+ | 21/32 | 32 | 0 | [48.3%, 79.6%] |
| print_trace_long_v1 | literal_three | train | +,+,− | 25/32 | 32 | 0 | [61.2%, 89.0%] |
| print_trace_long_v1 | literal_three | train | +,+,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,−,− | 7/32 | 32 | 0 | [11.0%, 38.8%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,−,+ | 24/32 | 32 | 0 | [57.9%, 86.7%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,+,− | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,−,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,+,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,−,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,−,+ | 24/32 | 32 | 0 | [57.9%, 86.7%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,+,− | 30/32 | 32 | 0 | [79.9%, 98.3%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,+,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_output | development | −,−,− | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | −,−,+ | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | −,+,− | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | +,−,+ | 32/32 | 21 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | +,+,− | 32/32 | 11 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | +,+,+ | 32/32 | 14 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | −,−,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | −,−,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | −,+,− | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | +,−,+ | 32/32 | 17 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | +,+,− | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | train | +,+,+ | 32/32 | 12 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | development | −,−,− | 13/32 | 32 | 0 | [25.5%, 57.7%] |
| print_trace_long_v1 | stored_result_one | development | −,−,+ | 8/32 | 32 | 0 | [13.3%, 42.1%] |
| print_trace_long_v1 | stored_result_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | development | +,−,+ | 30/32 | 32 | 0 | [79.9%, 98.3%] |
| print_trace_long_v1 | stored_result_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | train | −,−,− | 13/32 | 32 | 0 | [25.5%, 57.7%] |
| print_trace_long_v1 | stored_result_one | train | −,−,+ | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_trace_long_v1 | stored_result_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |

## Exact-source overlap audit

Zero-operation controls repeat answers as literal prompts and do not support independent numeric validation. Nonzero forms must have no exact training/development source overlap.

| Protocol | Form | Unique training sources | Unique development sources | Shared sources |
|---|---|---:|---:|---:|
| print_direct_v3 | literal_output | 48 | 52 | 44 |
| print_direct_v3 | stored_output | 48 | 52 | 44 |
| print_direct_v3 | literal_one | 192 | 192 | 0 |
| print_direct_v3 | bound_one | 192 | 192 | 0 |
| print_direct_v3 | stored_result_one | 192 | 192 | 0 |
| print_direct_v3 | literal_three | 192 | 192 | 0 |
| print_direct_v3 | bound_three | 192 | 192 | 0 |
| print_direct_v3 | stored_intermediates_three | 192 | 192 | 0 |
| print_trace_long_v1 | literal_output | 48 | 52 | 44 |
| print_trace_long_v1 | stored_output | 48 | 52 | 44 |
| print_trace_long_v1 | literal_one | 192 | 192 | 0 |
| print_trace_long_v1 | bound_one | 192 | 192 | 0 |
| print_trace_long_v1 | stored_result_one | 192 | 192 | 0 |
| print_trace_long_v1 | literal_three | 192 | 192 | 0 |
| print_trace_long_v1 | bound_three | 192 | 192 | 0 |
| print_trace_long_v1 | stored_intermediates_three | 192 | 192 | 0 |

## Token geometry

Lengths use saved prompt and generated token IDs, including invalid completions. Missing token IDs in software fixtures remain unreported. Different forms and protocols change token geometry.

| Protocol | Form | Split | Prompt tokens min/max/mean | Generated tokens min/max/mean |
|---|---|---|---|---|
| print_direct_v3 | bound_one | all | 53/55/53.85 | 3/5/4.03 |
| print_direct_v3 | bound_one | development | 53/55/53.89 | 3/5/4.02 |
| print_direct_v3 | bound_one | train | 53/55/53.81 | 3/5/4.05 |
| print_direct_v3 | bound_three | all | 68/72/69.92 | 3/16/4.57 |
| print_direct_v3 | bound_three | development | 68/72/69.94 | 3/16/4.57 |
| print_direct_v3 | bound_three | train | 68/71/69.90 | 3/16/4.57 |
| print_direct_v3 | literal_one | all | 44/46/44.85 | 3/5/4.11 |
| print_direct_v3 | literal_one | development | 44/46/44.89 | 3/5/4.10 |
| print_direct_v3 | literal_one | train | 44/46/44.81 | 3/5/4.12 |
| print_direct_v3 | literal_output | all | 41/42/41.41 | 3/5/3.91 |
| print_direct_v3 | literal_output | development | 41/42/41.39 | 3/5/3.89 |
| print_direct_v3 | literal_output | train | 41/42/41.43 | 3/5/3.93 |
| print_direct_v3 | literal_three | all | 50/54/51.92 | 3/7/4.39 |
| print_direct_v3 | literal_three | development | 50/54/51.94 | 3/7/4.39 |
| print_direct_v3 | literal_three | train | 50/53/51.90 | 3/7/4.39 |
| print_direct_v3 | stored_intermediates_three | all | 59/63/60.92 | 3/5/4.61 |
| print_direct_v3 | stored_intermediates_three | development | 59/63/60.94 | 3/5/4.62 |
| print_direct_v3 | stored_intermediates_three | train | 59/62/60.90 | 3/5/4.60 |
| print_direct_v3 | stored_output | all | 46/47/46.41 | 3/5/3.91 |
| print_direct_v3 | stored_output | development | 46/47/46.39 | 3/5/3.89 |
| print_direct_v3 | stored_output | train | 46/47/46.43 | 3/5/3.93 |
| print_direct_v3 | stored_result_one | all | 49/51/49.85 | 3/5/4.10 |
| print_direct_v3 | stored_result_one | development | 49/51/49.89 | 3/5/4.10 |
| print_direct_v3 | stored_result_one | train | 49/51/49.81 | 3/5/4.11 |
| print_trace_long_v1 | bound_one | all | 69/71/69.85 | 60/141/123.24 |
| print_trace_long_v1 | bound_one | development | 69/71/69.89 | 60/141/122.72 |
| print_trace_long_v1 | bound_one | train | 69/71/69.81 | 60/141/123.77 |
| print_trace_long_v1 | bound_three | all | 84/88/85.92 | 83/259/102.42 |
| print_trace_long_v1 | bound_three | development | 84/88/85.94 | 83/259/103.07 |
| print_trace_long_v1 | bound_three | train | 84/87/85.90 | 83/244/101.77 |
| print_trace_long_v1 | literal_one | all | 60/62/60.85 | 23/158/67.73 |
| print_trace_long_v1 | literal_one | development | 60/62/60.89 | 23/139/66.74 |
| print_trace_long_v1 | literal_one | train | 60/62/60.81 | 23/158/68.72 |
| print_trace_long_v1 | literal_output | all | 57/58/57.41 | 18/20/18.74 |
| print_trace_long_v1 | literal_output | development | 57/58/57.39 | 18/20/18.71 |
| print_trace_long_v1 | literal_output | train | 57/58/57.43 | 18/20/18.78 |
| print_trace_long_v1 | literal_three | all | 66/70/67.92 | 67/364/102.17 |
| print_trace_long_v1 | literal_three | development | 66/70/67.94 | 67/175/100.64 |
| print_trace_long_v1 | literal_three | train | 66/69/67.90 | 75/364/103.70 |
| print_trace_long_v1 | stored_intermediates_three | all | 75/79/76.92 | 113/234/160.39 |
| print_trace_long_v1 | stored_intermediates_three | development | 75/79/76.94 | 114/232/160.10 |
| print_trace_long_v1 | stored_intermediates_three | train | 75/78/76.90 | 113/234/160.67 |
| print_trace_long_v1 | stored_output | all | 62/63/62.41 | 40/85/74.77 |
| print_trace_long_v1 | stored_output | development | 62/63/62.39 | 40/85/74.35 |
| print_trace_long_v1 | stored_output | train | 62/63/62.43 | 40/85/75.18 |
| print_trace_long_v1 | stored_result_one | all | 65/67/65.85 | 86/221/119.05 |
| print_trace_long_v1 | stored_result_one | development | 65/67/65.89 | 86/213/117.46 |
| print_trace_long_v1 | stored_result_one | train | 65/67/65.81 | 86/221/120.63 |

## Paired form contrasts

Positive differences favor the left form. Sign-mirrored relatives are sampled together using paired_group_id; all registered contrasts remain reported. These intervals have no multiplicity adjustment.

| Protocol | Split | Contrast (left minus right) | Pairs | Numeric-relative groups | Difference | Exploratory 95% interval |
|---|---|---|---:|---:|---:|---|
| print_direct_v3 | all | three_literal_minus_one_literal | 384 | 192 | -72.14% | [-76.04%, -67.97%] |
| print_direct_v3 | all | one_bound_minus_literal | 384 | 192 | +3.39% | [-0.26%, +7.03%] |
| print_direct_v3 | all | three_stored_intermediates_minus_literal | 384 | 192 | -4.43% | [-7.29%, -1.56%] |
| print_direct_v3 | all | three_bound_minus_literal | 384 | 192 | -2.34% | [-4.69%, +0.00%] |
| print_direct_v3 | all | one_stored_result_minus_literal | 384 | 192 | -1.04% | [-2.60%, +0.52%] |
| print_direct_v3 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | train | three_literal_minus_one_literal | 192 | 96 | -69.79% | [-76.56%, -63.02%] |
| print_direct_v3 | train | one_bound_minus_literal | 192 | 96 | +5.21% | [+0.00%, +10.42%] |
| print_direct_v3 | train | three_stored_intermediates_minus_literal | 192 | 96 | -7.29% | [-11.46%, -3.12%] |
| print_direct_v3 | train | three_bound_minus_literal | 192 | 96 | -3.12% | [-7.29%, +0.53%] |
| print_direct_v3 | train | one_stored_result_minus_literal | 192 | 96 | -1.56% | [-3.65%, +0.52%] |
| print_direct_v3 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | development | three_literal_minus_one_literal | 192 | 96 | -74.48% | [-79.69%, -69.27%] |
| print_direct_v3 | development | one_bound_minus_literal | 192 | 96 | +1.56% | [-3.65%, +7.29%] |
| print_direct_v3 | development | three_stored_intermediates_minus_literal | 192 | 96 | -1.56% | [-5.73%, +2.08%] |
| print_direct_v3 | development | three_bound_minus_literal | 192 | 96 | -1.56% | [-4.17%, +1.04%] |
| print_direct_v3 | development | one_stored_result_minus_literal | 192 | 96 | -0.52% | [-2.08%, +1.04%] |
| print_direct_v3 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_trace_long_v1 | all | three_literal_minus_one_literal | 384 | 192 | -9.90% | [-15.36%, -4.69%] |
| print_trace_long_v1 | all | one_bound_minus_literal | 384 | 192 | +5.47% | [+1.04%, +9.64%] |
| print_trace_long_v1 | all | three_stored_intermediates_minus_literal | 384 | 192 | +19.79% | [+14.32%, +25.26%] |
| print_trace_long_v1 | all | three_bound_minus_literal | 384 | 192 | -57.81% | [-62.50%, -53.12%] |
| print_trace_long_v1 | all | one_stored_result_minus_literal | 384 | 192 | +5.73% | [+1.04%, +10.42%] |
| print_trace_long_v1 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| print_trace_long_v1 | train | three_literal_minus_one_literal | 192 | 96 | -5.73% | [-13.02%, +1.56%] |
| print_trace_long_v1 | train | one_bound_minus_literal | 192 | 96 | +7.81% | [+2.60%, +13.54%] |
| print_trace_long_v1 | train | three_stored_intermediates_minus_literal | 192 | 96 | +16.67% | [+9.90%, +23.44%] |
| print_trace_long_v1 | train | three_bound_minus_literal | 192 | 96 | -61.46% | [-67.71%, -55.21%] |
| print_trace_long_v1 | train | one_stored_result_minus_literal | 192 | 96 | +7.29% | [+1.04%, +13.54%] |
| print_trace_long_v1 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_trace_long_v1 | development | three_literal_minus_one_literal | 192 | 96 | -14.06% | [-21.88%, -6.25%] |
| print_trace_long_v1 | development | one_bound_minus_literal | 192 | 96 | +3.12% | [-3.65%, +9.90%] |
| print_trace_long_v1 | development | three_stored_intermediates_minus_literal | 192 | 96 | +22.92% | [+15.10%, +31.25%] |
| print_trace_long_v1 | development | three_bound_minus_literal | 192 | 96 | -54.17% | [-60.94%, -46.88%] |
| print_trace_long_v1 | development | one_stored_result_minus_literal | 192 | 96 | +4.17% | [-2.60%, +10.42%] |
| print_trace_long_v1 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |

No new mechanism claim, model training, frozen forecast or original final/extrapolation evaluation follows automatically from these descriptive results.
