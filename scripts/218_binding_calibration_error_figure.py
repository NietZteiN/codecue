#!/usr/bin/env python
"""Plot audited calibration failure categories without rescoring responses."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-config', required=True)
    parser.add_argument('--edition', type=int, required=True)
    args = parser.parse_args()
    from codecue.binding import relationship_capture as base, arithmetic_state_common as common
    from codecue.binding import arithmetic_graph_readouts as storage
    config = base._json(args.audit_config); common.completed(config)
    path = Path(config['run_dir']) / 'results.json'; data = base._json(path)
    own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    if args.edition < 1: raise ValueError('positive figure edition required')
    target = Path('reports/binding/figures') / f'arithmetic_calibration_error_audit_v{args.edition}'
    proof = Path('artifacts/binding/arithmetic_paired_exploration/20261101_v2') / f'figure_review_v{args.edition}.json'
    outputs = [target.with_suffix('.' + suffix) for suffix in ('png', 'svg', 'pdf')]
    if proof.exists() or any(p.exists() for p in outputs): raise ValueError('preserve existing figure editions')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import numpy as np
    labels = ['Output only · one value', 'Output only · four values',
        'Intermediate · one value', 'Intermediate · four values',
        'Stepwise · one value', 'Stepwise · four values']
    keys = [p + '/' + s for p in ('output_only', 'intermediate_query', 'stepwise') for s in ('single', 'all')]
    colors = ['#397c68', '#bd6364', '#b6becb', '#e5b15e']
    categories = ['Strict correct', 'Accepted, wrong', 'Completed, invalid format', 'Truncated']
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 5.8), sharey=True)
    values = {}
    for axis, alias in zip(axes, ('llama8b', 'codellama34b')):
        cells = data['models'][alias]['cells']; values[alias] = {}
        bars, diag = [], []
        for key in keys:
            c = cells[key]; n = c['rows']
            counts = [c['strict_correct'], c['strict_accepted'] - c['strict_correct'],
                n - c['strict_accepted'] - c['truncated'], c['truncated']]
            if any(v < 0 for v in counts) or sum(counts) != n: raise ValueError('failure partition differs')
            bars.append([100 * v / n for v in counts]); diag.append(100 * c['diagnostic_complete_correct'] / n)
            values[alias][key] = dict(rows=n, counts=dict(zip(categories, counts)),
                diagnostic_complete_correct=c['diagnostic_complete_correct'])
        bars = np.asarray(bars); left = np.zeros(len(keys)); y = np.arange(len(keys))
        for i, color in enumerate(colors):
            axis.barh(y, bars[:, i], left=left, color=color, height=.64)
            left += bars[:, i]
        for i, (row, diagnostic) in enumerate(zip(bars, diag)):
            if row[0] >= 7: axis.text(row[0] / 2, i, f'{row[0]:.1f}%', color='white', va='center', ha='center', fontsize=10)
            axis.text(103, i, f'{diagnostic:.1f}%', va='center', fontsize=10, color='#263345')
        axis.set_title('Llama 3.1 8B' if alias == 'llama8b' else 'CodeLlama 34B', loc='left', fontsize=14, weight='bold', pad=23)
        axis.text(103, -.75, 'Heading\ngrammar', fontsize=9, color='#526174', va='bottom')
        axis.set_xlim(0, 116); axis.set_xticks([0, 25, 50, 75, 100]); axis.set_xlabel('Responses (%)')
        axis.set_yticks(y, labels); axis.tick_params(axis='y', length=0)
        axis.spines[['top', 'right', 'left']].set_visible(False)
    axes[0].invert_yaxis()
    fig.suptitle('Calibration failures mix numerical errors, formatting and truncation', x=.02, ha='left', fontsize=17, weight='bold')
    fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(colors, categories)],
        loc='lower center', ncol=4, bbox_to_anchor=(.5, .075), frameon=False, fontsize=10)
    fig.text(.02, .025, '216 cases per row; calibration templates are correlated. Original strict scores are unchanged.\n'
        'Heading grammar is a separate complete-response diagnostic; truncated responses remain failures. Generation ceilings: 64 / 128 / 512.',
        fontsize=9, color='#526174')
    fig.subplots_adjust(left=.19, right=.98, top=.79, bottom=.25, wspace=.15)
    target.parent.mkdir(parents=True, exist_ok=True)
    for output in outputs: fig.savefig(output, dpi=180, facecolor='white')
    plt.close(fig)
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('figure utility changed')
    base._put(proof, dict(status='audited_figure', input=storage._pin(path), config=storage._pin(args.audit_config),
        utility=dict(path=str(own), sha256=own_sha), plotted_values=values,
        artifacts={p.suffix[1:]: storage._pin(p) for p in outputs}, new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status='audited_figure', figure=str(target), input_sha256=base._sha(path))))


if __name__ == '__main__': main()
