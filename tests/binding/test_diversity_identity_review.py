from copy import deepcopy
from dataclasses import replace
import json
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import diversity_identity_review as study
from codecue.binding import relationships


def bundle_fixture(site=7,n=4):
    source='\n'.join(['v0 = 1','v1 = 2','v2 = 3','v3 = 4','v0 = v1','v0 = v2','v1 = v0','v0 = v3','v0'])
    graph=relationships.labels_at(source,min(site,7),{f'v{i}':i for i in range(4)},output_visible=site==8)
    nodes=sorted(graph['version_nodes'],key=lambda x:x['statement']);node_index={node['id']:node['statement'] for node in nodes}
    current={node['slot']:node for node in nodes if node['status']=='current'}
    direct={(node_index[a],node_index[b]) for a,b in graph['direct_def_use_edges']}
    ancestor={(node_index[a],node_index[b]) for a,b in graph['strict_ancestor_edges']}
    output={node_index[x] for x in graph.get('output',{}).get('structural_ancestors',[])}
    y=np.zeros((n,232));mask=np.zeros_like(y,dtype=bool);checkpoint=min(site,7)
    for spec in study.target.COLUMNS:
        j=spec['index'];family=spec['family'];valid=False;value=False
        if family in ('direct','ancestor'):
            a,b=spec['source_node'],spec['consumer_node'];valid=4<=b<=checkpoint and a<b
            value=(a,b) in (direct if family=='direct' else ancestor)
        elif family in ('current','obsolete'):
            node=spec['source_node'];valid=node<=checkpoint
            value=valid and nodes[node]['status']==family
        elif family=='output_ancestor':valid=site==8;value=spec['source_node'] in output
        elif family=='current_definition':
            valid=spec['candidate']<=checkpoint;value=spec['candidate']==current[spec['slot']]['statement']
        elif family=='current_version':
            valid=site in (7,8) or spec['candidate']==1;value=spec['candidate']==current[spec['slot']]['version']
        elif family=='copy_parent':
            consumer=4+spec['copy_step'];valid=consumer<=checkpoint and spec['candidate']<consumer
            value=(spec['candidate'],consumer) in direct
        mask[:,j]=valid;y[:,j]=valid and value
    maps=[[dict(statement=x['statement'],id=x['id'],slot=x['slot'],version=x['version'],status=x['status']) for x in nodes] for _ in range(n)]
    descriptive=dict(control=False,version_map_by_case=maps,
        canonical_visible_prefixes=[source]*n,canonical_output_visible_prefixes=[source]*n)
    return study.target.TargetBundle(y,mask,study.target.COLUMNS,tuple(f'c{i}' for i in range(n)),
        tuple('large' if i<n-1 else 'small' for i in range(n)),('development',)*n,site,descriptive)


def methods_fixture(site=7):
    bundle=bundle_fixture(site)
    real=np.full(bundle.y.shape,np.nan);active=bundle.mask.any(axis=0);real[:,active]=bundle.y[:,active]
    data=study.saved.predictions(bundle,real)
    sham_y=bundle.y.copy()
    if site in (7,8):
        for head in study.target.HEADS:
            if head['family']=='current_version':
                sham_y[:,head['indices']]=0;sham_y[:,head['indices'][1]]=1
    sham_bundle=replace(bundle,y=sham_y,descriptive={**bundle.descriptive,'control':True})
    sham_scores=np.full(sham_y.shape,np.nan);sham_scores[:,active]=sham_y[:,active]
    sham=study.saved.predictions(sham_bundle,sham_scores)
    support=study.original._CORE._train_support(sham_bundle,np.ones(len(sham_y),dtype=bool))
    old_metrics=study.original.metrics(sham_bundle,sham_scores,support)
    return bundle,dict(direct=data,training_prior=deepcopy(data),random_prefix_control=sham),old_metrics


def config(tmp_path):
    return dict(evaluation_role=study.ROLE,readout_configs=[
        {'path':str(tmp_path/'a.json'),'sha256':'a'*64},{'path':str(tmp_path/'b.json'),'sha256':'b'*64}],
        declared_plan=str(tmp_path/'plan.md'),declared_plan_sha256='c'*64,
        run_dir=str(tmp_path/'out'),report=str(tmp_path/'report.md'))


def test_source_oracle_parent_frame_and_scalar_task_remain_separate():
    bundle,methods,sham=methods_fixture()
    diagnostic=study._diagnostics(bundle,methods,bundle.group_ids,['3_1_0_0']*4,sham)
    assert set(diagnostic['oracle_assisted_real_methods'])=={'direct','training_prior'}
    real=diagnostic['oracle_assisted_real_methods']['direct']
    # Statement1 is obsolete at capture but was exactly current when copy0 read it.
    assert bundle.descriptive['version_map_by_case'][0][1]['status']=='obsolete'
    assert real['per_head']['copy_parent/0']['counts']['exact']==4
    assert real['per_family']['copy_parent']['counts']['exact']==16
    assert real['per_family']['current_version']['metric_denominators']['owner_correct']==0
    assert real['per_family']['current_version']['metric_rates']['owner_correct'] is None
    assert diagnostic['sham_original_task']['whole_categorical_families']['current_version']['accuracy']==1


def test_sham_predictions_are_never_interpreted_against_real_source_truth():
    bundle,methods,sham=methods_fixture()
    assert not np.array_equal(methods['direct']['truth'],methods['random_prefix_control']['truth'])
    diagnostic=study._diagnostics(bundle,methods,bundle.group_ids,['profile']*4,sham)
    assert diagnostic['sham_original_task']['preserved_prediction_metrics']['whole_families']['current_version']['rate']==1
    with pytest.raises(ValueError,match='real-task bundle'):
        study._core().diagnostics(replace(bundle,descriptive={**bundle.descriptive,'control':True}),methods['random_prefix_control'])


def test_changed_saved_sham_predictions_fail_original_task_anchor():
    bundle,methods,sham=methods_fixture()
    methods['random_prefix_control']['predicted'][:,4]=1
    methods['random_prefix_control']['correct'][:,4]=False
    with pytest.raises(ValueError,match='sham predictions'):
        study._diagnostics(bundle,methods,bundle.group_ids,['profile']*4,sham)


def test_initial_undefined_parents_remain_undefined_in_compact_summary():
    bundle,methods,sham=methods_fixture(3)
    diagnostic=study._diagnostics(bundle,methods,bundle.group_ids,['profile']*4,sham)
    summary=study._cell_summary(diagnostic)['direct']['copy_parent']
    assert summary['n_total']==16 and summary['n_defined']==0 and summary['n_undefined']==16
    assert summary['metric_rates']['exact'] is None
    assert summary['metric_denominators']['exact']==0


def test_compact_stats_keep_target_specific_metric_denominators():
    stats=dict(n_total=20,n_defined=16,n_undefined=4,counts={'exact':8},rates={'exact':.5},
        equal_graph_rates={'exact':.4},metric_counts={'owner_correct':8},metric_denominators={'owner_correct':12},
        metric_rates={'owner_correct':2/3},equal_graph_metric_rates={'owner_correct':.6},per_graph={'large':{'n':12}})
    compact=study._compact_stats(stats)
    assert compact['metric_denominators']=={'owner_correct':12}
    assert 'per_graph' not in compact and compact['n_undefined']==4


def test_exact_full_output_inventory_has_no_overlaps(tmp_path):
    paths=study._output_paths(config(tmp_path))
    assert len(paths)==len(set(paths.values()))==185
    assert sum(path.suffix=='.npz' for path in paths.values())==90
    assert sum(name.startswith('diagnostics_') for name in paths)==90


@pytest.mark.parametrize('problem',['old_role','duplicate_source','bad_pin','report_reserved','input_ancestor'])
def test_config_guard_rejects_role_pin_and_output_overlap(tmp_path,problem):
    cfg=config(tmp_path)
    if problem=='old_role':cfg['evaluation_role']=study.saved.ROLE
    if problem=='duplicate_source':cfg['readout_configs'][1]=cfg['readout_configs'][0]
    if problem=='bad_pin':cfg['readout_configs'][0]['sha256']='bad'
    if problem=='report_reserved':cfg['report']=str(tmp_path/'out'/'prediction_replay_review_v1.json'/'bad.md')
    if problem=='input_ancestor':cfg['run_dir']=str(tmp_path/'plan.md'/'out')
    with pytest.raises(ValueError):study._config(cfg)


def test_prediction_identity_preserves_profiles_and_original_score_fingerprint(tmp_path):
    identity=dict(case_ids=['a','b'],features_sha256='f'*64)
    actual=study._prediction_identity(config(tmp_path),'llama8b','bank',{'path':'source.npz'},identity,['p0','p1'])
    assert actual['original_score_identity_sha256']==study.digest(identity)
    assert actual['profile_ids_sha256']==study.digest(['p0','p1'])
    assert 'case_ids' not in actual and actual['opaque_original_feature_sha256']=='f'*64


def summary_result():
    stats={family:dict(n_defined=5760,metric_rates=dict(exact=.5,owner_correct=None if family=='current_version' else .6,version_number_equal=.7),
        equal_graph_metric_rates=dict(exact=.4,owner_correct=None if family=='current_version' else .5,version_number_equal=.6))
        for family in study.FAMILIES}
    cells=[]
    for model in ('llama8b','codellama34b'):
        for backend,layer in (('hidden',24),('surface',-1)):
            for site in (7,8):
                for seed in study.SEEDS:
                    cells.append(dict(model=model,backend=backend,layer=layer,site=site,seed=seed,
                        summary_methods={method:deepcopy(stats) for method in study.REAL_METHODS}))
    return dict(config_hash='a'*64,cells=cells)


def test_primary_summary_keeps_three_seeds_and_scalar_owner_undefined():
    summary=study._summary(summary_result())
    current=summary['primary']['llama8b']['hidden']['7']['direct']['current_version']
    assert current['metric_rates']['owner_correct'] is None
    assert current['n_defined_per_seed']==5760 and current['weighting_seeds']==[17,29,43]
    assert current['equal_graph_metric_rates']['exact']==pytest.approx(.4)
    assert summary['saved_score_rows_checked']==518400 and summary['development_prediction_rows']==129600
    text=study._report(summary_result())
    assert 'oracle-assisted' in text and 'undefined' in text


def test_primary_summary_refuses_seed_selection():
    result=summary_result();result['cells'].pop()
    with pytest.raises(ValueError,match='all fixed primary seeds'):
        study._summary(result)


def test_small_immutable_diagnostics_and_conflict_detection(tmp_path):
    path=tmp_path/'diagnostics.json';study._publish_json(path,{'status':'synthetic'})
    study._publish_json(path,{'status':'synthetic'})
    with pytest.raises(ValueError):study._publish_json(path,{'status':'changed'})
    assert json.loads(path.read_text())=={'status':'synthetic'}
