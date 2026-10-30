from copy import deepcopy

import pytest

from codecue.binding.routing_extension import computed_rows, numeric_bank, validate, validate_layouts
from codecue.binding.value_transfer import qualification


def config():
    return dict(assay='computed_routing', generation=dict(seed=2026102604, numeric_groups=12))


def test_computed_counterfactuals_are_nonliteral_and_python_verified():
    cfg=config();rows=computed_rows(cfg)
    assert len(numeric_bank(cfg))==12
    assert len(rows)==576
    pairs=validate(cfg,rows,independent=True)
    assert len(pairs)==768 and sum(p['affected'] for p in pairs)==384
    assert {p['reverse'] for p in pairs}=={False,True}
    damaged=deepcopy(rows);damaged[0]['source']=damaged[0]['source'].replace(' + ',' - ',1)
    with pytest.raises(ValueError,match='registered'):
        validate(cfg,damaged)


def test_computed_site_must_be_unchanged_and_after_the_changed_operand():
    cases={'a':dict(input_token_ids=[0,1,2,3,4,5],positions=[2,4,0,5]),
           'b':dict(input_token_ids=[0,9,2,3,4,5],positions=[2,4,0,5])}
    pairs=[dict(recipient='a',donor='b',slot=0)]
    validate_layouts(config(),cases,pairs)
    cases['b']['input_token_ids']=[0,1,9,3,4,5]
    with pytest.raises(ValueError,match='unchanged token'):
        validate_layouts(config(),cases,pairs)


def test_reliability_gate_rejects_whole_family_when_one_cell_fails():
    cfg=dict(baseline_gate=dict(minimum_cell_n=24,minimum_accuracy=.9,maximum_invalid_rate=.05))
    cases={};baselines={}
    for family in ('ownership','versions'):
        for mapping in (0,1):
            for query in (0,1):
                for i in range(24):
                    key=f'{family}:{mapping}:{query}:{i}'
                    cases[key]=dict(record=dict(family=family,mapping=mapping,query=query))
                    baselines[key]=dict(correct=not(family=='ownership' and mapping==1 and query==1 and i<3),prediction=2)
    result=qualification(cfg,cases,baselines)
    assert result['eligible_families']==['versions']
    assert result['status']=='partial'
    assert sum(c['n'] for c in result['cells'])==len(cases)
    assert len(cases)==192  # The gate records failures; it does not discard cases.
    for key in baselines: baselines[key]['correct']=False
    assert qualification(cfg,cases,baselines)['status']=='failed'


def test_dead_reset_layout_targets_changed_identifier_itself():
    cases={'a':dict(input_token_ids=[0,1,2,3],positions=[1,2,0,3]),
           'b':dict(input_token_ids=[0,1,9,3],positions=[1,2,0,3])}
    pairs=[dict(recipient='a',donor='b',slot=1)]
    validate_layouts({'assay':'swap_reset'},cases,pairs)
    cases['b']['input_token_ids']=[0,9,2,3]
    with pytest.raises(ValueError,match='changed identifier'):
        validate_layouts({'assay':'swap_reset'},cases,pairs)
