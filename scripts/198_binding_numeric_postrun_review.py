#!/usr/bin/env python
"""Render a compact numeric-study review only after independent audit passes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean

ROOT = Path('artifacts/binding/arithmetic_numeric_exploration/20261031_v1')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def read(entry):
    if pin(entry['path'])['sha256'] != entry['sha256']: raise ValueError('review input changed')
    return json.loads(Path(entry['path']).read_text())


def panel(data, width, encoding):
    banks = [b for b in data['fits'] if b['width'] == width and encoding in b['selected_formats']]
    if sorted(b['seed'] for b in banks) != [11, 29, 47]: raise ValueError('complete selected seeds required')
    return {key: mean(b['development'][key][encoding]['exact'] for b in banks) for key in ['real', 'control', 'prior']} | dict(
        mae=mean(b['development']['real'][encoding]['mae'] for b in banks),
        seed_exact=[b['development']['real'][encoding]['exact'] for b in banks],
        seed_mae=[b['development']['real'][encoding]['mae'] for b in banks])


def main():
    proof_path = ROOT / 'postrun_audit/completion_review_v1.json'
    proof = json.loads(proof_path.read_text())
    if proof['status'] != 'passed': raise ValueError('independent postrun audit must pass')
    target = Path('reports/binding/arithmetic_numeric_postrun_review_v1.md')
    receipt = ROOT / 'postrun_review_v1.json'
    if target.exists() or receipt.exists(): raise ValueError('preserve existing review edition')
    data, inputs, rows = {}, {}, []
    for worker in proof['workers']:
        config = read(worker['config']); result = read(worker['results'])
        key = Path(worker['config']['path']).stem
        data[key] = result; inputs[key] = worker['results']
        widths = [64, result['widths'][-1]] if result['backend'] == 'hidden' else [64, 4096, 8192]
        for width in widths:
            for encoding in ['scalar', 'categorical', 'digits_joint']:
                p = panel(result, width, encoding)
                rows.append(f"| {key} | {width} | {encoding} | {100*p['real']:.2f}% | {p['mae']:.3f} | {100*p['control']:.2f}% | {100*p['prior']:.2f}% |")
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for key, label, color in [('llama8b_computed_definition', 'Llama 8B', '#2e78a6'),
            ('codellama34b_computed_definition', 'CodeLlama 34B', '#d67e38'),
            ('source_computed_definition', 'Source character probe', '#4d9a86')]:
        result = data[key]; widths = result['widths']
        for ax, encoding, metric, scale in [(axes[0], 'scalar', 'mae', 1), (axes[1], 'categorical', 'real', 100)]:
            panels = [panel(result, width, encoding) for width in widths]
            values = [p[metric] * scale for p in panels]
            samples = [p['seed_mae' if metric == 'mae' else 'seed_exact'] for p in panels]
            error = [[v - min(s)*scale for v, s in zip(values, samples)], [max(s)*scale - v for v, s in zip(values, samples)]]
            ax.errorbar(widths, values, yerr=error, color=color, label=label, marker='o', capsize=3, linewidth=1.8)
    prior = panel(data['llama8b_computed_definition'], 64, 'categorical')['prior']
    axes[1].axhline(100*prior, color='#666666', linestyle=':', label='TRAIN-only constant prior')
    for ax in axes:
        ax.set_xscale('log', base=2); ax.set_xticks([64, 256, 1024, 4096, 8192], ['64', '256', '1024', '4096', '8192'])
        ax.set_xlabel('Representation width'); ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.18)
    axes[0].set_title('Computed values: scalar error'); axes[0].set_ylabel('Mean absolute error'); axes[0].set_ylim(0, 6)
    axes[1].set_title('Computed values: categorical accuracy'); axes[1].set_ylabel('Exact accuracy (%)'); axes[1].set_ylim(0, 20)
    axes[1].legend(frameon=False, fontsize=9)
    fig.suptitle('Compression limits numeric readouts; computed values remain difficult', y=.99, fontsize=14)
    fig.text(.02, .025, 'Discovery DEV: 72 structural families; fixed layers; role-specific decoders; TRAIN-only alpha selection.\nPoints: mean of three weighting seeds. Whiskers: seed min/max, not confidence intervals. No causal-use claim.', fontsize=9)
    fig.tight_layout(rect=[0, .13, 1, .94])
    stem = Path('reports/binding/figures/arithmetic_numeric_compression_v1')
    artifacts = {}
    for suffix in ['.png', '.svg']:
        path = stem.with_suffix(suffix)
        if path.exists(): raise ValueError('preserve existing figure')
        fig.savefig(path, dpi=170, metadata={'Date': None} if suffix == '.svg' else None)
        artifacts[suffix[1:]] = pin(path)
    plt.close(fig)
    text = ['# Numeric exploration: audited completion review', '',
        f"All six workers and the report completed. The no-fit postrun audit verified **{proof['verified_banks']} unique fit banks**, recomputed TRAIN selections and replayed **{proof['replayed_selected_banks']} selected scorers** over **{proof['replayed_scores']:,} score values**. Maximum replay difference: **{proof['max_abs_replay_difference']:.3g}**. Independent metric checks covered real, coherent-family-control and TRAIN-prior panels. CV payloads/metadata were verified; CV scores were not reapplied. The source regression passed 2,467 tests.", '',
        '![Numeric compression comparison](figures/arithmetic_numeric_compression_v1.png)', '',
        'Within the fixed-layer role-specific assay, wider hidden features reduce computed-value error and improve categorical exact accuracy. Literal copying controls reach very high accuracy. Computed results remain difficult; component/digit decoding does not establish complete execution-state recovery. The limited source-character comparator, supplied site/statement scaffold and increased decoder capacity remain explicit. This is adaptive discovery on already-inspected DEV, not new-family confirmation or causal-use evidence.', '',
        '| Worker / role | Width | Encoding | DEV exact | DEV MAE | Shuffled exact | TRAIN prior exact |',
        '|---|---:|---|---:|---:|---:|---:|', *rows, '',
        'All declared widths, ten encodings, individual seeds, alpha choices, class support, invalid digit configurations, strata and parameter counts remain in the [full findings](arithmetic_numeric_exploration_findings_v1.md) and machine-readable results. Large artifacts use verified scratch storage after the [quota recovery](arithmetic_numeric_storage_recovery_20261031_v1.md). No postrun fits, model calls or sealed-final access occurred.', '',
        'Next: prepare separately declared later-token captures and matched arithmetic/binding/retention datasets. Freeze a primary measurement before independent-family confirmation. Existing final outcomes stay sealed.', '']
    target.write_text('\n'.join(text))
    artifacts['report'] = pin(target)
    receipt.write_text(json.dumps(dict(status='complete_exploratory', recorded_utc=datetime.now(timezone.utc).isoformat(),
        audit=pin(proof_path), inputs=inputs, renderer=pin(__file__), artifacts=artifacts, new_fits=0, new_model_queries=0), sort_keys=True, indent=2)+'\n')
    print('Audited review and figure generated.')


if __name__ == '__main__': main()
