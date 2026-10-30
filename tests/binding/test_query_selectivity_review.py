"""Bounded source guards and complete descriptive grids, no scientific fits."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import query_selectivity as query
from codecue.binding import query_selectivity_review as review
from codecue.binding.datasets import digest


def result_grid():
    fits = []
    for backend, layer in [('hidden', value) for value in query.LAYERS]+[('surface', -1)]:
        for site_index, site in enumerate(query.SITES):
            for seed_index, seed in enumerate(query.SEEDS):
                cells = []
                offset = (seed_index-1)*.01
                for condition_index, condition in enumerate(query.CONDITIONS):
                    layer_index = query.LAYERS.index(layer) if backend == 'hidden' else 0
                    q = (.6+.02*layer_index+.05*site_index-.04*condition_index
                         if backend == 'hidden' else .25+.01*site_index)+offset
                    u = (.2+.01*layer_index-.02*condition_index
                         if backend == 'hidden' else .18+.01*site_index)+offset
                    values = (q, u, .035+offset, .04-offset)
                    cells.append({'split': 'development', 'condition': condition, 'query_role': 'all',
                        'n': 768, 'structural_groups': 6,
                        'heads': [{'head': head, 'n': 768, 'accuracy': value}
                                  for head, value in zip(query.HEADS, values)]})
                fits.append({'name': query.fit_name(backend, layer, site_index, seed),
                    'backend': backend, 'layer': layer, 'site': site, 'seed': seed, 'cells': cells})
    delta = .74-.22
    primary = dict(contrast='queried_minus_unqueried_accuracy', primary=deepcopy(query.PRIMARY),
        mean_group_increment=delta, conditional_group_bootstrap_95=[delta-.02, delta+.02],
        template_ids=[f'dev:group{i}' for i in range(6)], template_increments=[delta]*6,
        rows_per_template=[128]*6, n=768, structural_groups=6, bootstrap=deepcopy(query.BOOTSTRAP),
        refits_per_draw=0, multiplicity_adjusted=False, seeds_are_replications=False)
    return dict(status='complete_exploratory', evaluation_role=query.ROLE, heads=list(query.HEADS),
        cases=9216, factorizations=45, independent_heads=180, new_model_queries=0,
        generated_holdouts_opened=False, mechanism_C_fitted=False, fits=fits, primary_comparison=primary)


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')
    return path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture
def source(tmp_path, monkeypatch):
    study = dict(evaluation_role=query.ROLE, capture_config=str(tmp_path/'capture_config.json'),
        capture_config_sha256='a'*64, capture_audit_sha256='b'*64, capture_manifest_sha256='c'*64,
        run_dir=str(tmp_path/'scientific_results'), report=str(tmp_path/'scientific_report.md'))
    path = write(tmp_path/'study_config.json', study)
    completion = dict(schema_version=2, evaluation_role=query.ROLE, status='complete_exploratory',
        config_hash=digest(study), primary_comparison=result_grid()['primary_comparison'],
        fit_source={'snapshot': str(tmp_path/'original_fit_source'), 'snapshot_id': 'source', 'source_sha256': 'd'*64},
        review={'path': str(Path(study['run_dir'])/'review_v1.json'), 'sha256': 'e'*64, 'bytes': 10480000},
        registration={'path': str(Path(study['run_dir'])/'registration.json'), 'sha256': 'f'*64},
        artifacts={'summary': {'path': str(Path(study['run_dir'])/'summary.json'), 'sha256': '1'*64},
            'fit': {'path': str(Path(study['run_dir'])/'fit.npz'), 'sha256': '2'*64}})
    manifest = write(Path(study['run_dir'])/'completion_manifest_v2.json', completion)
    config = dict(study_config=str(path), study_config_sha256=sha(path), completion_manifest=str(manifest),
        completion_manifest_sha256=sha(manifest), figure_png=str(tmp_path/'figures/grid.png'),
        figure_svg=str(tmp_path/'figures/grid.svg'), review_artifact=str(tmp_path/'figure_review.json'))
    value = result_grid(); value['config_hash'] = digest(study)
    calls = []
    def completed(study_config):
        assert study_config == study
        calls.append(True)
        return deepcopy(value)
    monkeypatch.setattr(query, 'completed_result', completed, raising=False)
    from codecue.binding import registry
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': '3'*64})
    return dict(config=config, study=study, completion=completion, result=value, calls=calls)


def test_all_grid_means_use_three_fixed_seeds_and_primary_is_preserved():
    source = result_grid(); result = review.grid_summary(source)
    assert result['fits'] == 45 and result['development_all_query_cells'] == 135
    assert result['mean_grid_cells'] == len(result['grid']) == 45
    assert result['seeds'] == [11, 29, 47]
    primary = result['primary']
    assert primary['definition'] == query.PRIMARY
    assert primary['queried_accuracy'] == pytest.approx(.74)
    assert primary['unqueried_accuracy'] == pytest.approx(.22)
    assert primary['mean_increment'] == pytest.approx(.52)
    assert primary['saved_comparison'] == source['primary_comparison']
    for cell in result['grid']:
        assert cell['seeds'] == [11, 29, 47]
        assert set(cell['accuracy']) == set(query.HEADS)
        assert cell['n'] == 768 and cell['structural_groups'] == 6
    # Neither fit/cell order nor head serialization order may select a seed.
    shuffled = deepcopy(source); shuffled['fits'].reverse()
    for fit in shuffled['fits']:
        fit['cells'].reverse()
        for cell in fit['cells']: cell['heads'].reverse()
    assert review.grid_summary(shuffled) == result


@pytest.mark.parametrize('change', ['missing_fit', 'duplicate_fit', 'unsupported_layer', 'unsupported_backend',
    'unsupported_site', 'unsupported_seed', 'fit_name', 'missing_cell', 'duplicate_cell', 'unsupported_cell',
    'bad_split', 'bad_query_role', 'n', 'groups', 'missing_head', 'duplicate_head', 'unsupported_head',
    'head_n', 'accuracy_nan', 'accuracy_inf', 'accuracy_negative', 'accuracy_above_one', 'accuracy_bool',
    'role', 'status', 'heads', 'heldout', 'new_query'])
def test_missing_duplicate_or_unsupported_grid_data_are_rejected(change):
    result = result_grid(); fit = result['fits'][0]; cell = fit['cells'][0]; head = cell['heads'][0]
    if change == 'missing_fit': result['fits'].pop()
    elif change == 'duplicate_fit': result['fits'][-1] = deepcopy(fit)
    elif change == 'unsupported_layer': fit['layer'] = 30
    elif change == 'unsupported_backend': fit['backend'] = 'selected_best'
    elif change == 'unsupported_site': fit['site'] = 'timestep'
    elif change == 'unsupported_seed': fit['seed'] = 99
    elif change == 'fit_name': fit['name'] = 'other'
    elif change == 'missing_cell': fit['cells'].pop()
    elif change == 'duplicate_cell': fit['cells'].append(deepcopy(cell))
    elif change == 'unsupported_cell': cell['condition'] = 'test'
    elif change == 'bad_split': cell['split'] = 'test'
    elif change == 'bad_query_role': cell['query_role'] = 'unknown'
    elif change == 'n': cell['n'] = 767
    elif change == 'groups': cell['structural_groups'] = 5
    elif change == 'missing_head': cell['heads'].pop()
    elif change == 'duplicate_head': cell['heads'][-1] = deepcopy(head)
    elif change == 'unsupported_head': head['head'] = 'selected_best'
    elif change == 'head_n': head['n'] = 767
    elif change == 'accuracy_nan': head['accuracy'] = float('nan')
    elif change == 'accuracy_inf': head['accuracy'] = float('inf')
    elif change == 'accuracy_negative': head['accuracy'] = -.01
    elif change == 'accuracy_above_one': head['accuracy'] = 1.01
    elif change == 'accuracy_bool': head['accuracy'] = True
    elif change == 'role': result['evaluation_role'] = 'final_evaluation'
    elif change == 'status': result['status'] = 'running'
    elif change == 'heads': result['heads'] = list(query.HEADS[:2])
    elif change == 'heldout': result['generated_holdouts_opened'] = True
    else: result['new_model_queries'] = 1
    with pytest.raises(ValueError): review.grid_summary(result)


@pytest.mark.parametrize('change', ['definition', 'contrast', 'mean', 'interval_order', 'interval_domain',
    'n', 'groups', 'bootstrap', 'refits', 'multiplicity', 'replications', 'template_ids', 'template_sizes', 'template_means'])
def test_primary_definition_delta_and_uncertainty_contract_cannot_change(change):
    result = result_grid(); primary = result['primary_comparison']
    if change == 'definition': primary['primary']['layer'] = 31
    elif change == 'contrast': primary['contrast'] = 'best_layer'
    elif change == 'mean': primary['mean_group_increment'] += .1
    elif change == 'interval_order': primary['conditional_group_bootstrap_95'] = [.8, .2]
    elif change == 'interval_domain': primary['conditional_group_bootstrap_95'] = [-2., 2.]
    elif change == 'n': primary['n'] = 767
    elif change == 'groups': primary['structural_groups'] = 5
    elif change == 'bootstrap': primary['bootstrap']['draws'] = 10
    elif change == 'refits': primary['refits_per_draw'] = 1
    elif change == 'multiplicity': primary['multiplicity_adjusted'] = True
    elif change == 'replications': primary['seeds_are_replications'] = True
    elif change == 'template_ids': primary['template_ids'][0] = primary['template_ids'][1]
    elif change == 'template_sizes': primary['rows_per_template'] = [127, 129]+[128]*4
    else: primary['template_increments'][0] += .1
    with pytest.raises(ValueError): review.grid_summary(result)


@pytest.mark.parametrize('change', ['config_pin', 'completion_pin', 'completion_role', 'completion_status',
    'completion_schema', 'completion_config', 'completion_path', 'study_role', 'unknown_key',
    'reserved_output', 'reserved_input', 'input_alias', 'scientific_alias', 'snapshot_output', 'duplicate_output'])
def test_source_and_output_guards_precede_public_result_reader(source, monkeypatch, change):
    config = source['config']
    if change == 'config_pin': config['study_config_sha256'] = '0'*64
    elif change == 'completion_pin': config['completion_manifest_sha256'] = '0'*64
    elif change.startswith('completion_') and change != 'completion_path':
        completion = source['completion']
        field, value = {'completion_role': ('evaluation_role', 'final_evaluation'),
            'completion_status': ('status', 'running'), 'completion_schema': ('schema_version', 1),
            'completion_config': ('config_hash', '0'*64)}[change]
        completion[field] = value; write(config['completion_manifest'], completion)
        config['completion_manifest_sha256'] = sha(config['completion_manifest'])
    elif change == 'completion_path': config['completion_manifest'] = str(Path(config['completion_manifest']).parent/'other.json')
    elif change == 'study_role':
        source['study']['evaluation_role'] = 'final_evaluation'; write(config['study_config'], source['study'])
        config['study_config_sha256'] = sha(config['study_config'])
    elif change == 'unknown_key': config['choose_best'] = True
    elif change == 'reserved_output': config['figure_png'] = '/tmp/final/grid.png'
    elif change == 'reserved_input': config['study_config'] = '/tmp/final/study.json'
    elif change == 'input_alias': config['review_artifact'] = config['study_config']
    elif change == 'scientific_alias': config['review_artifact'] = source['completion']['artifacts']['summary']['path']
    elif change == 'snapshot_output': config['figure_png'] = str(Path(source['completion']['fit_source']['snapshot'])/'grid.png')
    else: config['review_artifact'] = config['figure_svg']
    def forbidden(*args, **kwargs): raise AssertionError('public rich-result reader called before metadata rejection')
    monkeypatch.setattr(query, 'completed_result', forbidden, raising=False)
    with pytest.raises(ValueError): review.run(config)
    assert not source['calls']


def test_verified_but_inconsistent_grid_is_rejected_before_rendering(source, monkeypatch):
    source['result']['primary_comparison']['mean_group_increment'] += .1
    monkeypatch.setattr(review, '_figure', lambda value: pytest.fail('invalid fixed grid must precede plotting'))
    with pytest.raises(ValueError): review.run(source['config'])
    assert source['calls'] == [True]
    assert not Path(source['config']['figure_png']).exists()


def test_rendered_review_is_compact_immutable_and_has_no_array_loads(source, monkeypatch):
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('figure review must not load model or activation arrays'))
    result = review.run(source['config']); config = source['config']
    assert result['status'] == 'passed' and result['fits'] == result['mean_grid_cells'] == 45
    assert Path(config['figure_png']).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    svg = Path(config['figure_svg']).read_text()
    assert '<svg' in svg and '<dc:date>' not in svg
    assert 'saved token positions' in svg and 'Transformer block' in svg
    saved = json.loads(Path(config['review_artifact']).read_text())
    assert Path(config['review_artifact']).stat().st_size < 100000
    assert saved['grid_summary']['primary']['mean_increment'] == pytest.approx(.52)
    assert saved['new_readout_fits'] == saved['model_arrays_loaded'] == saved['activation_arrays_loaded'] == 0
    assert saved['source_completion_manifest']['sha256'] == config['completion_manifest_sha256']
    assert saved['fit_source'] == source['completion']['fit_source']
    for figure in saved['figures']: assert sha(figure['path']) == figure['sha256']
    assert review.run(config) == result
    Path(config['figure_svg']).write_text('changed')
    with pytest.raises(ValueError, match='immutable'): review.run(config)
