
## 2026-09-15 — E1 and E2 (pilot) on one h200 worker

E1: spans resolve for all 11 tokenizers in every regime (0 unresolved). Seven lure names are two
tokens on some tokenizers; span positions absorb that.

E2 pilot, level 3, 200 sets per target, four regimes, two models (~30 min of GPU in total).
Two bugs found and fixed from the stored generations, no rerun needed:
1. CodeLlama's trace continued past the blank line into invented problems, and the parser took
   the last `Answer:` — the same bug class as the arithmetic parser. Few-shot parsing now always
   cuts at the first blank line; a stopping criterion on the decoded tail ends generation there
   (Llama-2 tokenizers emit a blank line as two tokens, so no eos id catches it). CodeLlama trace
   accuracy 10% → 95%.
2. The codechain regime was truncated at 200 tokens for Llama-3.1-8B (parse rate 31–74%); now 448.

After the fix (lure excess = lure rate minus the matched neutral twin's rate of that digit):

| model | regime | target | acc (neutral) | lure | pseudo | excess |
|---|---|---|---|---|---|---|
| llama31-8b-it | direct | queried | 26.5 (29.5) | 14.5% | 12.0% | +2.5 |
| llama31-8b-it | direct | intermediate | 37.0 (38.0) | 23.0% | 20.5% | +2.5 |
| llama31-8b-it | trace | queried | 99.5 (99.5) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | trace | intermediate | 99.0 (99.5) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | prose | queried | 100.0 (100.0) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | prose | intermediate | 100.0 (100.0) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | codechain | queried | 15.0 (21.5) | 5.5% | 10.0% | -4.5 |
| llama31-8b-it | codechain | intermediate | 18.0 (30.5) | 5.0% | 16.0% | -11.0 |
| codellama-7b-it | direct | queried | 19.5 (20.5) | 12.5% | 11.0% | +1.5 |
| codellama-7b-it | direct | intermediate | 26.0 (26.0) | 19.5% | 23.0% | -3.5 |
| codellama-7b-it | trace | queried | 96.0 (96.0) | 0.0% | 0.0% | +0.0 |
| codellama-7b-it | trace | intermediate | 81.5 (95.0) | 2.0% | 0.0% | +2.0 |
| codellama-7b-it | prose | queried | 96.0 (93.5) | 0.5% | 0.5% | +0.0 |
| codellama-7b-it | prose | intermediate | 90.0 (94.0) | 0.5% | 1.5% | -1.0 |
| codellama-7b-it | codechain | queried | 24.0 (21.5) | 11.5% | 11.5% | +0.0 |
| codellama-7b-it | codechain | intermediate | 27.0 (28.5) | 19.0% | 22.0% | -3.0 |

Reading: (a) without a chain both models are near the floor (20–34%) and the **pseudo-lure is
high (11–23%)** because the implied quantities (len, sum, max, min of xs) are exactly the wrong
answers a failing model produces anyway — the matched-twin baseline is essential here, more than
in arithmetic, and the direct-regime excess is small (+1.5 to +2.5, CodeLlama intermediate −3.5).
(b) Trace and prose are at or near ceiling for both models, with zero lure: no variance for P3
at level 3 on these models. (c) **CodeLlama, trace regime, misleading name on the intermediate:
accuracy 81.5% against 95.5% neutral**, a 14-point interference under a chain that writes every
value — the first sign that code differs from arithmetic; needs the lure/pseudo split and more
seeds before it is a claim. (d) codechain (comments, no values) does not protect CodeLlama:
same accuracy and lure as direct.

Round 2 queued: level 5 for both pilot models; levels 3 and 5 for OLMo-2-1B and Llama-3.2-3B
(weak models, to get cells off the ceiling); codechain rerun for Llama-8B at 448 tokens.
