"""Leakage and access checks use small synthetic discovery records only."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import discovery_features as features
from codecue.binding import discovery_prediction as prediction
from codecue.binding.competition import names_for,ROLE as COMPETITION_ROLE
from codecue.binding.datasets import digest
from codecue.binding.interpreter import execute
from codecue.binding.programs import rename


@pytest.fixture
def paired_cases():
    cases=[];responses=[]
    for index in range(2):
        for lexical in (0,1):
            canonical=f'v0 = {index+2}\nv1 = {index+7}\nbuffer = 0\nsaved = v0\nv0 = {index+11}\nsaved'
            base=dict(base_id=f'base:{index}',template_id=f'template:{index}',
                split='train' if index==0 else 'development',family='versions',
                evaluation_role=COMPETITION_ROLE,
                available_bindings=2,updates=1,tail_placement='after',query_role='saved',
                ownership_swapped=False,canonical_source=canonical,lexical_realization=lexical)
            for condition in ('informative','neutral','misleading'):
                row={**base,'condition':condition}
                source=rename(canonical,names_for(row,condition,lexical))
                truth=execute(source)
                row.update(id=f'case:{index}:{lexical}:{condition}',source=source,
                    expected_answer=truth['expected_answer'],execution_trace=truth['execution_trace'])
                prompt='Synthetic fixture prompt:\n'+source
                case=dict(id=row['id'],kind='competition',variant='print_direct_v3',
                    task='print_direct_v3',section='binding_competition',record=row,
                    prompt=prompt,prompt_sha256=digest(prompt),input_token_ids=list(source.encode()))
                correct=(index+lexical+(condition=='misleading'))%2==0
                answer=truth['expected_answer']+(0 if correct else 1)
                response=dict(id=row['id'],raw_response=str(answer),output_token_ids=[answer+100],
                    score=dict(correct=correct,valid=True,prediction=answer))
                cases.append(case);responses.append(response)
    return cases,responses


class NoOracleFields(dict):
    def __getitem__(self,key):
        if key in {'expected_answer','execution_trace','error_alternatives'}:
            raise AssertionError('source feature collector touched an oracle field')
        return super().__getitem__(key)

    def get(self,key,default=None):
        return self[key] if key in self else default


def test_source_features_use_source_and_declared_design_without_oracle_access(paired_cases):
    case=deepcopy(paired_cases[0][0]);expected=features.source_features(case)
    case['record']=NoOracleFields(case['record'])
    assert features.source_features(case)==expected
    assert set(expected)==set(features.INPUT_COLUMNS)
    assert all(np.isfinite(value) for value in expected.values())
    assert expected['query_last_definition_distance']==1
    assert expected['query_dependency_depth']==2
    assert expected['negative_literals']==0


def test_target_outcome_changes_labels_but_never_prediction_features(paired_cases):
    cases,responses=paired_cases
    original=features.pair_features(cases,responses)
    changed=deepcopy(responses)
    for response,case in zip(changed,cases):
        if case['record']['condition']!='neutral':
            response.update(raw_response='malformed target text',output_token_ids=[901,902])
            response['score']=dict(correct=False,valid=False,prediction=None)
    mutated=features.pair_features(cases,changed)
    before={row['id']:row for row in original};after={row['id']:row for row in mutated}
    assert set(before)==set(after)
    assert any(before[key]['label']!=after[key]['label'] for key in before)
    assert all(before[key]['features']==after[key]['features'] for key in before)
    assert all(before[key]['reference_id']==after[key]['reference_id'] for key in before)
    assert all(after[key]['target_invalid'] for key in after)
    assert all('target_invalid' not in row['features'] for row in mutated)


def test_neutral_join_preserves_lexical_and_structural_identity(paired_cases):
    cases,responses=paired_cases;rows=features.pair_features(cases,responses)
    case_by_id={case['id']:case for case in cases}
    assert len(rows)==8
    assert Counter(row['condition'] for row in rows)=={'informative':4,'misleading':4}
    for row in rows:
        target=case_by_id[row['id']];reference=case_by_id[row['reference_id']]
        assert target['id']!=reference['id']
        assert target['prompt_sha256']!=reference['prompt_sha256']
        for key in ('base_id','template_id','split','updates','tail_placement','query_role',
                    'ownership_swapped','lexical_realization','canonical_source','expected_answer'):
            assert target['record'][key]==reference['record'][key]
        assert reference['record']['condition']=='neutral'
    assert len({row['reference_id'] for row in rows})==4


@pytest.mark.parametrize('change',['missing_neutral','multiple_neutral','same_id','same_prompt',
                                  'different_template','different_split','different_answer','different_source'])
def test_pairing_refuses_incomplete_self_or_incompatible_neutral_references(paired_cases,change):
    cases,responses=deepcopy(paired_cases)
    neutral=next(case for case in cases if case['record']['condition']=='neutral')
    target=next(case for case in cases if case['record']['condition']=='informative')
    if change=='missing_neutral':
        cases.remove(neutral)
        responses=[row for row in responses if row['id']!=neutral['id']]
    elif change=='multiple_neutral':
        duplicate=deepcopy(neutral);duplicate['id']='duplicate-neutral';duplicate['record']['id']=duplicate['id']
        cases.append(duplicate);responses.append(dict(responses[1],id=duplicate['id']))
    elif change=='same_id':
        original=target['id'];target['id']=neutral['id'];target['record']['id']=neutral['id']
        next(row for row in responses if row['id']==original)['id']=neutral['id']
    elif change=='same_prompt':target['prompt_sha256']=neutral['prompt_sha256']
    elif change=='different_template':target['record']['template_id']='wrong-template'
    elif change=='different_split':target['record']['split']='development'
    elif change=='different_answer':target['record']['expected_answer']+=1
    else:target['record']['canonical_source']+='\n# changed fixture source'
    with pytest.raises(ValueError):features.pair_features(cases,responses)


def _write_jsonl(path,rows):
    path.write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows))
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def source_metadata(tmp_path):
    dataset=tmp_path/'source.jsonl';dataset_hash=_write_jsonl(dataset,[{'id':'source-fixture'}])
    source=dict(dataset=str(dataset),run_dir=str(tmp_path/'run'),model='fixture-model',
        model_revision='fixture-revision',tokenizer_revision='fixture-tokenizer',
        sections=[dict(name='binding_competition',kind='competition',dataset=str(dataset),
                       sha256=dataset_hash,variants=['print_direct_v3'])])
    data_manifest=dict(status='validated',evaluation_role=COMPETITION_ROLE,sha256=dataset_hash,
                       rows=1,structural_components=1)
    identity=dict(config=deepcopy(source),model_revision=source['model_revision'],
                  tokenizer_revision=source['tokenizer_revision'],dataset_manifest=data_manifest,
                  code=dict(source_sha256='fixture-source'))
    stage=Path(source['run_dir'])/'checkpoint_suite';stage.mkdir(parents=True)
    manifest=dict(status='complete',identity=identity,identity_hash=digest(identity),responses_sha256='fixture')
    audit=dict(status='passed',complete=True,identity_hash=manifest['identity_hash'],
               model=source['model'],revision=source['model_revision'])
    path=tmp_path/'source_config.json'
    def save():
        path.write_text(json.dumps(source))
        dataset.with_suffix('.manifest.json').write_text(json.dumps(data_manifest))
        (stage/'manifest.json').write_text(json.dumps(manifest))
        (stage/'audit.json').write_text(json.dumps(audit))
        return dict(source_config=str(path),source_config_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    feature_table=str(tmp_path/'features.jsonl'))
    return dict(source=source,data_manifest=data_manifest,identity=identity,manifest=manifest,
                audit=audit,stage=stage,dataset=dataset,path=path,save=save)


@pytest.mark.parametrize('change',['config_hash','config_role','source_role','source_hash',
                                  'behavior_status','behavior_hash','behavior_config',
                                  'behavior_checkpoint','audit_status','reserved_response_path'])
def test_collector_refuses_reserved_or_mismatched_metadata_before_outcomes(source_metadata,monkeypatch,change):
    fixture=source_metadata
    if change=='config_role':fixture['source']['evaluation_role']='structural_extrapolation'
    elif change=='source_role':fixture['data_manifest']['evaluation_role']='final'
    elif change=='source_hash':fixture['data_manifest']['sha256']='0'*64
    elif change=='behavior_status':fixture['manifest']['status']='started'
    elif change=='behavior_hash':fixture['manifest']['identity_hash']='0'*64
    elif change=='behavior_config':fixture['identity']['config']['model']='wrong-checkpoint'
    elif change=='behavior_checkpoint':fixture['identity']['model_revision']='wrong-checkpoint'
    elif change=='audit_status':fixture['audit']['status']='failed'
    elif change=='reserved_response_path':fixture['source']['run_dir']=str(fixture['path'].parent/'final')
    config=fixture['save']()
    if change=='config_hash':config['source_config_sha256']='0'*64
    accesses=[]
    def forbidden(path):
        accesses.append(str(path))
        raise AssertionError('invalid source metadata reached a data/outcome reader')
    from codecue.binding import checkpoint_suite
    monkeypatch.setattr(features,'read_jsonl',forbidden)
    monkeypatch.setattr(checkpoint_suite,'audit',forbidden)
    with pytest.raises(ValueError):features.collect(config)
    assert not accesses


@pytest.fixture
def cv_rows():
    rows=[]
    for available in (2,4):
        for index in range(12):
            group=f'load:{available}:template:{index:02}'
            for lexical in (0,1):
                for condition in ('informative','misleading'):
                    columns={column:0. for column in features.INPUT_COLUMNS}
                    columns.update(prompt_tokens=70+3*index+available,source_chars=120+7*index,
                        statements=9,variables=available+2,assignments=8,copies=3,
                        literal_assignments=5,negative_literals=index%3,max_abs_literal=16,
                        mean_abs_literal=7.5,query_last_definition_distance=lexical+1,
                        query_definition_count=2,query_dependency_depth=3,
                        available_bindings=available,updates=1 if index%2 else 3,
                        tail_after=index%2,query_saved=lexical,
                        misleading=int(condition=='misleading'),lexical_one=lexical)
                    valid=index%5!=0;value=index-6 if valid else 0
                    columns.update(neutral_valid=int(valid),neutral_output_tokens=3,
                        neutral_response_chars=2,neutral_prediction_value=value,
                        neutral_prediction_abs=abs(value),neutral_failure=int((index+lexical)%3==0))
                    label=int((index+lexical+int(condition=='misleading'))%4==0)
                    rows.append(dict(id=f'{group}:{lexical}:{condition}',
                        reference_id=f'{group}:{lexical}:neutral',template_id=group,
                        base_id=f'{group}:base',original_split='train' if index<9 else 'development',
                        condition=condition,query_role='saved' if lexical else 'current',
                        available_bindings=available,lexical_realization=lexical,
                        features=columns,label=label,target_invalid=False))
    return rows


@pytest.fixture
def cv_plan():
    return dict(seeds=[17,23],outer_folds=3,inner_folds=2,l2_grid=[.1,1.],
                bootstrap_replicates=64,bootstrap_seed=29)


def test_fold_assignment_balances_templates_and_ignores_outcome_labels(cv_rows):
    assignment=prediction.assign_folds(cv_rows,n_folds=3,seed=17)
    metadata=[{key:row[key] for key in ('template_id','available_bindings')} for row in cv_rows]
    assert assignment==prediction.assign_folds(metadata,n_folds=3,seed=17)
    changed=deepcopy(cv_rows)
    for row in changed:
        row['label']=1-row['label'];row['target_invalid']=True
    assert assignment==prediction.assign_folds(list(reversed(changed)),n_folds=3,seed=17)
    assert len(assignment)==24
    for fold in range(3):
        for available in (2,4):
            groups={row['template_id'] for row in cv_rows if row['available_bindings']==available
                    and assignment[row['template_id']]==fold}
            assert len(groups)==4
    assert prediction.assign_folds(cv_rows,n_folds=3,seed=23)!=assignment
    with pytest.raises(ValueError):prediction.assign_folds(cv_rows,n_folds=5,seed=17)


def test_nested_cv_covers_every_seed_and_keeps_all_relatives_inside_folds(cv_rows,cv_plan):
    result=prediction.run_grouped_cv(cv_rows,cv_plan)
    assert result==prediction.run_grouped_cv(list(reversed(cv_rows)),cv_plan)
    columns=result['analysis_plan']['predictors']
    assert set(columns)=={'prior','A_input','A_neutral_raw','A_neutral_scored'}
    assert set(columns['A_input'])<set(columns['A_neutral_raw'])<set(columns['A_neutral_scored'])
    assert 'neutral_failure' not in columns['A_input']+columns['A_neutral_raw']
    assert set(columns['A_neutral_scored'])-set(columns['A_neutral_raw'])=={'neutral_failure'}
    assert set(columns['A_neutral_scored'])==set(cv_rows[0]['features'])
    assert not any(name in set(columns['A_neutral_scored']) for name in ('label','target_invalid','correct','expected_answer'))
    counts=Counter((row['seed'],row['id']) for row in result['oof_predictions'])
    assert set(counts)=={(seed,row['id']) for seed in cv_plan['seeds'] for row in cv_rows}
    assert set(counts.values())=={1}
    assignments=defaultdict(set)
    for row in result['oof_predictions']:
        assignments[row['seed'],row['template_id']].add(row['outer_fold'])
        assert all(0<value<1 for value in row['predictions'].values())
    assert all(len(folds)==1 for folds in assignments.values())
    for fold in result['fold_fits']:
        train=set(fold['train_groups']);test=set(fold['test_groups'])
        assert train.isdisjoint(test) and len(train|test)==24
        assert set(fold['inner_assignments'])==train
        for predictor in fold['predictors'].values():
            for curve in predictor['inner_curves']:
                for inner in curve['inner_fits']:
                    assert set(inner['train_groups']).isdisjoint(inner['validation_groups'])
                    assert set(inner['train_groups'])|set(inner['validation_groups'])==train
                    if inner['model']['kind']=='logistic':
                        matrix=np.array([[row['features'][column] for column in predictor['columns']]
                            for row in cv_rows if row['template_id'] in set(inner['train_groups'])])
                        assert np.allclose(inner['model']['mean'],matrix.mean(axis=0))
                        assert np.allclose(inner['model']['scale'],matrix.std(axis=0).clip(1e-8))
    assert result['summary']['n']==len(cv_rows)
    assert result['summary']['templates']==24
    assert result['summary']['mechanism_C_fitted'] is False
    assert result['summary']['generated_holdouts_opened'] is False


def test_held_out_labels_cannot_change_its_predictions_or_selected_model(cv_rows,cv_plan):
    plan={**cv_plan,'seeds':[17]}
    original=prediction.run_grouped_cv(cv_rows,plan)
    fold=original['fold_fits'][0];test_groups=set(fold['test_groups'])
    changed=deepcopy(cv_rows)
    for row in changed:
        if row['template_id'] in test_groups:row['label']=1-row['label']
    mutated=prediction.run_grouped_cv(changed,plan)
    corresponding=next(row for row in mutated['fold_fits']
                       if row['seed']==fold['seed'] and row['outer_fold']==fold['outer_fold'])
    assert fold['predictors']==corresponding['predictors']
    before={row['id']:row['predictions'] for row in original['oof_predictions']
            if row['template_id'] in test_groups}
    after={row['id']:row['predictions'] for row in mutated['oof_predictions']
           if row['template_id'] in test_groups}
    assert before==after
    model=fold['predictors']['A_input']['model']
    columns=fold['predictors']['A_input']['columns']
    training=np.array([[row['features'][column] for column in columns] for row in cv_rows
                       if row['template_id'] in set(fold['train_groups'])])
    assert np.allclose(model['mean'],training.mean(axis=0))
    assert np.allclose(model['scale'],training.std(axis=0).clip(1e-8))


@pytest.mark.parametrize('label',[0,1])
def test_single_class_training_keeps_every_target_with_documented_prior_fallback(cv_rows,cv_plan,label):
    rows=deepcopy(cv_rows)
    for row in rows:row['label']=label
    result=prediction.run_grouped_cv(rows,{**cv_plan,'seeds':[17]})
    assert len(result['oof_predictions'])==len(rows)
    assert all(fold['fallbacks'] for fold in result['fold_fits'])
    for fold in result['fold_fits']:
        for name,predictor in fold['predictors'].items():
            model=predictor['model']
            assert model['kind']=='jeffreys_prior'
            assert 0<model['probability']<1
            assert (model['probability']>.5)==bool(label)
            assert predictor['outer_single_class_fallback']==(name!='prior')


def test_paired_score_uncertainty_samples_templates_not_individual_rows():
    # Within either template every error difference is identical. Resampling
    # whole templates permits +/-1; row resampling would falsely narrow this CI.
    labels=[0]*40;left=[1]*20+[0]*20;right=[0]*20+[1]*20
    interval=prediction.group_bootstrap_improvement(labels,left,right,['a']*20+['b']*20,
                                                    draws=2000,seed=19)
    assert interval['templates']==2 and interval['n']==40
    assert interval['brier_score']['mean']==0
    assert interval['brier_score']['exploratory_template_bootstrap_95']==[-1.,1.]
    assert interval['resampling_unit']=='template_id'
    assert interval['conditional_on_saved_oof_probabilities'] is True
    assert interval['refits_per_bootstrap_draw']==0


@pytest.fixture
def feature_artifacts(tmp_path,cv_rows):
    table=tmp_path/'features.jsonl';checksum=_write_jsonl(table,cv_rows)
    manifest=dict(status='passed',evaluation_role=features.ROLE,sha256=checksum,
        n=len(cv_rows),groups=24,columns=dict(input=list(features.INPUT_COLUMNS),
            neutral_raw=list(features.NEUTRAL_RAW_COLUMNS),neutral_scored=list(features.NEUTRAL_SCORED_COLUMNS)),
        source_model='software-fixture',source_model_revision='fixture-revision',
        source_dataset_sha256='fixture-source')
    path=tmp_path/'features.manifest.json'
    path.write_text(json.dumps(manifest))
    config=dict(feature_table=str(table),feature_manifest=str(path),
                feature_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return config,manifest,path


def test_valid_feature_contract_loads_exact_registered_rows(feature_artifacts,cv_rows):
    config,manifest,_=feature_artifacts
    loaded,rows=prediction.load_features(config)
    assert loaded==manifest
    assert rows==sorted(cv_rows,key=lambda row:row['id'])


@pytest.mark.parametrize('change',['manifest_role','manifest_status','column_contract','payload_hash',
                                  'manifest_hash','missing_manifest_hash','checkpoint','declared_role','reserved_path'])
def test_feature_metadata_is_refused_before_payload_read(feature_artifacts,monkeypatch,change):
    config,manifest,path=feature_artifacts
    if change=='manifest_role':manifest['evaluation_role']='final'
    elif change=='manifest_status':manifest['status']='started'
    elif change=='column_contract':manifest['columns']['input'].append('target_invalid')
    elif change=='payload_hash':manifest['sha256']='0'*64
    elif change=='manifest_hash':config['feature_manifest_sha256']='0'*64
    elif change=='missing_manifest_hash':config.pop('feature_manifest_sha256')
    elif change=='checkpoint':config['model_revision']='wrong-revision'
    elif change=='declared_role':config['evaluation_role']='structural_extrapolation'
    else:config['feature_table']=str(path.parent/'test_responses.jsonl')
    path.write_text(json.dumps(manifest))
    if change not in ('manifest_hash','missing_manifest_hash'):
        config['feature_manifest_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    opened=[]
    def forbidden(path):
        opened.append(str(path));raise AssertionError('invalid declaration opened prediction features')
    monkeypatch.setattr(prediction,'read_jsonl',forbidden)
    with pytest.raises(ValueError):prediction.load_features(config)
    assert not opened


def test_failed_analysis_remains_visible_without_masking_the_original_error(feature_artifacts,tmp_path,monkeypatch):
    config,_,_=feature_artifacts
    config.update(output_dir=str(tmp_path/'failing_fit'),report=str(tmp_path/'failed.md'),
                  review_artifact=str(tmp_path/'failure_review.json'))
    from codecue.binding import registry
    monkeypatch.setattr(registry,'code_identity',lambda:{'source_sha256':'software-fixture'})
    def failure(rows,config):
        raise ValueError('synthetic nonconvergence; no observed groups may be dropped')
    monkeypatch.setattr(prediction,'run_grouped_cv',failure)
    with pytest.raises(ValueError,match='synthetic nonconvergence'):
        prediction.run(config)
    directory=Path(config['output_dir'])
    registration=json.loads((directory/'registration.json').read_text())
    failed=json.loads((directory/'summary.json').read_text())
    assert registration['status']=='started'
    assert failed['status']=='failed' and 'synthetic nonconvergence' in failed['error']
    assert failed['generated_holdouts_opened'] is False
    assert not Path(config['review_artifact']).exists()


def test_completed_analysis_reuses_and_protects_its_oof_artifacts(feature_artifacts,cv_plan,tmp_path,monkeypatch):
    config,_,_=feature_artifacts
    config.update(cv_plan,seeds=[17],l2_grid=[1.],output_dir=str(tmp_path/'fits'),
                  report=str(tmp_path/'report.md'),review_artifact=str(tmp_path/'review.json'))
    from codecue.binding import registry
    monkeypatch.setattr(registry,'code_identity',lambda:{'source_sha256':'software-fixture'})
    first=prediction.run(config)
    artifacts={path:path.read_bytes() for path in (tmp_path/'fits').iterdir() if path.is_file()}
    review=Path(config['review_artifact']).read_bytes()
    assert first['status']=='complete_exploratory' and first['n']==96
    assert prediction.run(config)['status']=='complete_reused'
    assert all(path.read_bytes()==value for path,value in artifacts.items())
    assert Path(config['review_artifact']).read_bytes()==review
    oof=Path(config['output_dir'])/'oof_predictions.jsonl'
    oof.write_text(oof.read_text()+'\n')
    with pytest.raises(ValueError,match='artifact changed'):prediction.run(config)
