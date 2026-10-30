# Arithmetic and readout feasibility: meta-llama/Llama-3.1-8B-Instruct

All 6,144 registered responses retained: 4,466 correct and 6 invalid across 384 numeric tuples. Execution/audit status: complete and passed.

Fresh numeric calibration on repeated arithmetic structures, not structural generalization or a causal mechanism test. One versus three operations also changes intermediate literal exposure; storage forms change assignments, dependencies and token distances. Trace responses change computation and generation allowance and are never pooled with direct answers. Intervals are exploratory without multiplicity adjustment. Historical failed gates and sealed final/extrapolation outcomes remain unchanged.

Each protocol has its own fixed gate. Every nonzero-operation form × split × sign-stratum cell must reach at least 90% accuracy, at most 5% invalid responses and n ≥ 24. Numeric development qualifies only after training qualification; no alternate protocol is substituted after failure. Zero-operation controls remain visible separately.

| Protocol | Training qualified | Numeric development qualified | Reliability |
|---|---|---|---|
| print_direct_v3 | False | False | failed |
| print_trace_long_v1 | False | False | failed |

## All forms by protocol and split

| Protocol | Form | Split | Correct / n | Unique prompts | Invalid | Accuracy Wilson 95% |
|---|---|---|---:|---:|---:|---|
| print_direct_v3 | bound_one | all | 351/384 | 384 | 0 | [88.2%, 93.8%] |
| print_direct_v3 | bound_one | development | 177/192 | 192 | 0 | [87.5%, 95.2%] |
| print_direct_v3 | bound_one | train | 174/192 | 192 | 0 | [85.7%, 94.0%] |
| print_direct_v3 | bound_three | all | 26/384 | 384 | 0 | [4.7%, 9.7%] |
| print_direct_v3 | bound_three | development | 12/192 | 192 | 0 | [3.6%, 10.6%] |
| print_direct_v3 | bound_three | train | 14/192 | 192 | 0 | [4.4%, 11.9%] |
| print_direct_v3 | literal_one | all | 320/384 | 384 | 0 | [79.3%, 86.7%] |
| print_direct_v3 | literal_one | development | 160/192 | 192 | 0 | [77.4%, 87.9%] |
| print_direct_v3 | literal_one | train | 160/192 | 192 | 0 | [77.4%, 87.9%] |
| print_direct_v3 | literal_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_direct_v3 | literal_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | literal_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | literal_three | all | 98/384 | 384 | 0 | [21.4%, 30.1%] |
| print_direct_v3 | literal_three | development | 46/192 | 192 | 0 | [18.5%, 30.5%] |
| print_direct_v3 | literal_three | train | 52/192 | 192 | 0 | [21.3%, 33.8%] |
| print_direct_v3 | stored_intermediates_three | all | 10/384 | 384 | 0 | [1.4%, 4.7%] |
| print_direct_v3 | stored_intermediates_three | development | 4/192 | 192 | 0 | [0.8%, 5.2%] |
| print_direct_v3 | stored_intermediates_three | train | 6/192 | 192 | 0 | [1.4%, 6.6%] |
| print_direct_v3 | stored_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_direct_v3 | stored_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | stored_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_direct_v3 | stored_result_one | all | 320/384 | 384 | 0 | [79.3%, 86.7%] |
| print_direct_v3 | stored_result_one | development | 160/192 | 192 | 0 | [77.4%, 87.9%] |
| print_direct_v3 | stored_result_one | train | 160/192 | 192 | 0 | [77.4%, 87.9%] |
| print_trace_long_v1 | bound_one | all | 384/384 | 384 | 0 | [99.0%, 100.0%] |
| print_trace_long_v1 | bound_one | development | 192/192 | 192 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | bound_one | train | 192/192 | 192 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | bound_three | all | 227/384 | 384 | 0 | [54.1%, 63.9%] |
| print_trace_long_v1 | bound_three | development | 114/192 | 192 | 0 | [52.3%, 66.1%] |
| print_trace_long_v1 | bound_three | train | 113/192 | 192 | 0 | [51.8%, 65.6%] |
| print_trace_long_v1 | literal_one | all | 214/384 | 384 | 2 | [50.7%, 60.6%] |
| print_trace_long_v1 | literal_one | development | 104/192 | 192 | 0 | [47.1%, 61.1%] |
| print_trace_long_v1 | literal_one | train | 110/192 | 192 | 2 | [50.2%, 64.1%] |
| print_trace_long_v1 | literal_output | all | 384/384 | 56 | 0 | [99.0%, 100.0%] |
| print_trace_long_v1 | literal_output | development | 192/192 | 52 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | literal_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | literal_three | all | 299/384 | 384 | 0 | [73.4%, 81.7%] |
| print_trace_long_v1 | literal_three | development | 153/192 | 192 | 0 | [73.4%, 84.8%] |
| print_trace_long_v1 | literal_three | train | 146/192 | 192 | 0 | [69.5%, 81.5%] |
| print_trace_long_v1 | stored_intermediates_three | all | 357/384 | 384 | 0 | [90.0%, 95.1%] |
| print_trace_long_v1 | stored_intermediates_three | development | 180/192 | 192 | 0 | [89.4%, 96.4%] |
| print_trace_long_v1 | stored_intermediates_three | train | 177/192 | 192 | 0 | [87.5%, 95.2%] |
| print_trace_long_v1 | stored_output | all | 382/384 | 56 | 2 | [98.1%, 99.9%] |
| print_trace_long_v1 | stored_output | development | 190/192 | 52 | 2 | [96.3%, 99.7%] |
| print_trace_long_v1 | stored_output | train | 192/192 | 48 | 0 | [98.0%, 100.0%] |
| print_trace_long_v1 | stored_result_one | all | 326/384 | 384 | 2 | [81.0%, 88.1%] |
| print_trace_long_v1 | stored_result_one | development | 163/192 | 192 | 2 | [79.1%, 89.3%] |
| print_trace_long_v1 | stored_result_one | train | 163/192 | 192 | 0 | [79.1%, 89.3%] |

## Complete sign-stratified cells

Cell Wilson intervals are descriptive binomial intervals, not structural-generalization uncertainty. Zero-operation controls repeat exact deterministic prompts, report unique counts, and cannot be treated as independent numeric generalization evidence. Paired contrasts bootstrap whole numeric-relative groups; repeated templates are not independent structural replications.

| Protocol | Form | Split | Signs (r,s,y) | Correct / n | Unique prompts | Invalid | Accuracy Wilson 95% |
|---|---|---|---|---:|---:|---:|---|
| print_direct_v3 | bound_one | development | −,−,− | 17/32 | 32 | 0 | [36.4%, 69.1%] |
| print_direct_v3 | bound_one | development | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | −,−,− | 14/32 | 32 | 0 | [28.2%, 60.7%] |
| print_direct_v3 | bound_one | train | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | bound_three | development | −,−,− | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_direct_v3 | bound_three | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | −,+,− | 3/32 | 32 | 0 | [3.2%, 24.2%] |
| print_direct_v3 | bound_three | development | +,−,+ | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | bound_three | development | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | development | +,+,+ | 5/32 | 32 | 0 | [6.9%, 31.8%] |
| print_direct_v3 | bound_three | train | −,−,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_direct_v3 | bound_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | −,+,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_direct_v3 | bound_three | train | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | bound_three | train | +,+,+ | 6/32 | 32 | 0 | [8.9%, 35.3%] |
| print_direct_v3 | literal_one | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_one | development | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_one | train | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | literal_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
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
| print_direct_v3 | literal_three | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | development | −,−,+ | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | literal_three | development | −,+,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_direct_v3 | literal_three | development | +,−,+ | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_direct_v3 | literal_three | development | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | development | +,+,+ | 26/32 | 32 | 0 | [64.7%, 91.1%] |
| print_direct_v3 | literal_three | train | −,−,− | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_direct_v3 | literal_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | literal_three | train | −,+,− | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_direct_v3 | literal_three | train | +,−,+ | 11/32 | 32 | 0 | [20.4%, 51.7%] |
| print_direct_v3 | literal_three | train | +,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | literal_three | train | +,+,+ | 28/32 | 32 | 0 | [71.9%, 95.0%] |
| print_direct_v3 | stored_intermediates_three | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | −,+,− | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_direct_v3 | stored_intermediates_three | development | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | development | +,+,+ | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_direct_v3 | stored_intermediates_three | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | −,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | −,+,− | 1/32 | 32 | 0 | [0.6%, 15.7%] |
| print_direct_v3 | stored_intermediates_three | train | +,−,+ | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | +,+,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_intermediates_three | train | +,+,+ | 5/32 | 32 | 0 | [6.9%, 31.8%] |
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
| print_direct_v3 | stored_result_one | development | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_result_one | development | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | −,−,− | 0/32 | 32 | 0 | [0.0%, 10.7%] |
| print_direct_v3 | stored_result_one | train | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_direct_v3 | stored_result_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | −,−,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | −,−,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | −,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_one | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | development | −,−,− | 2/32 | 32 | 0 | [1.7%, 20.1%] |
| print_trace_long_v1 | bound_three | development | −,−,+ | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_trace_long_v1 | bound_three | development | −,+,− | 6/32 | 32 | 0 | [8.9%, 35.3%] |
| print_trace_long_v1 | bound_three | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | train | −,−,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_trace_long_v1 | bound_three | train | −,−,+ | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_trace_long_v1 | bound_three | train | −,+,− | 4/32 | 32 | 0 | [5.0%, 28.1%] |
| print_trace_long_v1 | bound_three | train | +,−,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | bound_three | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | bound_three | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | development | −,−,− | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_trace_long_v1 | literal_one | development | −,−,+ | 9/32 | 32 | 0 | [15.6%, 45.4%] |
| print_trace_long_v1 | literal_one | development | −,+,− | 15/32 | 32 | 0 | [30.9%, 63.6%] |
| print_trace_long_v1 | literal_one | development | +,−,+ | 7/32 | 32 | 0 | [11.0%, 38.8%] |
| print_trace_long_v1 | literal_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | train | −,−,− | 10/32 | 32 | 0 | [18.0%, 48.6%] |
| print_trace_long_v1 | literal_one | train | −,−,+ | 11/32 | 32 | 0 | [20.4%, 51.7%] |
| print_trace_long_v1 | literal_one | train | −,+,− | 14/32 | 32 | 2 | [28.2%, 60.7%] |
| print_trace_long_v1 | literal_one | train | +,−,+ | 12/32 | 32 | 0 | [22.9%, 54.7%] |
| print_trace_long_v1 | literal_one | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_one | train | +,+,+ | 31/32 | 32 | 0 | [84.3%, 99.4%] |
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
| print_trace_long_v1 | literal_three | development | −,−,− | 17/32 | 32 | 0 | [36.4%, 69.1%] |
| print_trace_long_v1 | literal_three | development | −,−,+ | 19/32 | 32 | 0 | [42.3%, 74.5%] |
| print_trace_long_v1 | literal_three | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_three | development | +,−,+ | 25/32 | 32 | 0 | [61.2%, 89.0%] |
| print_trace_long_v1 | literal_three | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_three | development | +,+,+ | 28/32 | 32 | 0 | [71.9%, 95.0%] |
| print_trace_long_v1 | literal_three | train | −,−,− | 11/32 | 32 | 0 | [20.4%, 51.7%] |
| print_trace_long_v1 | literal_three | train | −,−,+ | 22/32 | 32 | 0 | [51.4%, 82.0%] |
| print_trace_long_v1 | literal_three | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | literal_three | train | +,−,+ | 22/32 | 32 | 0 | [51.4%, 82.0%] |
| print_trace_long_v1 | literal_three | train | +,+,− | 30/32 | 32 | 0 | [79.9%, 98.3%] |
| print_trace_long_v1 | literal_three | train | +,+,+ | 29/32 | 32 | 0 | [75.8%, 96.8%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,−,− | 24/32 | 32 | 0 | [57.9%, 86.7%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,−,+ | 28/32 | 32 | 0 | [71.9%, 95.0%] |
| print_trace_long_v1 | stored_intermediates_three | development | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,−,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,−,− | 27/32 | 32 | 0 | [68.2%, 93.1%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,−,+ | 24/32 | 32 | 0 | [57.9%, 86.7%] |
| print_trace_long_v1 | stored_intermediates_three | train | −,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,−,+ | 30/32 | 32 | 0 | [79.9%, 98.3%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_intermediates_three | train | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_output | development | −,−,− | 30/32 | 14 | 2 | [79.9%, 98.3%] |
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
| print_trace_long_v1 | stored_result_one | development | −,−,− | 28/32 | 32 | 0 | [71.9%, 95.0%] |
| print_trace_long_v1 | stored_result_one | development | −,−,+ | 24/32 | 32 | 1 | [57.9%, 86.7%] |
| print_trace_long_v1 | stored_result_one | development | −,+,− | 30/32 | 32 | 0 | [79.9%, 98.3%] |
| print_trace_long_v1 | stored_result_one | development | +,−,+ | 17/32 | 32 | 1 | [36.4%, 69.1%] |
| print_trace_long_v1 | stored_result_one | development | +,+,− | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | development | +,+,+ | 32/32 | 32 | 0 | [89.3%, 100.0%] |
| print_trace_long_v1 | stored_result_one | train | −,−,− | 31/32 | 32 | 0 | [84.3%, 99.4%] |
| print_trace_long_v1 | stored_result_one | train | −,−,+ | 21/32 | 32 | 0 | [48.3%, 79.6%] |
| print_trace_long_v1 | stored_result_one | train | −,+,− | 27/32 | 32 | 0 | [68.2%, 93.1%] |
| print_trace_long_v1 | stored_result_one | train | +,−,+ | 20/32 | 32 | 0 | [45.3%, 77.1%] |
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
| print_direct_v3 | bound_one | all | 75/75/75.00 | 3/3/3.00 |
| print_direct_v3 | bound_one | development | 75/75/75.00 | 3/3/3.00 |
| print_direct_v3 | bound_one | train | 75/75/75.00 | 3/3/3.00 |
| print_direct_v3 | bound_three | all | 90/90/90.00 | 3/3/3.00 |
| print_direct_v3 | bound_three | development | 90/90/90.00 | 3/3/3.00 |
| print_direct_v3 | bound_three | train | 90/90/90.00 | 3/3/3.00 |
| print_direct_v3 | literal_one | all | 67/67/67.00 | 3/3/3.00 |
| print_direct_v3 | literal_one | development | 67/67/67.00 | 3/3/3.00 |
| print_direct_v3 | literal_one | train | 67/67/67.00 | 3/3/3.00 |
| print_direct_v3 | literal_output | all | 64/64/64.00 | 3/3/3.00 |
| print_direct_v3 | literal_output | development | 64/64/64.00 | 3/3/3.00 |
| print_direct_v3 | literal_output | train | 64/64/64.00 | 3/3/3.00 |
| print_direct_v3 | literal_three | all | 73/73/73.00 | 3/4/3.00 |
| print_direct_v3 | literal_three | development | 73/73/73.00 | 3/3/3.00 |
| print_direct_v3 | literal_three | train | 73/73/73.00 | 3/4/3.01 |
| print_direct_v3 | stored_intermediates_three | all | 81/81/81.00 | 3/3/3.00 |
| print_direct_v3 | stored_intermediates_three | development | 81/81/81.00 | 3/3/3.00 |
| print_direct_v3 | stored_intermediates_three | train | 81/81/81.00 | 3/3/3.00 |
| print_direct_v3 | stored_output | all | 68/68/68.00 | 3/3/3.00 |
| print_direct_v3 | stored_output | development | 68/68/68.00 | 3/3/3.00 |
| print_direct_v3 | stored_output | train | 68/68/68.00 | 3/3/3.00 |
| print_direct_v3 | stored_result_one | all | 71/71/71.00 | 3/3/3.00 |
| print_direct_v3 | stored_result_one | development | 71/71/71.00 | 3/3/3.00 |
| print_direct_v3 | stored_result_one | train | 71/71/71.00 | 3/3/3.00 |
| print_trace_long_v1 | bound_one | all | 90/90/90.00 | 115/197/142.05 |
| print_trace_long_v1 | bound_one | development | 90/90/90.00 | 115/197/143.11 |
| print_trace_long_v1 | bound_one | train | 90/90/90.00 | 115/197/140.99 |
| print_trace_long_v1 | bound_three | all | 105/105/105.00 | 184/327/218.44 |
| print_trace_long_v1 | bound_three | development | 105/105/105.00 | 185/327/217.17 |
| print_trace_long_v1 | bound_three | train | 105/105/105.00 | 184/324/219.70 |
| print_trace_long_v1 | literal_one | all | 82/82/82.00 | 100/512/190.01 |
| print_trace_long_v1 | literal_one | development | 82/82/82.00 | 100/296/187.42 |
| print_trace_long_v1 | literal_one | train | 82/82/82.00 | 101/512/192.59 |
| print_trace_long_v1 | literal_output | all | 79/79/79.00 | 63/160/116.34 |
| print_trace_long_v1 | literal_output | development | 79/79/79.00 | 63/160/117.43 |
| print_trace_long_v1 | literal_output | train | 79/79/79.00 | 63/160/115.24 |
| print_trace_long_v1 | literal_three | all | 88/88/88.00 | 86/354/146.79 |
| print_trace_long_v1 | literal_three | development | 88/88/88.00 | 91/232/147.08 |
| print_trace_long_v1 | literal_three | train | 88/88/88.00 | 86/354/146.51 |
| print_trace_long_v1 | stored_intermediates_three | all | 96/96/96.00 | 139/312/205.76 |
| print_trace_long_v1 | stored_intermediates_three | development | 96/96/96.00 | 139/300/204.91 |
| print_trace_long_v1 | stored_intermediates_three | train | 96/96/96.00 | 142/312/206.61 |
| print_trace_long_v1 | stored_output | all | 83/83/83.00 | 70/146/109.92 |
| print_trace_long_v1 | stored_output | development | 83/83/83.00 | 70/143/110.29 |
| print_trace_long_v1 | stored_output | train | 83/83/83.00 | 70/146/109.56 |
| print_trace_long_v1 | stored_result_one | all | 86/86/86.00 | 102/512/168.06 |
| print_trace_long_v1 | stored_result_one | development | 86/86/86.00 | 114/512/173.03 |
| print_trace_long_v1 | stored_result_one | train | 86/86/86.00 | 102/313/163.08 |

## Paired form contrasts

Positive differences favor the left form. Sign-mirrored relatives are sampled together using paired_group_id; all registered contrasts remain reported. These intervals have no multiplicity adjustment.

| Protocol | Split | Contrast (left minus right) | Pairs | Numeric-relative groups | Difference | Exploratory 95% interval |
|---|---|---|---:|---:|---:|---|
| print_direct_v3 | all | three_literal_minus_one_literal | 384 | 192 | -57.81% | [-63.80%, -51.82%] |
| print_direct_v3 | all | one_bound_minus_literal | 384 | 192 | +8.07% | [+5.47%, +10.68%] |
| print_direct_v3 | all | three_stored_intermediates_minus_literal | 384 | 192 | -22.92% | [-26.82%, -18.75%] |
| print_direct_v3 | all | three_bound_minus_literal | 384 | 192 | -18.75% | [-22.92%, -14.58%] |
| print_direct_v3 | all | one_stored_result_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | train | three_literal_minus_one_literal | 192 | 96 | -56.25% | [-65.10%, -47.38%] |
| print_direct_v3 | train | one_bound_minus_literal | 192 | 96 | +7.29% | [+4.17%, +10.94%] |
| print_direct_v3 | train | three_stored_intermediates_minus_literal | 192 | 96 | -23.96% | [-29.69%, -18.23%] |
| print_direct_v3 | train | three_bound_minus_literal | 192 | 96 | -19.79% | [-25.52%, -14.06%] |
| print_direct_v3 | train | one_stored_result_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | development | three_literal_minus_one_literal | 192 | 96 | -59.38% | [-68.23%, -50.52%] |
| print_direct_v3 | development | one_bound_minus_literal | 192 | 96 | +8.85% | [+4.69%, +13.02%] |
| print_direct_v3 | development | three_stored_intermediates_minus_literal | 192 | 96 | -21.88% | [-28.12%, -16.15%] |
| print_direct_v3 | development | three_bound_minus_literal | 192 | 96 | -17.71% | [-23.96%, -11.46%] |
| print_direct_v3 | development | one_stored_result_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_direct_v3 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_trace_long_v1 | all | three_literal_minus_one_literal | 384 | 192 | +22.14% | [+16.41%, +28.12%] |
| print_trace_long_v1 | all | one_bound_minus_literal | 384 | 192 | +44.27% | [+40.36%, +48.44%] |
| print_trace_long_v1 | all | three_stored_intermediates_minus_literal | 384 | 192 | +15.10% | [+10.94%, +19.01%] |
| print_trace_long_v1 | all | three_bound_minus_literal | 384 | 192 | -18.75% | [-23.70%, -13.80%] |
| print_trace_long_v1 | all | one_stored_result_minus_literal | 384 | 192 | +29.17% | [+24.22%, +34.38%] |
| print_trace_long_v1 | all | zero_stored_minus_literal | 384 | 192 | -0.52% | [-1.30%, +0.00%] |
| print_trace_long_v1 | train | three_literal_minus_one_literal | 192 | 96 | +18.75% | [+10.94%, +26.56%] |
| print_trace_long_v1 | train | one_bound_minus_literal | 192 | 96 | +42.71% | [+36.46%, +48.96%] |
| print_trace_long_v1 | train | three_stored_intermediates_minus_literal | 192 | 96 | +16.15% | [+10.42%, +21.88%] |
| print_trace_long_v1 | train | three_bound_minus_literal | 192 | 96 | -17.19% | [-23.96%, -10.42%] |
| print_trace_long_v1 | train | one_stored_result_minus_literal | 192 | 96 | +27.60% | [+19.79%, +35.42%] |
| print_trace_long_v1 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| print_trace_long_v1 | development | three_literal_minus_one_literal | 192 | 96 | +25.52% | [+17.19%, +33.85%] |
| print_trace_long_v1 | development | one_bound_minus_literal | 192 | 96 | +45.83% | [+40.10%, +52.08%] |
| print_trace_long_v1 | development | three_stored_intermediates_minus_literal | 192 | 96 | +14.06% | [+8.33%, +19.79%] |
| print_trace_long_v1 | development | three_bound_minus_literal | 192 | 96 | -20.31% | [-26.56%, -14.06%] |
| print_trace_long_v1 | development | one_stored_result_minus_literal | 192 | 96 | +30.73% | [+23.96%, +37.50%] |
| print_trace_long_v1 | development | zero_stored_minus_literal | 192 | 96 | -1.04% | [-2.60%, +0.00%] |

No new mechanism claim, model training, frozen forecast or original final/extrapolation evaluation follows automatically from these descriptive results.
