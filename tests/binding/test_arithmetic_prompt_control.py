from copy import deepcopy
import contextlib
import io

import pytest

from codecue.binding import arithmetic_prompt_control as control
from codecue.binding import overnight_relationship_behavior as original


SOURCE='\n'.join(['v0 = 2','v1 = 3','v2 = -1','v3 = 4','v0 = v0 + v1',
                  'v1 = v0 - v3','v2 = v1 - v2','v3 = v2 + v0','v0'])


def test_actual_python_stdout_distinguishes_bare_and_printed_query():
    for source,expected in [(SOURCE,''),(control.printed(SOURCE),'5\n')]:
        output=io.StringIO()
        with contextlib.redirect_stdout(output):exec(source,{})
        assert output.getvalue()==expected


@pytest.mark.parametrize('arm',control.ARMS)
def test_all_arms_preserve_intended_query_and_original_record(arm):
    row=dict(id='case',source=SOURCE,canonical_source=SOURCE)
    old=deepcopy(row)
    new=control.variant_record(row,arm)
    assert row==old
    assert new['id']=='case:'+arm and new['format_pair_id']=='case'
    assert new['source_form']==arm
    assert control.semantic_execute(new['canonical_source'])['expected_answer']==5


@pytest.mark.parametrize('tail',['print(v0,v1)','print(v0, end="")','other(v0)','print(v0+v1)'])
def test_only_single_variable_print_wrapper_is_allowed(tail):
    with pytest.raises(ValueError):control.semantic_execute(SOURCE.rsplit('\n',1)[0]+'\n'+tail)


def test_baseline_instruction_and_legacy_engine_are_unchanged():
    assert control.INSTRUCTIONS[0]==original.capture.INSTRUCTION
    assert original.ROLE!=control.ROLE
    assert original.execute!=control.semantic_execute
    assert 'bare_i0' not in control.NEW_ARMS and len(control.NEW_ARMS)==5


def rows():
    baseline=[];fresh=[]
    for group in ['g0','g1']:
        for arm in control.ARMS:
            correct=arm!='bare_i0'
            row=dict(id=group+arm,format_pair_id=group,source_form=arm,split='development',
                     component_id=group,expected_answer=5,correct=correct,parsed=5 if correct else 7)
            (baseline if arm=='bare_i0' else fresh).append(row)
    return baseline,fresh


def test_cached_baselines_are_scored_without_becoming_new_queries():
    baseline,fresh=rows()
    result=control.summarize(fresh,baseline)
    delta=result['computed_literal']['print_i0_minus_bare_i0']
    assert delta['paired_rows']==2 and delta['families']==2
    assert delta['row_weighted_difference']==1
    assert delta['conditional_family_bootstrap_95']==[1,1]
    assert result['cells']['development/bare_i0']['accuracy']==0
    assert result['cells']['development/print_i0']['accuracy']==1
    assert len(fresh)==10


def test_missing_arm_prevents_matched_contrast():
    baseline,fresh=rows()
    with pytest.raises(ValueError,match='six paired arms'):control.summarize(fresh[:-1],baseline)


def test_different_targets_prevent_matched_contrast():
    baseline,fresh=rows();fresh[0]['expected_answer']=6
    with pytest.raises(ValueError,match='states differ'):control.summarize(fresh,baseline)


def test_control_separates_arithmetic_and_untouched_queries():
    baseline,fresh=rows()
    result=control.summarize(fresh,baseline,dict(g0='arithmetic_written',g1='untouched_literal'))
    assert result['cells']['development/arithmetic_written/print_i0']['rows']==1
    assert result['computed_literal']['arithmetic_written:print_i0_minus_bare_i0']['paired_rows']==1
    assert result['computed_literal']['untouched_literal:print_i0_minus_bare_i0']['paired_rows']==1


def test_query_strata_follow_actual_write_targets():
    assert control.query_kind(dict(canonical_source=SOURCE))=='arithmetic_written'
    text=SOURCE.replace('v3 = v2 + v0','v2 = v2 + v0').rsplit('\n',1)[0]+'\nv3'
    assert control.query_kind(dict(canonical_source=text))=='untouched_literal'


def test_failed_software_proof_cannot_load_model(tmp_path,monkeypatch):
    monkeypatch.setattr(control.base,'_current_source',lambda config:dict(source_sha256='a'*64))
    monkeypatch.setattr(control.base,'_json',lambda path:dict(status='failed',source=dict(code='a'*64)))
    monkeypatch.setattr(control._CORE,'run',lambda config:pytest.fail('failed validation reached model worker'))
    with pytest.raises(ValueError,match='software validation'):control.run(dict(run_dir=str(tmp_path/'model')))


def test_monitor_does_not_count_preparation_as_model_queries(tmp_path):
    from codecue.binding import arithmetic_prompt_suite as suite
    nodes=[dict(command='prepare',expected_cases=100,marker=str(tmp_path/'prep/a.json')),
           dict(command='run',expected_cases=7,marker=str(tmp_path/'worker1/a.json')),
           dict(command='run',expected_cases=11,marker=str(tmp_path/'worker2/a.json'))]
    config=dict(nodes=nodes,run_dir=str(tmp_path/'suite'),report=str(tmp_path/'report.md'))
    state=dict(status=dict(stage=dict(state='running')),attempts={},source={})
    result=suite._report(config,state,[])
    assert result['planned_model_prefills']==18
    assert result['observed_model_prefill_attempts']==0


def test_prompt_monitor_keeps_legacy_suite_unchanged():
    from codecue.binding import arithmetic_prompt_suite as suite,overnight_relationship_suite as legacy
    assert suite._CORE is not legacy
    assert suite.ROLE!=legacy.ROLE
    assert suite._CORE._submit_controller!=legacy._submit_controller
    assert 'scripts/173_binding_arithmetic_prompt_behavior.py' not in legacy.SCRIPTS
