"""Historical semantics and fresh discovery-source guards; no models or datasets opened."""
from collections import Counter
from copy import deepcopy
import ast
import hashlib
import json
from pathlib import Path

import pytest

from codecue.binding import old_value_programs as study
from codecue.binding import schedule_diversity_programs as graph_source


def template(destinations=(0,0,1,2),parents=(1,2,0,3)):
    graph=study._graph(destinations,parents)
    profile='_'.join(map(str,sorted(Counter(destinations).values(),reverse=True)+[0]*(4-len(set(destinations)))))
    return dict(canonical_graph_sha256=graph,component_id='schedule-diversity-graph:'+graph[:24],
        split='train',profile_id=profile,destinations=list(destinations),parents=list(parents))


def row(slot=0,mode='previous',parents=(1,2,0,3),values=(1,2,3,4),lexical=0):
    t=template(parents=parents)
    return study._row(t,1151,0,lexical,values,t['destinations'],t['parents'],slot,mode)


def python_answer(source):
    tree=ast.parse(source);expression=tree.body.pop();namespace={}
    exec(compile(tree,'<old-value-fixture>','exec'),{'__builtins__':{}},namespace)
    return eval(compile(ast.Expression(expression.value),'<old-value-fixture>','eval'),{'__builtins__':{}},namespace)


@pytest.fixture(scope='module')
def synthetic_templates():
    selected,_=graph_source._select(202610284,set())
    result=[]
    for profile in graph_source.PROFILES:
        for i,(graph,destinations,parents) in enumerate(selected[profile]):
            result.append(dict(canonical_graph_sha256=graph,component_id='schedule-diversity-graph:'+graph[:24],
                split='train' if i<15 else 'development',profile_id='_'.join(map(str,profile)),
                destinations=list(destinations),parents=list(parents)))
    return sorted(result,key=lambda r:r['canonical_graph_sha256'])


@pytest.fixture(scope='module')
def cohort(synthetic_templates):
    original=study._load_templates
    study._load_templates=lambda config:synthetic_templates
    try:rows=study.make_rows({})
    finally:study._load_templates=original
    return rows


@pytest.mark.parametrize('slot,old,current,last,version',[(0,2,3,5,2),(1,2,3,6,1),(2,3,4,7,1)])
def test_historical_question_reads_before_owners_last_write(slot,old,current,last,version):
    previous=row(slot);latest=row(slot,'current')
    assert previous['body']==latest['body'] and previous['pair_id']==latest['pair_id']
    assert previous['expected_answer']==old and latest['expected_answer']==current
    assert previous['last_write_statement']==last and previous['target_assignment_version']==version
    assert python_answer(previous['oracle_source'])==old and python_answer(latest['oracle_source'])==current
    assert python_answer(previous['source'])==current
    assert previous['oracle_source'].splitlines()[:-1]==previous['body'].splitlines()[:last]
    assert previous['query_statement']==last-1 and latest['query_statement']==7


def test_absent_retained_and_equal_value_controls_remain_distinct():
    absent=row(0);retained=row(2);equal=row(0,parents=(1,1,0,3))
    assert absent['old_storage']=='absent_all_current' and absent['previous_value'] not in absent['current_values']
    assert retained['old_storage']=='retained_other_current' and retained['old_retained_in_other_slots']==[0,1]
    assert equal['old_storage']=='equal_current' and equal['primary_distinct'] is False
    assert absent['primary_distinct'] and retained['primary_distinct']


def test_zero_and_signed_roots_have_unambiguous_python_history():
    value=row(values=(0,-1,12,-12))
    assert 0 in value['root_values'] and len(set(value['root_values']))==4
    assert python_answer(value['oracle_source'])==value['expected_answer']
    checked=study.trace_body(value['body'],independent=True)
    assert checked['independent_python_statements']==8


@pytest.mark.parametrize('body',[
    'a = 1\nb = 2\nc = 3\nd = 4\na = b\nb = a\nc = d\nd = missing',
    'a = 1\nb = 2\nc = 3\nd = 4\na = a\nb = a\nc = d\nd = c',
    'a = 1\nb = 2\nc = 3\nd = 4\na = b + 1\nb = a\nc = d\nd = c',
    'a = True\nb = 2\nc = 3\nd = 4\na = b\nb = a\nc = d\nd = c',
    'a = 1\nb = 1\nc = 3\nd = 4\na = b\nb = a\nc = d\nd = c',
    'a = 1\nb = 2\nc = 3\nd = 4\na = b\nb = a\nc = d\nimport os',
])
def test_restricted_source_rejects_undefined_selfcopy_arithmetic_and_noninteger_roots(body):
    with pytest.raises(ValueError):study.trace_body(body,independent=True)


def test_independent_python_comparison_cannot_be_a_predeclared_pass(monkeypatch):
    monkeypatch.setattr(study,'exec',lambda *args,**kwargs:None,raising=False)
    with pytest.raises(ValueError,match='ordinary-Python'):study.trace_body(row()['body'],independent=True)


class Tokenizer:
    def apply_chat_template(self,messages,tokenize=False,continue_final_message=False):
        assert tokenize is False and continue_final_message is True
        self.messages=messages
        return messages[0]['content']+'\n'+messages[1]['content']


@pytest.mark.parametrize('variant',study.INSTRUCTIONS)
def test_prompt_shows_full_body_and_question_without_truth_or_oracle_prefix(variant):
    value=row();tokenizer=Tokenizer();text,body=study.prompt(tokenizer,value,variant)
    assert body==value['body'] and '\n```\n\n'+value['question'] in text
    assert text.count(value['body'])==1 and text.count('item_0 = item_2')==1
    assert value['source'] not in text
    assert text.split('```python\n',1)[1].split('\n```',1)[0]==value['body']
    changed=deepcopy(value);changed['expected_answer']=99999;changed['oracle_source']='SECRET ORACLE';changed['previous_value']=99999
    assert study.prompt(tokenizer,changed,variant)[0]==text
    assert study.instruction_spec(variant)==dict(max_new_tokens=16,stop_at_blank_line=True,answer_mode='integer')


@pytest.mark.parametrize('raw,prediction', [('  +2\n',2),('-12',-12),('0',0),('02',2),('Answer: 2',None),('2\n3',None),('２',None),('2.0',None),('',None),('9'*129,None),(None,None)])
def test_strict_full_ascii_integer_response_parser(raw,prediction):
    result=study.score_case({'record':row()},raw)
    assert result==dict(prediction=prediction,valid=prediction is not None,correct=prediction==2)


@pytest.mark.parametrize('field,bad',[('expected_answer',99),('oracle_source','item_0'),('question','What is item_0 now?'),('old_storage','equal_current'),('last_write_statement',7),('target_assignment_version',4),('destination_schedule',[4,0,1,2]),('component_id','unrelated-group')])
def test_single_row_semantic_tampering_is_rejected(field,bad):
    value=row();value[field]=bad
    with pytest.raises(ValueError):study._validate_row(value)


def test_complete_cohort_preserves_pair_split_profile_and_factorial_support(cohort):
    checked=study._validation(cohort,independent=True)
    assert checked['rows']==6720 and checked['pairs']==3360 and checked['bodies']==1440
    assert checked['split_rows']=={'train':5040,'development':1680}
    assert checked['split_graph_families']=={'train':45,'development':15}
    assert checked['source_support_minimum']>=24 and checked['independent_python_statements']==11520
    assert set(checked['old_storage_counts'])==set(study.STORAGE)
    assert study.analysis_rows(cohort) is cohort


def test_missing_or_moved_graph_relatives_fail_even_with_replacement_counts(cohort):
    with pytest.raises(ValueError,match='full6720'):study.validate_rows(cohort[:-1])
    duplicate=list(cohort);duplicate[-1]=duplicate[0]
    with pytest.raises(ValueError,match='duplicate'):study.validate_rows(duplicate)
    moved=list(cohort);moved[0]=dict(moved[0],split='train' if moved[0]['split']=='development' else 'development')
    with pytest.raises(ValueError,match='crosses'):study.validate_rows(moved)


def config(folder):
    return dict(evaluation_role=study.ROLE,source_graphs=dict(path=str(folder/'pinned_graphs.jsonl'),sha256=study.SOURCE_SHA256),numeric_seeds=list(study.NUMERIC_SEEDS),dataset=str(folder/'sources.jsonl'),review=str(folder/'review.json'),report=str(folder/'sources.md'))


def test_sha_pin_is_checked_before_source_json_parse(tmp_path):
    cfg=config(tmp_path);Path(cfg['source_graphs']['path']).write_bytes(b'not-json')
    with pytest.raises(ValueError,match='SHA'):study._load_templates(cfg)


@pytest.mark.parametrize('problem',['role','seeds','source_pin','collision','sealed'])
def test_config_guards_pin_and_protected_output_contract(tmp_path,problem):
    cfg=config(tmp_path)
    if problem=='role':cfg['evaluation_role']='final_old_value'
    elif problem=='seeds':cfg['numeric_seeds']=[1,2,3]
    elif problem=='source_pin':cfg['source_graphs']['sha256']='0'*64
    elif problem=='collision':cfg['dataset']=cfg['source_graphs']['path']
    else:cfg['dataset']=str(tmp_path/'final_outcomes.jsonl')
    with pytest.raises(ValueError):study._config(cfg)


def test_generation_and_publication_are_deterministic_immutable(tmp_path,monkeypatch,synthetic_templates):
    cfg=config(tmp_path)
    monkeypatch.setattr(study,'_load_templates',lambda generation:synthetic_templates)
    monkeypatch.setattr(study,'code_identity',lambda:dict(source_sha256='0'*64))
    def publish(path,payload):
        Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_bytes(payload)
    monkeypatch.setattr(study,'_publish',publish)
    first=study.build(cfg);files=list(tmp_path.iterdir());before={p.name:p.read_bytes() for p in files}
    second=study.build(cfg)
    assert first==second and before=={p.name:p.read_bytes() for p in files}
    manifest=json.loads(Path(cfg['dataset']).with_suffix('.manifest.json').read_text())
    assert manifest['sha256']==hashlib.sha256(Path(cfg['dataset']).read_bytes()).hexdigest()
    assert manifest['independent_python_passed'] is True and manifest['generated_holdouts_opened'] is False
    Path(cfg['review']).write_text('changed')
    with pytest.raises(ValueError,match='immutable'):study.build(cfg)
    assert Path(cfg['dataset']).read_bytes()==before['sources.jsonl']
