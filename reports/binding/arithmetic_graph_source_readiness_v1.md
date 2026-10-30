# Arithmetic graph source-only readiness

This is a source/oracle audit, not model performance. Numeric, lexical and query relatives remain grouped.

| Behavior split | Rows | Query reads an arithmetic-written slot | Query reads an untouched literal |
|---|---:|---:|---:|
| train | 864 | 576 | 288 |
| development | 288 | 216 | 72 |

The generated-answer summary pools these query types. Its overall accuracy cannot establish a reliable computed-only regime; morning analysis must separate them.

| Slot | TRAIN value classes | DEV value classes | DEV rows with unseen class |
|---|---:|---:|---:|
| 0 | 34 | 30 | 40 |
| 1 | 35 | 31 | 16 |
| 2 | 36 | 31 | 16 |
| 3 | 36 | 23 | 8 |

All 48 relation cells meet the prospectively fixed TRAIN support rule at all three sites. DEV class support remains separately recorded. The fixed numeric domain is [-96,96]; class support must accompany interpretation of categorical value accuracy. No values or these support summaries enter hidden-probe inputs.
