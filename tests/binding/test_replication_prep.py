"""Generated-source preparation checks; no model outcomes or tokenizer loads."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from codecue.binding import replication_prep as prep
from codecue.binding import registry
from codecue.binding.datasets import read_jsonl
from codecue.binding.published_benchmarks import sha


@pytest.fixture(autouse=True)
def stable_source(monkeypatch):
    # Source files may be concurrently edited by other software-prep workers.
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'fixture'})


def recipe(tmp_path, kinds=('arithmetic_readout',)):
    generation = {
        'competition': dict(seed=41, numeric_per_template=1),
        'live_load': dict(seed=43, templates=1, numeric_per_template=2,
                          noise_pairs=1, initialize_results=True),
        'arithmetic_readout': dict(seed=47, numeric_per_stratum=2, operand_max=9),
    }
    return dict(banks=[dict(name=kind, kind=kind, generation=generation[kind],
                            dataset=str(tmp_path / (kind + '.jsonl'))) for kind in kinds],
                output=str(tmp_path / 'review.json'), report=str(tmp_path / 'review.md'))


def row(identity, source, split='train', **extra):
    return dict(id=identity, source=source, canonical_source=source, split=split,
                evaluation_role=prep._roles()['competition'], **extra)


def bank(name, rows):
    return dict(name=name, kind='competition', rows=rows)


def test_plan_is_exact_and_does_not_touch_payloads_or_write(tmp_path, monkeypatch):
    config = recipe(tmp_path, prep.KINDS)
    monkeypatch.setattr(prep, 'read_jsonl', lambda _: pytest.fail('plan read payload'))
    result = prep.plan(config)
    assert result['expected_rows'] == 1248 + 198 + 96
    assert [entry['expected_rows'] for entry in result['banks']] == [1248, 198, 96]
    assert result['banks'][0]['generator_config'] == {
        **config['banks'][0]['generation'], 'dataset': config['banks'][0]['dataset']}
    assert result['banks'][1]['generator_config']['generation']['initialize_results'] is True
    assert not result['writes_performed'] and not result['generated_holdouts_opened']
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('change', ['seed', 'name', 'dataset', 'sidecar', 'review', 'inventory'])
def test_duplicate_seeds_names_and_any_artifact_collision_are_rejected(tmp_path, change):
    config = recipe(tmp_path)
    if change in ('seed', 'name', 'dataset', 'sidecar'):
        second = deepcopy(config['banks'][0])
        second['name'] = 'second'
        second['generation']['seed'] += 1
        second['dataset'] = str(tmp_path / 'second.jsonl')
        if change == 'seed': second['generation']['seed'] -= 1
        if change == 'name': second['name'] = config['banks'][0]['name']
        if change == 'dataset': second['dataset'] = config['banks'][0]['dataset']
        if change == 'sidecar': config['manifest'] = str(Path(second['dataset']).with_suffix('.manifest.json'))
        config['banks'].append(second)
    elif change == 'review': config['manifest'] = config['output']
    else: config['inventory'] = config['banks'][0]['dataset']
    with pytest.raises(ValueError): prep.plan(config)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('declaration', [
    {'evaluation_role': 'sealed_final_outcomes'}, {'split': 'test'},
    {'splits': ['train', 'final']}, {'split_override': 'extrapolation'},
])
def test_reserved_generation_declarations_are_rejected(tmp_path, declaration):
    config = recipe(tmp_path)
    config['banks'][0]['generation'].update(declaration)
    with pytest.raises(ValueError): prep.plan(config)


@pytest.mark.parametrize('name', ['final_sources.jsonl', 'test.jsonl', 'reserved_bank.jsonl'])
def test_reserved_source_paths_are_rejected(tmp_path, name):
    config = recipe(tmp_path)
    config['banks'][0]['dataset'] = str(tmp_path / name)
    with pytest.raises(ValueError): prep.plan(config)


@pytest.mark.parametrize('scope', ['config', 'bank', 'generation'])
def test_declared_roles_must_match_the_registered_discovery_generator(tmp_path, scope):
    config = recipe(tmp_path)
    target = config if scope == 'config' else config['banks'][0]
    if scope == 'generation': target = target['generation']
    target['evaluation_role'] = 'unrelated_discovery'
    with pytest.raises(ValueError, match='role differs'): prep.plan(config)


@pytest.mark.parametrize('kind,expected', [('competition',1248), ('live_load',198),
                                         ('arithmetic_readout',96)])
def test_real_tiny_generators_validate_reuse_and_emit_immutable_provenance(tmp_path, kind, expected):
    config = recipe(tmp_path, (kind,))
    result = prep.build(config)
    artifacts = {key: Path(path) for key,path in prep.plan(config)['artifacts'].items()}
    source = Path(config['banks'][0]['dataset'])
    paths = [*artifacts.values(),source,source.with_suffix('.manifest.json')]
    original = {path:path.read_bytes() for path in paths}
    assert result['total_rows'] == expected
    assert result['evaluation_role'] == prep.ROLE and result['status'] == 'passed'
    assert not result['confirmatory_eligibility'] and not result['automatic_pooling_allowed']
    assert not result['model_inference'] and not result['generated_holdouts_opened']
    assert len(read_jsonl(artifacts['inventory'])) == expected
    assert result['fingerprint_inventory_sha256'] == sha(artifacts['inventory'])
    assert result['cohort_hashes'][kind]['sha256'] == sha(source)
    package = json.loads(artifacts['manifest'].read_text())
    assert package['review_sha256'] == sha(artifacts['output'])
    assert package['sha256'] == sha(artifacts['inventory'])
    assert prep.build(config) == result
    assert prep.audit(config) == result
    assert {path:path.read_bytes() for path in paths} == original
    if kind == 'arithmetic_readout':
        assert result['banks'][0]['alpha_skeletons_crossing_train_development'] > 0
        assert result['components_crossing_train_development'] > 0


def test_existing_manifest_role_and_recipe_checked_before_payload_open(tmp_path, monkeypatch):
    config = recipe(tmp_path)
    prep.build(config)
    source = Path(config['banks'][0]['dataset'])
    original = source.read_bytes()
    monkeypatch.setattr(prep, 'read_jsonl', lambda _: pytest.fail('untrusted payload opened'))
    changed = deepcopy(config)
    changed['banks'][0]['generation']['seed'] += 1
    with pytest.raises(ValueError, match='generation changed'): prep.build(changed)
    sidecar = source.with_suffix('.manifest.json')
    manifest = json.loads(sidecar.read_text())
    manifest['evaluation_role'] = 'reserved_final_outcomes'
    sidecar.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='reserved or final'): prep.audit(config)
    assert source.read_bytes() == original


def test_partial_existing_bank_is_never_overwritten(tmp_path):
    config = recipe(tmp_path)
    source = Path(config['banks'][0]['dataset'])
    source.write_bytes(b'incomplete')
    with pytest.raises(ValueError, match='complete immutable'): prep.build(config)
    assert source.read_bytes() == b'incomplete'
    assert not Path(config['output']).exists()


def test_source_hash_and_existing_generator_semantics_are_checked(tmp_path):
    config = recipe(tmp_path)
    prep.build(config)
    source = Path(config['banks'][0]['dataset'])
    source.write_bytes(source.read_bytes() + b'\n')
    with pytest.raises(ValueError, match='source hash differs'): prep.audit(config)
    records = read_jsonl(source)
    records[0]['expected_answer'] += 1
    source.write_text(''.join(json.dumps(record)+'\n' for record in records))
    sidecar = source.with_suffix('.manifest.json')
    manifest = json.loads(sidecar.read_text())
    manifest['sha256'] = sha(source)
    sidecar.write_text(json.dumps(manifest))
    with pytest.raises(ValueError): prep.audit(config)


def test_cross_bank_content_overlap_and_train_development_relatives_are_visible():
    a = row('a', 'x=1\ny=2\nx')
    b = row('b', 'x=7\ny=8\nx', split='development')
    c = row('c', a['source'], split='development')
    result = prep.audit_rows([bank('left',[a]),bank('right',[b,c])])
    pair = result['bank_pairs'][0]
    assert pair['shared_row_id'] == 0
    assert pair['shared_source_sha256'] == pair['shared_canonical_ast_sha256'] == 1
    assert pair['shared_alpha_skeleton_sha256'] == 1
    assert pair['alpha_skeletons_crossing_bank_train_development'] == 1
    assert pair['split_pairs'] == [dict(left_split='train', right_split='development',
        shared_row_id=0, shared_source_sha256=1, shared_canonical_ast_sha256=1,
        shared_alpha_skeleton_sha256=1)]
    assert pair['shared_skeletons_with_different_canonical_variants'] == 1
    assert result['content_relation_component_count'] == 1
    assert result['components_crossing_train_development'] == 1
    assert result['banks'][1]['unique_source_hashes'] == 2
    assert result['banks'][1]['unique_alpha_skeletons'] == 1
    assert result['source_preparation_opportunities']['bank_pairs_with_shared_source_prompts'] == 1
    assert result['source_preparation_opportunities']['bank_pairs_with_different_canonical_variants_on_shared_skeletons'] == 1
    assert prep.fingerprints(a)['source_sha256'] == hashlib.sha256(a['source'].encode()).hexdigest()


def test_reused_template_and_base_labels_do_not_join_different_bank_structures():
    a = row('a', 'x=1\ny=2\nx', template_id='shared', base_id='shared')
    b = row('b', 'y=5\nx=8\nx', template_id='shared', base_id='shared')
    result = prep.audit_rows([bank('left',[a]),bank('right',[b])])
    assert result['bank_pairs'][0]['shared_alpha_skeleton_sha256'] == 0
    assert result['content_relation_component_count'] == 2
    assert len(result['declared_template_ids_reused_with_different_content']) == 1
    assert len(result['declared_base_ids_reused_with_different_content']) == 1


def test_bank_local_relations_join_content_and_component_ids_are_order_invariant():
    rows = [row('a','x=1\ny=2\nx',base_id='relative'),
            row('b','x=1\ny=2\ny',split='development',base_id='relative')]
    banks = [bank('left',rows), bank('right',[row('c','x=7\ny=9\nx')])]
    first = prep.audit_rows(banks)
    second = prep.audit_rows([banks[1],bank('left',list(reversed(rows)))])
    assert first['content_relation_component_count'] == 1
    assert first['components_crossing_train_development'] == 1
    assert first['content_relation_components'] == second['content_relation_components']
    assert first['banks'][0]['within_bank_split_overlap'] == [dict(
        left_split='development', right_split='train', shared_row_id=0,
        shared_source_sha256=0, shared_canonical_ast_sha256=0, shared_alpha_skeleton_sha256=0)]


def test_row_identity_collision_is_reported_and_shared_numeric_content_not_hidden():
    a = row('same','x=1\nx')
    b = row('same','x=2\nx')
    result = prep.audit_rows([bank('left',[a]),bank('right',[b])])
    assert result['status'] == 'needs_attention'
    assert result['bank_pairs'][0]['shared_row_id'] == 1
    assert result['bank_pairs'][0]['shared_alpha_skeleton_sha256'] == 1
    assert len(result['row_ids_reused_with_different_sources']) == 1
    assert not result['confirmatory_eligibility']


@pytest.mark.parametrize('change', ['duplicate', 'missing_id', 'split', 'role', 'kind'])
def test_unvalidated_row_identity_and_reserved_metadata_refused(change):
    rows = [row('a','x=1\nx')]
    sample = bank('left', rows)
    if change == 'duplicate': rows.append(deepcopy(rows[0]))
    elif change == 'missing_id': del rows[0]['id']
    elif change == 'split': rows[0]['split'] = 'final'
    elif change == 'role': rows[0]['evaluation_role'] = 'unrelated_discovery'
    else: sample['kind'] = 'unregistered'
    with pytest.raises(ValueError): prep.audit_rows([sample])
