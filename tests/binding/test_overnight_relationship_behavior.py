from pathlib import Path
from types import SimpleNamespace
import json

import pytest

from codecue.binding import overnight_relationship_behavior as study
from codecue.binding.interpreter import execute


def cases(groups=9):
    result=[]
    for group in range(groups):
        for form in ('literal','computed'):
            expressions=['2','3','4','5'] if form=='literal' else ['15 - 13','16 - 13','17 - 13','18 - 13']
            source='\n'.join([*(f'v{i} = {value}' for i,value in enumerate(expressions)),
                'v0 = v1','v1 = v0','v2 = v1','v3 = v2','v0'])
            result.append({'record':dict(id=f'{group}-{form}',component_id=f'g{group}',split='development',condition='neutral',
                numeric_seed=101,numeric_draw=0,source_form=form,query_slot=0,format_pair_id=f'pair{group}',canonical_source=source)})
    return result


def responses(selected):
    out=[]
    for case in selected:
        record=case['record'];truth=execute(record['canonical_source'])['expected_answer']
        text=str(truth if record['source_form']=='literal' else truth+1)
        row={key:record[key] for key in ('id','split','component_id','numeric_seed','numeric_draw','source_form','query_slot','format_pair_id')}
        row.update(raw_response=text,parsed=int(text),expected_answer=truth,correct=int(text)==truth,output_token_ids=[7,2]);out.append(row)
    return out


@pytest.mark.parametrize('text,expected',[(' -12\n',-12),('+03',3),('0',0),('Answer: 3',None),('3 4',None),('3.0',None),('',None),('٣',None)])
def test_exact_integer_parser(text,expected):assert study.parse_integer(text)==expected


def test_balanced_selection_requires_neutral_discovery():
    selected=cases();assert len(study.select(selected))==18
    selected[0]['record']['numeric_draw']=1;assert len(study.select(selected))==17
    selected[1]['record']['split']='final'
    with pytest.raises(ValueError):study.select(selected)


def test_matched_component_comparison_uses_nine_groups():
    result=study.summarize(responses(cases()))
    assert result['computed_literal']['mean']==-1
    assert result['computed_literal']['conditional_group_bootstrap_95']==[-1,-1]
    assert result['computed_literal']['matched_pairs']==9
    assert result['cells']['source_form/literal']['accuracy']==1
    with pytest.raises(ValueError):study.summarize(responses(cases(8)))


def test_response_resume_preserves_committed_prefix_and_backs_up_tail(tmp_path):
    selected=cases(1);rows=responses(selected);p=tmp_path/'responses.jsonl'
    prefix=(json.dumps(rows[0])+'\n').encode();damaged=prefix+b'{"id":'
    p.write_bytes(damaged)
    assert study.read_responses(p,selected,repair=True)==rows[:1]
    assert p.read_bytes()==prefix
    assert next(tmp_path.glob('responses_interrupted_*.bin')).read_bytes()==damaged
    with p.open('a') as stream:stream.write(json.dumps(rows[1])+'\n')
    assert study.read_responses(p,selected)==rows


def test_committed_corruption_or_changed_group_is_never_silently_repaired(tmp_path):
    selected=cases(1);rows=responses(selected);p=tmp_path/'responses.jsonl'
    p.write_text(json.dumps(rows[0])+'\ninvalid\n')
    with pytest.raises(ValueError):study.read_responses(p,selected,repair=True)
    rows[0]['component_id']='wrong';p.write_text(json.dumps(rows[0])+'\n')
    with pytest.raises(ValueError,match='identity'):study.read_responses(p,selected)


def test_response_resume_adds_missing_final_separator_without_queries(tmp_path):
    selected=cases(1);row=responses(selected)[0];p=tmp_path/'responses.jsonl';p.write_text(json.dumps(row))
    assert study.read_responses(p,selected,repair=True)==[row]
    assert p.read_bytes().endswith(b'\n')


def test_attempt_journal_is_mutable_and_does_not_rebuild_dashboard(tmp_path,monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log,'note_artifact',lambda *a,**k:pytest.fail('hot journal rebuilt dashboard'))
    p=tmp_path/'manifest.json';study._journal(p,{'attempted':0});study._journal(p,{'attempted':64})
    assert json.loads(p.read_text())=={'attempted':64}


def test_no_model_inputs_before_sbatch_guard(tmp_path,monkeypatch):
    config=dict(evaluation_role=study.ROLE,capture_config=str(tmp_path/'capture.json'),capture_config_sha256='a'*64,
        declared_plan=str(tmp_path/'plan.md'),declared_plan_sha256='b'*64,generation_batch_size=64,run_dir=str(tmp_path/'run'),report=str(tmp_path/'report.md'))
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    monkeypatch.setattr(study,'_inputs',lambda *a:pytest.fail('sources reached before scheduler guard'))
    with pytest.raises(ValueError,match='SLURM'):study.run(config)


def test_generation_uses_only_prepared_tokens_and_keeps_one_logit_position():
    import torch
    class Encoded(dict):
        def __getattr__(self,key):return self[key]
        def to(self,device):return self
    class Tokenizer:
        pad_token_id=0;eos_token_id=2
        def __call__(self,*a,**k):return Encoded(input_ids=torch.tensor([[5,6]]),attention_mask=torch.tensor([[1,1]]))
        def decode(self,ids,**k):return '7'
    class Model:
        device='cpu';generation_config=SimpleNamespace(eos_token_id=[2])
        def generate(self,**kwargs):
            assert kwargs['logits_to_keep']==1 and kwargs['use_cache'] and kwargs['max_new_tokens']==12
            assert kwargs['do_sample'] is False
            return torch.tensor([[5,6,7,2,0]])
    assert study._generate(Tokenizer(),Model(),[{'prompt':'prepared','input_token_ids':[5,6]}])==[('7',[7,2])]
    with pytest.raises(ValueError,match='tokens differ'):study._generate(Tokenizer(),Model(),[{'prompt':'prepared','input_token_ids':[6,5]}])
