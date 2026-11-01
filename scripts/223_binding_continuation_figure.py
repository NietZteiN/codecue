#!/usr/bin/env python
"""Plot the completed, token-audited calibration continuation contrasts."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--edition', type=int, required=True)
    args = parser.parse_args()
    from codecue.binding import relationship_capture as base, arithmetic_graph_readouts as storage
    root = Path('artifacts/binding/arithmetic_paired_exploration/20261101_v2')
    original_path = root / 'error_audit/results.json'; original = base._json(original_path)
    inputs = dict(original=storage._pin(original_path)); models = {}
    for alias in ('llama8b', 'codellama34b'):
        folder = root / (alias + '_postrun'); proof = base._json(folder / 'completion_manifest_v1.json')
        if proof['status'] != 'complete_audited_exploratory': raise ValueError('completed token audit required')
        for pin in proof['artifacts'].values():
            if base._sha(pin['path']) != pin['sha256']: raise ValueError('audit artifact changed')
        models[alias] = base._json(folder / 'results.json'); inputs[alias] = storage._pin(folder / 'results.json')
    own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    target = Path('reports/binding/figures') / f'arithmetic_calibration_continuation_v{args.edition}'
    outputs = [target.with_suffix('.' + suffix) for suffix in ('png', 'svg', 'pdf')]
    proof_path = root / f'continuation_figure_review_v{args.edition}.json'
    if args.edition < 1 or proof_path.exists() or any(p.exists() for p in outputs): raise ValueError('fresh figure edition required')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import numpy as np
    keys = [p + '/' + s for p in ('output_only', 'intermediate_query', 'stepwise') for s in ('single', 'all')]
    labels = ['Output only · one value', 'Output only · all four', 'Intermediate · one value',
        'Intermediate · all four', 'Stepwise · one value', 'Stepwise · all four']
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6), sharey=True); plotted = {}
    for axis, alias in zip(axes, ('llama8b', 'codellama34b')):
        plotted[alias] = {}
        for i, key in enumerate(keys):
            before = original['models'][alias]['cells'][key]; after = models[alias]['cells'][key]; n = before['rows']
            if n != after['rows'] or n != 216 or after['truncated'] != 0: raise ValueError('matched completed rows required')
            b, a, d = [100 * c / n for c in (before['strict_correct'], after['strict_correct'], after['diagnostic_complete_correct'])]
            if a < b: raise ValueError('reused completed responses cannot lose original strict successes')
            axis.plot([b, a], [i - .1, i - .1], color='#94a3b8', lw=3, zorder=1)
            axis.plot([a, d], [i + .1, i + .1], color='#57a893', lw=2, zorder=1)
            axis.scatter(b, i - .1, color='#94a3b8', s=40, zorder=3)
            axis.scatter(a, i - .1, color='#3477bb', s=55, zorder=4)
            axis.scatter(d, i + .1, marker='D', color='#397c68', s=40, zorder=4)
            axis.text(103, i, f'{a:.1f} / {d:.1f}', va='center', fontsize=9, color='#263345')
            plotted[alias][key] = dict(rows=n, original_strict=before['strict_correct'],
                continued_strict=after['strict_correct'], continued_heading=after['diagnostic_complete_correct'])
        axis.set_xlim(-2, 126); axis.set_xticks([0, 25, 50, 75, 100]); axis.set_xlabel('Complete-response accuracy (%)')
        axis.set_yticks(np.arange(6), labels); axis.tick_params(axis='y', length=0)
        axis.spines[['top', 'right', 'left']].set_visible(False)
        axis.set_title('Llama 3.1 8B' if alias == 'llama8b' else 'CodeLlama 34B', loc='left', fontsize=14, weight='bold', pad=22)
        axis.text(103, -.75, 'Continued\nstrict / heading', fontsize=9, color='#526174', va='bottom')
        axis.grid(axis='x', alpha=.14); axis.set_axisbelow(True)
    axes[0].invert_yaxis()
    fig.suptitle('Longer continuations resolve truncation; answer format still changes scores', x=.02, ha='left', fontsize=16, weight='bold')
    handles = [Line2D([], [], marker='o', ls='', color=c, label=l) for c, l in
        [('#94a3b8', 'Original strict'), ('#3477bb', 'Continued strict')]]
    handles.append(Line2D([], [], marker='D', ls='', color='#397c68', label='Continued heading diagnostic'))
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .08), ncol=3, frameon=False, fontsize=10)
    fig.text(.02, .025, '216 correlated calibration cases per row. All-four rows require all four values correct. Original scores remain unchanged.\n'
        'Pilot ceilings: 64 / 128 / 512 tokens; continuation ceiling: 1,024 total. Completed outputs reused. This does not isolate an effect of reasoning.',
        fontsize=9, color='#526174')
    fig.subplots_adjust(left=.19, right=.98, top=.79, bottom=.25, wspace=.18)
    for output in outputs: fig.savefig(output, dpi=180, facecolor='white')
    plt.close(fig)
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('figure utility changed')
    base._put(proof_path, dict(status='audited_figure', inputs=inputs, plotted_values=plotted,
        utility=dict(path=str(own), sha256=own_sha), artifacts={p.suffix[1:]: storage._pin(p) for p in outputs},
        new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status='audited_figure', figure=str(target))))


if __name__ == '__main__': main()
