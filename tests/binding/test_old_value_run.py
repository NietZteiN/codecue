from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest

from codecue.binding import old_value_run as study
from codecue.binding.datasets import digest


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


@pytest.fixture
def assay(tmp_path,monkeypatch):
    variants=('old_value_output_v1','old_value_execute_v1','old_value_history_v1')
    programs=SimpleNamespace(ROLE='discovery_old_value_sources_v1',INSTRUCTIONS=dict.fromkeys(variants),
        validate_rows=lambda rows:rows,analysis_rows=lambda rows:rows,
        instruction_spec=lambda variant:dict(max_new_tokens=16))
    monkeypatch.setattr(study._CORE,'_programs',lambda:programs)
    source=dict(snapshot='fake-frozen-source',snapshot_id='f'*24,source_sha256='a'*64,frozen_manifest_sha256='b'*64)
    monkeypatch.setattr(study._CORE.base,'_current_source',lambda cfg:source)
    monkeypatch.setattr(study._CORE.base,'_verify_source',lambda cfg,saved:saved==source or (_ for _ in ()).throw(ValueError('source changed')))
    monkeypatch.setenv('SLURM_JOB_ID','12345')
    monkeypatch.setattr(study._CORE.suite,'configure_runtime',lambda cfg:None)
    rows=[]
    for split in study.SPLITS:
        for category in study.STORAGE:
            for index in range(24):
                old=index+1;current=old if category=='equal_current' else -old
                body=f'x = {old}\ny = {current}\nx = y # {split}/{category}/{index}'
                for mode,answer in [('previous',old),('current',current)]:
                    rows.append(dict(id=f'{split}/{category}/{index}/{mode}',pair_id=f'{split}/{category}/{index}',
                        evaluation_role=programs.ROLE,split=split,body=body,source=body+'\nx',
                        oracle_source=f'x = {answer}\nx',query_mode=mode,old_storage=category,
                        expected_answer=answer,component_id=f'{split}/graph{index%6}',target_slot=index%4,
                        target_update_count=1+index%3,last_write_lag=index%4,lexical_realization=index%2,
                        profile_id=['2_1_1_0','3_1_0_0','2_2_0_0'][index%3],numeric_seed=[1151,1297,1459][index%3]))
    dataset=tmp_path/'dataset.jsonl';dataset.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    put(dataset.with_suffix('.manifest.json'),dict(rows=len(rows),sha256=study._CORE.base._sha(dataset),
        evaluation_role=programs.ROLE,status='complete',independent_python_passed=True,generated_holdouts_opened=False))
    plan=tmp_path/'plan.md';plan.write_text('Fixed prospective history/current calibration.\n')
    runtime=tmp_path/'runtime.json';put(runtime,{})
    out=tmp_path/'run'
    cfg=dict(evaluation_role=study.ROLE,dataset=str(dataset),dataset_sha256=study._CORE.base._sha(dataset),
        dataset_manifest_sha256=study._CORE.base._sha(dataset.with_suffix('.manifest.json')),
        declared_plan=str(plan),declared_plan_sha256=study._CORE.base._sha(plan),
        model='meta-llama/Llama-3.1-8B-Instruct',model_revision=study.MODELS['meta-llama/Llama-3.1-8B-Instruct'],
        tokenizer_revision=study.MODELS['meta-llama/Llama-3.1-8B-Instruct'],device='cuda',dtype='bfloat16',context_limit=2048,
        sections=[dict(name='computation_routing',kind='computation_routing',dataset=str(dataset),sha256=study._CORE.base._sha(dataset),variants=list(variants))],
        run_dir=str(out),report=str(tmp_path/'report.md'),review_artifact=str(out/'review_v1.json'),
        prepared_cases=str(out/'prepared.jsonl'),preflight_result=str(out/'preflight.json'),
        runtime_manifest=str(runtime),runtime_manifest_sha256=study._CORE.base._sha(runtime),
        cuda_home='/usr/local/cuda-12.9',engine={},request_chunk_size=256,eos_token_ids=[128009],
        reliability_gate=deepcopy(study.THRESHOLDS),bootstrap_replicates=2000,bootstrap_seed=913,
        max_new_tokens=dict.fromkeys(variants,16))
    def score(case,raw):
        pred=int(raw) if re.fullmatch(r'\s*[+-]?\d+\s*',raw,flags=re.ASCII) else None
        return dict(prediction=pred,valid=pred is not None,correct=pred==case['record']['expected_answer'])
    monkeypatch.setattr(study._CORE.suite,'score_case',score)
    def prep(config):
        cases=[]
        for variant in variants:
            for row in rows:
                prompt=variant+' '+row['body']+' '+row['query_mode']
                cases.append(dict(section='computation_routing',kind='computation_routing',task=variant,
                    variant=variant,id=row['id'],record=row,prompt=prompt,prompt_sha256=digest(prompt),
                    input_token_ids=[1,len(cases)+2],max_new_tokens=16,stop=['\n\n']))
        p=Path(config['prepared_cases']);p.parent.mkdir(parents=True,exist_ok=True)
        study._CORE.base._publish(p,''.join(json.dumps(case,sort_keys=True)+'\n' for case in cases).encode())
        qa=dict(status='passed',config_hash=digest(config),source_sha256=source['source_sha256'],cases=len(cases),
            prepared_cases_sha256=study._CORE.base._sha(p),model_inference=False,generated_holdouts_opened=False)
        put(config['preflight_result'],qa);return qa
    monkeypatch.setattr(study._CORE.suite,'preflight',prep)
    def response(case,raw=None):
        raw=str(case['record']['expected_answer']) if raw is None else raw
        row={k:case[k] for k in ('section','task','id','input_token_ids','prompt_sha256')}
        row.update(record_sha256=digest(case['record']),raw_response=raw,output_token_ids=[9],finish_reason='stop',score=score(case,raw))
        return row
    calls=[]
    def backend(config):
        calls.append('run');_,cases=study._CORE.suite.prepared(config,source['source_sha256'])
        stage=Path(config['run_dir'])/'checkpoint_suite';stage.mkdir(parents=True,exist_ok=True)
        existing=study._CORE._responses(config,cases)
        with (stage/'responses.jsonl').open('a') as stream:
            for case in cases[len(existing):]:stream.write(json.dumps(response(case))+'\n')
        observed=study._CORE._responses(config,cases);identity=dict(config=config,code=dict(source_sha256=source['source_sha256']))
        put(stage/'manifest.json',dict(status='complete',identity=identity,identity_hash=digest(identity),responses_sha256=study._CORE.base._sha(stage/'responses.jsonl'),attempts=[dict(slurm_job_id='12345',status='complete')]))
        summary=study._CORE.suite.summarize(observed,len(cases));summary.update(gpu={},timings=[])
        put(stage/'summary.json',summary);put(stage/'runtime.json',{});return summary
    monkeypatch.setattr(study._CORE.suite,'run',backend)
    return SimpleNamespace(config=cfg,source=source,rows=rows,prep=prep,response=response,calls=calls,variants=variants)


def test_adapter_is_private_and_legacy_sources_are_unmodified():
    from codecue.binding import checkpoint_suite,computation_routing_run
    assert study._CORE is not computation_routing_run and study._CORE.suite is not checkpoint_suite
    assert computation_routing_run.ROLE=='discovery_computation_routing_calibration_v1'
    assert study._CORE.suite.score_case.__globals__ is study._CORE.suite.__dict__
    path=Path(checkpoint_suite.__file__);payload=path.read_text()
    assert payload.count('from .computation_routing_programs import ')==4
    assert 'from .old_value_programs import ' not in payload


@pytest.mark.parametrize('problem',['role','thresholds','instructions','revision','source_collision','reserved_collision'])
def test_config_rejects_unsafe_or_changed_protocol(assay,problem):
    cfg=deepcopy(assay.config)
    if problem=='role':cfg['evaluation_role']='final_test'
    elif problem=='thresholds':cfg['reliability_gate']['minimum_accuracy']=.1
    elif problem=='instructions':cfg['sections'][0]['variants'].pop()
    elif problem=='revision':cfg['model_revision']='0'*40
    elif problem=='source_collision':cfg['report']=cfg['declared_plan']
    else:cfg['review_artifact']=str(Path(cfg['run_dir'])/'routing_completion_v1.json')
    with pytest.raises(ValueError):study.metadata(cfg)


@pytest.mark.parametrize('name',['plan','dataset','manifest','runtime'])
def test_metadata_pin_failure_precedes_native_preparation(assay,name):
    cfg=assay.config
    p=Path({'plan':cfg['declared_plan'],'dataset':cfg['dataset'],'manifest':str(Path(cfg['dataset']).with_suffix('.manifest.json')),'runtime':cfg['runtime_manifest']}[name]);p.write_text(p.read_text()+' ')
    with pytest.raises(ValueError):study.preflight(cfg)
    assert not Path(cfg['prepared_cases']).exists()


def test_preparation_requires_sbatch_and_reuses_committed_native_artifacts(assay,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID')
    with pytest.raises(ValueError,match='SLURM'):study.preflight(assay.config)
    monkeypatch.setenv('SLURM_JOB_ID','12345');first=study.preflight(assay.config)
    monkeypatch.setattr(study._CORE.suite,'preflight',lambda cfg:(_ for _ in ()).throw(AssertionError('native preparation repeated')))
    assert study.preflight(assay.config)==first


def test_source_pairs_and_primary_cell_completeness_rejected_before_inference(assay):
    rows=deepcopy(assay.rows);rows[0]['body']+='\nx = 9'
    with pytest.raises(ValueError,match='share body'):study._cohort(rows)
    rows=[r for r in assay.rows if not(r['split']=='train' and r['old_storage']=='absent_all_current')]
    with pytest.raises(ValueError,match='primary source cell'):study._cohort(rows)


def test_complete_run_and_audit_replay_without_model_call(assay,monkeypatch):
    study.preflight(assay.config);first=study.run(assay.config)
    assert first['n']==len(assay.rows)*3 and first['unique_sources']==len(assay.rows)
    assert len(first['gate_cells'])==24 and len(first['equality_control_cells'])==12
    assert first['reliability_gate']['status']=='passed' and first['reliability_gate']['automatic_causal_launch'] is False
    assert first['accounting']['confirmed_warmup_requests']==8 and first['new_model_queries']==len(assay.rows)*3+8
    assert all(c['previous_minus_current']==0 for c in first['paired_contrasts'])
    monkeypatch.setattr(study._CORE.suite,'run',lambda cfg:(_ for _ in ()).throw(AssertionError('model repeated')))
    assert study.run(assay.config)==first and study.audit(assay.config)==first
    assert assay.calls==['run']


def test_invalid_old_answers_count_wrong_and_no_instruction_is_selected(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    records=[]
    for case in cases:
        raw='not an integer' if case['variant']==assay.variants[0] and case['record']['query_mode']=='previous' else None
        records.append((case,assay.response(case,raw)))
    result=study.summarize(records,assay.config)
    assert result['reliability_gate']['status']=='failed'
    assert result['reliability_gate']['instructions'][assay.variants[0]]['behavioral_calibration_qualified'] is False
    assert all(result['reliability_gate']['instructions'][v]['behavioral_calibration_qualified'] for v in assay.variants[1:])
    assert result['invalid']>0 and all('confidence_interval' in p and p['confidence_interval'] is None for p in result['paired_contrasts'])
    assert result['reliability_gate']['causal_design_review_required'] is True


def test_equality_controls_do_not_rescue_different_value_gate(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    records=[(case,assay.response(case,'999' if case['record']['old_storage'] in study.PRIMARY_STORAGE else None)) for case in cases]
    result=study.summarize(records,assay.config)
    assert result['reliability_gate']['status']=='failed'
    assert all(c['accuracy']==1 for c in result['equality_control_cells'])
    assert all(c['accuracy']==0 for c in result['gate_cells'])


def test_extra_duplicate_or_changed_response_identity_rejected(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    records=[(case,assay.response(case)) for case in cases]
    with pytest.raises(ValueError,match='unique'):study.summarize(records+[records[0]],assay.config)
    bad=deepcopy(records);bad[0][1]['score']['correct']=False
    with pytest.raises(ValueError,match='identity.*score'):study.summarize(bad,assay.config)
    with pytest.raises(ValueError,match='coverage'):study.summarize(records[:-1],assay.config)


def test_interrupted_response_tail_is_preserved_and_repaired(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    stage=Path(assay.config['run_dir'])/'checkpoint_suite';stage.mkdir()
    p=stage/'responses.jsonl';good=(json.dumps(assay.response(cases[0]))+'\n').encode();p.write_bytes(good+b'{"unfinished":')
    restored=study._responses(assay.config,cases,repair=True)
    assert len(restored)==1 and p.read_bytes()==good and len(list(stage.glob('responses_interrupted_*.bin')))==1


def test_comparison_keeps_graph_macro_and_row_average_separate(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    records=[(case,assay.response(case)) for case in cases]
    result=study.summarize(records,assay.config)
    assert all(c['group_macro_accuracy']==1 for c in result['gate_cells'])
    assert {cell['axis'] for cell in result['descriptive_cells']}=={'target_slot','target_update_count','last_write_lag','lexical_realization','profile_id','numeric_seed'}
    assert all(c['group_macro_previous_minus_current']==0 for c in result['paired_contrasts'])


def test_previous_current_answer_intrusions_and_paired_partition_are_explicit(assay):
    study.preflight(assay.config);_,cases=study._CORE.suite.prepared(assay.config,assay.source['source_sha256'])
    current={row['pair_id']:row['expected_answer'] for row in assay.rows if row['query_mode']=='current'}
    records=[(case,assay.response(case,str(current[case['record']['pair_id']]) if case['record']['query_mode']=='previous' else None)) for case in cases]
    result=study.summarize(records,assay.config)
    for pair in result['paired_contrasts']:
        events=pair['paired_outcomes']
        assert sum(events[name] for name in ['both_correct','previous_only_correct','current_only_correct','neither_correct'])==pair['paired_n']
        if pair['old_storage']=='equal_current':
            assert events['both_correct']==pair['paired_n'] and events['previous_answered_current']==0
        else:
            assert events['current_only_correct']==events['previous_answered_current']==pair['paired_n']
            assert events['current_answered_previous']==events['invalid_previous']==0


def test_private_backend_scores_historical_truth_while_prompt_keeps_full_body():
    from codecue.binding import old_value_programs as programs
    from codecue.binding.interpreter import execute
    destinations=[1,2,3,1];parents=[0,1,2,0]
    graph=programs._graph(tuple(destinations),tuple(parents))
    template=dict(canonical_graph_sha256=graph,component_id='graph:'+graph,split='train',profile_id='2_1_1_0')
    previous=programs._row(template,programs.NUMERIC_SEEDS[0],0,0,[1,2,3,4],destinations,parents,2,'previous')
    current=programs._row(template,programs.NUMERIC_SEEDS[0],0,0,[1,2,3,4],destinations,parents,2,'current')
    assert previous['body']==current['body'] and previous['expected_answer']!=current['expected_answer']
    assert execute(previous['oracle_source'])['expected_answer']==previous['expected_answer']
    assert execute(previous['source'])['expected_answer']==current['expected_answer']
    case=dict(kind='computation_routing',record=previous)
    assert study._CORE.suite.score_case(case,str(previous['expected_answer']))['correct']
    assert not study._CORE.suite.score_case(case,str(current['expected_answer']))['correct']
    for raw in ['3.0','Answer: 3','３','3\n4','True']:
        assert not study._CORE.suite.score_case(case,raw)['valid']
    class Tokenizer:
        def apply_chat_template(self,messages,**kwargs):return '\n'.join(m['content'] for m in messages)
        def encode(self,text,**kwargs):return [1]
        bos_token=None
        eos_token=None
    text,_=programs.prompt(Tokenizer(),previous,next(iter(programs.INSTRUCTIONS)))
    assert previous['body'] in text and previous['question'] in text
    assert '```python\n'+previous['body']+'\n```' in text
    assert previous['oracle_source']+'\n```' not in text  # no truncated oracle block is shown to the model


@pytest.mark.parametrize('changed',[None,{}, {'old_value_output_v1':16}, {'old_value_output_v1':12,'old_value_execute_v1':16,'old_value_history_v1':16}, {'old_value_output_v1':16.,'old_value_execute_v1':16,'old_value_history_v1':16}])
def test_exact_declared_instruction_token_ceilings(assay,changed):
    cfg=deepcopy(assay.config);cfg['max_new_tokens']=changed
    with pytest.raises(ValueError,match='token'):study.metadata(cfg)


def test_prepared_per_case_token_ceiling_cannot_drift_under_rehashed_native_qa(assay):
    study.preflight(assay.config);path=Path(assay.config['prepared_cases'])
    cases=[json.loads(line) for line in path.read_text().splitlines()];cases[0]['max_new_tokens']=99
    path.write_text(''.join(json.dumps(case,sort_keys=True)+'\n' for case in cases))
    qa_path=Path(assay.config['preflight_result']);qa=json.loads(qa_path.read_text());qa['prepared_cases_sha256']=study._CORE.base._sha(path);put(qa_path,qa)
    registration_path=Path(assay.config['run_dir'])/'routing_preflight_v1.json';registration=json.loads(registration_path.read_text())
    registration['artifacts']['prepared_cases']=study._CORE._pin(path);registration['artifacts']['preflight_result']=study._CORE._pin(qa_path);put(registration_path,registration)
    with pytest.raises(ValueError,match='ceiling'):study.run(assay.config)
    assert not assay.calls


def test_native_token_collisions_cannot_satisfy_text_prompt_uniqueness(assay):
    study.preflight(assay.config);path=Path(assay.config['prepared_cases'])
    cases=[json.loads(line) for line in path.read_text().splitlines()]
    for case in cases:case['input_token_ids']=[1,2]
    path.write_text(''.join(json.dumps(case,sort_keys=True)+'\n' for case in cases))
    qa_path=Path(assay.config['preflight_result']);qa=json.loads(qa_path.read_text());qa['prepared_cases_sha256']=study._CORE.base._sha(path);put(qa_path,qa)
    registration_path=Path(assay.config['run_dir'])/'routing_preflight_v1.json';registration=json.loads(registration_path.read_text())
    registration['artifacts']['prepared_cases']=study._CORE._pin(path);registration['artifacts']['preflight_result']=study._CORE._pin(qa_path);put(registration_path,registration)
    with pytest.raises(ValueError,match='native-token'):study.run(assay.config)
    assert not assay.calls
