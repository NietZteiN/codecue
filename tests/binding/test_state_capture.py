from copy import deepcopy

import numpy as np
import pytest

from codecue.binding.checkpoint_suite import score_case
from codecue.binding.datasets import digest
from codecue.binding.state_capture import validate_chunk


def fixture():
    expected=[];rows=[]
    for query in ('current','saved'):
        record=dict(id=query,base_id='base',template_id='structure',split='train',condition='neutral',
                    lexical_realization=0,available_bindings=2,updates=1,tail_placement='before',
                    query_role=query,expected_answer=2 if query=='current' else 3,error_alternatives=[])
        case=dict(record=record,kind='competition',variant='print_direct_v3',input_token_ids=[1,2,3])
        item=dict(case=case,targets=[2,3],positions=[0,2],state_prefix_sha256='prefix',visible_prefixes=['state','query'])
        row={k:record[k] for k in ('id','base_id','template_id','split','condition','lexical_realization',
                                  'available_bindings','updates','tail_placement','query_role')}
        raw=str(record['expected_answer'])
        row.update(targets=item['targets'],positions=item['positions'],state_prefix_sha256='prefix',
                   visible_prefixes=item['visible_prefixes'],input_token_ids_sha256=digest([1,2,3]),
                   raw_response=raw,output_token_ids=[4],score=score_case(case,raw))
        expected.append(item);rows.append(row)
    return dict(layers=[8,16,24],hidden_size=4),expected,np.ones((2,3,2,4)),rows


def test_capture_contract_checks_every_query_relative_and_label():
    cfg,expected,features,rows=fixture()
    validate_chunk(cfg,expected,features,rows)
    with pytest.raises(ValueError,match='coverage'):
        validate_chunk(cfg,expected[:1],features,rows)


def test_pre_answer_positive_control_requires_actual_greedy_token_agreement():
    cfg,expected,features,rows=fixture()
    cfg.update(sites=['pre_query_state','after_query','pre_answer'],verify_first_token=True)
    features=np.ones((2,3,3,4))
    for item,row in zip(expected,rows):
        item['positions']=[0,2,2];item['visible_prefixes']=['state','query','answer']
        row.update(positions=item['positions'],visible_prefixes=item['visible_prefixes'],prefill_argmax_token=4,first_generation_token=4)
    validate_chunk(cfg,expected,features,rows)
    rows[0]['prefill_argmax_token']=5
    with pytest.raises(ValueError,match='prefill logits'):
        validate_chunk(cfg,expected,features,rows)


@pytest.mark.parametrize('change',['split','prefix','score','nonfinite','causal'])
def test_capture_audit_rejects_leakage_nonfinite_vectors_and_changed_scores(change):
    cfg,expected,features,rows=fixture()
    if change=='split':rows[0]['split']='development'
    elif change=='prefix':rows[0]['visible_prefixes']=['future answer','query']
    elif change=='score':rows[0]['score']['correct']=False
    elif change=='nonfinite':features[0,0,0,0]=np.nan
    else:features[1,0,0,0]=2
    with pytest.raises(ValueError):validate_chunk(cfg,expected,features,rows)
