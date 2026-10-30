from copy import deepcopy
import json

import pytest

from codecue.binding.published_benchmarks import sha
from codecue.binding.timing_and_copy import make_rows, validate, validate_layouts, paired_answer_patterns
from codecue.binding.value_transfer import make_rows as literal_rows


def config(tmp_path,assay):
    anchor=tmp_path/'anchors.json'
    records=literal_rows({'generation':{'strides':[1]}})
    anchor.write_text(json.dumps(dict(cases={r['id']:dict(record=r) for r in records})))
    return dict(assay=assay,generation=dict(anchor_prepared=str(anchor),anchor_prepared_sha256=sha(anchor)))


@pytest.mark.parametrize('assay,n,pairs',[('query_timing',2592,0),('copy_path',1944,2592)])
def test_study_semantics_are_independently_verified_without_selecting_correct_cases(tmp_path,assay,n,pairs):
    cfg=config(tmp_path,assay);rows=make_rows(cfg)
    assert len(rows)==n
    checked=validate(cfg,rows,independent=True)
    assert len(checked)==pairs
    assert {r['instruction'] for r in rows}=={0,1,2}
    assert {r['lexical_realization'] for r in rows}=={0,1}
    if checked:
        assert {r['transformation'] for r in checked}=={'reordered','renamed'}
        assert {r['reverse'] for r in checked}=={False,True}
        assert all(not r['affected'] for r in checked)
    corrupt=deepcopy(rows);corrupt[0]['expected_answer']+=1
    with pytest.raises(ValueError,match='registered'):
        validate(cfg,corrupt)


def test_timing_requires_identical_token_bags_and_capture_positions():
    def case(form,tokens):
        return dict(record=dict(anchor_id='a',instruction=0,source_form=form),input_token_ids=tokens,positions=[1,2,0,4])
    cases={'early':case('early',[9,1,2,8,3]),'late':case('late',[8,1,2,9,3])}
    validate_layouts({'assay':'query_timing'},cases,[])
    cases['late']['input_token_ids'][-1]=4
    with pytest.raises(ValueError,match='token multiset'):
        validate_layouts({'assay':'query_timing'},cases,[])


def test_copy_intervention_rejects_misaligned_semantic_donors():
    cases={'a':dict(input_token_ids=[0,1,2,3],positions=[1,2,0,3]),
           'b':dict(input_token_ids=[0,2,1,3],positions=[1,2,0,3])}
    pairs=[dict(recipient='a',donor='b',transformation='reordered')]
    validate_layouts({'assay':'copy_path'},cases,pairs)
    cases['b']['positions'][1]=3
    with pytest.raises(ValueError,match='capture positions'):
        validate_layouts({'assay':'copy_path'},cases,pairs)


def test_paired_outputs_distinguish_wrong_ownership_from_losing_a_value():
    cases={};baselines={}
    for index,(a,b,predictions) in enumerate([(9,5,(5,9)),(8,4,(8,8)),(7,3,(7,3))]):
        for query in (0,1):
            key=f'{index}:{query}'
            cases[key]=dict(record=dict(source=f'x = {a}\ny = {b}\n'+('x' if query==0 else 'y'),
                family='ownership',instruction=0,source_form='anchor',mapping=1,query=query,expected_answer=(a,b)[query]))
            baselines[key]=dict(prediction=predictions[query])
    counts=paired_answer_patterns(cases,baselines)
    assert {row['category']:row['n'] for row in counts}==dict(both_swapped=1,duplicate_query0_value=1,both_correct=1)


def test_paired_output_diagnostic_refuses_missing_query_relatives():
    case=dict(record=dict(source='x = 9\ny = 5\nx',family='ownership',instruction=0,source_form='anchor',mapping=1,query=0,expected_answer=9))
    with pytest.raises(ValueError,match='exactly both queries'):
        paired_answer_patterns({'a':case},{'a':dict(prediction=9)})
