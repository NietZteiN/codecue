import ast
import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import pytest

from codecue.binding.calibration import VARIANTS
from codecue.binding.datasets import read_jsonl
from codecue.binding.interpreter import python_oracle
from codecue.binding.ladder import build, load_plan, select_regime, validate_rows


@pytest.fixture(scope='module')
def ladder(tmp_path_factory):
    output = tmp_path_factory.mktemp('ladder')/'ladder.jsonl'
    plan_path = Path(__file__).resolve().parents[2]/'configs/binding/difficulty_ladder_plan.json'
    config = {'dataset':str(output), 'calibration':dict(ladder_plan=str(plan_path),
              ladder_plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest())}
    manifest = build(config)
    return config, manifest, read_jsonl(output), load_plan(config)


def responses(rows, plan, counts=None):
    result=[]
    counts=counts or {}
    seen=defaultdict(int)
    for variant in plan['variants']:
        for row in rows:
            key=(variant,row['style'],row['assignment_count'])
            index=seen[key];seen[key]+=1
            good=index<counts.get(key,12)
            prediction=row['expected_answer'] if good else row['expected_answer']+100
            raw=str(prediction) if VARIANTS[variant]['answer_mode']=='integer' else f'Computed.\nAnswer: {prediction}'
            result.append(dict(row,variant=variant,raw_response=raw,prediction=prediction,correct=good,invalid=False))
    return result


def usable_counts(variant='print_direct_v3', n=2):
    return {(variant,'computed_baseline',1):11,
            (variant,'independent_arithmetic',n):11,
            (variant,'reassigned_chain',n):8,(variant,'fresh_chain',n):9}


def test_ladder_matches_paths_and_arithmetic_while_separating_dependencies(ladder):
    config,manifest,rows,plan=ladder
    assert manifest['rows']==120 and manifest['independent_python_programs']==120
    assert {r['split'] for r in rows}=={'train'}
    groups=defaultdict(list)
    for row in rows:
        tree=ast.parse(row['source'])
        assert sum(isinstance(node,ast.BinOp) for node in ast.walk(tree))==row['assignment_count']
        groups[row['paired_group_id']].append(row)
    assert len(groups)==48
    for group in groups.values():
        assert len({tuple(p['value'] for p in r['execution_trace']) for r in group})==1
        if len(group)>1:
            by_style={r['style']:r for r in group}
            assert by_style['independent_arithmetic']['dependency_depth']==1
            assert by_style['fresh_chain']['dependency_depth']==group[0]['assignment_count']
    oracle=python_oracle([r['source'] for r in rows])
    assert [r['expected_answer'] for r in rows]==[r['answer'] for r in oracle]
    with pytest.raises(ValueError,match='immutable'):
        build(config)


def test_ladder_gate_requires_full_suite_and_prefers_direct_then_smallest(ladder):
    _,_,rows,plan=ladder
    counts=usable_counts()|usable_counts('print_direct_v3',4)|usable_counts('print_trace_long_v1',2)
    observed=responses(rows,plan,counts)
    decision=select_regime(rows,observed,plan)
    assert decision['selected']=={'variant':'print_direct_v3','assignment_count':2}
    assert len(decision['eligible'])==3
    assert select_regime(rows,observed[:-1],plan)['status']=='incomplete_no_selection'
    assert select_regime(rows,responses(rows,plan),plan)['status']=='stop_no_usable_regime'


@pytest.mark.parametrize('style,n,correct', [('computed_baseline',1,9),('independent_arithmetic',2,9),
                                          ('reassigned_chain',2,5),('fresh_chain',2,12)])
def test_ladder_gate_rejects_weak_arithmetic_floor_and_ceiling(ladder,style,n,correct):
    _,_,rows,plan=ladder
    counts=usable_counts();counts[('print_direct_v3',style,n)]=correct
    assert select_regime(rows,responses(rows,plan,counts),plan)['status']=='stop_no_usable_regime'


def test_ladder_gate_keeps_invalid_outputs_separate_and_checks_saved_scores(ladder):
    _,_,rows,plan=ladder
    observed=responses(rows,plan,usable_counts())
    row=next(r for r in observed if r['variant']=='print_direct_v3' and r['style']=='fresh_chain' and r['assignment_count']==2)
    row.update(raw_response='',prediction=None,invalid=True,correct=False)
    assert select_regime(rows,observed,plan)['status']=='stop_no_usable_regime'
    row['correct']=True
    with pytest.raises(ValueError,match='score mismatch'):
        select_regime(rows,observed,plan)


def test_ladder_rejects_test_outcomes_duplicate_ids_and_changed_plan(ladder):
    config,_,rows,plan=ladder
    observed=responses(rows,plan)
    with pytest.raises(ValueError,match='duplicate'):
        select_regime(rows,observed+[observed[0]],plan)
    observed[0]['split']='test'
    with pytest.raises(ValueError,match='score mismatch'):
        select_regime(rows,observed,plan)
    altered=deepcopy(rows);altered[0]['dependency_depth']=99
    with pytest.raises(ValueError,match='metadata mismatch'):
        validate_rows(altered,plan)
    changed=deepcopy(config);changed['calibration']['ladder_plan_sha256']='changed'
    with pytest.raises(ValueError,match='checksum mismatch'):
        load_plan(changed)


def test_ladder_runner_and_analysis_preserve_both_protocols_without_real_model(ladder,tmp_path,monkeypatch):
    import torch
    from types import SimpleNamespace
    from codecue import models
    from codecue.binding import model_adapter
    from codecue.binding.calibration import run
    from codecue.binding.ladder import analyze
    config,_,_,plan=ladder
    effective=deepcopy(config)
    effective.update(run_dir=str(tmp_path/'software_run'),model='software_only',model_revision='a'*40,
                     tokenizer_revision='a'*40,device='cpu',dtype='float32',protocol='short_answer_prefill_v2',
                     max_gpu_seconds=30,batch_size=4,software_test_only=True)
    effective['calibration'].update(case_source='difficulty_ladder',variants=plan['variants'])
    class Tokenizer:
        bos_token_id=1
        def apply_chat_template(self,messages,**kwargs):
            return str(messages)
        def __call__(self,text,**kwargs):
            return {'input_ids':[1,2,3]}
    monkeypatch.setattr(model_adapter,'load',lambda cfg:(Tokenizer(),SimpleNamespace(parameters=lambda:iter([torch.zeros(1)]))))
    calls=[]
    def generate(tok,model,prompts,max_new_tokens,batch_size,stop_at_blank_line):
        calls.append((max_new_tokens,stop_at_blank_line))
        return [('0' if max_new_tokens==16 else 'Answer: 0') for _ in prompts]
    monkeypatch.setattr(models,'generate_free',generate)
    summary=run(effective)
    assert summary['complete'] and [r['n'] for r in summary['variants']]==[120,120]
    assert set(calls)=={(16,True),(512,False)}
    decision=analyze(effective)
    assert decision['queries_completed']==240 and decision['status']=='stop_no_usable_regime'
    assert all(row['correct']==4 for row in decision['cells'])
    with pytest.raises(ValueError,match='immutable'):
        analyze(effective)
