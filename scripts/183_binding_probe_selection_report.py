#!/usr/bin/env python
"""Render an aligned old/new probe comparison from saved predictions only."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from codecue.binding import arithmetic_probe_selection as revision
from codecue.binding import arithmetic_graph_readouts as original
from codecue.binding import relationship_capture as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/binding/arithmetic_probe_selection/20261030_v2'
REPORT = ROOT / 'reports/binding/arithmetic_probe_selection_findings_v1.md'
FIGURE = ROOT / 'reports/binding/figures/arithmetic_probe_selection_v1'
METRICS = ('parent_accuracy', 'relation_balanced_accuracy', 'value_mae')


def pin(path):
    path = Path(path)
    return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    if (OUT / 'findings_review_v1.json').exists():
        raise ValueError('completed comparison must be preserved')
    comparisons, choices, inputs = {}, {}, {}
    for name in ('llama8b', 'codellama34b'):
        config = base._json(ROOT / f'configs/binding/arithmetic_probe_selection_20261030_v2/{name}.json')
        revision.audit(config)
        path = Path(config['run_dir']) / 'results.json'
        current = base._json(path)
        inputs[name + '_revised'] = pin(path.resolve())
        choices[name] = current['choices']
        old_config = base._json(ROOT / f'configs/binding/arithmetic_graph_20261029_v3/{name}_readouts.json')
        receipt = base._json(Path(old_config['run_dir']) / 'completion_manifest_v1.json')
        entry = receipt['artifacts']['results']
        previous = base._json(entry['path'], entry['sha256'])
        inputs[name + '_original'] = pin(Path(entry['path']).resolve())
        comparisons[name] = {}
        for backend in ('hidden', 'source'):
            old_banks = [b for b in previous['fits'] if b['site'] == 2 and b['backend'] == backend]
            if len(old_banks) != 3:
                raise ValueError('three original weighting seeds required')
            families = sorted(old_banks[0]['development_family_metrics'])
            if len(families) != 12:
                raise ValueError('original structural DEV family coverage differs')
            before = {m: [] for m in METRICS}
            for bank in old_banks:
                old_metrics = bank['development_family_metrics']
                before['parent_accuracy'].append([old_metrics[g]['parent_accuracy'] for g in families])
                before['relation_balanced_accuracy'].append([old_metrics[g]['relations']['macro_balanced_accuracy'] for g in families])
                entry = bank['artifacts']['scores']
                if base._sha(entry['path']) != entry['sha256']:
                    raise ValueError('original score payload changed')
                inputs[f'{name}_{backend}_seed{bank["seed"]}_original_scores'] = pin(Path(entry['path']).resolve())
                with np.load(entry['path'], allow_pickle=False) as data:
                    predicted = original._decode(data['real'], bank['target_heads'], 'value') - 96
                    truth = original._decode(data['truth'], bank['target_heads'], 'value') - 96
                    cap = base._json(old_config['capture_config'], old_config['capture_config_sha256'])
                    rows = [json.loads(line) for line in Path(cap['dataset']).read_text().splitlines()]
                    groups = np.asarray([rows[i]['component_id'] for i in data['dev_indices']])
                    before['value_mae'].append([float(np.abs(predicted[groups == g] - truth[groups == g]).mean()) for g in families])
            after = {}
            for metric, task in [('parent_accuracy', 'parent_accuracy'), ('relation_balanced_accuracy', 'relation_balanced_accuracy'),
                                 ('value_mae', 'value_negative_mae')]:
                banks = [b for b in current['fits'] if b['backend'] == backend and b['selected_for'] == task]
                if len(banks) != 3:
                    raise ValueError('all three selected seeds required')
                values = []
                for bank in banks:
                    by_group = {e['group']: e[task] for e in bank['development']['family_metrics']}
                    if set(by_group) != set(families) or any(v is None for v in by_group.values()):
                        raise ValueError('paired family metric support differs')
                    values.append([(-1 if metric == 'value_mae' else 1) * by_group[g] for g in families])
                after[metric] = values
            cells = {}
            samples = np.random.default_rng(117).integers(0, 12, (2000, 12))
            for metric in METRICS:
                a, b = np.mean(before[metric], axis=0), np.mean(after[metric], axis=0)
                if not np.isfinite(a).all() or not np.isfinite(b).all():
                    raise ValueError('finite paired family metrics required')
                cells[metric] = dict(before=float(a.mean()), after=float(b.mean()),
                    before_family=a.tolist(), after_family=b.tolist(),
                    before_interval=np.quantile(a[samples].mean(axis=1), [.025, .975]).tolist(),
                    after_interval=np.quantile(b[samples].mean(axis=1), [.025, .975]).tolist(),
                    after_minus_before_interval=np.quantile((b - a)[samples].mean(axis=1), [.025, .975]).tolist())
            parents = [b for b in current['fits'] if b['backend'] == backend and b['selected_for'] == 'parent_accuracy']
            cells['whole_parent_after'] = float(np.mean([b['development']['whole_parent_accuracy'] for b in parents]))
            cells['whole_parent_before'] = float(np.mean([b['metrics']['direct']['whole_parent_accuracy'] for b in old_banks]))
            cells['parent_prior_before'] = float(np.mean([b['metrics']['train_prior']['parent_accuracy'] for b in old_banks]))
            comparisons[name][backend] = cells
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7))
    for ax, metric, title in zip(axes, METRICS, ['Dependency parents', 'Algebraic relations', 'Current numeric values']):
        for index, name in enumerate(('llama8b', 'codellama34b')):
            cell = comparisons[name]['hidden'][metric]
            scale = 1 if metric == 'value_mae' else 100
            for delta, key, color in [(-.18, 'before', '#cbd5e1'), (.18, 'after', '#307aab')]:
                value = cell[key] * scale
                lo, hi = np.asarray(cell[key + '_interval']) * scale
                ax.bar(index + delta, value, .31, color=color, label=key.capitalize() if index == 0 else None)
                ax.errorbar(index + delta, value, yerr=[[max(0, value - lo)], [max(0, hi - value)]], color='#334155', capsize=3, lw=1)
                ax.text(index + delta, hi + (.4 if metric == 'value_mae' else 2), f'{value:.2f}', ha='center', fontsize=9)
        ax.set_title(title)
        ax.set_xticks([0, 1], ['Llama 8B', 'CodeLlama 34B'])
        ax.spines[['top', 'right']].set_visible(False)
        if metric == 'value_mae':
            ax.set_ylabel('Mean absolute error; lower is better')
            ax.set_ylim(bottom=0)
        else:
            ax.set_ylabel('Family-macro accuracy (%)' if metric == 'parent_accuracy' else 'Family-macro balanced accuracy (%)')
            ax.set_ylim(0, 100)
        if metric == 'relation_balanced_accuracy':
            ax.axhline(50, color='#64748b', ls=':', lw=1)
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle('Probe revision on the previously examined structural DEV cohort', fontsize=15, y=.99)
    fig.text(.02, .015, 'Settings selected inside TRAIN for each objective. Fixed-fit 95% family-bootstrap intervals.\nNumeric decoding changes from categorical prediction to regression. Adaptive discovery; no causal or confirmatory claim.', fontsize=9)
    fig.tight_layout(rect=[0, .105, 1, .94])
    for extension in ('.png', '.svg'):
        fig.savefig(str(FIGURE) + extension, dpi=170, metadata={'Date': None} if extension == '.svg' else None)
    plt.close(fig)
    text = ['# Archived-feature probe revision: findings', '',
        'Settings were selected using grouped TRAIN validation and locked before scoring the previously examined DEV cohort. All original CV banks were reused under verified identical mathematics. No new language-model calls or CV fits were made during recovery. Selected settings were refitted on all TRAIN with three weighting seeds.', '',
        '![Aligned old/new probe comparison](figures/arithmetic_probe_selection_v1.png)', '',
        '| Model | Features | Parent accuracy before → after | Relation balanced accuracy before → after | Value MAE before → after | Whole graph after |',
        '|---|---|---|---|---|---|']
    for name, backends in comparisons.items():
        for backend, cells in backends.items():
            values = []
            for metric in METRICS:
                c = cells[metric]
                scale, suffix = (1, '') if metric == 'value_mae' else (100, '%')
                values.append(f"{c['before'] * scale:.2f}{suffix} → {c['after'] * scale:.2f}{suffix}")
            text.append(f"| {name} | {backend} | " + ' | '.join(values) + f" | {cells['whole_parent_after'] * 100:.2f}% |")
    text += ['', 'All table entries average weighting seeds within each of the same12 DEV families, then families equally. Relation figures therefore use family-macro balanced accuracy on both sides; the earlier pooled relation numbers have a different aggregation. Numeric MAE compares original categorical argmax values with continuous regression outputs. Whole-graph accuracy is from the dependency-selected decoder. Each objective has its own TRAIN-selected decoder; these are not three DEV-selected winners.', '',
        '| Model | Backend | Selection objective | Layer/features | Rank | Alpha |', '|---|---|---|---|---|---|']
    for name, backends in choices.items():
        for backend, tasks in backends.items():
            for task, choice in tasks.items():
                text.append(f"| {name} | {backend} | {task} | {choice['representation']} | {choice['rank']} | {choice['alpha']} |")
    text += ['', 'Intervals in the machine-readable review resample whole families conditional on fixed fits, after averaging seeds; they are exploratory and have no multiplicity correction. Source features receive their own TRAIN-only selection. All saved real/prior/shuffle outputs remain in the original result files. These findings cannot establish representational absence or natural causal use. The new local-dependency suite tests a different, distributed-accessibility question.', '',
        '[Implementation and launch](arithmetic_probe_improvement_launch_v1.md) · [New local experiment](arithmetic_local_probe_plan_v1.md)', '']
    base._publish(REPORT, '\n'.join(text).encode())
    review = dict(status='complete_exploratory', evaluation_role='arithmetic_probe_postrun_comparison_v1',
        comparisons=comparisons, choices=choices, inputs=inputs, renderer=pin(Path(__file__)),
        artifacts={name: pin(path) for name, path in [('report', REPORT), ('png', Path(str(FIGURE) + '.png')), ('svg', Path(str(FIGURE) + '.svg'))]},
        new_model_queries=0, new_fits=0, cv_fits_reused=90,
        limitations='Previously inspected12 DEV families; adaptive discovery. Relation aggregation aligned to family macro. Numeric target encoding changed.')
    base._put(OUT / 'findings_review_v1.json', review)
    print(json.dumps(dict(status=review['status'], comparisons=comparisons)))


if __name__ == '__main__':
    main()
