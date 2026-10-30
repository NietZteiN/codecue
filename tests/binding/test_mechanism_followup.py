from copy import deepcopy
import json

import pytest

from codecue.binding import mechanism_followup as m
from codecue.binding import timing_and_copy as prior
from codecue.binding.interpreter import execute
from codecue.binding.published_benchmarks import sha
from codecue.binding.value_transfer import make_rows as old_rows


def config(tmp_path):
    anchor=tmp_path/'anchor.json'
    rows=old_rows({'generation':{'strides':[1]}})
    anchor.write_text(json.dumps(dict(cases={r['id']:dict(record=r) for r in rows})))
    return dict(assay='value_owner',generation=dict(anchor_prepared=str(anchor),anchor_prepared_sha256=sha(anchor)))


def test_fresh_complete_numeric_bank_and_full_state_counterfactuals(tmp_path):
    cfg=config(tmp_path);values=m.fresh_values(cfg)
    assert len(values)==36
    assert all((b,a) in values for a,b in values)
    rows=m.make_rows(cfg);pairs=m.validate(cfg,rows,independent=True)
    assert len(rows)==2592 and len(pairs)==1728
    assert sum(r['source_form']=='wrong_version' for r in rows)==864
    records={r['id']:r for r in rows}
    for p in pairs:
        r=records[p['recipient']];x,y,_=m.names(r);cf=p['counterfactuals']
        before=execute(r['source'])['execution_trace'][-1]['values']
        assert cf['first_copy']['final_state'][y]==before[y]
        assert cf['second_copy']['final_state'][x]==before[x]
        assert sorted(cf['both_copies']['final_state'].values())==sorted(before.values())
        if r['mapping']==1:
            assert cf['wrong_version']['final_state'][y]==before[y]
        if r['query']==0:
            assert cf['second_copy']['answer']==r['expected_answer']
        else:
            assert cf['first_copy']['answer']==r['expected_answer']
    corrupt=deepcopy(rows);corrupt[0]['source']+=' + 1'
    with pytest.raises(ValueError,match='registered complete design'):m.validate(cfg,corrupt)


def test_common_final_query_cross_retains_every_old_variant(tmp_path):
    cfg=config(tmp_path);old=prior.make_rows(dict(cfg,assay='query_timing'))
    path=tmp_path/'timing.json';path.write_text(json.dumps(dict(cases={r['id']:dict(record=r) for r in old})))
    cfg=dict(assay='cue_control',generation=dict(anchor_prepared=str(path),anchor_prepared_sha256=sha(path)))
    rows=m.make_rows(cfg)
    assert len(rows)==5184 and m.validate(cfg,rows)==[]
    assert {r['timing_anchor_id'] for r in rows if r['common_final_query']}=={r['id'] for r in old}
    assert {r['timing_anchor_id'] for r in rows if not r['common_final_query']}=={r['id'] for r in old}


def test_common_final_prompt_is_identical_for_both_timing_conditions():
    class Tokenizer:
        def apply_chat_template(self,messages,**kwargs):
            return messages[0]['content']+messages[1]['content']
    # normalize_prompt only needs the chat-template output to be a string here.
    from unittest.mock import patch
    row=dict(source='x = 1\ny = 2\nx',source_form='early',instruction=0)
    cfg=dict(assay='query_timing',answer_prefix_suffix=' ')
    with patch('codecue.binding.model_adapter.normalize_prompt',side_effect=lambda tok,text:text):
        original=prior.prompt(Tokenizer(),row,cfg)[0]
        unchanged=prior.prompt(Tokenizer(),dict(row,common_final_query=False),cfg)[0]
        early=prior.prompt(Tokenizer(),dict(row,common_final_query=True),cfg)[0]
        late=prior.prompt(Tokenizer(),dict(row,source_form='late',common_final_query=True),cfg)[0]
    assert original==unchanged
    assert early.split('Now give the requested value.')[1]==late.split('Now give the requested value.')[1]
    assert 'Final target: x. Give its final value.' in early


def test_two_site_controls_match_two_component_doses():
    assert m.patch_sites('both_copies')==[0,1]
    for seed in (11,29,47):assert m.patch_sites(f'random_both_{seed}')==[0,1]
    assert m.patch_sites('nearby_position')==[0]
    assert m.patch_sites('unrelated_position')==[2]
    assert m.patch_sites('wrong_version')==[1]


def test_chunk_guards_final_layer_causality_and_bf16_effective_norm():
    cfg=dict(norm_tolerance=.03)
    data=dict(cases={'r':dict(record=dict(expected_answer=2)),'d':dict(record=dict(expected_answer=7))})
    pair=dict(id='p',recipient='r',donor='d',counterfactuals={})
    replay={'p':dict(first_token=17)}
    row=dict(pair_id='p',layer=31,condition='unrelated_position',sites=[2],target_answer=2,
             norms=[1.02],reference_norms=[1.],target_logprob=-1.,donor_logprob=-2.,recipient_logprob=-1.,first_token=17)
    m.check_chunk(cfg,data,31,'unrelated_position',[pair],[row],replay,{})
    with pytest.raises(ValueError,match='norm matching'):
        m.check_chunk(cfg,data,31,'unrelated_position',[pair],[dict(row,norms=[1.05])],replay,{})
    with pytest.raises(ValueError,match='earlier-token patch changed'):
        m.check_chunk(cfg,data,31,'unrelated_position',[pair],[dict(row,first_token=22)],replay,{})
