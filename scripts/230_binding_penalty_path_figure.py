#!/usr/bin/env python
"""Plot audited TRAIN-only penalty curves and the constant comparator."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--edition', type=int, required=True)
    args = parser.parse_args()
    from codecue.binding import arithmetic_penalty_path as study
    cfg = study.base._json('configs/binding/arithmetic_penalty_path_20261101_v1/report.json'); study.common.completed(cfg)
    inputs, cells = {}, {}
    for request in cfg['workers']:
        worker = study.base._json(request['path'], request['sha256']); study.common.completed(worker)
        p = Path(worker['run_dir']) / 'results.json'; data = study.base._json(p)
        key = data['alias'] + '/' + data['condition']; cells[key] = data['selection']; inputs[key] = study.storage._pin(p)
    own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    target = Path('reports/binding/figures') / f'arithmetic_penalty_path_v{args.edition}'
    outputs = [target.with_suffix('.' + suffix) for suffix in ('png', 'svg', 'pdf')]
    proof = Path('artifacts/binding/arithmetic_penalty_path/20261101_v1') / f'figure_review_v{args.edition}.json'
    if args.edition < 1 or proof.exists() or any(p.exists() for p in outputs): raise ValueError('preserve existing figure editions')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6), sharey=True); plotted = {}
    styles = [('source/source1024', 'Source 1024', '#a5abb6', '--'),
        ('source/source2048', 'Source 2048', '#657083', ':'),
        ('hidden', 'Hidden 1024', '#3477bb', '-'), ('joint', 'Source + hidden', '#397c68', '-'),
        ('shuffled_joint', 'Source + shuffled hidden', '#bd6364', '-')]
    for axis, alias in zip(axes, ('llama8b', 'codellama34b')):
        plotted[alias] = {}
        for key, label, color, line in styles:
            key = key if key.startswith('source/') else alias + '/' + key
            selection = cells[key]; records = sorted([c for c in selection['candidates'] if c['kind'] == 'ridge'], key=lambda c: c['alpha'])
            if tuple(c['alpha'] for c in records) != study.ALPHAS: raise ValueError('complete six-penalty curve required')
            x = [c['alpha'] for c in records]; y = [c['cv_mae'] for c in records]
            axis.plot(x, y, marker='o', markersize=4, color=color, ls=line, label=label)
            chosen = next(c for c in records if c['alpha'] == selection['ridge_alpha'])
            axis.scatter(chosen['alpha'], chosen['cv_mae'], color=color, marker='*', s=100, zorder=5)
            plotted[alias][key] = dict(curve=records, ridge_alpha=selection['ridge_alpha'], overall=selection['overall'])
        constants = [c for c in cells[alias + '/joint']['candidates'] if c['kind'] == 'prior']
        best = min(constants, key=lambda c: (c['cv_mae'], study.PRIOR_NAMES.index(c['prior'])))
        axis.axhline(best['cv_mae'], color='#222b39', ls='-.', lw=1.4, label='Best TRAIN-CV constant')
        plotted[alias]['constant_line'] = best
        axis.set_xscale('log'); axis.set_xticks(study.ALPHAS, ['1', '100', '10k', '100k', '1m', '10m'])
        axis.set_xlim(.7, 1.5e7); axis.set_xlabel('Ridge penalty α (log scale)')
        axis.set_title('Llama 3.1 8B' if alias == 'llama8b' else 'CodeLlama 34B', loc='left', fontsize=14, weight='bold')
        axis.axvspan(3e4, 1.5e7, color='#e9f2fb', alpha=.6, zorder=0)
        axis.text(.98, .97, 'New penalties →', transform=axis.transAxes, ha='right', va='top', fontsize=9, color='#526174')
        axis.spines[['top', 'right']].set_visible(False); axis.grid(alpha=.15); axis.set_axisbelow(True)
    axes[0].set_ylabel('TRAIN-fold computed-value MAE')
    fig.suptitle('Checking the penalty boundary without repeating completed fits', x=.02, ha='left', fontsize=17, weight='bold')
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(Line2D([], [], marker='*', ls='', color='#222b39', markersize=10)); labels.append('Selected ridge penalty')
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .085), ncol=4, frameon=False, fontsize=9)
    fig.text(.02, .025, 'Each point averages three structural TRAIN folds × three fitting seeds. No DEV selection. Old CV banks are reused.\n'
        'Constant line is chosen among four TRAIN-fold priors; all priors remain in the report. These curves measure proximity, not exact state recovery.',
        fontsize=9, color='#526174')
    fig.subplots_adjust(left=.08, right=.98, top=.83, bottom=.28, wspace=.16)
    for output in outputs: fig.savefig(output, dpi=180, facecolor='white')
    plt.close(fig)
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('plotting utility changed during run')
    study.base._put(proof, dict(status='audited_figure', utility=dict(path=str(own), sha256=own_sha), inputs=inputs,
        plotted_values=plotted, artifacts={p.suffix[1:]: study.storage._pin(p) for p in outputs}, new_model_queries=0, new_readout_fits=0))
    print(json.dumps(dict(status='audited_figure', figure=str(target))))


if __name__ == '__main__': main()
