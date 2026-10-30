"""The new calibration uses its own typed source, prompt and score contracts."""
import json
import sys
from types import SimpleNamespace

import pytest

from codecue.binding import checkpoint_suite as suite
from codecue.binding.datasets import digest
from codecue.binding.published_benchmarks import sha


def source(tmp_path, role):
    path=tmp_path/'sources.jsonl';path.write_text('{"id":"sample"}\n')
    path.with_suffix('.manifest.json').write_text(json.dumps(dict(sha256=sha(path),evaluation_role=role)))
    return dict(kind='computation_routing',dataset=str(path),sha256=sha(path))


def test_new_dataset_role_is_checked_before_its_validator(tmp_path,monkeypatch):
    module=SimpleNamespace(ROLE='routing_discovery',validate_rows=lambda rows:pytest.fail('unapproved source validation'))
    monkeypatch.setitem(sys.modules,'codecue.binding.computation_routing_programs',module)
    with pytest.raises(ValueError,match='calibration role'):
        suite.generated_rows(source(tmp_path,'reserved_outcomes'))


def test_new_sources_use_their_own_semantic_validator(tmp_path,monkeypatch):
    observed=[]
    def validate(rows):observed.extend(rows)
    monkeypatch.setitem(sys.modules,'codecue.binding.computation_routing_programs',
        SimpleNamespace(ROLE='routing_discovery',validate_rows=validate))
    assert suite.generated_rows(source(tmp_path,'routing_discovery'))==[dict(id='sample')]
    assert observed==[dict(id='sample')]


def test_new_scores_do_not_fall_through_to_legacy_calibration_parser(monkeypatch):
    seen=[]
    def score(case,raw):seen.append((case,raw));return dict(prediction=None,valid=False,correct=False)
    monkeypatch.setitem(sys.modules,'codecue.binding.computation_routing_programs',SimpleNamespace(score_case=score))
    case=dict(kind='computation_routing',variant='routing_output_v1',record=dict(expected_answer=2))
    assert suite.score_case(case,'Answer: 2')==dict(prediction=None,valid=False,correct=False)
    assert seen==[(case,'Answer: 2')]


def test_preparation_uses_declared_instruction_rendering_and_exact_token_ids(tmp_path,monkeypatch):
    class Tokenizer:
        def __call__(self,text,**kwargs):return dict(input_ids=[101,len(text)])
    tokenizer=Tokenizer();rendered=[]
    monkeypatch.setitem(sys.modules,'transformers',SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *a,**k:tokenizer)))
    import codecue.binding.model_adapter as adapter
    monkeypatch.setattr(adapter,'configure_tokenizer',lambda *args:None)
    monkeypatch.setattr(suite,'code_identity',lambda:dict(source_sha256='fixture'))
    row=dict(id='new',source='x = 2\nx',expected_answer=2)
    monkeypatch.setattr(suite,'generated_rows',lambda section:[row])
    def prompt(tok,record,variant):
        assert tok is tokenizer and record is row
        rendered.append(variant);return 'fixed '+variant,'x = 2\nprint(x)'
    spec=dict(max_new_tokens=16,stop_at_blank_line=True,answer_mode='integer')
    monkeypatch.setitem(sys.modules,'codecue.binding.computation_routing_programs',
        SimpleNamespace(instruction_spec=lambda variant:spec,prompt=prompt))
    cfg=dict(model='fixture',tokenizer_revision='a'*40,context_limit=4096,
        sections=[dict(kind='computation_routing',name='routing',variants=['routing_output_v1','routing_execute_v1','routing_value_v1'])],
        prepared_cases=str(tmp_path/'cases.jsonl'),preflight_result=str(tmp_path/'preflight.json'))
    checked=suite.preflight(cfg)
    cases=[json.loads(line) for line in (tmp_path/'cases.jsonl').read_text().splitlines()]
    assert checked['cases']==3 and rendered==cfg['sections'][0]['variants']
    assert all(c['kind']=='computation_routing' and c['record']==row and c['max_new_tokens']==16
        and c['stop']==['\n\n'] and c['input_token_ids']==[101,len(c['prompt'])]
        and c['prompt_sha256']==digest(c['prompt']) for c in cases)
