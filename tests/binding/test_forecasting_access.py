"""Outcome-access guards use only temporary synthetic programs and responses."""
import hashlib
import json
from pathlib import Path

import pytest

from codecue.binding import forecasting


@pytest.fixture
def fixture(tmp_path):
    dataset=tmp_path/'source.jsonl';responses=tmp_path/'responses.jsonl';features=tmp_path/'features.jsonl'
    rows=[];observed=[];table=[]
    for i in range(14):
        split='train' if i<8 else 'development' if i<12 else 'test'
        rows.append(dict(id=str(i),split=split,control_kind='primary',expected_answer=1,
                         cluster_id=f'{split}:{i//2}'))
        if split!='test':
            observed.append(dict(id=str(i),prediction=i%2))
            table.append(dict(id=str(i),features=dict(a=float(i),b=float(i%3),c=float(i%4),d=float(i%5))))
    def write_jsonl(path,values):
        path.write_text(''.join(json.dumps(value)+'\n' for value in values))
    write_jsonl(dataset,rows);write_jsonl(responses,observed);write_jsonl(features,table)
    manifest=dict(status='complete',identity_hash='legacy-software-fixture',identity=dict(
        dataset_manifest=dict(sha256=hashlib.sha256(dataset.read_bytes()).hexdigest()),model_revision='software-fixture'))
    path=responses.with_name('manifest.json');path.write_text(json.dumps(manifest))
    config=dict(dataset=str(dataset),model_revision='software-fixture',run_dir=str(tmp_path/'fits'),forecasting=dict(
        discovery_responses=str(responses),feature_table=str(features),l2_grid=[1.],features=dict(
            A_input=['a'],B_behavior=['a','b'],C_measurements=['a','b','c'],cheap_stress_test=['a','d'])))
    return dict(config=config,manifest=manifest,manifest_path=path,dataset=dataset,
                responses=responses,features=features,rows=rows,observed=observed)


def track_outcome_access(monkeypatch,fixture):
    original=forecasting.read_jsonl;opened=[]
    def read(path):
        target=Path(path).resolve();opened.append(target)
        if target==fixture['responses'].resolve():
            raise AssertionError('refused configuration opened model outcomes')
        return original(path)
    monkeypatch.setattr(forecasting,'read_jsonl',read)
    return opened


@pytest.mark.parametrize('location', ['config_role','config_generation','dataset_manifest',
                                     'behavior_role','behavior_config','behavior_dataset'])
def test_declared_reserved_roles_are_refused_before_opening_outcomes(fixture,monkeypatch,location):
    cfg=fixture['config'];manifest=fixture['manifest']
    if location=='config_role':
        cfg['evaluation_role']='final'
    elif location=='config_generation':
        cfg['generation']=dict(evaluation_role='structural_extrapolation',split_override='test')
    elif location=='dataset_manifest':
        fixture['dataset'].with_suffix('.manifest.json').write_text(json.dumps(dict(
            evaluation_role='structural_extrapolation',sha256=manifest['identity']['dataset_manifest']['sha256'])))
    elif location=='behavior_role':
        manifest['evaluation_role']='held_out'
    elif location=='behavior_config':
        manifest['identity']['config']=dict(splits=['train','test'],discovery_test_acknowledged=True)
    else:
        manifest['identity']['dataset_manifest']['evaluation_role']='sealed_final'
    fixture['manifest_path'].write_text(json.dumps(manifest))
    opened=track_outcome_access(monkeypatch,fixture)
    with pytest.raises(ValueError,match='cannot open test'):
        forecasting.fit(cfg)
    assert fixture['responses'] not in opened
    assert fixture['features'] not in opened


@pytest.mark.parametrize('relative', ['final/responses.jsonl','test/responses.jsonl',
                                    'extrapolation_depth_full_behavior/responses.jsonl',
                                    'final_responses.jsonl','test_responses.jsonl','extrapolation_responses.jsonl'])
def test_reserved_legacy_paths_are_refused_before_opening_outcomes(fixture,monkeypatch,relative):
    path=fixture['dataset'].parent/relative
    fixture['config']['forecasting']['discovery_responses']=str(path)
    fixture['responses']=path
    opened=track_outcome_access(monkeypatch,fixture)
    with pytest.raises(ValueError,match='reserved outcome paths'):
        forecasting.fit(fixture['config'])
    assert path not in opened


@pytest.mark.parametrize('change', ['status','dataset_hash','revision','missing_identity','missing_identity_hash',
                                    'source_sidecar','nested_revision','nested_model'])
def test_incompatible_response_provenance_is_refused_before_opening_outcomes(fixture,monkeypatch,change):
    manifest=fixture['manifest']
    if change=='status':
        manifest['status']='started'
    elif change=='dataset_hash':
        manifest['identity']['dataset_manifest']['sha256']='0'*64
    elif change=='revision':
        manifest['identity']['model_revision']='different-checkpoint'
    elif change=='missing_identity':
        manifest.pop('identity')
    elif change=='missing_identity_hash':
        manifest.pop('identity_hash')
    elif change=='source_sidecar':
        fixture['dataset'].with_suffix('.manifest.json').write_text(json.dumps(dict(sha256='0'*64)))
    elif change=='nested_revision':
        manifest['identity']['config']=dict(model_revision='different-checkpoint')
    else:
        fixture['config']['model']='model-expected'
        manifest['identity']['config']=dict(model='different-model')
    fixture['manifest_path'].write_text(json.dumps(manifest))
    opened=track_outcome_access(monkeypatch,fixture)
    with pytest.raises(ValueError):
        forecasting.fit(fixture['config'])
    assert fixture['responses'] not in opened
    assert fixture['features'] not in opened


def test_test_only_source_refused_before_even_requiring_response_manifest(fixture,monkeypatch):
    fixture['dataset'].write_text(json.dumps(dict(id='held',split='test'))+'\n')
    fixture['manifest_path'].unlink()
    opened=track_outcome_access(monkeypatch,fixture)
    with pytest.raises(ValueError,match='cannot open test outcomes'):
        forecasting.fit(fixture['config'])
    assert fixture['responses'] not in opened


def test_valid_legacy_mixed_source_still_fits_without_new_metadata_fields(fixture,monkeypatch):
    from codecue.binding import registry
    monkeypatch.setattr(registry,'code_identity',lambda:dict(source_sha256='software-fixture'))
    result=forecasting.fit(fixture['config'])
    fitted=json.loads(Path(result['fit']).read_text())
    assert fitted['train_n']==8 and fitted['development_n']==4
    assert fitted['behavior_identity_hash']=='legacy-software-fixture'
    assert set(fitted['models'])==set(forecasting.PREDICTORS)


@pytest.mark.parametrize('response', [dict(id='12',prediction=0),dict(id='unknown',prediction=0)])
def test_untyped_legacy_response_ids_are_still_checked_before_features(fixture,monkeypatch,response):
    original=forecasting.read_jsonl;opened=[]
    def read(path):
        opened.append(Path(path).resolve())
        if Path(path).resolve()==fixture['features'].resolve():
            raise AssertionError('invalid response identities reached feature collection')
        return original(path)
    fixture['responses'].write_text(json.dumps(response)+'\n')
    monkeypatch.setattr(forecasting,'read_jsonl',read)
    with pytest.raises(ValueError,match='cannot open test outcomes'):
        forecasting.fit(fixture['config'])
    assert fixture['responses'] in opened
    assert fixture['features'] not in opened
