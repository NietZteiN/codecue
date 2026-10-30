"""Capacity/access checks use synthetic source programs and statistical fixtures."""
import ast
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import discovery_controls as controls
from codecue.binding import discovery_features as base
from codecue.binding import discovery_prediction as prediction
from codecue.binding.published_benchmarks import sha
from test_discovery_prediction import cv_rows, cv_plan, paired_cases


PROFILE={'feature_profile':'capacity_oracle_v1'}
TIERS=('prior','A_input','A_interactions','A_interactions_neutral_raw',
       'A_interactions_neutral_scored','A_interactions_oracle',
       'A_interactions_oracle_neutral_raw','A_interactions_oracle_neutral_scored')
PAIRS=('u_c','u_m','u_q','u_t','c_m','c_q','c_t','m_q','m_t','q_t')
TRIPLES=('u_c_m','u_c_q','u_c_t','u_m_q','u_m_t','u_q_t','c_m_q','c_m_t','c_q_t','m_q_t')


class NoOutcomeOrOracle(dict):
    def __getitem__(self,key):
        if key in {'label','target_invalid','expected_answer','execution_trace',
                   'error_alternatives',*controls.ORACLE_COLUMNS} or key.startswith('neutral_'):
            raise AssertionError('source interaction touched outcome or oracle information')
        return super().__getitem__(key)

    def get(self,key,default=None):
        return self[key] if key in self else default


@pytest.mark.parametrize('bits,distance',[
    ((0,0,0,0,0),4),((1,1,1,1,1),3),((1,0,1,0,1),7),
])
def test_fixed_source_interactions_match_design_and_never_read_outcomes(bits,distance):
    u,c,m,q,t=bits
    source=NoOutcomeOrOracle(updates=1+2*u,available_bindings=2+2*c,
        misleading=m,query_saved=q,tail_after=t,query_last_definition_distance=distance,
        label=1,target_invalid=True,expected_answer=99,execution_trace=['forbidden'],
        oracle_answer_value=99,neutral_failure=1)
    observed=controls.interaction_features(source)
    expected_columns=tuple('interaction_'+code for code in PAIRS+TRIPLES)+tuple(
        'distance_x_'+code for code in ('u','c','m','q','t'))
    assert controls.INTERACTION_COLUMNS==expected_columns
    assert len(observed)==25 and len(set(observed))==25
    values=dict(zip(('u','c','m','q','t'),bits))
    for code in PAIRS+TRIPLES:
        expected=float(all(values[bit] for bit in code.split('_')))
        assert observed['interaction_'+code]==expected
    for bit,value in values.items():assert observed['distance_x_'+bit]==distance*value
    assert controls.interaction_features({'features':source})==observed
    assert controls.source_features(source)==observed


@pytest.mark.parametrize('field,value',[
    ('updates',2),('available_bindings',3),('misleading',2),
    ('query_last_definition_distance',-1),('query_last_definition_distance',float('nan')),
])
def test_source_interactions_reject_unregistered_or_nonfinite_design_fields(field,value):
    source=dict(updates=1,available_bindings=2,misleading=0,query_saved=0,
                tail_after=0,query_last_definition_distance=1)
    source[field]=value
    with pytest.raises(ValueError):controls.interaction_features(source)


@pytest.mark.parametrize('source,answer',[
    ('v0 = -7\nsaved = v0\nv0 = 4\nsaved',-7),
    ('v0 = 3\nsaved = v0\nv0 = 8\nv0',8),
    ('v0 = 0\nv0',0),
])
def test_declared_oracle_features_execute_source_instead_of_stored_answers(source,answer):
    class SourceOnly(dict):
        def __getitem__(self,key):
            if key in {'expected_answer','execution_trace','raw_response','score','label'}:
                raise AssertionError('oracle feature read a stored answer or model outcome')
            return super().__getitem__(key)
    record=SourceOnly(source=source,expected_answer=100,execution_trace=['wrong'],label=1)
    expected=dict(oracle_answer_value=answer,oracle_answer_abs=abs(answer),
                  oracle_answer_negative=int(answer<0))
    assert controls.oracle_features(record)==expected
    assert controls.oracle_features({'record':record})==expected


@pytest.mark.parametrize('valid,predicted,answer,failed',[
    (1,-7,-7,0),(1,7,-7,1),(0,0,-7,1),(1,0,0,0),(1,-3,4,1),
])
def test_scored_neutral_is_exactly_reconstructible_from_permitted_information(valid,predicted,answer,failed):
    values=dict(neutral_valid=valid,neutral_prediction_value=predicted,oracle_answer_value=answer)
    assert controls.reconstruct_neutral_failure(values)==failed
    assert controls.reconstruct_neutral_failure({'features':values})==failed
    without_oracle={key:value for key,value in values.items() if key!='oracle_answer_value'}
    assert controls.reconstruct_neutral_failure(without_oracle,answer)==failed


def test_augmented_rows_preserve_every_target_label_reference_and_source_group(paired_cases):
    cases,responses=paired_cases;parents=base.pair_features(cases,responses)
    original=deepcopy(parents);augmented=controls.augment_rows(parents,cases)
    assert parents==original
    assert len(augmented)==len(parents)
    by_id={row['id']:row for row in original}
    for row in augmented:
        before=by_id[row['id']]
        assert {key:value for key,value in row.items() if key!='features'}=={
            key:value for key,value in before.items() if key!='features'}
        assert len(row['features'])==53
        assert all(row['features'][column]==value for column,value in before['features'].items())
        assert row['features']['neutral_failure']==controls.reconstruct_neutral_failure(row)
    changed=deepcopy(parents)
    for row in changed:row['label']=1-row['label'];row['target_invalid']=True
    mutations=controls.augment_rows(changed,cases)
    assert all(a['features']==b['features'] for a,b in zip(augmented,mutations))
    assert all(a['label']!=b['label'] for a,b in zip(augmented,mutations))


@pytest.mark.parametrize('change',['neutral_failure','missing_target','duplicate_target',
                                  'reference','group','source_oracle'])
def test_augmentation_rejects_wrong_parent_information_or_source_oracle(paired_cases,change):
    cases,responses=deepcopy(paired_cases);parents=base.pair_features(cases,responses)
    if change=='neutral_failure':parents[0]['features']['neutral_failure']=1-parents[0]['features']['neutral_failure']
    elif change=='missing_target':parents.pop()
    elif change=='duplicate_target':parents.append(deepcopy(parents[0]))
    elif change=='reference':parents[0]['reference_id']=parents[0]['id']
    elif change=='group':parents[0]['template_id']='unrelated-component'
    else:
        target=next(case for case in cases if case['id']==parents[0]['id'])
        tree=ast.parse(target['record']['source'])
        tree.body[0].value,tree.body[1].value=tree.body[1].value,tree.body[0].value
        target['record']['source']=ast.unparse(tree)
        # Swapping literals preserves every permitted source summary, while
        # changing the saved value queried by this target.
        assert base.source_features(target)=={key:parents[0]['features'][key] for key in base.INPUT_COLUMNS}
    with pytest.raises(ValueError):controls.augment_rows(parents,cases)


@pytest.fixture
def controlled_rows(cv_rows):
    rows=deepcopy(cv_rows)
    for row in rows:
        values=row['features'];values.update(controls.interaction_features(row))
        answer=values['neutral_prediction_value']+values['neutral_failure']
        values.update(oracle_answer_value=answer,oracle_answer_abs=abs(answer),
                      oracle_answer_negative=int(answer<0))
        values['neutral_failure']=controls.reconstruct_neutral_failure(values)
    return rows


def test_profile_keeps_oracle_columns_out_of_every_unassisted_matrix(controlled_rows):
    columns=prediction.predictor_columns(PROFILE)
    assert tuple(columns)==TIERS
    assert prediction.predictor_columns()=={
        'prior':[],'A_input':list(base.INPUT_COLUMNS),
        'A_neutral_raw':list(base.INPUT_COLUMNS+base.NEUTRAL_RAW_COLUMNS),
        'A_neutral_scored':list(base.INPUT_COLUMNS+base.NEUTRAL_RAW_COLUMNS+base.NEUTRAL_SCORED_COLUMNS)}
    assert set(columns['A_input'])<set(columns['A_interactions'])
    assert len(columns['A_interactions'])==44
    assert len(columns['A_interactions_oracle_neutral_scored'])==53
    for name,selected in columns.items():
        if '_oracle' not in name:assert not set(selected)&set(controls.ORACLE_COLUMNS)
        if not name.endswith('_scored'):assert 'neutral_failure' not in selected
    class OracleBomb(dict):
        def __getitem__(self,key):
            if key in controls.ORACLE_COLUMNS:raise AssertionError('unassisted tier accessed source oracle')
            return super().__getitem__(key)
    bomb=[{**row,'features':OracleBomb(row['features'])} for row in controlled_rows]
    for name,selected in columns.items():
        if '_oracle' not in name:assert np.isfinite(prediction._matrix(bomb,selected)).all()


@pytest.fixture
def cv_results(controlled_rows,cv_rows,cv_plan):
    plan={**cv_plan,'seeds':[17],'l2_grid':[1.]}
    original=prediction.run_grouped_cv(cv_rows,plan)
    enhanced=prediction.run_grouped_cv(controlled_rows,{**plan,**PROFILE})
    return original,enhanced,plan


def test_original_input_and_prior_reproduce_v1_and_all_eight_tiers_cover_every_target(cv_results,controlled_rows):
    original,enhanced,plan=cv_results
    assert 'feature_profile' not in original['analysis_plan']
    assert enhanced['analysis_plan']['feature_profile']=='capacity_oracle_v1'
    original_by_id={row['id']:row for row in original['oof_predictions']}
    observed=Counter((row['seed'],row['id']) for row in enhanced['oof_predictions'])
    assert observed==Counter((17,row['id']) for row in controlled_rows)
    for row in enhanced['oof_predictions']:
        assert set(row['predictions'])==set(TIERS)
        assert row['outer_fold']==original_by_id[row['id']]['outer_fold']
        assert all(row['predictions'][name]==original_by_id[row['id']]['predictions'][name]
                   for name in ('prior','A_input'))
    original_folds={fold['outer_fold']:fold for fold in original['fold_fits']}
    for fold in enhanced['fold_fits']:
        before=original_folds[fold['outer_fold']]
        assert fold['train_groups']==before['train_groups']
        assert fold['test_groups']==before['test_groups']
        for name in ('prior','A_input'):assert fold['predictors'][name]==before['predictors'][name]
    assert set(enhanced['summary']['per_seed_and_ensemble'][0]['metrics'])==set(TIERS)
    assert enhanced['summary']['mechanism_C_fitted'] is False
    assert enhanced['summary']['generated_holdouts_opened'] is False


def test_new_profile_validation_labels_cannot_change_selected_models_or_probabilities(cv_results,controlled_rows):
    _,enhanced,plan=cv_results;fold=enhanced['fold_fits'][0]
    groups=set(fold['test_groups']);changed=deepcopy(controlled_rows)
    for row in changed:
        if row['template_id'] in groups:row['label']=1-row['label']
    rerun=prediction.run_grouped_cv(changed,{**plan,**PROFILE})
    same=next(item for item in rerun['fold_fits'] if item['outer_fold']==fold['outer_fold'])
    assert same['predictors']==fold['predictors']
    before={row['id']:row['predictions'] for row in enhanced['oof_predictions'] if row['template_id'] in groups}
    after={row['id']:row['predictions'] for row in rerun['oof_predictions'] if row['template_id'] in groups}
    assert before==after


def test_unknown_profile_is_refused_before_payload_access(tmp_path,monkeypatch):
    accesses=[]
    def forbidden(path):accesses.append(path);raise AssertionError('unknown profile opened payload')
    monkeypatch.setattr(prediction,'read_jsonl',forbidden)
    with pytest.raises(ValueError,match='profile'):prediction.load_features({'feature_profile':'unknown'})
    with pytest.raises(ValueError,match='profile'):prediction.predictor_columns({'feature_profile':'unknown'})
    assert not accesses


@pytest.fixture
def parent_artifacts(tmp_path,paired_cases,monkeypatch):
    cases,responses=paired_cases;rows=base.pair_features(cases,responses)
    table=tmp_path/'parent_features.jsonl'
    table.write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows))
    provenance=dict(source_config_sha256='source-config-pin',source_dataset_sha256='source-dataset',
        source_identity_hash='source-identity',source_model='software-fixture',
        source_model_revision='fixture-revision',source_prepared_sha256='source-prepared',
        source_audit_sha256='source-audit',original_source_sha256='source-software',
        source_responses_sha256='model-responses-never-opened')
    manifest=dict(status='passed',evaluation_role=base.ROLE,sha256=sha(table),n=len(rows),groups=2,
        columns=dict(input=list(base.INPUT_COLUMNS),neutral_raw=list(base.NEUTRAL_RAW_COLUMNS),
                     neutral_scored=list(base.NEUTRAL_SCORED_COLUMNS)),
        source_config=str(tmp_path/'source_config.json'),**provenance)
    manifest_path=tmp_path/'parent_features.manifest.json'
    parent=dict(feature_table=str(table),feature_manifest=str(manifest_path),
        feature_manifest_sha256='',feature_table_sha256=sha(table),
        model=provenance['source_model'],model_revision=provenance['source_model_revision'])
    parent_path=tmp_path/'parent_config.json'
    def save(update_manifest_pin=True):
        manifest_path.write_text(json.dumps(manifest))
        if update_manifest_pin:parent['feature_manifest_sha256']=sha(manifest_path)
        parent_path.write_text(json.dumps(parent))
        return dict(parent_config=str(parent_path),parent_config_sha256=sha(parent_path),
            model=parent['model'],model_revision=parent['model_revision'],
            feature_table=str(tmp_path/'controls.jsonl'),feature_manifest=str(tmp_path/'controls.manifest.json'))
    def permitted_source(config):
        assert config['source_config']==manifest['source_config']
        return {},{'identity_hash':'source-identity'},cases,dict(provenance)
    monkeypatch.setattr(base,'_source_inputs',permitted_source)
    from codecue.binding import registry
    monkeypatch.setattr(registry,'code_identity',lambda:{'source_sha256':'software-controls'})
    return dict(rows=rows,manifest=manifest,parent=parent,save=save,table=table,
                manifest_path=manifest_path,cases=cases)


def test_collect_uses_only_pinned_parent_features_and_source_and_is_immutable(parent_artifacts,monkeypatch):
    fixture=parent_artifacts;config=fixture['save']()
    from codecue.binding import checkpoint_suite
    def outcome_reader(*args,**kwargs):raise AssertionError('controls opened language-model outcomes')
    monkeypatch.setattr(checkpoint_suite,'audit',outcome_reader)
    before=fixture['table'].read_bytes(),fixture['manifest_path'].read_bytes()
    result=controls.collect(config)
    assert result['evaluation_role']==controls.ROLE and result['n']==len(fixture['rows'])
    assert result['neutral_failure_reconstruction_exact'] is True
    assert result['additional_query_cost']['new_language_model_queries']==0
    assert result['additional_query_cost']['new_response_payload_reads']==0
    observed=[json.loads(line) for line in Path(config['feature_table']).read_text().splitlines()]
    assert len(observed[0]['features'])==53
    assert fixture['table'].read_bytes()==before[0] and fixture['manifest_path'].read_bytes()==before[1]
    original=Path(config['feature_table']).read_bytes(),Path(config['feature_manifest']).read_bytes()
    assert controls.collect(config)==result
    assert (Path(config['feature_table']).read_bytes(),Path(config['feature_manifest']).read_bytes())==original


@pytest.mark.parametrize('change',['parent_pin','manifest_pin','role','source_pin','checkpoint',
                                  'declared_role','reserved_path','payload_hash'])
def test_incompatible_parent_metadata_is_rejected_before_feature_payload(parent_artifacts,monkeypatch,change):
    fixture=parent_artifacts
    if change=='manifest_pin':fixture['parent']['feature_manifest_sha256']='0'*64
    elif change=='role':fixture['manifest']['evaluation_role']='final'
    elif change=='source_pin':fixture['manifest']['source_dataset_sha256']='wrong-source'
    elif change=='reserved_path':fixture['parent']['feature_table']=str(fixture['table'].parent/'final_responses.jsonl')
    elif change=='payload_hash':fixture['manifest']['sha256']='0'*64
    config=fixture['save'](update_manifest_pin=change!='manifest_pin')
    if change=='parent_pin':config['parent_config_sha256']='0'*64
    elif change=='checkpoint':config['model_revision']='wrong-checkpoint'
    elif change=='declared_role':config['evaluation_role']='structural_extrapolation'
    opened=[]
    def forbidden(path):opened.append(path);raise AssertionError('bad metadata reached parent payload')
    monkeypatch.setattr(prediction,'read_jsonl',forbidden)
    with pytest.raises(ValueError):controls.collect(config)
    assert not opened
