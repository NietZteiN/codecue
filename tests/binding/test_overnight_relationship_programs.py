"""Deterministic grouped source cohorts, numeric uniqueness and paired semantics."""
import ast
from copy import deepcopy
from collections import Counter,defaultdict

import pytest

from codecue.binding import overnight_relationship_programs as study
from codecue.binding.interpreter import execute,python_oracle


def config(tmp_path,n=1):
    return dict(evaluation_role=study.ROLE,numeric_seeds=[101,211,307],numeric_instances=n,
        dataset=str(tmp_path/'union.jsonl'),review=str(tmp_path/'source_review.json'),report=str(tmp_path/'source.md'))


@pytest.fixture(scope='module')
def bank(tmp_path_factory):
    cfg=config(tmp_path_factory.mktemp('overnight_sources'))
    return cfg,study.make_rows(cfg)


def test_three_seed_union_covers_panels_without_duplicate_capture(bank):
    cfg,rows=bank
    assert len(rows)==7290 and len({row['id'] for row in rows})==7290
    assert Counter(row['source_form'] for row in rows)==dict(literal=5832,computed=1458)
    views=study.view_indices(rows)
    assert {key:value['rows'] for key,value in views.items()}==dict(numeric_replication=1458,query_twins=5832,computed_roots=1458)
    assert set(views['numeric_replication']['indices'])<=set(views['query_twins']['indices'])
    assert not set(views['computed_roots']['indices'])&set(views['numeric_replication']['indices'])
    assert set().union(*(set(view['indices']) for view in views.values()))==set(range(len(rows)))
    expected_indices=views['computed_roots']['matched_literal_indices']
    for ci,li in zip(views['computed_roots']['indices'],expected_indices):
        assert rows[ci]['format_pair_id']==rows[li]['format_pair_id']
        assert rows[ci]['source_form']=='computed' and rows[li]['source_form']=='literal'
        assert rows[ci]['root_values']==rows[li]['root_values']


def test_initial_states_are_globally_unique_by_numeric_base_and_stay_in_structural_split(bank):
    _,rows=bank
    states=defaultdict(set);base_splits=defaultdict(set);components=defaultdict(set)
    for row in rows:
        states[tuple(row['root_values'])].add(row['base_id']);base_splits[row['base_id']].add(row['split'])
        components[row['split']].add(row['component_id'])
        assert row['template_id']==row['cluster_id']==row['component_id']
    assert len(states)==243 and all(len(bases)==1 for bases in states.values())
    assert all(len(splits)==1 for splits in base_splits.values())
    assert {key:len(value) for key,value in components.items()}==dict(train=18,development=9)
    assert not components['train']&components['development']


def test_computed_root_operands_exclude_all_target_magnitudes_and_preserve_every_state(bank):
    _,rows=bank;views=study.view_indices(rows)
    operator_counts=Counter()
    for ci,li in zip(views['computed_roots']['indices'],views['computed_roots']['matched_literal_indices']):
        computed,literal=rows[ci],rows[li];operands=[]
        for expr in computed['root_expressions']:
            node=ast.parse(expr,mode='eval').body
            assert isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub))
            operator_counts[type(node.op).__name__]+=1
            operands.extend([ast.literal_eval(node.left),ast.literal_eval(node.right)])
        assert not {abs(value) for value in computed['root_values']} & {abs(value) for value in operands}
        assert all(13<=abs(value)<=32 for value in operands)
        assert computed['parent_slots']==literal['parent_slots']
        assert computed['expected_answer']==literal['expected_answer']
        assert [point['values'] for point in computed['execution_trace']]==[point['values'] for point in literal['execution_trace']]
    assert set(operator_counts)=={'Add','Sub'}


def test_query_twins_have_identical_bodies_and_actual_query_answers(bank):
    _,rows=bank;groups=defaultdict(list)
    for row in rows:
        if 'query_twins' in row['cohorts']:groups[row['surface_body_id']].append(row)
    assert len(groups)==1458
    distinct_answers=0
    for siblings in groups.values():
        assert {row['query_slot'] for row in siblings}=={0,1,2,3}
        assert len({row['source'].rsplit('\n',1)[0] for row in siblings})==1
        assert len({row['base_id'] for row in siblings})==1
        assert all(row['execution_trace']==siblings[0]['execution_trace'] for row in siblings)
        for row in siblings:
            assert row['query_role']==f'v{row["query_slot"]}'
            assert row['expected_answer']==row['execution_trace'][-1]['values'][row['query_role']]
        distinct_answers+=len({row['expected_answer'] for row in siblings})>1
    assert distinct_answers>0


def test_independent_ordinary_python_checks_computed_and_query_examples(bank):
    _,rows=bank
    selected=[rows[0]['canonical_source'],rows[1]['canonical_source'],rows[2]['canonical_source'],rows[3]['source']]
    for source,ordinary in zip(selected,python_oracle(selected)):
        truth=execute(source)
        assert ordinary['answer']==truth['expected_answer']
        assert ordinary['trace']==[point['values'] for point in truth['execution_trace']]


def test_validator_checks_full_factorial_and_rejects_tampered_source_metadata(bank):
    cfg,rows=bank
    review=study.validate_rows(cfg,rows)
    assert review['rows']==7290 and review['globally_unique_initial_states']==243
    assert review['computed_rows_with_all_target_magnitudes_absent']==1458
    assert not review['independent_python_passed']
    changed=deepcopy(rows);changed[0]['query_slot']=3
    with pytest.raises(ValueError,match='deterministic'):study.validate_rows(cfg,changed)


@pytest.mark.parametrize('problem',['role','too_few_seeds','duplicate_seed','bool_seed','too_many_draws','extra','same_path'])
def test_configuration_role_seed_count_domain_and_output_guards(tmp_path,problem):
    cfg=config(tmp_path)
    if problem=='role':cfg['evaluation_role']='sealed_final_sources'
    elif problem=='too_few_seeds':cfg['numeric_seeds']=[101,211]
    elif problem=='duplicate_seed':cfg['numeric_seeds']=[101,101,307]
    elif problem=='bool_seed':cfg['numeric_seeds']=[101,True,307]
    elif problem=='too_many_draws':cfg['numeric_instances']=5
    elif problem=='extra':cfg['model']='never-load'
    else:cfg['review']=str(tmp_path/'union.manifest.json')
    with pytest.raises(ValueError):study.make_rows(cfg)


def test_global_collision_rejection_is_deterministic_and_stays_in_stratum(tmp_path):
    cfg=config(tmp_path)
    raw=study.algebraic.make_rows(dict(evaluation_role=study.algebraic.ROLE,seed=101,numeric_instances=1,
        dataset=cfg['dataset'],review=cfg['review'],report=cfg['report']))
    first=raw[0];values=tuple(first['targets']['initial_values'])
    a=study._numeric_state(101,first,1,{values});b=study._numeric_state(101,first,1,{values})
    assert a==b and a[0]!=values and a[2]>=1
    stratum=first['targets']['numeric_stratum'];x,y,z,d=a[0]
    if stratum=='distinct_uniform':assert len({x,y,z,d})==4
    elif stratum=='additive_triplet':assert x+y==z and len({x,y,z,d})==4
    else:assert y==z and len({x,y,d})==3
