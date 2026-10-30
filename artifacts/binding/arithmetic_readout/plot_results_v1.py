#!/usr/bin/env python
"""Plot only the completed, audited arithmetic/readout comparison metadata.

This standalone artifact does not inspect response rows or run models. Existing
figures and their provenance must match byte for byte; otherwise use a new
version rather than replacing the original result figure.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys


MODEL_TITLES = {
    'llama31_8b': 'Llama 3.1 8B Instruct',
    'codellama34b': 'CodeLlama 34B Instruct',
}
PROTOCOLS = ('print_direct_v3', 'print_trace_long_v1')
FORMS = (
    ('literal_output', 'Literal output (0 operations)\N{DAGGER}', 0),
    ('stored_output', 'Stored output (0 operations)\N{DAGGER}', 0),
    ('literal_one', 'Literal subtraction (1 operation)', 1),
    ('bound_one', 'Bound operands (1 operation)', 1),
    ('stored_result_one', 'Stored result (1 operation)', 1),
    ('literal_three', 'Literal expression (3 operations)', 3),
    ('bound_three', 'Bound operands (3 operations)', 3),
    ('stored_intermediates_three', 'Stored intermediates (3 operations)', 3),
)


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _count(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return value


def validate_comparison(data):
    """Distinguish passed artifact audits from potentially failed science gates."""
    if data.get('status') != 'passed' or data.get('complete') is not True:
        raise ValueError('a completed comparison with passed artifact audits is required')
    if data.get('generated_holdouts_opened') is not False:
        raise ValueError('comparison must explicitly preserve sealed generated outcomes')
    models = data.get('models') or {}
    if set(models) != set(MODEL_TITLES):
        raise ValueError('both registered checkpoint reviews are required')
    checksums = data.get('review_checksums') or {}
    if len(checksums) != 2 or any(not isinstance(value, str) or len(value) != 64
                                  or any(c not in '0123456789abcdef' for c in value)
                                  for value in checksums.values()):
        raise ValueError('the comparison must retain both review SHA256 checksums')
    expected = {(protocol, form, split) for protocol in PROTOCOLS
                for form, _, _ in FORMS for split in ('train', 'development', 'all')}
    selected = {}
    total = 0
    dataset_hashes = set()
    for name in MODEL_TITLES:
        review = models[name]
        if review.get('status') != 'complete_audited' or review.get('complete') is not True:
            raise ValueError(f'{name}: completed audited embedded review required')
        if review.get('generated_holdouts_opened') is not False:
            raise ValueError(f'{name}: generated holdout outcomes must remain sealed')
        dataset_hash = review.get('dataset_sha256')
        if not isinstance(dataset_hash, str) or len(dataset_hash) != 64:
            raise ValueError(f'{name}: missing dataset SHA256')
        dataset_hashes.add(dataset_hash)
        cells = {}
        for cell in review.get('form_cells', []):
            key = (cell.get('variant'), cell.get('form'), cell.get('split'))
            if key not in expected or key in cells:
                raise ValueError(f'{name}: unexpected or duplicate aggregate form cell')
            n = _count(cell.get('n'), 'n')
            correct = _count(cell.get('correct'), 'correct')
            invalid = _count(cell.get('invalid'), 'invalid')
            unique = _count(cell.get('unique_prompt_n'), 'unique_prompt_n')
            if not n or correct + invalid > n or unique > n:
                raise ValueError(f'{name}: inconsistent aggregate counts')
            accuracy = cell.get('accuracy')
            if (isinstance(accuracy, bool) or not isinstance(accuracy, (int, float))
                    or abs(accuracy - correct / n) > 1e-12):
                raise ValueError(f'{name}: saved accuracy differs from correct/n')
            operations = dict((form, count) for form, _, count in FORMS)[key[1]]
            if cell.get('operation_count') != operations:
                raise ValueError(f'{name}: operation-count label differs')
            if operations and unique != n:
                raise ValueError(f'{name}: nonzero-operation prompts must be unique')
            cells[key] = cell
        if set(cells) != expected:
            raise ValueError(f'{name}: all forms, protocols and split aggregates are required')
        for protocol in PROTOCOLS:
            for form, _, _ in FORMS:
                train = cells[protocol, form, 'train']
                development = cells[protocol, form, 'development']
                combined = cells[protocol, form, 'all']
                for key in ('n', 'correct', 'invalid'):
                    if train[key] + development[key] != combined[key]:
                        raise ValueError(f'{name}: aggregate {key} does not match splits')
        n = _count(review.get('n'), 'review n')
        if n != sum(cell['n'] for key, cell in cells.items() if key[2] == 'all'):
            raise ValueError(f'{name}: review total differs from complete form matrix')
        total += n
        gates = (review.get('reliability_gate') or {}).get('protocols') or {}
        if set(gates) != set(PROTOCOLS) or any(gates[p].get('status') not in ('passed', 'failed')
                                            for p in PROTOCOLS):
            raise ValueError(f'{name}: both fixed scientific gate outcomes are required')
        threshold = ((review.get('reliability_gate') or {}).get('thresholds') or {}).get('minimum_accuracy')
        if threshold != .9:
            raise ValueError(f'{name}: this version requires the registered 90% reference')
        selected[name] = {(protocol, form): cells[protocol, form, 'development']
                          for protocol in PROTOCOLS for form, _, _ in FORMS}
    if len(dataset_hashes) != 1 or data.get('total_predictions') != total:
        raise ValueError('checkpoint cohorts or comparison response totals differ')
    return selected


def render(data, selected, comparison_hash, source_hash):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'arithmetic-readout-v1'})
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.6), sharey=True)
    colors = ('#2878A5', '#D17825')
    labels = ('Direct answer', 'Reasoning trace')
    for axis, name in zip(axes, MODEL_TITLES):
        for protocol, color, label, offset in zip(PROTOCOLS, colors, labels, (-.18, .18)):
            values = [selected[name][protocol, form] for form, _, _ in FORMS]
            ys = [index + offset for index in range(len(FORMS))]
            axis.barh(ys, [cell['correct'] / cell['n'] for cell in values], height=.31,
                      color=color, label=label, zorder=3)
            for y, cell in zip(ys, values):
                axis.text(cell['correct'] / cell['n'] + .012, y,
                          f"{cell['correct']}/{cell['n']}", ha='left', va='center', fontsize=9)
        axis.axvline(.9, linestyle=(0, (4, 3)), color='#666666', linewidth=1, zorder=2)
        axis.set_xlim(0, 1.24)
        axis.set_xticks([0, .25, .5, .75, 1])
        axis.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        axis.set_yticks(range(len(FORMS)), [label for _, label, _ in FORMS])
        axis.set_xlabel('Correct answers / numeric development responses')
        axis.grid(axis='x', alpha=.18, zorder=0)
        axis.set_title(MODEL_TITLES[name], fontweight='bold', pad=20)
        gates = data['models'][name]['reliability_gate']['protocols']
        axis.text(0, 1.015,
                  'Fixed gates: direct ' + gates[PROTOCOLS[0]]['status']
                  + '; trace ' + gates[PROTOCOLS[1]]['status'],
                  transform=axis.transAxes, fontsize=9, color='#444444')
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.64, .935),
               ncol=2, frameon=False)
    fig.suptitle('Arithmetic and readout feasibility: numeric development',
                 x=.62, y=.985, fontsize=15, fontweight='bold')
    fig.subplots_adjust(left=.255, right=.985, top=.85, bottom=.18, wspace=.15)
    fig.text(.255, .105,
             'Bars show correct/n. Dashed line: 90% reference; qualification also requires every sign cell and low invalid rates.',
             fontsize=9, color='#444444')
    fig.text(.255, .074,
             '\N{DAGGER} Zero-operation controls repeat exact prompts and are descriptive. Traces change computation; structures are shared with training.',
             fontsize=9, color='#444444')
    fig.text(.255, .039,
             f'Comparison SHA256 {comparison_hash[:16]}  |  Plot source SHA256 {source_hash[:16]}',
             fontsize=8, color='#666666')
    svg, png = io.BytesIO(), io.BytesIO()
    description = 'Complete audited arithmetic/readout comparison SHA256 ' + comparison_hash
    fig.savefig(svg, format='svg', metadata={'Date': None, 'Creator': 'CodeCue arithmetic/readout plot v1',
                                            'Description': description})
    fig.savefig(png, format='png', dpi=180,
                metadata={'Software': 'Matplotlib ' + matplotlib.__version__, 'Description': description})
    plt.close(fig)
    return svg.getvalue(), png.getvalue(), matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.root.resolve()
    comparison = root / 'artifacts/binding/arithmetic_readout/comparison_v1.json'
    if not comparison.is_file():
        raise ValueError('completed comparison_v1.json is required; no figure was produced')
    content = comparison.read_bytes()
    data = json.loads(content)
    selected = validate_comparison(data)
    comparison_hash = _sha(content)
    source_hash = _sha(Path(__file__).read_bytes())
    svg, png, version = render(data, selected, comparison_hash, source_hash)
    paths = {'svg': root / 'reports/binding/arithmetic_readout_results_v1.svg',
             'png': root / 'reports/binding/arithmetic_readout_results_v1.png'}
    review_path = root / 'artifacts/binding/arithmetic_readout/figure_review_v1.json'
    outputs = {'svg': svg, 'png': png}
    review = dict(status='passed', complete=True,
        analysis_role='descriptive_development_form_accuracy_figure',
        comparison=str(comparison), comparison_sha256=comparison_hash,
        plot_source=str(Path(__file__).resolve()), plot_source_sha256=source_hash,
        matplotlib_version=version, models=list(MODEL_TITLES), protocols=list(PROTOCOLS),
        split='development', uncertainty_whiskers=False, reference_accuracy=.9,
        zero_operation_controls='Repeated exact prompts; descriptive only; excluded from qualification gates',
        scientific_status={name: {protocol: data['models'][name]['reliability_gate']['protocols'][protocol]['status']
                                  for protocol in PROTOCOLS} for name in MODEL_TITLES},
        outputs={kind: dict(path=str(paths[kind]), sha256=_sha(value), bytes=len(value))
                 for kind, value in outputs.items()},
        review_checksums=data['review_checksums'], generated_holdouts_opened=False,
        limitation='All eight forms and both fixed protocols shown on numeric development only. '
                   'Shared program forms do not establish structural generalization or a causal mechanism.')
    review_bytes = (json.dumps(review, sort_keys=True, indent=2) + '\n').encode()
    planned = [(paths[kind], value) for kind, value in outputs.items()] + [(review_path, review_bytes)]
    for path, value in planned:
        if path.exists() and path.read_bytes() != value:
            raise ValueError(f'original figure/provenance differs; preserve it and use a new version: {path}')
    sys.path.insert(0, str(root / 'src'))
    from codecue.binding.published_benchmarks import immutable
    for path, value in planned:
        immutable(path, value)
    print(json.dumps(dict(status='passed', review=str(review_path),
                          outputs={kind: str(path) for kind, path in paths.items()}), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Arithmetic/readout figure refused: {exc}', file=sys.stderr)
        raise SystemExit(1)
