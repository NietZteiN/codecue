import ast
from collections import Counter
import pytest
from codecue.binding.calibration import printed_source,parse_completion,build_bank,choose_variant,select_bank
from codecue.binding.datasets import read_jsonl
from codecue.binding.interpreter import execute


def test_print_readout_changes_only_final_expression_wrapper():
    source='v0 = 9 - 4\nv1 = v0 + 2\nv1 - v0'
    original=ast.parse(source)
    printed=ast.parse(printed_source(source))
    assert [ast.dump(s) for s in original.body[:-1]]==[ast.dump(s) for s in printed.body[:-1]]
    call=printed.body[-1].value
    assert call.func.id=='print' and ast.dump(call.args[0])==ast.dump(original.body[-1].value)
    assert execute(source)['expected_answer']==2
    printed_values=[]
    exec(compile(printed,'<software-test>','exec'),{'__builtins__':{'print':printed_values.append}})
    assert printed_values==[2]
    with pytest.raises(ValueError,match='unshadowed'):
        printed_source('print = 3\nprint')


def test_trace_parser_uses_only_explicit_final_answer_line():
    assert parse_completion('v0 is 7, then v1 is 9.\n\nAnswer: -2\n','final_answer_line')==-2
    assert parse_completion('Answer: 9\nTherefore done.','final_answer_line') is None
    assert parse_completion('The result is -2','final_answer_line') is None
    assert parse_completion('Answer: 5.','final_answer_line') is None
    assert parse_completion('  +5\n','integer')==5
    assert parse_completion('Output: 5','integer') is None


def test_training_bank_has_balanced_signs_and_independent_python_traces(tmp_path):
    path=tmp_path/'bank.jsonl'
    result=build_bank(path,per_family=3)
    rows=read_jsonl(path)
    assert result['status']=='validated' and len(rows)==24
    assert {r['split'] for r in rows}=={'train'}
    assert len(Counter((r['family'],r['answer_sign']) for r in rows))==24
    assert all(execute(r['source'])['expected_answer']==r['expected_answer'] for r in rows)
    with pytest.raises(ValueError,match='immutable'):
        build_bank(path,per_family=3)
    full=tmp_path/'full.jsonl'
    assert build_bank(full)['rows']==96
    assert len({r['source'] for r in read_jsonl(full)})==96
    subset=select_bank(read_jsonl(full),1)
    assert len(subset)==24
    assert set(Counter((r['family'],r['answer_sign']) for r in subset).values())=={1}
    with pytest.raises(ValueError,match='other evaluation roles'):
        select_bank([{**subset[0],'split':'test'}],1)


def test_calibration_gate_requires_completed_suite_and_prefers_short_answers():
    good=dict(n=12,primitive_n=8,training_n=4,invalid=0,primitive_correct=7,training_correct=2)
    summary={'complete':True,'variants':[dict(good,variant='print_trace_v1')]}
    assert choose_variant(summary)=='print_trace_v1'
    summary['variants'].append(dict(good,variant='print_direct_v3'))
    assert choose_variant(summary)=='print_direct_v3'
    assert choose_variant({**summary,'complete':False}) is None
    summary['variants'][0]['invalid']=1
    summary['variants'][1]['training_correct']=1
    assert choose_variant(summary) is None
