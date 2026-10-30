#!/usr/bin/env python
"""Correct plot spacing using immutable comparison data; no score replay/refits."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from codecue.binding import relationship_capture as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/binding/arithmetic_probe_selection/20261030_v2'
SOURCE = OUT / 'findings_review_v1.json'
FIGURE = ROOT / 'reports/binding/figures/arithmetic_probe_selection_v2'
REPORT = ROOT / 'reports/binding/arithmetic_probe_selection_findings_v2.md'


def pin(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    if (OUT / 'figure_layout_review_v2.json').exists():
        raise ValueError('completed figure correction must be preserved')
    data = base._json(SOURCE)
    comparisons = data['comparisons']
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.6))
    for ax, metric, title in zip(axes, ('parent_accuracy', 'relation_balanced_accuracy', 'value_mae'),
                                ('Dependency parents', 'Algebraic relations', 'Current numeric values')):
        scale = 1 if metric == 'value_mae' else 100
        top = max(comparisons[name]['hidden'][metric]['before_interval'][1] for name in comparisons)
        top = max(top, max(comparisons[name]['hidden'][metric]['after_interval'][1] for name in comparisons))
        ceiling = top * 1.35 if metric == 'value_mae' else 100
        for index, name in enumerate(('llama8b', 'codellama34b')):
            cell = comparisons[name]['hidden'][metric]
            for delta, key, color in [(-.18, 'before', '#cbd5e1'), (.18, 'after', '#307aab')]:
                value = cell[key] * scale
                lo, hi = np.asarray(cell[key + '_interval']) * scale
                ax.bar(index + delta, value, .31, color=color, label=key.capitalize() if index == 0 else None)
                ax.errorbar(index + delta, value, yerr=[[max(0, value - lo)], [max(0, hi - value)]], color='#334155', capsize=3, lw=1)
                ax.text(index + delta, hi + ceiling * .025, f'{value:.2f}', ha='center', fontsize=9)
        ax.set_title(title, pad=14)
        ax.set_xticks([0, 1], ['Llama 8B', 'CodeLlama 34B'])
        ax.set_ylim(0, ceiling)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_ylabel('Mean absolute error; lower is better' if metric == 'value_mae'
            else 'Parent accuracy (%)' if metric == 'parent_accuracy' else 'Relation balanced accuracy (%)')
        if metric == 'relation_balanced_accuracy':
            ax.axhline(50, color='#64748b', ls=':', lw=1)
    fig.suptitle('Probe revision on the previously examined structural DEV cohort', fontsize=15, y=.985)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .93), ncol=2, frameon=False)
    fig.text(.02, .025, 'Family-macro metrics; settings selected inside TRAIN for each objective. Fixed-fit 95% family-bootstrap intervals.\nNumeric decoding changes from categorical prediction to regression. Adaptive discovery; no causal or confirmatory claim.', fontsize=9)
    fig.tight_layout(rect=[0, .11, 1, .84])
    for extension in ('.png', '.svg'):
        fig.savefig(str(FIGURE) + extension, dpi=170, metadata={'Date': None} if extension == '.svg' else None)
    plt.close(fig)
    old = ROOT / data['artifacts']['report']['path']
    if pin(old)['sha256'] != data['artifacts']['report']['sha256']:
        raise ValueError('original comparison report changed')
    content = old.read_text().replace('figures/arithmetic_probe_selection_v1.png', 'figures/arithmetic_probe_selection_v2.png')
    base._publish(REPORT, content.encode())
    base._put(OUT / 'figure_layout_review_v2.json', dict(status='complete_exploratory',
        input_review=pin(SOURCE), renderer=pin(Path(__file__)), scientific_metrics_unchanged=True,
        correction='Separate shared legend and numeric labels from titles; increase numeric-axis headroom.',
        artifacts={name: pin(path) for name, path in [('report', REPORT), ('png', Path(str(FIGURE) + '.png')), ('svg', Path(str(FIGURE) + '.svg'))]},
        new_fits=0, new_model_queries=0, score_reapplications=0))


if __name__ == '__main__':
    main()
