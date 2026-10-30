from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import direct_identity_readouts as study
from codecue.binding import schedule_readouts as original
from codecue.binding import direct_identity_targets as target


def bundle_fixture(n=18,site=7):
    y=np.zeros((n,192));mask=np.full_like(y,site in (7,8),dtype=bool)
    owners={'assignment':[0,0,1,0],'parent':[1,2,0,3]}
    versions={'assignment':[2,3,2,4],'parent':[1,1,3,1]}
    for head in target.HEADS:
        kind,component=head['family'].rsplit('_',1);event=head['event_index']
        owner,version=owners[kind][event],versions[kind][event]
        value=target.encode_joint(owner,version) if component=='joint' else owner if component=='owner' else version
        if site in (7,8):y[:,head['indices'][head['candidates'].index(value)]]=1
    description=dict(control=False,profile_ids=['3_1_0_0']*n,
        syntax_owners=[deepcopy(owners) for _ in range(n)],
        event_capture_status=[dict(assignment=['obsolete','obsolete','current','current'],
                                  parent=['obsolete','current','obsolete','current']) for _ in range(n)],
        event_truth_statements=[dict(assignment=[4,5,6,7],parent=[1,2,5,3]) for _ in range(n)],
        canonical_visible_prefixes=['source']*n,canonical_output_visible_prefixes=['source']*n)
    return target.TargetBundle(y,mask,target.COLUMNS,tuple(f'case{i}' for i in range(n)),
        tuple(f'g{i//3}' for i in range(n)),tuple('train' if i<12 else 'development' for i in range(n)),site,description)


def scores_for(bundle):
    scores=np.full(bundle.y.shape,np.nan);active=bundle.mask.any(axis=0);scores[:,active]=bundle.y[:,active]
    return scores


def change_prediction(scores,family,event,candidate):
    head=next(h for h in target.HEADS if h['family']==family and h['event_statement']==event)
    scores[:,head['indices']]=0;scores[:,head['indices'][head['candidates'].index(candidate)]]=1


def config(tmp_path):
    return dict(evaluation_role=study.ROLE,capture_config=str(tmp_path/'capture.json'),
        capture_config_sha256='b'*64,declared_plan=str(tmp_path/'plan.md'),declared_plan_sha256='c'*64,
        primary_layer=24,run_dir=str(tmp_path/'run'),report=str(tmp_path/'report.md'))


def test_fixed_active_grid_is_isolated_from_original_and_keeps_capture_axis_ids():
    assert study.SITES==(7,8) and study._CORE.CAPTURE_SITE_IDS==(3,7,8)
    assert study._CORE.FIXED_GRID_BANKS==30
    assert original.SITES==(3,7,8) and original.FIXED_GRID_BANKS==45
    assert original._additional_predictions(None,None,None)=={}
    assert study.protocol()['target_columns']==192 and study.protocol()['categorical_heads']==24
    assert study.protocol()['primary_layer']==24 and study.protocol()['primary_site']==7


def test_joint_and_factorized_eight_predictions_agree_when_all_heads_correct():
    bundle=bundle_fixture();result=study.binding_comparisons(bundle,scores_for(bundle))
    assert result['combined_eight']['joint']['accuracy']==1
    assert result['combined_eight']['factorized']['accuracy']==1
    assert result['capacity']['direct_joint_outputs_per_event']==16
    assert result['capacity']['separate_owner_plus_version_outputs_per_event']==8
    assert result['capacity']['whole_pipelines_parameter_matched'] is False


def test_coherent_linear_ridge_component_scores_are_joint_marginal_sums():
    rng=np.random.default_rng(37);bundle=bundle_fixture();y=np.zeros_like(bundle.y)
    for kind in ('assignment','parent'):
        for event in range(4,8):
            joint=rng.integers(0,16,len(y))
            for component,values in (('joint',joint),('owner',joint//4),('version',joint%4+1)):
                head=next(h for h in target.HEADS if h['family']==kind+'_'+component and h['event_statement']==event)
                for row,value in enumerate(values):y[row,head['indices'][head['candidates'].index(int(value))]]=1
    train=np.arange(18)<12;features=rng.normal(size=(18,7));weights=np.linspace(.5,1.5,12)
    models,scores,_=study._CORE.fit_masked_columns(features,y,bundle.mask,y,train,weights,bundle.case_ids)
    assert len(models)==1
    for kind in ('assignment','parent'):
        for event in range(4,8):
            heads={component:next(h for h in target.HEADS if h['family']==kind+'_'+component and h['event_statement']==event)
                   for component in ('joint','owner','version')}
            joint=scores[:,heads['joint']['indices']].reshape(18,4,4)
            np.testing.assert_allclose(scores[:,heads['owner']['indices']],joint.sum(axis=2),atol=2e-13,rtol=2e-13)
            np.testing.assert_allclose(scores[:,heads['version']['indices']],joint.sum(axis=1),atol=2e-13,rtol=2e-13)
    comparisons=study.binding_comparisons(replace(bundle,y=y),scores)
    for event in comparisons['per_event'].values():
        relation=event['score_marginal_linearity']
        assert relation['n_complete']==18
        assert relation['max_abs_owner_difference']<2e-13
        assert relation['max_abs_version_difference']<2e-13


def test_joint_vs_factorized_are_distinct_predictions_without_source_oracle_conversion():
    bundle=bundle_fixture();scores=scores_for(bundle)
    change_prediction(scores,'assignment_owner',4,1)
    result=study.binding_comparisons(bundle,scores)
    assert result['per_event']['assignment/event4']['joint']['accuracy']==1
    assert result['per_event']['assignment/event4']['factorized']['accuracy']==0
    assert result['whole_by_kind']['assignment']['joint']['accuracy']==1
    assert result['combined_eight']['factorized']['accuracy']==0
    scores=scores_for(bundle);change_prediction(scores,'assignment_joint',4,target.encode_joint(1,2))
    result=study.binding_comparisons(bundle,scores)
    event=result['per_event']['assignment/event4']
    assert event['joint']['accuracy']==0 and event['factorized']['accuracy']==1
    assert event['joint_owner']['accuracy']==0 and event['joint_version']['accuracy']==1


def test_missing_predictions_remain_errors_with_full_denominators():
    bundle=bundle_fixture();scores=scores_for(bundle)
    for family in ('assignment_joint','assignment_owner','assignment_version'):
        head=next(h for h in target.HEADS if h['family']==family and h['event_statement']==7)
        scores[:,head['indices']]=np.nan
    result=study.binding_comparisons(bundle,scores)['per_event']['assignment/event7']
    for method in ('joint','factorized','separate_owner','separate_version','joint_owner','joint_version'):
        assert result[method]['n']==18 and result[method]['accuracy']==0


def test_class_profile_and_underlying_capture_status_counts_are_retained():
    bundle=bundle_fixture();result=study.binding_comparisons(bundle,scores_for(bundle))
    event=result['per_event']['parent/event4']
    assert set(event['joint_classes'])==set(map(str,range(16)))
    assert sum(v['n'] for v in event['joint_classes'].values())==18
    assert event['by_capture_status']['obsolete']['joint']['n']==18
    assert event['by_profile']['3_1_0_0']['joint']['n']==18
    assert len(event['joint']['per_group'])==6
    assert 'random sham identity' in result['capture_status_scope']


def test_initialization_is_all_undefined_and_has_no_successful_joint_recovery():
    bundle=bundle_fixture(site=3);result=study.binding_comparisons(bundle,scores_for(bundle))
    assert result['combined_eight']['joint']['n']==0
    assert result['combined_eight']['joint']['accuracy'] is None


def test_initialization_source_preflight_rejects_any_defined_future_event(monkeypatch):
    initial=bundle_fixture(site=3)
    monkeypatch.setattr(study,'_targets',lambda:SimpleNamespace(targets=lambda rows,site:initial))
    study._initialization([{}]*18)
    initial.mask[0,0]=True
    with pytest.raises(ValueError,match='all192event targets undefined'):
        study._initialization([{}]*18)
    initial.mask[0,0]=False;initial.y[0,0]=1
    with pytest.raises(ValueError,match='all192event targets undefined'):
        study._initialization([{}]*18)


def test_joint_and_component_truth_must_be_coherent():
    bundle=bundle_fixture();head=next(h for h in target.HEADS if h['family']=='assignment_version' and h['event_statement']==4)
    bundle.y[:,head['indices']]=0;bundle.y[:,head['indices'][0]]=1
    with pytest.raises(ValueError,match='target identities disagree'):
        study.binding_comparisons(bundle,scores_for(bundle))


def test_additional_baseline_uses_only_train_version_labels_and_syntax_owners():
    bundle=bundle_fixture();train=np.arange(18)<12;weights=np.linspace(.5,2,12)
    before=study._CORE._additional_predictions(bundle,train,weights)['source_owner_version_prior']
    changed=bundle.y.copy();changed[~train]=np.nan
    poisoned=replace(bundle,y=changed)
    after=study._CORE._additional_predictions(poisoned,train,weights)['source_owner_version_prior']
    assert np.array_equal(before,after,equal_nan=True)
    assert np.isfinite(before).all()
    comparisons=study.binding_comparisons(bundle,before)
    assert comparisons['combined_eight']['joint']==comparisons['combined_eight']['factorized']
    for event in comparisons['per_event'].values():
        assert event['prediction_disagreement']['correct']==0
        assert event['score_marginal_linearity']['max_abs_owner_difference']<1e-15
        assert event['score_marginal_linearity']['max_abs_version_difference']<1e-15


def test_central_scorer_reuses_support_and_preserves_three_old_methods(monkeypatch):
    bundle=bundle_fixture();train=np.arange(18)<12;dev=np.flatnonzero(~train);weights=np.ones(12)
    scores=scores_for(bundle);eligibility=study._CORE._train_support(bundle,train)
    support=study._CORE._train_support(bundle,train)
    first=study._CORE._score_methods(bundle,bundle,train,weights,dev,scores,scores,
                                    eligibility=eligibility,control_support=support)
    monkeypatch.setattr(study._CORE,'_train_support',lambda *args:pytest.fail('precomputed support must be reused'))
    second=study._CORE._score_methods(bundle,bundle,train,weights,dev,scores,scores,
                                     eligibility=eligibility,control_support=support)
    assert first==second and set(first)==set(study.METHODS)
    assert first['source_owner_version_prior']['whole_categorical_families']['assignment_owner']['accuracy']==1


def test_new_role_and_primary_layer_are_guarded(tmp_path):
    cfg=config(tmp_path);assert study._config(cfg)==cfg
    with pytest.raises(ValueError):study._config({**cfg,'evaluation_role':original.ROLE})
    with pytest.raises(ValueError,match='layer24'):study._config({**cfg,'primary_layer':16})


def test_tiny_active_pipeline_routes_sites_to_capture_axes_and_replays_without_refits(tmp_path,monkeypatch):
    rng=np.random.default_rng(15);bundle=bundle_fixture();n=18
    cfg=config(tmp_path);source={'synthetic_fixture_only':True}
    checked=dict(layers=[8,16,24,31],feature_shape=[n,3,4,7],
        cases=[dict(visible_prefixes=[f'WRONG-{i}',f'body-{i}',f'query-{i}']) for i in range(n)],
        source={'snapshot_id':study.SOURCE_SNAPSHOT,'source_sha256':study.SOURCE_SHA},
        dataset_sha256='d'*64,model='synthetic-fixture')
    records=[dict(id=bundle.case_ids[i],split=bundle.splits[i],template_id=bundle.group_ids[i]) for i in range(n)]
    vectors=rng.normal(size=checked['feature_shape']).astype('float32');vectors[:,0]+=1000;vectors[:,1]+=10;vectors[:,2]+=20
    monkeypatch.setattr(study._CORE,'_metadata',lambda *a,**k:(source,checked,records))
    bundles={site:replace(bundle,site=site) for site in study.SITES}
    controls={(site,seed):bundles[site] for site in study.SITES for seed in (17,29,43)}
    monkeypatch.setattr(study._CORE,'_bundles',lambda records:(bundles,controls,{site:{} for site in study.SITES}))
    monkeypatch.setattr(study._CORE,'_load',lambda checked:vectors)
    features=study._CORE._features;routed=[]
    def checked_features(metadata,values,site_index,backend,layer):
        assert site_index in (1,2),'future/site3 axis was selected for a final-site fit'
        routed.append(site_index)
        return features(metadata,values,site_index,backend,layer)
    monkeypatch.setattr(study._CORE,'_features',checked_features)
    result=study.run(cfg)
    assert result['fit_banks']==result['factorizations']==30
    assert result['parameter_replay_rows']==30*n
    assert result['primary']['tasks']==list(study.FAMILIES)
    assert len(list((tmp_path/'run').glob('*.npz')))==30
    assert set(routed)=={1,2}
    monkeypatch.setattr(study._CORE,'ridge_fit',lambda *a,**k:pytest.fail('completed bank must not be fitted again'))
    assert study.run(cfg)==result
    proof=study.audit(cfg)
    assert proof['fit_banks']==proof['factorizations']==30 and proof['new_fits']==0
    assert proof['parameter_replay_rows']==30*n
