# Compression and numeric encoding: first exploratory wave

October 31, 2026. Implements E1/E2 of the [exploratory roadmap](arithmetic_exploration_20261031_plan_v1.md). Existing structural DEV has already been inspected: every result from this wave is adaptive discovery, not confirmation. Preserve completed work and sealed final outcomes. No language-model inference, backbone training or causal interventions occur in this wave.

## Fixed assay

Use the complete archived local cohort (216 structural TRAIN families, 72 DEV, six calibration), with all numeric/lexical relatives grouped. Fit root-definition and computed-definition readouts separately. Operand-use roles and new temporal sites are deferred to a separate protocol. Fix layers to 24 for Llama 8B and 36 for CodeLlama 34B, before fitting; this wave does not select a new layer.

This changes the previous shared-role assay: role-specific models have their own normalization/intercept and 12 supplied statement/depth coordinates. Compare feature widths within this new assay; do not attribute changes from the previous study solely to projection rank. Feature metadata contains no numeric targets, true parent, version or current-binding pointer. Root definitions are copying positive controls; computed definitions remain the primary scientific target.

## Feature widths and shared controls

Hidden widths are 64/256/1024/unprojected (4096 for 8B, 8192 for 34B). A fixed 1024-column random-sign map per seed has the original 64-column sign map as its first block, with remaining columns generated independently. The r-column prefix is divided by sqrt(r), so compressed representations are nested. Floating GEMM geometry may differ from older captures' projection application; the original results are preserved rather than refitted.

Extract only definition nodes at the fixed layer, streaming and checksum-validating archived capture chunks. Preserve raw states and all three 1024-dimensional projected banks as checksummed local arrays. No model is loaded. Completed cache and fitting receipts are immutable; interrupted preprocessing may be reconstructed from the immutable raw captures without new model queries.

The source comparator uses character 3–5-gram features of the actual source prefix through the definition end, excluding chat-template text and future source. Build one model-independent 8192-column signed hash bank. Smaller power-of-two widths are exact column folds of that bank; verify folding against direct hashing. Fit source widths 64/256/1024/4096/8192 once per role and share corresponding fits across checkpoints. This avoids duplicating identical comparator fits and matches each hidden model's full width. Exact source execution remains a 100% ceiling; this learned comparator is limited.

## Numeric heads and reconstruction

One multi-output ridge factorization has independent heads: scalar; 193-class integer identity over [-96,96]; three-way sign; absolute magnitude bins {0,1–9,10–96}; ten absolute units digits; ten absolute tens digits; parity; signed residues mod5 and mod10. Parity is the mod2 head, not a duplicated task. Signed residues use Python modulo on the signed integer; decimal components use absolute magnitude.

A separately scored joint reconstruction multiplies the predicted sign by ten times the tens digit plus the units digit. Zero sign with nonzero magnitude, nonzero sign with zero magnitude, and magnitude >96 are invalid and count as incorrect exact reconstruction. Report invalid frequency and ordinary numeric MAE as well. Component success alone is not full-value recovery. Class support and macro recall over supported evaluation classes remain explicit.

Every bank includes an intercept and the same 12 position/depth coordinates. Report feature width, shared-bank parameter count and the parameter count for each head/joint decoder. More features increase capacity; controls and TRAIN selection are essential to interpreting a width effect.

## TRAIN selection, controls and records

Use three grouped structural TRAIN folds, seeds 11/29/47 and alphas 1/100/10000. Draw family weights once per seed on all TRAIN examples of that role, then subset and normalize to mean1 within each fitting fold. Fit normalization only on fitting rows. Seeds index fitting/weighting sensitivity, not independent datasets. The random feature map is fixed without target labels.

Select alpha independently per encoding and width, averaging all nine TRAIN validation scores. Minimize scalar family-macro MAE; maximize categorical/joint-digit family-macro exact accuracy; maximize component macro recall on supported classes. Ties choose larger alpha. Lock all selections before accessing DEV predictions for that width. There is no DEV-selected winner across encodings or widths.

Each CV factorization fits all real-label heads jointly but independently. Post-selection, fit only unique selected alphas, jointly including the real-label heads and coherent-family-shuffled-label heads. Shuffling deranges whole structural families within split/depth/operator strata and preserves numeric/lexical relative coordinates. The shuffled task is evaluated against its own shuffled truth. All outputs share the same factorization but no target coupling. Preserve weighted TRAIN-only constant priors for every head.

There are 16 hidden role/width cells and ten shared-source cells: 702 CV factorizations and at most234 selected factorizations, rather than duplicating fits per encoding. Save every factorization's parameters, normalization, training identity hashes and metadata. Require exact score replay after reload. Save selected scores, point IDs, real/control truth and split tags. Record all TRAIN/DEV/calibration panels, per-seed results, component support and invalid rates. DEV strata include depth2/4/6, values matching/absent from initial literals, and values absent from TRAIN targets of that role. Empty strata remain explicit.

## Execution and interpretation

Archive tests/source/configuration and freeze the plan. Full frozen binding regression precedes every cache/readout. Three cache workers feed six CPU readout workers (two hidden checkpoints × two roles plus two shared-source roles). A final report follows all readouts. Requests use eligible CPU queues, 16 CPUs/64GiB and the scheduler's finite walltime; there is no cumulative project allowance or artificial concurrency limit. Preserve existing jobs and editor allocation. The durable controller checks about every ten minutes and retries only eligible scheduler interruptions. Scientific failures require review; completed fits are preserved. Job lifecycle events and results enter the existing automatic experiment logger.

Interpret width and encoding effects alongside source, shuffled-task and prior performance. Failure is specific to these measurements. Success may recover source-accessible information or let a decoder learn arithmetic; it does not establish native execution or natural causal use. E3/E4 will test later sites and matched arithmetic/binding/retention tasks after these diagnostics. Confirmation will use new structural families after a primary measurement is frozen.
