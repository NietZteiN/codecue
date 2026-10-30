from collections import Counter
from copy import deepcopy
import json

import pytest

from codecue.binding import live_load as study
from codecue.binding.interpreter import execute
from codecue.binding.published_benchmarks import sha


@pytest.fixture(scope='module')
def generated():
    config=dict(seed=20261027,templates=2,numeric_per_template=2,noise_pairs=4)
    rows,components=study.make_rows(config)
    return config,rows,components


def test_full_numeric_bank_is_unique_sign_balanced_and_magnitudes_are_not_literals():
    bank=study.numeric_bank(dict(seed=20261027,templates=24,numeric_per_template=16,noise_pairs=4))
    assert len(bank)==384 and len({tuple(r['values']) for r in bank})==384
    for a,b in zip(bank[::2],bank[1::2]):
        x,y,u,v=a['values'];assert b['values']==[y,x,v,u] and a['history']==b['history']
        forbidden=set(a['values']+a['history']+[0,31])
        assert all(abs(value) not in forbidden for value in (x-y,u-v,(x-y)-(u-v)))
    answers=[(r['values'][0]-r['values'][1])-(r['values'][2]-r['values'][3]) for r in bank]
    assert Counter(answers)==Counter(-a for a in answers)


def test_complete_matched_factorial_and_independent_full_traces(generated):
    config,rows,components=generated
    assert len(rows)==396 and components==2
    assert Counter(r['family'] for r in rows)==dict(retention_frontier=384,literal_arithmetic=4,decomposed_arithmetic=8)
    assert study.validate_rows(rows,config,independent=True)==rows
    programs=[r for r in rows if r['family']=='retention_frontier']
    assert {r['live_bindings'] for r in programs}=={None,2,3,4}
    assert {r['updates'] for r in programs}=={1,3}
    for row in programs:
        if row['checkpoint_statement'] is not None:
            assert sum(c['affected'] for c in row['checkpoint_counterfactuals'])==row['live_bindings']


def test_checkpoint_intervention_does_not_recompute_already_completed_ancestors(generated):
    _,rows,_=generated
    row=next(r for r in rows if r['family']=='retention_frontier' and r['early_count']==2 and r['updates']==1)
    source=row['canonical_source'];truth=execute(source);cp=row['checkpoint_statement']
    assert set(truth['liveness'][cp]['live_versions'])=={'r','s'}
    dead=next(c for c in study.checkpoint_interventions(source,cp) if c['variable']=='a')
    assert not dead['affected'] and dead['expected_answer']==truth['expected_answer']
    # Substituting its earlier definition would recompute r and answer another question.
    old_definition=truth['execution_trace'][cp]['versions']['a']
    assert execute(source,{old_definition:truth['execution_trace'][cp]['values']['a']+1})['expected_answer']!=truth['expected_answer']


def test_rejects_tampered_functional_counterfactual_or_live_count(generated):
    _,rows,_=generated;index=next(i for i,r in enumerate(rows) if r.get('early_count')==1)
    bad=deepcopy(rows);bad[index]['checkpoint_counterfactuals'][0]['expected_answer']+=1
    with pytest.raises(ValueError,match='counterfactual labels'):study.validate_rows(bad)
    bad=deepcopy(rows);bad[index]['live_bindings']=4
    with pytest.raises(ValueError,match='live load'):study.validate_rows(bad)


def test_token_layout_rejects_schedule_exposure_and_update_geometry_changes():
    cases=[]
    for updates in (1,3):
        for condition in ('neutral','informative','misleading'):
            for early in (0,1,2):
                row=dict(family='retention_frontier',base_id='base',condition=condition,lexical_realization=0,
                         updates=updates,noise_pairs=4,compute_order=['left','right'],early_count=early)
                cases.append(dict(record=row,input_token_ids=([1,2,3][early:]+[1,2,3][:early])))
    assert study.validate_token_layouts(cases)['status']=='passed'
    corrupt=deepcopy(cases);corrupt[0]['input_token_ids'][-1]=4
    with pytest.raises(ValueError,match='token multiset'):study.validate_token_layouts(corrupt)


def test_existing_suite_validates_new_dataset_and_scores_ambiguous_errors(tmp_path,generated):
    from codecue.binding.checkpoint_suite import generated_rows,score_case
    _,rows,_=generated
    path=tmp_path/'frontier.jsonl';path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    path.with_suffix('.manifest.json').write_text(json.dumps(dict(sha256=sha(path),evaluation_role=study.ROLE)))
    assert generated_rows(dict(kind='live_load',dataset=str(path),sha256=sha(path)))==rows
    row=next(r for r in rows if r['family']=='retention_frontier');case=dict(kind='live_load',variant='print_direct_v3',record=row)
    assert score_case(case,str(row['expected_answer']))['correct']
    wrong=-row['expected_answer'];scored=score_case(case,str(wrong))
    assert not scored['correct'] and 'swapped_final_results' in scored['compatible_error_labels']


def test_paired_uncertainty_resamples_templates_and_retains_every_pair():
    from codecue.binding.live_load import paired_contrast
    records=[('component_a',1),('component_a',1),('component_b',-1),('component_b',-1)]
    result=paired_contrast('contrast',records,seed=9,draws=1000)
    assert result['n']==4 and result['structural_components']==2 and result['mean']==0
    assert result['exploratory_component_bootstrap_95']==[-1.,1.]
    assert paired_contrast('contrast',records,seed=9,draws=1000)==result


def test_fixed_total_variable_count_is_separate_from_functionally_live_load():
    cfg=dict(seed=20261027,templates=1,numeric_per_template=2,noise_pairs=4,initialize_results=True)
    rows,_=study.make_rows(cfg)
    for row in rows:
        cp=row.get('checkpoint_statement')
        if cp is None:continue
        point=execute(row['source'])['execution_trace'][cp]
        assert len(point['values'])==row['fixed_defined_variables']==8
        assert len(row['live_values_at_checkpoint'])==row['live_bindings']
        assert len(row['checkpoint_counterfactuals'])==8
    assert study.validate_rows(rows)==rows


def test_statement_end_measurement_allows_only_trailing_whitespace_in_token():
    from codecue.binding.live_load import statement_end_token
    text='x = 1\nprint(x)\n```'
    assert statement_end_token(text,[(0,1),(1,4),(4,6)],5)==2
    # A token spanning the next statement cannot be labeled a prior checkpoint.
    with pytest.raises(ValueError,match='crosses later code'):
        statement_end_token(text,[(0,1),(1,4),(4,11)],5)


def test_analysis_preserves_shared_clean_anchors_and_three_way_interaction(tmp_path,generated,monkeypatch):
    """Synthetic scores test bookkeeping only; they are never experiment results."""
    from codecue.binding.datasets import digest
    from codecue.binding import checkpoint_suite
    _,records,_=generated
    config=dict(run_dir=str(tmp_path),model='unit-fixture',model_revision='unit-fixture',
                primary_contrasts=['live4_minus_live2:neutral:updates3','naming_by_load_by_updates'],
                reliability_gate=dict(minimum_cell_n=1,minimum_accuracy=.9,maximum_invalid_rate=.05))
    root=tmp_path/'checkpoint_suite';root.mkdir();cases=[];responses=[]
    for row in records:
        correct=not(row['family']=='retention_frontier' and row['live_bindings']==4 and row['updates']==3 and row['condition']=='misleading')
        cases.append(dict(record=row,input_token_ids=[1,2],live_load_token_layout=dict(checkpoint_to_query_tokens=1,live_definition_ages={'x':1})))
        responses.append(dict(score=dict(correct=correct,valid=True,compatible_error_labels=[])))
    path=root/'responses.jsonl';path.write_text(''.join(json.dumps(r)+'\n' for r in responses))
    identity=dict(config=config);identity_hash=digest(identity)
    (root/'manifest.json').write_text(json.dumps(dict(identity=identity,identity_hash=identity_hash,responses_sha256=sha(path))))
    (root/'audit.json').write_text(json.dumps(dict(status='passed',identity_hash=identity_hash,preflight=dict(source_sha256='fixture'))))
    monkeypatch.setattr(checkpoint_suite,'prepared',lambda cfg,source:({},cases))
    result=study.collect(config);contrasts={c['name']:c for c in result['contrasts']}
    assert len(contrasts)==56 and result['reliability_gate']['status']=='passed'
    assert len(result['reliability_gate']['cells'])==10
    assert contrasts['live4_minus_live2:neutral:updates3']['mean']==0
    assert contrasts['naming_by_load:updates1']['mean']==0
    assert contrasts['naming_by_load:updates3']['mean']==-1
    triple=contrasts['naming_by_load_by_updates']
    assert triple['mean']==-1 and triple['n']==16 and triple['structural_components']==2
    assert triple['exploratory_component_bootstrap_95']==[-1.,-1.]


def test_backend_sample_keeps_complete_sign_and_factor_relatives_without_scores(generated):
    _,records,_=generated;cases=[dict(id=r['id'],record=r) for r in records]
    selected=study.backend_sample(cases)
    assert len(selected)==396 and {c['record']['split'] for c in selected}=={'train','development','calibration'}
    assert Counter(c['record']['expected_answer']>0 for c in selected)=={True:198,False:198}
    with pytest.raises(ValueError,match='all 396'):
        study.backend_sample(cases[1:])


def test_backend_summary_does_not_count_two_invalid_answers_as_agreement():
    invalid=dict(correct=False,valid=False,prediction=None)
    row=dict(family='literal_arithmetic',score=invalid,reference_score=invalid,parsed_prediction_matches=False,
             output_token_ids=[],reference_output_token_ids=[],first_token=2,raw_response='',uncached=dict(invalid,raw_response=''))
    summary=study.backend_summary({},[row])
    assert summary['first_token_matches']==0 and summary['parsed_prediction_matches']==0
    assert summary['uncached_cases']==1 and summary['uncached_prediction_matches']==0
    assert summary['hf_invalid']==summary['vllm_invalid']==1


def test_completion_stop_cannot_match_prompt_newline_plus_generated_newline():
    class Tokenizer:
        def decode(self,ids,**kwargs):return ''.join({13:'\n',4:'4',1:'P'}[i] for i in ids)
    from codecue.binding.live_load import generated_stop_flags
    tok=Tokenizer()
    assert generated_stop_flags(tok,[[1,13,13]],2)==[False]
    assert generated_stop_flags(tok,[[1,13,13,4]],2)==[False]
    assert generated_stop_flags(tok,[[1,13,13,13]],2)==[True]
    assert generated_stop_flags(tok,[[1,13,13]],3)==[False]
