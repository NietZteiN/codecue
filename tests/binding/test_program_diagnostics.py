import ast
import json
from pathlib import Path
import pytest
from codecue.binding.program_diagnostics import build,validate_rows,oracle_source,summarize
from codecue.binding.datasets import read_jsonl,digest,write_json
from codecue.binding.calibration import printed_source


@pytest.mark.parametrize('kind,n', [('arithmetic_forms',192),('arithmetic_free',384)])
def test_diagnostic_design_is_fresh_balanced_and_independently_executable(tmp_path,kind,n):
    config=dict(dataset=str(tmp_path/'data.jsonl'),diagnostic_kind=kind,seed=2026102511)
    result=build(config);rows=read_jsonl(config['dataset'])
    assert len(rows)==n and result['independent_python_programs']==n
    assert len({r['source'] for r in rows})==n
    assert {r['split'] for r in rows}=={'train','development'}
    assert validate_rows(rows,kind)==rows
    if kind=='arithmetic_free':
        assert not any(isinstance(node,ast.BinOp) for r in rows for node in ast.walk(ast.parse(r['source'])))
    else:
        for group in {r['paired_group_id'] for r in rows}:
            assert len({r['expected_answer'] for r in rows if r['paired_group_id']==group})==1
    with pytest.raises(ValueError,match='immutable'):build(config)


def test_expression_only_readout_is_restricted_and_semantics_preserving():
    assert printed_source('(9 - 4) + 2')=='print(9 - 4 + 2)'
    assert oracle_source('(9 - 4) + 2')=='expression_result = 9 - 4 + 2\nexpression_result'
    with pytest.raises(ValueError):printed_source('arbitrary_call()')
    with pytest.raises(ValueError):printed_source('unbound + 2')


def test_protocol_is_chosen_on_training_and_cannot_fall_back_after_validation(tmp_path):
    config=dict(dataset=str(tmp_path/'data.jsonl'),diagnostic_kind='arithmetic_forms',seed=2026102512,
                run_dir=str(tmp_path/'run'),calibration={'variants':['print_direct_v3','print_trace_long_v1']})
    build(config);rows=read_jsonl(config['dataset']);output=Path(config['run_dir'])/'protocol_calibration';output.mkdir(parents=True)
    observed=[]
    for variant in config['calibration']['variants']:
        for row in rows:
            prediction=row['expected_answer']
            if variant=='print_direct_v3' and row['split']=='development':prediction+=100
            raw=str(prediction) if variant=='print_direct_v3' else f'Answer: {prediction}'
            observed.append(dict(row,variant=variant,raw_response=raw,prediction=prediction,correct=prediction==row['expected_answer']))
    (output/'responses.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in observed))
    identity={'config':config};write_json(output/'manifest.json',dict(identity=identity,identity_hash=digest(identity),status='complete'))
    decision=summarize(config)
    assert decision['training_candidate']=='print_direct_v3'
    assert decision['selected_protocol'] is None and decision['status']=='failed_validation'
