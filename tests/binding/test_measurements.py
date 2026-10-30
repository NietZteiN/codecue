import numpy as np
import pytest
from codecue.binding.activations import labels_at
from codecue.binding.analysis import summarize
from codecue.binding.behavior import select, classify
from codecue.binding.heldout import probability_scores
from codecue.binding.interpreter import execute
from codecue.binding.interventions import changed_record
from codecue.binding.programs import rename
from codecue.binding.probes import fit_ridge, predict, metrics


def test_prefix_labels_cannot_contain_future_updates():
    record = execute('v0 = 2\nv1 = v0 + 3\nv0 = 9\nv0 - v1')
    early = labels_at(record, 0)
    assert early['current'] == [2, None, None, None]
    assert early['previous'] == [None] * 4
    late = labels_at(record, 2)
    assert late['current'] == [9, 5, None, None]
    assert late['previous'] == [2, None, None, None]
    assert late['multiset'] == [5, 9, None, None]


def test_neutral_train_supplement_keeps_all_development_conditions():
    from codecue.binding.activations import extraction_rows
    rows=[dict(id=f'{s}:{c}',split=s,condition=c,control_kind='primary')
          for s in ('train','development') for c in ('neutral','informative','misleading')]
    config=dict(extraction_splits=['train','development'],control_kinds=['primary'],
                extraction_conditions_by_split={'train':['neutral'],'development':['neutral','informative','misleading']})
    chosen=extraction_rows(rows,config)
    assert {r['id'] for r in chosen}=={'train:neutral','development:neutral','development:informative','development:misleading'}
    with pytest.raises(ValueError,match='every requested split'):
        extraction_rows(rows,{**config,'extraction_conditions_by_split':{'train':['neutral']}})


def test_ridge_train_normalization_and_masking():
    rng = np.random.default_rng(19)
    x = rng.normal(size=(120, 8))
    y = np.rint(x @ rng.normal(size=(8,4)))
    y[:20,2] = np.nan
    fitted = fit_ridge(x[:100], y[:100], alpha=.01)
    assert np.allclose(fitted[0], x[:100].mean(0))
    assert metrics(predict(fitted, x[100:]), y[100:])['slot_exact_accuracy'] > .7
    # Unseen data cannot change a fitted normalizer.
    old = fitted[0].copy()
    predict(fitted, x[100:] + 100)
    assert np.array_equal(old, fitted[0])
    stronger=fit_ridge(x[:100],y[:100],alpha=10000)
    assert np.linalg.norm(stronger[2])<np.linalg.norm(fitted[2])


def test_masked_ridge_has_unpenalized_intercept_on_valid_rows():
    x = np.linspace(-10,10,120)[:,None]
    y = 2*x + 3
    y[x[:,0] < 2] = np.nan
    fitted = fit_ridge(x,y,alpha=1e-8)
    assert np.max(np.abs(predict(fitted,x)-np.rint(2*x+3))) == 0


def test_reanalysis_requires_explicit_cache_source_and_matching_capture_config():
    from codecue.binding.probes import check_cache_identity, source_at_site
    cached = {'identity':{'code':{'source_sha256':'old'},'config':{'dataset':'same'}}}
    current = {'identity':{'code':{'source_sha256':'new'}}}
    with pytest.raises(ValueError,match='cache identity'):
        check_cache_identity(cached,current,{'dataset':'same'})
    config={'dataset':'same','probe_analysis':{'cache_source_sha256':'old'}}
    check_cache_identity(cached,current,config)
    with pytest.raises(ValueError,match='configuration'):
        check_cache_identity(cached,current,{**config,'dataset':'changed'})
    row={'source':'v0 = 2\nv1 = v0 + 3\nv0 - v1','features':{}}
    assert source_at_site(row,'last_assignment')['source']=='v0 = 2\nv1 = v0 + 3'
    assert source_at_site(row,'source_final') is row


def test_frozen_probability_scores_and_boundaries():
    assert probability_scores([0,1], [0,1])['brier_score'] == 0
    assert probability_scores([.5,.5], [0,1])['brier_score'] == .25
    assert sum(b['n'] for b in probability_scores([0,.1,.2,.9,1], [0]*5)['calibration']) == 5
    with pytest.raises(ValueError):
        probability_scores([1.2], [1])


def test_same_answer_intervention_control_is_semantic():
    source = 'v0 = 8\nv1 = 3\nv2 = 1\nv3 = 2\n(v0 - (v1 + v1)) + (v2 - v3)'
    record = {'canonical_source': source, 'rename_map': {f'v{i}':f'item_{i}' for i in range(4)}}
    record['source'] = rename(source,record['rename_map'])
    donor = changed_record(record, {'v1@1':5})
    control = changed_record(record, {'v0@1':12, 'v1@1':5})
    assert donor['expected_answer'] != execute(source)['expected_answer']
    assert control['expected_answer'] == execute(source)['expected_answer']
    assert control['execution_trace'][-1]['values'] != execute(source)['execution_trace'][-1]['values']


def test_sealed_holdout_is_not_selected_implicitly():
    r = dict(split='test', control_kind='primary')
    with pytest.raises(ValueError, match='test is sealed'):
        select([r], dict(splits=['test'], control_kinds=['primary']))


def test_balanced_selection_keeps_every_naming_variant():
    rows=[]
    for base in ('a','b'):
        for condition in ('neutral','informative','misleading'):
            for lexical in (0,1):
                rows.append(dict(split='train', family='parallel',load=2,updates=1,
                                 base_id=base,condition=condition,lexical_realization=lexical,control_kind='primary'))
    chosen=select(rows,dict(splits=['train'],control_kinds=['primary'],per_cell_limit=1))
    assert len(chosen)==6 and {r['base_id'] for r in chosen}=={'a'}


def test_balanced_selection_can_preserve_primary_magnitude_mixture():
    from collections import Counter
    rows=[]
    for cell in (2,4):
        for bin_id in (0,1,2):
            for numeric in range(4):
                for condition in ('neutral','informative','misleading'):
                    for lexical in (0,1):
                        rows.append(dict(split='train',family='parallel',load=cell,updates=1,
                            base_id=f'{cell}:{bin_id}:{numeric}',condition=condition,lexical_realization=lexical,
                            control_kind='primary',answer_magnitude_bin=bin_id))
    config=dict(splits=['train'],control_kinds=['primary'],per_cell_limit=5,magnitude_bin_counts={'0':2,'1':2,'2':1})
    chosen=select(rows,config)
    assert len(chosen)==60
    assert Counter((r['load'],r['answer_magnitude_bin']) for r in chosen)=={
        (2,0):12,(2,1):12,(2,2):6,(4,0):12,(4,1):12,(4,2):6}
    with pytest.raises(ValueError,match='sum'):
        select(rows,{**config,'per_cell_limit':4})


def test_clustered_naming_deltas_and_interactions():
    rows=[]
    truth=dict(expected_answer=1,diagnostic_counterfactuals=[])
    for cluster in ('a','b'):
        for load in (2,4):
            for updates in (1,3):
                for condition in ('neutral','informative','misleading'):
                    for lexical in (0,1):
                        correct=not(condition=='misleading' and load==4)
                        pred=1 if correct else 2
                        rows.append(dict(id=f'{cluster}{load}{updates}{condition}{lexical}',
                            base_id=f'{cluster}{load}{updates}',template_id=f't{cluster}{load}{updates}',
                            cluster_id=f'{cluster}{updates}', family='parallel',load=load,updates=updates,
                            split='development',control_kind='primary', condition=condition,
                            lexical_realization=lexical,correct=correct,prediction=pred,
                            classification=classify(truth,pred),diagnostically_distinct_available=False))
    result=summarize(rows)
    effect=next(r for r in result['within_base_naming_deltas'] if r['condition']=='misleading')
    assert effect['estimate']==-.5
    interaction=next(r for r in result['naming_factor_interactions'] if r['condition']=='misleading' and r['factor']=='load')
    assert interaction['estimate']==-1
    assert effect['clusters']==4


def test_usage_accounting_does_not_block_parallel_stages_or_other_checkpoints(tmp_path):
    from codecue.binding.budget import reserve, release
    config = dict(device='cuda', model='local', model_revision='a'*40,
                  run_dir='example', max_gpu_seconds=10000, budget_ledger=str(tmp_path/'budget.json'))
    first=reserve(config,'behavior')
    second=reserve(config,'activations')
    assert first['reserved_seconds']==second['reserved_seconds']==0
    intervention=reserve(config,'interventions')
    release(first,20,'complete')
    release(second,10,'complete')
    third=reserve(config,'behavior')
    assert third['reserved_seconds']==0
    release(third,0,'test')
    diagnostic=reserve(config,'interface_diagnostics')
    assert diagnostic['reserved_seconds']==0
    release(diagnostic,0,'test')
    reference=reserve(config,'generation_reference')
    assert reference['reserved_seconds']==0
    release(reference,0,'test')
    assert reserve({**config,'device':'cpu'},'behavior') is None
    other=reserve({**config,'model':'different'},'behavior')
    release(intervention,0,'test')
    release(other,0,'test')


def test_every_calibration_boundary_is_counted_once():
    p=np.linspace(0,1,101)
    assert sum(b['n'] for b in probability_scores(p,np.zeros(101))['calibration'])==101


def test_registration_cannot_be_rewritten_during_resume(tmp_path):
    import json
    from codecue.binding.heldout import registration
    from codecue.binding.datasets import digest
    path=tmp_path/'registration.json'
    frozen={'status':'frozen'}
    path.write_text(json.dumps(frozen))
    config=dict(registration=str(path),registration_sha256=digest(frozen))
    frozen['hypothesis']='changed after freezing'
    path.write_text(json.dumps(frozen))
    with pytest.raises(ValueError,match='registration hash mismatch'):
        registration(config)


def test_late_quantity_queries_preserve_assignment_prefix():
    from codecue.binding.interventions import quantity_record
    from codecue.binding.programs import rename
    source='v0 = 2 + 3\nv1 = v0\nv2 = 1 + 2\nv3 = 6 - 1\nv0 = v0 + 1\nv0 - (v1 + v1)'
    row={**execute(source),'canonical_source':source,
         'rename_map':{f'v{i}':f'item_{i}' for i in range(4)},'variable_slots':{f'v{i}':i for i in range(4)}}
    row['source']=rename(source,row['rename_map'])
    q=quantity_record(row,'v1')
    assert q['source'].splitlines()[:-1]==row['source'].splitlines()[:-1]
    assert q['execution_trace']==row['execution_trace']
    assert q['expected_answer']==5
    assert q['liveness']!=row['liveness']
    with pytest.raises(ValueError,match='canonical variable slot'):
        quantity_record(row,'arbitrary()')


def test_computed_donors_retain_expression_and_verified_downstream_state():
    import ast
    from codecue.binding.interpreter import python_oracle
    from codecue.binding.programs import rename
    source='v0 = 2 + 3\nv1 = v0 + 2\nv2 = 4 - 1\nv3 = 7 - 2\nv0 - (v1 + v1)'
    record={**execute(source),'canonical_source':source,
            'rename_map':{f'v{i}':f'item_{i}' for i in range(4)},'variable_slots':{f'v{i}':i for i in range(4)}}
    record['source']=rename(source,record['rename_map'])
    donor=changed_record(record,{'v1@1':9},computed=True)
    assert isinstance(ast.parse(donor['canonical_source']).body[1].value,ast.BinOp)
    assert '9' not in donor['canonical_source']
    assert donor['execution_trace'][-1]['values']==dict(v0=5,v1=9,v2=3,v3=5)
    assert python_oracle([donor['source']])[0]['answer']==donor['expected_answer']
    assert donor['features']['answer_magnitude']==abs(donor['expected_answer'])
    # Requested values are simultaneous semantic targets even when the caller
    # lists the downstream definition first.
    both=changed_record(record,{'v1@1':9,'v0@1':8},computed=True)
    assert both['execution_trace'][-1]['values']['v0']==8
    assert both['execution_trace'][-1]['values']['v1']==9
    assert python_oracle([both['source']])[0]['answer']==both['expected_answer']
