"""Verified descriptive grid and figure for completed query-value readouts.

The compact completion identity is checked before the public completed-result
reader opens scientific results. This renderer never loads arrays, fits models,
selects a seed or changes the stored scientific comparison.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import io
import json
import math
from pathlib import Path

from . import query_selectivity as query
from .datasets import digest
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable
from .representation_sensitivity import _json, _safe

ROLE = 'discovery_query_selectivity_figure_review_v1'
CONFIG_KEYS = {'study_config', 'study_config_sha256', 'completion_manifest',
    'completion_manifest_sha256', 'figure_png', 'figure_svg', 'review_artifact'}
OUTPUT_KEYS = ('figure_png', 'figure_svg', 'review_artifact')


def _pin(value):
    if (not isinstance(value, str) or len(value) != 64
            or any(character not in '0123456789abcdef' for character in value)):
        raise ValueError('explicit SHA256 metadata pins required')


def _metadata(config):
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise ValueError('exact source/figure/review configuration fields required')
    _discovery_declaration(config)
    for key in ('study_config', 'completion_manifest', *OUTPUT_KEYS):
        if not isinstance(config[key], str) or not config[key]:
            raise ValueError('explicit source/output paths required')
        _discovery_response_path(config[key]); _safe(config[key])
    for key in ('study_config_sha256', 'completion_manifest_sha256'):
        _pin(config[key])
    expected_suffix = dict(figure_png='.png', figure_svg='.svg', review_artifact='.json')
    if any(Path(config[key]).suffix != suffix for key, suffix in expected_suffix.items()):
        raise ValueError('PNG, SVG and compact JSON review output types required')
    outputs = [Path(config[key]).resolve() for key in OUTPUT_KEYS]
    if len(set(outputs)) != len(outputs):
        raise ValueError('distinct figure/review output paths required')
    study = _json(config['study_config'], config['study_config_sha256'])
    _discovery_declaration(study); query._config(study)
    expected = Path(study['run_dir'])/'completion_manifest_v2.json'
    if Path(config['completion_manifest']).resolve() != expected.resolve():
        raise ValueError('expected compact completion manifest path required')
    completion = _json(config['completion_manifest'], config['completion_manifest_sha256'])
    _discovery_declaration(completion)
    if (completion.get('schema_version') != 2 or completion.get('evaluation_role') != query.ROLE
            or completion.get('status') != 'complete_exploratory'
            or completion.get('config_hash') != digest(study)):
        raise ValueError('matching completed discovery role/config identity required before result access')
    protected = [config['study_config'], config['completion_manifest'], study['capture_config'], study['report']]
    for binding in (completion.get('review', {}), completion.get('registration', {})):
        if not isinstance(binding, dict) or not isinstance(binding.get('path'), str):
            raise ValueError('pinned completed scientific source paths required')
        _safe(binding['path']); _discovery_response_path(binding['path']); protected.append(binding['path'])
    artifacts = completion.get('artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError('completed scientific artifact inventory required')
    for binding in artifacts.values():
        if not isinstance(binding, dict) or not isinstance(binding.get('path'), str):
            raise ValueError('completed scientific artifact path required')
        _safe(binding['path']); _discovery_response_path(binding['path']); protected.append(binding['path'])
    if any(output == Path(path).resolve() for output in outputs for path in protected):
        raise ValueError('figure/review outputs cannot replace scientific source artifacts')
    source_snapshot = completion.get('fit_source', {}).get('snapshot')
    if not isinstance(source_snapshot, str) or not source_snapshot:
        raise ValueError('original fit source snapshot declaration required')
    snapshot = Path(source_snapshot).resolve()
    if any(output == snapshot or snapshot in output.parents for output in outputs):
        raise ValueError('figure/review outputs cannot modify the immutable fit source snapshot')
    return study, completion


def _number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('finite '+label+' in the registered domain required')
    return float(value)


def grid_summary(result):
    """Validate and average all fixed seeds at every saved grid location."""
    if (not isinstance(result, dict) or result.get('status') != 'complete_exploratory'
            or result.get('evaluation_role') != query.ROLE or result.get('heads') != list(query.HEADS)
            or result.get('cases') != 9216 or result.get('factorizations') != 45
            or result.get('independent_heads') != 180
            or any(result.get(key) is not False for key in ('generated_holdouts_opened', 'mechanism_C_fitted'))
            or result.get('new_model_queries') != 0):
        raise ValueError('complete fixed discovery query-selectivity result required')
    candidates = [('hidden', layer) for layer in query.LAYERS]+[('surface', -1)]
    expected = {(backend, layer, site, seed) for backend, layer in candidates
        for site in query.SITES for seed in query.SEEDS}
    fits = result.get('fits')
    if not isinstance(fits, list) or len(fits) != len(expected):
        raise ValueError('all 45 registered layer/site/backend/seed fits required')
    seen = set(); aggregate = defaultdict(dict)
    for fit in fits:
        if not isinstance(fit, dict):
            raise ValueError('registered fit metadata objects required')
        key = tuple(fit.get(name) for name in ('backend', 'layer', 'site', 'seed'))
        if (not isinstance(key[0], str) or type(key[1]) is not int or not isinstance(key[2], str)
                or type(key[3]) is not int or key not in expected or key in seen):
            raise ValueError('unique fixed layer/site/backend/seed fit required')
        seen.add(key)
        if fit.get('name') != query.fit_name(key[0], key[1], query.SITES.index(key[2]), key[3]):
            raise ValueError('fit name and registered grid identity differ')
        cells = fit.get('cells')
        if not isinstance(cells, list):
            raise ValueError('saved descriptive cells required')
        selected = {}; all_cells = set()
        for cell in cells:
            if not isinstance(cell, dict):
                raise ValueError('saved cell metadata object required')
            identity = tuple(cell.get(name) for name in ('split', 'condition', 'query_role'))
            if (any(not isinstance(value, str) for value in identity) or identity in all_cells or identity[0] not in ('train', 'development')
                    or identity[1] not in query.CONDITIONS or identity[2] not in ('all', 'current', 'saved')
                    or identity[0] == 'train' and identity[1] != 'neutral'):
                raise ValueError('unique supported discovery split/condition/query cell required')
            all_cells.add(identity)
            if identity[0] != 'development' or identity[2] != 'all':
                continue
            if (type(cell.get('n')) is not int or cell['n'] != 768
                    or type(cell.get('structural_groups')) is not int or cell['structural_groups'] != 6):
                raise ValueError('each development all-query cell requires 768 rows and six groups')
            heads = cell.get('heads')
            if not isinstance(heads, list) or len(heads) != 4:
                raise ValueError('four complete registered head accuracies required')
            metrics = {}
            for head in heads:
                if not isinstance(head, dict) or head.get('head') not in query.HEADS or head['head'] in metrics:
                    raise ValueError('unique registered queried/unqueried/shuffled heads required')
                if type(head.get('n')) is not int or head['n'] != 768:
                    raise ValueError('head accuracy row coverage differs from the registered cell')
                metrics[head['head']] = _number(head.get('accuracy'), 'accuracy', 0., 1.)
            selected[identity[1]] = metrics
        if set(selected) != set(query.CONDITIONS):
            raise ValueError('all three unique development all-query naming cells required per fit')
        for condition, metrics in selected.items():
            group = (*key[:3], condition)
            aggregate[group][key[3]] = metrics
    if seen != expected:
        raise ValueError('registered full fit grid coverage differs')
    grid = []
    for backend, layer in candidates:
        for site in query.SITES:
            for condition in query.CONDITIONS:
                values = aggregate[backend, layer, site, condition]
                if set(values) != set(query.SEEDS):
                    raise ValueError('all three fixed weighting seeds required before averaging')
                means = {head: sum(values[seed][head] for seed in query.SEEDS)/len(query.SEEDS)
                    for head in query.HEADS}
                grid.append(dict(backend=backend, layer=layer, site=site, condition=condition,
                    n=768, structural_groups=6, seeds=list(query.SEEDS), accuracy=means))
    saved = result.get('primary_comparison')
    if (not isinstance(saved, dict) or saved.get('primary') != query.PRIMARY
            or saved.get('contrast') != 'queried_minus_unqueried_accuracy'
            or type(saved.get('n')) is not int or saved['n'] != 768
            or type(saved.get('structural_groups')) is not int or saved['structural_groups'] != 6
            or saved.get('bootstrap') != query.BOOTSTRAP or saved.get('refits_per_draw') != 0
            or saved.get('multiplicity_adjusted') is not False or saved.get('seeds_are_replications') is not False):
        raise ValueError('fixed primary contrast and conditional uncertainty contract required')
    primary_cell = next(row for row in grid if all(row[key] == query.PRIMARY[key]
        for key in ('backend', 'layer', 'site', 'condition')))
    gap = primary_cell['accuracy']['queried']-primary_cell['accuracy']['unqueried']
    mean = _number(saved.get('mean_group_increment'), 'primary increment', -1., 1.)
    if abs(gap-mean) > 1e-12:
        raise ValueError('saved primary increment differs from the complete fixed-seed grid')
    interval = saved.get('conditional_group_bootstrap_95')
    if not isinstance(interval, list) or len(interval) != 2:
        raise ValueError('saved two-sided conditional primary interval required')
    low, high = [_number(value, 'conditional interval endpoint', -1., 1.) for value in interval]
    if low > high:
        raise ValueError('ordered conditional primary interval required')
    names, increments, sizes = (saved.get(key) for key in ('template_ids', 'template_increments', 'rows_per_template'))
    if (not isinstance(names, list) or len(names) != 6
            or any(not isinstance(value, str) or not value for value in names) or len(set(names)) != 6
            or not isinstance(increments, list) or len(increments) != 6
            or not isinstance(sizes, list) or sizes != [128]*6):
        raise ValueError('six balanced saved primary structural components required')
    checked = [_number(value, 'structural primary increment', -1., 1.) for value in increments]
    if abs(sum(checked)/6-mean) > 1e-12:
        raise ValueError('saved primary structural increments differ from their fixed mean')
    return dict(status='passed', fits=45, development_all_query_cells=135, mean_grid_cells=len(grid),
        seeds=list(query.SEEDS), aggregation='Unweighted mean of all three fixed neutral-training weighting fits; no seed or grid selection.',
        grid=grid, primary=dict(definition=deepcopy(query.PRIMARY),
            queried_accuracy=primary_cell['accuracy']['queried'], unqueried_accuracy=primary_cell['accuracy']['unqueried'],
            mean_increment=mean, conditional_group_bootstrap_95=[low, high], n=768, structural_groups=6,
            saved_comparison=deepcopy(saved)))


def _figure(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    by_key = {(row['backend'], row['layer'], row['site'], row['condition']): row['accuracy'] for row in summary['grid']}
    labels = {'pre_query_state': 'Before query', 'after_query': 'After query', 'pre_answer': 'Before answer'}
    styles = [
        ('queried', 'Hidden: queried', '#2357a0', '-', 'o'),
        ('unqueried', 'Hidden: unqueried', '#9a437c', '-', 's'),
        ('shuffled_queried', 'Hidden: shuffled queried', '#777777', '--', '^'),
        ('shuffled_unqueried', 'Hidden: shuffled unqueried', '#aaaaaa', (0, (2, 2)), 'v'),
    ]
    surface = [('queried', 'Surface: queried', '#18743b', (0, (1, 2))),
        ('unqueried', 'Surface: unqueried', '#61aa73', (0, (1, 5)))]
    with matplotlib.rc_context({'svg.hashsalt': 'binding-query-selectivity-review-v1', 'font.family': 'DejaVu Sans'}):
        fig, axes = plt.subplots(3, 3, figsize=(15, 11.8), sharex=True, sharey=True)
        for row_index, site in enumerate(query.SITES):
            for column, condition in enumerate(query.CONDITIONS):
                axis = axes[row_index, column]
                for head, _, color, linestyle, marker in styles:
                    values = [100*by_key['hidden', layer, site, condition][head] for layer in query.LAYERS]
                    axis.plot(query.LAYERS, values, color=color, linestyle=linestyle, marker=marker,
                        linewidth=1.7, markersize=4.5, zorder=3)
                for head, _, color, linestyle in surface:
                    axis.axhline(100*by_key['surface', -1, site, condition][head], color=color,
                        linestyle=linestyle, linewidth=2., zorder=2)
                axis.set_ylim(0, 100); axis.set_xlim(7, 32)
                axis.set_xticks(query.LAYERS); axis.set_yticks([0, 25, 50, 75, 100])
                axis.grid(alpha=.17); axis.tick_params(labelsize=9)
                if row_index == 0: axis.set_title(condition.title(), fontsize=12, pad=10)
                if column == 0: axis.set_ylabel(labels[site]+'\nAccuracy (%)', fontsize=11)
                if row_index == 2: axis.set_xlabel('Transformer block', fontsize=10)
                if site == query.PRIMARY['site'] and condition == query.PRIMARY['condition']:
                    primary = summary['primary']; layer = query.PRIMARY['layer']
                    axis.axvspan(layer-.55, layer+.55, color='#e6be53', alpha=.2, zorder=1)
                    axis.scatter([layer, layer], [100*primary['queried_accuracy'], 100*primary['unqueried_accuracy']],
                        s=110, facecolors='none', edgecolors='#ad7900', linewidths=1.5, zorder=5)
                    low, high = primary['conditional_group_bootstrap_95']
                    axis.text(.04, .51, f"Fixed primary: block {layer}\nQueried − unqueried: {100*primary['mean_increment']:+.2f} pp\nConditional 95%: [{100*low:.2f}, {100*high:.2f}] pp",
                        transform=axis.transAxes, fontsize=8.4, va='center',
                        bbox={'facecolor': '#fff9e8', 'edgecolor': '#e0c57f', 'alpha': .94, 'pad': 4})
        handles = [Line2D([], [], color=color, linestyle=linestyle, marker=marker,
            linewidth=1.7, markersize=4, label=label) for _, label, color, linestyle, marker in styles]
        handles += [Line2D([], [], color=color, linestyle=linestyle, linewidth=2., label=label)
            for _, label, color, linestyle in surface]
        fig.suptitle('Query value accessibility at saved token positions', fontsize=16, y=.99)
        fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .955), ncol=3, fontsize=9, frameon=False)
        fig.text(.5, .055, 'Each curve averages three fixed neutral-training weighting fits; all registered grid cells are shown.\n'
            'Curves are descriptive across transformer blocks; the three rows are saved token boundaries, not elapsed model steps.\n'
            'The fixed primary interval conditions on saved fits and six development components; it is not a causal or final-validation result.',
            ha='center', va='center', fontsize=9, linespacing=1.6)
        fig.tight_layout(rect=(.02, .105, .99, .885), h_pad=1.9, w_pad=1.4)
        images = {}
        for extension in ('png', 'svg'):
            stream = io.BytesIO()
            fig.savefig(stream, format=extension, dpi=170, facecolor='white',
                metadata={'Date': None} if extension == 'svg' else None)
            images[extension] = stream.getvalue()
        plt.close(fig)
    return images


def run(config):
    study, completion = _metadata(config)
    # The public reader validates every scientific result/source hash. It does
    # not load model/activation arrays or fit any head.
    result = query.completed_result(study)
    if result.get('config_hash') != digest(study):
        raise ValueError('verified result configuration differs from the pinned study')
    summary = grid_summary(result)
    if summary['primary']['saved_comparison'] != completion.get('primary_comparison'):
        raise ValueError('verified primary result differs from the pinned compact completion')
    images = _figure(summary)
    from .registry import code_identity
    figure_paths = [config['figure_png'], config['figure_svg']]
    review = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), analysis_source=code_identity(),
        source_study_config={'path': config['study_config'], 'sha256': config['study_config_sha256']},
        source_completion_manifest={'path': config['completion_manifest'], 'sha256': config['completion_manifest_sha256']},
        source_scientific_review=deepcopy(completion['review']), fit_source=deepcopy(completion['fit_source']),
        grid_summary=summary, figures=[{'path': path, 'sha256': hashlib.sha256(images[extension]).hexdigest()}
            for path, extension in zip(figure_paths, ('png', 'svg'))],
        new_readout_fits=0, model_arrays_loaded=0, activation_arrays_loaded=0, model_loading=False,
        new_model_queries=0, generated_holdouts_opened=False, mechanism_C_fitted=False, limitation=query.LIMITATION)
    payloads = {Path(config['figure_png']): images['png'], Path(config['figure_svg']): images['svg'],
        Path(config['review_artifact']): (json.dumps(review, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()}
    for path, content in payloads.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError('immutable query-selectivity figure/review artifact differs: '+str(path))
    for path, content in payloads.items():
        immutable(path, content)
    return dict(status='passed', fits=45, mean_grid_cells=45, review_artifact=config['review_artifact'],
        figures=figure_paths, source_completion_manifest_sha256=config['completion_manifest_sha256'])
