#!/usr/bin/env python
"""Render the completed semantic-control findings from hash-pinned fit banks."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from codecue.binding import arithmetic_semantic_controls as study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, default=3)
    revision = parser.parse_args().revision
    if not 3 <= revision <= 99: raise ValueError('a fresh explicit figure revision is required')
    stem = Path(f'reports/binding/figures/arithmetic_semantic_controls_v{revision}')
    review_path = Path(f'artifacts/binding/arithmetic_global_state/20261031_v1/semantic_figure_review_v{revision}.json')
    if review_path.exists() or any(stem.with_suffix(s).exists() for s in ('.png', '.svg', '.pdf')):
        raise ValueError('preserve existing figure revisions and their provenance')
    config_path = Path('configs/binding/arithmetic_semantic_controls_20261031_v2/report.json')
    config = study.base._json(config_path); study.common.completed(config)
    report_path = Path(config['run_dir']) / 'results.json'; data = study.base._json(report_path)
    inputs, mae = dict(config=study.storage._pin(config_path), report=study.storage._pin(report_path)), []
    for item in config['comparisons']:
        values = []
        for key in ('ordinary', 'alternate'):
            cfg = study.base._json(item[key]['path'], item[key]['sha256']); study.common.completed(cfg)
            path = Path(cfg['run_dir']) / 'results.json'; bank = study.base._json(path)
            inputs[f"{item['name']}_{key}"] = study.storage._pin(path)
            selected = [b for b in bank['fits'] if b['width'] == item['width'] and 'scalar' in b['selected_formats']]
            if sorted(b['seed'] for b in selected) != [11, 29, 47]: raise ValueError('complete scalar seed panels required')
            values.append(float(np.mean([b['development']['real']['scalar']['mae'] for b in selected])))
        mae.append(values)
    contrasts = [c for c in data['paired_family_contrasts'] if c['comparison'] == 'alternate minus ordinary normalized MAE']
    if [c['name'] for c in contrasts] != [i['name'] for i in config['comparisons']]: raise ValueError('contrast order differs')
    labels = ['Llama 8B\nhidden, 4096', 'CodeLlama 34B\nhidden, 8192', 'Source\nhash, 4096', 'Source\nhash, 8192']
    colors = ['#3366a3', '#cb8d37']; y = np.arange(4)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    figure, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.9), gridspec_kw={'width_ratios': [1.1, 1]})
    for j, label in enumerate(('Ordinary targets', 'Swapped +/− targets')):
        left.barh(y + (j - .5) * .31, np.asarray(mae)[:, j], height=.29, color=colors[j], label=label)
    left.set(yticks=y, yticklabels=labels, xlabel='Raw scalar MAE on development families (lower is better)',
        title='Both hidden readouts also recover alternate values')
    left.invert_yaxis(); left.legend(frameon=False, fontsize=9, loc='upper right'); left.set_xlim(0, 6.7)
    for i, c in enumerate(contrasts):
        right.plot([c['lower'], c['upper']], [i, i], color='#566579', linewidth=2)
        right.scatter(c['delta'], i, color='#3366a3' if i < 2 else '#7f8790', s=35, zorder=3)
    right.axvline(0, color='#b04c49', linewidth=1, linestyle='--')
    right.set(yticks=y, yticklabels=[], xlabel='Alternate − ordinary normalized MAE',
        title='Source features find alternate targets easier too', ylim=(3.6, -.6))
    right.text(.02, .02, '← alternate targets easier        ordinary targets easier →',
        transform=right.transAxes, fontsize=8)
    figure.suptitle('Recoverability alone does not identify native program semantics', fontsize=15, fontweight='bold')
    figure.text(.02, .065, 'Same archived inputs and states; three TRAIN-selected fitting seeds. Right: 95% paired structural-family bootstrap intervals.', fontsize=9)
    figure.text(.02, .025, 'Adaptive DEV; non-simultaneous intervals. Target distributions/scales differ. Parity is invariant under swapping + and −.', fontsize=9)
    figure.tight_layout(rect=(0, .11, 1, .93))
    artifacts = {}
    stem.parent.mkdir(exist_ok=True)
    for suffix in ('.png', '.svg', '.pdf'):
        path = stem.with_suffix(suffix)
        figure.savefig(path, dpi=180, metadata={'Creator': 'CodeCue hash-pinned semantic-control figure'})
        artifacts[suffix[1:]] = study.storage._pin(path)
    plt.close(figure)
    review = dict(status='rendered_existing_results', script=study.storage._pin(__file__), inputs=inputs,
        artifacts=artifacts, scalar_mae=mae, contrasts=contrasts, new_fits=0, new_model_queries=0,
        limitation='Existing adaptive DEV; no native-semantic preference or causal-use conclusion')
    study.base._put(review_path, review)
    print(json.dumps(dict(status=review['status'], artifacts=artifacts)))


if __name__ == '__main__': main()
