"""Matched arithmetic/context/routing sources, de-duplication and strict prompts."""
import ast
from collections import defaultdict
from copy import deepcopy
import json

import pytest

from codecue.binding import computation_routing_programs as p
from codecue.binding.interpreter import execute,python_oracle


@pytest.fixture(scope='module')
def bank():
    config=dict(evaluation_role=p.ROLE,numeric_seeds=[401,503,607])
    return config,p.make_rows(config)


def test_unique_sources_expand_to_exact_matched_logical_grid(bank):
    config,rows=bank;logical=p.analysis_rows(rows)
    assert len(rows)<6912 and len(logical)==6912
    assert len({row['source'] for row in rows})==len(rows)
    assert len({row['id'] for row in rows})==len(rows)
    assert len({row['id'] for row in logical})==6912
    assert {row['source_id'] for row in logical}=={row['id'] for row in rows}
    paired=defaultdict(list)
    for row in logical:paired[row['paired_group_id']].append(row)
    assert len(paired)==288
    for values in paired.values():
        assert len(values)==24 and {row['form'] for row in values}==set(p.FORMS)
        assert {row['question'] for row in values}==set(p.QUESTIONS)
        assert len({row['expected_answer'] for row in values})==1


def test_all_topologies_forms_sign_mirrors_and_names_stay_in_root_order_cluster(bank):
    _,rows=bank;groups=defaultdict(list)
    for row in p.analysis_rows(rows):groups[row['root_order_cluster']].append(row)
    assert len(groups)==24
    split_counts=defaultdict(int)
    for group in groups.values():
        assert len({row['split'] for row in group})==1
        assert {row['chain_depth'] for row in group}=={0,1,2,4}
        assert {row['numeric_seed'] for row in group}=={401,503,607}
        assert {row['answer_sign'] for row in group}=={-1,1}
        assert {row['lexical_realization'] for row in group}=={0,1}
        split_counts[group[0]['split']]+=1
    assert dict(split_counts)=={'train':12,'development':12}


def test_full_root_leaf_share_body_answer_and_target_root_survives(bank):
    _,rows=bank;groups=defaultdict(dict)
    for row in p.analysis_rows(rows):
        if row['question'].startswith('full_'):groups[row['paired_group_id'],row['form'],row['chain_depth']][row['question']]=row
    for group in groups.values():
        root,leaf=group['full_root'],group['full_leaf']
        assert root['source'].rsplit('\n',1)[0]==leaf['source'].rsplit('\n',1)[0]
        assert root['expected_answer']==leaf['expected_answer']
        tree=ast.parse(root['source']);names=[s.targets[0].id for s in tree.body[:-1]]
        assert len(names)==8 and len(set(names))==8
        assert isinstance(tree.body[-1].value,ast.Name)
        assert tree.body[-1].value.id==names[0]  # Queried root is first and never overwritten.
        leaf_name=ast.parse(leaf['source']).body[-1].value.id
        assert leaf_name==names[-1]


def test_forms_preserve_all_numeric_states_and_match_operator_operand_signs(bank):
    _,rows=bank;groups=defaultdict(dict)
    for row in p.analysis_rows(rows):groups[row['paired_group_id'],row['question'],row['chain_depth']][row['form']]=row
    for forms in groups.values():
        traces=[[point['values'] for point in row['execution_trace']] for row in forms.values()]
        assert all(trace==traces[0] for trace in traces)
        small,cancel=forms['small'],forms['cancellation']
        a=ast.parse(small['source']).body[0].value;b=ast.parse(cancel['source']).body[0].value
        assert type(a.op)==type(b.op)
        small_terms=[ast.literal_eval(a.left),ast.literal_eval(a.right)]
        large_terms=[ast.literal_eval(b.left),ast.literal_eval(b.right)]
        assert [value>0 for value in small_terms]==[value>0 for value in large_terms]
        assert all(abs(value)<=16 for value in small_terms)
        assert all(13<=abs(value)<=32 for value in large_terms)
        for row in (small,cancel):
            literal_magnitudes={node.value for node in ast.walk(ast.parse(row['source'])) if isinstance(node,ast.Constant)}
            assert abs(row['expected_answer']) not in literal_magnitudes


def test_only_literal_isolated_controls_may_be_shared_across_splits(bank):
    _,rows=bank;shared=0;canonical_splits=defaultdict(set)
    for row in rows:
        splits={member['split'] for member in row['logical_memberships']}
        assert row['logical_splits']==sorted(splits)
        if len(splits)>1:
            shared+=1
            assert row['form']=='literal' and row['question']=='arithmetic_only'
            assert row['shared_control_across_splits']
        if row['form']!='literal':
            canonical_splits[ast.dump(ast.parse(row['canonical_source']))].update(splits)
    assert shared>0 and all(len(splits)==1 for splits in canonical_splits.values())


def test_sign_mirror_arithmetic_uses_exact_mirrored_operands(bank):
    _,rows=bank;groups=defaultdict(dict)
    for row in p.analysis_rows(rows):
        if row['question']=='arithmetic_only' and row['form']!='literal':
            key=(row['root_order_cluster'],row['numeric_seed'],row['lexical_realization'],row['form'])
            groups[key][row['answer_sign']]=row
    for pair in groups.values():
        positive,negative=pair[1],pair[-1]
        a=ast.parse(positive['source']).body[0].value;b=ast.parse(negative['source']).body[0].value
        assert ast.literal_eval(a.left)==-ast.literal_eval(b.left)
        assert ast.literal_eval(a.right)==-ast.literal_eval(b.right)
        assert positive['expected_answer']==-negative['expected_answer']


def test_validation_and_prospective_source_support(bank):
    config,rows=bank;review=p._validation(rows,config)
    assert review['logical_rows']==6912 and review['root_order_clusters']==24
    assert review['source_support_minimum']>=24
    assert not review['independent_python_passed']
    assert p.validate_rows(rows) is rows
    changed=deepcopy(rows);changed[0]['logical_memberships'][0]['chain_depth']=99
    with pytest.raises(ValueError,match='deterministic'):p.validate_rows(changed)


def test_independent_python_root_and_leaf_arithmetic_examples(bank):
    _,rows=bank
    chosen=[]
    for form in p.FORMS:
        for question in p.QUESTIONS:
            row=next(row for row in rows if row['form']==form and row['question']==question)
            chosen.append(row['source'])
    for source,result in zip(chosen,python_oracle(chosen)):
        truth=execute(source)
        assert result['answer']==truth['expected_answer']
        assert result['trace']==[point['values'] for point in truth['execution_trace']]


@pytest.mark.parametrize('raw,valid',[(' -12\n',True),('+3',True),('3.0',False),('Answer: 3',False),('٣',False),('3 words',False),('',False)])
def test_scoring_uses_whole_ascii_integer(raw,valid):
    result=p.score_case({'record':{'expected_answer':3}},raw)
    assert result['valid']==valid
    assert result['correct']==(raw=='+3')


def test_three_native_direct_instructions_render_printed_source(bank):
    _,rows=bank
    class Tokenizer:
        def apply_chat_template(self,messages,**kwargs):
            assert kwargs==dict(tokenize=False,continue_final_message=True)
            assert messages[-1]==dict(role='assistant',content='Output:\n')
            self.messages=messages
            return messages[0]['content']+'\n'+messages[-1]['content']
    tokenizer=Tokenizer();texts=[]
    for variant in p.INSTRUCTIONS:
        assert p.instruction_spec(variant)==dict(max_new_tokens=16,stop_at_blank_line=True,answer_mode='integer')
        text,source=p.prompt(tokenizer,rows[0],variant)
        assert '```python' in text and source.splitlines()[-1].startswith('print(')
        texts.append(text)
    assert len(set(texts))==3
    with pytest.raises(ValueError):p.instruction_spec('unknown')


def test_prior_source_audit_reports_literal_control_reuse_and_rejects_noncontrol_overlap(bank,tmp_path):
    config,rows=bank;path=tmp_path/'prior.jsonl'
    control=next(row for row in rows if row['form']=='literal' and row['question']=='arithmetic_only')
    path.write_text(json.dumps({'source':control['source'],'evaluation_role':'discovery_sources'})+'\n')
    review=p._exclusions(dict(config,exclude_datasets=[str(path)]),rows)
    assert review[0]['literal_control_repetitions']==1 and review[0]['noncontrol_overlaps']==0
    other=next(row for row in rows if row['question']=='full_leaf')
    path.write_text(json.dumps({'source':other['source'],'evaluation_role':'discovery_sources'})+'\n')
    with pytest.raises(ValueError,match='prior completed'):p._exclusions(dict(config,exclude_datasets=[str(path)]),rows)


@pytest.mark.parametrize('problem',['role','seeds','bool_seed','extra','exclusion_type'])
def test_generation_contract_rejects_unregistered_or_reserved_requests(problem):
    config=dict(evaluation_role=p.ROLE,numeric_seeds=[401,503,607])
    if problem=='role':config['evaluation_role']='sealed_final_sources'
    elif problem=='seeds':config['numeric_seeds']=[1,2]
    elif problem=='bool_seed':config['numeric_seeds']=[1,2,True]
    elif problem=='extra':config['model']='not-used'
    else:config['exclude_datasets']={'not':'a source list'}
    with pytest.raises(ValueError):p.make_rows(config)
